"""Real standalone picker C with synthetic native interfaces; no camera claim."""
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'firmware';E=Path(sys.argv[1]);E.mkdir()
header='#include <assert.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\nstatic void *resolve(unsigned long);\n'
s=(S/'picker.c').read_text().replace('#define FN(a,t) ((t)(uintptr_t)(a))','#define FN(a,t) ((t)resolve((uintptr_t)(a)))').replace('#define K ((struct picker *)(uintptr_t)0xa04e3d600ULL)','#define K (&fake)').replace('#define HOLDER ((uint8_t *)(uintptr_t)0xa028d29b0ULL)','#define HOLDER (fixture_holder)').replace('_Static_assert(sizeof(struct picker)','static struct picker fake;static _Alignas(8) uint8_t fixture_holder[48],fixture_builtin[220];\n_Static_assert(sizeof(struct picker)').replace('(const uint8_t *)(uintptr_t)0x431897a4','(const uint8_t *)fixture_builtin')
body=(R/'picker_body.c').read_text()
body=body.replace('static unsigned extra_files, short_bytes;','static unsigned type_value,highlight_calls,focus_id,cleared_types,last_mark;\nstatic unsigned extra_files, short_bytes;')
body=body.replace('assert(id==0x2005f0e);return 0;','assert(id==0x2005f0e);return type_value;')
body=body.replace('(void)ctx;(void)id;(void)mode;','(void)ctx;highlight_calls++;if(id>=0x3a6a&&id<0x3a6f&&!mode)cleared_types|=1u<<(id-0x3a6a);if(mode)last_mark=id;')
body=body.replace('case 0x403edb20:', 'case 0x403ae600:return(void*)entry_mode;case 0x403b0560:return(void*)focus_file;case 0x405a54b4:return(void*)original_parent;case 0x403edb20:')
prefix='static uint32_t entry_mode(void){return 1;}\nstatic unsigned text_calls,refresh_calls;\n'
body=body.replace('static void original_refresh', 'static void focus_file(void *ctx,uint32_t id){(void)ctx;focus_id=id;}\nstatic void original_parent(void *ctx){(void)ctx;mark2_outer_type_text((const char *)(uintptr_t)0x4200b5e2,0,0x46);}\nstatic void original_refresh')
c=E/'cold-menu.c';c.write_text(header+s+prefix+body+(R/'cold_menu_body.c').read_text());commands=[]
for argv in [['gcc','-O1','-g','-I',str(S),'-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(c),str(S/'profile.c'),str(S/'mark2_import.c'),'-o',str(E/'cold-menu')],[str(E/'cold-menu')]]:
 q=subprocess.run(argv,capture_output=True,text=True);commands.append(dict(argv=argv,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=commands,source_SHA256=hashlib.sha256((S/'picker.c').read_bytes()).hexdigest()),indent=2)+'\n');print(q.stdout+q.stderr,flush=True)
 if q.returncode:raise SystemExit(q.returncode)
