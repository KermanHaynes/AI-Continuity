"""Resolve checkout-specific Git metadata independently of content containment."""
import hashlib
import pathlib
import subprocess
import tempfile


def git_metadata_dir(root):
    result = subprocess.run(['git', 'rev-parse', '--absolute-git-dir'],
                            cwd=root, text=True, capture_output=True)
    return pathlib.Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def metadata_path(root, name):
    if '/' in name or '\\' in name or name in ('', '.', '..'):
        raise ValueError('Invalid Git metadata filename')
    result = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-path', name],
                            cwd=root, text=True, capture_output=True)
    if result.returncode == 0:
        return pathlib.Path(result.stdout.strip()).resolve()
    # Unversioned synthetic repositories still keep transaction state outside content.
    key = hashlib.sha256(str(pathlib.Path(root).resolve()).encode()).hexdigest()
    return pathlib.Path(tempfile.gettempdir()) / 'memory-unversioned-metadata' / key / name
