#!/usr/bin/env python3
"""Local-only build/pack/verify CLI. No camera, upload or update operations."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    build=commands.add_parser('build',help='Compile and patch an exact original MAIN module')
    build.add_argument('--module',type=Path,required=True)
    build.add_argument('--output',type=Path,required=True,help='New private build directory; contains derived firmware')
    for name in ('pack','verify'):
        p=commands.add_parser(name,help='Local container operation; requires separately supplied private format material')
        p.add_argument('--stock',type=Path,required=True)
        p.add_argument('--tables',type=Path,required=True)
        p.add_argument('--integrity-material',type=Path,required=True)
        if name=='pack':
            p.add_argument('--payload',type=Path,required=True)
            p.add_argument('--output',type=Path,required=True)
        else:p.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args()
    try:
        if not __debug__:raise ValueError('Use normal Python; -O disables internal checks')
        if args.command=='build':
            from z9patch.builder import build
            result=build(args.module,args.output)
            result={k:v for k,v in result.items()if k!='patches'}
        else:
            from z9patch.packaging import operate
            result=operate(args)
        print(json.dumps(result,indent=2))
        return 0
    except (ValueError,OSError,AssertionError,KeyError,TypeError,ImportError) as exc:
        # Never echo key material or input contents on validation failures.
        print('Operation rejected: '+str(exc),file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
