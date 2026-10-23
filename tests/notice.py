import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'firmware';T=R;E=Path(sys.argv[1]);E.mkdir(exist_ok=False)
header='#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nstatic void *resolve(unsigned long);\n'
s=(S/'adapter.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define P ((struct state *)(uintptr_t)0xa04e3d000ULL)','#define P (&fake)').replace('#define NATIVE_U8(a) (*(volatile uint8_t *)(uintptr_t)(a))','#define NATIVE_U8(a) (native8)').replace('#define NATIVE_U32(a) (*(volatile uint32_t *)(uintptr_t)(a))','#define NATIVE_U32(a) (*native_word(a))').replace('void m2_composite(void);','static struct state fake;static uint8_t native8;static uint32_t native32,pending[3];\nstatic uint32_t *native_word(uintptr_t a){if(a==0xa03ad9534ULL)return pending;if(a==0xa03ad9538ULL)return pending+1;if(a==0xa03ad9574ULL)return pending+2;return &native32;}\nvoid m2_composite(void);')
body=(T/'adapter_body.c').read_text()
extra=r'''
static void start(uint64_t *a){memset(a,0,13*sizeof *a);a[3]=0x40fa0320;a[8]=0x40e35768;assert(!m2_api(a));fake.notice=notify;uint64_t b[3]={0,9600,1};m2_pcm(b);assert(b[1]==144000&&b[2]==2);a[9]=1;m2_api_result(a);}
int main(void){static uint8_t pcm[288000];uint32_t data[2]={0,0};uint64_t a[13];assert(!m2_bind_file(pcm,sizeof pcm,0));
 for(unsigned n=0;n<1000;n++){
  start(a);unsigned slot=fake.current-1;m2_notice_slot(slot,0x4212004,data);m2_notice_slot(slot,0x4212005,data);assert(fake.slots[slot].completed==1&&!fake.active);
  for(unsigned k=0;k<3;k++){pending[k]=1;m2_notice_retired();assert(fake.slots[slot].completed==1);pending[k]=0;}
  m2_notice_slot(slot,0x4212005,data);assert(fake.slots[slot].completed==1);m2_notice_retired();assert(fake.slots[slot].completed==2);
 }
 assert(fake.inputs==1000&&fake.completes==1000&&fake.used==64&&fake.reserved==936&&!fake.rejects);puts("1000_REQUESTS_WITHOUT_RESET_REGISTER_RETIREMENT_PASS");
 memset(&fake,0,sizeof fake);assert(!m2_bind_file(pcm,sizeof pcm,0));for(unsigned n=0;n<64;n++){start(a);m2_notice_slot(n,0x4212005,data);}memset(a,0,sizeof a);a[3]=0x40fa0320;a[8]=0x40e35768;assert(m2_api(a)==1&&fake.used==64);puts("COMPLETION_ALONE_DOES_NOT_PERMIT_REUSE_PASS");
 m2_notice_retired();start(a);assert(fake.current==1&&fake.active);uint64_t older[13];memcpy(older,a,sizeof a);older[10]--;older[9]=0;m2_api_result(older);assert(fake.active);puts("STALE_API_RETURN_DOES_NOT_CLEAR_NEW_OWNER_PASS");
 printf("NOTICE_RETIREMENT_TEST_PASS state_bytes=%zu native_terminal_hook_required=1 PCM_freed=0\n",sizeof fake);return 0;}
'''
p=E/'adapter_notice.c';p.write_text(header+s+body+extra);rows=[]
for argv in [['gcc','-O1','-g','-I',str(S),'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),'-o',str(E/'adapter_notice')],[str(E/'adapter_notice')]]:
 q=subprocess.run(argv,capture_output=True,text=True);rows.append(dict(argv=argv,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=rows,source_SHA256=hashlib.sha256((S/'adapter.c').read_bytes()).hexdigest(),native_terminal_flow_verified=False),indent=2)+'\n');print(q.stdout+q.stderr,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
