"""Build frozen mark2 v11 from a user-supplied original Z9 5.32 MAIN.

The source tree contains no original instruction words or menu resources.
Any displaced instruction/resource is read locally from the exact checked input.
"""
import binascii, hashlib, json, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_MODULE='979fc8c5a46b3be8a998d5defb8be916d766ef85428744ba0bc47a1cb0ba9a66'
EXPECTED_PAYLOAD='9184a62c803d1d47ca18f11e244b848150287927c6db25ba00385e087a826f91'
def build(module,output):
    if not __debug__: raise ValueError('Optimized Python disables internal checks; use normal Python')
    if Path(output).is_symlink(): raise ValueError('Build directory must not be a link')
    module=Path(module).resolve();O=Path(output).resolve()
    if O.exists(): raise ValueError('Build directory must be new')
    if O.is_relative_to(ROOT): raise ValueError('Keep private build output outside the repository')
    if hashlib.sha256(module.read_bytes()).hexdigest()!=EXPECTED_MODULE: raise ValueError('Only the exact original Z9 5.32 MAIN module is supported')
    manifest=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
    for name,expected in manifest['authored_source_sha256'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=expected: raise ValueError('Source differs from frozen v11: '+name)
    O.mkdir(parents=True);patches=[];commands=[]
    def sha(b):return hashlib.sha256(b).hexdigest()
    raw=module.read_bytes();assert sha(raw)=='979fc8c5a46b3be8a998d5defb8be916d766ef85428744ba0bc47a1cb0ba9a66'
    orig=raw[:-2];b=bytearray(orig);BASE=0x40160000;ENTRY=0x44f6c000;patches=[];commands=[]
    source=ROOT/'firmware/adapter.c'
    for n in ['adapter.c','picker.c','mark2_import.c','mark2_import.h','mark2_native_file.c','profile.h','profile.c','profile_native.c','runtime.c']:(O/n).write_bytes((source.parent/n).read_bytes())


    def run(args):
     q=subprocess.run(args,cwd=O,capture_output=True,text=True);commands.append(dict(argv=args,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));(O/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8');assert q.returncode==0,q.stderr;return q.stdout
    def off(a):return a-0x9fdd0b000 if 0xa02808000<=a<0xa02acf000 else a-BASE
    def patch(a,new,why):
     p=off(a);old=orig[p:p+len(new)];assert len(old)==len(new) and b[p:p+len(new)]==old
     b[p:p+len(new)]=new;patches.append(dict(VA=hex(a),input_space='ROM or proven initialized RAM',offset=hex(p),original_SHA256=sha(old),replacement_SHA256=sha(new),bytes=len(new),consumer=why))
    def branch(a,target):
     delta=target-a;assert delta%4==0 and -(1<<27)<=delta<(1<<27);return struct.pack('<I',0x14000000|((delta//4)&0x3ffffff))

    def append(blob,align=16):
     b.extend(bytes(-len(b)%align));p=len(b);b.extend(blob);return BASE+p
    rows=orig[0x431897a4-BASE:0x431897a4-BASE+5*44];new=bytearray(rows[-44:]);struct.pack_into('<H',new,0,0xc86);struct.pack_into('<I',new,24,0x7e20)
    rp=append(rows+new);ep=append(orig[0x43189880-BASE:0x43189880-BASE+40]+21*orig[0x43189880-BASE:0x43189880-BASE+8])
    patch(0xa028d29c0,struct.pack('<Q',rp),'Sound rows: five originals byte-identical plus Load WAV from card')
    patch(0xa028d29c8,struct.pack('<Q',ep),'26 original-compatible event bindings; 20 displayed files')
    patch(0xa028d29d0,struct.pack('<H',6),'Initial six sound rows; scanned filenames published by native task')
    for pc in [0xa028d29d8,0xa028d29e0]:patch(pc,struct.pack('<H',416),'Bound native scrolling list rectangle')
    classes=orig[0x426f3b25-BASE:0x426f3b25-BASE+0xc84];cp=append(classes+23*classes[0x93e:0x93f],1)
    words=memoryview(orig[:0x13c0000]).cast('I');sites=[]
    for i,w in enumerate(words):
     if w&0xff800000!=0xd2800000 or(w>>5)&0xffff!=0x3b25:continue
     reg=w&31;value=(w>>5)&0xffff;pcs=[BASE+i*4]
     for j in range(i+1,min(i+10,len(words))):
      n=words[j]
      if n&0xff80001f==0xf2800000|reg:
       shift=((n>>21)&3)*16;value=(value&~(0xffff<<shift))|(((n>>5)&0xffff)<<shift);pcs.append(BASE+j*4)
       if shift==48:break
     if value!=0x426f3b25:continue
     sites.append(pcs)
     for pc in pcs:
      word=struct.unpack_from('<I',orig,pc-BASE)[0];shift=((word>>21)&3)*16
      patch(pc,struct.pack('<I',(word&~(0xffff<<5))|(((cp>>shift)&0xffff)<<5)),'Extended label classifier; original entries unchanged')
    assert sites
    api=struct.unpack_from('<I',orig,0x40e355fc-BASE)[0]
    call=struct.unpack_from('<I',orig,0x40e355c4-BASE)[0];assert call&0xfc000000==0x94000000 and 0x40e355c4+((call&0x3ffffff)<<2)==0x40e355fc
    asm=['.section .text.hooks,"ax"']
    for name,func,pc,word in [('api','m2_api',0x40e355fc,api),('pcm','m2_pcm',0x40d25dd0,struct.unpack_from('<I',orig,0x40d25dd0-BASE)[0])]:
     assert struct.unpack_from('<I',orig,pc-BASE)[0]==word
     asm += [f'.global hook_{name}',f'hook_{name}:','sub sp,sp,#96','stp x0,x1,[sp]','stp x2,x3,[sp,#16]','stp x4,x5,[sp,#32]','stp x6,x7,[sp,#48]','str x30,[sp,#64]','mov x0,sp',f'bl {func}',*(['cbnz w0,api_rejected']if name=='api'else []),'ldp x0,x1,[sp]','ldp x2,x3,[sp,#16]','ldp x4,x5,[sp,#32]','ldp x6,x7,[sp,#48]',*(['bl original_api','str x0,[sp,#72]','mov x0,sp','bl m2_api_result','ldr x0,[sp,#72]','ldr x30,[sp,#64]','add sp,sp,#96','ret']if name=='api'else ['ldr x30,[sp,#64]','add sp,sp,#96',f'.inst {word}',f'b continue_{name}'])]
    for name,func,pc,word in [('flags','m2_flags',0x40f9f758,struct.unpack_from('<I',orig,0x40f9f758-BASE)[0]),('terminal','m2_terminal',0x40f9ff2c,struct.unpack_from('<I',orig,0x40f9ff2c-BASE)[0]),('fast_timer','m2_fast_timer',0x40f9fdf0,struct.unpack_from('<I',orig,0x40f9fdf0-BASE)[0])]:
     assert struct.unpack_from('<I',orig,pc-BASE)[0]==word
     asm += [f'.global hook_{name}',f'hook_{name}:','stp x0,x30,[sp,#-16]!',*(['mov x0,x30']if name=='terminal'else []),f'bl {func}','mov w9,w0','ldp x0,x30,[sp],#16','cbnz w9,1f',f'.inst {word}',f'b continue_{name}','1: ret']

    for name,func,pc in [('composite','m2_composite',0x40fa0130),('cxx_stop','m2_cxx_stop',0x40fa0198)]:
     word=struct.unpack_from('<I',orig,pc-BASE)[0]
     asm += [f'.global hook_{name}',f'hook_{name}:','sub sp,sp,#80','stp x0,x1,[sp]','stp x2,x3,[sp,#16]','stp x4,x5,[sp,#32]','stp x6,x7,[sp,#48]','str x30,[sp,#64]',f'bl {func}','ldp x0,x1,[sp]','ldp x2,x3,[sp,#16]','ldp x4,x5,[sp,#32]','ldp x6,x7,[sp,#48]','ldr x30,[sp,#64]','add sp,sp,#80',f'.inst {word}',f'b continue_{name}']
    # Input identity is checked before reading any displaced instruction.
    asm += ['.global hook_current','hook_current:','sub sp,sp,#128','stp x0,x1,[sp]','stp x2,x3,[sp,#16]','stp x4,x5,[sp,#32]','stp x6,x7,[sp,#48]','str x30,[sp,#64]','mov x0,sp','bl m2_frame_snapshot','ldp x0,x1,[sp]','ldp x2,x3,[sp,#16]','ldp x4,x5,[sp,#32]','ldp x6,x7,[sp,#48]','bl native_submit','str x0,[sp,#72]','mov x0,sp','bl m2_frame_commit','ldr x0,[sp,#72]','ldr x30,[sp,#64]','add sp,sp,#128','ret']

    asm+=['api_rejected:','ldr x30,[sp,#64]','add sp,sp,#96','mov w0,wzr','ret',
     '.global original_api','original_api:',f'.inst {api}','b continue_api']
    for i in range(64):
     asm += [f'.global notice_slot_{i}',f'notice_slot_{i}:','mov x2,x1','mov w1,w0',f'mov w0,#{i}','b m2_notice_slot']
    asm += ['.section .rodata.callbacks,"a"','.balign 8','.global callback_slots','callback_slots:']
    asm += [f'.quad notice_slot_{i}'for i in range(64)]
    label_word=struct.unpack_from('<I',orig,0x4032e57c-BASE)[0]
    asm += ['.section .text.labels,"ax"','.global mark2_discovery_label','mark2_discovery_label:',
     'cmp w1,#0xc86','b.lo 3f','cmp w1,#0xc9b','b.lo mark2_picker_label','3:',
     f'.inst {label_word}','b native_text_continue']
    (O/'hooks.S').write_text('\n'.join(asm)+'\n')
    (O/'layout.ld').write_text('native_text_continue = 0x4032e580; native_submit = 0x40f96a20; continue_composite = 0x40fa0134; continue_cxx_stop = 0x40fa019c; continue_api = 0x40e35600; continue_pcm = 0x40d25dd4; continue_flags = 0x40f9f75c; continue_terminal = 0x40f9ff30; continue_fast_timer = 0x40f9fdf4; SECTIONS { . = 0x44f6c000; .text : { *(.text*) } .rodata : { *(.rodata*) } /DISCARD/ : { *(.comment) *(.eh_frame*) *(.note*) } }\n')
    flags=['-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-mgeneral-regs-only','-mstrict-align','-fno-pic','-march=armv8-a','-mno-outline-atomics']

    for unit in ['picker','mark2_import','mark2_native_file','profile','profile_native','runtime']:run(['aarch64-linux-gnu-gcc',*flags,'-c',unit+'.c','-o',unit+'.o'])
    run(['aarch64-linux-gnu-gcc',*flags,'-c','adapter.c','-o','adapter.o']);run(['aarch64-linux-gnu-gcc','-c','hooks.S','-o','hooks.o']);run(['aarch64-linux-gnu-ld','--build-id=none','-T','layout.ld','adapter.o','hooks.o','picker.o','mark2_import.o','mark2_native_file.o','profile.o','profile_native.o','runtime.o','-o','adapter.elf']);assert not run(['aarch64-linux-gnu-nm','-u','adapter.elf']).strip()
    syms={v[2]:int(v[0],16)for line in run(['aarch64-linux-gnu-nm','-n','adapter.elf']).splitlines()if len(v:=line.split())==3}
    run(['aarch64-linux-gnu-objcopy','-O','binary','adapter.elf','adapter.bin']);dis=run(['aarch64-linux-gnu-objdump','-d','adapter.elf']);(O/'adapter-disassembly.txt').write_text(dis,encoding='utf-8')
    code=(O/'adapter.bin').read_bytes();end=(ENTRY+len(code)+4095)&~4095
    assert len(orig)+BASE<ENTRY and end<0x45980000
    b.extend(bytes(ENTRY-BASE-len(b)));b.extend(code)
    call2=struct.unpack_from('<I',orig,0x40e35764-BASE)[0];assert call2&0xfc000000==0x94000000
    for pc,name in [(0x40e355fc,'api'),(0x40d25dd0,'pcm'),(0x40f9f758,'flags'),(0x40f9ff2c,'terminal'),(0x40f9fdf0,'fast_timer')]:patch(pc,branch(pc,syms['hook_'+name]),name+' native adapter, original displaced instruction replayed')
    for pc,name in [(0x40fa0130,'composite'),(0x40fa0198,'cxx_stop')]:patch(pc,branch(pc,syms['hook_'+name]),'Composite-route bounded frame audio '+name+'; original entry instruction replayed')
    target=syms['hook_current'];pc=0x40f73ea0
    patch(pc,struct.pack('<I',0x94000000|(((target-pc)//4)&0x3ffffff)),'Original current-frame BL redirected through snapshot/native submit/audio-commit wrapper; history BL unchanged')
    assert orig[off(0xa02ac5010):off(0xa02ac5010)+32]==struct.pack('<IIQQQ',1,15,0xa02acf000,0xa02acf000,0)
    patch(0xa02ac5010,struct.pack('<IIQQQ',2,15,ENTRY,end,ENTRY),'Explicit RX map for authored integration code')
    patch(0xa02ac50e0,struct.pack('<Q',ENTRY),'Original resource RO region ends before explicit RX')
    size=struct.unpack_from('<Q',orig,off(0x401680e8))[0];assert 0xa02b15000+size==0xa04e3d000
    assert (0xa04e3d000+8192+16383)&~16383==0xa04e40000
    patch(0x401680e8,struct.pack('<Q',size+8192),'Native startup private BSS +8192; original TTBR alignment unchanged')
    for pc in [0x431c1ff8,0x431c2018,0x431c20b8]:
     assert struct.unpack_from('<Q',orig,off(pc))[0]==0x405a57e0
     patch(pc,struct.pack('<Q',syms['mark2_discovery_submit']),'All native Type menu submit events -> file/native selector, original handler retained')
    assert struct.unpack_from('<Q',orig,off(0xa028f42d8))[0]==0x405a575c
    patch(0xa028f42d8,struct.pack('<Q',syms['mark2_sound_refresh']),'Native type refresh followed by selected filename highlight')
    # Displaced text instruction was read from the user input above.
    patch(0x4032e57c,branch(0x4032e57c,syms['mark2_discovery_label']),'Custom labels only; original text resolver instruction replayed')
    patch(0x405a5584,struct.pack('<I',0x94000000|(((syms['mark2_outer_type_text']-0x405a5584)//4)&0x3ffffff)),'Only outer Camera sounds Type text: CUS when custom selected, native enum unchanged')
    b.extend(b'Ver.05.32.00\0');payload=O/'payload.bin'
    assert sha(b)==EXPECTED_PAYLOAD, 'Compiler output differs from frozen v11; no final payload/module written'
    payload.write_bytes(b)
    module_bytes=bytes(b)+struct.pack('>H',binascii.crc_hqx(b,0))
    (O/'eg1990_053200.bi').write_bytes(module_bytes)

    result=dict(feature='mark2-v11',input_module_sha256=sha(raw),payload_sha256=sha(b),payload_bytes=len(b),module_sha256=sha(module_bytes),module_bytes=len(module_bytes),patches=patches,compiler=run(['aarch64-linux-gnu-gcc','--version']).splitlines()[0],device_qualified=False)
    (O/'build-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result
