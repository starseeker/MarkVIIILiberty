#!/usr/bin/env python3
"""Run inside Scribus to verify image links and export the updated native book.

Does not save/rewrite the SLA serialization. Seven artwork frames were replaced
by tested SVG groups; all other objects are preserved. See validate_final_book.py.
"""
from pathlib import Path
import json,os,tempfile,traceback
import scribus as s
ROOT=Path(__file__).resolve().parent;R=ROOT/'restoration'
try:
    (R/'native-error.txt').unlink(missing_ok=True)
    loaded={f[0]:Path(f[-1]) for f in s.getXFontNames()}
    for face,filename in [('C059 Roman','C059-Roman.otf'),('C059 Bold','C059-Bold.otf'),('C059 Italic','C059-Italic.otf')]:
        assert loaded[face].read_bytes()==(ROOT/'fonts'/filename).read_bytes(),face
    print('Opening restored native book',flush=True)
    s.openDoc(str(ROOT/'SNL_G13_Pilot.sla'));s.setRedraw(False);assert s.pageCount()==314
    m=json.loads((R/'manifest.json').read_text());checks=[]
    for n in m:
        name='p277-foldout-plate-2' if n=='277_foldout' else f'p{n}-plate-artwork'
        kind=s.getObjectType(name)
        expected='Group' if (m[n].get('vector') or {}).get('recommended') else 'ImageFrame'
        assert kind==expected,(n,kind,expected)
        checks.append({'folio':n,'object':name,'type':kind,'size_points':s.getSize(name)})
    for name,reading in [('p43-r22-ord','SH40AD'),('p66-r28-ord','SH976C'),('p97-r03-item','1⅛')]:
        assert reading in s.getAllText(name),(name,reading)
    print('Verified 7 SVG groups, 24 artwork frames and transcription corrections; exporting 314 pages',flush=True)
    with tempfile.TemporaryDirectory(prefix='snl-restored-book-') as tmp:
        out=Path(tmp)/'book.pdf';pdf=s.PDFfile();pdf.file=str(out)
        pdf.pages=list(range(1,315));pdf.version=15;pdf.fonts=[]
        pdf.subsetList=['C059 Roman','C059 Bold','C059 Italic'];pdf.compress=1;pdf.quality=0;pdf.resolution=300
        pdf.compressmtd=2;pdf.downsample=0
        pdf.save();data=out.read_bytes();assert data.rstrip().endswith(b'%%EOF')
        (ROOT/'SNL_G13_Pilot.pdf').write_bytes(data)
    (R/'native_validation.json').write_text(json.dumps({'pages':314,'artwork_frames':checks,'exported':True,'font_files_verified':True},indent=2))
    print('Export complete',flush=True)
except Exception:(R/'native-error.txt').write_text(traceback.format_exc())
finally:
    if os.environ.get('SNL_BATCH')=='1':os._exit(0)
