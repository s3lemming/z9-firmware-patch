"""Execute the production gate with a synthetic instruction and ABI-clobbering stub."""
from pathlib import Path
import hashlib,json,os,struct,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from z9patch.restart import ordinary_restart_assembly
E=Path(sys.argv[1]);E.mkdir();commands=[]
for invalid in [True,-1,1<<32,'not-an-instruction']:
 try:ordinary_restart_assembly(invalid)
 except ValueError:pass
 else:raise AssertionError('Malformed gate input accepted')
def run(args):
 q=subprocess.run(args,capture_output=True,text=True);commands.append(dict(argv=args,exit=q.returncode,stdout=q.stdout,stderr=q.stderr));(E/'result.json').write_text(json.dumps(dict(passed=q.returncode==0,commands=commands,system_guest=False,scope='Synthetic displaced instruction and clobbering leaf; verifies gate ABI, not native scheduler timing or hardware acceptance'),indent=2)+'\n');print(q.stdout+q.stderr,end='',flush=True)
 if q.returncode:raise SystemExit(q.returncode)
# This authored ADD fixture differs from the original scheduler instruction.
(E/'fixture.S').write_text('.text\nadds x8,x22,x8\n')
run(['aarch64-linux-gnu-gcc','-c',str(E/'fixture.S'),'-o',str(E/'fixture.o')])
run(['aarch64-linux-gnu-objcopy','-O','binary','--only-section=.text',str(E/'fixture.o'),str(E/'fixture-code')])
word=struct.unpack('<I',(E/'fixture-code').read_bytes())[0]
asm=['.text','.global run_hook','run_hook:','sub sp,sp,#96']
pairs=[(19,20),(21,22),(23,24),(25,26),(27,28),(29,30)]
asm += [f'stp x{i},x{j},[sp,#{k*16}]'for k,(i,j)in enumerate(pairs)]
asm += ['adrp x0,sp_before','add x0,x0,:lo12:sp_before','mov x1,sp','str x1,[x0]',
        'mov x9,#0xa0000000','msr nzcv,x9','adrp x30,original','add x30,x30,:lo12:original']
asm += [f'ldp x{i},x{i+1},[x30,#{i*8}]'for i in range(0,30,2)]+['ldr x30,[x30,#240]','b hook_ordinary_restart']
asm += ordinary_restart_assembly(word)
asm += ['m2_ordinary_restart_required:']+[f'mov x{i},#0x777'for i in range(19)]
asm += ['adds x9,x9,#1','adrp x16,decision','ldr w0,[x16,:lo12:decision]','ret']
for label,route in [('ordinary_restart_continue',0),('ordinary_restart_stop_native',1)]:
 asm += [label+':','sub sp,sp,#256']+[f'stp x{i},x{i+1},[sp,#{i*8}]'for i in range(0,30,2)]+['str x30,[sp,#240]',
   'mrs x2,nzcv','adrp x1,observed_flags','str x2,[x1,:lo12:observed_flags]',
   'add x2,sp,#256','adrp x1,sp_after','str x2,[x1,:lo12:sp_after]',
   'adrp x3,observed','add x3,x3,:lo12:observed']
 for i in range(0,30,2):asm += [f'ldp x0,x1,[sp,#{i*8}]',f'stp x0,x1,[x3,#{i*8}]']
 asm += ['ldr x0,[sp,#240]','str x0,[x3,#240]',f'mov w0,#{route}','adrp x1,taken','str w0,[x1,:lo12:taken]','add sp,sp,#256']
 asm += [f'ldp x{i},x{j},[sp,#{k*16}]'for k,(i,j)in enumerate(pairs)]+['add sp,sp,#96','ret']
(E/'gate.S').write_text('\n'.join(asm)+'\n')
(E/'main.c').write_text(r'''
#include <stdint.h>
#include <stdio.h>
#include <assert.h>
uint64_t original[31],observed[31],observed_flags,sp_before,sp_after;
unsigned decision,taken;extern void run_hook(void);
int main(void){unsigned cases=0;
 const uint64_t operands[4][2]={{0,0},{UINT64_MAX,1},{0x7fffffffffffffffULL,1},{0x123456789abcULL,0xfedcba}};
 for(decision=0;decision<2;decision++)for(unsigned v=0;v<4;v++){
  for(unsigned i=0;i<31;i++)original[i]=0x1234000000000000ULL+i*0x101;
  original[22]=operands[v][0];original[8]=operands[v][1];run_hook();
  uint64_t a=original[22],b=original[8],sum=a+b;
  unsigned flags=((sum>>63)<<3)|((sum==0)<<2)|((sum<a)<<1)|((~(a^b)&(a^sum))>>63);
  for(unsigned i=0;i<31;i++)assert(observed[i]==(!decision&&i==8?sum:original[i]));
  assert(observed_flags==((uint64_t)(decision?10:flags)<<28));
  assert(sp_before==sp_after&&!(sp_before&15)&&taken==decision);cases++;
 }
 printf("RESTART_AARCH64_ABI_PASS cases=%u registers=X0-X30 NZCV=checked SP=aligned_and_restored paths=both\n",cases);
}
''')
run(['aarch64-linux-gnu-gcc','-O2','-Wall','-Wextra','-Werror','-static',str(E/'main.c'),str(E/'gate.S'),'-o',str(E/'test')])
run([os.environ.get('QEMU_AARCH64','qemu-aarch64'),str(E/'test')])
