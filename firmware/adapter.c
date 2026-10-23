/* P308 bounded C30/60/120 frame bridge experiment. Native imported PCM allocations are retained for the
 * entire guest lifetime. Callback slots are never reused in this experiment;
 * no callback or stop acknowledgement grants a production owner fence.
 * Original SOD consumer owns stop/wait/restart; no native worker replacement.
 */
#include <stdint.h>
#include <stddef.h>
#define FN(a,t) ((t)(uintptr_t)(a))
#define P ((struct state *)(uintptr_t)0xa04e3d000ULL)
#define BYTES 288000u
#define SLOTS 64u
#define NATIVE_U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NATIVE_U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
/* Custom PCM is published only after native card read, RIFF validation and close. */
typedef void (*notice_fn)(uint32_t,const void *);
extern const notice_fn callback_slots[SLOTS];
struct slot { uint32_t kind,accepted,completed,error,bootstrap; };
struct state {
 uint32_t magic,route,active,armed,kind,inputs,phase,tail;
 uint32_t busy,accepts,completes,errors,pcm_hooks,last_flags,result,stops;
 void *allocation;uint8_t *pcm;notice_fn notice;
 uint32_t current,used,api_replies,api_failures,rejects,stale,duplicates,reserved;
 struct slot slots[SLOTS];
 uint32_t cxx_pending,cxx_enabled,cxx_epoch,cxx_frames,cxx_submits,cxx_dropped,cxx_boots,cxx_stops;
 uint32_t cxx_bad_native,cxx_duplicates,cxx_pcm,last_sequence;
 uintptr_t last_metadata;
 uint8_t *silence;
 uint32_t cxx_waiting,cxx_wakes,cxx_natural_retire;
 uint32_t selected,pcm_bytes,selected_file;
};
void m2_composite(void);
extern void m2_restore_for_audio(void);
_Static_assert(sizeof(struct state)<=1536,"adapter must end before v09 picker at A04E3D600");
void m2_notice_slot(uint32_t slot,uint32_t code,const void *data) {
 struct state *p=P;
 if(slot>=p->used || !data || (code!=0x04212004u && code!=0x04212005u))return;
 const uint32_t *w=data;struct slot *s=&p->slots[slot];
 if(w[0]!=s->kind){p->errors++;return;}
 if(s->bootstrap && code==0x04212005u && !w[1] && p->current==slot+1 &&
    !s->completed && NATIVE_U8(0xa03d9d631ULL)==1 && NATIVE_U32(0xa03d9d638ULL)==1) {
  /* Finite custom Cxx sound has actually completed. Move the native sound
   * lifecycle to its ending phase so the unchanged completion consumer can
   * retire it. No host RAM write, fake completion, DMA stop, or memory free. */
  NATIVE_U32(0xa03d9d638ULL)=2;p->cxx_natural_retire++;
 }
 uint32_t wake=s->bootstrap && code==0x04212005u && !w[1] &&
  p->current==slot+1 && p->cxx_waiting && p->cxx_enabled && NATIVE_U8(0xa03d9d631ULL)==1 &&
  NATIVE_U32(0xa03d9d638ULL)==2;
 if(code==0x04212004u) {
  if(s->accepted){p->duplicates++;return;}
  s->accepted=1;s->error=w[1];p->accepts++;
  if(w[1]){p->rejects++;if(p->current==slot+1)p->active=p->armed=0;}
 } else {
  if(s->completed){p->duplicates++;return;}
  s->completed=1;s->error|=w[1];p->completes++;
  if(p->current==slot+1)p->active=p->armed=0;else {p->stale++;return;}
 }
 /* Preserve each original camera notification once. No token is claimed in
  * its payload; identity comes from the immutable callback registration. */
 if(p->notice)p->notice(code,data);
 /* Delay the first ordinary SOD dispatch until the actual bootstrap ends.
  * Repost the latest copied SOD record only after the real owned completion
  * and verified original state transition. This is
  * not a DMA/producer fence and grants no memory reclamation permission. */
 if(wake && !NATIVE_U8(0xa03d9d631ULL) && !NATIVE_U32(0xa03d9d638ULL)) {
  FN(0x40c002a0,uint32_t(*)(uintptr_t,uint32_t))(0xa03d9d570ULL,2);
  p->cxx_wakes++;
 }
 if(s->bootstrap && code==0x04212005u && p->current==slot+1)p->cxx_waiting=0;
}
uint32_t m2_api(uint64_t *args) {
 struct state *p=P;uint64_t caller=args[8];
 if(args[3]==0x40fa0320u && !p->selected)m2_restore_for_audio();
 if(p->selected && !p->used && !p->cxx_enabled && ((caller==0x40e35768u && args[0]==6)||(caller==0x40e357d4u && args[0]==0)))p->cxx_pending=1;

 if(args[3]!=0x40fa0320u || !p->selected || !p->pcm || !p->pcm_bytes)return 0;
 uint32_t bootstrap=p->cxx_pending && args[1]==0 &&
  ((caller==0x40e35768u && args[0]==6) || (caller==0x40e357d4u && args[0]==0));
 if(bootstrap && NATIVE_U8(0xa03d9d631ULL)>1) {
  p->cxx_bad_native++;p->cxx_pending=0;return 0;
 }
 if(!bootstrap && !((caller==0x40e355c8u && args[0]==1 && args[1]==1) ||
      (caller==0x40e35768u && args[0]==0 && args[1]==0)))return 0;
 p->magic=0x4d325313u;p->inputs++;p->route=1;
 if(p->active){p->busy++;p->rejects++;return 1;}
 /* Exhaustion fails closed, never wraps a callback identity or falls back
  * to a stock clip through an active custom route. Research bound only. */
 if(p->used==SLOTS){p->rejects++;return 1;}
 uint32_t slot=p->used++;p->slots[slot].kind=(uint32_t)args[0];
 p->notice=(notice_fn)(uintptr_t)args[3];p->route=1;
 p->slots[slot].bootstrap=bootstrap;
 p->current=slot+1;p->kind=(uint32_t)args[0];p->active=1;p->armed=bootstrap?3:1;
 if(bootstrap){p->route=2;p->cxx_pending=0;p->cxx_enabled=1;p->cxx_boots++;}
 args[1]=p->pcm_bytes/4u>65535u?2u:1u;
 args[3]=(uintptr_t)callback_slots[slot];return 0;
}
void m2_api_result(uint64_t *args) {
 struct state *p=P;uint32_t slot;
 for(slot=0;slot<p->used;slot++)if(args[3]==(uintptr_t)callback_slots[slot])break;
 if(slot==p->used)return;
 p->api_replies++;
 if(!(args[9]&1u)) {
  p->api_failures++;p->rejects++;
  if(p->current==slot+1)p->active=p->armed=0;
 }
}
void m2_pcm(uint64_t *args) {
 struct state *p=P;
 if(p->active && p->armed==3) {
  if(args[1] && args[2] && args[1]<=9600 && args[2]<=9600/args[1]) {
   args[0]=(uintptr_t)p->pcm;args[2]=p->pcm_bytes/4u>65535u?2u:1u;args[1]=p->pcm_bytes/args[2];p->armed=4;p->cxx_pcm++;
  } else p->errors++;
  return;
 }
 if(!p->active || p->armed!=1 || args[1]!=(p->kind?4800u:9600u))return;
 p->armed=2;args[0]=(uintptr_t)p->pcm;args[2]=p->pcm_bytes/4u>65535u?2u:1u;args[1]=p->pcm_bytes/args[2];p->pcm_hooks++;
}
uint32_t m2_flags(uint32_t flags) {
 struct state *p=P;p->last_flags=flags;
 if(flags&~7u)return 0;
 if(flags&1u)p->stops++;
 if(flags&2u){
  if(p->route==2 && p->active){
   p->cxx_waiting=1;FN(0x40fa0228,void(*)(void))();return 1;
  }
  p->route=0;return 0;
 }
 if(p->route && (flags&4u)) {
  /* Combined stop+phase must retain explicit native stop, without kind2. */
  if(flags&1u)FN(0x40fa0228,void(*)(void))();
  p->phase++;return 1;
 }
 return 0;
}
uint32_t m2_terminal(uintptr_t caller){
 if(caller==0x40f84ac4u){m2_composite();return 0;}
 if(P->route){P->tail++;return 1;}return 0;
}
uint32_t m2_fast_timer(uintptr_t timer) {
 if(timer==0xa03d9d5e8ULL && P->route && P->kind==0 && P->active){P->result++;return 1;}
 return 0;
}
void m2_composite(void) {
 struct state *p=P;
 p->route=0;p->cxx_pending=p->selected;p->cxx_enabled=0;p->cxx_epoch++;
 p->last_metadata=0;p->last_sequence=0;
}
void m2_cxx_stop(void) {
 struct state *p=P;
 if(p->cxx_enabled){p->cxx_enabled=0;p->cxx_stops++;}
 if(p->route==2 && p->active)FN(0x40fa0228,void(*)(void))();
}
void m2_frame_snapshot(uint64_t *args) {
 struct state *p=P;args[10]=args[11]=args[12]=0;
 if(!p->cxx_enabled)return;
 const uint8_t *r=(const uint8_t *)(uintptr_t)args[0];
 /* R+0 varies 1..24 in the observed native burst; it is not a class tag. */
 if(!r){p->cxx_dropped++;return;}
 const uint8_t *m=*(const uint8_t *const *)(r+0x790);
 if(!m || *(const uint32_t *)m!=3){p->cxx_dropped++;return;}
 args[10]=*(const uint32_t *)(m+0x120);args[11]=p->cxx_epoch;args[12]=(uintptr_t)m;
 p->cxx_frames++;
}
void m2_frame_commit(uint64_t *args) {
 struct state *p=P;
 if(!args[11])return;
 if(!p->cxx_enabled || args[11]!=p->cxx_epoch){p->cxx_dropped++;return;}
 if(p->last_metadata==args[12] && p->last_sequence==args[10]){p->cxx_duplicates++;return;}
 p->last_metadata=args[12];p->last_sequence=(uint32_t)args[10];
 /* Audio control request, not a fabricated original photo/exposure event.
  * Copy-only native producer; original SOD task retains stop/wait/restart.
  * Latest native event flags can coalesce. No history-buffer replay sound. */
 struct { uint32_t control0,control1;uint64_t control2,timestamp; } request={192,1536,1,0};
 FN(0x40c7d438,void(*)(uint64_t *))(&request.timestamp);
 p->cxx_submits++;
 FN(0x40f9fe58,void(*)(const void *))(&request);
}

int m2_bind_file(uint8_t *pcm,uint32_t bytes,uint32_t file){
 struct state *p=P;
 if(!pcm || !bytes || bytes>BYTES || bytes%192u || p->active || p->armed || p->cxx_enabled)return 1;
 p->pcm=pcm;p->pcm_bytes=bytes;p->selected_file=file;p->route=0;
 __atomic_store_n(&p->selected,1,__ATOMIC_RELEASE);return 0;
}
int m2_native_selection(void){
 struct state *p=P;if(p->active || p->armed || p->cxx_enabled)return 1;
 p->selected=0;p->route=0;p->cxx_pending=0;return 0;
}
uint32_t m2_custom_selected(void){return __atomic_load_n(&P->selected,__ATOMIC_ACQUIRE);}
