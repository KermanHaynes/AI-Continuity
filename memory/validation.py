"""Finding-only deterministic integrity validation shared by CLI and CI."""
import collections, datetime as dt, hashlib, json, re, subprocess, uuid
from .schema import SCHEMAS, check_record, CURRENT_SECTIONS, WORK_SECTIONS, OPERATIONS
from .records import collect, load, inside, digest, registry_views, agenda, temporal, normalized, topic_markdown, subject_index, occurrence_key

def _stream_digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

ANCHOR=re.compile(r'^### msg-([0-9a-f-]{36})$',re.M)

def validate(root, *, affected_paths=None):
    root=root.resolve(); findings=[]; records=[]
    def add(code,path,message,severity='ERROR'):
        findings.append(dict(code=code,path=str(path.relative_to(root)) if path.is_relative_to(root) else str(path),message=message,severity=severity))
    from .records import metadata_paths
    for p in metadata_paths(root):
        try:
            value=load(p); d,body=value if isinstance(value,tuple) else (value,None)
            expected={'export.yaml':'sot_export','manifest.yaml':'sot_conversation','MESSAGES.yaml':'message_index','TOPIC_MAP.yaml':'topic_map','subject.yaml':'knowledge_subject'}.get(p.name)
            if p.parent.name=='ITEMS': expected='work_item'
            if p.parent.name=='PROCESSING': expected='processing_state'
            if p.parent.name=='CLOSEOUTS': expected='closeout'
            if not isinstance(d,dict) or d.get('record_type')!=expected: raise ValueError('Canonical path requires record_type '+str(expected))
            check_record(d); records.append((p,d,body))
        except Exception as e: add('schema_invalid',p,str(e))
    for original in root.glob('SOT/EXPORTS/*/original.*'):
        if not (original.parent/'export.yaml').is_file(): add('orphan_source',original,'Preserved bytes have no export metadata; resume checkpoint')
    for index in root.glob('SOT/*/*/*/*/MESSAGES.yaml'):
        if not (index.parent/'manifest.yaml').is_file(): add('orphan_sot',index,'Normalization checkpoint lacks a conversation manifest')
    for folder in (root/'KNOWLEDGE').glob('*'):
        if folder.is_dir() and not (folder/'subject.yaml').is_file(): add('subject_structure',folder,'Subject directory lacks subject.yaml')
    for p in root.glob('WORK/ITEMS/*'):
        if p.suffix in ('.yaml','.yml'): add('legacy_work',p,'Canonical work must be Markdown v3')
        elif p.suffix=='.md' and not p.name.startswith('work_'): add('identity_path',p,'Unrecognized canonical work filename')
    # Exported JSON schemas must agree exactly with the runtime definitions.
    for name,schema in SCHEMAS.items():
        p=root/f'schemas/{name}.schema.json'
        try:
            if json.loads(p.read_text())!={'$schema':'https://json-schema.org/draft/2020-12/schema',**schema}: add('schema_drift',p,'Schema differs from runtime contract')
        except Exception: add('schema_missing',p,'Required schema missing or malformed')
    bytype=collections.defaultdict(dict); identities={}; messages={}; sots={}; subjects={}; works={}
    def identity(value,p):
        try:
            if str(uuid.UUID(value,version=4))!=value or uuid.UUID(value).version!=4: raise ValueError()
        except Exception: add('invalid_id',p,'Expected UUIDv4'); return
        if value in identities: add('duplicate_id',p,'Permanent ID reused at '+str(identities[value]))
        else: identities[value]=p
    primary={'sot_export':'export_id','sot_conversation':'sot_id','knowledge_subject':'subject_id','work_item':'work_item_id','processing_state':'transaction_id','closeout':'closeout_id'}
    for p,d,b in records:
        kind=d['record_type']; key=primary.get(kind)
        if key:
            # Transaction IDs are reused references only in closeouts; closeout ID is separate.
            identity(d[key],p); bytype[kind][d[key]]=(p,d,b)
        for array,key in [('messages','message_id'),('topics','topic_id'),('actions','action_id'),('dates','date_id'),('events','event_id'),('outcomes','outcome_id')]:
            for item in d.get(array,[]): identity(item[key],p)
    exports=bytype['sot_export']; sots=bytype['sot_conversation']; subjects=bytype['knowledge_subject']; works=bytype['work_item']
    selected_sots=set(); selected_exports=set(); source_paths=set()
    if affected_paths is not None:
        affected_paths=set(affected_paths)
        def referenced(value):
            if isinstance(value,dict):
                if 'sot_id' in value: selected_sots.add(value['sot_id'])
                for v in value.values(): referenced(v)
            elif isinstance(value,list):
                for v in value: referenced(v)
        for p,d,_ in records:
            rel=p.relative_to(root).as_posix()
            directory=p.parent.relative_to(root).as_posix()+'/'
            if rel in affected_paths or (d['record_type']=='sot_conversation' and any(a.startswith(directory) for a in affected_paths)):
                referenced(d)
                if d['record_type']=='sot_export': selected_exports.add(d['export_id'])
        for sid in selected_sots:
            if sid in sots: selected_exports.update(sots[sid][1]['export_ids'])
        source_paths.update(affected_paths)
        for eid in selected_exports:
            if eid in exports: source_paths.update(sf['path'] for sf in exports[eid][1]['source_files'])
        for _,d,_ in records:
            if d['record_type']=='message_index': messages[d['sot_id']]={m['message_id'] for m in d['messages']}
    local_only={sf['path'] for _,ex,_ in exports.values() if ex.get('publication',{}).get('status')=='local_only' for sf in ex['source_files']}
    checked_files=set()
    def file_hash(sf,p):
        if affected_paths is not None and sf['path'] not in source_paths and sf.get('sot_id') not in selected_sots: return
        key=(sf['path'],sf['sha256'])
        if key in checked_files:return
        checked_files.add(key)
        try:
            f=inside(root,sf['path'])
            if not f.is_file():
                if sf['path'] in local_only:add('source_local_only',p,'Original retained locally; remote preservation is explicitly blocked','WARNING')
                else:add('source_missing',p,'Registered source missing')
            elif _stream_digest(f)!=sf['sha256']: add('source_hash',p,'Registered source hash mismatch')
            else:
                rel=f.relative_to(root).as_posix()
                first=subprocess.run(['git','log','--reverse','--format=%H','--',rel],cwd=root,text=True,capture_output=True).stdout.splitlines()
                if first:
                    original=subprocess.run(['git','show',first[0]+':'+rel],cwd=root,capture_output=True)
                    if original.returncode==0 and digest(original.stdout)!=sf['sha256']: add('source_immutable',p,'Source differs from first preserved Git version')
        except ValueError as e: add('path_escape',p,str(e))
    artifacts={}
    for filename,key,schema in [('ARTIFACTS','artifacts','artifact-index'),('EXCEPTIONS','exceptions','exceptions-registry')]:
        p=root/f'INDEX/{filename}.yaml'
        try:
            data=load(p); check_record(data,schema)
            for entry in data[key]:
                identity(entry['artifact_id' if key=='artifacts' else 'exception_id'],p)
                if key=='artifacts': artifacts[entry['artifact_id']]=entry; file_hash(entry,p)
                elif entry['status']=='open': add('open_exception',p,entry['classification'],'WARNING')
        except Exception as e: add('index_schema',p,str(e))
    for p,d,b in records:
        if d['record_type'] in ('sot_export','sot_conversation'):
            for sf in d['source_files']: file_hash(sf,p)
        if d['record_type']=='sot_export':
            expected=f"SOT/EXPORTS/{d['export_id']}/export.yaml"
            if p.relative_to(root).as_posix()!=expected: add('identity_path',p,'Export path differs from identity')
            for eid in d['previous_export_ids']:
                if eid not in exports: add('export_reference',p,'Previous export missing')
    native={}
    for sid,(p,d,_) in sots.items():
        try:
            parts=p.relative_to(root).parts
            if p.parent.name!=sid or parts[1:3]!=(d['provider'],d['environment']) or not re.fullmatch(r'(?:\d{4}|unknown)',parts[3]): add('identity_path',p,'SOT path differs from canonical provider/environment/year/identity')
            composite=(d['provider'],d['environment'],d['native_conversation_id'])
            if composite[2] is not None:
                if composite in native: add('native_identity',p,'Duplicate native conversation identity')
                native[composite]=sid
            if affected_paths is not None and sid not in selected_sots: continue
            inside(root,(p.parent/'transcript.md').relative_to(root))
            for eid in d['export_ids']:
                if eid not in exports: add('export_reference',p,'Missing export')
                else:
                    from .archive import export_supports_environment
                    if not export_supports_environment(exports[eid][1],*composite[:2]):add('export_reference',p,'Export provider/environment mismatch')
            if d['states']['source_preservation']=='complete' and any(exports[eid][1].get('publication',{}).get('status')=='local_only' for eid in d['export_ids'] if eid in exports):add('source_publication_state',p,'Source preservation cannot be complete while a referenced original is explicitly local-only')
            registered={(sf['path'],sf['sha256']) for eid in d['export_ids'] if eid in exports for sf in exports[eid][1]['source_files']}
            if {(sf['path'],sf['sha256']) for sf in d['source_files']}!=registered: add('export_reference',p,'Manifest source files differ from registered export evidence')
            archive_only = d.get('archive_mode') == 'archive_only'
            required_files = ('transcript.md','MESSAGES.yaml') if archive_only else ('transcript.md','MESSAGES.yaml','TOPIC_MAP.yaml','TOPIC_MAP.md')
            for required in required_files:
                if not (p.parent/required).is_file(): add('sot_file_missing',p,required)
            if not archive_only and not (p.parent/'attachments').is_dir(): add('attachments_missing',p,'Required attachments directory')
            index=load(p.parent/'MESSAGES.yaml'); check_record(index,'messages')
            topicmap={'sot_id':sid,'topics':[]}
            if not archive_only or d.get('topic_map_file') is not None:
                topicmap=load(p.parent/'TOPIC_MAP.yaml'); check_record(topicmap,'topic-map')
            if index['sot_id']!=sid or topicmap['sot_id']!=sid: add('sot_identity',p,'Child metadata SOT mismatch')
            if (not archive_only or d.get('topic_map_markdown_file') is not None) and (p.parent/'TOPIC_MAP.md').read_text()!=topic_markdown(topicmap): add('topic_view',p,'Topic Markdown differs from structured topic map')
            if archive_only:
                if d['review']['status']=='reviewed' and d['review']['history'][-1]['transcript_sha256']!=digest((p.parent/'transcript.md').read_bytes()): add('review_version',p,'Reviewed status requires approval of this exact transcript version')
                from .archive import review_findings
                for error in review_findings(d,index): add('archive_contract',p,error)
                for stamp in d['review']['history']:
                    if not set(stamp['subject_ids'])<=subjects.keys() or not set(stamp['work_item_ids'])<=works.keys():add('review_reference',p,'Review stamp contains unresolved downstream identities')
            entries=index['messages']; mids={m['message_id'] for m in entries}; messages[sid]=mids
            raw_transcript=(p.parent/'transcript.md').read_bytes()
            if d.get('transcript_format') == 'conversation_v1':
                anchors=[]; previous_end=0
                for entry in entries:
                    span=entry.get('transcript_byte_range',{})
                    start=span.get('start',0)
                    framing=raw_transcript[previous_end:start].decode('utf-8')
                    anchors.extend(ANCHOR.findall(framing))
                    previous_end=span.get('end',0)
                if entries and raw_transcript[previous_end:] != b'\n\n': add('normalized_content',p,'Unexpected trailing transcript content')
                if not entries:
                    from .archive import render_conversation
                    expected,_=render_conversation(sid,d['title'],d['provider'],d['native_conversation_id'],d['timestamps']['original_started_at'],[])
                    if raw_transcript!=expected:add('normalized_content',p,'Zero-turn transcript differs from its identifying header')
            else:
                anchors=ANCHOR.findall(raw_transcript.decode('utf-8'))
            if len(anchors)!=len(set(anchors)): add('anchor_duplicate',p,'Repeated transcript anchor')
            if set(anchors)!=mids: add('message_anchor',p,'Index and transcript anchors differ')
            if [m['ordinal'] for m in entries]!=list(range(1,len(entries)+1)): add('message_ordinal',p,'Ordinals must be consecutive')
            transcript=(p.parent/'transcript.md').read_text()
            chunks={mid:content for mid,content in re.findall(r'^### msg-([a-f0-9-]{36})\n(.*?)(?=^### msg-|\Z)',transcript,re.M|re.S)}
            native_counts=collections.Counter(x['native_message_id'] for x in entries if x['native_message_id'] is not None)
            for m in entries:
                block=chunks.get(m['message_id'],'')
                prefix=f"\nRole: {m['role']}  \nOriginal timestamp: {m['original_timestamp'] or 'unknown'}  \nExport: {m['export_id']}  \nSource locator: {m['source_locator'] or 'unavailable'}\n\n"
                if d.get('transcript_format') == 'conversation_v1':
                    raw=raw_transcript
                    span=m.get('transcript_byte_range',{})
                    start,end=span.get('start',-1),span.get('end',-1)
                    if not 0 <= start <= end <= len(raw) or digest(raw[start:end])!=m['content_sha256']:
                        add('normalized_content',p,'Exact transcript byte span differs from message index')
                elif not block.startswith(prefix) or not block.endswith('\n\n') or digest(block[len(prefix):-2].encode())!=m['content_sha256']: add('normalized_content',p,'Normalized transcript content or provenance differs from message index')
                if m['anchor']!='msg-'+m['message_id']: add('message_anchor',p,'Incorrect anchor convention')
                if m['export_id'] not in d['export_ids']: add('export_reference',p,'Message source export absent from manifest')
                if m['native_message_id'] is not None and native_counts[m['native_message_id']]!=1: add('native_message_identity',p,'Native message identity duplicated')
                for aid in m['attachment_ids']:
                    if aid not in artifacts: add('artifact_reference',p,'Unknown attachment')
            counts=d['counts']
            if counts['total_messages']!=len(entries): add('message_count',p,'Indexed message count differs')
            if counts['role_totals']!=dict(collections.Counter(m['role'] for m in entries)): add('role_count',p,'Role totals differ')
            if counts['user_turns']!=sum(m['role']=='user' for m in entries): add('user_turn_count',p,'User turn count differs')
            aids={a for m in entries for a in m['attachment_ids']}
            registered_aids={aid for aid,a in artifacts.items() if a['sot_id']==sid and not a.get('conflicts_with')}
            if not aids<=registered_aids: add('artifact_reference',p,'Message attachment must resolve to a canonical logical artifact in this conversation')
            inventory=d['attachment_inventory']
            listed=set(inventory['registered_logical_attachment_ids'])
            if listed!=registered_aids: add('attachment_inventory',p,'Registered inventory IDs differ from canonical logical artifacts')
            if counts['attachments']!=len(registered_aids): add('attachment_count',p,'Logical attachment count differs; conflict versions are excluded')
            verified=inventory['inventory_verification']=='verified'
            expected=inventory['expected_logical_attachments']
            supported=bool(inventory['inventory_evidence'])
            if verified and (expected is None or not supported): add('attachment_inventory',p,'Verified inventory requires known expected count and source evidence')
            if verified and expected is not None and len(registered_aids)>expected: add('attachment_inventory',p,'Verified expected count excludes registered logical attachments')
            state=d['states']['attachment_preservation']
            if state=='not_applicable' and not (verified and expected==0 and supported and not registered_aids): add('attachment_completion',p,'not_applicable requires an evidenced verified zero inventory')
            if state=='complete':
                if not (verified and supported and expected is not None and expected==len(registered_aids)):
                    add('attachment_completion',p,'Completion requires an evidenced verified inventory with every logical attachment registered')
                exceptions=load(root/'INDEX/EXCEPTIONS.yaml')['exceptions']
                versions={aid for aid,a in artifacts.items() if a['sot_id']==sid and a.get('conflicts_with')}
                if any(e['status']=='open' and set(e['affected_record_ids']) & (versions|registered_aids) for e in exceptions): add('attachment_completion',p,'Unresolved attachment exception blocks completion')
            if d['states']['topic_indexing']=='complete' and counts['topics']!=len(topicmap['topics']): add('topic_count',p,'Topic count differs')
            for topic in topicmap['topics']:
                if not set(topic['message_ids'])<=mids: add('topic_reference',p,'Topic message missing')
                if not set(topic['subject_ids'])<=subjects.keys(): add('subject_reference',p,'Topic subject missing')
                if not set(topic['artifact_ids'])<=artifacts.keys(): add('artifact_reference',p,'Topic artifact missing')
            for operation,state in d['states'].items():
                if state in ('pending','in_progress','blocked'): add('incomplete_processing',p,operation+': '+state,'WARNING')
                if state=='not_applicable' and not d['state_reasons'].get(operation): add('processing_evidence',p,'not_applicable requires reason')
                if state=='complete' and operation=='native_completeness':
                    if d['capture_gaps'] or (d['export_ids'][-1] in exports and exports[d['export_ids'][-1]][1]['capture_completeness']!='complete'): add('processing_evidence',p,'Completeness assertion lacks verified complete scope')
            for op,key,target in [('knowledge_reconciliation','integrated_subject_ids',subjects),('work_reconciliation','integrated_work_item_ids',works)]:
                if not set(d[key])<=target.keys(): add('integration_reference',p,'Integrated record missing')
                if d['states'][op]=='complete':
                    for integrated in d[key]:
                        if integrated in target and not any(r['sot_id']==sid for r in target[integrated][1]['source_refs']): add('integration_evidence',p,'Integrated record lacks source chain back to conversation')
                if d['states'][op]=='complete' and not d[key]: add('processing_evidence',p,'Complete integration requires records; use not_applicable with reason otherwise')
        except Exception as e: add('sot_structure',p,str(e))
    navigation=root/'INDEX/CONVERSATIONS.json'
    if navigation.exists() or any(d.get('archive_mode')=='archive_only' for _,d,_ in sots.values()):
        try:
            entries=json.loads(navigation.read_bytes())['conversations']
            if len(entries)!=len(sots) or {entry['sot_id'] for entry in entries}!=set(sots): raise ValueError('Navigation conversation identities differ from canonical manifests')
            for entry in entries:
                path,data,_=sots[entry['sot_id']]
                for field in ('provider','environment','title','native_conversation_id','timestamps','counts','export_ids','source_files','capture_gaps'):
                    if entry[field]!=data[field]: raise ValueError('Navigation field differs from canonical manifest: '+field)
                if entry['transcript']!=(path.parent/'transcript.md').relative_to(root).as_posix() or entry['review_status']!=data.get('review',{}).get('status','unreviewed') or entry['fidelity']!=data['states']['normalization'] or entry['native_completeness']!=data['states']['native_completeness']: raise ValueError('Navigation path or processing status is stale')
        except (OSError,ValueError,KeyError,TypeError) as error:add('archive_navigation',navigation,str(error))
    def refs(value,p):
        if isinstance(value,dict):
            if 'sot_id' in value and 'message_ids' in value:
                if value['sot_id'] not in messages or not set(value['message_ids'])<=messages.get(value['sot_id'],set()): add('source_reference',p,'Unresolved SOT/message evidence')
            for k,v in value.items():
                if k not in ('messages','topics'): refs(v,p)
        elif isinstance(value,list):
            for v in value: refs(v,p)
    def timestamps(value,p):
        if isinstance(value,dict):
            for key,v in value.items():
                if v is not None and (key.endswith('_at') or key=='original_timestamp') and isinstance(v,str):
                    try:
                        if key in ('occurred_at','effective_at') and len(v)==10: dt.date.fromisoformat(v)
                        elif dt.datetime.fromisoformat(v).tzinfo is None: raise ValueError('timestamp lacks offset')
                    except ValueError: add('timestamp',p,'Invalid or zone-less '+key)
                timestamps(v,p)
        elif isinstance(value,list):
            for v in value: timestamps(v,p)
    for p,d,b in records: refs(d,p); timestamps(d,p)
    aliasmap={}
    for sid,(p,d,_) in subjects.items():
        if (p.parent/'INDEX.md').is_file() and (p.parent/'INDEX.md').read_text()!=subject_index(d): add('subject_index',p,'Subject navigation view is stale')
        for name in [d['canonical_name'],*d['aliases']]:
            key=normalized(name)
            if key in aliasmap and aliasmap[key]!=sid: add('alias_collision',p,'Ambiguous normalized name or alias')
            aliasmap[key]=sid
        for name in ('INDEX.md','CURRENT.md','EVOLUTION.md','SOURCES.md'):
            if not (p.parent/name).is_file(): add('subject_structure',p,'Missing '+name)
        if not (p.parent/'ARTIFACTS').is_dir(): add('subject_structure',p,'Missing ARTIFACTS directory')
        current=(p.parent/'CURRENT.md')
        if current.is_file():
            for section in CURRENT_SECTIONS:
                if not re.search(r'^## '+re.escape(section)+r'\n\n\S',current.read_text(),re.M): add('subject_section',p,'Missing or empty '+section)
        if not set(d['related_subject_ids'])<=subjects.keys(): add('subject_reference',p,'Related subject absent')
        if d['integration_state']=='complete' and (not d['source_refs'] or not d['last_evidence_reviewed_at']): add('integration_evidence',p,'Integrated subject requires evidence and review timestamp')
        known=[c['occurred_at'] for c in d['contributions'] if c['occurred_at'] is not None]
        try:
            if known!=sorted(known,key=occurrence_key): add('knowledge_chronology',p,'Contributions must follow original occurrence order')
        except ValueError as e: add('knowledge_chronology',p,str(e))
    for wid,(p,w,body) in works.items():
        if p.name!=f'work_{wid}.md': add('identity_path',p,'Work filename differs from ID')
        for section in WORK_SECTIONS:
            if not re.search(r'^## '+re.escape(section)+r'\n\n\S',body or '',re.M): add('work_section',p,'Missing or empty '+section)
        if not set(w['subject_ids'])<=subjects.keys(): add('subject_reference',p,'Unknown work subject')
        history=w['status_history']; previous=None
        for h in history:
            if h['previous'] is not None and not h['source_refs']: add('status_evidence',p,'Status transition lacks evidence')
            if h['previous']!=previous: add('status_history',p,'Broken status transition chain')
            previous=h['new']
        if not history or previous!=w['status']: add('status_history',p,'Status lacks matching history')
        rel=w['relationships']
        for kind in ('parent','children','depends_on','related_to','follows_from'):
            targets=([rel[kind]] if rel[kind] else []) if kind=='parent' else rel[kind]
            for target in targets:
                if target not in works: add('work_relationship',p,'Unresolved '+kind); continue
                other=works[target][1]['relationships']
                if kind=='parent' and wid not in other['children'] or kind=='children' and other['parent']!=wid or kind=='related_to' and wid not in other['related_to']: add('relationship_reciprocity',p,'Missing reciprocal '+kind)
        dateids={d['date_id'] for d in w['dates']}; actions={a['action_id']:a for a in w['actions']}
        for a in w['actions']:
            if not set(a['date_ids'])<=dateids: add('action_date',p,'Unknown date ID')
        for aid in w['resumption']['next_action_ids']:
            if aid not in actions or actions[aid]['classification']!='established' or actions[aid]['state']!='outstanding': add('next_action',p,'Next action must be established and outstanding')
        for t in w['dates']+w['events']:
            try: temporal(t)
            except Exception as e: add('temporal',p,str(e))
    # Separate directed graphs: parent, depends_on, follows_from only.
    for kind in ('parent','depends_on','follows_from'):
        visited=set(); active=set()
        def visit(wid):
            if wid in active: return True
            if wid in visited or wid not in works: return False
            active.add(wid); rel=works[wid][1]['relationships'][kind]; targets=([rel] if rel else []) if kind=='parent' else rel
            cycle=any(visit(x) for x in targets); active.remove(wid); visited.add(wid); return cycle
        if any(visit(wid) for wid in works): add('cycle_'+kind,root/'WORK/ITEMS','Directed cycle detected')
    try:
        registry,aliases=registry_views(root)
        for filename,key,value in [('REGISTRY','records',registry),('ALIASES','aliases',aliases)]:
            p=root/f'INDEX/{filename}.yaml'; actual=load(p); check_record(actual,'registry' if key=='records' else 'aliases')
            if actual[key]!=value: add('registry_coherence',p,'Derived index differs from canonical records')
        if (root/'WORK/AGENDA.md').read_text()!=agenda([w for _,w,_ in works.values()]): add('agenda_mismatch',root/'WORK/AGENDA.md','Agenda is stale')
    except Exception as e: add('derived_view',root/'INDEX',str(e))
    native_artifacts={}
    for artifact in artifacts.values():
        conflict=artifact.get('conflicts_with')
        if conflict and (conflict not in artifacts or conflict==artifact['artifact_id'] or artifacts[conflict]['sot_id']!=artifact['sot_id'] or artifacts[conflict].get('conflicts_with')): add('artifact_reference',root/'INDEX/ARTIFACTS.yaml','Conflicting artifact identity does not resolve within the conversation')
        if conflict:
            recorded=load(root/'INDEX/EXCEPTIONS.yaml')['exceptions']
            if not any({conflict,artifact['artifact_id']}<=set(e['affected_record_ids']) for e in recorded): add('artifact_conflict_exception',root/'INDEX/ARTIFACTS.yaml','Conflict version requires a persistent exception referencing both identities')
        native=artifact['native_artifact_id']
        if native is not None and not conflict:
            key=(artifact['sot_id'],native)
            if key in native_artifacts: add('artifact_identity',root/'INDEX/ARTIFACTS.yaml','Duplicate native artifact identity without an explicit conflict relationship')
            native_artifacts[key]=artifact['artifact_id']
        refs(artifact,root/'INDEX/ARTIFACTS.yaml')
        if artifact['sot_id'] not in sots: add('artifact_reference',root/'INDEX/ARTIFACTS.yaml','Artifact conversation missing')
    ep=root/'INDEX/EXCEPTIONS.yaml'
    try:
        for e in load(ep)['exceptions']:
            for sha in ([e['last_verified_sha']] if e['last_verified_sha'] else [])+e['correcting_commits']:
                if not re.fullmatch('[a-f0-9]{40}',sha) or subprocess.run(['git','cat-file','-e',sha+'^{commit}'],cwd=root,capture_output=True).returncode: add('exception_commit',ep,'Exception references unavailable or invalid commit')
            if not set(e['affected_record_ids'])<=identities.keys(): add('exception_reference',ep,'Affected identity missing')
    except Exception: pass
    for p,d,_ in records:
        if d['record_type']=='processing_state':
            if d['state']=='archive_verified':
                try:
                    from .transactions import _verify_archive_checkpoint
                    if d['derived_commit'] is not None: raise ValueError('Archive-only checkpoint cannot claim derived reconciliation')
                    _verify_archive_checkpoint(root,d['preservation_commit'],d['starting_sha'])
                    if not set(d['affected_record_ids']) <= sots.keys(): raise ValueError('Archive checkpoint must resolve affected conversations')
                except (ValueError,TypeError) as e: add('processing_evidence',p,str(e))
            if d['state']=='verified_complete' and d['preservation_commit'] and d['derived_commit']:
                try:
                    from .transactions import git,ancestor
                    for sha in (d['starting_sha'],d['preservation_commit'],d['derived_commit']):
                        if not re.fullmatch('[a-f0-9]{40}',sha): raise ValueError('Full checkpoint SHA required')
                        git(root,'cat-file','-e',sha+'^{commit}')
                    if d['preservation_commit']==d['derived_commit'] or not ancestor(root,d['starting_sha'],d['preservation_commit']) or not ancestor(root,d['preservation_commit'],d['derived_commit']): raise ValueError('Checkpoint ancestry is invalid')
                except ValueError as e: add('processing_evidence',p,str(e))
            if not set(d['affected_record_ids'])<=identities.keys(): add('processing_reference',p,'Affected record missing')
            if d['state'] not in ('verified_complete','archive_verified'): add('incomplete_transaction',p,d['state'],'WARNING')
            if d['state']=='verified_complete' and set(d['affected_record_ids'])!={r['record_id'] for r in d['reconciliation']}: add('processing_evidence',p,'Every affected record requires a reconciliation disposition')
            if d['state']=='verified_complete' and (not d['preservation_commit'] or not d['derived_commit'] or any(x['disposition']=='incomplete' for x in d['reconciliation'])): add('processing_evidence',p,'Complete transaction lacks checkpoints/reconciliation')
        if d['record_type']=='closeout':
            try:
                from .transactions import verify_receipt
                verify_receipt(root,d,fetch=False)
            except Exception as e: add('receipt_integrity',p,str(e))
    return sorted(findings,key=lambda f:(f['path'],f['code'],f['message']))


def validate_incremental(root, affected_paths):
    """Metadata graph plus affected SOT/source checks; never a full archive audit.

    Global metadata is needed to detect duplicate permanent IDs, resolve references,
    reconcile indexes and validate directed relationship cycles. Only affected
    conversations, their exports, and affected attachments have source bytes read.
    """
    return validate(root, affected_paths=set(affected_paths))
