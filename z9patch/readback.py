"""Separate parser/CRC implementation. Never calls the package builder."""
import hashlib,struct
import numpy as np

def sha(b):return hashlib.sha256(b).hexdigest()

_crc=[]
for i in range(256):
    value=i<<8
    for _ in range(8):value=((value<<1)^0x1021 if value&0x8000 else value<<1)&65535
    _crc.append(value)

def crc16(data):
    value=0
    for octet in data:value=((value<<8)^_crc[(value>>8)^octet])&65535
    return value

def decode(data,tables):
    out=bytearray(data)
    for pos in range(64,len(out),262144):
        end=min(pos+262144,len(out));j=np.arange(pos,end,dtype=np.uint32)-32
        block=np.frombuffer(data[pos:end],dtype=np.uint8).copy()
        block^=tables[2][(j//65536)%256]
        block^=tables[1][(j//256)%256]
        block^=tables[0][j%256]
        out[pos:end]=block.tobytes()
    return bytes(out)

def verify(encoded,tables,k8,stock_plain,modules,payload_SHA256,capacity):
    decoded=decode(encoded,tables);body=decoded[32:]
    if decoded[20:32]!=stock_plain[20:32]or body[:32]!=b' '*32:raise ValueError('fixed header')
    if hashlib.sha1(body+k8).digest()!=decoded[:20]:raise ValueError('header SHA1')
    if len(body)<256 or body[-14:]!=bytes(14):raise ValueError('tail padding')
    if crc16(body[:-16])!=int.from_bytes(body[-16:-14],'big'):raise ValueError('package CRC16')
    count,first=struct.unpack_from('>II',body,32)
    if(count,first)!=(6,240)or body[40:48]!=bytes(8):raise ValueError('directory shape')
    cursor=first;rows=[];seen=set();payload=None
    for index in range(count):
        pos=48+32*index;name=body[pos:pos+16].rstrip(b'\0').decode('ascii')
        off,size=struct.unpack_from('>II',body,pos+16)
        if name not in modules or name in seen:raise ValueError('module names')
        if name=='eg1990_053200.bi'and size>capacity:raise ValueError('EG capacity')
        if off!=cursor or size<2 or off+size>len(body)-16 or body[pos+24:pos+32]!=bytes(8):raise ValueError('module bounds')
        module=body[off:off+size]
        if crc16(module[:-2])!=int.from_bytes(module[-2:],'big'):raise ValueError('module CRC16')
        if name=='eg1990_053200.bi':
            if module[-15:-2]!=b'Ver.05.32.00\0'or module[-11:-3]!=b'05.32.00':raise ValueError('EG updater terminal version')
            payload=module[:-2]
            if sha(payload)!=payload_SHA256:raise ValueError('tested payload identity')
        elif module!=modules[name]:raise ValueError('non-EG module identity')
        rows.append(dict(name=name,body_offset=off,module_bytes=size,module_SHA256=sha(module),CRC16=module[-2:].hex()))
        cursor=off+size;seen.add(name)
    if cursor!=len(body)-16 or len(seen)!=6 or payload is None:raise ValueError('complete body extent')
    return dict(passed=True,modules=rows,header_SHA1=decoded[:20].hex(),package_CRC16=body[-16:-14].hex(),payload_SHA256=sha(payload),payload_bytes=len(payload),package_bytes=len(encoded),package_SHA256=sha(encoded),every_package_byte_accounted=True),payload
