#include "profile.h"
#define FN(a,t) ((t)(uintptr_t)(a))
#define OK 0x04350080u
struct file {const char *path;uint32_t flags,fd;uint64_t cursor,length,auxiliary;};
_Static_assert(sizeof(struct file)==40,"original native file ABI");
static void init(struct file *f,const char *p){FN(0x408666f8,void(*)(void *,const char *,uint64_t,uint64_t))(f,p,0,0);}
int m2_native_profile_read(const char *path,uint8_t *b){
 struct file f;init(&f,path);uint32_t status=FN(0x40866720,uint32_t(*)(void *,uint32_t,uint32_t))(&f,0,0);uint32_t actual=0;
 int bad=status!=OK;
 if(!bad && FN(0x408669d4,uint64_t(*)(void *))(&f)!=M2_PROFILE_BYTES)bad=1;
 if(!bad)bad=FN(0x408669f8,uint32_t(*)(void *,void *,uint32_t,uint32_t *))(&f,b,M2_PROFILE_BYTES,&actual)!=OK || actual!=M2_PROFILE_BYTES;
 if(f.fd!=UINT32_MAX && FN(0x408667a8,uint32_t(*)(void *))(&f)!=OK)bad=1;
 return bad;
}
int m2_native_profile_write(const char *path,const uint8_t *b){
 struct file f;init(&f,path);uint32_t status=FN(0x40866780,uint32_t(*)(void *,uint32_t))(&f,0);uint32_t actual=0;
 int bad=status!=OK;
 if(!bad)bad=FN(0x408668ac,uint32_t(*)(void *,const void *,uint32_t,uint32_t *))(&f,b,M2_PROFILE_BYTES,&actual)!=OK || actual!=M2_PROFILE_BYTES;
 if(f.fd!=UINT32_MAX && FN(0x408667a8,uint32_t(*)(void *))(&f)!=OK)bad=1;
 if(bad)return 1;
 uint8_t verify[M2_PROFILE_BYTES];if(m2_native_profile_read(path,verify))return 1;
 for(unsigned i=0;i<M2_PROFILE_BYTES;i++)if(b[i]!=verify[i])return 1;
 return 0;
}
