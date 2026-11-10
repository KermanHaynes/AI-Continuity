"""Check current contract identities, bindings and generated technical data.

The enumeration comes from current architecture and maintenance sources.
Stable identities are locked independently of paragraph order.
Bindings identify the scope of each structural or operator-review check.
"""
import pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
SPEC='\n# 0. Source boundary\n'.join((ROOT/path).read_text() for path in ('docs/ARCHITECTURE_SPEC.md','docs/MAINTENANCE.md'))

def units():
 section=0;buffer=[];lineno=0
 def flush():
  nonlocal buffer
  if buffer:
   text=' '.join(buffer);buffer=[];return text
 for line in SPEC.splitlines():
  lineno+=1
  m=re.match(r'^# (\d+)\. ',line)
  if m:
   text=flush()
   if text and section:yield section,text
   section=int(m[1]);continue
  if not section:continue
  # Required field/list entries are individually traceable; prose is preserved as paragraphs.
  if not line.strip() or line.startswith('#') or line.strip()=='---':
   text=flush()
   if text:yield section,text
   continue
  if line.startswith('    '):
   text=flush()
   if text:yield section,text
   if line.strip():yield section,line.strip()
  elif re.match(r'^(?:- |\d+\. )',line):
   text=flush()
   if text:yield section,text
   yield section,line
  else:buffer.append(line.strip())
 text=flush()
 if text:yield section,text


def source_rows():
 import json
 identities=json.loads((ROOT/'contracts/identities.json').read_text())
 lookup={}
 for rid,v in identities.items():lookup.setdefault((v['section'],v['source_sha256']),[]).append(rid)
 seen=set()
 for section,text in units():
  matches=lookup.get((section,source_hash(text)),[])
  if not matches:raise ValueError('Source unit needs an explicit stable identity: '+text)
  rid=matches.pop(0)
  if rid in seen:raise ValueError('Repeated source identity: '+rid)
  seen.add(rid)
  yield rid,section,text
 if seen!=set(identities):raise ValueError('Identity has no authoritative source unit')


def default_config():
 import json
 return json.loads((ROOT/'contracts/bindings.json').read_text())

def source_hash(text):
 import hashlib
 return hashlib.sha256(text.encode()).hexdigest()

KINDS=('structural_invariant','operating_procedure','human_evidence_review','governance_restriction','deferred_provider_specific')
PROOFS=('test_assertion','source_review','procedure_review','transaction_verification','human_review_required')

def validate_evidence(rid,text,entry):
 """Check traceability declarations, never infer semantic certification."""
 required=('source_sha256','requirement_kind','record_schema','implementation','procedure','verification','negative_test_applicability','applicability','status','issue_type','result')
 if any(not entry.get(key) for key in required): raise ValueError(rid+': incomplete per-requirement evidence')
 if entry['source_sha256']!=source_hash(text): raise ValueError(rid+': evidence belongs to different source text')
 if entry['status'] not in ('implemented','partial','blocked'): raise ValueError(rid+': invalid evidence status')
 if entry['requirement_kind'] not in KINDS[:-1]: raise ValueError(rid+': invalid binding requirement kind')
 if entry['issue_type'] not in ('none','human_review_required','implementation_gap','traceability_gap','transaction_verification_pending'): raise ValueError(rid+': invalid issue type')
 for key in ('implementation','positive_tests','negative_tests','verification'):
  if not isinstance(entry.get(key),list): raise ValueError(rid+': explicit reference lists required')
 for proof in entry['verification']:
  if proof.get('type') not in PROOFS or not proof.get('ref') or not proof.get('assertion'): raise ValueError(rid+': incomplete typed evidence')
 if entry['status']=='implemented':
  if entry['issue_type']!='none': raise ValueError(rid+': implemented requirement has outstanding issue')
  if entry['requirement_kind']=='human_evidence_review': raise ValueError(rid+': interpretive requirements need actual user review evidence')
  if not any(p['type']!='human_review_required' for p in entry['verification']): raise ValueError(rid+': no completed verification')
  if entry['requirement_kind']=='structural_invariant' and not entry['positive_tests'] and not any(p['type']=='source_review' for p in entry['verification']): raise ValueError(rid+': structural verification missing')
 return entry

def classified_rows(config=None):
 config=default_config() if config is None else config
 known={rid for rid,_,_ in source_rows()}
 contexts=set(config.get('context',{}));evidence=set(config.get('evidence',{}));deferred=set(config.get('approved_deferrals',[]))
 if not contexts|evidence|deferred<=known: raise ValueError('Declaration references an unknown stable requirement ID')
 if contexts&evidence or contexts&deferred or evidence&deferred: raise ValueError('Conflicting source-unit classifications')
 for rid,section,text in source_rows():
  row=dict(id=rid,text=text,status_scope='individual binding or actual user operation; not architectural completion',classification='binding',requirement_kind='unclassified',status='partial',issue_type='traceability_gap',record_schema='Binding required',implementation=[],procedure='docs/ARCHITECTURE_SPEC.md',positive_tests=[],negative_tests=[],verification=[],negative_test_applicability='Review the current binding',result='Register the binding for this check',applicability='Add the record or operation binding before using this check.')
  if rid in contexts:
   entry=config['context'][rid]
   if entry.get('source_sha256')!=source_hash(text) or not entry.get('reason'): raise ValueError('Incomplete contextual classification: '+rid)
   row.update(classification='context',requirement_kind='context',status=None,issue_type='none',applicability=entry['reason'],result='Current reference context')
  elif rid in deferred:
   if not (section==20 and text.startswith('- ')): raise ValueError('Environment obligation must belong to the configured interface boundary list')
   row.update(classification='approved_deferral',requirement_kind='deferred_provider_specific',status='deferred_provider_specific',issue_type='none',applicability='Environment-specific operation requiring actual access/review',result='Requires evidence for the actual external operation')
  elif rid in evidence:row.update(validate_evidence(rid,text,config['evidence'][rid]))
  yield row

def generate(config=None):
 import json
 return json.dumps({'contract_rows': list(classified_rows(config))}, ensure_ascii=False, indent=2)+'\n'

def partial_report():
 import json
 rows=[r for r in classified_rows() if r['status'] in ('partial','blocked') or r['classification']=='approved_deferral']
 return json.dumps({'operator_or_environment_obligations':rows}, ensure_ascii=False, indent=2)+'\n'

if __name__=='__main__':
 import json
 (ROOT/'contracts/requirements.json').write_text(json.dumps({rid:dict(section=section,text=text) for rid,section,text in source_rows()},indent=2)+'\n')
 (ROOT/'contracts/traceability.json').write_text(generate())
 (ROOT/'contracts/review-obligations.json').write_text(partial_report())
