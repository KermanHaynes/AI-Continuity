"""Fictional fixtures only. Never read provider history or user content."""
import copy,datetime as dt,json,pathlib,shutil,subprocess,tempfile,unittest,uuid
from memory.records import *
from memory.operations import *
from memory.validation import validate
from memory.audits import audit
from memory.schema import SCHEMAS
from memory.transactions import *

SOURCE=pathlib.Path(__file__).resolve().parents[1]
class Fixture(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)/'repo';self.root.mkdir()
  for name in ['schemas','CONTEXT'] :shutil.copytree(SOURCE/name,self.root/name)
  for rel in ['INDEX/PROCESSING','INDEX/CLOSEOUTS','SOT/EXPORTS','KNOWLEDGE','WORK/ITEMS']:(self.root/rel).mkdir(parents=True,exist_ok=True)
  for name,key in [('REGISTRY','records'),('ALIASES','aliases'),('ARTIFACTS','artifacts'),('EXCEPTIONS','exceptions')]:atomic(self.root/f'INDEX/{name}.yaml',yaml.safe_dump({'schema_version':1,key:[]}))
  rebuild(self.root)
 def codes(self):return {f['code'] for f in validate(self.root) if f['severity']=='ERROR'}
 def clean(self):self.assertEqual([], [f for f in validate(self.root) if f['severity']=='ERROR'])
 def export(self,content=b'{"fictional":"fixture"}',previous=None):
  path=pathlib.Path(self.tmp.name)/'native.json';path.write_bytes(content)
  return register_export(self.root,path,'fictional','test','Synthetic complete fixture',completeness='complete',previous_export_ids=previous)
 def sot(self,exp=None,native='conversation-one',messages=None):
  exp=exp or self.export()
  return register_sot(self.root,exp['export_id'],dict(native_conversation_id=native,title='Fictional experiment',messages=messages or [dict(native_message_id='one',role='user',content='Fictional user position.',source_locator='messages[0]'),dict(native_message_id='two',role='assistant',content='Fictional suggestion.',source_locator='messages[1]')]))
 def sotpath(self,sid):return next(p for p,d,_ in collect(self.root) if d.get('sot_id')==sid and d['record_type']=='sot_conversation')
 def work(self,title='Fictional pursuit'):return create_work(self.root,title,'experiment')
 def workpath(self,w):return self.root/f"WORK/ITEMS/work_{w['work_item_id']}.md"
 def savework(self,w):
  p=self.workpath(w);_,b=load(p);write(p,w,b);rebuild(self.root)
 def evidence(self):
  s=self.sot();p=self.sotpath(s['sot_id']);mid=load(p.parent/'MESSAGES.yaml')['messages'][0]['message_id'];return dict(sot_id=s['sot_id'],message_ids=[mid])
 def date(self,ref,kind='external_deadline',at='2026-10-21',zone='America/New_York',state='active',precision='date'):
  return dict(date_id=new_id(),kind=kind,at=at,precision=precision,time_zone=zone,state=state,source_refs=[ref],external_verification=None)

class Foundation(Fixture):
 def test_empty_baseline(self):self.clean()
 def test_schema_drift(self):
  p=self.root/'schemas/work-item.schema.json';p.write_text('{}');self.assertIn('schema_drift',self.codes())
 def test_shared_export_idempotence(self):
  e=self.export();s=self.sot(e);second=self.sot(e,'conversation-two');self.assertNotEqual(s['sot_id'],second['sot_id']);self.assertEqual(s,self.sot(e));self.assertEqual(1,len(list(self.root.glob('SOT/EXPORTS/*/original.*'))));self.clean()
 def test_expansion_preserves_message_ids(self):
  e=self.export();s=self.sot(e);p=self.sotpath(s['sot_id']);before=load(p.parent/'MESSAGES.yaml');expanded=self.export(b'{"fictional":"expanded"}',[e['export_id']]);messages=[dict(native_message_id='one',role='user',content='Fictional user position.',source_locator='messages[0]'),dict(native_message_id='two',role='assistant',content='Fictional suggestion.',source_locator='messages[1]'),dict(native_message_id='three',role='tool',content='Fictional tool result.')];after=self.sot(expanded,messages=messages);self.assertEqual(s['sot_id'],after['sot_id']);self.assertEqual(before['messages'],load(p.parent/'MESSAGES.yaml')['messages'][:2]);self.assertEqual(2,len(list(self.root.glob('SOT/EXPORTS/*/original.*'))));self.clean()
 def test_conflict_preserves_export(self):
  self.sot();e=self.export(b'{"fictional":"conflict"}')
  with self.assertRaises(ValueError):self.sot(e,messages=[dict(native_message_id='one',role='user',content='Contradiction')])
  self.assertEqual(2,len(list(self.root.glob('SOT/EXPORTS/*/original.*'))));self.assertEqual('concurrent_semantic_conflict',load(self.root/'INDEX/EXCEPTIONS.yaml')['exceptions'][0]['classification'])
 def test_hash_mismatch(self):
  self.sot();p=next(self.root.glob('SOT/EXPORTS/*/original.*'));p.write_bytes(b'changed');self.assertIn('source_hash',self.codes())
 def test_source_missing(self):
  self.sot();next(self.root.glob('SOT/EXPORTS/*/original.*')).unlink();self.assertIn('source_missing',self.codes())
 def test_native_original_not_metadata(self):
  self.sot(self.export(b'not valid json {'));self.clean()
 def test_secret_detection(self):
  with self.assertRaises(ValueError):self.export(b'password=abcdefghijklmnop')
  self.assertFalse(list(self.root.glob('SOT/EXPORTS/*/original.*')))
 def test_count_defects(self):
  s=self.sot();p=self.sotpath(s['sot_id'])
  for field,value,code in [('total_messages',99,'message_count'),('role_totals',{'user':99},'role_count'),('user_turns',0,'user_turn_count'),('attachments',1,'attachment_count')]:
   original=load(p);bad=copy.deepcopy(original);bad['counts'][field]=value;write(p,bad);self.assertIn(code,self.codes());write(p,original)
 def test_anchor_missing(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'transcript.md';p.write_text('# Lost content\n');self.assertIn('message_anchor',self.codes())
 def test_anchor_duplicate(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'transcript.md';p.write_text(p.read_text()+p.read_text());self.assertIn('anchor_duplicate',self.codes())
 def test_message_id_duplicate(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'MESSAGES.yaml';d=load(p);d['messages'][1]['message_id']=d['messages'][0]['message_id'];write(p,d);self.assertIn('duplicate_id',self.codes())
 def test_message_ordinal(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'MESSAGES.yaml';d=load(p);d['messages'][0]['ordinal']=3;write(p,d);self.assertIn('message_ordinal',self.codes())
 def test_unknown_export_reference(self):
  s=self.sot();p=self.sotpath(s['sot_id']);s['export_ids']=[new_id()];write(p,s);self.assertIn('export_reference',self.codes())
 def test_topic_reference(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'TOPIC_MAP.yaml';d=load(p);d['topics']=[dict(topic_id=new_id(),label='Fictional topic',provisional=True,message_ids=[new_id()],subject_ids=[],decisions_stated=[],revisions=[],open_questions=[],experiments_and_results=[],artifact_ids=[])];write(p,d);self.assertIn('topic_reference',self.codes())
 def test_multitopic_overlapping_sources(self):
  s=self.sot(messages=[dict(native_message_id=f'message-{n}',role='user' if n%2==0 else 'assistant',content=f'Fictional passage {n}') for n in range(6)]);p=self.sotpath(s['sot_id']);mids=[m['message_id'] for m in load(p.parent/'MESSAGES.yaml')['messages']];topics=[]
  for n in range(3):
   subject=create_subject(self.root,f'Fictional topic {n}',f'fictional-{n}','Fictional scope');associate_source(self.root,subject['subject_id'],dict(sot_id=s['sot_id'],message_ids=mids),'model_suggestion','Unaccepted fictional suggestion')
   topics.append(dict(topic_id=new_id(),label=f'Overlapping topic {n}',provisional=True,message_ids=[mids[n],mids[3],mids[5]],subject_ids=[subject['subject_id']],decisions_stated=[],revisions=[],open_questions=[],experiments_and_results=[],artifact_ids=[]))
  write(p.parent/'TOPIC_MAP.yaml',dict(record_type='topic_map',schema_version=1,sot_id=s['sot_id'],topics=topics));set_processing(self.root,s['sot_id'],'topic_indexing','complete');self.assertEqual(1,len(list(self.root.glob('SOT/EXPORTS/*/original.*'))));self.clean()
 def test_topic_count(self):
  s=self.sot();p=self.sotpath(s['sot_id']);s['states']['topic_indexing']='complete';s['counts']['topics']=99;write(p,s);self.assertIn('topic_count',self.codes())
 def test_artifact_reference(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'MESSAGES.yaml';d=load(p);d['messages'][0]['attachment_ids']=[new_id()];write(p,d);self.assertIn('artifact_reference',self.codes())
 def test_completeness_assertion(self):
  s=self.sot();p=self.sotpath(s['sot_id']);s['states']['native_completeness']='complete';s['capture_gaps']=['Known omission'];write(p,s);self.assertIn('processing_evidence',self.codes())
 def test_not_applicable_reason(self):
  s=self.sot();p=self.sotpath(s['sot_id']);s['state_reasons']={};s['states']['attachment_preservation']='not_applicable';write(p,s);self.assertIn('processing_evidence',self.codes())
 def test_alias_lookup_and_collision(self):
  a=create_subject(self.root,'Fictional Subject','a','Scope');b=create_subject(self.root,'Fictional Subjects','b','Scope');p,d=resolve_subject(self.root,a['subject_id']);d['aliases']=['Alias'];write(p,d);rebuild(self.root);self.assertEqual(a['subject_id'],resolve_subject(self.root,'  ALIAS ')[1]['subject_id']);q,e=resolve_subject(self.root,b['subject_id']);e['aliases']=['alias'];write(q,e);rebuild(self.root)
  with self.assertRaises(ValueError):resolve_subject(self.root,' ALIAS ')
  self.assertIn('alias_collision',self.codes())
 def test_rename_identity(self):
  a=create_subject(self.root,'Old name','a','Scope');p,d=resolve_subject(self.root,a['subject_id']);d['canonical_name']='New name';d['aliases'].append('Old name');write(p,d);rebuild(self.root);self.assertEqual(a['subject_id'],resolve_subject(self.root,'Old name')[1]['subject_id']);self.clean()
 def test_subject_sections(self):
  a=create_subject(self.root,'Name','name','Scope');p,d=resolve_subject(self.root,a['subject_id']);(p.parent/'CURRENT.md').write_text('missing');self.assertIn('subject_section',self.codes())
 def test_integrated_requires_evidence(self):
  a=create_subject(self.root,'Name','name','Scope');p,d=resolve_subject(self.root,a['subject_id']);d['integration_state']='complete';write(p,d);self.assertIn('integration_evidence',self.codes())
 def test_source_reference_missing(self):
  w=self.work();w['source_refs']=[dict(sot_id=new_id(),message_ids=[new_id()])];self.savework(w);self.assertIn('source_reference',self.codes())
 def test_knowledge_evolution_never_promotes(self):
  a=create_subject(self.root,'Fictional decision','decision','Scope');p,_=resolve_subject(self.root,a['subject_id']);current=(p.parent/'CURRENT.md').read_text().replace('Unknown; evidence review required.','Established fictional user position: retain the fictional baseline.',1);atomic(p.parent/'CURRENT.md',current)
  passages=['Use the fictional baseline.','Reject the fictional alternative because its experiment failed.','Possible counterevidence remains unresolved; retain the accepted baseline.']
  for n,classification in enumerate(['established_user_position','rejected_or_superseded','unresolved_interpretation']):
   e=self.export(json.dumps({'fictional':n}).encode());s=self.sot(e,native=f'conversation-{n}',messages=[dict(native_message_id=f'position-{n}',role='user',content=passages[n])]);mid=load(self.sotpath(s['sot_id']).parent/'MESSAGES.yaml')['messages'][0]['message_id'];associate_source(self.root,a['subject_id'],dict(sot_id=s['sot_id'],message_ids=[mid]),classification,passages[n],f'202{n}-01-01')
  self.assertEqual(current,(p.parent/'CURRENT.md').read_text());self.assertEqual(3,len(load(p)['contributions']));self.assertIn('experiment failed',(p.parent/'EVOLUTION.md').read_text());self.assertIn('unresolved',(p.parent/'EVOLUTION.md').read_text());self.clean()
 def test_work_lifecycle_outcome_independent(self):
  w=self.work();ref=self.evidence()
  for status in ('active','completed','awaiting_outcome','closed','active'): w=transition_work(self.root,w['work_item_id'],status,'Fictional explicit instruction',source_refs=[ref])
  self.assertEqual(6,len(w['status_history']));self.assertEqual([],w['outcomes']);self.clean()
 def test_status_history(self):
  w=self.work();w['status']='active';self.savework(w);self.assertIn('status_history',self.codes())
 def test_work_narrative(self):
  w=self.work();write(self.workpath(w),w,'Empty narrative');self.assertIn('work_section',self.codes())
 def test_legacy_work_rejected(self):
  atomic(self.root/'WORK/ITEMS/legacy.yaml','record_type: work_item\n');self.assertIn('legacy_work',self.codes())
 def test_valid_three_level_hierarchy(self):
  a,b,c=self.work('a'),self.work('b'),self.work('c');a['relationships']['children']=[b['work_item_id']];b['relationships'].update(parent=a['work_item_id'],children=[c['work_item_id']]);c['relationships'].update(parent=b['work_item_id'],depends_on=[a['work_item_id']]);self.savework(a);self.savework(b);self.savework(c);self.clean()
 def test_reciprocity(self):
  a,b=self.work('a'),self.work('b');a['relationships']['children']=[b['work_item_id']];self.savework(a);self.assertIn('relationship_reciprocity',self.codes())
 def test_each_cycle_graph(self):
  for kind,code in [('parent','cycle_parent'),('depends_on','cycle_depends_on'),('follows_from','cycle_follows_from')]:
   a,b=self.work(kind+' a'),self.work(kind+' b');a['relationships'][kind]=b['work_item_id'] if kind=='parent' else [b['work_item_id']];b['relationships'][kind]=a['work_item_id'] if kind=='parent' else [a['work_item_id']];self.savework(a);self.savework(b);self.assertIn(code,self.codes())
 def test_date_only_midnight(self):
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref)];self.savework(w)
  before=audit(self.root,'daily',dt.datetime.fromisoformat('2026-10-21T03:59:00+00:00'));after=audit(self.root,'daily',dt.datetime.fromisoformat('2026-10-22T04:01:00+00:00'));self.assertIn('approaching_external_deadline',{x['code'] for x in before['findings']});self.assertIn('overdue_external_deadline',{x['code'] for x in after['findings']});self.assertEqual('2026-10-21',w['dates'][0]['at']);self.clean()
 def test_dst_offsets(self):
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref,at='2026-11-01T01:30:00-04:00',precision='datetime')];self.savework(w);self.clean();w['dates'][0]['at']='2026-11-01T01:30:00-05:00';self.savework(w);self.clean();w['dates'][0]['at']='2026-11-01T01:30:00-06:00';write(self.workpath(w),w,load(self.workpath(w))[1]);self.assertIn('temporal',self.codes())
 def test_bad_zone(self):
  w=self.work();ref=self.evidence();w['dates']=[self.date(ref,zone='Not/AZone')];write(self.workpath(w),w,load(self.workpath(w))[1]);self.assertIn('temporal',self.codes())
 def test_unknown_dates_and_satisfied(self):
  w=self.work();ref=self.evidence();w['dates']=[self.date(ref,at=None,precision='unknown'),self.date(ref,at='2000-01-01',state='satisfied')];self.savework(w);self.assertIn('## Undated work',(self.root/'WORK/AGENDA.md').read_text());self.assertEqual([],audit(self.root,'daily')['findings']);self.clean()
 def test_cancelled_and_occurred_events(self):
  w=self.work();ref=self.evidence();w['events']=[dict(event_id=new_id(),description='Fictional event',at='2000-01-01',precision='date',time_zone='America/New_York',source_refs=[ref],state='cancelled')];self.savework(w);self.assertEqual([],audit(self.root,'daily')['findings']);w['events'][0]['state']='occurred';self.savework(w);self.assertEqual([],audit(self.root,'daily')['findings']);w['events'][0]['state']='scheduled';self.savework(w);self.assertIn('past_scheduled_event',{f['code'] for f in audit(self.root,'daily')['findings']});self.clean()
 def test_proposed_action_not_agenda(self):
  ref=self.evidence();w=self.work();w['actions']=[dict(action_id=new_id(),description='UNACCEPTED PROPOSAL',classification='proposed',source_refs=[ref],state='outstanding',date_ids=[])];self.savework(w);self.assertNotIn('UNACCEPTED PROPOSAL',(self.root/'WORK/AGENDA.md').read_text());w['resumption']['next_action_ids']=[w['actions'][0]['action_id']];self.savework(w);self.assertIn('next_action',self.codes())
 def test_stale_agenda_and_registry(self):
  self.work();atomic(self.root/'WORK/AGENDA.md','stale');atomic(self.root/'INDEX/ALIASES.yaml','schema_version: 1\naliases: [{subject_id: 00000000-0000-4000-8000-000000000000, name: stale}]\n');self.assertIn('agenda_mismatch',self.codes());self.assertIn('registry_coherence',self.codes())
 def test_readonly_audits(self):
  self.sot();self.work()
  def snapshot():return {p.relative_to(self.root).as_posix():digest(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
  before=snapshot()
  for scope in ('daily','weekly','monthly'):audit(self.root,scope)
  self.assertEqual(before,snapshot())
 def test_plan_repair_readonly(self):
  from memory.cli import main
  self.work();p=self.root/'WORK/AGENDA.md';p.write_text('stale');
  import contextlib,io
  with contextlib.redirect_stdout(io.StringIO()):result=main(['--root',str(self.root),'plan-repair'])
  self.assertEqual(0,result);self.assertEqual('stale',p.read_text())
 def test_cli_new_session_lookup(self):
  ref=self.evidence();a=create_subject(self.root,'Fictional subject','subject','Scope');associate_source(self.root,a['subject_id'],ref,'supporting_evidence','Fictional source chain');w=self.work();w['subject_ids']=[a['subject_id']];w['source_refs']=[ref];w['resumption']['current_position']='Fictional pending experiment';self.savework(w);p,d=resolve_subject(self.root,a['subject_id']);d['aliases']=['fictional alias'];write(p,d);rebuild(self.root)
  result=subprocess.run([__import__('sys').executable,'-m','memory.cli','--root',str(self.root),'resolve-subject','fictional alias'],cwd=SOURCE,text=True,capture_output=True);self.assertEqual(0,result.returncode,result.stderr);self.assertEqual(a['subject_id'],json.loads(result.stdout)['subject']['subject_id']);self.assertEqual('Fictional pending experiment',json.loads(result.stdout)['associated_work'][0]['resumption']['current_position']);self.assertTrue(json.loads(result.stdout)['subject']['source_refs'])
 def test_invalid_schema(self):
  w=self.work();p=self.workpath(w);text=p.read_text();p.write_text(text.replace('schema_version: 3','schema_version: 2'));self.assertIn('schema_invalid',self.codes())
 def test_path_escape(self):
  self.export();p=next(self.root.glob('SOT/EXPORTS/*/export.yaml'));d=load(p);d['source_files'][0]['path']='../outside';write(p,d);self.assertIn('path_escape',self.codes())
 def test_exception_references(self):
  raise_exception(self.root,'validation_failed',[new_id()],['Fictional defect']);self.assertIn('exception_reference',self.codes())
 def test_processing_assertion_rejected(self):
  s=self.sot()
  with self.assertRaises(ValueError):set_processing(self.root,s['sot_id'],'knowledge_reconciliation','complete')
  self.assertEqual('pending',load(self.sotpath(s['sot_id']))['states']['knowledge_reconciliation'])
 def test_recovery_idempotent(self):
  e=self.export();original=next(self.root.glob('SOT/EXPORTS/*/original.*')).read_bytes();self.sot(e);self.sot(e);self.assertEqual(original,next(self.root.glob('SOT/EXPORTS/*/original.*')).read_bytes());self.assertEqual(1,len(list(self.root.glob('SOT/*/*/*/*/manifest.yaml'))));self.clean()

class GitTransactions(Fixture):
 def git_init(self):
  git(self.root,'init','-b','review');git(self.root,'config','user.name','Synthetic');git(self.root,'config','user.email','synthetic@example.invalid');self.commit('baseline');remote=pathlib.Path(self.tmp.name)/'remote.git';subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True);git(self.root,'remote','add','origin',str(remote));git(self.root,'push','-u','origin','review')
 def commit(self,message):
  git(self.root,'add','.');git(self.root,'commit','--allow-empty','-m',message);return git(self.root,'rev-parse','HEAD')
 def test_closeout_three_commits_and_later_advance(self):
  self.git_init();self.export();preservation=self.commit('preserve synthetic evidence');work=self.work();derived=self.commit('reconcile synthetic work');git(self.root,'push','origin','review');tid=new_id();state=dict(record_type='processing_state',schema_version=1,transaction_id=tid,starting_sha=preservation,state='verified_complete',affected_record_ids=[work['work_item_id']],reconciliation=[dict(record_id=work['work_item_id'],disposition='changed',evidence=[derived])],preservation_commit=preservation,derived_commit=derived,updated_at=now());write(self.root/f'INDEX/PROCESSING/{tid}.yaml',state);rebuild(self.root);self.commit('record checkpoint');git(self.root,'push','origin','review');receipt=closeout_record(self.root,tid,preservation,derived,'origin','review',[work['work_item_id']],['Synthetic transaction only']);self.commit('subsequent receipt');git(self.root,'push','origin','review');self.commit('later ordinary change');git(self.root,'push','origin','review');self.assertTrue(verify_receipt(self.root,receipt));self.clean();receipt['derived_commit']='f'*40
  with self.assertRaises(ValueError):verify_receipt(self.root,receipt)
 def test_concurrent_unrelated_and_overlap(self):
  self.git_init();base=git(self.root,'rev-parse','HEAD');atomic(self.root/'local.md','local');self.commit('local');git(self.root,'checkout','-b','other',base);atomic(self.root/'remote.md','remote');self.commit('remote');git(self.root,'push','origin','HEAD:review');git(self.root,'checkout','review');plan=concurrency(self.root,base,'origin','review');self.assertEqual('merge_unrelated',plan['state']);git(self.root,'merge','--no-edit',plan['observed_sha']);self.assertEqual('local',(self.root/'local.md').read_text());self.assertEqual('remote',(self.root/'remote.md').read_text());git(self.root,'push','origin','review');base=git(self.root,'rev-parse','HEAD');atomic(self.root/'local.md','local new');self.commit('local new');git(self.root,'checkout','-B','other',base);atomic(self.root/'local.md','remote conflicting');self.commit('remote conflicting');git(self.root,'push','origin','HEAD:review');git(self.root,'checkout','review');self.assertEqual('semantic_review_required',concurrency(self.root,base,'origin','review')['state']);self.assertEqual('local new',(self.root/'local.md').read_text())

if __name__=='__main__':unittest.main()

class FaultInjection(Fixture):
 def test_missing_schema_and_index_schema(self):
  (self.root/'schemas/subject.schema.json').unlink();atomic(self.root/'INDEX/ARTIFACTS.yaml','invalid: true\n');self.assertTrue({'schema_missing','index_schema'}<=self.codes())
 def test_wrong_identity_path(self):
  w=self.work();self.workpath(w).rename(self.root/f'WORK/ITEMS/work_{new_id()}.md');self.assertIn('identity_path',self.codes())
 def test_duplicate_native_conversation(self):
  s=self.sot();p=self.sotpath(s['sot_id']);new=new_id();folder=p.parent.parent/new;shutil.copytree(p.parent,folder);d=load(folder/'manifest.yaml');d['sot_id']=new;write(folder/'manifest.yaml',d);rebuild(self.root);self.assertIn('native_identity',self.codes())
 def test_sot_file_and_attachments_missing(self):
  s=self.sot();p=self.sotpath(s['sot_id']);(p.parent/'TOPIC_MAP.md').unlink();shutil.rmtree(p.parent/'attachments');self.assertTrue({'sot_file_missing','attachments_missing','sot_structure'}<=self.codes())
 def test_child_metadata_identity(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'MESSAGES.yaml';d=load(p);d['sot_id']=new_id();write(p,d);self.assertIn('sot_identity',self.codes())
 def test_topic_readable_view(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'TOPIC_MAP.md';atomic(p,'stale');self.assertIn('topic_view',self.codes())
 def test_native_message_identity(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'MESSAGES.yaml';d=load(p);d['messages'][1]['native_message_id']=d['messages'][0]['native_message_id'];write(p,d);self.assertIn('native_message_identity',self.codes())
 def test_normalized_content(self):
  s=self.sot();p=self.sotpath(s['sot_id']).parent/'transcript.md';p.write_text(p.read_text().replace('Fictional user position.','Changed content.'));self.assertIn('normalized_content',self.codes())
 def test_integration_unknown_id(self):
  s=self.sot();p=self.sotpath(s['sot_id']);s['integrated_subject_ids']=[new_id()];write(p,s);self.assertIn('integration_reference',self.codes())
 def test_invalid_timestamp(self):
  w=self.work();w['updated_at']='yesterday';self.savework(w);self.assertIn('timestamp',self.codes())
 def test_subject_index_and_structure(self):
  s=create_subject(self.root,'Fictional','fictional','Scope');p,_=resolve_subject(self.root,s['subject_id']);atomic(p.parent/'INDEX.md','stale');(p.parent/'SOURCES.md').unlink();self.assertTrue({'subject_index','subject_structure'}<=self.codes())
 def test_unknown_subject_reference(self):
  w=self.work();w['subject_ids']=[new_id()];self.savework(w);self.assertIn('subject_reference',self.codes())
 def test_knowledge_chronology(self):
  ref=self.evidence();s=create_subject(self.root,'Fictional','fictional','Scope');p,d=resolve_subject(self.root,s['subject_id']);d['contributions']=[dict(occurred_at=date,classification='model_suggestion',description='Fictional contribution',source_refs=[ref]) for date in ['2026-01-01','2020-01-01']];write(p,d);self.assertIn('knowledge_chronology',self.codes())
 def test_unknown_work_relationship(self):
  w=self.work();w['relationships']['depends_on']=[new_id()];self.savework(w);self.assertIn('work_relationship',self.codes())
 def test_unknown_action_date(self):
  w=self.work();ref=self.evidence();w['actions']=[dict(action_id=new_id(),description='Fictional explicit action',classification='established',source_refs=[ref],state='outstanding',date_ids=[new_id()])];self.savework(w);self.assertIn('action_date',self.codes())
 def test_missing_derived_view(self):
  (self.root/'INDEX/REGISTRY.yaml').unlink();self.assertIn('derived_view',self.codes())
 def test_processing_unknown_reference_and_false_completion(self):
  tid=new_id();state=dict(record_type='processing_state',schema_version=1,transaction_id=tid,starting_sha='a'*40,state='verified_complete',affected_record_ids=[new_id()],reconciliation=[],preservation_commit=None,derived_commit=None,updated_at=now());write(self.root/f'INDEX/PROCESSING/{tid}.yaml',state);rebuild(self.root);self.assertTrue({'processing_reference','processing_evidence'}<=self.codes())
 def test_receipt_without_evidence(self):
  cid=new_id();d=dict(record_type='closeout',schema_version=1,closeout_id=cid,transaction_id=new_id(),preservation_commit='a'*40,derived_commit='b'*40,remote='origin',branch='review',observed_sha='b'*40,verified_at=now(),verification_mechanism='git-fetch-and-merge-base',affected_record_ids=[],validation_results=['Forged assertion'],limitations=[]);write(self.root/f'INDEX/CLOSEOUTS/{cid}.yaml',d);rebuild(self.root);self.assertIn('receipt_integrity',self.codes())
 def test_artifact_positive_and_corruption(self):
  s=self.sot();p=self.sotpath(s['sot_id']);mid=load(p.parent/'MESSAGES.yaml')['messages'][0]['message_id'];aid=new_id();attachment=p.parent/'attachments/fictional.txt';attachment.write_bytes(b'fictional artifact');a=dict(record_type='artifact',schema_version=1,artifact_id=aid,native_artifact_id='fixture-attachment',sot_id=s['sot_id'],source_refs=[dict(sot_id=s['sot_id'],message_ids=[mid])],path=attachment.relative_to(self.root).as_posix(),sha256=digest(attachment.read_bytes()));check_record(a);atomic(self.root/'INDEX/ARTIFACTS.yaml',yaml.safe_dump(dict(schema_version=1,artifacts=[a])));idx=load(p.parent/'MESSAGES.yaml');idx['messages'][0]['attachment_ids']=[aid];write(p.parent/'MESSAGES.yaml',idx);s['counts']['attachments']=1;s['attachment_inventory']=dict(expected_logical_attachments=1,inventory_verification='verified',inventory_evidence=['synthetic export attachment locator'],registered_logical_attachment_ids=[aid]);s['states']['attachment_preservation']='complete';write(p,s);rebuild(self.root);self.clean();attachment.write_bytes(b'corruption');self.assertIn('source_hash',self.codes())
 def test_no_native_ambiguous_identity(self):
  e=self.export();payload=dict(native_conversation_id=None,source_conversation_locator='conversations[0]',title='Fictional',messages=[dict(role='user',content='Fictional')]);s=register_sot(self.root,e['export_id'],payload);self.assertEqual(s['sot_id'],register_sot(self.root,e['export_id'],payload)['sot_id']);other=self.export(b'{"different":"source"}')
  with self.assertRaises(ValueError):register_sot(self.root,other['export_id'],payload)
 def test_uuid4_required(self):
  w=self.work();p=self.workpath(w);p.write_text(p.read_text().replace(w['work_item_id'],str(uuid.uuid1())));self.assertIn('schema_invalid',self.codes())
 def test_cli_rejects_invalid_source_without_mutation(self):
  from memory.cli import main
  w=self.work();p=pathlib.Path(self.tmp.name)/'bad.json';p.write_text(json.dumps([dict(sot_id=new_id(),message_ids=[new_id()])]))
  from memory.staging import snapshot
  before=snapshot(self.root)
  import contextlib,io
  with contextlib.redirect_stderr(io.StringIO()):result=main(['--root',str(self.root),'transition-work',w['work_item_id'],'active','--reason','Fictional','--evidence',str(p)])
  self.assertEqual(2,result);self.assertEqual(before,snapshot(self.root))
 def test_cli_valid_candidate(self):
  from memory.cli import main
  import contextlib,io
  with contextlib.redirect_stdout(io.StringIO()):result=main(['--root',str(self.root),'create-work','Fictional','--type','experiment'])
  self.assertEqual(0,result);self.clean()
 def test_work_continuity_full_record(self):
  ref=self.evidence();w=self.work();aid=new_id();date=self.date(ref);w.update(external_parties=['Fictional review panel'],actions=[dict(action_id=aid,description='Explicit fictional follow-up',classification='established',source_refs=[ref],state='outstanding',date_ids=[date['date_id']])],dates=[date],outcomes=[dict(outcome_id=new_id(),description='Fictional interim result',classification='partial',occurred_at='2026-01-01',source_refs=[ref])]);w['resumption'].update(current_position='Fictional review pending',last_meaningful_development='Fictional submission acknowledged',next_action_ids=[aid],pending_external_matters=['Fictional external decision'],source_refs=[ref],last_reviewed_at=now());self.savework(w)
  narrative='\n'.join(f'## {section}\n\nFictional experiment was submitted to the fictional review panel; an interim result is recorded, and the external final decision remains pending. The established follow-up is retained with its source evidence.\n' for section in WORK_SECTIONS);write(self.workpath(w),w,narrative)
  for status in ('active','completed','awaiting_outcome'):w=transition_work(self.root,w['work_item_id'],status,'Fictional status evidence',source_refs=[ref])
  self.assertEqual('partial',w['outcomes'][0]['classification']);self.assertIn('Explicit fictional follow-up',(self.root/'WORK/AGENDA.md').read_text());self.clean()
 def test_internal_target_not_external_alert(self):
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref,kind='internal_target',at='2000-01-01')];self.savework(w);self.assertEqual([],audit(self.root,'daily')['findings']);self.assertIn('internal_target',(self.root/'WORK/AGENDA.md').read_text())
 def test_followup_due(self):
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref,kind='follow_up',at='2000-01-01')];self.savework(w);self.assertIn('due_follow_up',{f['code'] for f in audit(self.root,'daily')['findings']})
 def test_original_git_version_immutable(self):
  e=self.export();git(self.root,'init','-b','review');git(self.root,'config','user.name','Synthetic');git(self.root,'config','user.email','synthetic@example.invalid');git(self.root,'add','.');git(self.root,'commit','-m','preserve fixture');p=next(self.root.glob('SOT/EXPORTS/*/original.*'));p.write_bytes(b'changed');meta=next(self.root.glob('SOT/EXPORTS/*/export.yaml'));d=load(meta);d['source_files'][0]['sha256']=digest(p.read_bytes());write(meta,d);self.assertIn('source_immutable',self.codes())

class SchemaContracts(unittest.TestCase):
 def test_each_required_field_and_unknown_properties(self):
  from jsonschema import Draft202012Validator
  def example(schema):
   if 'const' in schema:return schema['const']
   if 'enum' in schema:return schema['enum'][0]
   if 'anyOf' in schema:return example(schema['anyOf'][0])
   typ=schema.get('type');typ=typ[0] if isinstance(typ,list) else typ
   if typ=='object':return {key:example(value) for key,value in schema.get('properties',{}).items()}
   if typ=='array':return [example(schema['items'])] if schema.get('items',{}).get('type')=='object' or schema.get('minItems',0)>0 else []
   if typ=='integer':return 1
   if typ=='boolean':return True
   if typ=='null':return None
   if 'pattern' in schema:return new_id() if '4[0-9a-f]' in schema['pattern'] else 'a'*64
   return 'Fictional schema fixture'
  tested=0
  def inspect(schema,path):
   nonlocal tested
   if schema.get('type')=='object':
    valid=example(schema);validator=Draft202012Validator(schema)
    self.assertEqual([],list(validator.iter_errors(valid)),path)
    for key in schema.get('required',[]):
     bad=copy.deepcopy(valid);del bad[key]
     with self.subTest(contract=path,missing=key):self.assertTrue(list(validator.iter_errors(bad)))
     tested+=1
    bad=copy.deepcopy(valid);bad['unrecognized_field']='fictional'
    if schema.get('additionalProperties') is False:
     with self.subTest(contract=path,extra=True):self.assertTrue(list(validator.iter_errors(bad)))
    for key,value in schema.get('properties',{}).items():inspect(value,path+'/'+key)
   if schema.get('type')=='array':inspect(schema['items'],path+'/*')
  for name,schema in SCHEMAS.items():inspect(schema,name)
  self.assertGreater(tested,200)
 def test_cli_lists_all_required_operations(self):
  from memory.cli import parser
  help=parser().format_help()
  for command in ('validate','new-id','register-export','register-sot','resolve-source','create-subject','resolve-subject','associate-source','create-work','transition-work','render-agenda','set-processing','raise-exception','review-queue','closeout-record','plan-repair','apply-repair'):self.assertIn(command,help)

class RecoveryAndStatus(Fixture):
 def test_status_evidence_required(self):
  w=self.work();w['status']='active';w['status_history'].append(dict(previous='planned',new='active',effective_at=None,reason=None,source_refs=[]));self.savework(w);self.assertIn('status_evidence',self.codes())
 def test_orphan_export_checkpoint_reused(self):
  eid=new_id();p=self.root/f'SOT/EXPORTS/{eid}/original.json';p.parent.mkdir(parents=True);p.write_bytes(b'{"fictional":"fixture"}');e=self.export();self.assertEqual(eid,e['export_id']);self.assertEqual(1,len(list(self.root.glob('SOT/EXPORTS/*/original.*'))));self.clean()
 def test_partial_publication_replay(self):
  from memory.staging import prepare,changed_files,recover_publication,OVERLAYS
  git(self.root,'init','-b','review');root=self.root.resolve();target,info=prepare(root);create_work(target,'Fictional recovered pursuit','experiment');changes=changed_files(target,info);journal=dict(version=2,stage=str(info['stage']),changes=changes);atomic(root/'.git/memory-publish-journal.json',json.dumps(journal));entry=changes[0];dst=root/entry['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(entry['replacement'],dst);OVERLAYS.pop(target);recover_publication(root);self.assertEqual(1,len(list(root.glob('WORK/ITEMS/work_*.md'))));self.clean()
 def test_work_alias_resolution_fresh(self):
  w=self.work();w['aliases']=['Resume alias'];self.savework(w);self.assertEqual(w['work_item_id'],resolve_work(self.root,' RESUME ALIAS ')[1]['work_item_id'])

class AdditionalIntegrity(Fixture):
 def test_orphan_evidence_findings(self):
  p=self.root/f'SOT/EXPORTS/{new_id()}/original.json';p.parent.mkdir(parents=True);p.write_bytes(b'fictional');self.assertIn('orphan_source',self.codes())
  s=self.sot();self.sotpath(s['sot_id']).unlink();self.assertIn('orphan_sot',self.codes())
 def test_date_calendar_horizon(self):
  ref=self.evidence();w=self.work();w['dates']=[self.date(ref,at='2026-10-28T23:30:00-04:00',precision='datetime')];self.savework(w);result=audit(self.root,'daily',dt.datetime.fromisoformat('2026-10-21T00:01:00-04:00'));self.assertIn('approaching_external_deadline',{f['code'] for f in result['findings']})
 def test_complete_expansion_after_partial_export(self):
  e=self.export();p=next(self.root.glob('SOT/EXPORTS/*/export.yaml'));d=load(p);d['capture_completeness']='partial';write(p,d);s=self.sot(e);later=self.export(b'{"fictional":"complete later scope"}',[e['export_id']]);self.sot(later);set_processing(self.root,s['sot_id'],'native_completeness','complete');self.clean()
 def test_readonly_audit_verification_receipt(self):
  for scope in ('daily','weekly','monthly'):self.assertTrue(audit(self.root,scope)['read_only_verified'])


class ContractDocumentation(unittest.TestCase):
 def test_complete_architectural_contract(self):
  self.assertEqual('6d647a8cc13e9ffe8012d11f3e902f249c3d8c853df96e727a63f2a6b3e4493a',digest((SOURCE/'docs/ARCHITECTURE_SPEC.md').read_bytes().split(b'\n\n',1)[1]))
 def test_requirements_traceability(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('matrix',SOURCE/'tools/build_requirements_matrix.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  text=(SOURCE/'contracts/traceability.json').read_text();self.assertEqual(module.generate(),text);ids=[row['id'] for row in json.loads(text)['contract_rows']];self.assertEqual(len(ids),len(set(ids)));self.assertGreater(len(ids),400)
 def test_navigation_and_context(self):
  for path in ('README.md','START_HERE.md','AGENTS.md','docs/ARCHITECTURE_SPEC.md','docs/DESIGN_DECISIONS.md','contracts/traceability.json','docs/SETUP.md','CONTEXT/WORKING_STYLE.md','CONTEXT/WRITING_STYLE.md','CONTEXT/PREFERENCES.md','CONTEXT/RESOURCES.md'):
   self.assertTrue((SOURCE/path).is_file(),path)
  for name in ('SESSION_OPEN','SESSION_CLOSE','SOT_IMPORT','SUBJECT_MAINTENANCE','WORK_MAINTENANCE','RECONCILIATION','AUDIT','RECOVERY'):self.assertTrue((SOURCE/f'docs/OPERATIONS/{name}.md').is_file())
  self.assertIn('unavailable',(SOURCE/'CONTEXT/RESOURCES.md').read_text().casefold())

class AdditionalFaults(Fixture):
 def test_exception_commit_reference(self):
  raise_exception(self.root,'validation_failed',[],['Fictional exception'],last_sha='f'*40);self.assertIn('exception_commit',self.codes())
 def test_monthly_interpretation_concern(self):
  from memory.audits import review_queue
  ref=self.evidence();s=create_subject(self.root,'Fictional','fictional','Scope');associate_source(self.root,s['subject_id'],ref,'unresolved_interpretation','Unresolved fictional evidence');kinds={e['kind'] for e in review_queue(self.root)};self.assertTrue({'prior_interpretation_concern','recent_knowledge_review','pending_integration','older_source_sample'}<=kinds)
 def test_recovery_rejects_competing_local_edit(self):
  from memory.staging import prepare,changed_files,recover_publication,OVERLAYS
  git(self.root,'init','-b','review');root=self.root.resolve();target,info=prepare(root);create_work(target,'Fictional recovery','experiment');changes=changed_files(target,info);atomic(root/'.git/memory-publish-journal.json',json.dumps(dict(version=2,stage=str(info['stage']),changes=changes)));entry=changes[0];dst=root/entry['path'];dst.parent.mkdir(parents=True,exist_ok=True);atomic(dst,'Competing local edit');OVERLAYS.pop(target)
  with self.assertRaises(ValueError):recover_publication(root)
  self.assertTrue((root/'.git/memory-publish-journal.json').is_file());shutil.rmtree(info['stage'])

class NativeProvenance(Fixture):
 def test_identical_no_native_conversations_distinct_locators(self):
  e=self.export();payload=dict(native_conversation_id=None,source_conversation_locator='conversations[0]',title='Fictional',messages=[dict(role='user',content='Fictional identical content')]);a=register_sot(self.root,e['export_id'],payload);payload['source_conversation_locator']='conversations[1]';b=register_sot(self.root,e['export_id'],payload);self.assertNotEqual(a['sot_id'],b['sot_id']);self.clean()
 def test_shorter_later_export_linked_without_truncation(self):
  s=self.sot();later=self.export(b'{"fictional":"shorter partial capture"}');after=self.sot(later,messages=[dict(native_message_id='one',role='user',content='Fictional user position.')]);self.assertEqual(2,after['counts']['total_messages']);self.assertIn(later['export_id'],after['export_ids']);self.clean()

class SchemaEnums(unittest.TestCase):
 def test_every_enum_accepts_only_declared_values(self):
  from jsonschema import Draft202012Validator
  def inspect(schema,path):
   if 'enum' in schema:
    validator=Draft202012Validator(schema)
    for value in schema['enum']:
     with self.subTest(path=path,value=value):self.assertEqual([],list(validator.iter_errors(value)))
    self.assertTrue(list(validator.iter_errors('__invalid_enum__')),path)
   for key,value in schema.get('properties',{}).items():inspect(value,path+'/'+key)
   if 'items' in schema:inspect(schema['items'],path+'/*')
  for name,schema in SCHEMAS.items():inspect(schema,name)
