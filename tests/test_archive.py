"""Necessary regression checks for exact archive rendering and review boundaries."""
import hashlib
import unittest
import uuid
from memory.archive import render_conversation, review_findings
from memory.schema import check_record

class ArchiveContract(unittest.TestCase):
    def test_exact_body_bytes_and_branch_identity(self):
        first,second=str(uuid.uuid4()),str(uuid.uuid4())
        text='  leading\r\n\r\n| a | b |\r\n```\r\n### msg-not-an-anchor\r\n```\r\ntrailing  '
        raw,entries=render_conversation(str(uuid.uuid4()),'Conversation','claude','native',None,[
            {'message_id':first,'role':'user','text':text,'parent_message_id':None},
            {'message_id':second,'role':'assistant','text':'Answer\n\n','parent_message_id':first}])
        for original,entry in zip([text,'Answer\n\n'],entries):
            span=entry['transcript_byte_range']; body=raw[span['start']:span['end']]
            self.assertEqual(body,original.encode());self.assertEqual(hashlib.sha256(body).hexdigest(),entry['content_sha256'])
        self.assertEqual(entries[1]['parent_message_id'],first)

    def test_archive_pending_and_review_coverage(self):
        mid=str(uuid.uuid4())
        index={'messages':[{'message_id':mid}]}
        manifest={'review':{'status':'unreviewed','history':[],'pending_message_ids':[mid]},'states':dict.fromkeys(['topic_indexing','knowledge_reconciliation','work_reconciliation'],'pending'),'integrated_subject_ids':[],'integrated_work_item_ids':[],'topic_map_file':None,'topic_map_markdown_file':None}
        self.assertEqual(review_findings(manifest,index),[])
        manifest['review']['status']='reviewed'
        self.assertTrue(review_findings(manifest,index))
        manifest['review']['status']='unreviewed';manifest['states']['knowledge_reconciliation']='complete'
        self.assertTrue(any('pending' in x for x in review_findings(manifest,index)))

    def test_visible_surrogate_is_not_silently_replaced(self):
        with self.assertRaises(UnicodeEncodeError):
            render_conversation(str(uuid.uuid4()),'Title','claude',None,None,[{'message_id':str(uuid.uuid4()),'role':'user','text':'\ud800'}])

from test_foundation import Fixture
from memory.records import load,write
from memory.archive import rebuild_navigation

class ArchiveValidation(Fixture):
    def test_archive_without_topic_or_attachment_directories(self):
        import shutil
        source=self.sot();path=self.sotpath(source['sot_id'])
        index=load(path.parent/'MESSAGES.yaml')
        original_work=(self.root/'WORK/AGENDA.md').read_bytes()
        inputs=[dict(m,text='Exact\r\nbody '+str(i)) for i,m in enumerate(index['messages'])]
        body,index['messages']=render_conversation(source['sot_id'],source['title'],source['provider'],source['native_conversation_id'],None,inputs)
        (path.parent/'transcript.md').write_bytes(body)
        write(path.parent/'MESSAGES.yaml',index)
        source.update(archive_mode='archive_only',transcript_format='conversation_v1',topic_map_file=None,topic_map_markdown_file=None,review={'status':'unreviewed','history':[],'pending_message_ids':[m['message_id'] for m in index['messages']]})
        write(path,source)
        (path.parent/'TOPIC_MAP.yaml').unlink();(path.parent/'TOPIC_MAP.md').unlink();shutil.rmtree(path.parent/'attachments')
        rebuild_navigation(self.root)
        self.clean()
        self.assertEqual(original_work,(self.root/'WORK/AGENDA.md').read_bytes())
        self.assertEqual('unreviewed',load(path)['review']['status'])
        # Body corruption must fail despite a valid archive-only state.
        (path.parent/'transcript.md').write_bytes(body.replace(b'Exact',b'Wrong',1))
        self.assertIn('normalized_content',self.codes())

    def test_snapshot_extension_and_visible_conflict_preserves_original_body(self):
        from memory.archive import register_archive_conversation
        export=self.export()
        def payload(text='Old exact answer', extra=False):
            rows=[{'identity_key':'native:first','native_message_id':'first','role':'assistant','original_timestamp':None,'parent_native_message_id':None,'text':text,'source_locator':'/messages/0','parts':[]}]
            if extra:rows.append({'identity_key':'native:second','native_message_id':'second','role':'user','original_timestamp':None,'parent_native_message_id':'first','text':'New question','source_locator':'/messages/1','parts':[]})
            return {'provider':'fictional','environment':'test','native_conversation_id':'native','title':'Title','original_started_at':None,'original_ended_at':None,'messages':rows,'limitations':[]}
        one=register_archive_conversation(self.root,export,payload());rebuild_navigation(self.root)
        path=self.sotpath(one['sot_id']);first_id=load(path.parent/'MESSAGES.yaml')['messages'][0]['message_id']
        two=register_archive_conversation(self.root,export,payload(extra=True));rebuild_navigation(self.root)
        self.assertEqual(first_id,load(path.parent/'MESSAGES.yaml')['messages'][0]['message_id'])
        self.assertEqual(2,two['counts']['total_messages']);self.clean()
        conflict=register_archive_conversation(self.root,export,payload('Conflicting text',True));rebuild_navigation(self.root)
        self.assertEqual('blocked',conflict['states']['normalization'])
        self.assertIn(b'Old exact answer',(path.parent/'transcript.md').read_bytes())
        self.assertNotIn(b'Conflicting text',(path.parent/'transcript.md').read_bytes())
        self.assertTrue(conflict['capture_gaps']);self.clean()

    def test_local_only_source_is_explicit_and_not_remote_complete(self):
        from memory.archive import register_archive_export,register_archive_conversation
        from memory.records import digest
        import pathlib
        source=pathlib.Path(self.tmp.name)/'original.json';source.write_bytes(b'{"fictional":"local-only original"}')
        export=register_archive_export(self.root,source,'fictional','test',digest(source.read_bytes()),['LFS storage capacity unverified'])
        self.assertEqual('local_only',export['publication']['status'])
        self.assertFalse((self.root/export['source_files'][0]['path']).exists())
        rebuild_navigation(self.root);self.clean()
        from memory.validation import validate
        self.assertIn('source_local_only',{f['code'] for f in validate(self.root)})

class NativeBoundaryFidelity(unittest.TestCase):
    def test_whitespace_text_block_between_dialogue_blocks_is_preserved(self):
        from memory.native_dialogue import Capture
        capture=Capture('archive','native','claude','Title',['source'])
        record=capture.record('source','/message','native-message','assistant',None)
        for n,text in enumerate(['Paragraph one.','\n\n','Paragraph two.']):capture.text(record,text,'/content/'+str(n)+'/text','ASSISTANT')
        capture.finish_message(record,'ASSISTANT')
        self.assertEqual('Paragraph one.\n\nParagraph two.',''.join(p['text'] for p in capture.turns[0]['parts']))

    def test_explicit_subagent_session_is_native_evidence_not_human_dialogue(self):
        from memory.native_dialogue import Capture,stream_dialogue
        capture=Capture('archive','native','codex','Title',['source'])
        rows=[(1,{'type':'session_meta','payload':{'id':'native','source':{'subagent':{'parent_thread_id':'parent'}}}}),(2,{'type':'response_item','payload':{'type':'message','role':'user','content':[{'type':'input_text','text':'Delegated agent task'}]}})]
        stream_dialogue(capture,{'provider':'codex','id':'source'},rows)
        self.assertTrue(capture.context['native_only_auxiliary_agent']);self.assertEqual([],capture.turns)

class SnapshotChronology(Fixture):
    def test_disjoint_dated_snapshots_use_native_times_without_interleaving_guesses(self):
        from memory.archive import register_archive_conversation
        def payload(ids,seconds,known=True):
            return {'provider':'fictional','environment':'test','native_conversation_id':'native','title':'Title','original_started_at':'2020-01-01T00:00:00+00:00' if known else None,'original_ended_at':None,'limitations':[],'messages':[{'identity_key':'native:'+identity,'native_message_id':identity,'role':'user','original_timestamp':f'2020-01-01T00:00:0{second}+00:00' if known else None,'parent_native_message_id':None,'text':identity,'source_locator':'/messages/'+str(n),'parts':[]} for n,(identity,second) in enumerate(zip(ids,seconds))]}
        first=self.export();one=register_archive_conversation(self.root,first,payload(['a','c'],[0,2]));second=self.export(b'{"fictional":"second"}')
        register_archive_conversation(self.root,second,payload(['b','d'],[1,3]));rebuild_navigation(self.root)
        path=self.sotpath(one['sot_id']);rows=load(path.parent/'MESSAGES.yaml')['messages']
        self.assertEqual(['a','b','c','d'],[m['native_message_id'] for m in rows]);self.clean()

class AttachmentOnlyFidelity(unittest.TestCase):
    def test_attachment_only_user_identity_is_preserved_without_fabricated_text(self):
        from memory.native_dialogue import Capture,stream_dialogue
        capture=Capture('archive','native','codex',None,['source'])
        stream_dialogue(capture,{'provider':'codex','id':'source'},[(1,{'type':'response_item','payload':{'type':'message','id':'attachment-message','role':'user','content':[{'type':'input_image','image_url':'native-reference'}]}}),(2,{'type':'response_item','payload':{'type':'message','id':'thinking-only','role':'assistant','content':[{'type':'thinking','thinking':'excluded'}]}})])
        self.assertEqual(1,len(capture.turns));self.assertEqual('attachment-message',capture.turns[0]['native_message_id']);self.assertEqual([],capture.turns[0]['parts'])

    def test_independent_native_role_and_order_verification_rejects_mismatch(self):
        import tempfile,json,pathlib
        from memory.archive_import import verify_capture
        with tempfile.TemporaryDirectory() as folder:
            path=pathlib.Path(folder)/'original.jsonl'
            path.write_text(json.dumps({'type':'response_item','timestamp':'2020-01-01T00:00:00Z','payload':{'type':'message','id':'m','role':'user','content':[]}})+'\n')
            source={'path':'original.jsonl','kind':'native_stream','provider':'codex'}
            message={'source_locator':'line:1','parts':[],'text':'','role':'user','native_message_id':'m','original_timestamp':'2020-01-01T00:00:00+00:00'}
            self.assertEqual(1,verify_capture(folder,source,{'messages':[message]}))
            message['role']='assistant'
            with self.assertRaisesRegex(ValueError,'identity or role'):verify_capture(folder,source,{'messages':[message]})
            message['role']='user';message['parent_native_message_id']='incorrect-parent'
            with self.assertRaisesRegex(ValueError,'branch parent'):verify_capture(folder,source,{'messages':[message]})

class MixedNativePackage(unittest.TestCase):
    def test_shared_claude_package_can_reference_both_native_environments(self):
        from memory.archive import export_supports_environment
        import tempfile,pathlib,zipfile
        from memory.archive_batch import source_environment
        with tempfile.TemporaryDirectory() as folder:
            package=pathlib.Path(folder)/'native.zip'
            with zipfile.ZipFile(package,'w') as archive:
                archive.writestr('conversations.json','[]');archive.writestr('design_chats/id.json','{}')
            self.assertEqual('web_and_design',source_environment({'provider':'claude','kind':'native_package'},package))
        source={'provider':'claude','environment':'web_and_design'}
        self.assertTrue(export_supports_environment(source,'claude','web'));self.assertTrue(export_supports_environment(source,'claude','design'));self.assertFalse(export_supports_environment(source,'codex','local'));self.assertFalse(export_supports_environment(source,'claude','local'))

class MetadataCacheIntegrity(unittest.TestCase):
    def test_exact_byte_cache_never_reuses_mutated_values_or_changed_files(self):
        import tempfile,pathlib
        from memory.records import load
        with tempfile.TemporaryDirectory() as folder:
            path=pathlib.Path(folder)/'record.yaml';path.write_text('items: [one]\n')
            first=load(path);first['items'].append('mutated')
            self.assertEqual(['one'],load(path)['items'])
            path.write_text('items: [two]\n');self.assertEqual(['two'],load(path)['items'])

class ArchiveNoopTransaction(Fixture):
    def test_skipping_noop_validation_never_skips_changed_file_validation(self):
        from memory.staging import candidate
        from memory.records import atomic
        with self.assertRaisesRegex(ValueError,'Incremental validation failed'):
            with candidate(self.root,validate_noop=False) as target:
                atomic(target/'schemas/manifest.schema.json','{}')
        self.clean()

class NativeIdentityAuthority(unittest.TestCase):
    def test_native_session_identity_overrides_unverified_catalog_metadata_mapping(self):
        import tempfile,pathlib,json,hashlib
        from memory.archive_import import native_captures,capture_payload,verify_capture
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);originals=root/'ORIGINALS';originals.mkdir()
            native='actual-native-session';row={'type':'user','sessionId':native,'uuid':'native-message','timestamp':'2020-01-01T00:00:00Z','message':{'role':'user','content':'Exact original text'}}
            path=originals/'session.jsonl';path.write_text(json.dumps(row)+'\n');metadata=originals/'metadata.json';metadata.write_text(json.dumps({'sessionId':'wrapper','cliSessionId':'incorrect-mapping','title':'Unverified title'}))
            source={'path':'ORIGINALS/session.jsonl','id':'source','kind':'native_stream','provider':'claude','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mapped_native_id':'incorrect-mapping','native_ids':[native],'_metadata_source':{'path':'ORIGINALS/metadata.json','sha256':hashlib.sha256(metadata.read_bytes()).hexdigest()}}
            env,capture=next(native_captures(root,source));payload=capture_payload(env,capture)
            self.assertEqual(native,payload['native_conversation_id']);self.assertFalse(capture.context['metadata_association_verified']);self.assertNotEqual('Unverified title',payload['title']);self.assertEqual(1,verify_capture(root,source,payload))
            metadata.write_text(json.dumps({'sessionId':'application-wrapper','cliSessionId':native,'title':'Associated title','createdAt':'1999-01-01T00:00:00Z'}));source['_metadata_source']['sha256']=hashlib.sha256(metadata.read_bytes()).hexdigest()
            env,capture=next(native_captures(root,source));payload=capture_payload(env,capture)
            self.assertTrue(capture.context['metadata_association_verified']);self.assertEqual('2020-01-01T00:00:00+00:00',payload['original_started_at'])

class FlattenedProtocolRegression(unittest.TestCase):
    def test_flattened_protocol_is_excluded_but_typed_literal_is_preserved(self):
        from memory.native_dialogue import visible_ranges
        for value in ('[thinking: private reasoning]','[tool_use: Bash {"command":"echo [x]"}]','[tool_result: command output]'):
            spans,excluded,issues=visible_ranges(value,'ASSISTANT',native_flattened=True)
            self.assertEqual('', ''.join(value[a:b] for a,b in spans));self.assertTrue(excluded);self.assertFalse(issues)
            spans,_,_=visible_ranges(value,'ASSISTANT')
            self.assertEqual(value,''.join(value[a:b] for a,b in spans))
        value='```text\n[tool_result: literal example]\n```'
        spans,_,_=visible_ranges(value,'ASSISTANT',native_flattened=True)
        self.assertEqual(value,''.join(value[a:b] for a,b in spans))

    def test_native_coverage_rejects_omitted_text_even_when_selected_spans_match(self):
        import tempfile,json,pathlib
        from memory.archive_import import verify_capture
        with tempfile.TemporaryDirectory() as folder:
            path=pathlib.Path(folder)/'original.jsonl'
            row={'type':'user','uuid':'m','sessionId':'s','message':{'role':'user','content':[{'type':'text','text':'first'},{'type':'text','text':' second'}]}}
            path.write_text(json.dumps(row)+'\n')
            message={'source_locator':'line:1','parts':[{'locator':'line:1#/message/content/0/text','start_character':0,'end_character':5}],'text':'first','role':'user','native_message_id':'m','original_timestamp':None}
            with self.assertRaisesRegex(ValueError,'coverage'):verify_capture(folder,{'path':'original.jsonl','kind':'native_stream','provider':'claude'},{'messages':[message]})

    def test_ambiguous_flattened_brackets_do_not_leak_internal_payload(self):
        from memory.native_dialogue import visible_ranges
        value='[thinking: internal ] bracket inside reasoning]'
        spans,_,issues=visible_ranges(value,'ASSISTANT',native_flattened=True)
        self.assertEqual('', ''.join(value[a:b] for a,b in spans));self.assertTrue(issues)
        value='Actual spoken prefix\n[tool_result: output ] ambiguous tail'
        spans,_,issues=visible_ranges(value,'ASSISTANT',native_flattened=True)
        self.assertEqual('Actual spoken prefix\n',''.join(value[a:b] for a,b in spans));self.assertTrue(issues)

class ArchiveOverlayValidation(Fixture):
    def test_full_staged_validation_has_navigation_and_rejects_navigation_drift(self):
        from memory.archive import register_archive_conversation
        from memory.records import atomic
        from memory.staging import candidate
        from memory.validation import validate
        export=self.export()
        payload={'provider':'fictional','environment':'test','native_conversation_id':'native','title':'Exact archive','original_started_at':None,'original_ended_at':None,'limitations':[],'messages':[{'identity_key':'native:m','native_message_id':'m','role':'user','original_timestamp':None,'parent_native_message_id':None,'text':'Exact words','source_locator':'/messages/0','parts':[]}]}
        register_archive_conversation(self.root,export,payload);rebuild_navigation(self.root)
        with candidate(self.root) as target:
            self.assertEqual([], [f for f in validate(target) if f['severity']=='ERROR'])
        original=(self.root/'INDEX/CONVERSATIONS.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'archive_navigation'):
            with candidate(self.root) as target:atomic(target/'INDEX/CONVERSATIONS.json','{"conversations":[]}\n')
        self.assertEqual(original,(self.root/'INDEX/CONVERSATIONS.json').read_bytes())
