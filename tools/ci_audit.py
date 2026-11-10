"""Finding-only CI runner. Private source content never enters logs or artifacts."""
import datetime as dt,hashlib,json,os,pathlib,subprocess,sys,urllib.request
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from memory.audits import audit,missing_audit_executions
from memory.staging import snapshot
root=pathlib.Path('.').resolve();scope=sys.argv[1];before=snapshot(root);status=subprocess.run(['git','status','--porcelain'],capture_output=True,text=True,check=True).stdout
report=audit(root,scope)
if scope=='weekly':
    token=os.environ.get('GH_TOKEN');repository=os.environ.get('GITHUB_REPOSITORY')
    if token and repository:
        request=urllib.request.Request(f'https://api.github.com/repos/{repository}/actions/runs?per_page=100',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'})
        try:
            with urllib.request.urlopen(request,timeout=20) as response: runs=json.load(response)['workflow_runs']
            for workflow in missing_audit_executions(runs):
                report['findings'].append(dict(code='missing_audit_execution',severity='WARNING',workflow=workflow))
            report['limitations'].append('Execution coverage examines at most the most recent 100 runs')
        except Exception: report['findings'].append(dict(code='audit_history_unavailable',severity='WARNING'))
    else: report['findings'].append(dict(code='audit_history_unavailable',severity='WARNING'))
if before!=snapshot(root) or status!=subprocess.run(['git','status','--porcelain'],capture_output=True,text=True,check=True).stdout: raise RuntimeError('Read-only audit changed repository')
# Only identifiers and codes are logged. Store no transcript data or public artifacts.
summary=dict(scope=scope,workflow_sha=report['workflow_sha'],run_id=report['run_id'],executed_at=report['executed_at'],findings=[{k:v for k,v in f.items() if k in ('code','severity','record_id','work_item_id','exception_id','obligation_id','workflow')} for f in report['findings']],limitations=report['limitations'])
text=json.dumps(summary,sort_keys=True,indent=2);print(text)
if os.environ.get('GITHUB_STEP_SUMMARY'):
 with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('```json\n'+text+'\n```\n')
sys.exit(1 if any(f.get('severity')=='ERROR' for f in report['findings']) else 0)
