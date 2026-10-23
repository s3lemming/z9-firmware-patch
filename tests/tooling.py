"""Synthetic container checks and fail-closed command tests; no vendor fixtures."""
import binascii,hashlib,json,struct,subprocess,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from z9patch.container import build,transform
from z9patch.readback import verify,crc16,decode
from z9patch.packaging import NAMES,stock_modules,read_material
from z9patch.builder import build as build_module
E=Path(sys.argv[1]);E.mkdir();cases=0
def reject(fn):
    global cases
    try:fn()
    except (ValueError,AssertionError,UnicodeError,struct.error):cases+=1;return
    raise AssertionError('Malformed input accepted')
tables=[np.array([(i*m+7)%256 for i in range(256)],dtype=np.uint8)for m in (3,5,7)]
k=hashlib.sha256(b'synthetic test material only').digest()[:8]
modules={n:(('fixture-%d'%i).encode()+b'Ver.05.32.00\0')for i,n in enumerate(NAMES)}
modules={n:v+struct.pack('>H',binascii.crc_hqx(v,0))for n,v in modules.items()}
body=bytearray(b' '*32+struct.pack('>II',6,240)+bytes(200));cursor=240
for i,(n,v)in enumerate(modules.items()):
    body[48+32*i:64+32*i]=n.encode().ljust(16,b'\0');struct.pack_into('>II',body,64+32*i,cursor,len(v));body.extend(v);cursor+=len(v)
body.extend(struct.pack('>H',binascii.crc_hqx(body,0))+bytes(14))
plain=hashlib.sha1(body+k).digest()+bytes(12)+body;stock=transform(plain,tables)
assert decode(stock,tables)==plain and stock_modules(plain,k)==modules;cases+=1
payload=b'authored synthetic replacement'+b'Ver.05.32.00\0';digest=hashlib.sha256(payload).hexdigest()
encoded,_=build(stock,payload,tables,k,modules)
r,out=verify(encoded,tables,k,plain,modules,digest,4096);assert r['passed']and out==payload;cases+=1
assert crc16(b'123456789')==0x31c3;cases+=1
for off in (0,20,64,100,len(encoded)-1):
    altered=bytearray(encoded);altered[off]^=1
    reject(lambda:verify(altered,tables,k,plain,modules,digest,4096))
reject(lambda:verify(encoded[:-1],tables,k,plain,modules,digest,4096))
reject(lambda:verify(encoded,tables,k,plain,modules,digest,1))
reject(lambda:verify(encoded,tables,k,plain,modules,'0'*64,4096))
bad=E/'wrong-module.bi';bad.write_bytes(b'synthetic wrong input')
reject(lambda:build_module(bad,E/'must-not-exist'));assert not(E/'must-not-exist').exists()
reject(lambda:build_module(bad,E))
material=E/'invalid-material.json';material.write_text('{}',encoding='utf-8')
reject(lambda:read_material(material,material))
for args in (['build','--module',str(bad),'--output',str(E/'cli-output')],['pack','--stock',str(bad),'--tables',str(material),'--integrity-material',str(material),'--payload',str(bad),'--output',str(E/'package.bin')]):
    q=subprocess.run([sys.executable,'-B',str(ROOT/'patch.py'),*args],capture_output=True,text=True)
    assert q.returncode!=0 and 'Traceback'not in q.stderr;cases+=1
assert not(E/'cli-output').exists()and not(E/'package.bin').exists()
(E/'result.json').write_text(json.dumps(dict(passed=True,cases=cases,fixtures='synthetic only'),indent=2)+'\n',encoding='utf-8')
print('TOOLING_PASS cases='+str(cases))
