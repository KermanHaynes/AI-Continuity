import copy,json,pathlib,tempfile,unittest
from memory.openai_archive import captures,verify,ordered_graph
from memory.archive_import import capture_payload

class OpenAIArchive(unittest.TestCase):
    def fixture(self):
        def node(mid,role,text,parent,typ='text',stamp=100):
            return {'id':mid,'parent':parent,'message':{'id':mid,'author':{'role':role},'create_time':stamp,'content':{'content_type':typ,'parts':text},'metadata':{}}}
        # Deliberately unordered mapping, with two actual alternatives.
        return [{'id':'c','conversation_id':'c','title':'Synthetic','create_time':90,'update_time':130,'current_node':'answer','mapping':{'answer':node('answer','assistant',['full\n\nresponse'],'thought',stamp=120),'alternate':node('alternate','assistant',['alternative'],'user',stamp=119),'thought':node('thought','assistant',[],'user','thoughts',110),'root':{'id':'root','parent':None,'message':None},'user':node('user','user',['[thinking: literal user words]','\n','question'],'root',stamp=100)}}]
    def payload(self,data):
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup);path=pathlib.Path(directory.name)/'original.json';path.write_text(json.dumps(data));env,cap=next(captures(path,{'id':'source'}));return path,capture_payload(env,cap)
    def test_graph_order_all_branches_exact_parts_and_reasoning_exclusion(self):
        path,payload=self.payload(self.fixture());self.assertEqual(3,verify(path,payload));self.assertEqual({'user','answer','alternate'},{m['native_message_id'] for m in payload['messages']});self.assertEqual('[thinking: literal user words]\nquestion',payload['messages'][0]['text']);self.assertLess([m['native_message_id'] for m in payload['messages']].index('user'),[m['native_message_id'] for m in payload['messages']].index('answer'));self.assertEqual('thought',next(m for m in payload['messages'] if m['native_message_id']=='answer')['parent_native_message_id'])
    def test_omitted_alternative_and_omitted_text_fail_independent_coverage(self):
        path,payload=self.payload(self.fixture());bad=copy.deepcopy(payload);bad['messages']=[m for m in bad['messages'] if m['native_message_id']!='alternate']
        with self.assertRaisesRegex(ValueError,'coverage'):verify(path,bad)
        bad=copy.deepcopy(payload);bad['messages'][0]['text']='question'
        with self.assertRaisesRegex(ValueError,'coverage'):verify(path,bad)
    def test_cycle_unresolved_parent_and_identity_mismatch_rejected(self):
        for mode in ('cycle','missing','identity'):
            data=self.fixture();mapping=data[0]['mapping']
            if mode=='cycle':mapping['root']['parent']='answer'
            elif mode=='missing':mapping['user']['parent']='missing'
            else:mapping['user']['id']='different'
            with self.assertRaises(ValueError):ordered_graph(mapping)
    def test_attachment_only_user_and_unknown_timestamp_remain_explicit(self):
        data=self.fixture();data[0]['mapping']['user']['message']['create_time']=None;data[0]['mapping']['user']['message']['content']={'content_type':'multimodal_text','parts':[{'content_type':'image_asset_pointer','asset_pointer':'file-native'}]};path,payload=self.payload(data);user=next(m for m in payload['messages'] if m['role']=='user');self.assertEqual('',user['text']);self.assertIsNone(user['original_timestamp']);self.assertEqual(3,verify(path,payload))
    def test_group_reverse_array_keeps_user_only_roles_and_source_indices(self):
        data={'chats':[{'id':'g','name':'Group','created_at':'2020-01-01T00:00:00Z','updated_at':None,'members':[{'id':'member'}],'messages':[{'id':'later','role':'user','text':'later','created_at':'2020-01-02T00:00:00Z','attachments':[]},{'id':'first','role':'user','text':'first','created_at':'2020-01-01T00:00:00Z','attachments':[]}]}]};path,payload=self.payload(data);self.assertEqual('chatgpt_group',payload['environment']);self.assertEqual(['first','later'],[m['native_message_id'] for m in payload['messages']]);self.assertEqual('json:/chats/0/messages/1',payload['messages'][0]['source_locator']);self.assertEqual(2,verify(path,payload));self.assertEqual({'user'},{m['role'] for m in payload['messages']})
    def test_source_locator_cannot_point_to_another_field_with_equal_text(self):
        path,payload=self.payload(self.fixture());bad=copy.deepcopy(payload);bad['messages'][0]['parts'][0]['locator']='json:/0/title'
        with self.assertRaisesRegex(ValueError,'spans'):verify(path,bad)
