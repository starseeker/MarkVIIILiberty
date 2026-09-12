#!/usr/bin/env python3
"""Reproducible tonal cleanup and optional layered outline tracing.

Inputs are the accepted geometry assets, never the source JPEGs. No geometric
resampling, inferred text, AI generation, or drawing reconstruction is performed.
The only interpolation in tracing is a 3x sampling grid for subpixel contours.
"""
from pathlib import Path
import argparse, base64, hashlib, io, json, os, shutil, subprocess, tempfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.interpolate import griddata

ROOT=Path(__file__).resolve().parent
DEST=ROOT/'restoration'
CFG=json.loads((DEST/'config.json').read_text())
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def save_png(image,path):
    # Encode before writing: the workspace-backed filesystem needs one write.
    data=io.BytesIO();image.save(data,format='PNG',optimize=True)
    path.write_bytes(data.getvalue())

def region_mask(size, polygons):
    w,h=size; im=Image.new('L',size);d=ImageDraw.Draw(im)
    for polygon in polygons:
        d.polygon([(round(x*w),round(y*h)) for x,y in polygon],fill=255)
    return np.array(im)>0

def paper_field(g, exclude, valid):
    h,w=g.shape;step=60;pts=[];vals=[]
    for y in range(0,h,step):
        for x in range(0,w,step):
            a=g[y:y+step,x:x+step]
            v=a[(~exclude[y:y+step,x:x+step])&valid[y:y+step,x:x+step]]
            if len(v)>160:
                pts.append((x+step/2,y+step/2));vals.append(float(np.quantile(v,.90)))
    if len(vals)<4:
        return np.full(g.shape,float(np.quantile(g[valid],.90)))
    yy,xx=np.indices(g.shape)
    nearest=griddata(pts,vals,(xx,yy),method='nearest')
    try:
        field=griddata(pts,vals,(xx,yy),method='linear')
        field=np.where(np.isfinite(field),field,nearest)
    except Exception:field=nearest
    return np.clip(nd.gaussian_filter(field,35),np.quantile(vals,.15),np.quantile(vals,.90))

def clean(n):
    cfg=CFG[n];src=ROOT/'assets'/f'p{n}-geometry.png'
    im=Image.open(src).convert('RGB');rgb=np.array(im)
    raw=np.asarray(im.convert('L')).astype(float)/255
    # Very mild grain suppression. No sharpening or super-resolution.
    paired=cfg.get('paired_reverse_field')
    if paired:
        reverse=np.load(ROOT/paired)['reverse_ink_fraction']
        assert reverse.shape==raw.shape
        # Multiplicative attenuation correction retains dark front ink. Only the
        # reverse reference was registered; these front pixels are not moved.
        working=np.clip(raw/np.maximum(1-reverse,.65),0,1)
    else:working=raw
    g=nd.gaussian_filter(working,.35)
    # Artificial padding from earlier geometric rectification is not plate ink.
    padding=np.all(rgb==[248,246,239],axis=2)
    valid=(nd.distance_transform_edt(~padding)>6) if padding.any() else np.ones(g.shape,bool)
    shade=region_mask(im.size,cfg['tone_regions'])
    exclude=region_mask(im.size,cfg['exclusions'])
    local=nd.gaussian_filter(nd.grey_closing(g,size=(31,31)),3)
    ink=np.clip(1-g/np.maximum(local,.1),0,1)
    f=cfg['line_floor'];r=cfg['line_range']
    line=1-np.clip((ink-f)/(r-f),0,1)**.85
    background=paper_field(g,exclude,valid)
    tone_ink=np.clip(1-g/np.maximum(background,.1),0,1)
    f=cfg['tone_floor'];r=cfg['tone_range']
    tone=1-np.clip((tone_ink-f)/(r-f),0,1)
    if n=='283':
        diagram=region_mask(im.size,cfg['tone_regions'][1:])
        tone[diagram]=np.minimum(tone[diagram],line[diagram])
    # A small feather prevents an abrupt change of processing at hand masks.
    blend=nd.gaussian_filter(nd.binary_dilation(shade,iterations=2).astype(float),2)
    cleaned=np.clip(tone*blend+line*(1-blend),0,1)
    # Preserve dark ink that approaches the artificial canvas boundary (e.g.
    # Plate 29's leftmost 8). Only the pale seam/padding may be made white.
    cleaned[(~valid)&(raw>.56)]=1
    if cfg.get('keep_regions'):
        keep=region_mask(im.size,cfg['keep_regions'])|shade
        keep=nd.binary_dilation(keep,iterations=5)
        cleaned[~keep]=1
    out=DEST/'clean'/f'p{n}-clean.png'
    pixels=np.uint8(np.round(cleaned*255))
    accepted_mask=cfg.get('accepted_keep_mask')
    if accepted_mask:
        # Apply the user-reviewed mask only after reproducing the conservative
        # grayscale pixels. No rotation, interpolation or inferred marks.
        keep=np.asarray(Image.open(ROOT/accepted_mask).convert('L'))>0
        assert keep.shape==pixels.shape
        before=DEST/'aggressive'/'Plate12_Current.png'
        assert np.array_equal(pixels,np.asarray(Image.open(before)))
        pixels[~keep]=255
        cleaned=pixels.astype(float)/255
    save_png(Image.fromarray(pixels),out)
    save_png(Image.fromarray(np.uint8(shade)*255),DEST/'review'/f'p{n}-tone-mask.png')
    rec={'folio':n,'plates':cfg['plates'],'kind':cfg['kind'],'source':str(src.relative_to(ROOT)),
         'source_sha256':digest(src),'clean':str(out.relative_to(ROOT)),
         'clean_sha256':digest(out),'pixel_size':list(im.size),
         'geometry_change':False,'background_field_range_0_1':[float(background.min()),float(background.max())],
         'white_fraction':float(np.mean(cleaned>=254.5/255)),
         'tone_area_fraction':float(shade.mean()),'vector':None,'review':'pending'}
    if paired:
        rec['paired_reverse_field']=paired
        rec['paired_reverse_field_sha256']=digest(ROOT/paired)
        rec['reverse_folio']='283'
    if accepted_mask:
        rec['accepted_keep_mask']=accepted_mask
        rec['accepted_keep_mask_sha256']=digest(ROOT/accepted_mask)
        rec['cleanup_approval']='Aggressive Plate 12 candidate accepted by user, 2026-09-12.'
    return rec

def trace(n,potrace):
    cfg=CFG[n];im=Image.open(DEST/'clean'/f'p{n}-clean.png').convert('L');w,h=im.size
    a=np.asarray(im).copy();shade=region_mask(im.size,cfg['tone_regions'])
    shade=nd.binary_dilation(shade,iterations=7) if shade.any() else shade
    a[shade]=255
    top=ET.Element('{%s}svg'%NS,{'version':'1.1','width':str(w),'height':str(h),'viewBox':f'0 0 {w} {h}'})
    ET.SubElement(top,'{%s}title'%NS).text=f"SNL G-13, folio {n}, plates {cfg['plates']}"
    ET.SubElement(top,'{%s}desc'%NS).text=(
        'Eight gray levels of source-derived outline paths. Original lettering remains outlines. '
        'Not a semantic CAD model. No missing detail reconstructed. '+
        ('Protected shaded regions are embedded lossless raster pixels.' if shade.any() else 'Contains vector paths only.'))
    ET.SubElement(top,'{%s}rect'%NS,{'width':str(w),'height':str(h),'fill':'white'})
    if shade.any():
        # Opaque white outside the retained tone region avoids soft-mask seams
        # when an SVG is placed at small print sizes or converted to PDF.
        retained=np.asarray(im).copy();retained[~shade]=255
        bio=io.BytesIO();Image.fromarray(retained).save(bio,format='PNG',optimize=True)
        ET.SubElement(top,'{%s}image'%NS,{'x':'0','y':'0','width':str(w),'height':str(h),
            '{http://www.w3.org/1999/xlink}href':'data:image/png;base64,'+base64.b64encode(bio.getvalue()).decode()})
    # Multiple levels retain the distinction between a faint hatch and a bold outline.
    # No turd/speckle deletion: small original punctuation must not disappear.
    sampled=np.asarray(Image.fromarray(a).resize((w*3,h*3),Image.Resampling.BICUBIC))
    paths=0
    with tempfile.TemporaryDirectory(prefix='snl-trace-') as tmp:
        tmp=Path(tmp)
        for level in range(1,9):
            cutoff=255-(level-.5)*255/8
            binary=Image.fromarray(np.uint8(sampled>=cutoff)*255).convert('1',dither=Image.Dither.NONE)
            pbm=tmp/'layer.pbm';svg=tmp/'layer.svg';binary.save(pbm)
            subprocess.run([potrace,str(pbm),'-s','-t','0','-a','1','-O','0.12','-o',str(svg)],check=True,capture_output=True)
            layer=ET.SubElement(top,'{%s}g'%NS,{'id':f'ink-level-{level}','transform':'scale(0.3333333333333333)',
                'fill':'#'+('%02x'%round(255-level*255/8))*3})
            tr=ET.parse(svg).getroot()
            for group in tr.findall('{%s}g'%NS):
                group.attrib.pop('fill',None);layer.append(group)
                paths+=len(group.findall('.//{%s}path'%NS))
    out=DEST/'vector'/f'p{n}-restored.svg'
    ET.ElementTree(top).write(out,encoding='utf-8',xml_declaration=True)
    return {'path':str(out.relative_to(ROOT)),'sha256':digest(out),'type':'hybrid SVG' if shade.any() else 'vector SVG',
            'gray_levels':8,'paths':paths,'embedded_raster_regions':bool(shade.any()),
            'text_representation':'source-derived outlines, not editable characters'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pages',nargs='*');ap.add_argument('--trace',action='store_true');ap.add_argument('--potrace',default=os.environ.get('POTRACE',shutil.which('potrace')));args=ap.parse_args()
    for d in ['clean','vector','review']:(DEST/d).mkdir(parents=True,exist_ok=True)
    mp=DEST/'manifest.json';manifest=json.loads(mp.read_text()) if mp.exists() else {}
    for n in args.pages or CFG:
        previous=manifest.get(n,{})
        rec=clean(n)
        if args.trace and CFG[n]['vector_candidate']:
            if not args.potrace:raise RuntimeError('Set POTRACE or --potrace to the executable.')
            rec['vector']=trace(n,args.potrace)
        unchanged=previous.get('clean_sha256')==rec['clean_sha256'] and previous.get('source_sha256')==rec['source_sha256']
        if not args.trace and unchanged:rec['vector']=previous.get('vector')
        if rec['vector']:
            old_vector=previous.get('vector') or {}
            if old_vector.get('sha256')==rec['vector']['sha256']:
                rec['vector']['recommended']=old_vector.get('recommended',False)
            else:
                rec['vector']['recommended']=False
                unchanged=False
        for key in ['preferred','note','historical_vector_trial','book_representation']:
            if key in previous:rec[key]=previous[key]
        rec['review']=previous.get('review','pending') if unchanged else 'Outputs changed; review required before publication.'
        manifest[n]=rec;print(f"Cleaned {n}; vector={bool(rec['vector'])}",flush=True)
        mp.write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
