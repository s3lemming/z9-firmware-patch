import hashlib,json,subprocess
from pathlib import Path
import sys
R=Path(__file__).resolve().parent;S=R.parent/'firmware';E=Path(sys.argv[1]);E.mkdir();commands=[]
s=(S/'profile_native.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))');p=E/'test.c';body=R/'profile_native_body.c';p.write_text('#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <stdint.h>\nstatic void *resolve(uintptr_t);\n'+s+body.read_text());cmd=['gcc','-O1','-g','-I',str(S),'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),str(S/'profile.c'),'-o',str(E/'test')];commands=[]
for a in [cmd,[str(E/'test')]]:
 q=subprocess.run(a,capture_output=True,text=True);commands.append(dict(argv=a,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert not q.returncode,q.stdout+q.stderr
out=dict(passed=True,cases=329,stdout=q.stdout,scope='Actual profile_native.c/profile.c, original file ABI mocks with partial writes/reads and card IO faults; no real card pull/power cut',source_SHA256={n:hashlib.sha256((S/n).read_bytes()).hexdigest()for n in ['profile_native.c','profile.c']},test_SHA256=hashlib.sha256(body.read_bytes()).hexdigest(),ASan_UBSan=True);(E/'result.json').open('x').write(json.dumps(out,indent=2)+'\n');print(q.stdout)
