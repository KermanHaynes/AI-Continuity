"""Regenerate reviewable schema artifacts from memory.schema's single definition."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from memory.schema import SCHEMAS
root=pathlib.Path(__file__).resolve().parents[1]
for path in (root/'schemas').glob('*.json'): path.unlink()
for name,schema in SCHEMAS.items():
    (root/f'schemas/{name}.schema.json').write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema',**schema},indent=2)+'\n')
