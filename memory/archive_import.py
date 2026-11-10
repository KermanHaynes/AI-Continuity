"""Bounded native capture interpretation for the authorized historical archive."""
import collections
import contextlib
import datetime as dt
import hashlib
import json
import pathlib
import subprocess
import zipfile
from .native_dialogue import Capture, web, design, stream_dialogue, visible_ranges


class NativeFormatError(ValueError):
    pass


@contextlib.contextmanager
def jsonl_rows(path):
    process=None
    if path.name.endswith('.zst'):
        process=subprocess.Popen(['zstd','-q','-dc','--',str(path)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        stream=process.stdout
    else:stream=path.open('rb')
    def rows():
        for number,line in enumerate(stream,1):
            if line.strip():
                try:yield number,json.loads(line)
                except json.JSONDecodeError as error:
                    yield number,{'_native_parse_error':{'line':number,'column':error.colno,'reason':error.msg}}
    try:
        yield rows()
        if process and process.wait()!=0:raise ValueError('Native decompression failed')
    finally:
        stream.close()
        if process and process.poll() is None:process.terminate();process.wait()


def native_captures(corpus, source):
    """Yield one conversation snapshot at a time, retaining native field locators."""
    root=pathlib.Path(corpus).resolve();path=root/source['path']
    if not path.resolve().is_relative_to(root/'ORIGINALS') or path.is_symlink():raise ValueError('Source escapes immutable archive')
    with path.open('rb') as stream:
        if hashlib.file_digest(stream,'sha256').hexdigest()!=source['sha256']:raise ValueError('Native source changed after preservation inventory')
    if source['provider']=='grok':
        from .grok_archive import captures
        yield from captures(path,source)
        return
    if source['provider']=='openai':
        from .openai_archive import captures
        yield from captures(path,source)
        return
    fmt=source.get('source_format','')
    if source['kind']=='native_stream':
        native=source.get('mapped_native_id') or next(iter(source.get('native_ids',[])),None)
        capture=Capture('archive',native,source['provider'],None,[source['id']])
        with jsonl_rows(path) as rows: native_rows=list(rows)
        flattened=source['provider']=='claude' and not any(isinstance(row.get('message',{}).get('content'),list) for _,row in native_rows)
        capture.context['source_representation']='flattened_capture' if flattened else 'native_blocks'
        stream_dialogue(capture,dict(source,_flattened_capture=flattened),native_rows)
        if source['provider']=='codex':
            capture.native=capture.context.get('id') or native
            timestamps={r['timestamp_original'] for r in capture.records if r['timestamp_original']}
            wrappers=any(e['reason']=='external_agent_tool_execution' for r in capture.records for e in r['exclusions'])
            if capture.context.get('history_mode')=='paginated' and len(timestamps)<=1 and wrappers:
                for turn in capture.turns:
                    turn['snapshot_observation_timestamp']=turn['timestamp_original'];turn['timestamp_original']=None
                capture.exceptions.append({'issue':'Paginated external-agent replay: original turn timestamps and original participant/model identity are unknown'})
            else:
                capture.context['native_timestamps']={'start':capture.context.get('timestamp'),'end':None}
        if source['provider']=='claude':
            identities=capture.context.get('native_session_ids',set())
            if len(identities)>1:raise NativeFormatError('Native stream contains multiple session identities; single-conversation association requires source-specific review')
            if identities:capture.native=next(iter(identities))
        metadata_source=source.get('_metadata_source')
        if metadata_source:
            metadata_path=root/metadata_source['path']
            if not metadata_path.resolve().is_relative_to(root/'ORIGINALS'):raise ValueError('Session metadata escapes immutable archive')
            raw=metadata_path.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=metadata_source['sha256']:raise ValueError('Session metadata checksum differs from source catalog')
            metadata=json.loads(raw)
            capture.context['metadata_association_verified']=capture.native in (metadata.get('sessionId'),metadata.get('cliSessionId'))
            if capture.context['metadata_association_verified']:
                capture.title=metadata.get('title') or capture.title
                if metadata.get('sessionId')==capture.native:
                    capture.context['native_timestamps']={'start':metadata.get('createdAt'),'end':metadata.get('lastActivityAt')}
                else:capture.context['associated_metadata_timestamps']={'createdAt':metadata.get('createdAt'),'lastActivityAt':metadata.get('lastActivityAt')}
            else:capture.exceptions.append({'issue':'Unapplied metadata association: catalog mapping disagrees with authoritative native session identity; metadata retained separately'})
        if not capture.native:raise ValueError('Native session identity unavailable; cannot establish logical conversation')
        if capture.context.get('native_only_auxiliary_agent') or (capture.context.get('auxiliary_agent_evidence') and not capture.turns):yield ('native_only',capture)
        elif capture.turns:yield ('local',capture)
        elif capture.exceptions:raise NativeFormatError('Native stream has no recoverable dialogue and has parsing or integrity exceptions; original evidence retained for review')
        return
    def conversations(data,prefix):
        if not isinstance(data,list) or not all(isinstance(x,dict) and 'chat_messages' in x and 'uuid' in x for x in data):raise NativeFormatError('Unrecognized JSON export structure: expected a native Claude conversation array; no conversation identity has been inferred')
        for index,item in enumerate(data):
            capture=Capture('archive',item['uuid'],'claude',item.get('name'),[source['id']])
            web(capture,dict(source,locator_prefix=prefix),item,index)
            capture.context['native_timestamps']={'start':item.get('created_at'),'end':item.get('updated_at')}
            yield ('web',capture)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as package:
            for name in package.namelist():
                if name.endswith('conversations.json'):
                    yield from conversations(json.loads(package.read(name)),'zip:'+name+'#')
                elif name.startswith('design_chats/') and name.endswith('.json'):
                    item=json.loads(package.read(name))
                    if not isinstance(item,dict) or not isinstance(item.get('messages'),list):raise ValueError('Unrecognized native design conversation')
                    capture=Capture('archive',item['uuid'],'claude',item.get('title'),[source['id']])
                    design(capture,source,item,name)
                    capture.context['native_timestamps']={'start':item.get('created_at'),'end':item.get('updated_at')}
                    yield ('design',capture)
        return
    if path.suffix=='.json' and source['kind'] in ('potential_export','native_package') or fmt=='claude-native-bundled-json':
        data=json.loads(path.read_bytes()); yield from conversations(data,'json:')


def utc_timestamp(value):
    if value is None:return None
    try:
        parsed=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
        if parsed.tzinfo is None:return None
        return parsed.astimezone(dt.timezone.utc).isoformat()
    except (ValueError,AttributeError):return None


def capture_payload(environment, capture):
    """Compact conversation-only derivative; no execution or reasoning index."""
    occurrences=collections.Counter();messages=[]
    for turn in capture.turns:
        text=''.join(part['text'] for part in turn['parts'])
        stamp=utc_timestamp(turn['timestamp_original'])
        if turn['native_message_id'] is not None:identity='native:'+turn['native_message_id']
        else:
            observation=json.dumps([turn['speaker'],turn['timestamp_original'],hashlib.sha256(text.encode()).hexdigest()],ensure_ascii=True)
            occurrences[observation]+=1
            identity='observation:'+hashlib.sha256(observation.encode()).hexdigest()+':'+str(occurrences[observation])
        messages.append({'identity_key':identity,'native_message_id':turn['native_message_id'],'role':turn['speaker'].lower(),'original_timestamp':stamp,'parent_native_message_id':turn['parent_native_message_id'],'text':text,'source_locator':turn['locator'],'parts':[{k:v for k,v in part.items() if k!='text'} for part in turn['parts']]})
    original=capture.context.get('native_timestamps',{})
    stamps=[m['original_timestamp'] for m in messages if m['original_timestamp']]
    return {'provider':capture.provider,'environment':environment,'native_conversation_id':capture.native,'title':capture.title or capture.native,'original_started_at':utc_timestamp(original.get('start')) or min(stamps,default=None),'original_ended_at':utc_timestamp(original.get('end')) or max(stamps,default=None),'messages':messages,'limitations':[e['issue'] for e in capture.exceptions],'native_parent_map':capture.context.get('parent_map',{}),'native_lineage':{key:capture.context.get(key) for key in ('forked_from_id','parent_thread_id')}}


def verify_capture(corpus, source, payload):
    """Reopen native source independently and compare every selected field span."""
    if source['provider']=='grok':
        from .grok_archive import verify
        return verify(pathlib.Path(corpus)/source['path'],payload)
    if source['provider']=='openai':
        from .openai_archive import verify
        return verify(pathlib.Path(corpus)/source['path'],payload)
    path=pathlib.Path(corpus)/source['path']; fields={p['locator'] for m in payload['messages'] for p in m['parts']} | {m['source_locator'] for m in payload['messages']};resolved={};native_contexts={};stream_session=None
    def pointer(value,fragment):
        for token in fragment.lstrip('/').split('/') if fragment else []:
            token=token.replace('~1','/').replace('~0','~')
            value=value[int(token)] if isinstance(value,list) else value[token]
        return value
    if source['kind']=='native_stream':
        wanted=collections.defaultdict(list)
        for field in fields:
            line,separator,fragment=field.partition('#');wanted[int(line.removeprefix('line:'))].append((field,fragment))
        with jsonl_rows(path) as rows: native_rows=list(rows)
        flattened=source['provider']=='claude' and not any(isinstance(row.get('message',{}).get('content'),list) for _,row in native_rows)
        for number,row in native_rows:
                if source['provider']=='codex' and row.get('type')=='session_meta':stream_session=row.get('payload',{}).get('id')
                for field,fragment in wanted.get(number,[]):
                    resolved[field]=pointer(row,fragment);native_contexts[field]=row.get('sessionId') if source['provider']=='claude' else stream_session
    elif zipfile.is_zipfile(path):
        grouped=collections.defaultdict(list)
        for field in fields:
            member,fragment=field.removeprefix('zip:').split('#',1);grouped[member].append((field,fragment))
        with zipfile.ZipFile(path) as package:
            for member,items in grouped.items():
                data=json.loads(package.read(member))
                for field,fragment in items:
                    resolved[field]=pointer(data,fragment)
                    native_contexts[field]=data[int(fragment.lstrip('/').split('/')[0])].get('uuid') if isinstance(data,list) else data.get('uuid')
    else:
        data=json.loads(path.read_bytes())
        for field in fields:
            fragment=field.removeprefix('json:');resolved[field]=pointer(data,fragment)
            native_contexts[field]=data[int(fragment.lstrip('/').split('/')[0])].get('uuid') if isinstance(data,list) else data.get('uuid')
    previous_positions={}
    for message in payload['messages']:
        locator=message['source_locator'];native=resolved[locator]
        expected_conversation=message.get('native_conversation_id',payload.get('native_conversation_id'))
        if native_contexts.get(locator) is not None and expected_conversation is not None and native_contexts[locator]!=expected_conversation:raise ValueError('Native conversation identity comparison failed')
        if source['kind']=='native_stream':
            position=int(locator.removeprefix('line:'));body=native.get('payload',{}) if source['provider']=='codex' else native.get('message',{})
            role=body.get('role',native.get('type'));identity=body.get('id') if source['provider']=='codex' else native.get('uuid');stamp=native.get('timestamp');parent=None if source['provider']=='codex' else native.get('parentUuid')
        else:
            position=int(locator.rsplit('/',1)[1]);role=native.get('sender',native.get('role'));role='user' if role=='human' else role;identity=native.get('uuid');stamp=native.get('created_at');parent=native.get('parent_message_uuid')
        group=message.get('native_conversation_id',payload.get('native_conversation_id','conversation'))
        if position<=previous_positions.get(group,-1):raise ValueError('Native message order comparison failed')
        previous_positions[group]=position
        if message.get('parent_native_message_id')!=parent:raise ValueError('Native branch parent comparison failed')
        if role!=message['role'] or identity!=message['native_message_id']:raise ValueError('Native message identity or role comparison failed')
        if message['original_timestamp'] is not None and utc_timestamp(stamp)!=message['original_timestamp']:raise ValueError('Native message timestamp comparison failed')
        if source['kind']=='native_stream':
            if native.get('isMeta') is True or native.get('isApiErrorMessage') is True or native.get('isSidechain') or body.get('channel')=='analysis' or body.get('phase')=='analysis':raise ValueError('Non-dialogue native record was included')
            content=body.get('content',[]);expected=[]
            if isinstance(content,str):
                ranges,_,_=visible_ranges(content,role.upper(),native_flattened=flattened,native_context=source['provider']=='claude')
                expected=[content[a:b] for a,b in ranges]
            else:
                for block in content:
                    if isinstance(block,dict) and block.get('type') in ('text','input_text','output_text'):
                        value=block.get('text','');ranges,_,_=visible_ranges(value,role.upper(),native_context=source['provider']=='claude')
                        expected.extend(value[a:b] for a,b in ranges)
            if ''.join(expected)!=message['text']:raise ValueError('Native dialogue coverage comparison failed: omitted or non-dialogue text')
        recovered=''.join(resolved[p['locator']][p['start_character']:p['end_character']] for p in message['parts'])
        if recovered.encode()!=message['text'].encode():raise ValueError('Native field span fidelity comparison failed')
    return len(payload['messages'])
