"""Dedicated Grok backend export: faithful message text and native ancestry."""
import collections,datetime as dt,heapq,json,pathlib
from .native_dialogue import Capture

ENVIRONMENTS={'grok_in_x','standalone','unknown'}
def timestamp(value):
    try:
        if isinstance(value,dict):
            value=value.get('$date')
            if isinstance(value,dict):value=value.get('$numberLong')
            if isinstance(value,(str,int)) and str(value).lstrip('-').isdigit():
                return (dt.datetime(1970,1,1,tzinfo=dt.timezone.utc)+dt.timedelta(milliseconds=int(value))).isoformat()
        if not isinstance(value,str):return None
        parsed=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
        return parsed.astimezone(dt.timezone.utc).isoformat() if parsed.tzinfo else None
    except (ValueError,TypeError,OverflowError):return None

def role(response):
    sender=response.get('sender')
    if sender=='human':return 'user'
    if sender in ('assistant','ASSISTANT'):return 'assistant'
    if sender in ('grok-3','grok-4') and response.get('model')==sender:return 'assistant'
    return None

def nontext(response):return bool(response.get('file_attachments') or response.get('media_types'))
def eligible(response):return role(response) is not None and (isinstance(response.get('message'),str) and bool(response['message'].strip()) or nontext(response))
def order(responses):
    byid={r['_id']:r for r in responses}
    if len(byid)!=len(responses):raise ValueError('Duplicate Grok response identities')
    children=collections.defaultdict(list);degree={key:0 for key in byid}
    for key,r in byid.items():
        parent=r.get('parent_response_id')
        if parent in byid:children[parent].append(key);degree[key]+=1
    def priority(key):return (timestamp(byid[key].get('create_time')) or '9999',key)
    ready=[priority(k) for k,v in degree.items() if not v];heapq.heapify(ready);result=[]
    while ready:
        _,key=heapq.heappop(ready);result.append(key)
        for child in children[key]:
            degree[child]-=1
            if not degree[child]:heapq.heappush(ready,priority(child))
    if len(result)!=len(byid):raise ValueError('Grok native response graph contains a cycle')
    return result

def captures(path,source):
    data=json.loads(pathlib.Path(path).read_bytes())
    if not isinstance(data,dict) or not isinstance(data.get('conversations'),list):raise ValueError('Unsupported Grok native export structure')
    for ci,item in enumerate(data['conversations']):
        conversation=item['conversation'];cid=conversation.get('id')
        if not cid:raise ValueError('Grok native conversation identity unavailable')
        environment=conversation.get('creation_source') or 'unknown';cap=Capture('archive',cid,'grok',conversation.get('title'),[source['id']])
        if environment not in ENVIRONMENTS:cap.exceptions.append({'issue':'Unrecognized native Grok creation_source; environment remains recorded for review'})
        cap.context['native_timestamps']={'start':timestamp(conversation.get('create_time')),'end':timestamp(conversation.get('modify_time'))}
        responses=[r['response'] for r in item['responses']];byid={r['_id']:(i,r) for i,r in enumerate(responses)};cap.context['parent_map']={r['_id']:r.get('parent_response_id') or None for r in responses};gaps=[]
        missing={r.get('parent_response_id') for r in responses if r.get('parent_response_id') and r['parent_response_id'] not in byid}
        if missing:gaps.append('Native parent references outside the exported conversation remain unresolved: '+', '.join(sorted(missing))+'. No missing message or root text is invented.')
        if conversation.get('leaf_response_id') and conversation['leaf_response_id'] not in byid:gaps.append('Declared native leaf response is absent from the export; no replacement leaf is inferred')
        if any(r.get('partial') is True for r in responses):gaps.append('Native source marks response records partial; exact available text retained without asserting complete source capture')
        children=collections.Counter(r.get('parent_response_id') for r in responses if r.get('parent_response_id') in byid)
        if any(v>1 for v in children.values()):gaps.append('All native response branches retained; topological traversal uses original timestamps for ready siblings without asserting a response relationship between siblings')
        cap.context['provenance_notes']=gaps
        for key in order(responses):
            ri,r=byid[key]
            if r.get('conversation_id')!=cid:raise ValueError('Grok response belongs to a different conversation')
            loc=f'json:/conversations/{ci}/responses/{ri}/response';rec=cap.record(source['id'],loc,key,r.get('sender'),timestamp(r.get('create_time')),r.get('parent_response_id') or None);speaker=role(r)
            for name in ('thinking_trace','agent_thinking_traces','steps'):
                if r.get(name):cap.exclude(rec,'native_only_'+name,loc+'/'+name)
            if (r.get('metadata') or {}).get('summarized_trace'):cap.exclude(rec,'native_only_summarized_trace',loc+'/metadata/summarized_trace')
            if speaker is None:
                cap.exclude(rec,'unresolved_native_sender');cap.exceptions.append({'locator':loc,'issue':'Unrecognized Grok native sender retained without inventing a role'});continue
            text=r.get('message')
            if not isinstance(text,str):cap.exceptions.append({'locator':loc,'issue':'Native Grok message is not a text string; no replacement applied'});continue
            try:text.encode('utf-8')
            except UnicodeEncodeError:cap.exceptions.append({'locator':loc,'issue':'Unpaired surrogate in Grok message; no replacement applied'});continue
            if text:rec['_parts']=[{'source_id':source['id'],'locator':loc+'/message','start_character':0,'end_character':len(text),'text':text}]
            if nontext(r):cap.exclude(rec,'non_text_attachment',loc+('/file_attachments' if r.get('file_attachments') else '/media_types'))
            cap.finish_message(rec,speaker.upper(),allow_assistant_attachments=True)
        yield environment,cap

def verify(path,payload):
    """Independent source-field, coverage, timestamp and native-parent checks."""
    data=json.loads(pathlib.Path(path).read_bytes());byid={c['conversation']['id']:(i,c) for i,c in enumerate(data['conversations'])};seen=collections.defaultdict(set);positions=collections.defaultdict(dict)
    def pointer(field):
        value=data
        for part in field.removeprefix('json:').lstrip('/').split('/'):
            part=part.replace('~1','/').replace('~0','~');value=value[int(part)] if isinstance(value,list) else value[part]
        return value
    for index,m in enumerate(payload['messages']):
        cid=m.get('native_conversation_id',payload.get('native_conversation_id'));ci,c=byid[cid];r=pointer(m['source_locator']);nid=r['_id'];ri=next(i for i,item in enumerate(c['responses']) if item['response']['_id']==nid)
        if m['source_locator']!=f'json:/conversations/{ci}/responses/{ri}/response' or r.get('conversation_id')!=cid:raise ValueError('Grok source locator or native conversation identity mismatch')
        if nid in seen[cid] or nid!=m['native_message_id'] or not eligible(r) or role(r)!=m['role']:raise ValueError('Grok native role, eligibility or message identity comparison failed')
        if timestamp(r.get('create_time'))!=m['original_timestamp']:raise ValueError('Grok original timestamp comparison failed')
        if (r.get('parent_response_id') or None)!=m.get('parent_native_message_id'):raise ValueError('Grok native parent comparison failed')
        if r['message']!=m['text']:raise ValueError('Grok complete message text coverage comparison failed')
        expected=[{'locator':m['source_locator']+'/message','start_character':0,'end_character':len(r['message'])}] if r['message'] else []
        actual=[{key:p[key] for key in ('locator','start_character','end_character')} for p in m['parts']]
        if actual!=expected or ''.join(pointer(p['locator'])[p['start_character']:p['end_character']] for p in m['parts'])!=r['message']:raise ValueError('Grok exact source field span comparison failed')
        seen[cid].add(nid);positions[cid][nid]=index
    for cid,ids in seen.items():
        _,c=byid[cid];responses={r['response']['_id']:r['response'] for r in c['responses']}
        if ids!={key for key,r in responses.items() if eligible(r)}:raise ValueError('Grok conversation coverage omits native dialogue or a branch')
        for key in ids:
            parent=responses[key].get('parent_response_id');ancestors={key}
            while parent in responses:
                if parent in ancestors:raise ValueError('Grok source graph has a cycle')
                ancestors.add(parent)
                if parent in positions[cid] and positions[cid][parent]>=positions[cid][key]:raise ValueError('Grok native graph order comparison failed')
                parent=responses[parent].get('parent_response_id')
    return sum(len(ids) for ids in seen.values())
