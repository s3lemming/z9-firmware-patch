import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'firmware';T=R;E=Path(sys.argv[1]);E.mkdir(exist_ok=False)
header='#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nstatic void *resolve(unsigned long);\n'
s=(S/'picker.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define K ((struct picker *)(uintptr_t)0xa04e3d600ULL)','#define K (&fake)').replace('#define HOLDER ((uint8_t *)(uintptr_t)0xa028d29b0ULL)','#define HOLDER (fixture_holder)').replace('_Static_assert(sizeof(struct picker)','static struct picker fake;static _Alignas(8) uint8_t fixture_holder[48],fixture_builtin[220];\n_Static_assert(sizeof(struct picker)').replace('(const uint8_t *)(uintptr_t)0x431897a4','(const uint8_t *)fixture_builtin')
body=(T/'picker_body.c').read_text().replace('heap[4][288128]','heap[21][288128]').replace('allocs<4','allocs<21')
body=body.replace('static unsigned cases,', 'static unsigned content_seed;static int binding_busy,allocation_fail;\nstatic unsigned cases,')
body=body.replace('return heap[allocs++];','if(allocation_fail)return 0;return heap[allocs++];')
body=body.replace('(void)file;selected=1;', '(void)file;if(binding_busy)return 1;selected=1;')
body=body.replace('cursor=0;*owned=1;', 'for(unsigned i=0;i<file_bytes-44;i++)wav_data[i+44]=(uint8_t)(content_seed+path[0]+i);cursor=0;*owned=1;')
extra=r'''
static void fresh(void){present[0]=1;present[1]=0;directory[0]=1;file_missing=0;profile_write_fail=0;extra_files=0;short_bytes=192;content_seed=0;binding_busy=0;allocation_fail=0;memset(record_exists,0,sizeof record_exists);reset();select_row(5);}
int main(void){
 fresh();select_row(6);T(fake.cache_count==1&&allocs==2);uint8_t *first=fake.last_PCM;uint8_t old[192];memcpy(old,first,192);
 for(unsigned i=0;i<1000;i++){
  content_seed=i%9;select_row(6);T(fake.import_status==0&&selected&&fake.last_PCM[0]==(uint8_t)('A'+content_seed));
  T(!memcmp(first,old,192));if(i%7==0)select_row(0);
 }
 T(fake.cache_count==9&&allocs==10&&fake.cache_hits==992);puts("SINGLE_BOOT_1001_SELECTIONS_9_CONTENTS_IMMUTABLE_AND_NO_CLICK_QUOTA PASS");
 unsigned n=allocs;for(unsigned i=0;i<200;i++){select_row(7);T(fake.import_status==M2_FORMAT);select_row(8);T(fake.import_status==M2_LIMIT);}
 content_seed=3;select_row(6);T(!fake.import_status&&allocs==n);puts("400_INVALID_IMPORTS_DO_NOT_EXHAUST_VALID_SELECTION PASS");
 file_missing=1;select_row(6);T(fake.import_status==M2_OPEN);file_missing=0;select_row(6);T(!fake.import_status);puts("CACHE_HIT_STILL_OPENS_AND_VALIDATES_CARD PASS");
 content_seed=11;binding_busy=1;uint8_t *previous=fake.last_PCM;unsigned imports=fake.imports;select_row(6);T(fake.import_status==M2_BUSY&&fake.imports==imports&&fake.last_PCM==previous);binding_busy=0;select_row(6);T(!fake.import_status&&fake.last_PCM[0]=='A'+11);puts("BUSY_RETRY_PRESERVES_PRIOR_SELECTION PASS");
 /* Same full path with different content is never a stale cache hit. */
 T(fake.last_PCM!=previous);content_seed=0;select_row(6);T(fake.last_PCM==first);puts("SAME_PATH_CONTENT_CHANGE_AND_RETURN PASS");
 fresh();present[1]=directory[1]=1;select_row(5);select_row(6);uint8_t *a=fake.last_PCM;select_row(9);T(!fake.import_status&&fake.last_PCM!=a&&fake.last_PCM[0]=='B');puts("DUAL_CARD_SAME_FILENAME_DIFFERENT_PCM PASS");
 struct m2_profile pa={0},pb={0};T(read_profile('A',&pa)>=0&&read_profile('B',&pb)>=0&&!pa.enabled&&pb.enabled);
 reset();m2_restore_for_audio();T(!fake.restore_status&&fake.loaded_path[0]=='B');puts("DUAL_CARD_LATEST_SELECTION_RESTORES_UNAMBIGUOUSLY PASS");
 fresh();allocation_fail=1;select_row(6);T(fake.import_status&&fake.cache_count==0&&!selected);allocation_fail=0;select_row(6);T(!fake.import_status&&selected);puts("ALLOCATION_FAILURE_RECOVERS PASS");
 fresh();select_row(6);reset();m2_restore_for_audio();T(!fake.restore_status&&fake.cache_count==1);select_row(5);for(unsigned i=0;i<100;i++)select_row(6);T(fake.imports==101&&allocs==2);puts("AUTO_RESTORE_THEN_100_SELECTIONS PASS");
 fresh();for(content_seed=0;content_seed<20;content_seed++)select_row(6);T(fake.cache_count==20&&allocs==21);previous=fake.last_PCM;select_row(6);T(fake.import_status==M2_LIMIT&&fake.cache_full&&fake.last_PCM==previous);content_seed=0;select_row(6);T(!fake.import_status&&allocs==21);puts("20_DISTINCT_CONTENT_BOUND_PRESERVES_EXISTING_CACHE PASS");
 const uint16_t *label;uint32_t bytes;content_seed=21;select_row(6);mark2_picker_label(0,0xc86,&label,&bytes);T(bytes==40&&label[0]=='C');
 printf("CACHE_TEST_PASS assertions=%u picker_bytes=%zu\n",cases,sizeof fake);return 0;
}
'''
p=E/'picker_cache.c';p.write_text(header+s+body+extra)
commands=[]
for argv in [['gcc','-O1','-g','-I',str(S),'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(p),str(S/'profile.c'),str(S/'mark2_import.c'),'-o',str(E/'picker_cache')],[str(E/'picker_cache')]]:
 q=subprocess.run(argv,capture_output=True,text=True);commands.append(dict(argv=argv,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=commands,source_SHA256=hashlib.sha256((S/'picker.c').read_bytes()).hexdigest()),indent=2)+'\n');print(q.stdout+q.stderr,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
