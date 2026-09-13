#!/usr/bin/env python3
"""Render each new printed page with Poppler; verify complete PNGs before saving."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,io,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
P=R/'Handbook_Master_001-220_v11.pdf';out=R/'proofs/checkpoint11';out.mkdir(parents=True,exist_ok=True)
def render(n):
 raw=subprocess.check_output(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-r','144','-png',str(P)])
 im=Image.open(io.BytesIO(raw));im.load();p=out/f'page{n}.png';p.write_bytes(raw)
 return dict(page=n,path=p.relative_to(R).as_posix(),pixels=list(im.size),sha256=hashlib.sha256(raw).hexdigest())
with ThreadPoolExecutor(max_workers=2) as ex:rows=list(ex.map(render,range(201,221)))
result=dict(pdf=P.name,pdf_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),renderer='Poppler pdftoppm',dpi=144,pages=rows,errors=[])
(R/'data/render_validation.json').write_text(json.dumps(result,indent=2)+'\n');print('Rendered',len(rows),'pages',flush=True)
