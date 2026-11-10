"""Native ChatGPT export shards and group records; no intellectual filtering."""
import collections,datetime as dt,heapq,json,math,pathlib
from .native_dialogue import Capture

INTERNAL={'thoughts','reasoning_recap','reasoning','redacted_thinking'}
def timestamp(value):
    if value is None:return None
    try:
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            return dt.datetime.fromtimestamp(value,dt.timezone.utc).isoformat() if math.isfinite(value) else None
        parsed=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.astimezone(dt.timezone.utc).isoformat() if parsed.tzinfo else None
    except (ValueError,TypeError,AttributeError,OverflowError,OSError):return None

def token(value):return str(value).replace('~','~0').replace('/','~1')
def ordered_graph(mapping):
    children=collections.defaultdict(list);degree={key:0 for key in mapping}
    for key,node in mapping.items():
        if node.get('id')!=key:raise ValueError('OpenAI graph node identity mismatch')
        parent=node.get('parent')
        if parent is not None:
            if parent not in mapping:raise ValueError('OpenAI graph parent is unresolved')
            children[parent].append(key);degree[key]+=1
    def priority(key):return (timestamp((mapping[key].get('message') or {}).get('create_time')) or '9999',key)
    ready=[priority(k) for k,v in degree.items() if not v];heapq.heapify(ready);ordered=[]
    while ready:
        _,key=heapq.heappop(ready);ordered.append(key)
        for child in children[key]:
            degree[child]-=1
            if degree[child]==0:heapq.heappush(ready,priority(child))
    if len(ordered)!=len(mapping):raise ValueError('OpenAI graph contains a cycle')
    return ordered

def eligible(message,group=False):
    role=message.get('role') if group else message.get('author',{}).get('role')
    if role not in ('user','assistant'):return False
    if group:return True
    return (message.get('channel') not in ('analysis','justify') and message.get('recipient') in (None,'all') and not message.get('metadata',{}).get('is_visually_hidden_from_conversation') and message.get('content',{}).get('content_type') in ('text','multimodal_text'))

def add_native_parts(capture,record,message,locator,group=False):
    role=record['native_role'];content=message.get('content',{});parts=[message.get('text','')] if group else content.get('parts',[])
    for i,part in enumerate(parts):
        field=locator+'/text' if group else locator+'/content/parts/'+str(i)
        if isinstance(part,str):
            try:part.encode('utf-8')
            except UnicodeEncodeError:
                capture.exceptions.append({'locator':field,'issue':'Unpaired surrogate in native dialogue; no replacement or invented text'});continue
            if part:record.setdefault('_parts',[]).append({'source_id':record['source_id'],'locator':field,'start_character':0,'end_character':len(part),'text':part})
        elif isinstance(part,dict) and part.get('content_type')=='image_asset_pointer':capture.exclude(record,'non_text_attachment',field)
        else:
            capture.exclude(record,'unknown_native_content_part',field);capture.exceptions.append({'locator':field,'issue':'Unrecognized OpenAI content part requires native review'})
    if message.get('attachments') or message.get('metadata',{}).get('attachments'):capture.exclude(record,'separate_attachment_content_or_reference',locator+('/attachments' if group else '/metadata/attachments'))
    capture.finish_message(record,role.upper())

def captures(path,source):
    data=json.loads(pathlib.Path(path).read_bytes());group=isinstance(data,dict) and 'chats' in data
    conversations=data['chats'] if group else data
    if not isinstance(conversations,list):raise ValueError('Unsupported OpenAI conversation export shape')
    for ordinal,c in enumerate(conversations):
        native=c.get('id');prefix='json:'+('/chats' if group else '')+'/'+str(ordinal)
        if not native or (not group and c.get('conversation_id') not in (None,native)):raise ValueError('OpenAI conversation identity mismatch or unavailable')
        cap=Capture('archive',native,'openai',c.get('name' if group else 'title'),[source['id']]);cap.context['native_timestamps']={'start':timestamp(c.get('created_at' if group else 'create_time')),'end':timestamp(c.get('updated_at' if group else 'update_time'))}
        if group:
            items=sorted(enumerate(c['messages']),key=lambda pair:(timestamp(pair[1].get('created_at')) or '9999',pair[0]))
            for i,message in items:
                loc=prefix+'/messages/'+str(i);role=message.get('role');record=cap.record(source['id'],loc,message.get('id'),role,timestamp(message.get('created_at')))
                if eligible(message,True):add_native_parts(cap,record,message,loc,True)
                else:cap.exclude(record,'non_dialogue_native_role')
            cap.context['group_source_only_user_roles']=all(m.get('role')=='user' for m in c['messages'])
        else:
            mapping=c['mapping'];order=ordered_graph(mapping);cap.context['parent_map']={key:node.get('parent') for key,node in mapping.items()}
            if c.get('current_node') not in mapping:cap.exceptions.append({'issue':'Native current_node is unresolved; all recoverable graph branches retained'})
            for key in order:
                node=mapping[key];message=node.get('message')
                if not message:continue
                if message.get('id')!=key:raise ValueError('OpenAI message and graph node identities differ')
                loc=prefix+'/mapping/'+token(key)+'/message';role=message.get('author',{}).get('role');record=cap.record(source['id'],loc,key,role,timestamp(message.get('create_time')),node.get('parent'))
                if eligible(message):add_native_parts(cap,record,message,loc)
                else:
                    kind=message.get('content',{}).get('content_type');cap.exclude(record,'native_only_'+str(kind))
                    if role in ('user','assistant') and kind not in INTERNAL and kind not in ('text','multimodal_text'):
                        cap.exceptions.append({'locator':loc,'issue':'Unsupported OpenAI content type retained native-only: '+str(kind)})
        yield ('chatgpt_group' if group else 'chatgpt'),cap

def verify(path,payload):
    """Independently enumerate native text and graph links, including all branches."""
    data=json.loads(pathlib.Path(path).read_bytes());group=isinstance(data,dict);conversations=data['chats'] if group else data
    byid={c['id']:(i,c) for i,c in enumerate(conversations)};seen=collections.defaultdict(set);positions=collections.defaultdict(dict);nodes=collections.defaultdict(dict);previous_times={}
    def pointer(field):
        value=data
        for part in field.removeprefix('json:').lstrip('/').split('/'):
            part=part.replace('~1','/').replace('~0','~');value=value[int(part)] if isinstance(value,list) else value[part]
        return value
    for index,m in enumerate(payload['messages']):
        cid=m.get('native_conversation_id',payload.get('native_conversation_id'));ci,conversation=byid[cid];native=pointer(m['source_locator']);nid=native['id']
        expected_prefix='json:'+('/chats' if group else '')+'/'+str(ci)
        expected_locator=(expected_prefix+'/messages/'+str(next(i for i,n in enumerate(conversation['messages']) if n['id']==nid))) if group else expected_prefix+'/mapping/'+token(nid)+'/message'
        if m['source_locator']!=expected_locator:raise ValueError('OpenAI source locator belongs to a different native record')
        if nid in seen[cid]:raise ValueError('Duplicate OpenAI normalized native message')
        seen[cid].add(nid);positions[cid][nid]=index
        if not eligible(native,group):raise ValueError('Internal or non-dialogue OpenAI record included')
        role=native.get('role') if group else native['author']['role'];stamp=timestamp(native.get('created_at' if group else 'create_time'))
        if nid!=m['native_message_id'] or role!=m['role'] or stamp!=m['original_timestamp']:raise ValueError('OpenAI identity, role or timestamp comparison failed')
        parent=None if group else conversation['mapping'][nid].get('parent');nodes[cid][nid]=parent
        if parent!=m.get('parent_native_message_id'):raise ValueError('OpenAI native parent comparison failed')
        strings=[native.get('text','')] if group else [part for part in native.get('content',{}).get('parts',[]) if isinstance(part,str)]
        expected=''.join(strings)
        if expected!=m['text']:raise ValueError('OpenAI full native text coverage comparison failed')
        native_parts=[native.get('text','')] if group else native.get('content',{}).get('parts',[])
        expected_parts=[{'locator':m['source_locator']+('/text' if group else '/content/parts/'+str(i)),'start_character':0,'end_character':len(part)} for i,part in enumerate(native_parts) if isinstance(part,str) and part]
        if [{k:p[k] for k in ('locator','start_character','end_character')} for p in m['parts']]!=expected_parts:raise ValueError('OpenAI source spans do not cover the native text fields exactly')
        recovered=''.join(pointer(p['locator'])[p['start_character']:p['end_character']] for p in m['parts'])
        if recovered!=expected:raise ValueError('OpenAI source field span comparison failed')
        if group and stamp:
            if cid in previous_times and stamp<previous_times[cid]:raise ValueError('OpenAI group chronological order failed')
            previous_times[cid]=stamp
    for cid,ids in seen.items():
        _,c=byid[cid];native_messages=c['messages'] if group else [n['message'] for n in c['mapping'].values() if n.get('message')]
        expected=set()
        for n in native_messages:
            if not eligible(n,group):continue
            strings=[n.get('text','')] if group else [p for p in n.get('content',{}).get('parts',[]) if isinstance(p,str)]
            attachments=n.get('attachments') or n.get('metadata',{}).get('attachments') or (not group and any(isinstance(p,dict) and p.get('content_type')=='image_asset_pointer' for p in n.get('content',{}).get('parts',[])))
            if ''.join(strings).strip() or n.get('author',{}).get('role',n.get('role'))=='user' and attachments:expected.add(n['id'])
        if ids!=expected:raise ValueError('OpenAI conversation message coverage differs from all eligible native branches')
        if not group:
            for nid,parent in nodes[cid].items():
                ancestry=set()
                while parent is not None:
                    if parent in ancestry or parent not in c['mapping']:raise ValueError('OpenAI native graph cycle or unresolved parent')
                    ancestry.add(parent)
                    if parent in positions[cid] and positions[cid][parent]>=positions[cid][nid]:raise ValueError('OpenAI native graph order comparison failed')
                    parent=c['mapping'][parent]['parent']
    return sum(len(ids) for ids in seen.values())
