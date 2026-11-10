"""Explicit metadata discovery, atomic validated writes, identity and agenda views."""
from __future__ import annotations
import contextlib, datetime as dt, hashlib, json, os, pathlib, re, tempfile, unicodedata, uuid
from zoneinfo import ZoneInfo
import yaml
import collections, copy

_LOAD_CACHE=collections.OrderedDict()
_LOAD_CACHE_BYTES=0

from .schema import check_record, LIFECYCLE, WORK_SECTIONS, CURRENT_SECTIONS

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def new_id(): return str(uuid.uuid4())
def digest(b): return hashlib.sha256(b).hexdigest()
def normalized(s): return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())
def load(path):
    # Cache parsed metadata by exact bytes, never by path or timestamps. Callers
    # receive independent copies, so mutation cannot change the cached evidence.
    global _LOAD_CACHE_BYTES
    raw=path.read_bytes();key=(path.suffix,hashlib.sha256(raw).digest())
    cached=_LOAD_CACHE.get(key)
    if cached is not None:
        _LOAD_CACHE.move_to_end(key)
        return copy.deepcopy(cached[1])
    text=raw.decode('utf-8')
    if path.suffix=='.md':
        if not text.startswith('---\n'):raise ValueError('Work record requires YAML front matter')
        front,body=text[4:].split('\n---\n',1)
        value=(yaml.load(front,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader)),body)
    else:value=yaml.load(text,Loader=getattr(yaml,'CSafeLoader',yaml.SafeLoader))
    budget=128*1024*1024
    if len(raw)<=budget:
        while _LOAD_CACHE and (_LOAD_CACHE_BYTES+len(raw)>budget or len(_LOAD_CACHE)>=8192):
            _,(weight,_)=_LOAD_CACHE.popitem(last=False);_LOAD_CACHE_BYTES-=weight
        _LOAD_CACHE[key]=(len(raw),copy.deepcopy(value));_LOAD_CACHE_BYTES+=len(raw)
    return value

def atomic(path,text):
    from .staging import track_write
    track_write(path)
    if path.is_file() and path.read_text(encoding='utf-8') == text: return
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.memory-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: f.write(text); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def write(path,data,body=None):
    check_record(data)
    text=yaml.dump(data,Dumper=getattr(yaml,'CSafeDumper',yaml.SafeDumper),sort_keys=False,allow_unicode=True)
    if body is not None: text='---\n'+text+'---\n'+body
    atomic(path,text)
def inside(root,path):
    root=pathlib.Path(root).absolute()
    logical=pathlib.Path(os.path.abspath(root/path))
    if not logical.is_relative_to(root): raise ValueError('Path escapes repository')
    from .staging import overlay_info
    info=overlay_info(root)
    if info:
        rel=logical.relative_to(root)
        source=info['base_root']/rel
        if not logical.exists() and source.is_file():
            if not source.resolve().is_relative_to(info['base_root'].resolve()): raise ValueError('Path escapes repository')
            logical.parent.mkdir(parents=True,exist_ok=True)
            logical.symlink_to(source)
        resolved=logical.resolve()
        if not resolved.is_relative_to(root) and resolved!=source.resolve(): raise ValueError('Path escapes repository')
        if source.exists() and not source.resolve().is_relative_to(info['base_root'].resolve()): raise ValueError('Path escapes repository')
        return logical
    if not logical.resolve().is_relative_to(root.resolve()): raise ValueError('Path escapes repository')
    return logical

def metadata_paths(root):
    """Never parse provider originals or arbitrary attachment JSON/YAML."""
    for pattern in ('SOT/EXPORTS/*/export.yaml','SOT/*/*/*/*/manifest.yaml','SOT/*/*/*/*/MESSAGES.yaml','SOT/*/*/*/*/TOPIC_MAP.yaml','KNOWLEDGE/*/subject.yaml','WORK/ITEMS/work_*.md','INDEX/PROCESSING/*.yaml','INDEX/CLOSEOUTS/*.yaml'):
        yield from sorted(root.glob(pattern))
def collect(root, *, names=None):
    records=[]
    for p in metadata_paths(root):
        if names is not None and p.name not in names:continue
        value=load(p); body=None
        if isinstance(value,tuple): value,body=value
        records.append((p,value,body))
    return records

def indexes(records):
    registry=[]; aliases=[]
    for p,d,_ in records:
        kind=d['record_type']
        key={'sot_export':'export_id','sot_conversation':'sot_id','knowledge_subject':'subject_id','work_item':'work_item_id','processing_state':'transaction_id','closeout':'closeout_id','artifact':'artifact_id','exception':'exception_id'}.get(kind)
        if key: registry.append({'id':d[key],'record_type':kind,'path':p.as_posix()})
        if kind=='knowledge_subject':
            aliases.extend({'subject_id':d['subject_id'],'name':n} for n in [d['canonical_name'],*d['aliases']])
    return sorted(registry,key=lambda r:r['id']),sorted(aliases,key=lambda r:(r['name'],r['subject_id']))
def registry_views(root):
    records=[(p.relative_to(root),d,b) for p,d,b in collect(root,names={'export.yaml','manifest.yaml','subject.yaml'} | {p.name for pattern in ('WORK/ITEMS/work_*.md','INDEX/PROCESSING/*.yaml','INDEX/CLOSEOUTS/*.yaml') for p in root.glob(pattern)})]
    for name,key in [('ARTIFACTS','artifacts'),('EXCEPTIONS','exceptions')]:
        path=root/f'INDEX/{name}.yaml'
        records.extend((path.relative_to(root),d,None) for d in load(path)[key])
    return indexes(records)
def rebuild(root):
    registry,aliases=registry_views(root)
    for name,key,value in [('REGISTRY','records',registry),('ALIASES','aliases',aliases)]:
        atomic(root/f'INDEX/{name}.yaml',yaml.safe_dump({'schema_version':1,key:value},sort_keys=False,allow_unicode=True))
    atomic(root/'WORK/AGENDA.md',agenda([d for _,d,_ in collect(root) if d['record_type']=='work_item']))
    for p,d,_ in collect(root):
        if d['record_type']=='topic_map': atomic(p.parent/'TOPIC_MAP.md',topic_markdown(d))
        if d['record_type']=='knowledge_subject': atomic(p.parent/'INDEX.md',subject_index(d))

def resolve_subject(root,query):
    subjects=[(p,d) for p,d,_ in collect(root) if d['record_type']=='knowledge_subject']
    for predicate in (lambda d:d['subject_id']==query,lambda d:d['canonical_name']==query,lambda d:query in d['aliases'],lambda d:normalized(query) in [normalized(n) for n in [d['canonical_name'],*d['aliases']]]):
        matches=[(p,d) for p,d in subjects if predicate(d)]
        if len(matches)>1: raise ValueError('Ambiguous subject lookup: '+', '.join(d['subject_id'] for _,d in matches))
        if matches: return matches[0]
    raise ValueError('Subject not found')

def temporal(t):
    at=t.get('at'); precision=t.get('precision')
    zone=t.get('time_zone')
    if zone: ZoneInfo(zone)
    if at is None:
        if precision!='unknown': raise ValueError('Null dates require unknown precision')
        return None
    if precision=='date':
        if len(at)!=10: raise ValueError('Date-only requires YYYY-MM-DD')
        return dt.date.fromisoformat(at)
    if precision!='datetime' or not zone: raise ValueError('Datetime requires IANA time zone')
    value=dt.datetime.fromisoformat(at)
    if value.tzinfo is None: raise ValueError('Datetime must include explicit offset')
    local=value.astimezone(ZoneInfo(zone))
    if local.utcoffset()!=value.utcoffset(): raise ValueError('Datetime offset disagrees with IANA zone')
    return value

def occurrence_key(value):
    if value is None: return ('9999-12-31',2,'')
    if len(value)==10: return (dt.date.fromisoformat(value).isoformat(),0,'')
    instant=dt.datetime.fromisoformat(value)
    if instant.tzinfo is None: raise ValueError('Known occurrence datetime requires an offset')
    utc=instant.astimezone(dt.timezone.utc)
    return (utc.date().isoformat(),1,utc.isoformat())


def obligation_key(t):
    value=temporal(t)
    if value is None: return ('9999',1,'')
    # Date-only values retain their calendar dates; instants compare in UTC.
    if isinstance(value,dt.datetime): return (value.astimezone(dt.timezone.utc).date().isoformat(),1,value.astimezone(dt.timezone.utc).isoformat())
    return (value.isoformat(),0,'')

def agenda(items):
    visible=[w for w in items if w['status'] in LIFECYCLE and w['status'] not in ('completed','closed')]
    def obligations(w): return [d for d in w['dates'] if d['state']=='active']+[e for e in w['events'] if e['state']=='scheduled']
    def key(w): return (min([obligation_key(d) for d in obligations(w) if d['at']] or [('9999',1,'')]),w['work_item_id'])
    lines=['# Agenda','','Derived from canonical WORK records; regenerate with `python -m memory.cli render-agenda`.','']
    for dated in (True,False):
        lines.extend(['## Dated work' if dated else '## Undated work',''])
        for w in sorted(visible,key=key):
            dates=obligations(w)
            if any(d['at'] for d in dates)!=dated: continue
            wid=w['work_item_id']; lines.append(f"- [{w['title']}](ITEMS/work_{wid}.md) | {wid} | {w['status']}")
            actions=[a['description'] for a in w['actions'] if a['action_id'] in w['resumption']['next_action_ids'] and a['classification']=='established' and a['state']=='outstanding']
            lines.append('  - Established next action: '+('; '.join(actions) or 'undetermined'))
            for d in sorted(dates,key=obligation_key):
                lines.append(f"  - {d.get('kind','scheduled_event')}: {d['at'] or 'unknown'} | {d['time_zone'] or 'zone undetermined'}"+(f" | {d['description']}" if 'description' in d else ''))
            lines.append('  - Pending external matters: '+('; '.join(w['resumption']['pending_external_matters']) or 'undetermined'))
        lines.append('')
    return '\n'.join(lines).rstrip()+'\n'

@contextlib.contextmanager
def lock(root):
    """Advisory lock serializes cooperative local writers, independent of Git leases."""
    import fcntl
    from .git_paths import metadata_path
    path=metadata_path(root,'.memory.lock')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(f,fcntl.LOCK_UN)

def topic_markdown(data):
    lines=['# Topic map','']
    for t in data['topics']:
        lines.extend([f"## {t['label']}",'',f"Topic ID: {t['topic_id']} | Provisional: {str(t['provisional']).lower()}",''])
        lines.extend(f"- [Message {mid}](transcript.md#msg-{mid})" for mid in t['message_ids'])
        for key in ('subject_ids','decisions_stated','revisions','open_questions','experiments_and_results','artifact_ids'):
            lines.extend(['',key.replace('_',' ').title()+': '+('; '.join(t[key]) or 'none recorded')])
        lines.append('')
    if not data['topics']: lines.extend(['No reviewed topics; consult manifest processing state.',''])
    return '\n'.join(lines).rstrip()+'\n'

def subject_index(d):
    return f"# {d['canonical_name']}\n\nID: {d['subject_id']}\n\nScope: {d['scope']}\n\nExclusions: {'; '.join(d['exclusions']) or 'undetermined'}\n\nAliases: {'; '.join(d['aliases']) or 'none'}\n\nClassifications: {'; '.join(d['classifications']) or 'none'}\n\nStatus: {d['status']}; integration: {d['integration_state']}. Consult the current position and evidence chain before resuming.\n\n[Current](CURRENT.md) · [Evolution](EVOLUTION.md) · [Sources](SOURCES.md) · [Metadata](subject.yaml) · [Artifacts](ARTIFACTS/)\n"

def resolve_work(root,query):
    works=[(p,d,b) for p,d,b in collect(root) if d['record_type']=='work_item']
    for predicate in (lambda d:d['work_item_id']==query,lambda d:d['title']==query,lambda d:query in d['aliases'],lambda d:normalized(query) in [normalized(n) for n in [d['title'],*d['aliases']]]):
        matches=[(p,d,b) for p,d,b in works if predicate(d)]
        if len(matches)>1: raise ValueError('Ambiguous work lookup')
        if matches: return matches[0]
    raise ValueError('Work not found')
