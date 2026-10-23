import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'firmware';T=R;E=Path(sys.argv[1]);E.mkdir(exist_ok=False)
s=(S/'adapter.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define P ((struct state *)(uintptr_t)0xa04e3d000ULL)','#define P (&fake)').replace('#define NATIVE_U8(a) (*(volatile uint8_t *)(uintptr_t)(a))','#define NATIVE_U8(a) (native8)').replace('#define NATIVE_U32(a) (*(volatile uint32_t *)(uintptr_t)(a))','#define NATIVE_U32(a) (*native_word(a))').replace('void m2_composite(void);','static struct state fake;static uint8_t native8;static uint32_t native32,pending[3];\nstatic uint32_t *native_word(uintptr_t a){if(a==0xa03ad9534ULL)return pending;if(a==0xa03ad9538ULL)return pending+1;if(a==0xa03ad9574ULL)return pending+2;return &native32;}\nvoid m2_composite(void);')
head='#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nstatic void *resolve(unsigned long);\n'
body=r'''
static unsigned queued;
static void notify(uint32_t code,const void *v){(void)v;if(code==0x4212005){native8=0;native32=0;}}
const notice_fn callback_slots[SLOTS]={[0 ... SLOTS-1]=notify};
void m2_restore_for_audio(void){}
static void stop(void){}
static void timestamp(uint64_t *v){*v=123;}
static void request(const void *v){assert(v);queued++;}
static uint32_t post(uintptr_t a,uint32_t b){(void)a;(void)b;return 0;}
static void *resolve(uintptr_t a){switch(a){case 0x40fa0228:return(void*)stop;case 0x40c002a0:return(void*)post;case 0x40c7d438:return(void*)timestamp;case 0x40f9fe58:return(void*)request;default:abort();}}
static void end(void){uint32_t v[2]={fake.kind,0};unsigned slot=fake.current-1;m2_notice_slot(slot,0x4212004,v);m2_notice_slot(slot,0x4212005,v);m2_notice_retired();assert(fake.slots[slot].completed==2);}
int main(void){static uint8_t pcm[288000];unsigned cases=0;
 for(unsigned size=192;size<=288000;size+=192)for(unsigned c15=0;c15<2;c15++){
  memset(&fake,0,sizeof fake);queued=0;native8=native32=0;assert(!m2_bind_file(pcm,size,0));m2_composite();native8=native32=1;
  uint64_t a[13]={0};a[0]=c15?0:6;a[2]=c15?66:0;a[3]=0x40fa0320;a[8]=c15?0x40e357d4:0x40e35768;assert(!m2_api(a));assert(a[1]==0&&a[2]==0);fake.notice=notify;a[9]=1;m2_api_result(a);
  unsigned prefix=size<9600?size:9600;
  for(unsigned n=0;n<5;n++){uint64_t b[3]={0,c15?9600:7680,1};m2_pcm(b);assert(b[0]==(uintptr_t)pcm&&b[1]==prefix&&b[2]==1);}
  uint64_t frame[13]={0};m2_frame_snapshot(frame);m2_frame_commit(frame);assert(!queued&&fake.active&&fake.cxx_enabled);
  assert(m2_bind_file(pcm,192,0));m2_cxx_stop();m2_cxx_stop();assert(fake.cxx_stops==1);native32=2;end();
  if(size>9600){assert(queued==1&&fake.cxx_tail_pending&&fake.cxx_enabled);assert(m2_native_selection());
   memset(a,0,sizeof a);a[3]=0x40fa0320;a[8]=0x40e35768;assert(!m2_api(a));fake.notice=notify;a[9]=1;m2_api_result(a);uint64_t b[3]={0,9600,1};m2_pcm(b);assert(b[0]==(uintptr_t)(pcm+9600)&&b[1]*b[2]==size-9600&&fake.cxx_tail_requests==1);end();
  }else assert(!queued);
  assert(!fake.active&&!fake.armed&&!fake.cxx_enabled&&!fake.cxx_tail_active&&!fake.cxx_tail_pending&&!fake.errors);assert(!m2_native_selection());cases++;
 }
 printf("CXX_50MS_LOOP_TAIL_PASS cases=%u state_bytes=%zu repeated_lower_starts=5 duplicate_release=checked no_frame_retrigger=checked\n",cases,sizeof fake);return 0;
}
'''
p=E/'test.c';p.write_text(head+s+body);rows=[]
for cmd in [['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),'-o',str(E/'test')],[str(E/'test')]]:
 q=subprocess.run(cmd,capture_output=True,text=True);rows.append(dict(argv=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=rows,adapter_SHA256=hashlib.sha256((S/'adapter.c').read_bytes()).hexdigest(),native_verified=False),indent=2)+'\n');print(q.stdout+q.stderr,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
