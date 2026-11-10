"""Canonical schema definitions exported to schemas/."""
import uuid, hashlib, json
from jsonschema import Draft202012Validator, FormatChecker

def obj(fields, **extra):
    return dict(type='object', required=list(fields), properties=fields, additionalProperties=False, **extra)
def arr(item): return dict(type='array', items=item)
def enum(*values): return dict(enum=list(values))
S={'type':'string'}
TEXT={'type':'string','minLength':1}
NULL={'type':['string','null']}
ID={'type':'string','pattern':r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'}
IDS=dict(type='array',items=ID,uniqueItems=True)
REF=obj({'sot_id':ID,'message_ids':dict(type='array',items=ID,minItems=1,uniqueItems=True)})
REFS=arr(REF)
FILE=obj({'path':TEXT,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}})
STATES=('pending','in_progress','complete','blocked','not_applicable')
OPERATIONS=('source_preservation','native_completeness','normalization','attachment_preservation','topic_indexing','knowledge_reconciliation','work_reconciliation')
LIFECYCLE=('planned','active','waiting','blocked','paused','completed','awaiting_outcome','closed')
WORK_SECTIONS=('Objective','Current Position','Activity and Status History','External Interactions','Outcomes','Constraints and Dependencies','Resume From Here')
CURRENT_SECTIONS=('Established Current Position','Accepted Decisions','Current Constraints','Unresolved Questions','Relevant Active Work','Resume From Here','Last Supporting Evidence')
EVIDENCE=('established_user_position','user_proposal','model_suggestion','rejected_or_superseded','supporting_evidence','contradictory_evidence','unresolved_interpretation')
def record(kind, fields, version=1): return obj({'record_type':{'const':kind},'schema_version':{'const':version},**fields})
TEMPORAL={'at':NULL,'precision':enum('date','datetime','unknown'),'time_zone':NULL}
SCHEMAS={
'export':record('sot_export',{'export_id':ID,'provider':TEXT,'environment':TEXT,'native_export_id':NULL,'source_files':dict(type='array',items=FILE,minItems=1),'captured_at':TEXT,'capture_completeness':enum('complete','partial','unknown'),'capture_scope':TEXT,'previous_export_ids':IDS}),
'manifest':record('sot_conversation',{'sot_id':ID,'provider':TEXT,'environment':TEXT,'native_conversation_id':NULL,'fingerprint':TEXT,'source_conversation_locator':NULL,'title':TEXT,'export_ids':dict(type='array',items=ID,minItems=1,uniqueItems=True),'source_files':arr(FILE),'transcript_file':{'const':'transcript.md'},'message_index_file':{'const':'MESSAGES.yaml'},'topic_map_file':{'const':'TOPIC_MAP.yaml'},'topic_map_markdown_file':{'const':'TOPIC_MAP.md'},'timestamps':obj({'original_started_at':NULL,'original_ended_at':NULL,'imported_at':TEXT}),'attachment_inventory':obj({'expected_logical_attachments':{'type':['integer','null'],'minimum':0},'inventory_verification':enum('verified','partial','unknown'),'inventory_evidence':arr(TEXT),'registered_logical_attachment_ids':IDS}),'counts':obj({'total_messages':{'type':'integer','minimum':0},'role_totals':{'type':'object','additionalProperties':{'type':'integer','minimum':0}},'user_turns':{'type':'integer','minimum':0},'attachments':{'type':'integer','minimum':0},'topics':{'type':['integer','null'],'minimum':0}}),'states':obj({op:enum(*STATES) for op in OPERATIONS}),'state_reasons':{'type':'object','additionalProperties':TEXT},'integrated_subject_ids':IDS,'integrated_work_item_ids':IDS,'capture_gaps':arr(TEXT),'last_processed_at':NULL}),
'messages':record('message_index',{'sot_id':ID,'messages':arr(obj({'message_id':ID,'native_message_id':NULL,'ordinal':{'type':'integer','minimum':1},'role':TEXT,'original_timestamp':NULL,'export_id':ID,'source_locator':NULL,'content_sha256':FILE['properties']['sha256'],'anchor':TEXT,'attachment_ids':IDS,'limitations':arr(TEXT)}))}),
'topic-map':record('topic_map',{'sot_id':ID,'topics':arr(obj({'topic_id':ID,'label':TEXT,'provisional':{'type':'boolean'},'message_ids':dict(type='array',items=ID,minItems=1,uniqueItems=True),'subject_ids':IDS,'decisions_stated':arr(TEXT),'revisions':arr(TEXT),'open_questions':arr(TEXT),'experiments_and_results':arr(TEXT),'artifact_ids':IDS}))}),
'subject':record('knowledge_subject',{'subject_id':ID,'canonical_name':TEXT,'aliases':arr(TEXT),'classifications':arr(TEXT),'scope':TEXT,'exclusions':arr(TEXT),'status':enum('provisional','active','dormant','archived'),'related_subject_ids':IDS,'source_refs':REFS,'created_at':TEXT,'updated_at':TEXT,'last_evidence_reviewed_at':NULL,'integration_state':enum(*STATES),'contributions':arr(obj({'occurred_at':NULL,'classification':enum(*EVIDENCE),'description':TEXT,'source_refs':dict(type='array',items=REF,minItems=1)}))}),
'work-item':record('work_item',{'work_item_id':ID,'title':TEXT,'aliases':arr(TEXT),'type':TEXT,'status':enum(*LIFECYCLE),'status_history':arr(obj({'previous':enum(None,*LIFECYCLE),'new':enum(*LIFECYCLE),'effective_at':NULL,'reason':NULL,'source_refs':REFS})),'subject_ids':IDS,'source_refs':REFS,'relationships':obj({'parent':{'anyOf':[ID,{'type':'null'}]},**{k:IDS for k in ('children','depends_on','related_to','follows_from')}}),'external_parties':arr(TEXT),'actions':arr(obj({'action_id':ID,'description':TEXT,'classification':enum('established','proposed'),'source_refs':dict(type='array',items=REF,minItems=1),'state':enum('outstanding','completed','cancelled','superseded'),'date_ids':IDS})),'dates':arr(obj({'date_id':ID,'kind':enum('external_deadline','internal_target','follow_up'),**TEMPORAL,'state':enum('active','satisfied','superseded','cancelled'),'source_refs':dict(type='array',items=REF,minItems=1),'external_verification':NULL})),'events':arr(obj({'event_id':ID,'description':TEXT,**TEMPORAL,'source_refs':dict(type='array',items=REF,minItems=1),'state':enum('scheduled','occurred','cancelled','unknown')})),'outcomes':arr(obj({'outcome_id':ID,'description':TEXT,'classification':enum('partial','final'),'occurred_at':NULL,'source_refs':dict(type='array',items=REF,minItems=1)})),'last_external_verification':NULL,'resumption':obj({'current_position':NULL,'last_meaningful_development':NULL,'next_action_ids':IDS,'unresolved_questions':arr(TEXT),'pending_external_matters':arr(TEXT),'source_refs':REFS,'last_reviewed_at':NULL}),'created_at':TEXT,'updated_at':TEXT},3),
'artifact':record('artifact',{'artifact_id':ID,'native_artifact_id':NULL,'description':NULL,'conflicts_with':{'anyOf':[ID,{'type':'null'}]},'sot_id':ID,'source_refs':REFS,'path':TEXT,'sha256':FILE['properties']['sha256']}),
'exception':record('exception',{'exception_id':ID,'classification':{'type':'string','pattern':'^[a-z0-9_]+$','not':{'const':'verified_complete'}},'detected_at':TEXT,'affected_record_ids':IDS,'evidence':arr(TEXT),'last_verified_sha':NULL,'status':enum('open','resolved'),'recovery_requirements':arr(TEXT),'correcting_commits':arr(TEXT)}),
'processing':record('processing_state',{'transaction_id':ID,'starting_sha':TEXT,'state':enum('native_capture_unavailable','captured_not_normalized','preserved_not_integrated','derived_incomplete','validation_failed','remote_push_failed','concurrent_semantic_conflict','verified_complete'),'affected_record_ids':IDS,'reconciliation':arr(obj({'record_id':ID,'disposition':enum('changed','verified_unchanged','not_applicable','incomplete'),'evidence':arr(TEXT)})),'preservation_commit':NULL,'derived_commit':NULL,'updated_at':TEXT}),
'closeout':record('closeout',{'closeout_id':ID,'transaction_id':ID,'preservation_commit':TEXT,'derived_commit':TEXT,'remote':TEXT,'branch':TEXT,'observed_sha':TEXT,'verified_at':TEXT,'verification_mechanism':{'const':'git-fetch-and-merge-base'},'affected_record_ids':IDS,'validation_results':arr(TEXT),'limitations':arr(TEXT)}),
}
for name,key in [('registry','records'),('aliases','aliases'),('artifact-index','artifacts'),('exceptions-registry','exceptions')]:
    item={'type':'object'}
    if key=='records': item=obj({'id':ID,'record_type':TEXT,'path':TEXT})
    if key=='aliases': item=obj({'subject_id':ID,'name':TEXT})
    if key=='artifacts': item=SCHEMAS['artifact']
    if key=='exceptions': item=SCHEMAS['exception']
    SCHEMAS[name]=obj({'schema_version':{'const':1},key:arr(item)})
BY_TYPE={s['properties']['record_type']['const']:n for n,s in SCHEMAS.items() if 'record_type' in s['properties']}
_SCHEMA_PROOFS=set()
def check_record(data, name=None):
    name=name or BY_TYPE.get(data.get('record_type'))
    if name not in SCHEMAS: raise ValueError('Unknown record type')
    # Cache only pure schema proofs, keyed by exact data and exact contract.
    # Source integrity, identities, references and transaction checks still run.
    proof=None
    try:
        proof=(name,hashlib.sha256(json.dumps(SCHEMAS[name],sort_keys=True,ensure_ascii=True).encode()).digest(),hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=True).encode()).digest())
    except (TypeError,ValueError):pass
    if proof is not None and proof in _SCHEMA_PROOFS:return
    errors=sorted(Draft202012Validator(SCHEMAS[name],format_checker=FormatChecker()).iter_errors(data),key=lambda e:str(e.path))
    if errors: raise ValueError('; '.join(f'{list(e.path)}: {e.message}' for e in errors))
    if proof is not None:
        if len(_SCHEMA_PROOFS)>=16384:_SCHEMA_PROOFS.clear()
        _SCHEMA_PROOFS.add(proof)

KNOWN_EXCEPTION_CLASSIFICATIONS = frozenset(('native_capture_unavailable','broken_source_reference','attachment_integrity_failure','duplicate_identity_conflict','preserved_not_integrated','deadline_status_discrepancy','unverified_user_approval','concurrent_semantic_conflict','remote_push_failed','validation_failed'))
SCHEMAS['artifact']['required'].remove('description')
SCHEMAS['artifact']['required'].remove('conflicts_with')

# Archive-only records retain the established SOT destinations and identities.
# Optional fields preserve compatibility with existing integrated records.
manifest = SCHEMAS['manifest']['properties']
manifest['archive_mode'] = enum('integrated', 'archive_only')
manifest['transcript_format'] = enum('foundation_v1', 'conversation_v1')
manifest['review'] = obj({
    'status': enum('unreviewed', 'in_review', 'reviewed'),
    'history': arr(obj({
        'transcript_sha256': FILE['properties']['sha256'],
        'message_ids': IDS,
        'completed_at': TEXT,
        'user_approval_evidence': TEXT,
        'subject_ids': IDS,
        'work_item_ids': IDS,
        'deferred_material': arr(TEXT),
    })),
    'pending_message_ids': IDS,
})
for field in ('topic_map_file', 'topic_map_markdown_file'):
    manifest[field] = {'anyOf': [manifest[field], {'type': 'null'}]}
message = SCHEMAS['messages']['properties']['messages']['items']['properties']
message['transcript_byte_range'] = obj({'start': {'type': 'integer', 'minimum': 0}, 'end': {'type': 'integer', 'minimum': 0}})
message['parent_message_id'] = {'anyOf': [ID, {'type': 'null'}]}
message['source_observations'] = arr(obj({'export_id': ID, 'source_locator': TEXT, 'field': TEXT, 'start': {'type': 'integer', 'minimum': 0}, 'end': {'type': 'integer', 'minimum': 0}}))
SCHEMAS['processing']['properties']['state']['enum'].append('archive_verified')
SCHEMAS['closeout']['properties']['operation_mode'] = enum('integrated', 'archive_only')
SCHEMAS['closeout']['properties']['derived_commit'] = NULL
SCHEMAS['closeout']['allOf']=[{
    'if': {'required':['operation_mode'], 'properties':{'operation_mode':{'const':'archive_only'}}},
    'then': {'properties':{'derived_commit':{'type':'null'}}},
    'else': {'properties':{'derived_commit':TEXT}},
}]
SCHEMAS['manifest']['allOf']=[{
    'if': {'required':['archive_mode'], 'properties':{'archive_mode':{'const':'archive_only'}}},
    'then': {'required':['review','transcript_format'], 'properties':{'topic_map_file':{'type':'null'},'topic_map_markdown_file':{'type':'null'}}},
    'else': {'properties':{'topic_map_file':{'const':'TOPIC_MAP.yaml'},'topic_map_markdown_file':{'const':'TOPIC_MAP.md'}}},
}]
SCHEMAS['messages']['properties']['messages']['items']['properties']['archive_identity_key'] = TEXT
SCHEMAS['export']['properties']['publication'] = obj({
    'status': enum('eligible_not_verified_remote', 'local_only'),
    'blockers': arr(TEXT),
    'retained_local_path': NULL,
})
SCHEMAS['export']['properties']['publication']['allOf']=[{
    'if':{'properties':{'status':{'const':'local_only'}}},
    'then':{'properties':{'blockers':{'minItems':1},'retained_local_path':TEXT}},
}]
SCHEMAS['messages']['properties']['messages']['items']['properties']['native_parent_message_id'] = NULL
SCHEMAS['manifest']['properties']['native_lineage'] = obj({'forked_from_id':NULL,'parent_thread_id':NULL})
