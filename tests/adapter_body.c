/* Actual adapter C, native side effects resolved to isolated ABI mocks. */
static unsigned notifications,stops,reposts;
static void notify(uint32_t code,const void *v){assert(code==0x4212004||code==0x4212005);assert(v);notifications++;}
const notice_fn callback_slots[SLOTS]={[0 ... SLOTS-1]=notify};
void m2_restore_for_audio(void){}
static void stop_native(void){stops++;}
static uint32_t post_native(uintptr_t p,uint32_t flags){assert(p&&flags==2);reposts++;return 0;}
static void timestamp_native(uint64_t *v){*v=123;}
static void request_native(const void *v){assert(v);}
static void *resolve(uintptr_t a){switch(a){case 0x40fa0228:return(void*)stop_native;case 0x40c002a0:return(void*)post_native;case 0x40c7d438:return(void*)timestamp_native;case 0x40f9fe58:return(void*)request_native;default:abort();}}
static void request(uint32_t expected_segments){
 uint64_t a[13]={0};a[3]=0x40fa0320;a[8]=0x40e35768;
 assert(!m2_api(a));assert(a[1]==expected_segments);
 /* The saved original ROM notice target is resolved by the host ABI fixture. */
 fake.notice=notify;
 uint32_t slot=fake.used-1;uint64_t pcm[3]={0,9600,1};m2_pcm(pcm);
 assert(pcm[0]==(uintptr_t)fake.pcm&&pcm[1]*pcm[2]==fake.pcm_bytes&&pcm[2]==expected_segments);
 assert(m2_bind_file(fake.pcm,192,0)&&m2_native_selection());
 a[9]=1;m2_api_result(a);uint32_t payload[2]={0,0};
 m2_notice_slot(slot,0x4212004,payload);m2_notice_slot(slot,0x4212005,payload);
 assert(!fake.active&&!fake.armed&&fake.slots[slot].accepted&&fake.slots[slot].completed&&!fake.slots[slot].error);
}
int main(void){
 static uint8_t pcm[288000];unsigned requests=0,exhaustions=0;
 const unsigned sizes[]={192,262080,262272,288000};
 for(unsigned epoch=0;epoch<1000;epoch++){
  memset(&fake,0,sizeof fake);assert(!m2_bind_file(pcm,sizes[epoch%4],7));
  for(unsigned i=0;i<64;i++){
   request(fake.pcm_bytes/4>65535?2:1);requests++;
   uint32_t payload[2]={0,0};m2_notice_slot(i,0x4212005,payload);assert(fake.duplicates==i+1);
  }
  unsigned used=fake.used,completed=fake.completes;uint8_t *prior=fake.pcm;
  uint64_t a[13]={0};a[3]=0x40fa0320;a[8]=0x40e35768;assert(m2_api(a)==1);
  assert(fake.used==used&&used==64&&fake.completes==completed&&!fake.active&&fake.pcm==prior&&fake.selected);exhaustions++;
  assert(!m2_native_selection());assert(!fake.selected);
 }
 /* Delayed completion from a failed API cannot retire a newer owner. */
 memset(&fake,0,sizeof fake);assert(!m2_bind_file(pcm,192,0));uint64_t a[13]={0};a[3]=0x40fa0320;a[8]=0x40e35768;assert(!m2_api(a));m2_api_result(a);assert(!fake.active);
 a[1]=0;a[3]=0x40fa0320;assert(!m2_api(a));assert(fake.current==2&&fake.active);uint32_t payload[2]={0,0};m2_notice_slot(0,0x4212005,payload);assert(fake.active&&fake.current==2&&fake.stale==1);
 printf("MARK2_ADAPTER_STRESS_PASS requests=%u lifecycle_epochs=1000 exhaustion_checks=%u; 65th request returns rejection, no completion or audible fallback\n",requests,exhaustions);return 0;
}
