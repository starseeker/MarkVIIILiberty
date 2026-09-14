#!/usr/bin/env python3
"""Export candidate SVGs and make visually comparable, unresampled PDF masters."""
from pathlib import Path
import concurrent.futures,json,subprocess,tempfile
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parent;R=ROOT/'restoration'

def export(n):
    src=R/'vector'/f'p{n}-restored.svg'
    with tempfile.TemporaryDirectory(prefix='snl-svg-export-') as tmp:
        out=Path(tmp)/'vector.pdf'
        cp=subprocess.run(['inkscape',str(src),'--export-type=pdf','--export-filename='+str(out)],capture_output=True)
        if cp.returncode:raise RuntimeError(cp.stderr.decode())
        data=out.read_bytes();assert data.rstrip().endswith(b'%%EOF')
        (R/'vector'/f'p{n}-restored.pdf').write_bytes(data)
    d=fitz.open(stream=data,filetype='pdf');w,h=Image.open(R/'clean'/f'p{n}-clean.png').size
    assert len(d)==1 and abs(d[0].rect.width/w-.75)<.001
    d[0].get_pixmap(matrix=fitz.Matrix(4/3,4/3)).save(R/'review'/f'p{n}-vector-preview.png')
    print('Exported',n,flush=True)

def main():
    manifest=json.loads((R/'manifest.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(export,[n for n,r in manifest.items() if r.get('vector')]))
    # Native-pixel PDF wrappers for all clean rasters. No JPEG compression.
    for n,r in manifest.items():
        d=fitz.open();w,h=r['pixel_size'];p=d.new_page(width=w*.75,height=h*.75)
        p.insert_image(p.rect,filename=str(ROOT/r['clean']))
        (R/'clean'/f'p{n}-clean.pdf').write_bytes(d.tobytes(deflate=True));d.close()
    print('All 31 raster PDF masters exported.',flush=True)

if __name__=='__main__':main()
