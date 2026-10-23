"""Host-only tests. Fixtures are generated; no camera or firmware is required."""
import argparse,json,subprocess,sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if not __debug__:p.error('Run without Python -O')
    if a.output.exists() or a.output.is_symlink():p.error('Output directory must be new')
    if a.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):p.error('Keep test output outside the repository')
    a.output.mkdir(parents=True);rows=[]
    for name in ('core','native_profile','formats','tooling'):
        q=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name(name+'.py')),str(a.output/name)],capture_output=True,text=True)
        row=dict(test=name,exit=q.returncode,stdout=q.stdout,stderr=q.stderr);rows.append(row)
        (a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
        print(q.stdout,end='',flush=True)
        if q.returncode:print(q.stderr,file=sys.stderr);return 1
    print('All host suites passed; no device qualification implied.');return 0
if __name__=='__main__':raise SystemExit(main())
