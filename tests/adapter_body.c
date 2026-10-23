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
