"""Private format inputs are explicit, never embedded, downloaded or logged."""
import binascii,hashlib,json,struct
from pathlib import Path
import numpy as np
from .container import build,transform
from .readback import verify

ROOT=Path(__file__).resolve().parents[1]
CAPACITY=0x5820000
NAMES=('ex1990_051000.bi','_tpj01_0210.bin','eg1990_053200.bi','vr1990_010200.bi','_gst00_0017.bin','li1990_053200.bi')
def sha(b):return hashlib.sha256(b).hexdigest()
def read_material(tables_path,integrity_path):
    try:
        t=json.loads(Path(tables_path).read_text(encoding='utf-8'))
        rows=[bytes.fromhex(t[n])for n in ('T1','T2','T3')]
        k=bytes.fromhex(json.loads(Path(integrity_path).read_text(encoding='utf-8'))['K8'])
        if any(len(r)!=256 for r in rows)or len(k)!=8:raise ValueError()
    except (ValueError,TypeError,KeyError):raise ValueError('Private format material has an unsupported shape') from None
    return [np.frombuffer(r,dtype=np.uint8)for r in rows],k
def stock_modules(plain,k):
    body=plain[32:]
    if len(body)<256 or body[:32]!=b' '*32 or hashlib.sha1(body+k).digest()!=plain[:20]:raise ValueError('Original container integrity check failed')
    if struct.unpack_from('>II',body,32)!=(6,240)or body[40:48]!=bytes(8)or body[-14:]!=bytes(14):raise ValueError('Original directory shape')
    if binascii.crc_hqx(body[:-16],0)!=int.from_bytes(body[-16:-14],'big'):raise ValueError('Original container CRC')
    modules={};cursor=240
    for i,expected in enumerate(NAMES):
        pos=48+32*i;name=body[pos:pos+16].rstrip(b'\0').decode('ascii');off,n=struct.unpack_from('>II',body,pos+16)
        if name!=expected or off!=cursor or n<2 or off+n>len(body)-16 or body[pos+24:pos+32]!=bytes(8):raise ValueError('Original module layout')
        m=body[off:off+n]
        if binascii.crc_hqx(m[:-2],0)!=int.from_bytes(m[-2:],'big'):raise ValueError('Original module CRC')
        modules[name]=m;cursor=off+n
    if cursor!=len(body)-16:raise ValueError('Original extent')
    return modules
def operate(args):
    profile=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
    stock=args.stock.read_bytes()
    if sha(stock)!=profile['original_container_sha256']:raise ValueError('Only exact original Z9 5.32 container is supported')
    tables,k=read_material(args.tables,args.integrity_material)
    plain=transform(stock,tables);modules=stock_modules(plain,k)
    if sha(modules['eg1990_053200.bi'])!=profile['original_module_sha256']:raise ValueError('Original MAIN identity')
    if args.command=='pack':
        if args.output.exists()or args.output.is_symlink():raise ValueError('Output already exists')
        if args.output.resolve().is_relative_to(ROOT):raise ValueError('Keep generated firmware outside the repository')
        payload=args.payload.read_bytes()
        if sha(payload)!=profile['expected_payload_sha256']or len(payload)!=profile['expected_payload_bytes']:raise ValueError('Only frozen mark2 v11 payload can be packed')
        encoded,_=build(stock,payload,tables,k,modules)
    else:encoded=args.candidate.read_bytes()
    report,_=verify(encoded,tables,k,plain,modules,profile['expected_payload_sha256'],CAPACITY)
    if sha(encoded)!=profile['expected_container_sha256']or len(encoded)!=profile['expected_container_bytes']:raise ValueError('Candidate differs from frozen v11 container')
    if args.command=='pack':
        # No output is opened until independent readback and full identity pass.
        with args.output.open('xb')as f:f.write(encoded)
    return dict(passed=True,package_sha256=sha(encoded),package_bytes=len(encoded),payload_sha256=report['payload_SHA256'],all_module_CRCs_valid=True,other_five_modules_unchanged=True,device_qualified=False)
