"""Deterministic record writers; no semantic inference or provider-native parsing."""
import collections, copy, datetime as dt, json, pathlib, re
from .records import *
from .schema import *

def sections(names): return '\n'.join('## '+n+'\n\nUnknown; evidence review required.\n' for n in names)
def secret_scan(data):
    patterns=(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'AKIA[0-9A-Z]{16}',rb'(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_\-]{20,}',rb'(?i)(?:api[_-]?key|password|secret|access[_-]?token)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{12,}')
    if any(re.search(p,data) for p in patterns): raise ValueError('Potential credential material detected; preservation stopped for authorized review')
    if len(data)>=100*1024*1024: raise ValueError('Source exceeds GitHub file limit; storage authorization required')

def register_export(root,source,provider,environment,scope,completeness='unknown',native_export_id=None,previous_export_ids=None):
    raw=source.read_bytes(); secret_scan(raw); sha=digest(raw)
    for p,d,_ in collect(root):
        if d['record_type']=='sot_export' and d['provider']==provider and d['environment']==environment and any(sf['sha256']==sha for sf in d['source_files']):
            from .staging import require_validation
            require_validation(root,{p.relative_to(root).as_posix()})
            return d
    for value in (provider,environment):
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',value): raise ValueError('Provider/environment must be path-safe names')
    from .staging import overlay_info
    base=overlay_info(root)
    archive_root=base['base_root'] if base else root
    orphans=[p for p in (archive_root/'SOT/EXPORTS').glob('*/original.*') if not (p.parent/'export.yaml').exists() and digest(p.read_bytes())==sha]
    if len(orphans)>1: raise ValueError('Ambiguous orphan source preservation; review checkpoints')
    eid=orphans[0].parent.name if orphans else new_id(); ext=orphans[0].suffix if orphans else (source.suffix or '.bin'); path=pathlib.Path('SOT/EXPORTS')/eid/('original'+ext)
    d=dict(record_type='sot_export',schema_version=1,export_id=eid,provider=provider,environment=environment,native_export_id=native_export_id,source_files=[dict(path=path.as_posix(),sha256=sha)],captured_at=now(),capture_completeness=completeness,capture_scope=scope,previous_export_ids=previous_export_ids or [])
    check_record(d)
    known={v['export_id'] for _,v,_ in collect(root) if v['record_type']=='sot_export'}
    if not set(d['previous_export_ids'])<=known: raise ValueError('Previous export missing')
    folder=root/path.parent; folder.mkdir(parents=True,exist_ok=bool(orphans))
    if orphans: inside(root,path)
    try:
        if not (root/path).exists(): (root/path).write_bytes(raw)
        write(folder/'export.yaml',d)
    except Exception:
        # Preserve original bytes if the metadata write fails; retry discovers the checkpoint.
        raise
    rebuild(root); return d

def raise_exception(root,classification,affected,evidence,last_sha=None):
    d=dict(record_type='exception',schema_version=1,exception_id=new_id(),classification=classification,detected_at=now(),affected_record_ids=affected,evidence=evidence,last_verified_sha=last_sha,status='open',recovery_requirements=['Review evidence and resume from last verified checkpoint'],correcting_commits=[])
    check_record(d); p=root/'INDEX/EXCEPTIONS.yaml'; index=load(p)
    existing=next((x for x in index['exceptions'] if x['classification']==classification and x['affected_record_ids']==affected and x['evidence']==evidence and x['status']=='open'),None)
    if existing: return existing
    index['exceptions'].append(d); check_record(index,'exceptions-registry'); atomic(p,yaml.safe_dump(index,sort_keys=False)); rebuild(root); return d

def register_sot(root,export_id,payload):
    """payload is an explicit normalized mapping made by a supported adapter/operator.

    This is not a parser for a provider's native proprietary export.
    """
    exports={d['export_id']:d for _,d,_ in collect(root) if d['record_type']=='sot_export'}
    if export_id not in exports: raise ValueError('Unknown source export')
    exp=exports[export_id]; native=payload.get('native_conversation_id'); locator=payload.get('source_conversation_locator'); incoming=payload['messages']
    if native is None and not locator and not payload.get('sot_id'): raise ValueError('Missing native identity requires exact source conversation locator or an explicit existing SOT ID')
    if not incoming: raise ValueError('No source messages supplied')
    for m in incoming:
        if not isinstance(m.get('content'),str) or not m.get('role'): raise ValueError('Each message requires exact normalized content and role')
    native_ids=[m.get('native_message_id') for m in incoming if m.get('native_message_id') is not None]
    if len(native_ids)!=len(set(native_ids)): raise ValueError('Duplicate native message identities')
    fingerprint=digest(json.dumps([{k:m.get(k) for k in ('role','content','native_message_id')} for m in incoming],sort_keys=True,ensure_ascii=False).encode())
    candidates=[(p,d) for p,d,_ in collect(root) if d['record_type']=='sot_conversation' and (d['provider'],d['environment'])==(exp['provider'],exp['environment']) and ((native is not None and d['native_conversation_id']==native) or (native is None and d['native_conversation_id'] is None and ((payload.get('sot_id')==d['sot_id']) or (d['fingerprint']==fingerprint and export_id in d['export_ids'] and d['source_conversation_locator']==locator))))]
    if len(candidates)>1: raise ValueError('Ambiguous source identity')
    if native is None and not candidates:
        likely=[d for _,d,_ in collect(root) if d['record_type']=='sot_conversation' and d['native_conversation_id'] is None and d['fingerprint']==fingerprint and export_id not in d['export_ids']]
        if likely: raise ValueError('Likely duplicate without native identity; supply existing sot_id only after provenance review')
    old_messages=[]; old_text=''; old=None
    if candidates:
        from .staging import require_validation
        require_validation(root,{candidates[0][0].relative_to(root).as_posix()})
        manifest,old=candidates[0]; folder=manifest.parent; old_messages=load(folder/'MESSAGES.yaml')['messages']; old_text=inside(root,(folder/'transcript.md').relative_to(root)).read_text()
        # Existing exact normalized content is compared against the transcript blocks.
        chunks={mid:content for mid,content in re.findall(r'^### msg-([a-f0-9-]{36})\n(.*?)(?=^### msg-|\Z)',old_text,re.M|re.S)}
        for i,m in enumerate(incoming[:len(old_messages)]):
            existing=old_messages[i]
            if existing['native_message_id']!=m.get('native_message_id') or existing['role']!=m['role'] or existing['original_timestamp']!=m.get('original_timestamp') or digest(m['content'].encode())!=existing['content_sha256']:
                raise_exception(root,'concurrent_semantic_conflict',[old['sot_id']],['Conflicting normalized content preserved in export '+export_id]); raise ValueError('Conflicting evidence; original export retained, conversation unchanged')
        if len(incoming)==len(old_messages) and export_id in old['export_ids']: return old
        sid=old['sot_id']
    else:
        sid=new_id(); year=str(dt.datetime.now(dt.timezone.utc).year); folder=root/'SOT'/exp['provider']/exp['environment']/year/sid
    entries=copy.deepcopy(old_messages); additions=[]
    for i,m in enumerate(incoming[len(old_messages):],len(old_messages)+1):
        mid=new_id(); entry=dict(message_id=mid,native_message_id=m.get('native_message_id'),ordinal=i,role=m['role'],original_timestamp=m.get('original_timestamp'),export_id=export_id,source_locator=m.get('source_locator'),content_sha256=digest(m['content'].encode()),anchor='msg-'+mid,attachment_ids=m.get('attachment_ids',[]),limitations=m.get('limitations',[]))
        entries.append(entry)
        additions.append(f"### msg-{mid}\n\nRole: {m['role']}  \nOriginal timestamp: {m.get('original_timestamp') or 'unknown'}  \nExport: {export_id}  \nSource locator: {m.get('source_locator') or 'unavailable'}\n\n{m['content']}\n\n")
    states={op:'pending' for op in OPERATIONS}; states.update(source_preservation='complete',normalization='complete')
    if old: states=copy.deepcopy(old['states']); states.update(native_completeness='pending',knowledge_reconciliation='pending',work_reconciliation='pending',topic_indexing='pending')
    aids={aid for m in entries for aid in m['attachment_ids']}
    artifact_records=load(root/'INDEX/ARTIFACTS.yaml')['artifacts']
    logical_ids=[a['artifact_id'] for a in artifact_records if a['sot_id']==sid and not a.get('conflicts_with')]
    declared=payload.get('attachment_inventory',{})
    inventory=dict(expected_logical_attachments=declared.get('expected_logical_attachments'),inventory_verification=declared.get('inventory_verification','unknown'),inventory_evidence=declared.get('inventory_evidence',[]),registered_logical_attachment_ids=sorted(logical_ids))
    # A later export reopens review even if its caller repeats the older declaration.
    if old:
        inventory.update(expected_logical_attachments=None,inventory_verification='unknown',inventory_evidence=[])
    states['attachment_preservation']='pending'
    reasons=copy.deepcopy(old['state_reasons']) if old else {}
    reasons.pop('attachment_preservation',None)
    if inventory['inventory_verification']=='verified' and inventory['expected_logical_attachments']==0 and inventory['inventory_evidence'] and not logical_ids:
        states['attachment_preservation']='not_applicable'
        reasons['attachment_preservation']='Verified source inventory contains zero attachments: '+'; '.join(inventory['inventory_evidence'])
    d=dict(record_type='sot_conversation',schema_version=1,sot_id=sid,provider=exp['provider'],environment=exp['environment'],native_conversation_id=native,fingerprint=fingerprint,source_conversation_locator=locator,title=payload['title'],export_ids=list(dict.fromkeys((old['export_ids'] if old else [])+[export_id])),source_files=(old['source_files'] if old else [])+[sf for sf in exp['source_files'] if not old or sf not in old['source_files']],transcript_file='transcript.md',message_index_file='MESSAGES.yaml',topic_map_file='TOPIC_MAP.yaml',topic_map_markdown_file='TOPIC_MAP.md',timestamps=old['timestamps'] if old else dict(original_started_at=payload.get('original_started_at'),original_ended_at=payload.get('original_ended_at'),imported_at=now()),attachment_inventory=inventory,counts=dict(total_messages=len(entries),role_totals=dict(collections.Counter(m['role'] for m in entries)),user_turns=sum(m['role']=='user' for m in entries),attachments=len(logical_ids),topics=None),states=states,state_reasons=reasons,integrated_subject_ids=old['integrated_subject_ids'] if old else [],integrated_work_item_ids=old['integrated_work_item_ids'] if old else [],capture_gaps=payload.get('capture_gaps',[]),last_processed_at=now())
    index=dict(record_type='message_index',schema_version=1,sot_id=sid,messages=entries)
    topics=dict(record_type='topic_map',schema_version=1,sot_id=sid,topics=[])
    for data in (d,index,topics): check_record(data)
    folder.mkdir(parents=True,exist_ok=True); (folder/'attachments').mkdir(exist_ok=True)
    keep=inside(root,(folder/'attachments/.gitkeep').relative_to(root))
    if not keep.exists(): keep.touch()
    atomic(folder/'transcript.md',(old_text or '# Normalized transcript\n\n')+''.join(additions)); write(folder/'MESSAGES.yaml',index)
    if not old: write(folder/'TOPIC_MAP.yaml',topics); atomic(folder/'TOPIC_MAP.md','# Topic map\n\nPending evidence review.\n')
    write(folder/'manifest.yaml',d); rebuild(root); return d

def create_subject(root,name,slug,scope):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug): raise ValueError('Use a lowercase subject slug')
    if any(normalized(name)==normalized(n) for _,d,_ in collect(root) if d['record_type']=='knowledge_subject' for n in [d['canonical_name'],*d['aliases']]): raise ValueError('Subject name already registered')
    sid=new_id(); stamp=now()
    d=dict(record_type='knowledge_subject',schema_version=1,subject_id=sid,canonical_name=name,aliases=[],classifications=[],scope=scope,exclusions=[],status='provisional',related_subject_ids=[],source_refs=[],created_at=stamp,updated_at=stamp,last_evidence_reviewed_at=None,integration_state='pending',contributions=[])
    check_record(d); folder=root/'KNOWLEDGE'/slug; folder.mkdir(parents=True,exist_ok=False)
    write(folder/'subject.yaml',d)
    atomic(folder/'INDEX.md',f'# {name}\n\nID: {sid}\n\nScope: {scope}\n\nExclusions: undetermined. Aliases: none. Classifications: none.\n\nProvisional subject awaiting evidence review.\n\n[Current](CURRENT.md) · [Evolution](EVOLUTION.md) · [Sources](SOURCES.md) · [Metadata](subject.yaml) · [Artifacts](ARTIFACTS/)\n')
    atomic(folder/'CURRENT.md',sections(CURRENT_SECTIONS)); atomic(folder/'EVOLUTION.md','# Evolution\n\nNo reviewed contributions. Unknown occurrence dates remain unknown.\n'); atomic(folder/'SOURCES.md','# Sources\n\nNo evidence associated.\n')
    (folder/'ARTIFACTS').mkdir(); (folder/'ARTIFACTS/.gitkeep').touch(); rebuild(root); return d

def create_work(root,title,kind):
    wid=new_id(); stamp=now()
    d=dict(record_type='work_item',schema_version=3,work_item_id=wid,title=title,aliases=[],type=kind,status='planned',status_history=[dict(previous=None,new='planned',effective_at=None,reason='Explicit creation instruction',source_refs=[])],subject_ids=[],source_refs=[],relationships=dict(parent=None,children=[],depends_on=[],related_to=[],follows_from=[]),external_parties=[],actions=[],dates=[],events=[],outcomes=[],last_external_verification=None,resumption=dict(current_position=None,last_meaningful_development=None,next_action_ids=[],unresolved_questions=[],pending_external_matters=[],source_refs=[],last_reviewed_at=None),created_at=stamp,updated_at=stamp)
    write(root/f'WORK/ITEMS/work_{wid}.md',d,sections(WORK_SECTIONS)); rebuild(root); return d

def transition_work(root,wid,status,reason,effective_at=None,source_refs=None):
    p=inside(root,f'WORK/ITEMS/work_{wid}.md'); w,body=load(p)
    if not source_refs: raise ValueError('Status transition requires source evidence')
    w['status_history'].append(dict(previous=w['status'],new=status,effective_at=effective_at,reason=reason,source_refs=source_refs or [])); w['status']=status; w['updated_at']=now()
    write(p,w,body); rebuild(root); return w

def associate_source(root,query,ref,classification,description,occurred_at=None):
    p,d=resolve_subject(root,query)
    sots={v['sot_id']:q for q,v,_ in collect(root) if v['record_type']=='sot_conversation'}
    if ref['sot_id'] not in sots: raise ValueError('Source SOT missing')
    mids={m['message_id'] for m in load(sots[ref['sot_id']].parent/'MESSAGES.yaml')['messages']}
    if not ref['message_ids'] or not set(ref['message_ids'])<=mids: raise ValueError('Unresolved source messages')
    if ref not in d['source_refs']: d['source_refs'].append(ref)
    contribution=dict(occurred_at=occurred_at,classification=classification,description=description,source_refs=[ref])
    if contribution not in d['contributions']: d['contributions'].append(contribution)
    d['contributions'].sort(key=lambda c:(occurrence_key(c['occurred_at']),c['description'])); d['updated_at']=now(); check_record(d)
    # Association never changes CURRENT or claims semantic integration.
    lines=['# Sources','']
    for c in d['contributions']:
        lines.extend([f"## {c['occurred_at'] or 'Unknown occurrence date'} — {c['classification']}",'',c['description'],''])
        for r in c['source_refs']:
            rel=pathlib.Path(os.path.relpath(sots[r['sot_id']].parent/'transcript.md',p.parent)).as_posix()
            lines.extend(f"- [{mid}]({rel}#msg-{mid})" for mid in r['message_ids'])
        lines.append('')
    evolution=p.parent/'EVOLUTION.md'
    text=evolution.read_text(); marker='<!-- BEGIN DERIVED CONTRIBUTION TIMELINE -->'
    preserved=text.split(marker)[0].rstrip()
    timeline=[preserved,'',marker,'']
    for c in d['contributions']:
        timeline.extend([f"## {c['occurred_at'] or 'Unknown occurrence date'} — {c['classification']}",'',c['description'],''])
        for r in c['source_refs']:
            rel=pathlib.Path(os.path.relpath(sots[r['sot_id']].parent/'transcript.md',p.parent)).as_posix()
            timeline.extend(f"- [{mid}]({rel}#msg-{mid})" for mid in r['message_ids'])
        timeline.append('')
    write(p,d); atomic(p.parent/'SOURCES.md','\n'.join(lines)+'\n'); atomic(evolution,'\n'.join(timeline)+'\n'); rebuild(root); return d

def set_processing(root,sid,operation,state,reason=None):
    candidates=[(p,d) for p,d,_ in collect(root) if d['record_type']=='sot_conversation' and d['sot_id']==sid]
    if not candidates: raise ValueError('SOT missing')
    p,d=candidates[0]
    if operation not in OPERATIONS: raise ValueError('Unknown processing operation')
    if state=='not_applicable' and not reason: raise ValueError('not_applicable requires evidence-backed reason')
    d['states'][operation]=state
    if reason: d['state_reasons'][operation]=reason
    if operation=='topic_indexing' and state=='complete': d['counts']['topics']=len(load(p.parent/'TOPIC_MAP.yaml')['topics'])
    d['last_processed_at']=now(); check_record(d)
    from .staging import overlay_info,candidate
    from .validation import validate_incremental
    if overlay_info(root):
        write(p,d); rebuild(root)
        errors=[f for f in validate_incremental(root,{p.relative_to(root).as_posix()}) if f['severity']=='ERROR']
        if errors: raise ValueError('Processing assertion fails incremental validation: '+json.dumps(errors))
    else:
        with candidate(root) as target:
            write(target/p.relative_to(root),d); rebuild(target)
    return d

class EvidenceConflict(ValueError):
    """A reported conflict whose preserved evidence/exception must be published."""
    preserve_changes = True


def register_artifact(root, sot_id, source, native_artifact_id=None,
                      message_ids=None, description=None, artifact_id=None):
    """Preserve an attachment without provider parsing or implicit replacement."""
    matches = [(p,d) for p,d,_ in collect(root)
               if d['record_type']=='sot_conversation' and d['sot_id']==sot_id]
    if len(matches)!=1: raise ValueError('SOT missing or ambiguous')
    manifest, sot = matches[0]
    from .staging import require_validation
    require_validation(root,{manifest.relative_to(root).as_posix()})
    if not source.is_file(): raise ValueError('Attachment source file does not exist')
    message_ids = list(dict.fromkeys(message_ids or []))
    index_path = manifest.parent / 'MESSAGES.yaml'
    messages = load(index_path)
    known = {m['message_id'] for m in messages['messages']}
    if not set(message_ids)<=known: raise ValueError('Missing attachment message references')
    raw = source.read_bytes()
    secret_scan(raw)
    sha = digest(raw)
    artifacts_path = root / 'INDEX/ARTIFACTS.yaml'
    registry = load(artifacts_path)
    same_sot = [a for a in registry['artifacts'] if a['sot_id']==sot_id]
    if artifact_id:
        candidates = [a for a in same_sot if a['artifact_id']==artifact_id]
        if len(candidates)!=1: raise ValueError('Established artifact identity not found')
    elif native_artifact_id is not None:
        candidates = [a for a in same_sot if a['native_artifact_id']==native_artifact_id
                      and not a.get('conflicts_with')]
    else:
        candidates = [a for a in same_sot if a['native_artifact_id'] is None and a['sha256']==sha]
    if len(candidates)>1: raise ValueError('Ambiguous attachment identity')
    old = candidates[0] if candidates else None
    if old and old.get('conflicts_with'):
        roots=[a for a in same_sot if a['artifact_id']==old['conflicts_with'] and not a.get('conflicts_with')]
        if len(roots)!=1: raise ValueError('Canonical artifact identity does not resolve')
        old=roots[0]
    if old and native_artifact_id is not None and old['native_artifact_id']!=native_artifact_id:
        raise ValueError('Native identity differs from the established artifact')
    conflict = old is not None and old['sha256']!=sha
    if old:
        preserved = inside(root, old['path'])
        if not preserved.is_file() or digest(preserved.read_bytes())!=old['sha256']:
            raise ValueError('Established attachment integrity failure; original metadata retained')
    if conflict:
        # Repeating the identical conflict also reuses its already-preserved identity.
        prior = [a for a in same_sot if a.get('conflicts_with')==old['artifact_id'] and a['sha256']==sha]
        if len(prior)>1: raise ValueError('Ambiguous conflicting attachment evidence')
        entry = prior[0] if prior else None
    else:
        entry = old
    if entry is None:
        aid = new_id()
        ext = source.suffix if re.fullmatch(r'\.[A-Za-z0-9]{1,16}', source.suffix) else '.bin'
        rel = manifest.parent.relative_to(root) / 'attachments' / aid / ('original'+ext)
        entry = dict(record_type='artifact',schema_version=1,artifact_id=aid,
                     native_artifact_id=(native_artifact_id if native_artifact_id is not None else (old['native_artifact_id'] if old else None)),
                     description=description,conflicts_with=old['artifact_id'] if conflict else None,
                     sot_id=sot_id,source_refs=[],path=rel.as_posix(),sha256=sha)
        check_record(entry)
        destination = inside(root, rel)
        destination.parent.mkdir(parents=True,exist_ok=False)
        destination.write_bytes(raw)
        registry['artifacts'].append(entry)
    elif digest(inside(root,entry['path']).read_bytes())!=entry['sha256']:
        raise ValueError('Attachment integrity failure')
    if message_ids:
        ref=dict(sot_id=sot_id,message_ids=message_ids)
        if ref not in entry['source_refs']: entry['source_refs'].append(ref)
        for m in messages['messages']:
            logical_id=entry.get('conflicts_with') or entry['artifact_id']
            if m['message_id'] in message_ids and logical_id not in m['attachment_ids']:
                m['attachment_ids'].append(logical_id)
    check_record(registry,'artifact-index')
    atomic(artifacts_path,yaml.safe_dump(registry,sort_keys=False,allow_unicode=True))
    write(index_path,messages)
    logical_ids=sorted(a['artifact_id'] for a in registry['artifacts'] if a['sot_id']==sot_id and not a.get('conflicts_with'))
    inventory=sot['attachment_inventory']
    added=set(logical_ids)-set(inventory['registered_logical_attachment_ids'])
    inventory['registered_logical_attachment_ids']=logical_ids
    sot['counts']['attachments']=len(logical_ids)
    if added or conflict:
        sot['states']['attachment_preservation']='blocked' if conflict else 'pending'
        sot['state_reasons'].pop('attachment_preservation',None)
    expected=inventory['expected_logical_attachments']
    if inventory['inventory_verification']=='verified' and expected is not None and len(logical_ids)>expected:
        inventory['inventory_verification']='partial'
    write(manifest,sot)
    if conflict:
        raise_exception(root,'duplicate_identity_conflict',[old['artifact_id'],entry['artifact_id'],sot_id],
                        ['Conflicting attachment bytes preserved as '+entry['artifact_id']+'; original '+old['artifact_id']+' unchanged'])
    rebuild(root)
    if conflict: raise EvidenceConflict('Conflicting attachment evidence preserved as '+entry['artifact_id']+'; established bytes unchanged')
    return entry


def set_attachment_inventory(root,sot_id,expected,verification,evidence):
    matches=[(p,d) for p,d,_ in collect(root) if d['record_type']=='sot_conversation' and d['sot_id']==sot_id]
    if len(matches)!=1: raise ValueError('SOT missing or ambiguous')
    p,d=matches[0]
    if expected is not None and expected<0: raise ValueError('Expected attachments must be nonnegative')
    if verification=='verified' and (expected is None or not evidence): raise ValueError('Verified inventory requires a known count and source evidence')
    logical=sorted(a['artifact_id'] for a in load(root/'INDEX/ARTIFACTS.yaml')['artifacts'] if a['sot_id']==sot_id and not a.get('conflicts_with'))
    if verification=='verified' and len(logical)>expected: raise ValueError('Verified source inventory cannot exclude registered logical attachments')
    d['attachment_inventory']=dict(expected_logical_attachments=expected,inventory_verification=verification,inventory_evidence=evidence,registered_logical_attachment_ids=logical)
    d['states']['attachment_preservation']='pending'
    d['state_reasons'].pop('attachment_preservation',None)
    if verification=='verified' and expected==0:
        d['states']['attachment_preservation']='not_applicable'
        d['state_reasons']['attachment_preservation']='Verified source inventory contains zero attachments: '+'; '.join(evidence)
    check_record(d)
    from .staging import overlay_info,candidate
    if overlay_info(root): write(p,d);rebuild(root)
    else:
        with candidate(root) as target: write(target/p.relative_to(root),d);rebuild(target)
    return d
