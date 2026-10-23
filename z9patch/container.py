"""Offline Nikon 5.32 container construction; no device interfaces.

Newly authored container reconstruction. All original bytes and private format
material are provided locally by the user and are never distributed here.
"""
import binascii, hashlib, struct
import numpy as np

def sha(data):
    return hashlib.sha256(data).hexdigest()

def transform(data, tables):
    """Nikon XOR, body index starts at container+32; first64 bytes stay plain."""
    out=bytearray(data)
    source=np.frombuffer(data,dtype=np.uint8)
    target=np.frombuffer(out,dtype=np.uint8)
    for start in range(64,len(data),1048576):
        end=min(start+1048576,len(data));index=np.arange(start-32,end-32,dtype=np.uint32)
        target[start:end]=source[start:end]^tables[0][index&255]^tables[1][index>>8&255]^tables[2][index>>16&255]
    return bytes(out)

def build(stock,payload,tables,k8,original_modules):
    plain=transform(stock,tables);body=plain[32:]
    assert plain[32:64]==b' '*32
    assert hashlib.sha1(body+k8).digest()==plain[:20]
    assert binascii.crc_hqx(body[:-16],0)==int.from_bytes(body[-16:-14],'big')
    assert body[-14:]==bytes(14)
    count,directory=struct.unpack_from('>II',body,32);assert(count,directory)==(6,240)
    out=bytearray(body[:directory]);cursor=directory;rows=[];old_end=directory
    for index in range(count):
        pos=48+index*32;name=body[pos:pos+16].rstrip(b'\0').decode('ascii')
        start,length=struct.unpack_from('>II',body,pos+16)
        assert start==old_end and length>=2 and start+length<=len(body)-16
        original=body[start:start+length];assert original==original_modules[name]
        assert binascii.crc_hqx(original[:-2],0)==int.from_bytes(original[-2:],'big')
        replacement=payload+struct.pack('>H',binascii.crc_hqx(payload,0))if name=='eg1990_053200.bi'else original
        assert len(replacement)<2**32 and cursor<2**32
        struct.pack_into('>II',out,pos+16,cursor,len(replacement));out.extend(replacement)
        rows.append(dict(name=name,original_body_offset=start,body_offset=cursor,original_bytes=length,bytes=len(replacement),SHA256=sha(replacement),original_SHA256=sha(original),CRC16=replacement[-2:].hex(),unchanged=replacement==original))
        cursor+=len(replacement);old_end=start+length
    assert old_end==len(body)-16 and sum(x['unchanged']for x in rows)==5
    out.extend(struct.pack('>H',binascii.crc_hqx(out,0))+bytes(14))
    rebuilt=hashlib.sha1(out+k8).digest()+plain[20:32]+out
    encoded=transform(rebuilt,tables)
    return encoded,dict(module_rows=rows,package_CRC16=out[-16:-14].hex(),header_SHA1=rebuilt[:20].hex(),fixed_header_exact=rebuilt[20:32]==plain[20:32])
