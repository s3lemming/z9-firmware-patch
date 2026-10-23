static uint8_t store[160];static uint32_t length,write_n=160,read_n=160;
static int create_fail,open_fail,owned_on_fail,close_fail,write_fail,read_fail,corrupt_read;
static unsigned closes,opens,creates;
static void init_native(void *v,const char *path,uint64_t a,uint64_t b){assert(!a&&!b);struct file *f=v;memset(f,0,sizeof *f);f->path=path;f->fd=UINT32_MAX;}
static uint32_t create_native(void *v,uint32_t flags){assert(!flags);struct file *f=v;creates++;f->fd=create_fail&&!owned_on_fail?UINT32_MAX:3;if(!create_fail){length=0;memset(store,0,sizeof store);}return create_fail?1:OK;}
static uint32_t open_native(void *v,uint32_t a,uint32_t b){assert(!a&&!b);struct file *f=v;opens++;f->fd=open_fail&&!owned_on_fail?UINT32_MAX:3;return open_fail?1:OK;}
static uint64_t size_native(void *v){assert(v);return length;}
static uint32_t write_native(void *v,const void *p,uint32_t n,uint32_t *actual){assert(v&&n==160);*actual=write_n;memcpy(store,p,write_n);length=write_n;return write_fail?1:OK;}
static uint32_t read_native(void *v,void *p,uint32_t n,uint32_t *actual){assert(v&&n==160);*actual=read_n;memcpy(p,store,read_n);if(corrupt_read&&read_n)((uint8_t*)p)[read_n/2]^=1;return read_fail?1:OK;}
static uint32_t close_native(void *v){struct file *f=v;assert(f->fd!=UINT32_MAX);f->fd=UINT32_MAX;closes++;return close_fail?1:OK;}
static void *resolve(uintptr_t a){switch(a){case 0x408666f8:return(void*)init_native;case 0x40866780:return(void*)create_native;case 0x40866720:return(void*)open_native;case 0x408669d4:return(void*)size_native;case 0x408668ac:return(void*)write_native;case 0x408669f8:return(void*)read_native;case 0x408667a8:return(void*)close_native;default:abort();}}
static void reset(void){length=160;write_n=read_n=160;create_fail=open_fail=owned_on_fail=close_fail=write_fail=read_fail=corrupt_read=0;closes=opens=creates=0;}
int main(void){uint8_t b[160];assert(!m2_profile_encode(b,123,1,"A:\\CUSTOM_SOUND\\VALID.WAV"));unsigned cases=0;
 reset();assert(!m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==2&&opens==1&&creates==1&&!memcmp(b,store,160));cases++;
 for(unsigned n=0;n<160;n++){
  reset();write_n=n;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==1&&!opens);struct m2_profile p;assert(m2_profile_decode(store,length,&p));cases++;
  reset();read_n=n;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==2&&opens==1);cases++;
 }
 for(int owned=0;owned<=1;owned++){
  reset();create_fail=1;owned_on_fail=owned;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==(unsigned)owned&&!opens);cases++;
  reset();open_fail=1;owned_on_fail=owned;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==1+(unsigned)owned);cases++;
 }
 reset();close_fail=1;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==1&&!opens);cases++;
 reset();write_fail=1;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==1&&!opens);cases++;
 reset();read_fail=1;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==2);cases++;
 reset();corrupt_read=1;assert(m2_native_profile_write("A:\\CUSTOM_SOUND\\M2SND0.CFG",b)&&closes==2);cases++;
 printf("MARK2_NATIVE_PROFILE_BRIDGE_PASS cases=%u (partial0..159 write/read, card create/open failures, close/write/read/readback corruption; ASan+UBSan)\n",cases);return 0;}
