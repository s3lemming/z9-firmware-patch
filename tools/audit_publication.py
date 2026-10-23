"""Fail-closed source-only publication inventory; never prints matched values."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def audit():
    declared=json.loads((ROOT/'public-files.json').read_text(encoding='utf-8'))
    allowed=set(declared['files'])|{'public-files.json'}
    actual=set();rows=[];errors=[]
    patterns={
        'private host path':r'(?i)(?:(?<![a-z])[C-Z]:[\\/]|/mnt/[c-z]/|/root/'+r'[^ /]+/|/home/[^ /]+/)',
        'credential marker':r'(?i)(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)',
    }
    for p in ROOT.rglob('*'):
        rel=p.relative_to(ROOT).as_posix()
        if rel=='.git'or rel.startswith('.git/'):continue
        if p.is_symlink():errors.append([rel,'symlink']);continue
        if p.is_dir():continue
        actual.add(rel)
        if rel not in allowed:errors.append([rel,'undeclared file']);continue
        data=p.read_bytes()
        if len(data)>100000 or b'\0'in data:errors.append([rel,'binary or oversized']);continue
        try:s=data.decode('utf-8')
        except UnicodeError:errors.append([rel,'not UTF-8']);continue
        if s.startswith('\ufeff'):errors.append([rel,'unexpected BOM'])
        for name,pattern in patterns.items():
            if re.search(pattern,s):errors.append([rel,name])
        rows.append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    for rel in sorted(allowed-actual):errors.append([rel,'missing file'])
    if(ROOT/'.git').exists():
        q=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True,check=True)
        for rel in q.stdout.decode().split('\0'):
            if rel and rel not in allowed:errors.append([rel,'tracked outside declaration'])
    result=dict(passed=not errors,files=sorted(rows,key=lambda r:r['path']),errors=errors)
    print(json.dumps(result,indent=2));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(audit())
