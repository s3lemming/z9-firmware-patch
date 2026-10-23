/* Actual picker and importer, mocked native filesystem; no device claim. */
static unsigned cases, selected, allocs, writes, scans, makes, root_decoys;
static unsigned extra_files, short_bytes;static const char *outer_text;
static int present[2]={1,0}, directory[2], collision, mkdir_fail, root_error, folder_error,file_missing,profile_write_fail;
static uint8_t heap[4][288128], records[2][2][160], wav_data[300064];
static int record_exists[2][2];static unsigned file_bytes, cursor;
#define T(v) do{assert(v);cases++;}while(0)
static void le16p(unsigned p,unsigned v){wav_data[p]=v;wav_data[p+1]=v>>8;}
static void le32p(unsigned p,unsigned v){for(unsigned i=0;i<4;i++)wav_data[p+i]=v>>(8*i);}
static void make_wav(unsigned n,unsigned rate){
 memset(wav_data,0,sizeof wav_data);memcpy(wav_data,"RIFF",4);le32p(4,n+36);
 memcpy(wav_data+8,"WAVEfmt ",8);le32p(16,16);le16p(20,1);le16p(22,2);
 le32p(24,rate);le32p(28,rate*4);le16p(32,4);le16p(34,16);
 memcpy(wav_data+36,"data",4);le32p(40,n);memset(wav_data+44,0x41,n);file_bytes=n+44;
}
static const char *mount_name(uint32_t card){assert(card<2);return card?"B:":"A:";}
static uint32_t capacity(uint32_t pool){(void)pool;return 0x100000;}
static void *allocate(uint32_t n,uint32_t pool){assert(n<=sizeof heap[0]&&pool<2&&allocs<4);return heap[allocs++];}
static uint32_t flush(void *p,int32_t n,int32_t mode){assert(p&&n>0&&!mode);return 0;}
static void native_handler(void **ctx){(void)ctx;}
static uint32_t property(uint32_t id){assert(id==0x2005f0e);return 0;}
static void original_refresh(void *ctx){(void)ctx;}
static void highlight(void *ctx,uint32_t id,uint32_t mode){(void)ctx;(void)id;(void)mode;}
static void emit(const char *name,unsigned attrs,uint32_t(*fn)(const uint8_t *)){
 uint8_t entry[600]={0};memcpy(entry,name,strlen(name)+1);entry[0x20e]=attrs;fn(entry);
}
static uint32_t enumerate(const char *path,uint32_t filter,uint32_t(*fn)(const uint8_t *)){
 unsigned card=path[0]-'A';assert(card<2);scans++;if(!present[card]||root_error)return 0x80000010u;
 if(!strcmp(path+1,":\\")){
  assert(filter==0xff);emit("ROOT_ONLY.WAV",0x20,fn);root_decoys++;
  emit("M2SND0.CFG",0x20,fn);emit("OTHER",0x10,fn);
  if(directory[card])emit("CUSTOM_SOUND",0x10,fn);
  if(collision)emit("CUSTOM_SOUND",0x20,fn);
 }else{
  assert(!strcmp(path+1,":\\CUSTOM_SOUND")&&filter==0xef);
  if(!directory[card]||folder_error)return 0x80000010u;
  emit("A.WAV",0x20,fn);for(unsigned i=0;i<extra_files;i++){char n[32];snprintf(n,sizeof n,"EXTRA%02u.WAV",i);emit(n,0x20,fn);}emit("BAD.WAV",0x20,fn);emit("LONG.WAV",0x20,fn);
  emit("nested",0x10,fn);emit("no.mp3",0x20,fn);emit("bad:alias.WAV",0x20,fn);
 }
 return 0x80000030u;
}
static uint32_t mkdir_native(const char *path,uint32_t attr){
 unsigned card=path[0]-'A';assert(card<2&&!strcmp(path+1,":\\CUSTOM_SOUND")&&attr==0x10);
 makes++;if(mkdir_fail)return 0x80000020u;directory[card]=1;return 0;
}
int m2_bind_file(uint8_t *pcm,uint32_t bytes,uint32_t file){assert(pcm&&bytes&&bytes<=288000);(void)file;selected=1;return 0;}
int m2_native_selection(void){selected=0;return 0;}
uint32_t m2_custom_selected(void){return selected;}
static int op_open(void *ctx,const char *path,int *owned){
 (void)ctx;unsigned card=path[0]-'A';assert(card<2&&!strncmp(path+1,":\\CUSTOM_SOUND\\",15));
 if(!present[card]||!directory[card]||file_missing)return 1;
 make_wav(strstr(path,"LONG")?288004:short_bytes?short_bytes:288000,strstr(path,"BAD")?44100:48000);cursor=0;*owned=1;return 0;
}
static int op_size(void *ctx,uint64_t *n){(void)ctx;*n=file_bytes;return 0;}
static int op_read(void *ctx,uint8_t *p,uint32_t n,uint32_t *actual){
 (void)ctx;if(n>file_bytes-cursor)n=file_bytes-cursor;memcpy(p,wav_data+cursor,n);cursor+=n;*actual=n;return 0;
}
static int op_close(void *ctx){(void)ctx;return 0;}
int m2_native_import(const char *path,uint8_t *pcm,uint32_t n,struct m2_pcm_info *info){
 const struct m2_file_ops ops={.open=op_open,.size=op_size,.read=op_read,.close=op_close};return m2_import(&ops,0,path,pcm,n,info);
}
static unsigned bank(const char *path){
 assert(!strncmp(path+1,":\\CUSTOM_SOUND\\M2SND",20));unsigned v=path[21]-'0';assert(v<2);return v;
}
int m2_native_profile_read(const char *path,uint8_t *out){
 unsigned card=path[0]-'A',slot=bank(path);assert(card<2);
 if(!present[card]||!directory[card]||!record_exists[card][slot])return 1;
 memcpy(out,records[card][slot],160);return 0;
}
int m2_native_profile_write(const char *path,const uint8_t *body){
 unsigned card=path[0]-'A',slot=bank(path);assert(card<2);
 if(!present[card]||!directory[card]||profile_write_fail)return 1;
 memcpy(records[card][slot],body,160);record_exists[card][slot]=1;writes++;return 0;
}
static void text_sink(const char *s,uint32_t slot,uint32_t label){assert(slot==0&&label==0x46);outer_text=s;}
static void *resolve(uintptr_t a){switch(a){
 case 0x403edb20:return(void*)text_sink;
 case 0x4031c30c:return(void*)mount_name;case 0x402da504:return(void*)enumerate;
 case 0x402da358:return(void*)mkdir_native;case 0x40d30594:return(void*)capacity;
 case 0x40d30458:return(void*)allocate;case 0x40d2fa34:return(void*)flush;
 case 0x405a57e0:return(void*)native_handler;case 0x403e74a8:return(void*)property;
 case 0x405a575c:return(void*)original_refresh;case 0x403b05d0:return(void*)highlight;
 default:fprintf(stderr,"unexpected ABI %lx\n",(unsigned long)a);abort();}}
static void select_row(unsigned index){uint8_t context[128]={0};*(void**)(context+0x50)=fixture_holder;*(uint16_t*)(context+0x32)=(uint16_t)index;void *ctx=context;mark2_discovery_submit(&ctx);}
static void reset(void){
 memset(&fake,0,sizeof fake);selected=0;allocs=0;memset(fixture_holder,0,sizeof fixture_holder);
 memset(fixture_builtin,0,sizeof fixture_builtin);for(unsigned i=0;i<5;i++)*(uint32_t*)(fixture_builtin+i*44+24)=0x3a6a+i;
 static uint8_t initial[6*44];memcpy(initial,fixture_builtin,sizeof fixture_builtin);*(uint32_t*)(initial+5*44+24)=0x7e20;
 *(void**)(fixture_holder+0x10)=initial;*(uint16_t*)(fixture_holder+0x20)=6;
}
int main(void){
 reset();select_row(5);T(makes==1&&directory[0]&&fake.count==3);T(root_decoys&&fake.directory_checks==2);
 char actual_path[128];file_path(actual_path,&fake.files[0]);T(!strcmp(actual_path,"A:\\CUSTOM_SOUND\\A.WAV"));T(fake.label_bytes[0]==10&&fake.files[0].label[0]=='A');
 unsigned mk=makes;select_row(5);T(makes==mk&&fake.count==3);select_row(6);
 T(selected&&fake.imports==1&&fake.profile_commits==1&&fake.last_bytes==288000&&writes==1);
 struct m2_profile profile={0};T(!m2_profile_decode(records[0][0],160,&profile)&&!strcmp(profile.path,"A:\\CUSTOM_SOUND\\A.WAV"));
 uint8_t *pcm=fake.last_PCM;uint8_t saved[sizeof records];memcpy(saved,records,sizeof saved);
 select_row(7);T(fake.import_status==M2_FORMAT&&fake.imports==1&&selected&&fake.last_PCM==pcm);T(!memcmp(saved,records,sizeof saved)&&writes==1&&pcm[0]==0x41);
 select_row(8);T(fake.import_status==M2_LIMIT&&fake.imports==1&&fake.last_PCM==pcm&&selected);T(!memcmp(saved,records,sizeof saved)&&writes==1&&pcm[287999]==0x41);
 reset();m2_restore_for_audio();T(selected&&fake.imports==1&&!fake.restore_status&&fake.last_bytes==288000);
 directory[0]=0;mk=makes;reset();select_row(5);T(makes==mk+1&&fake.count==3);
 directory[0]=0;collision=1;mk=makes;reset();select_row(5);T(fake.count==0&&fake.directory_errors[0]&&makes==mk);collision=0;
 mkdir_fail=1;mk=makes;reset();select_row(5);T(!fake.count&&makes==mk+1&&fake.directory_create_status==0x80000020u);mkdir_fail=0;
 root_error=1;mk=makes;reset();select_row(5);T(!fake.count&&makes==mk);root_error=0;
 directory[0]=1;folder_error=1;reset();select_row(5);T(!fake.count&&fake.errors[0]==0x80000010u);folder_error=0;
 present[0]=0;mk=makes;reset();m2_restore_for_audio();T(!selected&&!fake.imports&&makes==mk);present[0]=1;
 /* Current immutable cache survives removal; cold restore still requires card. */
 reset();m2_restore_for_audio();T(selected&&!fake.restore_status);pcm=fake.last_PCM;
 present[0]=0;select_row(5);T(selected&&fake.last_PCM==pcm&&!fake.count&&pcm[0]==0x41);
 select_row(0);T(!selected&&fake.persist_status);present[0]=1;reset();m2_restore_for_audio();T(selected&&!fake.restore_status);
 file_missing=1;reset();m2_restore_for_audio();T(!selected&&fake.restore_status==5&&!fake.imports);file_missing=0;
 present[0]=0;reset();m2_restore_for_audio();T(!selected&&fake.restore_status==2);present[0]=1;m2_restore_for_audio();T(!selected&&!fake.imports);select_row(5);select_row(6);T(selected&&fake.imports==1);
 reset();select_row(5);profile_write_fail=1;unsigned prior_writes=writes;memcpy(saved,records,sizeof saved);select_row(6);
 T(selected&&fake.imports==1&&fake.persist_status&&writes==prior_writes&&!memcmp(saved,records,sizeof saved));profile_write_fail=0;
 /* Two enabled cards must not be guessed; an A-path profile moved to B is rejected. */
 present[1]=1;directory[1]=1;T(!m2_profile_encode(records[1][0],1,1,"B:\\CUSTOM_SOUND\\B.WAV"));record_exists[1][0]=1;
 reset();m2_restore_for_audio();T(!selected&&fake.restore_status==3&&!fake.imports);
 present[0]=0;reset();m2_restore_for_audio();T(selected&&!strcmp(fake.loaded_path,"B:\\CUSTOM_SOUND\\B.WAV"));
 memcpy(records[1],records[0],sizeof records[1]);memcpy(record_exists[1],record_exists[0],sizeof record_exists[1]);reset();m2_restore_for_audio();T(!selected&&fake.restore_status==2);
 select_row(5);select_row(6);T(selected&&fake.profile_commits==1&&!strcmp(fake.loaded_path,"B:\\CUSTOM_SOUND\\A.WAV"));
 reset();m2_restore_for_audio();T(selected&&!fake.restore_status&&!strcmp(fake.loaded_path,"B:\\CUSTOM_SOUND\\A.WAV"));present[0]=1;present[1]=0;
 /* Root-only legacy records are never requested by any mocked profile ABI. */
 memset(record_exists,0,sizeof record_exists);reset();m2_restore_for_audio();T(!selected&&fake.restore_status==2&&!fake.imports);
 /* New menu capacity uses the same 8192-byte initialized BSS, not TTBR. */
 extra_files=25;reset();select_row(5);T(fake.count==20&&fake.overflow);
 T(*(uint16_t*)(fixture_holder+0x20)==26);
 for(unsigned i=0;i<20;i++){
  const uint16_t *label=0;uint32_t bytes=0;mark2_picker_label(0,0xc87+i,&label,&bytes);
  T(label&&bytes==fake.label_bytes[i]);for(unsigned k=0;k<bytes/2;k++)T(label[k]!=':'&&label[k]!='\\');
 }
 select_row(25);T(selected&&fake.selected==19&&fake.imports==1);
 file_path(actual_path,&fake.files[19]);T(!strcmp(fake.loaded_path,actual_path));
 T(!m2_profile_decode(records[0][0],160,&profile)||!m2_profile_decode(records[0][1],160,&profile));
 extra_files=0;
 /* Route-specific outer text; native A remains A after selecting built-in. */
 mark2_outer_type_text((const char*)(uintptr_t)0x4200b5e2,0,0x46);T(!strcmp(outer_text,"CUS"));
 mark2_outer_type_text("Type B",0,0x46);T(!strcmp(outer_text,"Type B"));
 select_row(0);mark2_outer_type_text((const char*)(uintptr_t)0x4200b5e2,0,0x46);T(outer_text==(const char*)(uintptr_t)0x4200b5e2);
 /* Each duration gets a fresh picker, matching one boot; do not mask the
  * separate four-allocation lifecycle bound by counting earlier attempts. */
 unsigned lengths[]={4,192,9600,19200,96000,192000,262140,262144,262148,287996,288000};
 for(unsigned i=0;i<sizeof lengths/sizeof lengths[0];i++){
  short_bytes=lengths[i];reset();select_row(5);select_row(6);
  T(selected&&fake.import_status==0&&fake.info.valid_bytes==short_bytes);
  T(fake.info.play_bytes==(short_bytes+191)/192*192&&fake.last_bytes<=288000);
  for(unsigned j=short_bytes;j<fake.last_bytes;j++)T(fake.last_PCM[j]==0);
 }
 short_bytes=0;
 /* Short alias differs from exFAT long filename. Match display, open,
  * and persisted path against the original long filename, not the alias. */
 uint8_t ent[600]={0}, decoded[112];uint32_t length=0;
 const char *longname="example_long_sound.wav";memcpy(ent,"EXAMPL~1.WAV",sizeof "EXAMPL~1.WAV");
 for(unsigned i=0;longname[i];i++)ent[14+2*i]=(uint8_t)longname[i];
 T(entry_name(ent,decoded,&length)&&length==strlen(longname)&&!strcmp((char*)decoded,longname));
 reset();fake.active=1;collect(ent);T(fake.count==1);
 file_path(actual_path,&fake.files[0]);T(!strcmp(actual_path,"A:\\CUSTOM_SOUND\\example_long_sound.wav"));
 /* Reject unsupported/oversized full names without falling back to a
  * different, deceptively valid short alias. */
 ent[15]=1;T(!entry_name(ent,decoded,&length));ent[15]=0;
 ent[14]='/';T(!entry_name(ent,decoded,&length));
 for(unsigned i=0;i<112;i++){ent[14+2*i]='x';ent[15+2*i]=0;}
 T(!entry_name(ent,decoded,&length));ent[14+2*111]=0;
 T(entry_name(ent,decoded,&length)&&length==111);
 memset(ent,0,sizeof ent);memcpy(ent,"CUSTOM_S",8);
 for(unsigned i=0;i<12;i++)ent[14+2*i]=(uint8_t)"CUSTOM_SOUND"[i];
 ent[0x20e]=0x10;fake.directory_seen=0;find_directory(ent);T(fake.directory_seen==1);
 memset(ent,0,sizeof ent);memcpy(ent,"ONE.WAV",8);T(entry_name(ent,decoded,&length)&&!strcmp((char*)decoded,"ONE.WAV"));
 printf("MARK2_LAYOUT picker_size=%zu files=%zu stride=%zu rows=%zu loaded_path=%zu restore=%zu directory=%zu\n",sizeof fake,offsetof(struct picker,files),sizeof(struct file),offsetof(struct picker,rows),offsetof(struct picker,loaded_path),offsetof(struct picker,restore_attempted),offsetof(struct picker,directory_seen));
 printf("MARK2_DIRECTORY_AND_ACTUAL_IMPORT_PASS %u scans=%u mkdir=%u writes=%u\n",cases,scans,makes,writes);return 0;
}
