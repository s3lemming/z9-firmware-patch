#include "mark2_import.h"

/* Fixed to original EG 5.32, exact wrapper ABI recovered in P1.
 * This bridge is executed only in an isolated laboratory address map.
 * ROM calls depend on initialized native RTOS file task on real firmware.
 */
struct native_file {
    const char *path; uint32_t flags, fd; uint64_t cursor, length, auxiliary;
};
_Static_assert(sizeof(struct native_file)==0x28,"native file object size");
_Static_assert(offsetof(struct native_file,fd)==0xc,"native fd field");
_Static_assert(offsetof(struct native_file,length)==0x18,"native length field");
#define CALL(address,type) ((type)(uintptr_t)(address))
#define SUCCESS UINT32_C(0x04350080)
static int native_open(void *ctx,const char *path,int *owned) {
    struct native_file *f=ctx;
    CALL(0x408666f8,uint64_t (*)(void *,const char *,uint64_t,uint64_t))(f,path,0,0);
    uint32_t status=CALL(0x40866720,uint32_t (*)(void *,uint32_t,uint32_t))(f,0,0);
    *owned=f->fd!=UINT32_MAX;
    return status!=SUCCESS;
}
static int native_size(void *ctx,uint64_t *bytes) {
    *bytes=CALL(0x408669d4,uint64_t (*)(void *))(ctx);return 0;
}
static int native_read(void *ctx,uint8_t *dst,uint32_t request,uint32_t *actual) {
    return CALL(0x408669f8,uint32_t (*)(void *,uint8_t *,uint32_t,uint32_t *))(ctx,dst,request,actual)!=SUCCESS;
}
static int native_close(void *ctx) {
    return CALL(0x408667a8,uint32_t (*)(void *))(ctx)!=SUCCESS;
}
int m2_native_import(const char *path,uint8_t *dst,uint32_t capacity,struct m2_pcm_info *info) {
    struct native_file f;
    const struct m2_file_ops op={native_open,native_size,native_read,native_close,0};
    return m2_import(&op,&f,path,dst,capacity,info);
}
