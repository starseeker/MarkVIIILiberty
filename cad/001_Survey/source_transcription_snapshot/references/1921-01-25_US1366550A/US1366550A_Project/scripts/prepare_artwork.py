"""Conservative source-pixel cleanup and outline tracing. No synthesized linework.

Crop boxes are reviewed on 918 x 1188 renders of the supplied letter-size PDF.
Its displayed proportions are preserved; unequal source x/y sampling is not
interpreted as evidence for changing engineering geometry.
"""
from pathlib import Path
import os,json,hashlib,subprocess,shutil
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import fitz
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
SPECS=[
    dict(id='sheet1_figure1',page=1,box=[150,241,718,936]),
    dict(id='sheet1_signature',page=1,box=[510,941,760,1005]),
    dict(id='sheet2_figures2_3_signature',page=2,box=[174,234,774,1039]),
]
def main():
    trace=os.environ.get('POTRACE') or shutil.which('potrace')
    if not trace:raise SystemExit('Install potrace 1.16 or provide POTRACE.')
    source=fitz.open(ROOT/'sources/US-1366550-A.pdf');out=[]
    q=ROOT/'qa';q.mkdir(exist_ok=True)
    for a in SPECS:
        page=source[a['page']-1];px=fitz.Pixmap(source,page.get_images()[0][0])
        im=Image.frombytes('L',(px.width,px.height),px.samples)
        box=[round(v*([px.width/918,px.height/1188][i%2])) for i,v in enumerate(a['box'])]
        crop=im.crop(box);arr=np.asarray(crop)<128
        # The drawing and the last header line share a narrow horizontal band.
        # Remove only the header portion, whose type is recreated in Scribus.
        if a['id']!='sheet1_signature':
            cut_x=round(548*px.width/918)-box[0]
            cut_y=round(249*px.height/1188)-box[1]
            arr[:max(0,cut_y),max(0,cut_x):]=False
        labs,n=ndi.label(arr,np.ones((3,3),int));areas=np.bincount(labs.ravel());areas[0]=0
        # Delete only tiny isolated marks. Dotted paths, hatching, label fragments
        # and signature dots beside surviving detail remain in the bitmap.
        substantial=areas[labs]>=24
        dist=ndi.distance_transform_edt(~substantial)
        remove=(arr & (areas[labs]<=6) & (dist>14))
        cleaned=arr & ~remove
        clean=Image.fromarray(np.where(cleaned,0,255).astype('uint8')).convert('1')
        png=ROOT/'assets'/(a['id']+'.png');pbm=q/(a['id']+'.pbm');svg=ROOT/'assets'/(a['id']+'.svg')
        clean.save(png);clean.save(pbm)
        # No turd removal in the tracer: all retained dotted-line components count.
        subprocess.run([trace,str(pbm),'-s','-o',str(svg),'-t','0','-a','0.55','-O','0.1'],check=True)
        tree=etree.parse(str(svg));el=tree.getroot()
        width=(box[2]-box[0])*612/px.width;height=(box[3]-box[1])*792/px.height
        el.set('width',f'{width:.9f}pt');el.set('height',f'{height:.9f}pt')
        tree.write(str(svg),xml_declaration=True,encoding='UTF-8')
        compare=np.repeat(np.asarray(crop)[:,:,None],3,2).copy()
        compare[remove]=[240,50,50];Image.fromarray(compare).save(q/(a['id']+'_removed_pixels.png'))
        clean.convert('RGB').resize((round(width*2),round(height*2)),Image.Resampling.LANCZOS).save(q/(a['id']+'_clean_preview.png'))
        yy,xx=np.nonzero(cleaned)
        out.append(dict(**a,native_box=box,pixel_size=list(clean.size),x=box[0]*612/px.width,y=box[1]*792/px.height,width=width,height=height,ink_offset=[float(xx.min()*612/px.width),float(yy.min()*792/px.height)],removed_black_pixels=int(remove.sum()),original_black_pixels=int(arr.sum()),svg=svg.name,raster=png.name,sha256=hashlib.sha256(png.read_bytes()).hexdigest()))
    (ROOT/'data/artwork.json').write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
