"""Regression tests for integrity, recovery, and operational behavior; fictional evidence only."""
import contextlib, copy, datetime as dt, io, json, pathlib, shutil, unittest
from unittest.mock import patch
from test_foundation import Fixture
from memory.records import *
from memory.operations import *
from memory.schema import check_record,SCHEMAS,KNOWN_EXCEPTION_CLASSIFICATIONS
from memory.staging import candidate,prepare,changed_files,OVERLAYS,recover_publication,journal_path
from memory.validation import validate,validate_incremental
from memory.cli import main

class DailyHorizons(Fixture):
 def setup_obligations(self,kind,offsets,precision='date'):
  ref=self.evidence();w=self.work();base=dt.datetime.fromisoformat('2026-10-21T12:00:00-04:00');ids=[]
  for days in offsets:
   value=base+dt.timedelta(days=days);at=value.date().isoformat() if precision=='date' else value.isoformat()
   if kind=='event':
    item=dict(event_id=new_id(),description='Fictional event',at=at,precision=precision,time_zone='America/New_York',source_refs=[ref],state='scheduled');w['events'].append(item);ids.append(item['event_id'])
   else:
    item=self.date(ref,kind=kind,at=at,precision=precision);w['dates'].append(item);ids.append(item['date_id'])
  self.savework(w);return w,base,ids
 def test_event_three_days_but_not_sixty(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('event',[3,60]);f=audit(self.root,'daily',at)['findings'];self.assertEqual([(ids[0],'upcoming_event')],[(x['obligation_id'],x['code']) for x in f])
 def test_followup_three_days_but_not_sixty(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('follow_up',[3,60]);f=audit(self.root,'daily',at)['findings'];self.assertEqual([(ids[0],'approaching_follow_up')],[(x['obligation_id'],x['code']) for x in f])
 def test_boundary_seven_eight_and_past_events(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('event',[-1,7,8]);codes={x['obligation_id']:x['code'] for x in audit(self.root,'daily',at)['findings']};self.assertEqual({ids[0]:'past_scheduled_event',ids[1]:'upcoming_event'},codes)
 def test_followup_overdue_due_and_approaching(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('follow_up',[-1,0,7,8]);codes={x['obligation_id']:x['code'] for x in audit(self.root,'daily',at)['findings']};self.assertEqual({ids[0]:'due_follow_up',ids[1]:'due_follow_up',ids[2]:'approaching_follow_up'},codes)
 def test_inactive_and_unknown_obligations_excluded(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('follow_up',[0,0,0]);
  for item,state in zip(w['dates'],['satisfied','superseded','cancelled']):item['state']=state
  w['dates'].append(self.date(self.evidence(),kind='follow_up',at=None,precision='unknown'));self.savework(w);self.assertEqual([],audit(self.root,'daily',at)['findings'])
 def test_calendar_horizon_uses_obligation_zone(self):
  from memory.audits import audit
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref,kind='follow_up',at='2026-10-29',zone='Asia/Tokyo')];self.savework(w)
  # October 22 in Tokyo, still October 21 in UTC: exactly seven local calendar days.
  f=audit(self.root,'daily',dt.datetime.fromisoformat('2026-10-21T16:30:00+00:00'))['findings'];self.assertEqual('approaching_follow_up',f[0]['code'])

class Artifacts(Fixture):
 def setup_attachment(self):
  s=self.sot();p=self.sotpath(s['sot_id']);mid=load(p.parent/'MESSAGES.yaml')['messages'][0]['message_id'];src=pathlib.Path(self.tmp.name)/'fictional.txt';src.write_bytes(b'fictional original attachment bytes');return s,p,mid,src
 def run_cli(self,*args):
  out=io.StringIO();err=io.StringIO()
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):code=main(['--root',str(self.root),*map(str,args)])
  return code,out.getvalue(),err.getvalue()
 def test_registration_preserves_and_links(self):
  s,p,mid,src=self.setup_attachment();code,out,err=self.run_cli('register-artifact',s['sot_id'],src,'--native-artifact-id','native-fictional','--message-id',mid,'--description','Fictional attachment');self.assertEqual(0,code,err);result=json.loads(out);self.assertEqual('incremental',result['validation_scope']);a=result['result'];self.assertEqual(src.read_bytes(),(self.root/a['path']).read_bytes());self.assertIn('/attachments/'+a['artifact_id']+'/original.txt',a['path']);self.assertEqual('native-fictional',a['native_artifact_id']);self.assertIn(a['artifact_id'],load(p.parent/'MESSAGES.yaml')['messages'][0]['attachment_ids']);self.clean()
 def test_identical_reregistration_is_idempotent(self):
  s,p,mid,src=self.setup_attachment();args=('register-artifact',s['sot_id'],src,'--native-artifact-id','native-fictional','--message-id',mid)
  a=json.loads(self.run_cli(*args)[1])['result'];b=json.loads(self.run_cli(*args)[1])['result'];self.assertEqual(a,b);self.assertEqual(1,len(load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts']));self.clean()
 def test_conflicting_bytes_preserved_and_reported(self):
  s,p,mid,src=self.setup_attachment();args=('register-artifact',s['sot_id'],src,'--native-artifact-id','native-fictional','--message-id',mid);code,out,err=self.run_cli(*args);self.assertEqual(0,code,err);original=json.loads(out)['result'];src.write_bytes(b'conflicting fictional evidence');code,out,err=self.run_cli(*args);self.assertEqual(2,code);self.assertIn('Conflicting attachment evidence preserved',err);entries=load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts'];self.assertEqual(2,len(entries));self.assertEqual(original['sha256'],digest((self.root/original['path']).read_bytes()));conflict=next(a for a in entries if a.get('conflicts_with'));self.assertEqual(src.read_bytes(),(self.root/conflict['path']).read_bytes());self.assertEqual(original['artifact_id'],conflict['conflicts_with']);self.assertEqual(2,self.run_cli(*args)[0]);self.assertEqual(2,len(load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts']));self.clean()
 def test_missing_message_or_sot_rolls_back(self):
  s,p,mid,src=self.setup_attachment();before=load(self.root/'INDEX/ARTIFACTS.yaml');self.assertEqual(2,self.run_cli('register-artifact',s['sot_id'],src,'--message-id',new_id())[0]);self.assertEqual(2,self.run_cli('register-artifact',new_id(),src)[0]);self.assertEqual(before,load(self.root/'INDEX/ARTIFACTS.yaml'));self.assertFalse(list(p.parent.glob('attachments/*/original.*')))
 def test_missing_source_rolls_back(self):
  s,p,mid,src=self.setup_attachment();src.unlink();self.assertEqual(2,self.run_cli('register-artifact',s['sot_id'],src)[0]);self.assertEqual([],load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts'])
 def test_hash_mismatch_detected(self):
  s,p,mid,src=self.setup_attachment();code,out,err=self.run_cli('register-artifact',s['sot_id'],src);self.assertEqual(0,code,err);a=json.loads(out)['result'];(self.root/a['path']).write_bytes(b'corrupt');self.assertIn('source_hash',self.codes());self.assertEqual(2,self.run_cli('register-artifact',s['sot_id'],src)[0])
 def test_path_escape_rejected(self):
  s,p,mid,src=self.setup_attachment();self.assertEqual(2,self.run_cli('register-artifact','../../outside',src)[0]);self.assertEqual([],load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts']);self.assertFalse((self.root.parent/'outside').exists())
 def test_registered_path_escape_fails_validation(self):
  s,p,mid,src=self.setup_attachment();code,out,err=self.run_cli('register-artifact',s['sot_id'],src);self.assertEqual(0,code,err);index=load(self.root/'INDEX/ARTIFACTS.yaml');index['artifacts'][0]['path']='../outside.txt';atomic(self.root/'INDEX/ARTIFACTS.yaml',yaml.safe_dump(index));self.assertIn('path_escape',self.codes())
 def test_registration_without_message_reference(self):
  s,p,mid,src=self.setup_attachment();code,out,err=self.run_cli('register-artifact',s['sot_id'],src);self.assertEqual(0,code,err);self.assertEqual([],json.loads(out)['result']['source_refs']);self.assertEqual(1,load(p)['counts']['attachments']);self.clean()

class ExceptionClassifications(Fixture):
 def test_unanticipated_normalized_classification(self):
  d=raise_exception(self.root,'new_fictional_condition_42',[],['Fictional evidence']);self.assertEqual('new_fictional_condition_42',d['classification']);raise_exception(self.root,'42_future_condition',[],['Fictional evidence']);raise_exception(self.root,'_future_condition',[],['Fictional evidence']);self.clean()
 def test_known_classifications(self):
  for value in KNOWN_EXCEPTION_CLASSIFICATIONS:raise_exception(self.root,value,[],['Fictional evidence'])
  self.assertEqual(len(KNOWN_EXCEPTION_CLASSIFICATIONS),len(load(self.root/'INDEX/EXCEPTIONS.yaml')['exceptions']));self.clean()
 def test_invalid_and_processing_only_classification(self):
  for value in ('','UPPER','white space','hyphen-value','verified_complete'):
   with self.subTest(value=value),self.assertRaises(ValueError):raise_exception(self.root,value,[],['Fictional evidence'])
 def test_processing_enum_unchanged(self):
  self.assertEqual(['native_capture_unavailable','captured_not_normalized','preserved_not_integrated','derived_incomplete','validation_failed','remote_push_failed','concurrent_semantic_conflict','verified_complete','archive_verified'],SCHEMAS['processing']['properties']['state']['enum'])

class IncrementalWrites(Fixture):
 def archived_repository(self,count=30):
  for n in range(count):self.export(json.dumps({'fictional_archive':n,'padding':'x'*4096}).encode())
  return self.work('Unrelated fictional pursuit')
 def test_unrelated_work_does_not_copy_or_hash_archive(self):
  w=self.archived_repository();root=self.root.resolve();original_read=pathlib.Path.read_bytes;seen=[]
  def watched(path):
   if path.name.startswith('original.'):
    seen.append(str(path));raise AssertionError('Unrelated source bytes were read')
   return original_read(path)
  with patch.object(pathlib.Path,'read_bytes',watched),patch('shutil.copytree',side_effect=AssertionError('Whole archive copy')):
   with candidate(root) as target:
    self.assertFalse(list(target.glob('SOT/EXPORTS/*/original.*')))
    p=target/self.workpath(w).relative_to(self.root);d,b=load(p);d['title']='Updated unrelated fictional pursuit';write(p,d,b);rebuild(target)
  self.assertEqual([],seen);self.assertEqual('Updated unrelated fictional pursuit',load(self.workpath(w))[0]['title']);self.clean()
 def test_full_validation_detects_unrelated_corruption(self):
  w=self.archived_repository(12);src=next(self.root.glob('SOT/EXPORTS/*/original.*'));src.write_bytes(b'fictional corruption')
  with candidate(self.root) as target:
   p=target/self.workpath(w).relative_to(self.root);d,b=load(p);d['title']='Unrelated updated title';write(p,d,b);rebuild(target)
  self.assertIn('source_hash',self.codes())
 def test_affected_source_corruption_blocks_incremental(self):
  s=self.sot();src=next(self.root.glob('SOT/EXPORTS/*/original.*'));src.write_bytes(b'fictional corruption')
  with self.assertRaises(ValueError):
   with candidate(self.root) as target:
    p=target/self.sotpath(s['sot_id']).relative_to(self.root);d=load(p);d['title']='Changed fictional source title';write(p,d);rebuild(target)
  self.assertNotEqual('Changed fictional source title',load(self.sotpath(s['sot_id']))['title'])
 def test_concurrent_changed_file_rejected(self):
  w=self.work();p=self.workpath(w)
  with self.assertRaises(ValueError):
   with candidate(self.root) as target:
    staged=target/p.relative_to(self.root);d,b=load(staged);d['title']='Candidate edit';write(staged,d,b);rebuild(target);atomic(p,'Concurrent real edit')
  self.assertEqual('Concurrent real edit',p.read_text());self.assertFalse(journal_path(self.root).exists())
 def test_unrelated_concurrent_file_preserved(self):
  w=self.work()
  with candidate(self.root) as target:
   p=target/self.workpath(w).relative_to(self.root);d,b=load(p);d['title']='Candidate edit';write(p,d,b);rebuild(target);atomic(self.root/'unrelated.txt','Concurrent unrelated bytes')
  self.assertEqual('Concurrent unrelated bytes',(self.root/'unrelated.txt').read_text());self.clean()
 def test_interrupted_replacements_recover_from_journal(self):
  w=self.work();root=self.root.resolve();real_replace=__import__('os').replace;count=0
  def interrupted(src,dst):
   nonlocal count
   if pathlib.Path(src).name.startswith('.memory-replace-'):
    count+=1
    if count==2:raise OSError('Fictional interruption')
   return real_replace(src,dst)
  with self.assertRaises(OSError),patch('memory.staging.os.replace',interrupted):
   with candidate(root) as target:
    p=target/self.workpath(w).relative_to(self.root);d,b=load(p);d['title']='Recovered edit';write(p,d,b);rebuild(target)
  journal=load_json=json.loads(journal_path(root).read_text());self.assertEqual('incremental',journal['validation_scope']);self.assertTrue(all('before' in c and 'replacement' in c for c in journal['changes']));recover_publication(root);self.assertEqual('Recovered edit',load(self.workpath(w))[0]['title']);self.assertFalse(journal_path(root).exists());self.clean()
 def test_existing_original_cannot_be_replaced(self):
  self.export();src=next(self.root.glob('SOT/EXPORTS/*/original.*'));before=src.read_bytes()
  with self.assertRaises(ValueError):
   with candidate(self.root) as target:atomic(inside(target,src.relative_to(self.root)),'replacement')
  self.assertEqual(before,src.read_bytes())

class Traceability(unittest.TestCase):
 def module(self):
  from tools import build_requirements_matrix
  return build_requirements_matrix
 def test_source_ids_and_text_preserved(self):
  module=self.module();baseline=json.loads((module.ROOT/'contracts/requirements.json').read_text());actual={rid:dict(section=section,text=text) for rid,section,text in module.source_rows()};self.assertEqual(728,len(actual));self.assertEqual(baseline,actual);self.assertEqual(set(json.loads((module.ROOT/'contracts/identities.json').read_text())),set(actual));self.assertNotIn('P1-21-008',actual);self.assertNotIn('P1-18-016',actual);self.assertEqual(module.generate(),(module.ROOT/'contracts/traceability.json').read_text());self.assertEqual(module.partial_report(),(module.ROOT/'contracts/review-obligations.json').read_text())
 def test_missing_or_unverified_evidence_defaults_partial(self):
  module=self.module();rows=list(module.classified_rows(dict(context={},approved_deferrals=[],evidence={})));self.assertTrue(all(r['classification']=='binding' and r['status']=='partial' for r in rows));config=module.default_config();rid=next(k for k,v in config['evidence'].items() if v['status']=='implemented');del config['evidence'][rid];self.assertEqual('partial',next(r for r in module.classified_rows(config) if r['id']==rid)['status'])
 def test_implemented_requires_specific_complete_evidence(self):
  module=self.module();config=module.default_config();rid=next(k for k,v in config['evidence'].items() if v['status']=='implemented')
  for key in ('implementation','verification','applicability','source_sha256','requirement_kind','negative_test_applicability'):
   bad=copy.deepcopy(config);bad['evidence'][rid][key]=[] if key in ('implementation','verification') else ''
   with self.subTest(missing=key),self.assertRaises(ValueError):list(module.classified_rows(bad))
 def test_explicit_evidence_references_resolve(self):
  import ast
  module=self.module()
  def resolves(ref):
   path,sep,symbol=ref.partition(':');p=module.ROOT/path;self.assertTrue(p.is_file(),ref)
   if sep:
    nodes=ast.parse(p.read_text()).body
    for name in symbol.split('.'):
     matched=[node for node in nodes if isinstance(node,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and node.name==name];self.assertEqual(1,len(matched),ref);nodes=matched[0].body
  for row in module.classified_rows():
   self.assertIn(row['classification'],('binding','context','approved_deferral'))
   if row['classification']=='context':self.assertIsNone(row['status'])
   elif row['classification']=='binding':self.assertIn(row['status'],('partial','implemented','blocked'))
   else:self.assertEqual('deferred_provider_specific',row['status'])
   if row['implementation']:
    for ref in row['implementation']+row['positive_tests']+row['negative_tests']:resolves(ref)
    self.assertTrue((module.ROOT/row['procedure']).is_file())
  # Reference existence and declaration completeness do NOT prove behavioral applicability.
 def test_context_and_deferral_cannot_inherit_completion(self):
  module=self.module();config=module.default_config();rows=list(module.classified_rows());self.assertEqual(8,sum(r['status']=='deferred_provider_specific' for r in rows));self.assertTrue(any(r['classification']=='context' for r in rows));config['evidence']['P1-20-001']=copy.deepcopy(next(iter(config['evidence'].values())))
  with self.assertRaises(ValueError):list(module.classified_rows(config))
 def test_one_mapping_does_not_certify_its_section(self):
  module=self.module();config=module.default_config();rid='P1-15-003';del config['evidence'][rid];rows=list(module.classified_rows(config));self.assertEqual('partial',next(r for r in rows if r['id']==rid)['status']);self.assertEqual('implemented',next(r for r in rows if r['id']=='P1-15-004')['status'])

class ExternalDeadlineHorizon(Fixture):
 setup_obligations=DailyHorizons.setup_obligations
 def test_external_deadline_three_days_but_not_sixty(self):
  from memory.audits import audit
  w,at,ids=self.setup_obligations('external_deadline',[3,60]);f=audit(self.root,'daily',at)['findings'];self.assertEqual([(ids[0],'approaching_external_deadline')],[(x['obligation_id'],x['code']) for x in f])
