import copy,json,pathlib,tempfile,unittest
from memory.grok_archive import captures,verify,timestamp,order,role
from memory.archive_import import capture_payload
from memory.archive import export_supports_environment

class GrokArchive(unittest.TestCase):
    def fixture(self):
        def r(nid,sender,message,parent=None,ms='1000',**extra):return {'response':dict(_id=nid,conversation_id='c',sender=sender,message=message,create_time={'$date':{'$numberLong':ms}},model='grok-4',**({'parent_response_id':parent} if parent else {}),**extra),'share_link':None}
        return {'conversations':[{'conversation':{'id':'c','title':'Synthetic','create_time':'1970-01-01T00:00:00Z','modify_time':'1970-01-01T00:00:03Z','creation_source':'standalone','leaf_response_id':'answer'},'responses':[r('answer','assistant','  Full\n\nanswer  ','user','3000',thinking_trace='INTERNAL',steps=[{'text':'TOOL'}]),r('alternative','ASSISTANT','alternative','user','2500'),r('user','human','[thinking: literal user text]',None,'2000')]}],'projects':[],'tasks':[],'media_posts':[]}
    def payload(self,data):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup);path=pathlib.Path(directory.name)/'original.json';path.write_text(json.dumps(data));env,cap=next(captures(path,{'id':'source'}));return path,capture_payload(env,cap),cap
    def test_graph_order_all_branches_and_exact_visible_text_only(self):
        path,p,cap=self.payload(self.fixture());self.assertEqual(3,verify(path,p));self.assertEqual('user',p['messages'][0]['native_message_id']);answer=next(m for m in p['messages'] if m['native_message_id']=='answer');self.assertEqual('  Full\n\nanswer  ',answer['text']);self.assertNotIn('INTERNAL',answer['text']);self.assertEqual('[thinking: literal user text]',p['messages'][0]['text']);self.assertEqual({'user','assistant'},{m['role'] for m in p['messages']})
    def test_missing_native_parent_is_preserved_and_disclosed_not_invented(self):
        data=self.fixture();data['conversations'][0]['responses'][2]['response']['parent_response_id']='absent';path,p,cap=self.payload(data);self.assertEqual(3,verify(path,p));self.assertEqual('absent',p['messages'][0]['parent_native_message_id']);self.assertTrue(any('unresolved' in n for n in cap.context['provenance_notes']))
    def test_cycle_duplicate_and_foreign_conversation_rejected(self):
        for mode in ('cycle','duplicate','foreign'):
            data=self.fixture();rs=data['conversations'][0]['responses']
            if mode=='cycle':rs[2]['response']['parent_response_id']='answer'
            elif mode=='duplicate':rs.append(copy.deepcopy(rs[0]))
            else:rs[0]['response']['conversation_id']='other'
            with self.assertRaises(ValueError):self.payload(data)
    def test_native_timestamp_milliseconds_and_unknown_are_distinct(self):
        self.assertEqual('1970-01-01T00:00:01.234000+00:00',timestamp({'$date':{'$numberLong':'1234'}}));self.assertIsNone(timestamp({'$date':{'$numberLong':'unknown'}}));self.assertIsNone(timestamp('2020-01-01'))
    def test_audio_only_assistant_and_file_only_user_keep_real_identities(self):
        data=self.fixture();rs=data['conversations'][0]['responses'];rs[0]['response'].update(message='',media_types=['audio']);rs[2]['response'].update(message='',file_attachments=['native-file']);path,p,cap=self.payload(data);self.assertEqual(3,verify(path,p));self.assertEqual('',next(m for m in p['messages'] if m['native_message_id']=='answer')['text']);self.assertEqual('',p['messages'][0]['text'])
    def test_independent_coverage_rejects_omission_truncation_and_wrong_field(self):
        path,p,_=self.payload(self.fixture());bad=copy.deepcopy(p);bad['messages']=[m for m in bad['messages'] if m['native_message_id']!='alternative']
        with self.assertRaisesRegex(ValueError,'coverage'):verify(path,bad)
        bad=copy.deepcopy(p);bad['messages'][0]['text']='short'
        with self.assertRaisesRegex(ValueError,'coverage'):verify(path,bad)
        bad=copy.deepcopy(p);bad['messages'][0]['parts'][0]['locator']='json:/conversations/0/conversation/title'
        with self.assertRaisesRegex(ValueError,'span'):verify(path,bad)
    def test_model_named_sender_requires_matching_model_and_unknown_environment_stays_unknown(self):
        self.assertEqual('assistant',role({'sender':'grok-4','model':'grok-4'}));self.assertIsNone(role({'sender':'grok-4','model':'different'}));data=self.fixture();data['conversations'][0]['conversation']['creation_source']=None;_,p,_=self.payload(data);self.assertEqual('unknown',p['environment']);self.assertTrue(export_supports_environment({'provider':'grok','environment':'grok_package'},'grok','unknown'));self.assertFalse(export_supports_environment({'provider':'grok','environment':'grok_package'},'openai','chatgpt'))
