"""Validate exported text, vector fidelity, and portability; make a comparison PDF."""
from pathlib import Path
import json,hashlib,re,collections,unicodedata
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
import fitz
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
def normalized(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t))
def main():
    R=json.loads((ROOT/'data/release.json').read_text())
    frames=json.loads((ROOT/'data/native_frames.json').read_text())
    artwork=json.loads((ROOT/'data/artwork.json').read_text())
    source=fitz.open(ROOT/'sources/US-1366550-A.pdf');final=fitz.open(ROOT/R['pdf'])
    assert len(final)==len(source)==4
    checks=[]
    for i,pg in enumerate(final):
        assert tuple(pg.rect)==(0,0,612,792)
        expected=collections.Counter(normalized(''.join(f['text'] for f in frames if f['page']==i+1)))
        actual=collections.Counter(normalized(pg.get_text()))
        assert expected==actual,dict(page=i+1,missing=dict(expected-actual),extra=dict(actual-expected))
        assert not pg.get_images(), 'All final artwork should be native vector paths.'
        checks.append(dict(page=i+1,pdf_text_character_inventory_matches=True,native_vector_paths=len(pg.get_drawings()),raster_images=0))
    vectors=[]
    for a in artwork:
        px=final[a['page']-1].get_pixmap(matrix=fitz.Matrix(2320/612,3408/792),colorspace=fitz.csGRAY)
        cur=np.asarray(Image.frombytes('L',(px.width,px.height),px.samples).crop(a['native_box']))<240
        ref=np.asarray(Image.open(ROOT/'assets'/a['raster']).convert('L'))<128
        if a['id']!='sheet1_signature':
            x=max(0,round(548*2320/918)-a['native_box'][0]);y=max(0,round(249*3408/1188)-a['native_box'][1]);cur[:y,x:]=False
        dr=ndi.distance_transform_edt(~ref);dc=ndi.distance_transform_edt(~cur)
        q=dict(id=a['id'],visible_ink_threshold=240,reference_ink_pixels=int(ref.sum()),coverage_within_two_native_pixels=float((dc[ref]<=2).mean()),render_within_two_native_pixels=float((dr[cur]<=2).mean()),max_reference_distance=float(dc[ref].max()))
        assert q['coverage_within_two_native_pixels']==1.0,q
        assert q['render_within_two_native_pixels']>.999,q
        vectors.append(q)
    xml=etree.parse(str(ROOT/R['sla']))
    links=[e.get('PFILE') for e in xml.iter() if e.get('PFILE')]
    assert not links,links
    report=dict(page_checks=checks,vector_checks=vectors,external_artwork_links=links,pdf_bytes=(ROOT/R['pdf']).stat().st_size)
    (ROOT/'data/export_validation.json').write_text(json.dumps(report,indent=2))
    comparison=fitz.open()
    for i in range(4):
        pg=comparison.new_page(width=936,height=654)
        pg.insert_text((24,25),f'U.S. PATENT 1,366,550 | PAGE {i+1} | '+R['release_id'],fontsize=10,fontname='hebo')
        pg.insert_text((24,43),'SUPPLIED USPTO SCAN',fontsize=8,fontname='hebo')
        pg.insert_text((482,43),'SCRIBUS RECONSTRUCTION',fontsize=8,fontname='hebo')
        pg.show_pdf_page(fitz.Rect(24,54,454,611),source,i)
        pg.show_pdf_page(fitz.Rect(482,54,912,611),final,i)
        pg.insert_text((24,637),'Original page order and letter-size geometry. Printed text rebuilt; source-derived drawing outlines retained.',fontsize=8)
    # The last sheet keeps three fine-detail comparisons large enough to inspect.
    pg=comparison.new_page(width=936,height=744)
    pg.insert_text((24,26),'DRAWING DETAIL CHECK | SOURCE / RECONSTRUCTION',fontsize=12,fontname='hebo')
    details=[(0,fitz.Rect(290,270,390,393),'Figure 1 - hatching, fasteners and chamber perforations'),(1,fitz.Rect(287,395,458,490),'Figure 3 - dotted movement outlines'),(1,fitz.Rect(313,626,498,666),'Inventor signature')]
    for j,(i,rect,title) in enumerate(details):
        yy=52+j*222
        pg.insert_text((24,yy),title,fontsize=9,fontname='hebo')
        pg.insert_text((24,yy+16),'SOURCE',fontsize=7);pg.insert_text((482,yy+16),'RECONSTRUCTION',fontsize=7)
        pg.show_pdf_page(fitz.Rect(24,yy+24,454,yy+207),source,i,clip=rect)
        pg.show_pdf_page(fitz.Rect(482,yy+24,912,yy+207),final,i,clip=rect)
    pg.insert_text((24,729),'Tracing smooths pixel boundaries. Cleaned native-resolution bitmaps and the untouched source PDF are included.',fontsize=8)
    comparison.set_metadata(dict(title='US1366550A - source comparison - '+R['release_id'],author='Herbert W. Alden; digital reconstruction'))
    comparison.save(ROOT/R['comparison'],garbage=4,deflate=True)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
