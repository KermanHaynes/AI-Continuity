"""Run python -m memory.cli --help for the deterministic command contract."""
import argparse, json, pathlib, sys
from .records import *
from .operations import *
from .validation import validate
from .audits import audit,review_queue
from .transactions import closeout_record
from .staging import candidate

def parser():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--root',type=pathlib.Path,default=pathlib.Path('.')); s=p.add_subparsers(dest='command',required=True)
    for name in ('validate','new-id','render-agenda','review-queue','plan-repair','recover-publication','archive-reconcile-order','verify-archive-fidelity'): s.add_parser(name)
    q=s.add_parser('archive-batch'); q.add_argument('stage',choices=['sources','dialogue']); q.add_argument('corpus',type=pathlib.Path); q.add_argument('inventory',type=pathlib.Path)
    q=s.add_parser('archive-inventory'); q.add_argument('corpus',type=pathlib.Path); q.add_argument('destination',type=pathlib.Path)
    q=s.add_parser('apply-repair'); q.add_argument('--authorized',action='store_true',required=True)
    q=s.add_parser('register-export'); q.add_argument('source',type=pathlib.Path); q.add_argument('--provider',required=True); q.add_argument('--environment',required=True); q.add_argument('--scope',required=True); q.add_argument('--completeness',choices=['complete','partial','unknown'],default='unknown'); q.add_argument('--native-export-id'); q.add_argument('--previous-export-id',action='append',default=[])
    q=s.add_parser('set-attachment-inventory'); q.add_argument('sot_id'); q.add_argument('--expected',type=int); q.add_argument('--verification',choices=['verified','partial','unknown'],required=True); q.add_argument('--evidence',action='append',default=[])
    q=s.add_parser('register-artifact'); q.add_argument('sot_id'); q.add_argument('source',type=pathlib.Path); q.add_argument('--native-artifact-id'); q.add_argument('--message-id',action='append',default=[]); q.add_argument('--description'); q.add_argument('--artifact-id')
    q=s.add_parser('register-sot'); q.add_argument('export_id'); q.add_argument('mapping',type=pathlib.Path)
    q=s.add_parser('resolve-source'); q.add_argument('sot_id'); q.add_argument('--message-id')
    q=s.add_parser('create-subject'); q.add_argument('name'); q.add_argument('--slug',required=True); q.add_argument('--scope',required=True)
    q=s.add_parser('resolve-subject'); q.add_argument('query')
    q=s.add_parser('resolve-work'); q.add_argument('query')
    q=s.add_parser('associate-source'); q.add_argument('query'); q.add_argument('sot_id'); q.add_argument('message_ids',nargs='+'); q.add_argument('--classification',choices=EVIDENCE,required=True); q.add_argument('--description',required=True); q.add_argument('--occurred-at')
    q=s.add_parser('create-work'); q.add_argument('title'); q.add_argument('--type',required=True)
    q=s.add_parser('transition-work'); q.add_argument('work_item_id'); q.add_argument('status',choices=LIFECYCLE); q.add_argument('--reason',required=True); q.add_argument('--effective-at'); q.add_argument('--evidence',type=pathlib.Path,required=True,help='JSON array of exact source references')
    q=s.add_parser('set-processing'); q.add_argument('sot_id'); q.add_argument('operation',choices=OPERATIONS); q.add_argument('state',choices=STATES); q.add_argument('--reason')
    q=s.add_parser('raise-exception'); q.add_argument('classification'); q.add_argument('--affected-id',action='append',default=[]); q.add_argument('--evidence',action='append',required=True); q.add_argument('--last-verified-sha')
    q=s.add_parser('archive-receipt'); q.add_argument('transaction_id'); q.add_argument('--preservation',required=True); q.add_argument('--remote',required=True); q.add_argument('--branch',required=True); q.add_argument('--affected-id',action='append',default=[]); q.add_argument('--limitation',action='append',default=[])
    q=s.add_parser('closeout-record'); q.add_argument('transaction_id'); q.add_argument('--preservation',required=True); q.add_argument('--derived',required=True); q.add_argument('--remote',required=True); q.add_argument('--branch',required=True); q.add_argument('--affected-id',action='append',default=[]); q.add_argument('--limitation',action='append',default=[])
    q=s.add_parser('audit'); q.add_argument('scope',choices=['daily','weekly','monthly']); q.add_argument('--at')
    return p

def execute(a):
    root=a.root.resolve(); cmd=a.command
    if cmd=='verify-archive-fidelity':
        from .archive_fidelity import verify
        return verify(root)
    if cmd=='archive-reconcile-order':
        from .archive import reconcile_archive_order
        return reconcile_archive_order(root)
    if cmd=='archive-batch':
        from .archive_batch import run
        return run(root,a.corpus,a.inventory,a.stage)
    if cmd=='archive-inventory':
        from .archive_inventory import inventory
        return inventory(a.corpus,a.destination)
    if cmd=='new-id': return {'id':new_id()}
    if cmd=='validate': return validate(root)
    if cmd=='review-queue': return review_queue(root)
    if cmd=='audit': return audit(root,a.scope,dt.datetime.fromisoformat(a.at) if a.at else None)
    if cmd=='plan-repair':
        return {'mechanical_corrections':['Regenerate INDEX/REGISTRY.yaml, INDEX/ALIASES.yaml and WORK/AGENDA.md'],'findings':validate(root),'semantic_repairs':[]}
    if cmd=='resolve-work':
        p,d,body=resolve_work(root,a.query)
        return {'path':str(p.relative_to(root)),'work':d,'narrative':body,'agenda':(root/'WORK/AGENDA.md').read_text()}
    if cmd=='resolve-subject':
        p,d=resolve_subject(root,a.query)
        work=[w for _,w,_ in collect(root) if w['record_type']=='work_item' and d['subject_id'] in w['subject_ids']]
        return {'path':str(p.relative_to(root)),'subject':d,'current':(p.parent/'CURRENT.md').read_text(),'associated_work':work,'agenda':(root/'WORK/AGENDA.md').read_text(),'history_path':str((p.parent/'EVOLUTION.md').relative_to(root)),'sources_path':str((p.parent/'SOURCES.md').relative_to(root))}
    if cmd=='resolve-source':
        found=[(p,d) for p,d,_ in collect(root) if d['record_type']=='sot_conversation' and d['sot_id']==a.sot_id]
        if len(found)!=1: raise ValueError('Source missing or ambiguous')
        p,d=found[0]
        if a.message_id:
            if a.message_id not in {m['message_id'] for m in load(p.parent/'MESSAGES.yaml')['messages']}: raise ValueError('Message missing')
        return {'manifest':d,'transcript':str((p.parent/'transcript.md').relative_to(root))+('#msg-'+a.message_id if a.message_id else '')}
    if cmd=='recover-publication':
        from .staging import recover_publication
        with lock(root): return recover_publication(root)
    with lock(root), candidate(root) as root:
        if cmd in ('render-agenda','apply-repair'): rebuild(root); return {'updated':['INDEX/REGISTRY.yaml','INDEX/ALIASES.yaml','WORK/AGENDA.md']}
        if cmd=='register-export': return register_export(root,a.source,a.provider,a.environment,a.scope,a.completeness,a.native_export_id,a.previous_export_id)
        if cmd=='set-attachment-inventory': return set_attachment_inventory(root,a.sot_id,a.expected,a.verification,a.evidence)
        if cmd=='register-artifact': return register_artifact(root,a.sot_id,a.source,a.native_artifact_id,a.message_id,a.description,a.artifact_id)
        if cmd=='register-sot': return register_sot(root,a.export_id,json.loads(a.mapping.read_text()))
        if cmd=='create-subject': return create_subject(root,a.name,a.slug,a.scope)
        if cmd=='associate-source': return associate_source(root,a.query,dict(sot_id=a.sot_id,message_ids=a.message_ids),a.classification,a.description,a.occurred_at)
        if cmd=='create-work': return create_work(root,a.title,a.type)
        if cmd=='transition-work': return transition_work(root,a.work_item_id,a.status,a.reason,a.effective_at,json.loads(a.evidence.read_text()) if a.evidence else [])
        if cmd=='set-processing': return set_processing(root,a.sot_id,a.operation,a.state,a.reason)
        if cmd=='raise-exception': return raise_exception(root,a.classification,a.affected_id,a.evidence,a.last_verified_sha)
        if cmd=='archive-receipt':
            from .transactions import archive_receipt
            return archive_receipt(root,a.transaction_id,a.preservation,a.remote,a.branch,a.affected_id,a.limitation)
        if cmd=='closeout-record': return closeout_record(root,a.transaction_id,a.preservation,a.derived,a.remote,a.branch,a.affected_id,a.limitation)
    raise ValueError('Unsupported command')

def main(argv=None):
    a=parser().parse_args(argv)
    try:
        result=execute(a)
        if a.command in ('register-export','register-sot','register-artifact','set-attachment-inventory','create-subject','associate-source','create-work','transition-work','set-processing','raise-exception','closeout-record','render-agenda','apply-repair'):
            output={'result':result,'validation_scope':'incremental'}
        else: output=result
        print(json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2))
        if a.command=='verify-archive-fidelity': return 1 if result['failures'] else 0
        if a.command=='validate': return 1 if any(f['severity']=='ERROR' for f in result) else 0
        if a.command=='audit' and a.scope=='weekly': return 1 if any(f.get('severity')=='ERROR' for f in result['findings']) else 0
        return 0
    except (ValueError,KeyError,OSError) as e: print(json.dumps({'error':str(e)}),file=sys.stderr); return 2
if __name__=='__main__': sys.exit(main())
