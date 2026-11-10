"""Changed-file transactions over a read-only metadata overlay.

No existing archive is copied. Source bytes are read only by applicable integrity
checks; metadata symlinks supply the dependency graph without a working snapshot.
"""
import contextlib, json, os, pathlib, shutil, tempfile
from .records import digest, atomic

OVERLAYS = {}


def snapshot(root):
    """Full checksum snapshot, reserved for explicit read-only audits/tests."""
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts
            and '__pycache__' not in p.parts and p.name != '.memory.lock'}


def overlay_info(root):
    return OVERLAYS.get(pathlib.Path(root).absolute())


def journal_path(root):
    from .git_paths import metadata_path
    return metadata_path(root, 'memory-publish-journal.json')


def file_hash(path):
    return digest(path.read_bytes()) if path.is_file() else None


def metadata_dependencies(root):
    from .records import metadata_paths
    paths = set(metadata_paths(root))
    for pattern in ('schemas/*.json', 'INDEX/*.yaml', 'INDEX/CONVERSATIONS.json', 'WORK/AGENDA.md',
                    'KNOWLEDGE/*/*.md',
                    'SOT/*/*/*/*/TOPIC_MAP.md'):
        paths.update(root.glob(pattern))
    return sorted(p for p in paths if p.is_file())


def prepare(root):
    """Link metadata dependencies only; record their starting hashes before edits."""
    stage = pathlib.Path(tempfile.mkdtemp(prefix='memory-changes-'))
    target = (stage / 'repo').resolve()
    target.mkdir()
    info = dict(base_root=root, base={}, stage=stage)
    OVERLAYS[target] = info
    for source in metadata_dependencies(root):
        rel = source.relative_to(root).as_posix()
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(source)
    for path in root.glob('KNOWLEDGE/*/ARTIFACTS'):
        (target / path.relative_to(root)).mkdir(parents=True, exist_ok=True)
    for path in root.glob('SOT/*/*/*/*/attachments'):
        (target / path.relative_to(root)).mkdir(parents=True, exist_ok=True)
    for rel in ('WORK/ITEMS', 'KNOWLEDGE', 'SOT/EXPORTS', 'INDEX/PROCESSING', 'INDEX/CLOSEOUTS'):
        (target / rel).mkdir(parents=True, exist_ok=True)
    from .git_paths import git_metadata_dir
    gitdir=git_metadata_dir(root)
    if gitdir is not None:
        (target / '.git').write_text('gitdir: '+str(gitdir)+'\n')
    return target, info


def track_write(path):
    """Capture only an intended replacement's original bytes, before the write."""
    path=pathlib.Path(path).absolute()
    for target,info in OVERLAYS.items():
        if path.is_relative_to(target):
            rel=path.relative_to(target).as_posix()
            if rel not in info['base']:
                source=info['base_root']/rel
                if '/original.' in rel and source.exists(): raise ValueError('Existing original source evidence is immutable')
                info['base'][rel]=file_hash(source)
            return


def require_validation(root, paths):
    info=overlay_info(root)
    if info: info.setdefault('validation_paths',set()).update(paths)


def changed_files(target, info):
    changes = []
    for p in target.rglob('*'):
        if not p.is_file() or p.is_symlink() or '.git' in p.relative_to(target).parts:
            continue
        rel = p.relative_to(target).as_posix()
        sha = file_hash(p)
        old = info['base'].get(rel)
        existing = info['base_root'] / rel
        if rel not in info['base'] and existing.exists():
            # A writer must declare an existing dependency before replacing it.
            if '/original.' in rel:
                raise ValueError('Existing original source evidence is immutable')
            raise ValueError('Undeclared existing write dependency: ' + rel)
        if sha != old:
            changes.append(dict(path=rel, before=old, after=sha, replacement=str(p)))
    return sorted(changes, key=lambda c: c['path'])


def preconditions(root, changes, recovery=False):
    from .records import inside
    for entry in changes:
        observed = file_hash(inside(root, entry['path']))
        allowed = (entry['before'], entry['after']) if recovery else (entry['before'],)
        if observed not in allowed:
            raise ValueError('Concurrent change blocks publication: ' + entry['path'])


def publish(root, target, info, changes, recovery=False):
    """Journal replacements and use same-filesystem atomic rename for each file."""
    from .records import inside
    preconditions(root, changes, recovery=recovery)
    journal = journal_path(root)
    atomic(journal, json.dumps(dict(version=2, stage=str(info['stage']),
                                   changes=changes, validation_scope='incremental'), sort_keys=True))
    for entry in changes:
        dst = inside(root, entry['path'])
        # Check immediately before each replacement as well as before the batch.
        preconditions(root, [entry], recovery=True)
        dst.parent.mkdir(parents=True, exist_ok=True)
        # The durable replacement stays in staging until journal removal, enabling replay.
        fd, tmp = tempfile.mkstemp(prefix='.memory-replace-', dir=dst.parent)
        try:
            with os.fdopen(fd, 'wb') as out, open(entry['replacement'], 'rb') as src:
                shutil.copyfileobj(src, out)
                out.flush()
                os.fsync(out.fileno())
            os.replace(tmp, dst)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    journal.unlink()


@contextlib.contextmanager
def candidate(root, *, validate_noop=True):
    """Stage only replacements; metadata and existing originals remain read-only inputs."""
    root = root.resolve()
    if journal_path(root).exists():
        raise ValueError('Incomplete publication checkpoint; recover-publication before further writes')
    target, info = prepare(root)
    retain = False
    try:
        error = None
        try:
            yield target
        except ValueError as exc:
            error = exc
        changes = changed_files(target, info)
        if error is not None:
            # Only explicitly durable evidence conflicts may publish on an operation error.
            if not getattr(error, 'preserve_changes', False):
                # Legacy SOT conflicts preserve their registered exception, never source changes.
                if any(c['path']=='INDEX/EXCEPTIONS.yaml' for c in changes):
                    changes = [c for c in changes if c['path'] in ('INDEX/EXCEPTIONS.yaml', 'INDEX/REGISTRY.yaml')]
                else: changes=[]
        if changes or info.get('validation_paths') or (validate_noop and error is None):
            from .validation import validate_incremental
            scope={c['path'] for c in changes}|info.get('validation_paths',set())
            errors = [f for f in validate_incremental(target, scope) if f['severity'] == 'ERROR']
            if errors: raise ValueError('Incremental validation failed: ' + json.dumps(errors))
        if changes:
            retain = True
            publish(root, target, info, changes)
            retain = False
        if error is not None: raise error
    finally:
        OVERLAYS.pop(target, None)
        if not journal_path(root).exists(): shutil.rmtree(info['stage'], ignore_errors=True)


def recover_publication(root):
    """Replay only journaled replacements, preserving unrelated concurrent changes."""
    journal = journal_path(root)
    if not journal.is_file(): raise ValueError('No retained publication journal')
    data = json.loads(journal.read_text())
    if data.get('version') != 2: raise ValueError('Legacy journal requires explicit recovery review')
    changes = data['changes']
    preconditions(root, changes, recovery=True)
    target, info = prepare(root)
    retain = False
    try:
        from .records import inside
        for entry in changes:
            replacement = pathlib.Path(entry['replacement'])
            if not replacement.resolve().is_relative_to(pathlib.Path(data['stage']).resolve()) or replacement.is_symlink(): raise ValueError('Recovery replacement escapes its retained stage')
            if not replacement.is_file() or file_hash(replacement) != entry['after']:
                raise ValueError('Missing or corrupt staged replacement')
            dst = inside(target, entry['path'])
            if dst.is_symlink(): dst.unlink()
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(replacement, dst)
        from .validation import validate_incremental
        if any(f['severity'] == 'ERROR' for f in validate_incremental(target, {e['path'] for e in changes})):
            raise ValueError('Recovered incremental candidate fails validation')
        # Reuse original starting conditions, not the partially published tree's hashes.
        publish(root, target, dict(stage=pathlib.Path(data['stage'])), changes, recovery=True)
        shutil.rmtree(data['stage'], ignore_errors=True)
        return dict(recovered=[e['path'] for e in changes], validation_scope='incremental')
    finally:
        OVERLAYS.pop(target, None)
        shutil.rmtree(info['stage'], ignore_errors=True)
