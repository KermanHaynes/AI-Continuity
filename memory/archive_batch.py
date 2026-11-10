"""Resumable source-first historical archive, without semantic operations."""
import collections
import hashlib
import json
import pathlib
import subprocess
import zipfile
from .archive import register_archive_export, register_archive_conversation, rebuild_navigation, export_supports_environment
from .archive_import import native_captures, capture_payload, verify_capture, NativeFormatError
from .archive_inventory import COMPILED
from .records import atomic, collect, lock, now
from .git_paths import metadata_path
from .staging import candidate


def source_environment(source,path):
    if source['provider']=='UNCLASSIFIED':return 'unknown'
    if source['kind'] in ('native_stream','session_metadata'):return 'local'
    if source['kind']=='native_package' and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as package:
            names=package.namelist()
        web=any(name.endswith('conversations.json') for name in names)
        design=any(name.startswith('design_chats/') and name.endswith('.json') for name in names)
        if web and design:return 'web_and_design'
        if design:return 'design'
    return 'web'


def _safe_blocker(error):
    message=str(error)
    prefixes=('Native snapshot ordering contradicts','Archive graph or review contract','Native field span fidelity comparison failed','Native message order comparison failed','Native message identity or role comparison failed','Native message timestamp comparison failed','Source environment differs','Session metadata identity','Session metadata checksum','Native decompression failed')
    return message if isinstance(error,NativeFormatError) or message.startswith(prefixes) else 'Native interpretation requires source-specific review'


def run(root, corpus, inventory_path, stage):
    # Bulk native/YAML trees are released at bounded checkpoints. Avoid repeatedly
    # scanning the entire live archive graph during every small allocation.
    import gc
    enabled=gc.isenabled();gc.disable()
    try:return _run(root,corpus,inventory_path,stage)
    finally:
        gc.collect()
        if enabled:gc.enable()


def _run(root, corpus, inventory_path, stage):
    root=pathlib.Path(root).resolve();corpus=pathlib.Path(corpus).resolve()
    inventory=json.loads(pathlib.Path(inventory_path).read_bytes())
    if not inventory.get('complete'):raise ValueError('Completed source inventory required')
    catalog=json.loads((corpus/'METADATA/sources.json').read_bytes());byid={s['id']:s for s in catalog}
    ledger=metadata_path(root,'continuity-archive-progress.json')
    progress=json.loads(ledger.read_bytes()) if ledger.exists() else {'source':{},'dialogue':{}}
    selected=[s for s in inventory['sources'] if s['kind']!='supporting_artifact']
    records=collect(root,names={'export.yaml','manifest.yaml'})
    exports={d['export_id']:d for _,d,_ in records if d['record_type']=='sot_export'}
    conversations={(d['provider'],d['environment'],d['native_conversation_id']):(p.relative_to(root),d) for p,d,_ in records if d['record_type']=='sot_conversation'}
    import copy
    for offset in range(0,len(selected),100):
        batch=selected[offset:offset+100]
        pending=[entry for entry in batch if not (progress['source'].get(entry['sha256'],{}).get('export_id') if stage=='sources' else progress['dialogue'].get(entry['sha256'],{}).get('complete'))]
        if not pending:continue
        candidate_progress=copy.deepcopy(progress)
        candidate_exports=copy.deepcopy(exports);candidate_conversations=copy.deepcopy(conversations)
        with lock(root),candidate(root,validate_noop=False) as target:
            for entry in pending:
                sha=entry['sha256'];choices=[byid[sid] for sid in entry['source_ids']]
                source=dict(next((s for s in choices if s['provider'] in ('claude','codex')),choices[0]))
                source['_metadata_source']=byid.get(source.get('metadata_source_id'))
                env=source_environment(source,corpus/source['path'])
                if stage=='sources':
                    export=register_archive_export(target,corpus/source['path'],source['provider'].lower(),env,sha,entry.get('blockers',[]),candidate_exports)
                    candidate_progress['source'][sha]={'export_id':export['export_id'],'manifest':f"SOT/EXPORTS/{export['export_id']}/export.yaml",'publication':export['publication']['status'],'checked_at':now()}
                    continue
                original=progress['source'].get(sha)
                if not original or 'export_id' not in original:continue
                export=candidate_exports[original['export_id']];done=[];blocked=[]
                try:
                    for environment,capture in native_captures(corpus,source):
                        try:
                            if environment=='native_only':
                                done.append({'native_id':capture.native,'classification':'auxiliary_agent_native_evidence_only','verified_snapshot_turns':0})
                                continue
                            if not export_supports_environment(export,source['provider'],environment):raise ValueError('Source environment differs from conversation environment')
                            payload=capture_payload(environment,capture)
                            metadata_source=source.get('_metadata_source')
                            if metadata_source and capture.context.get('metadata_association_verified'):
                                metadata_record=progress['source'].get(metadata_source['sha256'])
                                if not metadata_record or 'export_id' not in metadata_record:raise ValueError('Session metadata evidence has not been registered')
                                payload['supporting_exports']=[candidate_exports[metadata_record['export_id']]]
                            verified=verify_capture(corpus,source,payload)
                            if any(rule.search(m['text'].encode()) for m in payload['messages'] for rule in COMPILED.values()):
                                blocked.append({'native_id':payload['native_conversation_id'],'blocker':'Potential credentials in visible dialogue; transcript publication requires source-specific review'})
                                continue
                            manifest=register_archive_conversation(target,export,payload,candidate_conversations)
                            done.append({'sot_id':manifest['sot_id'],'native_id':manifest['native_conversation_id'],'verified_snapshot_turns':verified,'normalization':manifest['states']['normalization'],'native_records_examined':len(capture.records),'native_records_without_dialogue':sum(r['classification']=='excluded' for r in capture.records),'attachment_only_user_turns':sum(m['role']=='user' and not m['parts'] for m in payload['messages']),'excluded_structure_reasons':dict(collections.Counter(e['reason'] for r in capture.records for e in r['exclusions']))})
                        except (ValueError,OSError,KeyError,TypeError,UnicodeError) as error:
                            blocked.append({'native_id':capture.native,'blocker_type':type(error).__name__,'blocker':_safe_blocker(error)})
                    candidate_progress['dialogue'][sha]={'complete':True,'conversations':done,'blocked':blocked,'checked_at':now()}
                except (ValueError,OSError,KeyError,TypeError,UnicodeError,json.JSONDecodeError) as error:
                    candidate_progress['dialogue'][sha]={'complete':False,'conversations':done,'blocked':blocked,'blocker_type':type(error).__name__,'blocker':_safe_blocker(error),'checked_at':now()}
            rebuild_navigation(target)
        progress=candidate_progress;exports=candidate_exports;conversations=candidate_conversations
        atomic(ledger,json.dumps(progress,ensure_ascii=True,indent=2)+'\n')
        import gc
        gc.collect()
        print(json.dumps({'stage':stage,'source_position':min(offset+100,len(selected)),'source_total':len(selected)}),flush=True)
    return {'stage':stage,'sources_registered':sum('export_id' in s for s in progress['source'].values()),'source_blockers':sum('blocker' in s for s in progress['source'].values()),'dialogue_sources_completed':sum(s.get('complete',False) for s in progress['dialogue'].values()),'dialogue_sources_blocked':sum(not s.get('complete',False) for s in progress['dialogue'].values()),'ledger':str(ledger)}
