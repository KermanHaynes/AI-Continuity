"""Regression tests for attachment inventories, linked worktrees, and contract consistency."""
import contextlib, io, json, pathlib, shutil, subprocess, unittest
from unittest.mock import patch
from test_foundation import Fixture, SOURCE
from memory.records import *
from memory.operations import *
from memory.schema import check_record, SCHEMAS
from memory.validation import validate
from memory.staging import candidate, journal_path, recover_publication
from memory.git_paths import metadata_path, git_metadata_dir
from memory.transactions import git, verify_remote
from memory.cli import main

class AttachmentInventory(Fixture):
 def setup_inventory(self,expected=None,verification='unknown',evidence=None):
  native=dict(native_conversation_id='conversation-one',attachments=[{'native_id':f'attachment-{i}'} for i in range(expected or 0)])
  e=self.export(json.dumps(native).encode());payload=dict(native_conversation_id='conversation-one',title='Fictional attachments',messages=[dict(native_message_id='one',role='user',content='Fictional user position.'),dict(native_message_id='two',role='assistant',content='Fictional suggestion.')])
  if expected is not None or verification!='unknown':payload['attachment_inventory']=dict(expected_logical_attachments=expected,inventory_verification=verification,inventory_evidence=evidence or [])
  s=register_sot(self.root,e['export_id'],payload);return s,self.sotpath(s['sot_id']),e
 def attachment(self,s,n=0,native=None):
  src=pathlib.Path(self.tmp.name)/f'attachment-{n}.txt';src.write_bytes(f'Fictional attachment {n}'.encode())
  with candidate(self.root) as target:a=register_artifact(target,s['sot_id'],src,native_artifact_id=native or f'attachment-{n}')
  return a,src
 def test_new_unknown_inventory_stays_pending(self):
  s,p,e=self.setup_inventory();self.assertEqual('pending',s['states']['attachment_preservation']);self.assertIsNone(s['attachment_inventory']['expected_logical_attachments']);self.assertEqual('unknown',s['attachment_inventory']['inventory_verification']);self.clean()
 def test_verified_zero_inventory_allows_not_applicable(self):
  s,p,e=self.setup_inventory(0,'verified',['conversations[0].attachments: empty list verified in original export']);self.assertEqual('not_applicable',s['states']['attachment_preservation']);self.assertTrue(s['state_reasons']['attachment_preservation']);self.assertEqual([],s['attachment_inventory']['registered_logical_attachment_ids']);self.clean()
 def test_zero_without_verified_evidence_cannot_skip_preservation(self):
  s,p,e=self.setup_inventory(0,'partial');self.assertEqual('pending',s['states']['attachment_preservation']);s['states']['attachment_preservation']='not_applicable';s['state_reasons']['attachment_preservation']='Claimed none';write(p,s);self.assertIn('attachment_completion',self.codes())
 def test_verified_inventory_requires_count_and_evidence(self):
  s,p,e=self.setup_inventory();s['attachment_inventory']['inventory_verification']='verified';write(p,s);self.assertIn('attachment_inventory',self.codes())
  with self.assertRaises(ValueError):set_attachment_inventory(self.root,s['sot_id'],0,'verified',[])
 def test_one_of_several_preserved_is_not_complete(self):
  s,p,e=self.setup_inventory(3,'verified',['conversations[0].attachments: three logical attachments']);a,_=self.attachment(s);d=load(p);self.assertEqual(1,d['counts']['attachments']);self.assertEqual([a['artifact_id']],d['attachment_inventory']['registered_logical_attachment_ids']);self.assertEqual('pending',d['states']['attachment_preservation'])
  with self.assertRaises(ValueError):set_processing(self.root,s['sot_id'],'attachment_preservation','complete')
  self.assertEqual('pending',load(p)['states']['attachment_preservation']);self.clean()
 def test_completed_inventory_requires_explicit_completion(self):
  s,p,e=self.setup_inventory(2,'verified',['conversations[0].attachments: both source entries reviewed']);a,_=self.attachment(s,0);b,_=self.attachment(s,1);self.assertEqual('pending',load(p)['states']['attachment_preservation']);set_processing(self.root,s['sot_id'],'attachment_preservation','complete');d=load(p);self.assertEqual('complete',d['states']['attachment_preservation']);self.assertEqual(2,d['counts']['attachments']);self.assertEqual({a['artifact_id'],b['artifact_id']},set(d['attachment_inventory']['registered_logical_attachment_ids']));self.clean()
 def test_unknown_inventory_cannot_be_completed_after_registration(self):
  s,p,e=self.setup_inventory();a,_=self.attachment(s)
  with self.assertRaises(ValueError):set_processing(self.root,s['sot_id'],'attachment_preservation','complete')
  self.assertIsNone(load(p)['attachment_inventory']['expected_logical_attachments']);self.clean()
 def test_expanded_export_reopens_inventory_review(self):
  s,p,e=self.setup_inventory(1,'verified',['source attachment inventory']);a,_=self.attachment(s);set_processing(self.root,s['sot_id'],'attachment_preservation','complete');later=self.export(b'{"expanded":true,"attachments":["old","new"]}',[e['export_id']]);payload=dict(native_conversation_id='conversation-one',title='Expanded fictional conversation',messages=[dict(native_message_id='one',role='user',content='Fictional user position.'),dict(native_message_id='two',role='assistant',content='Fictional suggestion.'),dict(native_message_id='three',role='user',content='Additional fictional evidence')],attachment_inventory=dict(expected_logical_attachments=0,inventory_verification='verified',inventory_evidence=['old declaration']))
  d=register_sot(self.root,later['export_id'],payload);self.assertEqual('pending',d['states']['attachment_preservation']);self.assertEqual('unknown',d['attachment_inventory']['inventory_verification']);self.assertIsNone(d['attachment_inventory']['expected_logical_attachments']);self.assertEqual([a['artifact_id']],d['attachment_inventory']['registered_logical_attachment_ids']);self.clean()
 def test_conflict_versions_preserve_one_logical_identity(self):
  s,p,e=self.setup_inventory(1,'verified',['one logical source attachment']);a,src=self.attachment(s);src.write_bytes(b'Conflicting fictional version')
  with self.assertRaises(EvidenceConflict):
   with candidate(self.root) as target:register_artifact(target,s['sot_id'],src,native_artifact_id='attachment-0')
  entries=load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts'];version=next(v for v in entries if v.get('conflicts_with'));self.assertEqual(a['artifact_id'],version['conflicts_with']);self.assertEqual(2,len(entries));self.assertEqual(1,load(p)['counts']['attachments']);self.assertEqual([a['artifact_id']],load(p)['attachment_inventory']['registered_logical_attachment_ids']);self.assertEqual(a['sha256'],digest((self.root/a['path']).read_bytes()));self.assertEqual(src.read_bytes(),(self.root/version['path']).read_bytes());self.assertTrue(any(x['status']=='open' for x in load(self.root/'INDEX/EXCEPTIONS.yaml')['exceptions']))
  with self.assertRaises(ValueError):set_processing(self.root,s['sot_id'],'attachment_preservation','complete')
  self.clean()
 def test_conflict_cannot_be_counted_as_another_logical_attachment(self):
  s,p,e=self.setup_inventory(1,'verified',['one source entry']);a,src=self.attachment(s);src.write_bytes(b'Conflicting version')
  with self.assertRaises(EvidenceConflict):
   with candidate(self.root) as target:register_artifact(target,s['sot_id'],src,native_artifact_id='attachment-0')
  d=load(p);version=next(v for v in load(self.root/'INDEX/ARTIFACTS.yaml')['artifacts'] if v.get('conflicts_with'));d['counts']['attachments']=2;d['attachment_inventory']['registered_logical_attachment_ids'].append(version['artifact_id']);write(p,d);self.assertTrue({'attachment_count','attachment_inventory'}<=self.codes())
 def test_missing_identity_or_corrupt_bytes_prevent_completion(self):
  s,p,e=self.setup_inventory(1,'verified',['one reviewed source entry']);a,_=self.attachment(s);(self.root/a['path']).write_bytes(b'Corrupt')
  with self.assertRaises(ValueError):set_processing(self.root,s['sot_id'],'attachment_preservation','complete')
  self.assertIn('source_hash',self.codes());d=load(p);d['attachment_inventory']['registered_logical_attachment_ids']=[new_id()];write(p,d);self.assertIn('attachment_inventory',self.codes())
 def test_inventory_cli_declaration_is_explicit_and_staged(self):
  s,p,e=self.setup_inventory();out=io.StringIO()
  with contextlib.redirect_stdout(out):code=main(['--root',str(self.root),'set-attachment-inventory',s['sot_id'],'--expected','0','--verification','verified','--evidence','source attachment list reviewed empty'])
  self.assertEqual(0,code);self.assertEqual('incremental',json.loads(out.getvalue())['validation_scope']);self.assertEqual('not_applicable',load(p)['states']['attachment_preservation']);self.clean()

class LinkedWorktrees(Fixture):
 def setup_worktrees(self):
  git(self.root,'init','-b','review');git(self.root,'config','user.name','Synthetic');git(self.root,'config','user.email','synthetic@example.invalid');git(self.root,'add','.');git(self.root,'commit','-m','Fictional foundation');linked=pathlib.Path(self.tmp.name)/'linked';git(self.root,'worktree','add','-b','linked-review',str(linked));return linked.resolve()
 def test_linked_update_uses_git_resolved_lock_and_journal(self):
  linked=self.setup_worktrees();metadata=git_metadata_dir(linked);self.assertFalse(metadata.is_relative_to(linked));self.assertEqual(pathlib.Path(git(linked,'rev-parse','--path-format=absolute','--git-path','memory-publish-journal.json')),journal_path(linked));self.assertNotEqual(journal_path(self.root),journal_path(linked))
  with lock(linked):
   self.assertTrue(metadata_path(linked,'.memory.lock').is_file())
   with candidate(linked) as target:w=create_work(target,'Fictional linked pursuit','experiment')
  self.assertTrue((linked/f"WORK/ITEMS/work_{w['work_item_id']}.md").is_file());self.assertFalse(journal_path(linked).exists());self.assertFalse(list(linked.glob('*journal*')));self.assertFalse(any(f['severity']=='ERROR' for f in validate(linked)));self.assertNotIn('memory-publish-journal',git(linked,'status','--porcelain'))
 def test_linked_interruption_and_recovery_never_track_journal(self):
  linked=self.setup_worktrees();real_replace=__import__('os').replace;count=0
  def fail_after_one(src,dst):
   nonlocal count
   if pathlib.Path(src).name.startswith('.memory-replace-'):
    count+=1
    if count==2:raise OSError('Fictional interruption')
   return real_replace(src,dst)
  with self.assertRaises(OSError),patch('memory.staging.os.replace',fail_after_one):
   with lock(linked),candidate(linked) as target:create_work(target,'Fictional recovered linked pursuit','experiment')
  journal=journal_path(linked);self.assertTrue(journal.is_file());self.assertTrue(journal.is_relative_to(git_metadata_dir(linked)));self.assertFalse(journal.is_relative_to(linked));self.assertNotIn('journal',git(linked,'status','--porcelain'))
  with lock(linked):recover_publication(linked)
  self.assertFalse(journal.exists());self.assertEqual(1,len(list(linked.glob('WORK/ITEMS/work_*.md'))));git(linked,'add','.');self.assertNotIn('journal',git(linked,'diff','--cached','--name-only'));self.assertFalse(any(f['severity']=='ERROR' for f in validate(linked)))
 def test_content_escape_stays_rejected_despite_external_git_metadata(self):
  linked=self.setup_worktrees()
  with self.assertRaises(ValueError):inside(linked,'../outside.md')
  outside=pathlib.Path(self.tmp.name)/'outside.txt';outside.write_text('Fictional outside content');(linked/'escape').symlink_to(outside)
  with self.assertRaises(ValueError):inside(linked,'escape')
  self.assertTrue(metadata_path(linked,'.memory.lock').parent.is_dir());self.assertEqual('Fictional outside content',outside.read_text())

class FoundationContracts(Fixture):
 def test_layout_and_runtime_contract(self):
  s=self.sot();subject=create_subject(self.root,'Fictional subject','fictional','Scope');w=self.work();sot_folder=self.sotpath(s['sot_id']).parent;subject_folder=self.root/'KNOWLEDGE/fictional'
  # Every generated canonical component is present, including both identity metadata and readable views.
  for name in ('manifest.yaml','MESSAGES.yaml','transcript.md','TOPIC_MAP.yaml','TOPIC_MAP.md','attachments'):self.assertTrue((sot_folder/name).exists(),name)
  for name in ('subject.yaml','INDEX.md','CURRENT.md','EVOLUTION.md','SOURCES.md','ARTIFACTS'):self.assertTrue((subject_folder/name).exists(),name)
  self.assertTrue(self.workpath(w).read_text().startswith('---\n'));self.assertIsNone(s['counts']['topics']);self.assertEqual(3,w['schema_version']);self.assertEqual([],subject['aliases']);self.assertEqual([],subject['classifications']);self.assertEqual('unknown',s['attachment_inventory']['inventory_verification'])
  for rel in ('README.md','START_HERE.md','AGENTS.md','CONTEXT/WORKING_STYLE.md','CONTEXT/WRITING_STYLE.md','CONTEXT/PREFERENCES.md','CONTEXT/RESOURCES.md','TEMPLATES','schemas','tools','tests','.github/workflows','docs/ARCHITECTURE_SPEC.md','docs/DESIGN_DECISIONS.md','contracts/traceability.json','docs/SETUP.md'):
   self.assertTrue((SOURCE/rel).exists(),rel)
  for name in ('SESSION_OPEN','SESSION_CLOSE','SOT_IMPORT','SUBJECT_MAINTENANCE','WORK_MAINTENANCE','RECONCILIATION','AUDIT','RECOVERY'):self.assertTrue((SOURCE/f'docs/OPERATIONS/{name}.md').is_file())
  for name in ('daily-watch','monthly-review'):self.assertEqual({'contents':'read'},load(SOURCE/f'.github/workflows/{name}.yml')['permissions'])
  self.assertEqual({'contents':'read','actions':'read'},load(SOURCE/'.github/workflows/weekly-audit.yml')['permissions']);self.assertEqual({'contents':'read'},load(SOURCE/'.github/workflows/foundation-checks.yml')['permissions']);self.assertEqual('PyYAML>=6.0,<7\njsonschema>=4.20,<5',(SOURCE/'requirements.txt').read_text().strip());self.clean()
 def test_cli_roundtrip_and_mechanical_modes(self):
  def call(*args):
   out=io.StringIO();err=io.StringIO()
   with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):code=main(['--root',str(self.root),*map(str,args)])
   self.assertEqual(0,code,err.getvalue());value=json.loads(out.getvalue());return value.get('result',value) if isinstance(value,dict) else value
  identifier=call('new-id')['id'];self.assertEqual(4,__import__('uuid').UUID(identifier).version)
  raw=pathlib.Path(self.tmp.name)/'fictional.json';raw.write_text('{"fictional":"source"}');e=call('register-export',raw,'--provider','fictional','--environment','synthetic','--scope','Fictional capture');mapping=pathlib.Path(self.tmp.name)/'mapping.json';mapping.write_text(json.dumps(dict(native_conversation_id='fixture',title='Fictional source',messages=[dict(role='user',native_message_id='one',content='Fictional message',source_locator='messages[0]')])));s=call('register-sot',e['export_id'],mapping);mid=load(self.sotpath(s['sot_id']).parent/'MESSAGES.yaml')['messages'][0]['message_id'];self.assertTrue(call('resolve-source',s['sot_id'],'--message-id',mid)['transcript'].endswith('#msg-'+mid))
  subject=call('create-subject','Fictional subject','--slug','fictional-subject','--scope','Fictional scope');call('associate-source',subject['subject_id'],s['sot_id'],mid,'--classification','model_suggestion','--description','Fictional unaccepted suggestion');self.assertEqual(subject['subject_id'],call('resolve-subject','Fictional subject')['subject']['subject_id'])
  w=call('create-work','Fictional pursuit','--type','experiment');refs=pathlib.Path(self.tmp.name)/'refs.json';refs.write_text(json.dumps([dict(sot_id=s['sot_id'],message_ids=[mid])]));updated=call('transition-work',w['work_item_id'],'active','--reason','Fictional instruction','--evidence',refs);self.assertEqual(2,len(updated['status_history']));self.assertEqual('active',call('resolve-work',w['work_item_id'])['work']['status']);call('render-agenda');call('set-processing',s['sot_id'],'topic_indexing','complete');self.assertEqual(0,load(self.sotpath(s['sot_id']))['counts']['topics'])
  exc=call('raise-exception','fictional_review', '--evidence','Fictional known limitation');self.assertTrue(any(x.get('record_id')==exc['exception_id'] for x in call('review-queue')));agenda=self.root/'WORK/AGENDA.md';agenda.write_text('stale');plan=call('plan-repair');self.assertEqual('stale',agenda.read_text());self.assertEqual([],plan['semantic_repairs']);call('apply-repair','--authorized');self.assertNotEqual('stale',agenda.read_text());self.assertFalse(any(f['severity']=='ERROR' for f in call('validate')))
 def test_agenda_visibility_dates_and_established_actions(self):
  ref=self.evidence();items=[]
  for status in ('planned','active','waiting','blocked','paused','awaiting_outcome','completed','closed'):
   w=self.work('Fictional '+status)
   if status!='planned':w=transition_work(self.root,w['work_item_id'],status,'Fictional status',source_refs=[ref])
   items.append(w)
  w=items[0];established=new_id();proposed=new_id();w['actions']=[dict(action_id=established,description='Established fictional next action',classification='established',source_refs=[ref],state='outstanding',date_ids=[]),dict(action_id=proposed,description='Unaccepted fictional proposal',classification='proposed',source_refs=[ref],state='outstanding',date_ids=[])];w['resumption'].update(next_action_ids=[established],pending_external_matters=['Fictional external result pending']);w['dates']=[self.date(ref,kind='external_deadline',at='2026-10-25'),self.date(ref,kind='internal_target',at='2026-10-23'),self.date(ref,kind='follow_up',at='2026-10-24')];self.savework(w);text=(self.root/'WORK/AGENDA.md').read_text()
  for item in items[:6]:self.assertIn(item['work_item_id'],text)
  for item in items[6:]:self.assertNotIn(item['work_item_id'],text)
  self.assertIn('Established fictional next action',text);self.assertNotIn('Unaccepted fictional proposal',text);self.assertIn('Fictional external result pending',text);self.assertIn('undetermined',text);self.assertIn('America/New_York',text);self.assertIn('ITEMS/work_'+w['work_item_id']+'.md',text);self.assertLess(text.index('internal_target:'),text.index('follow_up:'));self.assertLess(text.index('follow_up:'),text.index('external_deadline:'));self.assertIn('## Undated work',text);self.clean()
 def test_related_links_and_action_evidence_are_enforced(self):
  a,b=self.work('Parent'),self.work('Child');a['relationships'].update(children=[b['work_item_id']],related_to=[b['work_item_id']]);b['relationships'].update(parent=a['work_item_id'],related_to=[a['work_item_id']],depends_on=[a['work_item_id']],follows_from=[a['work_item_id']]);self.savework(a);self.savework(b);self.clean();b['relationships']['related_to']=[];self.savework(b);self.assertIn('relationship_reciprocity',self.codes());b['relationships']['related_to']=[a['work_item_id']];b['actions']=[dict(action_id=new_id(),description='Fictional action',classification='established',source_refs=[dict(sot_id=new_id(),message_ids=[new_id()])],state='outstanding',date_ids=[])];self.savework(b);self.assertIn('source_reference',self.codes())
 def test_complete_processing_requires_real_ordered_checkpoint_commits(self):
  tid=new_id();state=dict(record_type='processing_state',schema_version=1,transaction_id=tid,starting_sha='a'*40,state='verified_complete',affected_record_ids=[],reconciliation=[],preservation_commit='b'*40,derived_commit='c'*40,updated_at=now());write(self.root/f'INDEX/PROCESSING/{tid}.yaml',state);rebuild(self.root);self.assertIn('processing_evidence',self.codes())
 def test_known_occurrence_order_uses_instants_and_preserves_unknowns(self):
  ref=self.evidence();subject=create_subject(self.root,'Fictional chronology','chronology','Scope');associate_source(self.root,subject['subject_id'],ref,'supporting_evidence','Later instant','2026-10-21T01:00:00+00:00');associate_source(self.root,subject['subject_id'],ref,'supporting_evidence','Earlier instant','2026-10-21T02:00:00+02:00');associate_source(self.root,subject['subject_id'],ref,'unresolved_interpretation','Unknown occurrence');p,d=resolve_subject(self.root,subject['subject_id']);self.assertEqual(['Earlier instant','Later instant','Unknown occurrence'],[x['description'] for x in d['contributions']]);self.assertIsNone(d['contributions'][-1]['occurred_at']);self.clean()

class AdditionalFoundationChecks(Fixture):
 def test_canonical_path_cannot_change_metadata_record_type(self):
  e=self.export();subject=create_subject(self.root,'Fictional disguised subject','disguised','Scope');folder=self.root/'KNOWLEDGE/disguised';export_folder=self.root/'SOT/EXPORTS'/e['export_id']
  for path in folder.iterdir():
   if path.name=='subject.yaml':continue
   if path.is_dir():shutil.copytree(path,export_folder/path.name)
   else:shutil.copyfile(path,export_folder/path.name)
  write(export_folder/'export.yaml',subject);shutil.rmtree(folder);rebuild(self.root);self.assertIn('schema_invalid',self.codes())
 def test_workflow_history_coverage_and_audit_context(self):
  from memory.audits import missing_audit_executions,audit
  at=dt.datetime.fromisoformat('2026-10-21T12:00:00+00:00');self.assertEqual(3,len(missing_audit_executions([],at)));runs=[dict(path='.github/workflows/'+name,status='completed',conclusion='success',created_at=at.isoformat()) for name in ('daily-watch.yml','weekly-audit.yml','monthly-review.yml')];self.assertEqual([],missing_audit_executions(runs,at));runs[0]['created_at']='2020-01-01T00:00:00+00:00';self.assertEqual(['daily-watch.yml'],missing_audit_executions(runs,at))
  with patch.dict(__import__('os').environ,{'GITHUB_SHA':'a'*40,'GITHUB_RUN_ID':'fictional-run'}):report=audit(self.root,'daily',at)
  self.assertEqual('a'*40,report['workflow_sha']);self.assertEqual('fictional-run',report['run_id']);self.assertEqual(at.isoformat(),report['executed_at']);self.assertTrue(report['read_only_verified']);self.assertTrue(report['limitations'])


class AcceptanceEvidence(unittest.TestCase):
 def test_every_source_unit_is_classified_with_typed_evidence(self):
  from tools import build_requirements_matrix as matrix
  rows=list(matrix.classified_rows());self.assertEqual(728,len(rows));self.assertEqual(8,sum(r['classification']=='approved_deferral' for r in rows))
  for row in rows:
   with self.subTest(requirement=row['id']):
    if row['classification']!='binding':continue
    self.assertIn(row['requirement_kind'],matrix.KINDS[:-1]);self.assertNotEqual('traceability_gap',row['issue_type']);self.assertTrue(row['verification'])
    for proof in row['verification']:
     self.assertIn(proof['type'],matrix.PROOFS);self.assertTrue(proof['assertion']);path=proof['ref'].split(':')[0];self.assertTrue((SOURCE/path).is_file(),proof['ref'])
     if 'schema_pointer' in proof:
      schema,pointer=proof['schema_pointer'].split('#');node=json.loads((SOURCE/f'schemas/{schema}.schema.json').read_text())
      for key in pointer.strip('/').split('/'):node=node[key]
      self.assertIsInstance(node,dict)
    if row['requirement_kind']=='human_evidence_review':self.assertEqual('partial',row['status']);self.assertEqual('human_review_required',row['issue_type'])
    elif row['requirement_kind'] in ('operating_procedure','governance_restriction'):
     self.assertTrue(any(p['type'] in ('source_review','procedure_review','test_assertion','transaction_verification') for p in row['verification']))
 def test_human_or_unverified_proof_cannot_be_labeled_implemented(self):
  import copy
  from tools import build_requirements_matrix as matrix
  config=matrix.default_config();rid=next(k for k,v in config['evidence'].items() if v['requirement_kind']=='human_evidence_review');bad=copy.deepcopy(config);bad['evidence'][rid]['status']='implemented'
  with self.assertRaises(ValueError):list(matrix.classified_rows(bad))
  rid=next(k for k,v in config['evidence'].items() if v['status']=='implemented');bad=copy.deepcopy(config);bad['evidence'][rid]['verification']=[]
  with self.assertRaises(ValueError):list(matrix.classified_rows(bad))
