/* Native 5.32 menu -> directory task -> WAV import -> actual photo adapter.
 * Four immutable import allocations are retained until guest shutdown. No
 * overwrite/free of any published PCM, and no fabricated completion fence.
 */
#include <stdint.h>
#include <stddef.h>
#include "mark2_import.h"
#include "profile.h"
#define FN(a,t) ((t)(uintptr_t)(a))
#define K ((struct picker *)(uintptr_t)0xa04e3d600ULL)
#define HOLDER ((uint8_t *)(uintptr_t)0xa028d29b0ULL)
extern int m2_bind_file(uint8_t *,uint32_t,uint32_t);
extern int m2_native_selection(void);
extern uint32_t m2_custom_selected(void);
#define FILE_LIMIT 20u
/* ASCII filename stored once as its native UTF-16 display label.  The mount
 * stays separate; construct the complete import/profile path on the stack. */
struct file {uint16_t label[112];char root;};
struct picker {
 uint32_t magic,calls,active,count,errors[2],overflow,scans;
 uint32_t import_status,selected,imports,attempts,native_selections,busy;
 struct m2_pcm_info info;
 uint32_t label_bytes[FILE_LIMIT];struct file files[FILE_LIMIT];uint8_t rows[6+FILE_LIMIT][44];
 void *retained[4];uint8_t *last_PCM;uint32_t last_bytes,published;char loaded_path[128];uint32_t restore_attempted,restore_status,persist_status,profile_commits;
 uint32_t directory_seen,directory_checks,directory_create_attempts,directory_create_status,directory_errors[2];
};
_Static_assert(sizeof(struct picker)<=6656,"picker fits original +8192 BSS reservation after 1536-byte adapter");
static void file_path(char path[128],const struct file *f){
 const char *prefix=":\\CUSTOM_SOUND\\";path[0]=f->root;
 for(unsigned i=0;i<15;i++)path[i+1]=prefix[i];
 unsigned n=0;do{path[16+n]=(char)f->label[n];}while(f->label[n++]);
}
static int wav(const uint8_t *s,uint32_t n){return n>=5 && s[n-4]=='.' && (s[n-3]|32)=='w' && (s[n-2]|32)=='a' && (s[n-1]|32)=='v';}
/* Native directory enumeration reports END as 80000030, not success=0. */
static int enumeration_ok(uint32_t rc){return !rc || rc==0x80000030u;}
static void directory_path(char *p,char root){
 const char *tail=":\\CUSTOM_SOUND";p[0]=root;unsigned i=0;
 do{p[i+1]=tail[i];}while(tail[i++]);
}
/* Original 5.32 ROM 40866C58 reads UTF-16 at +0x0e first, then
 * falls back to the 13-byte short-name field only if the long name is empty.
 * exFAT's synthesized 8.3 display name need not be an openable alias.
 * Bound the decoded name before writing a label or constructing a path. */
static int entry_name(const uint8_t *entry,uint8_t name[112],uint32_t *length){
 int wide=entry[14]||entry[15];
 for(uint32_t n=0;n<112;n++){
  if(!wide && n>=13)return 0;
  uint32_t c=wide?(uint32_t)entry[14+2*n]|((uint32_t)entry[15+2*n]<<8):entry[n];
  if(!c){name[n]=0;*length=n;return n!=0;}
  if(c<32 || c>126 || c=='/' || c=='\\' || c==':' || c=='*' ||
     c=='?' || c=='"' || c=='<' || c=='>' || c=='|')return 0;
  name[n]=(uint8_t)c;
 }
 return 0;
}
static uint32_t find_directory(const uint8_t *entry){
 const char *wanted="CUSTOM_SOUND";uint8_t name[112];uint32_t n;
 if(!entry_name(entry,name,&n)||n!=12)return 0;
 for(unsigned i=0;i<n;i++)if((name[i]|32)!=(uint8_t)(wanted[i]|32))return 0;
 K->directory_seen|=(entry[0x20e]&0x10)?1u:2u;return 0;
}
static int ensure_directory(char root){
 struct picker *p=K;char base[4]={root,':','\\',0},path[20];
 p->directory_checks++;p->directory_seen=0;directory_path(path,root);
 uint32_t rc=FN(0x402da504,uint32_t(*)(const char *,uint32_t,uint32_t(*)(const uint8_t *)))(base,0xff,find_directory);
 if(!enumeration_ok(rc) || (p->directory_seen&2u))return 1;
 if(p->directory_seen==1)return 0;
 p->directory_create_attempts++;
 p->directory_create_status=FN(0x402da358,uint32_t(*)(const char *,uint32_t))(path,0x10);
 /* Recheck native directory entry even on a concurrent already-created error. */
 p->directory_seen=0;
 rc=FN(0x402da504,uint32_t(*)(const char *,uint32_t,uint32_t(*)(const uint8_t *)))(base,0xff,find_directory);
 return !enumeration_ok(rc) || p->directory_seen!=1;
}
static uint32_t collect(const uint8_t *entry){
 struct picker *p=K;uint8_t name[112];uint32_t n;
 if((entry[0x20e]&0x10)||!entry_name(entry,name,&n)||!wav(name,n))return 0;
 if(p->count==FILE_LIMIT){p->overflow=1;return 0;}
 struct file *f=&p->files[p->count];const char *mount=FN(0x4031c30c,const char *(*)(uint32_t))(p->active-1);
 f->root=mount[0];
 for(uint32_t i=0;i<=n;i++)f->label[i]=name[i];
 p->label_bytes[p->count]=n*2;p->count++;return 0;
}

static int same_path(const char *a,const char *b){for(unsigned i=0;i<128;i++){if(a[i]!=b[i])return 0;if(!a[i])return 1;}return 0;}
static void slot_path(char *p,char root,unsigned slot){const char *tail=slot?":\\CUSTOM_SOUND\\M2SND1.CFG":":\\CUSTOM_SOUND\\M2SND0.CFG";p[0]=root;unsigned i=0;do{p[i+1]=tail[i];}while(tail[i++]);}
static int read_profile(char root,struct m2_profile *selected){
 if(ensure_directory(root))return -1;
 struct m2_profile a={0},b={0};uint8_t body[M2_PROFILE_BYTES];char path[40];
 slot_path(path,root,0);int av=!m2_native_profile_read(path,body)&&!m2_profile_decode(body,sizeof body,&a);
 slot_path(path,root,1);int bv=!m2_native_profile_read(path,body)&&!m2_profile_decode(body,sizeof body,&b);
 int i=m2_profile_newest(&a,av,&b,bv);if(i>=0)*selected=i?b:a;return i;
}
static int save_profile(char root,const char *path,uint32_t enabled){
 if(ensure_directory(root))return 1;
 struct m2_profile old={0};int prior=read_profile(root,&old);if(prior==-2)return 1;
 uint8_t body[M2_PROFILE_BYTES];char target[40];
 if(m2_profile_encode(body,prior>=0?old.sequence+1:1,enabled,path))return 1;
 slot_path(target,root,prior>=0?(unsigned)prior^1u:0);return m2_native_profile_write(target,body);
}
static void disable_profiles(void){
 struct picker *p=K;p->restore_attempted=1;p->persist_status=0;uint32_t was_active=p->active;p->active=3;
 for(unsigned card=0;card<2;card++){
  const char *mount=FN(0x4031c30c,const char *(*)(uint32_t))(card);struct m2_profile old={0};
  if(mount && mount[0]>='A'&&mount[0]<='Z'&&mount[1]==':'&&!mount[2]){
   int prior=read_profile(mount[0],&old);
   if((prior>=0&&old.enabled)||(prior<0&&p->published&&p->loaded_path[0]==mount[0]))
    p->persist_status|=save_profile(mount[0],0,0);
  }
 }
 p->active=was_active;
}
void m2_restore_for_audio(void){
 struct picker *p=K;if(p->restore_attempted || p->active)return;p->restore_attempted=1;
 /* Only the original Type A mapping may own the persisted custom route. */
 if(FN(0x403e74a8,uint32_t(*)(uint32_t))(0x02005f0e)!=0){p->restore_status=1;return;}
 p->magic=0x4d325049u;p->active=3;struct m2_profile choice={0};unsigned found=0;
 for(unsigned card=0;card<2;card++){
  const char *mount=FN(0x4031c30c,const char *(*)(uint32_t))(card);struct m2_profile f={0};
  if(mount && mount[0]>='A'&&mount[0]<='Z'&&mount[1]==':'&&!mount[2]&&read_profile(mount[0],&f)>=0&&f.enabled&&f.path[0]==mount[0]){choice=f;found++;}
 }
 if(found!=1){p->restore_status=found?3:2;p->active=0;return;}
 uint32_t size=M2_PCM_MAX+63,pool=FN(0x40d30594,uint32_t(*)(uint32_t))(0)>=size?0:1;
 if(p->attempts>=4 || FN(0x40d30594,uint32_t(*)(uint32_t))(pool)<size){p->restore_status=4;p->active=0;return;}
 void *allocation=FN(0x40d30458,void *(*)(uint32_t,uint32_t))(size,pool);
 if(!allocation){p->restore_status=4;p->active=0;return;}p->retained[p->attempts++]=allocation;
 uint8_t *pcm=(uint8_t *)(((uintptr_t)allocation+63u)&~(uintptr_t)63u);struct m2_pcm_info info={0};
 int rc=m2_native_import(choice.path,pcm,M2_PCM_MAX,&info);
 if(!rc){FN(0x40d2fa34,uint32_t(*)(void *,int32_t,int32_t))(pcm,(int32_t)info.play_bytes,0);rc=m2_bind_file(pcm,info.play_bytes,UINT32_MAX);}
 p->restore_status=rc?5:0;
 if(!rc){p->info=info;p->last_PCM=pcm;p->last_bytes=info.play_bytes;p->imports++;p->published=1;for(unsigned i=0;i<128;i++)p->loaded_path[i]=choice.path[i];}
 p->active=0;
}
static void publish_rows(void){
 struct picker *p=K;const uint8_t *builtin=(const uint8_t *)(uintptr_t)0x431897a4;
 for(uint32_t i=0;i<5*44;i++)((uint8_t *)p->rows)[i]=builtin[i];
 for(uint32_t r=5;r<6+p->count;r++){
  for(uint32_t i=0;i<44;i++)p->rows[r][i]=builtin[4*44+i];
  *(uint16_t *)p->rows[r]=(uint16_t)(r==5?0xc86:0xc87+r-6);
  *(uint32_t *)(p->rows[r]+24)=r==5?0x7e20:0x7e21+r-6;
 }
 *(uint8_t **)(HOLDER+0x10)=(uint8_t *)p->rows;*(uint16_t *)(HOLDER+0x20)=(uint16_t)(6+p->count);
}
void mark2_discovery_submit(void **outer){
 if(!outer || !*outer)return;
 const uint8_t *ctx=*outer;const uint8_t *holder=*(const uint8_t *const *)(ctx+0x50);
 uint32_t index=*(const uint16_t *)(ctx+0x32)+*(const uint16_t *)(ctx+0x58);
 if(holder!=HOLDER || index>=*(const uint16_t *)(holder+0x20))return;
 const uint8_t *rows=*(const uint8_t *const *)(holder+0x10);uint32_t id=*(const uint32_t *)(rows+index*44+24);
 struct picker *p=K;if((p->magic && p->magic!=0x4d325049u)||p->active)return;
 p->magic=0x4d325049u;p->calls++;
 if(id<0x7e20 || id>=0x7e21+FILE_LIMIT){
  if(m2_native_selection()){p->busy++;return;}
  disable_profiles();p->native_selections++;FN(0x405a57e0,void(*)(void **))(outer);return;
 }
 if(id==0x7e20){
  p->count=0;p->overflow=0;p->scans++;
  for(uint32_t storage=0;storage<2;storage++){
   const char *mount=FN(0x4031c30c,const char *(*)(uint32_t))(storage);char path[20];
   if(!mount || mount[0]<'A' || mount[0]>'Z' || mount[1]!=':' || mount[2]){p->errors[storage]=0xffffffffu;continue;}
   p->active=storage+1;p->directory_errors[storage]=ensure_directory(mount[0]);
   if(p->directory_errors[storage]){p->errors[storage]=0xffffffffu;continue;}
   directory_path(path,mount[0]);
   p->errors[storage]=FN(0x402da504,uint32_t(*)(const char *,uint32_t,uint32_t(*)(const uint8_t *)))(path,0xef,collect);
  }
  p->active=0;publish_rows();return;
 }
 uint32_t file=id-0x7e21;if(file>=p->count)return;
 if(p->attempts==4){p->import_status=M2_LIMIT;return;}
 p->active=3;uint32_t size=M2_PCM_MAX+63;
 uint32_t pool=FN(0x40d30594,uint32_t(*)(uint32_t))(0)>=size?0:1;
 if(FN(0x40d30594,uint32_t(*)(uint32_t))(pool)<size){p->import_status=M2_LIMIT;p->active=0;return;}
 void *allocation=FN(0x40d30458,void *(*)(uint32_t,uint32_t))(size,pool);
 if(!allocation){p->import_status=M2_BUSY;p->active=0;return;}
 p->retained[p->attempts++]=allocation;
 uint8_t *pcm=(uint8_t *)(((uintptr_t)allocation+63u)&~(uintptr_t)63u);struct m2_pcm_info info={0};
 char path[128];file_path(path,&p->files[file]);
 p->import_status=m2_native_import(path,pcm,M2_PCM_MAX,&info);
 if(!p->import_status){
  FN(0x40d2fa34,uint32_t(*)(void *,int32_t,int32_t))(pcm,(int32_t)info.play_bytes,0);
  if(m2_bind_file(pcm,info.play_bytes,file)){p->import_status=M2_BUSY;p->busy++;}
  else{
   p->restore_attempted=1;for(unsigned i=0;i<128;i++){p->loaded_path[i]=path[i];if(!path[i])break;}
   p->persist_status=save_profile(p->loaded_path[0],p->loaded_path,1);if(!p->persist_status)p->profile_commits++;
   p->info=info;p->selected=file;p->last_PCM=pcm;p->last_bytes=info.play_bytes;p->imports++;p->published=1;
   /* Recovered original handler maps extra UI values to native Type A=0;
    * no unknown DSID value is introduced. Original dispatch/notifications run. */
   FN(0x405a57e0,void(*)(void **))(outer);
  }
 }
 p->active=0;
}
void mark2_sound_refresh(void *ctx){
 FN(0x405a575c,void(*)(void *))(ctx);
 if(m2_custom_selected())for(unsigned i=0;i<K->count;i++){
  char path[128];file_path(path,&K->files[i]);
  if(same_path(K->loaded_path,path))FN(0x403b05d0,void(*)(void *,uint32_t,uint32_t))(ctx,0x7e21+i,1);
 }
}
/* Hook only the Camera sounds -> Type value consumer (405A5584).  The
 * native DSID enum and the five built-in Type submenu names stay intact. */
void mark2_outer_type_text(const char *text,uint32_t slot,uint32_t label){
 if(m2_custom_selected() && text==(const char *)(uintptr_t)0x4200b5e2)text="CUS";
 FN(0x403edb20,void(*)(const char *,uint32_t,uint32_t))(text,slot,label);
}
void mark2_picker_label(uint32_t language,uint32_t label,const uint16_t **out,uint32_t *bytes){
 if(label==0xc86){
  static const uint16_t scan[]={'L','o','a','d',' ','W','A','V',' ','f','r','o','m',' ','c','a','r','d'};
  static const uint16_t fail[]={'S','a','v','e',' ','f','a','i','l','e','d',' ','-',' ','c','h','e','c','k',' ','c','a','r','d'};
  if(language>=29){*out=0;*bytes=0;return;}
  *out=K->persist_status?fail:scan;*bytes=K->persist_status?sizeof fail:sizeof scan;return;
 }
 uint32_t i=label-0xc87;
 if(language<29 && i<K->count){*out=K->files[i].label;*bytes=K->label_bytes[i];}
 else{*out=0;*bytes=0;}
}
