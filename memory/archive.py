"""Archive-only invariants. No semantic promotion or operational reconstruction."""
import hashlib


def export_supports_environment(export, provider, environment):
    return export['provider']==provider and (export['environment']==environment or (provider=='grok' and export['environment']=='grok_package' and environment in ('grok_in_x','standalone','unknown')) or (provider=='openai' and export['environment']=='chatgpt_package' and environment in ('chatgpt','chatgpt_group')) or (provider=='claude' and export['environment']=='web_and_design' and environment in ('web','design')))


def review_findings(manifest, index):
    errors = []
    messages = index['messages']
    ids = {m['message_id'] for m in messages}
    review = manifest.get('review')
    if not review:
        return ['Archive-only conversation requires explicit review metadata']
    pending = set(review['pending_message_ids'])
    if not pending <= ids:
        errors.append('Pending review scope references missing messages')
    approved = set()
    for stamp in review['history']:
        scope = set(stamp['message_ids'])
        if not scope or not scope <= ids:
            errors.append('Review history requires a nonempty resolvable message scope')
        approved.update(scope)
    if review['status'] == 'reviewed' and (pending or approved != ids or not review['history']):
        errors.append('Reviewed status requires approved scope covering every message and no pending material')
    if review['status'] == 'unreviewed' and not review['history'] and pending != ids:
        errors.append('New archive must leave every message awaiting intellectual review')
    for operation in ('topic_indexing', 'knowledge_reconciliation', 'work_reconciliation'):
        if manifest['states'][operation] != 'pending':
            errors.append('Archive-only operation must leave '+operation+' pending')
    if manifest['integrated_subject_ids'] or manifest['integrated_work_item_ids']:
        errors.append('Archive-only operation cannot claim downstream integration')
    if manifest['topic_map_file'] is not None or manifest['topic_map_markdown_file'] is not None:
        errors.append('Archive-only operation must not require placeholder topic maps')
    positions = {m['message_id']: i for i,m in enumerate(messages)}
    spans = []
    for i, message in enumerate(messages):
        parent = message.get('parent_message_id')
        if parent is not None and (parent not in positions or parent==message['message_id']):
            errors.append('Native branch parent must resolve to a different indexed message')
        if manifest.get('transcript_format') == 'conversation_v1':
            span = message.get('transcript_byte_range')
            if not span:
                errors.append('Conversation format requires an exact body byte range')
            else:
                if span['end'] < span['start']:
                    errors.append('Transcript body range is reversed')
                if spans and span['start'] < spans[-1][1]:
                    errors.append('Transcript body ranges overlap or reverse native order')
                spans.append((span['start'],span['end']))
    parents={m['message_id']:m.get('parent_message_id') for m in messages}
    completed=set()
    for identity in parents:
        seen=set();current=identity
        while current is not None and current in parents and current not in completed:
            if current in seen:
                errors.append('Native branch relationships contain a cycle');break
            seen.add(current);current=parents[current]
        completed.update(seen)
    return errors


def render_conversation(identity, title, provider, native_id, started_at, messages):
    """Render exact body bytes; source strings are never stripped or normalized.

    Callers supply permanent UUIDv4 identities and native order. Parent identities
    remain in MESSAGES.yaml; a branch label avoids implying a single linear chat.
    """
    display_title=title.replace('\r','\\r').replace('\n','\\n')
    data = bytearray((f'# {display_title}\n\nProvider: {provider}\nNative conversation: {native_id or "unknown"}\nRepository conversation: {identity}\nFirst available native timestamp: {started_at or "unknown"}\n\n').encode('utf-8'))
    indexed = []
    for ordinal, item in enumerate(messages, 1):
        body = item['text'].encode('utf-8', errors='strict')
        entry = {k:v for k,v in item.items() if k != 'text'}
        entry['ordinal'] = ordinal
        entry['anchor'] = 'msg-'+item['message_id']
        heading=f"### {entry['anchor']}\n\n**{item['role'].upper()}**"
        if item.get('parent_message_id'):
            heading+=' (parent: msg-'+item['parent_message_id']+')'
        data.extend((heading+'\n\n').encode('utf-8'))
        start=len(data); data.extend(body)
        entry['transcript_byte_range']={'start':start,'end':len(data)}
        entry['content_sha256']=hashlib.sha256(body).hexdigest()
        data.extend(b'\n\n'); indexed.append(entry)
    return bytes(data), indexed


def rebuild_navigation(root):
    """Rebuild archival navigation only. Never regenerate operational records."""
    import json
    import yaml
    from .records import atomic, collect, registry_views
    registry,_=registry_views(root)
    atomic(root/'INDEX/REGISTRY.yaml',yaml.dump({'schema_version':1,'records':registry},Dumper=getattr(yaml,'CSafeDumper',yaml.SafeDumper),sort_keys=False))
    conversations=[]
    for path,data,_ in collect(root,names={'manifest.yaml'}):
        if data['record_type']!='sot_conversation':continue
        conversations.append({
            'sot_id':data['sot_id'],'provider':data['provider'],'environment':data['environment'],
            'title':data['title'],'native_conversation_id':data['native_conversation_id'],
            'timestamps':data['timestamps'],'counts':data['counts'],
            'export_ids':data['export_ids'],'source_files':data['source_files'],
            'transcript':(path.parent/'transcript.md').relative_to(root).as_posix(),
            'fidelity':data['states']['normalization'],'native_completeness':data['states']['native_completeness'],
            'capture_gaps':data['capture_gaps'],'review_status':data.get('review',{}).get('status','unreviewed')})
    conversations.sort(key=lambda x:(x['timestamps']['original_started_at'] is None,x['timestamps']['original_started_at'] or '',x['sot_id']))
    atomic(root/'INDEX/CONVERSATIONS.json',json.dumps({'schema_version':1,'conversations':conversations},ensure_ascii=True,indent=2)+'\n')
    rows=['# Conversation navigation','', 'Archived evidence is unreviewed unless an approval record establishes otherwise. No subject or project classifications are inferred.','']
    for item in conversations:
        # Escape bracket/line framing in provider-native titles, without altering transcript bodies.
        title=item['title'].replace('\\','\\\\').replace('[','\\[').replace(']','\\]').replace('\n',' ')
        rows.append(f"- [{title}](../{item['transcript']}) — {item['provider']}/{item['environment']}; {item['timestamps']['original_started_at'] or 'chronology unknown'}; {item['counts']['total_messages']} turns; {item['review_status']}")
    atomic(root/'INDEX/CONVERSATIONS.md','\n'.join(rows)+'\n')


def register_archive_export(root, source, provider, environment, expected_sha, blockers=None, export_cache=None):
    """Preserve one eligible original without touching KNOWLEDGE or WORK views."""
    import pathlib, shutil
    from .archive_inventory import source_findings
    from .records import collect, inside, new_id, now, write
    source=pathlib.Path(source).resolve()
    digest=hashlib.sha256()
    with source.open('rb') as stream:
        while block:=stream.read(1024*1024):digest.update(block)
    if digest.hexdigest()!=expected_sha: raise ValueError('Source changed after inventory')
    blockers=list(blockers or [])
    if source.stat().st_size>=100*1024*1024 and not blockers: raise ValueError('Source exceeds the ordinary object size limit; configure and verify supported large-file storage before publication.')
    if not blockers and source_findings(source): raise ValueError('Potential credentials: original retained locally, publication blocked')
    for record in (export_cache.values() if export_cache is not None else (d for _,d,_ in collect(root))):
        if record['record_type']=='sot_export' and record['provider']==provider and record['environment']==environment and any(f['sha256']==expected_sha for f in record['source_files']):return record
    identity=new_id(); suffix=''.join(source.suffixes) or '.bin'
    target=inside(root,f'SOT/EXPORTS/{identity}/original{suffix}')
    from .staging import track_write
    if not blockers:track_write(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    if not blockers:
        shutil.copyfile(source,target)
        with target.open('rb') as stream: copied=hashlib.file_digest(stream,'sha256').hexdigest()
        if copied!=expected_sha:raise ValueError('Copied original checksum mismatch')
    data=dict(record_type='sot_export',schema_version=1,export_id=identity,provider=provider,environment=environment,native_export_id=None,source_files=[{'path':target.relative_to(root).as_posix(),'sha256':expected_sha}],captured_at=now(),capture_completeness='unknown',capture_scope='Preserved original source snapshot; verify the actual capture scope before declaring completeness.',previous_export_ids=[])
    data['publication']={'status':'local_only' if blockers else 'eligible_not_verified_remote','blockers':blockers,'retained_local_path':str(source) if blockers else None}
    write(target.parent/'export.yaml',data)
    if export_cache is not None:export_cache[data['export_id']]=data
    return data


def register_archive_conversation(root, export, payload, conversation_cache=None):
    """Register verified dialogue. Snapshot identity conflicts never overwrite text."""
    import collections, heapq, re
    from .records import collect, load, write, new_id, now, atomic, inside
    conversation_key=(payload['provider'],payload['environment'],payload['native_conversation_id'])
    if conversation_cache is None:
        found=[(p,d) for p,d,_ in collect(root) if d['record_type']=='sot_conversation' and (d['provider'],d['environment'],d['native_conversation_id'])==conversation_key]
    else:
        cached=conversation_cache.get(conversation_key)
        found=[(root/cached[0],cached[1])] if cached else []
    if len(found)>1:raise ValueError('Logical conversation identity is ambiguous')
    if found:
        path,manifest=found[0]
        import copy
        manifest=copy.deepcopy(manifest)
        if manifest.get('archive_mode')!='archive_only':raise ValueError('Integrated conversation requires an explicit update procedure')
        index=load(path.parent/'MESSAGES.yaml');raw=inside(root,(path.parent/'transcript.md').relative_to(root)).read_bytes()
        existing=[]
        for item in index['messages']:
            span=item['transcript_byte_range'];existing.append(dict(item,text=raw[span['start']:span['end']].decode('utf-8')))
    else:
        identity=new_id();year=(payload['original_started_at'] or 'unknown')[:4] if payload['original_started_at'] else 'unknown'
        path=inside(root,f"SOT/{payload['provider']}/{payload['environment']}/{year}/{identity}/manifest.yaml")
        existing=[]
        manifest=dict(record_type='sot_conversation',schema_version=1,sot_id=identity,provider=payload['provider'],environment=payload['environment'],native_conversation_id=payload['native_conversation_id'],fingerprint=hashlib.sha256((payload['provider']+':'+payload['environment']+':'+payload['native_conversation_id']).encode()).hexdigest(),source_conversation_locator=None,title=payload['title'],export_ids=[],source_files=[],transcript_file='transcript.md',message_index_file='MESSAGES.yaml',topic_map_file=None,topic_map_markdown_file=None,timestamps={'original_started_at':payload['original_started_at'],'original_ended_at':payload['original_ended_at'],'imported_at':now()},attachment_inventory={'expected_logical_attachments':None,'inventory_verification':'unknown','inventory_evidence':[],'registered_logical_attachment_ids':[]},counts={},states={op:'pending' for op in ('source_preservation','native_completeness','normalization','attachment_preservation','topic_indexing','knowledge_reconciliation','work_reconciliation')},state_reasons={},integrated_subject_ids=[],integrated_work_item_ids=[],capture_gaps=[],last_processed_at=None,archive_mode='archive_only',transcript_format='conversation_v1',review={'status':'unreviewed','history':[],'pending_message_ids':[]})
    if 'native_lineage' in payload:
        lineage=manifest.get('native_lineage')
        updated=dict(lineage or {})
        for field,value in payload['native_lineage'].items():
            if value is None:continue
            if updated.get(field) is not None and updated[field]!=value:manifest['capture_gaps'].append('Conflicting native session lineage across snapshots; original source versions retained')
            else:updated[field]=value
        manifest['native_lineage']={key:updated.get(key) for key in payload['native_lineage']}
    evidence_exports=[export]+payload.get('supporting_exports',[])
    for evidence in evidence_exports:
        if not export_supports_environment(evidence,payload['provider'],payload['environment']):raise ValueError('Supporting evidence provider/environment does not match conversation')
        if evidence['export_id'] not in manifest['export_ids']:
            manifest['export_ids'].append(evidence['export_id']);manifest['source_files'].extend(evidence['source_files'])
    # Persist observation identity separately from native identity. An absent native ID stays null.
    bykey={m.get('archive_identity_key','native:'+str(m['native_message_id'])):m for m in existing}
    edges=collections.defaultdict(set);indegree={key:0 for key in bykey};oldkeys=list(bykey)
    observed=collections.defaultdict(dict)
    for key,item in bykey.items():
        observations=item.get('source_observations') or [{'export_id':item['export_id'],'source_locator':item.get('source_locator') or ''}]
        for observation in observations:
            locator=observation['source_locator'];match=re.search(r'(?:^line:|/(?:chat_messages|messages)/)([0-9]+)',locator)
            ordinal=int(match.group(1)) if match else item.get('ordinal',0)
            bucket=observed[observation['export_id']]
            bucket[key]=min(bucket.get(key,ordinal),ordinal)
    for observations in observed.values():
        sequence=sorted(observations,key=lambda key:observations[key])
        for first,second in zip(sequence,sequence[1:]):edges[first].add(second)
    incoming=[];incoming_seen=set();conflicts=[];new_ids=[]
    for item in payload['messages']:
        key=item['identity_key']
        if key not in incoming_seen:incoming.append(key);incoming_seen.add(key)
        observations=[{'export_id':export['export_id'],'source_locator':item['source_locator'],'field':p['locator'],'start':p['start_character'],'end':p['end_character']} for p in item['parts']]
        if not observations:observations=[{'export_id':export['export_id'],'source_locator':item['source_locator'],'field':item['source_locator'],'start':0,'end':0}]
        if key in bykey:
            current=bykey[key]
            if current['text']!=item['text'] or current['role']!=item['role']:
                conflicts.append('Competing visible dialogue preserved in export '+export['export_id']+' at '+item['source_locator'])
                continue
            for observation in observations:
                if observation not in current.setdefault('source_observations',[]):current['source_observations'].append(observation)
        else:
            mid=payload.get('repository_message_ids',{}).get(key) or new_id();new_ids.append(mid)
            bykey[key]={'message_id':mid,'native_message_id':item['native_message_id'],'role':item['role'],'original_timestamp':item['original_timestamp'],'export_id':export['export_id'],'source_locator':item['source_locator'],'attachment_ids':[],'limitations':item.get('limitations',[]),'parent_message_id':None,'native_parent_message_id':item['parent_native_message_id'],'archive_identity_key':key,'source_observations':observations,'text':item['text']}
        indegree.setdefault(key,0)
    for first,second in zip(incoming,incoming[1:]):
        if first!=second:edges[first].add(second)
    for first,children in edges.items():
        for child in children:indegree[child]+=1
    all_dated=all(item['original_timestamp'] is not None for item in bykey.values())
    encounter={key:i for i,key in enumerate(bykey)}
    def priority(key):
        item=bykey[key]
        return (item['original_timestamp'] if all_dated else '',manifest['export_ids'].index(item['export_id']),encounter[key],key)
    ready=[priority(k) for k in bykey if indegree[k]==0];heapq.heapify(ready);ordered=[]
    while ready:
        key=heapq.heappop(ready)[-1];ordered.append(key)
        for child in sorted(edges[key]):
            indegree[child]-=1
            if indegree[child]==0:heapq.heappush(ready,priority(child))
    # Disjoint evidence without shared identities or comparable native times cannot
    # establish a cross-snapshot chronology. Retain the text and disclose that limit.
    neighbors={key:set(children) for key,children in edges.items()}
    for key in bykey:neighbors.setdefault(key,set())
    for first,children in edges.items():
        for child in children:neighbors[child].add(first)
    native_keys={item['native_message_id']:key for key,item in bykey.items() if item['native_message_id'] is not None}
    for key,item in bykey.items():
        parent=native_keys.get(item.get('native_parent_message_id'))
        if parent:neighbors[key].add(parent);neighbors[parent].add(key)
    if bykey and not all_dated:
        reached=set();todo=[next(iter(bykey))]
        while todo:
            key=todo.pop()
            if key in reached:continue
            reached.add(key);todo.extend(neighbors[key]-reached)
        if reached!=set(bykey):conflicts.append('Disjoint native snapshots lack shared message identities, parent lineage or comparable original timestamps; cross-snapshot order remains unverified')
    if len(ordered)!=len(bykey):raise ValueError('Native snapshot ordering contradicts preserved ordering; source retained, transcript update blocked')
    native_ids={m['native_message_id']:m['message_id'] for m in bykey.values() if m['native_message_id'] is not None}
    native_parents=dict(payload.get('native_parent_map',{}))
    native_parents.update({m['native_message_id']:m['parent_native_message_id'] for m in payload['messages'] if m['native_message_id'] is not None})
    for item in payload['messages']:
        parent=item['parent_native_message_id'];seen=set()
        while parent and parent not in native_ids and parent not in seen:
            seen.add(parent);parent=native_parents.get(parent)
        if parent in native_ids and parent!=item['native_message_id']:bykey[item['identity_key']]['parent_message_id']=native_ids[parent]
    starts=[stamp for stamp in (manifest['timestamps']['original_started_at'],payload['original_started_at']) if stamp]
    manifest['timestamps']['original_started_at']=min(starts,default=None)
    if manifest['title']==manifest['native_conversation_id'] and payload['title']!=manifest['native_conversation_id']:manifest['title']=payload['title']
    body,entries=render_conversation(manifest['sot_id'],manifest['title'],manifest['provider'],manifest['native_conversation_id'],manifest['timestamps']['original_started_at'],[bykey[key] for key in ordered])
    manifest['capture_gaps']=list(dict.fromkeys(manifest['capture_gaps']+payload['limitations']+conflicts))
    dialogue_limitations=[item for item in payload['limitations'] if not item.startswith(('Paginated external-agent replay:','Unapplied metadata association:'))]
    manifest['states'].update(source_preservation='blocked' if any(evidence.get('publication',{}).get('status')=='local_only' for evidence in evidence_exports) or manifest['states']['source_preservation']=='blocked' else 'complete',normalization='blocked' if conflicts or dialogue_limitations or manifest['states']['normalization']=='blocked' else 'complete')
    manifest['state_reasons']['native_completeness']='Record completeness from the verified capture scope and any known gaps.'
    manifest['counts']={'total_messages':len(entries),'role_totals':dict(collections.Counter(m['role'] for m in entries)),'user_turns':sum(m['role']=='user' for m in entries),'attachments':0,'topics':None}
    ends=[x for x in (manifest['timestamps']['original_ended_at'],payload['original_ended_at']) if x]
    manifest['timestamps']['original_ended_at']=max(ends,default=None)
    manifest['last_processed_at']=now()
    pending=manifest['review']['pending_message_ids'];pending.extend(mid for mid in new_ids if mid not in pending)
    if new_ids and manifest['review']['status']=='reviewed':manifest['review']['status']='in_review'
    from .schema import check_record
    graph_errors=review_findings(manifest,{'messages':entries})
    if graph_errors:raise ValueError('Archive graph or review contract requires review: '+ '; '.join(graph_errors))
    check_record(manifest,'manifest')
    check_record({'record_type':'message_index','schema_version':1,'sot_id':manifest['sot_id'],'messages':entries},'messages')
    # Atomic text writer does not normalize embedded CRLF sequences on this platform.
    atomic(path.parent/'transcript.md',body.decode('utf-8'))
    write(path.parent/'MESSAGES.yaml',{'record_type':'message_index','schema_version':1,'sot_id':manifest['sot_id'],'messages':entries})
    write(path,manifest)
    if conversation_cache is not None:conversation_cache[conversation_key]=(path.relative_to(root),manifest)
    return manifest


def reconcile_archive_order(root):
    """Rebuild ordering from native observation locators, keeping exact body bytes."""
    import gc
    enabled=gc.isenabled();gc.disable()
    try:return _reconcile_archive_order(root)
    finally:
        gc.collect()
        if enabled:gc.enable()


def _reconcile_archive_order(root):
    from .records import collect,lock
    from .staging import candidate
    records=collect(root,names={'export.yaml','manifest.yaml'})
    exports={d['export_id']:d for _,d,_ in records if d['record_type']=='sot_export'}
    conversations={(d['provider'],d['environment'],d['native_conversation_id']):(p.relative_to(root),d) for p,d,_ in records if d['record_type']=='sot_conversation' and d.get('archive_mode')=='archive_only'}
    keys=list(conversations)
    for offset in range(0,len(keys),100):
        with lock(root),candidate(root) as target:
            for key in keys[offset:offset+100]:
                _,manifest=conversations[key]
                payload={'provider':manifest['provider'],'environment':manifest['environment'],'native_conversation_id':manifest['native_conversation_id'],'title':manifest['title'],'original_started_at':manifest['timestamps']['original_started_at'],'original_ended_at':manifest['timestamps']['original_ended_at'],'messages':[],'limitations':[]}
                register_archive_conversation(target,exports[manifest['export_ids'][0]],payload,conversations)
            rebuild_navigation(target)
        import gc
        gc.collect()
        print({'ordered_conversations':min(offset+100,len(keys)),'total_conversations':len(keys)},flush=True)
    return {'conversations':len(keys),'scope':'Native message-order constraints, original timestamps and parent lineage; no semantic processing'}
