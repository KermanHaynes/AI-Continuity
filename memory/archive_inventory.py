"""Bounded, restartable source inventory. Does not alter originals or publish data."""
import collections
import hashlib
import json
import pathlib
import re
import subprocess
import zipfile
from .records import atomic, now

# Findings identify a rule only. Never write candidate credential values to logs.
RULES = {
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'github_token': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'provider_key': rb'sk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}',
    'aws_access_key': rb'AKIA[A-Z0-9]{16}',
    'credential_assignment': rb'(?i)(?:password|api[_-]?key|secret[_-]?key|access[_-]?token)\s*["\x27]?\s*[:=]\s*["\x27][^"\x27\r\n]{12,}',
}
COMPILED = {k:re.compile(v) for k,v in RULES.items()}


def scan_stream(stream):
    found=set(); tail=b''
    while True:
        block=stream.read(1024*1024)
        if not block: break
        data=tail+block
        views=(data,data.replace(bytes((92,34)),bytes((34,))))
        found.update(name for name,rule in COMPILED.items() if any(rule.search(view) for view in views))
        tail=data[-4096:]
    return found


def source_findings(path):
    if path.name.endswith('.zst'):
        with subprocess.Popen(['zstd','-q','-dc','--',str(path)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL) as process:
            found=scan_stream(process.stdout)
            if process.wait()!=0: raise ValueError('Compressed source could not be decoded')
        return sorted(found)
    if zipfile.is_zipfile(path):
        found=set()
        with zipfile.ZipFile(path) as package:
            for member in package.infolist():
                if not member.is_dir():
                    with package.open(member) as stream: found.update(scan_stream(stream))
        return sorted(found)
    with path.open('rb') as stream: return sorted(scan_stream(stream))


def inventory(corpus, destination):
    corpus=pathlib.Path(corpus).resolve(); destination=pathlib.Path(destination).resolve()
    originals=(corpus/'ORIGINALS').resolve()
    catalog=json.loads((corpus/'METADATA/sources.json').read_bytes())
    groups=collections.defaultdict(list)
    for source in catalog: groups[source['sha256']].append(source)
    destination.mkdir(parents=True,exist_ok=True)
    statefile=destination/'sources.json'
    previous=json.loads(statefile.read_bytes()) if statefile.exists() else {'sources':[]}
    previous={s['sha256']:s for s in previous['sources']}
    results=[]
    for sha, observations in sorted(groups.items()):
        source=observations[0];path=(corpus/source['path'])
        result={'sha256':sha,'bytes':source['bytes'],'provider':source['provider'], 'kind':source['kind'], 'source_format':source.get('source_format'), 'source_ids':[s['id'] for s in observations], 'paths':[s['path'] for s in observations], 'publication':'not_attempted'}
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(originals): raise ValueError('Source path escapes ORIGINALS or is a symlink')
            # Recheck bytes each invocation; cached scan is tied to this verified hash.
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                while block:=stream.read(1024*1024):digest.update(block)
            if digest.hexdigest()!=sha or path.stat().st_size!=source['bytes']:raise ValueError('Source checksum or size differs from preserved catalog')
            result['checksum_verified']=True
            old=previous.get(sha,{})
            if old.get('checksum_verified') and old.get('scan_policy')==1:
                result['credential_rules']=old['credential_rules']
            elif source['kind'] in ('native_stream','native_package','potential_export','session_metadata','export_manifest'):
                result['credential_rules']=source_findings(path)
            else: result['credential_rules']=[]
            result['scan_policy']=1
            blockers=[]
            if source['bytes']>=100*1024*1024: blockers.append('Exceeds ordinary GitHub file limit; Git LFS availability and storage capacity unverified')
            if result['credential_rules']:blockers.append('Potential credentials in immutable source; requires source-specific publication decision without altering original bytes')
            if source['kind']=='supporting_artifact':blockers.append('Ancillary artifact retained locally; conversation association and publication eligibility not established')
            result['blockers']=blockers
            result['eligibility']='blocked' if blockers else 'eligible_pending_native_interpretation'
        except (OSError,ValueError,zipfile.BadZipFile) as error:
            result['eligibility']='blocked';result['blockers']=[str(error)]
        result['checked_at']=now();results.append(result)
        if len(results)%25==0:
            atomic(statefile,json.dumps({'complete':False,'sources':results},ensure_ascii=True,indent=2)+'\n')
    report={'complete':True,'checked_at':now(),'physical_records':len(catalog),'unique_hashes':len(groups),'unique_bytes':sum(s['bytes'] for s in results),'kinds':dict(collections.Counter(s['kind'] for s in results)),'eligibility':dict(collections.Counter(s['eligibility'] for s in results)),'sources':results}
    atomic(statefile,json.dumps(report,ensure_ascii=True,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='sources'}
