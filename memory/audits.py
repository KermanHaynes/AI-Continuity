"""Read-only operational findings and fidelity preparation; never semantic certification."""
import datetime as dt, os, subprocess
from zoneinfo import ZoneInfo
from .records import collect, load, temporal, now
from .validation import validate

def review_queue(root,at=None):
    at=at or dt.datetime.now(dt.timezone.utc);cutoff=at-dt.timedelta(days=35)
    entries=[];sources=[]
    for p,d,_ in collect(root):
        kind=d['record_type']
        if kind=='knowledge_subject':
            if dt.datetime.fromisoformat(d['updated_at'])>=cutoff: entries.append(dict(kind='recent_knowledge_review',record_id=d['subject_id'],updated_at=d['updated_at']))
            if any(c['classification'] in ('contradictory_evidence','unresolved_interpretation') for c in d['contributions']): entries.append(dict(kind='prior_interpretation_concern',record_id=d['subject_id']))
        if kind=='sot_conversation':
            if any(d['states'][op] not in ('complete','not_applicable') for op in ('knowledge_reconciliation','work_reconciliation')): entries.append(dict(kind='pending_integration',record_id=d['sot_id']))
            sources.append(dict(kind='older_source_sample',record_id=d['sot_id'],occurred_at=d['timestamps']['original_started_at']))
    entries.extend(sorted(sources,key=lambda e:(e['occurred_at'] is None,e['occurred_at'] or '',e['record_id']))[:5])
    for e in load(root/'INDEX/EXCEPTIONS.yaml')['exceptions']:
        if e['status']=='open': entries.append(dict(kind='open_exception',record_id=e['exception_id']))
    return sorted(entries,key=lambda e:(e['kind'],e.get('occurred_at') or '',e['record_id']))

def _audit(root,scope,at=None):
    at=at or dt.datetime.now(dt.timezone.utc)
    if at.tzinfo is None: raise ValueError('Audit instant requires UTC offset')
    findings=[]
    if scope=='weekly':
        findings=validate(root)
        findings.append(dict(severity='INFO',code='audit_history_unverified',message='Prior workflow execution history requires GitHub Actions run inspection; local files do not prove executions'))
    elif scope=='monthly': findings=review_queue(root,at)
    elif scope=='daily':
        for _,w,_ in collect(root):
            if w['record_type']!='work_item' or w['status'] in ('completed','closed'): continue
            for item in w['dates']+w['events']:
                if item['state'] not in ('active','scheduled') or item['at'] is None: continue
                value=temporal(item)
                if isinstance(value,dt.datetime):
                    delta=(value-at).total_seconds()/86400; due=value<=at
                    calendar_delta=(value.astimezone(ZoneInfo(item['time_zone'])).date()-at.astimezone(ZoneInfo(item['time_zone'])).date()).days
                else:
                    # Calendar dates are evaluated in their recorded zone; unknown zone is reported.
                    if not item['time_zone']:
                        findings.append(dict(work_item_id=w['work_item_id'],code='unknown_time_zone',obligation_id=item.get('date_id',item.get('event_id')))); continue
                    local=at.astimezone(ZoneInfo(item['time_zone'])).date(); delta=(value-local).days; calendar_delta=delta; due=value<=local
                kind=item.get('kind','event')
                code=None
                if kind=='external_deadline' and delta<0: code='overdue_external_deadline'
                elif kind=='external_deadline' and calendar_delta<=7: code='approaching_external_deadline'
                elif kind=='follow_up' and due: code='due_follow_up'
                elif kind=='follow_up' and calendar_delta<=7: code='approaching_follow_up'
                elif kind=='event' and delta<0: code='past_scheduled_event'
                elif kind=='event' and calendar_delta<=7: code='upcoming_event'
                if code: findings.append(dict(work_item_id=w['work_item_id'],code=code,obligation_id=item.get('date_id',item.get('event_id'))))
        for e in load(root/'INDEX/EXCEPTIONS.yaml')['exceptions']:
            if e['status']=='open': findings.append(dict(code='open_exception',exception_id=e['exception_id'],classification=e['classification']))
    else: raise ValueError('Unknown audit scope')
    sha=subprocess.run(['git','rev-parse','HEAD'],cwd=root,text=True,capture_output=True).stdout.strip() or None
    return dict(scope=scope,workflow_sha=os.environ.get('GITHUB_SHA',sha),run_id=os.environ.get('GITHUB_RUN_ID'),executed_at=at.isoformat(),findings=findings,limitations=['Scope: structural and operational findings. Review source interpretations and verify external status through their procedures.','Workflow-history coverage must be verified through GitHub Actions'])


def audit(root,scope,at=None):
    from .staging import snapshot
    before=snapshot(root)
    status=subprocess.run(['git','status','--porcelain'],cwd=root,capture_output=True,text=True).stdout
    result=_audit(root,scope,at)
    after_status=subprocess.run(['git','status','--porcelain'],cwd=root,capture_output=True,text=True).stdout
    if before!=snapshot(root) or status!=after_status: raise ValueError('Audit changed canonical worktree')
    result['read_only_verified']=True
    return result


def missing_audit_executions(runs,at=None):
    """Read-only deterministic evaluation of explicitly supplied workflow history."""
    at=at or dt.datetime.now(dt.timezone.utc)
    missing=[]
    for workflow,days in [('daily-watch.yml',2),('weekly-audit.yml',9),('monthly-review.yml',35)]:
        cutoff=at-dt.timedelta(days=days)
        eligible=[r for r in runs if r['path'].endswith(workflow) and r['status']=='completed' and r['conclusion']=='success' and dt.datetime.fromisoformat(r['created_at'].replace('Z','+00:00'))>=cutoff]
        if not eligible: missing.append(workflow)
    return missing
