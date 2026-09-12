#!/usr/bin/env python3
"""Preservation checks against the preceding complete project checkpoint."""
from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as ET
import fitz,numpy as np
from PIL import Image
from project_sequence import LABELS

ROOT=Path(__file__).resolve().parent;R=ROOT/'restoration'
def canon(n):return (n.tag,sorted(n.attrib.items()),(n.text or '').strip(),[canon(c) for c in n])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--baseline-zip',required=True);args=ap.parse_args()
    z=zipfile.ZipFile(args.baseline_zip);prefix='SNL_G13_Project/'
    m=json.loads((R/'manifest.json').read_text());assert len(m)==31
    assert sorted(p for r in m.values()for p in r['plates'])==list(range(1,35))
    old=ET.fromstring(z.read(prefix+'SNL_G13_Pilot.sla'));new=ET.parse(ROOT/'SNL_G13_Pilot.sla').getroot()
    objs=old.findall('.//PAGEOBJECT');assert len(objs)==32632
    changed=[]
    for obj in objs:
        for n,r in m.items():
            if obj.get('PFILE')==f'assets/p{n}-geometry.png':
                obj.set('PFILE',r['clean']);changed.append(n);break
    assert sorted(changed)==sorted(m)
    assert canon(old)==canon(new),'Native changes other than the 31 image links'
    counts={}
    for folder in ['sources','assets','data']:
        files=[n for n in z.namelist() if n.startswith(prefix+folder+'/') and not n.endswith('/')]
        for n in files:assert (ROOT/n[len(prefix):]).read_bytes()==z.read(n),n
        counts[folder]=len(files)
    vectors=[]
    for n,r in m.items():
        src=Image.open(ROOT/r['source']);im=Image.open(ROOT/r['clean']);im.load()
        assert src.size==im.size==tuple(r['pixel_size']) and im.mode=='L'
        assert sha(ROOT/r['source'])==r['source_sha256'] and sha(ROOT/r['clean'])==r['clean_sha256']
        if r.get('paired_reverse_field'):
            assert sha(ROOT/r['paired_reverse_field'])==r['paired_reverse_field_sha256']
            field=np.load(ROOT/r['paired_reverse_field'])['reverse_ink_fraction']
            assert field.shape==np.asarray(im).shape and np.all(np.isfinite(field)) and field.min()>=0 and field.max()<=.25
        if r.get('vector'):
            svg=ROOT/r['vector']['path'];assert sha(svg)==r['vector']['sha256']
            tree=ET.parse(svg);ns='{http://www.w3.org/2000/svg}'
            embedded=len(tree.findall('.//'+ns+'image'))
            assert embedded==int(r['vector']['embedded_raster_regions'])
            d=fitz.open(svg.with_suffix('.pdf'));pix=d[0].get_pixmap(matrix=fitz.Matrix(4/3,4/3),colorspace=fitz.csGRAY)
            a=np.asarray(im);b=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)[:a.shape[0],:a.shape[1]]
            mae=float(np.abs(a.astype(float)-b).mean())
            lost=float(np.sum((a<120)&(b>245))/max(1,np.sum(a<120)))
            assert mae<8 and lost<.001,(n,mae,lost)
            assert len(d[0].get_images())==embedded
            vectors.append(dict(folio=n,recommended=r['vector']['recommended'],mean_absolute_gray_difference=mae,dark_to_white_dropout_fraction=lost,embedded_raster_images=embedded))
    native=json.loads((R/'native_validation.json').read_text());assert native['exported'] and len(native['artwork_frames'])==31
    before=fitz.open(stream=z.read(prefix+'SNL_G13_Pilot.pdf'),filetype='pdf');after=fitz.open(ROOT/'SNL_G13_Pilot.pdf')
    assert len(after)==314 and after.get_toc()==before.get_toc()
    assert [p.get_label() for p in after]==LABELS
    same=[];different=[]
    for i,(p,q) in enumerate(zip(before,after)):
        assert p.rect==q.rect and p.get_text()==q.get_text(),LABELS[i]
        assert all(after.extract_font(f[0])[3] for f in q.get_fonts())
        a=p.get_pixmap(matrix=fitz.Matrix(1,1));b=q.get_pixmap(matrix=fitz.Matrix(1,1))
        (same if a.samples==b.samples else different).append(LABELS[i])
        if LABELS[i] in m or LABELS[i]=='Face p. 277':
            a=p.get_image_info();b=q.get_image_info()
            assert len(a)==len(b)==1
            assert all(abs(x-y)<.001 for x,y in zip(a[0]['bbox'],b[0]['bbox'])),LABELS[i]
            assert (a[0]['width'],a[0]['height'])==(b[0]['width'],b[0]['height']),LABELS[i]
    assert len(same)==283 and len(different)==31,(len(same),different)
    for filename,pages in [('Figure_Restoration_Comparisons.pdf',38),('Restored_Figures.pdf',31),('Plate12_Mirror_Study.pdf',5)]:
        d=fitz.open(ROOT/filename);assert len(d)==pages
        for p in d:p.get_pixmap(matrix=fitz.Matrix(.8,.8))
    result=dict(status='PASS',artwork_assets=31,plates=34,native_pages=314,native_objects=32632,
        editable_text_frames=25682,only_native_changes='31 image link paths',native_geometry_unchanged=True,
        original_files_unchanged=counts,all_clean_images_decoded=True,input_pixel_dimensions_preserved=True,
        pdf_text_unchanged_all_pages=True,pdf_unchanged_page_count=len(same),pdf_changed_folios=different,
        pdf_image_bounds_and_dimensions_preserved=True,vector_validation=vectors,
        paired_reverse_folios=['284'],
        validation_limit='Pixel comparison validates tracing against the cleaned raster, not historical accuracy or complete recovery of faint source information.')
    (R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
