"""Compile unchanged actual C with explicit native-address ABI substitutions."""
import hashlib,json,subprocess,time,sys
from pathlib import Path
import sys
R=Path(__file__).resolve().parent;S=R.parent/'firmware';E=Path(sys.argv[1]);E.mkdir();commands=[]
def run(args):
 t=time.monotonic();p=subprocess.run(args,capture_output=True,text=True);commands.append(dict(argv=args,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,wall_seconds=time.monotonic()-t));(E/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');assert not p.returncode,p.stdout+p.stderr;return p.stdout
header='#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nstatic void *resolve(unsigned long);\n'
s=(S/'picker.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define K ((struct picker *)(uintptr_t)0xa04e3d600ULL)','#define K (&fake)').replace('#define HOLDER ((uint8_t *)(uintptr_t)0xa028d29b0ULL)','#define HOLDER (fixture_holder)').replace('_Static_assert(sizeof(struct picker)','static struct picker fake;static _Alignas(8) uint8_t fixture_holder[48],fixture_builtin[220];\n_Static_assert(sizeof(struct picker)').replace('(const uint8_t *)(uintptr_t)0x431897a4','(const uint8_t *)fixture_builtin')
p=E/'picker_test.c';p.write_text(header+s+(R/'picker_body.c').read_text().replace('int main(void)','int baseline_main(void)')+(R/'picker_stress_body.c').read_text())
base=['gcc','-O1','-g','-I',str(S),'-Wall','-Wextra','-Werror','-fsanitize=undefined,address','-fno-sanitize-recover=all']
run([*base,str(p),str(S/'profile.c'),str(S/'mark2_import.c'),'-o',str(E/'picker_test')]);picker=run([str(E/'picker_test')]);print(picker,flush=True)
s=(S/'adapter.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define P ((struct state *)(uintptr_t)0xa04e3d000ULL)','#define P (&fake)').replace('#define NATIVE_U8(a) (*(volatile uint8_t *)(uintptr_t)(a))','#define NATIVE_U8(a) (native8)').replace('#define NATIVE_U32(a) (*(volatile uint32_t *)(uintptr_t)(a))','#define NATIVE_U32(a) (native32)').replace('void m2_composite(void);','static struct state fake;static uint8_t native8;static uint32_t native32;\nvoid m2_composite(void);')
p=E/'adapter_test.c';p.write_text(header+s+(R/'adapter_body.c').read_text());run([*base,str(p),'-o',str(E/'adapter_test')]);adapter=run([str(E/'adapter_test')]);print(adapter,flush=True)
report=dict(passed=True,scope='Unchanged v11 actual C with native ABI mocks; no native guest soak claim',picker=picker,adapter=adapter,compiler=run(['gcc','--version']),sanitizers=['ASan','UBSan'],source_SHA256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in S.iterdir()if p.is_file()},commands_SHA256=hashlib.sha256((E/'commands.json').read_bytes()).hexdigest(),long_term_qualification=False,resource_limit='4 import attempts and64 never-reused callback slots; 65th rejected without audio completion or fallback')
(E/'result.json').open('x').write(json.dumps(report,indent=2)+'\n')
