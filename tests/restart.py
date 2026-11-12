"""Actual predicate ownership matrix: no state mutation or native side effect."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];E=Path(sys.argv[1]);E.mkdir()
s=(R/'firmware/adapter.c').read_text().replace('#define P ((struct state *)(uintptr_t)0xa04e3d000ULL)','#define P (&fake)').replace('void m2_composite(void);','static struct state fake;\nvoid m2_composite(void);')
body=r'''
int main(void){unsigned cases=0;struct state before;
 for(unsigned selected=0;selected<2;selected++)
 for(unsigned enabled=0;enabled<3;enabled++)
 for(unsigned pending=0;pending<2;pending++)
 for(unsigned tail=0;tail<2;tail++)
 for(unsigned active=0;active<2;active++)
 for(unsigned armed=0;armed<2;armed++)
 for(unsigned route=0;route<3;route++)
 for(unsigned old_kind=0;old_kind<2;old_kind++){
  memset(&fake,0x5a,sizeof fake);fake.selected=selected;
  fake.cxx_enabled=enabled;fake.cxx_tail_pending=pending;fake.cxx_tail_active=tail;
  fake.active=active;fake.armed=armed;fake.route=route;fake.kind=old_kind?6:0;
  memcpy(&before,&fake,sizeof fake);
  assert(m2_ordinary_restart_required()==(selected&&!enabled&&!pending&&!tail));
  assert(!memcmp(&before,&fake,sizeof fake));cases++;
 }
 printf("ORDINARY_RESTART_PASS cases=%u state_unchanged=checked native_calls=none\n",cases);
 return 0;
}
'''
p=E/'test.c';p.write_text('#include <assert.h>\n#include <stdio.h>\n#include <string.h>\n'+s+body)
rows=[]
for cmd in [['gcc','-O1','-g','-Wall','-Wextra','-Werror','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),'-o',str(E/'test')],[str(E/'test')]]:
 q=subprocess.run(cmd,capture_output=True,text=True);rows.append(dict(argv=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=rows,adapter_SHA256=hashlib.sha256((R/'firmware/adapter.c').read_bytes()).hexdigest(),scope='Actual ownership predicate, original kind0 admission is upstream; no AArch64 hook execution, device, frame-rate or timing-window qualification'),indent=2)+'\n');print(q.stdout+q.stderr,end='',flush=True)
 if q.returncode:raise SystemExit(q.returncode)
