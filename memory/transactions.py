"""Git checkpoints, remote ancestry, and subsequent closeout attestations."""
import subprocess, re
from .records import now,new_id,write,collect,rebuild

def git(root,*args):
    p=subprocess.run(['git',*args],cwd=root,text=True,capture_output=True)
    if p.returncode: raise ValueError('Git operation failed: '+ ' '.join(args[:2]))
    return p.stdout.strip()
def ancestor(root,older,newer):
    return subprocess.run(['git','merge-base','--is-ancestor',older,newer],cwd=root,capture_output=True).returncode==0

def verify_remote(root,remote,branch,commits):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',remote) or branch.startswith('-'): raise ValueError('Unsafe remote or branch')
    git(root,'check-ref-format','refs/heads/'+branch)
    git(root,'fetch','--no-tags',remote,'refs/heads/'+branch)
    observed=git(root,'rev-parse','FETCH_HEAD')
    for sha in commits:
        if not re.fullmatch('[0-9a-f]{40}',sha): raise ValueError('Full commit SHA required')
        git(root,'cat-file','-e',sha+'^{commit}')
        if not ancestor(root,sha,observed): raise ValueError('Commit is not remotely reachable')
    return observed

def verify_checkpoint_commits(root,preservation,derived,affected):
    import yaml
    paths=git(root,'diff-tree','--no-commit-id','--name-only','-r','--root',preservation).splitlines()
    if any(p.startswith(('KNOWLEDGE/','WORK/ITEMS/','CONTEXT/')) for p in paths): raise ValueError('Preservation commit must be separate from knowledge/work reconciliation')
    if not any(p.startswith('SOT/EXPORTS/') and '/original.' in p for p in paths): raise ValueError('Preservation commit contains no original export evidence')
    changed=git(root,'diff','--name-only',preservation,derived).splitlines();material=set()
    if any(p.startswith('SOT/EXPORTS/') and '/original.' in p for p in changed): raise ValueError('Derived reconciliation must not introduce or modify original source bytes')
    for p in changed:
        if p.startswith('KNOWLEDGE/') and p.endswith('/subject.yaml'):
            material.add(yaml.safe_load(git(root,'show',derived+':'+p))['subject_id'])
        if p.startswith('WORK/ITEMS/work_') and p.endswith('.md'):
            front=git(root,'show',derived+':'+p).split('---',2)[1];material.add(yaml.safe_load(front)['work_item_id'])
    if not material<=set(affected): raise ValueError('Receipt omits materially changed subject/work IDs')

def closeout_record(root,transaction_id,preservation,derived,remote,branch,affected,limitations):
    if preservation==derived or not ancestor(root,preservation,derived): raise ValueError('Separate ordered preservation and derived commits required')
    verify_checkpoint_commits(root,preservation,derived,affected)
    states=[d for _,d,_ in collect(root) if d['record_type']=='processing_state' and d['transaction_id']==transaction_id]
    if len(states)!=1 or states[0]['state']!='verified_complete': raise ValueError('A verified-complete processing checkpoint is required')
    state=states[0]
    if state['preservation_commit']!=preservation or state['derived_commit']!=derived or set(affected)!=set(state['affected_record_ids']): raise ValueError('Checkpoint and receipt disagree')
    from .validation import validate_incremental
    affected_paths={p.relative_to(root).as_posix() for p,d,_ in collect(root) if any(d.get(key) in affected for key in ('sot_id','subject_id','work_item_id')) or d.get('transaction_id')==transaction_id}
    errors=[f for f in validate_incremental(root,affected_paths) if f['severity']=='ERROR']
    if errors: raise ValueError('Validation failed before receipt')
    observed=verify_remote(root,remote,branch,[preservation,derived])
    d=dict(record_type='closeout',schema_version=1,closeout_id=new_id(),transaction_id=transaction_id,preservation_commit=preservation,derived_commit=derived,remote=remote,branch=branch,observed_sha=observed,verified_at=now(),verification_mechanism='git-fetch-and-merge-base',affected_record_ids=affected,validation_results=['Deterministic structural validation passed; semantic fidelity requires review'],limitations=limitations)
    write(root/f"INDEX/CLOSEOUTS/{d['closeout_id']}.yaml",d); rebuild(root); return d

def verify_receipt(root,d,fetch=True):
    if d.get('operation_mode') == 'archive_only':
        states=[x for _,x,_ in collect(root) if x['record_type']=='processing_state' and x['transaction_id']==d['transaction_id']]
        if len(states)!=1: raise ValueError('Archive checkpoint missing')
        state=states[0]
        if state['state']!='archive_verified' or state['derived_commit'] is not None or d['derived_commit'] is not None or state['preservation_commit']!=d['preservation_commit'] or set(state['affected_record_ids'])!=set(d['affected_record_ids']): raise ValueError('Archive receipt and checkpoint disagree')
        _verify_archive_checkpoint(root,d['preservation_commit'],state['starting_sha'])
        if not re.fullmatch('[a-f0-9]{40}',d['observed_sha']) or not ancestor(root,d['preservation_commit'],d['observed_sha']): raise ValueError('Archive observed ancestry invalid')
        if fetch: verify_remote(root,d['remote'],d['branch'],[d['preservation_commit'],d['observed_sha']])
        elif not ancestor(root,d['observed_sha'],'HEAD'): raise ValueError('Archive observation is absent from local history')
        return True
    for key in ('preservation_commit','derived_commit','observed_sha'):
        if not re.fullmatch('[a-f0-9]{40}',d[key]): raise ValueError('Invalid full commit SHA')
        git(root,'cat-file','-e',d[key]+'^{commit}')
    if d['preservation_commit']==d['derived_commit'] or not ancestor(root,d['preservation_commit'],d['derived_commit']) or not ancestor(root,d['derived_commit'],d['observed_sha']): raise ValueError('Receipt commit ancestry invalid')
    verify_checkpoint_commits(root,d['preservation_commit'],d['derived_commit'],d['affected_record_ids'])
    states=[x for _,x,_ in collect(root) if x['record_type']=='processing_state' and x['transaction_id']==d['transaction_id']]
    if len(states)!=1 or states[0]['state']!='verified_complete': raise ValueError('Receipt processing checkpoint missing or incomplete')
    state=states[0]
    if set(state['affected_record_ids'])!=set(d['affected_record_ids']): raise ValueError('Receipt affected identities differ from checkpoint')
    if state['preservation_commit']!=d['preservation_commit'] or state['derived_commit']!=d['derived_commit']: raise ValueError('Receipt does not match checkpoint')
    if fetch: verify_remote(root,d['remote'],d['branch'],[d['preservation_commit'],d['derived_commit'],d['observed_sha']])
    elif not ancestor(root,d['observed_sha'],'HEAD'): raise ValueError('Historical observed commit is not in local ancestry')
    return True

def concurrency(root,starting_sha,remote,branch):
    """Return an explicit integration plan; never overwrite concurrent records."""
    observed=verify_remote(root,remote,branch,[])
    if observed==starting_sha: return dict(state='unchanged',observed_sha=observed,overlap=[])
    local=set(git(root,'diff','--name-only',starting_sha,'HEAD').splitlines())
    upstream=set(git(root,'diff','--name-only',starting_sha,observed).splitlines())
    overlap=sorted(local&upstream)
    return dict(state='semantic_review_required' if overlap else 'merge_unrelated',observed_sha=observed,overlap=overlap)

def archive_receipt(root, transaction_id, preservation, remote, branch, affected, limitations):
    """Attest archive preservation independently of intellectual reconciliation."""
    from .validation import validate
    states=[d for _,d,_ in collect(root) if d['record_type']=='processing_state' and d['transaction_id']==transaction_id]
    if len(states)!=1: raise ValueError('Archive processing checkpoint required')
    state=states[0]
    if state['state']!='archive_verified' or state['preservation_commit']!=preservation or state['derived_commit'] is not None or set(state['affected_record_ids'])!=set(affected):
        raise ValueError('Archive checkpoint must agree with the evidence commit and affected identities')
    _verify_archive_checkpoint(root,preservation,state['starting_sha'])
    if any(f['severity']=='ERROR' for f in validate(root)): raise ValueError('Archive structural validation failed')
    observed=verify_remote(root,remote,branch,[preservation])
    data=dict(record_type='closeout',schema_version=1,operation_mode='archive_only',closeout_id=new_id(),transaction_id=transaction_id,preservation_commit=preservation,derived_commit=None,remote=remote,branch=branch,observed_sha=observed,verified_at=now(),verification_mechanism='git-fetch-and-merge-base',affected_record_ids=affected,validation_results=['Archive structure and remote ancestry verified; intellectual review remains pending'],limitations=limitations)
    write(root/f"INDEX/CLOSEOUTS/{data['closeout_id']}.yaml",data)
    from .archive import rebuild_navigation
    rebuild_navigation(root)
    return data


def _verify_archive_checkpoint(root, preservation, starting):
    if not re.fullmatch('[a-f0-9]{40}',preservation) or not ancestor(root,starting,preservation): raise ValueError('Archive checkpoint ancestry invalid')
    paths=git(root,'diff','--name-only',starting,preservation).splitlines()
    if any(p.startswith(('KNOWLEDGE/','WORK/','CONTEXT/')) for p in paths): raise ValueError('Archive transaction changes downstream content')
    if not any(p.startswith('SOT/') for p in paths): raise ValueError('Archive transaction contains no SOT evidence')
