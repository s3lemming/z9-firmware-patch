"""Current C importer, independent byte fixtures and no output commit on reject."""
import ctypes as C,hashlib,json,struct,subprocess
from pathlib import Path
import sys
R=Path(__file__).resolve().parent;S=R.parent/'firmware';E=Path(sys.argv[1]);E.mkdir();commands=[]
cmd=['gcc','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all',str(S/'mark2_import.c'),'-o',str(E/'import.so')];q=subprocess.run(cmd,capture_output=True,text=True);(E/'compile.json').write_text(json.dumps(dict(argv=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr),indent=2)+'\n');assert q.returncode==0,q.stderr
lib=C.CDLL(str(E/'import.so'));OPEN=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_char_p,C.POINTER(C.c_int));SIZE=C.CFUNCTYPE(C.c_int,C.c_void_p,C.POINTER(C.c_uint64));READ=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_void_p,C.c_uint32,C.POINTER(C.c_uint32));CLOSE=C.CFUNCTYPE(C.c_int,C.c_void_p);CANCEL=C.CFUNCTYPE(C.c_int,C.c_void_p)
class Ops(C.Structure):_fields_=[('open',OPEN),('size',SIZE),('read',READ),('close',CLOSE),('cancelled',CANCEL)]
class Info(C.Structure):_fields_=[('valid_bytes',C.c_uint32),('play_bytes',C.c_uint32),('frames',C.c_uint32),('rate',C.c_uint32),('channels',C.c_uint16),('bits',C.c_uint16)]
state={};rows=[]
@OPEN
def op_open(ctx,path,owned):state['pos']=0;state['closed']=False;owned[0]=1;return 0
@SIZE
def op_size(ctx,n):n[0]=len(state['blob']);return 0
@READ
def op_read(ctx,dst,n,actual):
 b=state['blob'][state['pos']:state['pos']+min(n,997)];C.memmove(dst,b,len(b));state['pos']+=len(b);actual[0]=len(b);return 0
@CLOSE
def op_close(ctx):state['closed']=True;return 0
ops=Ops(op_open,op_size,op_read,op_close,CANCEL());lib.m2_import.argtypes=[C.POINTER(Ops),C.c_void_p,C.c_char_p,C.c_void_p,C.c_uint32,C.POINTER(Info)]
def wav(n=288000,kind=1,channels=2,rate=48000,bits=16,align=4,byte_rate=192000):
 data=b'\x41'*n;fmt=struct.pack('<HHIIHH',kind,channels,rate,byte_rate,align,bits);body=b'WAVEfmt '+struct.pack('<I',16)+fmt+b'data'+struct.pack('<I',n)+data;return b'RIFF'+struct.pack('<I',len(body))+body
fixtures=[('exact_1p5s',wav(),0),('one_frame_below',wav(287996),0),('one_frame_over',wav(288004),11),('two_seconds',wav(384000),11),('IEEE_float',wav(kind=3),8),('extensible_PCM',wav(kind=0xfffe),8),('mono',wav(channels=1),8),('four_channels',wav(channels=4),8),('44100Hz',wav(rate=44100,byte_rate=176400),8),('96000Hz',wav(rate=96000,byte_rate=384000),8),('8bit',wav(bits=8),8),('24bit',wav(bits=24),8),('bad_alignment',wav(align=2),8),('bad_byte_rate',wav(byte_rate=192001),8),('empty_PCM',wav(0),8),('not_frame_aligned',wav(10),8),('MP3',b'ID3'+bytes(128),7),('AAC',b'\xff\xf1'+bytes(128),7),('truncated',wav()[:-1],7),('trailing_bytes',wav()+b'X',7)]
fixtures += [('short_'+str(n)+'_bytes',wav(n),0)for n in [4,192,9600,19200,96000,192000,262140,262144,262148]]
pcm=(C.c_uint8*288000)()
for name,blob,expected in fixtures:
 state['blob']=blob;out=Info();C.memset(C.byref(out),0x55,C.sizeof(out));prior=bytes(out);rc=lib.m2_import(C.byref(ops),None,b'A:\\CUSTOM_SOUND\\TEST.WAV',pcm,len(pcm),C.byref(out));assert rc==expected,(name,rc,expected);assert state['closed']
 if rc:assert bytes(out)==prior
 else:assert out.valid_bytes==len(blob)-44 and out.play_bytes<=288000 and out.frames<=72000
 rows.append(dict(name=name,expected_error=expected,actual_error=rc,closed=True,output_metadata_unchanged_on_reject=bool(rc),fixture_SHA256=hashlib.sha256(blob).hexdigest()))
(E/'result.json').open('x').write(json.dumps(dict(passed=True,cases=len(rows),rows=rows,source_SHA256=hashlib.sha256((S/'mark2_import.c').read_bytes()).hexdigest(),scope='Actual importer; separate picker test proves published PCM and stored configuration preserved'),indent=2)+'\n');print('MARK2_ACTUAL_FORMAT_DURATION_CORE_PASS',len(rows))
