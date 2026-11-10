"""Independent end-to-end native-source to canonical-transcript fidelity check."""
import collections,gc,json,pathlib,hashlib
from .records import load,collect,now
from .archive_import import verify_capture

def verify(root):
    root=pathlib.Path(root).resolve()
    enabled=gc.isenabled();gc.disable()
    try:return _verify(root)
    finally:
        gc.collect()
        if enabled:gc.enable()

def _verify(root):
    records=collect(root,names={'export.yaml','manifest.yaml'});exports={d['export_id']:d for _,d,_ in records if d['record_type']=='sot_export'};groups=collections.defaultdict(list);conversations=[];empty=0;unknown_native_ids=0;unknown_timestamps=0
    for path,d,_ in records:
     if d['record_type']!='sot_conversation':continue
     raw=(path.parent/'transcript.md').read_bytes();index=load(path.parent/'MESSAGES.yaml');conversations.append(d)
     for m in index['messages']:
      span=m['transcript_byte_range'];body=raw[span['start']:span['end']].decode('utf-8');assert hashlib.sha256(body.encode()).hexdigest()==m['content_sha256']
      eid=m['export_id'];parts=[{'locator':o['field'],'start_character':o['start'],'end_character':o['end']} for o in m.get('source_observations',[]) if o['export_id']==eid and o['source_locator']==m['source_locator'] and o['end']>o['start']]
      if not body:empty+=1
      if m['native_message_id'] is None:unknown_native_ids+=1
      if m['original_timestamp'] is None:unknown_timestamps+=1
      groups[eid].append({'parts':parts,'text':body,'source_locator':m['source_locator'],'role':m['role'],'native_message_id':m['native_message_id'],'original_timestamp':m['original_timestamp'],'native_conversation_id':d['native_conversation_id'],'parent_native_message_id':m.get('native_parent_message_id')})
    verified=0;failures=[]
    for position,(eid,messages) in enumerate(groups.items(),1):
     e=exports[eid];path=root/e['source_files'][0]['path']
     if not path.exists():path=pathlib.Path(e['publication']['retained_local_path'])
     source={'path':str(path),'provider':e['provider'],'kind':'native_stream' if '.jsonl' in path.name else 'native_package'}
     try:
      with path.open('rb') as stream:
       if hashlib.file_digest(stream,'sha256').hexdigest()!=e['source_files'][0]['sha256']:raise ValueError('Native original checksum comparison failed')
      verified+=verify_capture(root,source,{'messages':messages})
     except Exception as error:failures.append({'export_id':eid,'error_type':type(error).__name__,'reason':str(error) if isinstance(error,ValueError) else 'Native source mapping could not be independently resolved'})
     if position%25==0:print(json.dumps({'native_sources_compared':position,'total_sources':len(groups)}),flush=True);gc.collect()
    result={'checked_at':now(),'canonical_conversations':len(conversations),'canonical_turns':sum(len(v) for v in groups.values()),'native_verified_canonical_turns':verified,'empty_attachment_communications':empty,'native_message_identity_unknown_turns':unknown_native_ids,'original_timestamp_unknown_turns':unknown_timestamps,'source_groups':len(groups),'failures':failures,'method':'Reopen authoritative originals; independently resolve native record roles, identities, timestamps, source order and text field spans; compare exact canonical transcript body bytes. No semantic promotion.'}
    return result
