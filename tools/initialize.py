"""Create an empty data root using canonical runtime generators; never overwrite."""
import argparse
import pathlib
import shutil
import sys

PACKAGE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from memory.records import atomic, rebuild
import yaml


def initialize(destination):
    root = pathlib.Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('Destination must be empty')
    root.mkdir(parents=True, exist_ok=True)
    for name in ('schemas', 'CONTEXT'):
        shutil.copytree(PACKAGE / name, root / name)
    for rel in ('INDEX/PROCESSING', 'INDEX/CLOSEOUTS', 'SOT/EXPORTS', 'KNOWLEDGE', 'WORK/ITEMS'):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for name, key in (('REGISTRY', 'records'), ('ALIASES', 'aliases'), ('ARTIFACTS', 'artifacts'), ('EXCEPTIONS', 'exceptions')):
        atomic(root / f'INDEX/{name}.yaml', yaml.safe_dump({'schema_version': 1, key: []}))
    rebuild(root)
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=pathlib.Path)
    args = parser.parse_args()
    print(initialize(args.destination))
