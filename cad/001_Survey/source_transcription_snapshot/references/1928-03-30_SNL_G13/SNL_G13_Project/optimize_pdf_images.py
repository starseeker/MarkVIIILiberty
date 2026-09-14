from pathlib import Path
import fitz,io,struct,hashlib,sys,json
from PIL import Image
p=Path(sys.argv[1]);d=fitz.open(p);out=[]
for x in range(1,d.xref_length()):
 if d.xref_get_key(x,'Subtype')[1]!='/Image':continue
 if d.xref_get_key(x,'BitsPerComponent')[1]!='8':continue
 cs=d.xref_get_key(x,'ColorSpace')[1];channels={'/DeviceRGB':3,'/DeviceGray':1}.get(cs)
 if not channels:continue
 w=int(d.xref_get_key(x,'Width')[1]);h=int(d.xref_get_key(x,'Height')[1]);raw=d.xref_stream(x)
 if len(raw)!=w*h*channels:continue
 bio=io.BytesIO();Image.frombytes('RGB' if channels==3 else 'L',(w,h),raw).save(bio,format='PNG',optimize=True)
 data=bio.getvalue();pos=8;idat=[]
 while pos<len(data):
  size=int.from_bytes(data[pos:pos+4],'big');tag=data[pos+4:pos+8]
  if tag==b'IDAT':idat.append(data[pos+8:pos+8+size])
  pos+=size+12
 encoded=b''.join(idat);before=len(d.xref_stream_raw(x))
 if len(encoded)>=before:continue
 d.update_stream(x,encoded,compress=False);d.xref_set_key(x,'Filter','/FlateDecode');d.xref_set_key(x,'DecodeParms',f'<< /Predictor 15 /Colors {channels} /BitsPerComponent 8 /Columns {w} >>')
 assert d.xref_stream(x)==raw
 out.append({'xref':x,'before':before,'after':len(encoded),'decoded_sha256':hashlib.sha256(raw).hexdigest()})
old=p.stat().st_size;new=d.tobytes(garbage=4,deflate=True);d.close();p.write_bytes(new)
print(p.name,old,len(new),'saved MB',(old-len(new))/1e6,flush=True)
Path(str(p)+'.lossless.json').write_text(json.dumps({'decoded_pixels_identical':True,'old_bytes':old,'new_bytes':len(new),'streams':out},indent=2))
