#!/usr/bin/env python3
"""Make full-project and portable figure-asset bundles without scratch previews."""
from pathlib import Path
import argparse,json,tempfile,zipfile
ROOT=Path(__file__).resolve().parent

def write_zip(dest,entries,extra=None):
    with tempfile.TemporaryDirectory(prefix='snl-delivery-') as td:
        tmp=Path(td)/dest.name
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for arc,path in sorted(entries.items()):z.write(path,arc)
            for arc,data in (extra or {}).items():z.writestr(arc,data)
        with zipfile.ZipFile(tmp) as z:
            assert z.testzip() is None
            count=len(z.namelist())
        dest.write_bytes(tmp.read_bytes())
    print(dest.name, count,'entries',round(dest.stat().st_size/1e6,2),'MB',flush=True)
    return count

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--baseline-zip',required=True);args=ap.parse_args()
    baseline=zipfile.ZipFile(args.baseline_zip);prefix='SNL_G13_Project/'
    files={}
    for name in baseline.namelist():
        if not name.endswith('/'):
            p=ROOT/name[len(prefix):];assert p.is_file(),p;files[name]=p
    added=['FIGURE_RESTORATION.md','DOCUMENTATION.md','Figure_Restoration_Comparisons.pdf','Plate12_Mirror_Study.pdf','Restored_Figures.pdf','restore_figures.py','paired_bleedthrough.py','export_restored_figures.py','make_restoration_proofs.py','make_plate12_mirror_study.py','integrate_restored_figures.py','export_restored_book.py','validate_figure_restoration.py','package_restoration.py']
    added += ['prepare_native_vectors.py','import_native_vectors.py','integrate_native_vectors.py','validate_final_book.py','optimize_pdf_images.py']
    for name in added:files[prefix+name]=ROOT/name
    for p in (ROOT/'restoration').rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if '__pycache__' in p.parts or 'review' in p.parts or 'fitting-output' in p.parts or p.name.startswith('study-') or p.name=='native-error.txt':continue
        if 'native' in p.parts and (p.name.endswith(('-import.svg','-native.sla','-native.pdf','-preview.png')) or 'error' in p.name):continue
        files[prefix+str(rel)]=p
    # Large comparison proof is delivered separately. All source/working assets,
    # the full book, native document and preferred-master gallery stay bundled.
    files.pop(prefix+'Figure_Restoration_Comparisons.pdf',None)
    result=json.loads((ROOT/'restoration/validation.json').read_text());assert result['status']=='PASS'
    m=json.loads((ROOT/'restoration/manifest.json').read_text());small={};sm={};sp='SNL_G13_Restored_Figures/'
    for n,r in m.items():
        r=dict(r);r['original_geometry_reference_in_bundle']=False
        for path in [r['clean'],str(Path(r['clean']).with_suffix('.pdf'))]:small[sp+path]=ROOT/path
        if r.get('vector'):
            r['vector']=dict(r['vector']);r['vector']['included_in_bundle']=r['vector']['recommended']
            if r['vector']['recommended']:
                for path in [r['vector']['path'],str(Path(r['vector']['path']).with_suffix('.pdf'))]:small[sp+path]=ROOT/path
        sm[n]=r
    small[sp+'FIGURE_RESTORATION.md']=ROOT/'FIGURE_RESTORATION.md'
    small[sp+'DOCUMENTATION.md']=ROOT/'DOCUMENTATION.md'
    small[sp+'restoration/validation.json']=ROOT/'restoration/validation.json'
    small[sp+'restoration/paired/p284-validation.json']=ROOT/'restoration/paired/p284-validation.json'
    for name in ['Plate12_KeepMask.png','Plate12_Current.png','README.md','validation.json']:
        small[sp+'restoration/aggressive/'+name]=ROOT/'restoration/aggressive'/name
    readme='''# SNL G-13 — restored figure masters

All 34 plates in 31 ordered artwork assets. Use restoration/clean for all lossless
PNG/PDF masters, or restoration/vector for the seven recommended SVG/PDF masters
(five pure vector and two hybrid). Folio-based filenames preserve paired plates
and the foldout. Plate 12 is the accepted aggressive cleanup, with its mask and
earlier conservative master retained under restoration/aggressive/.

FIGURE_RESTORATION.md explains methods, decisions and remaining limits.
DOCUMENTATION.md records the complete book and archival provenance. The manifest
explicitly marks omitted, non-recommended vector trials. Original geometry
references, source JPEGs, fitting experiments and Scribus files are in the full
SNL_G13_Project.zip. Proof PDFs and the preferred-master gallery are separate
companion downloads; this smaller ZIP contains the artwork assets themselves.
'''
    write_zip(ROOT.parent/'SNL_G13_Restored_Figures.zip',small,{sp+'README.md':readme,sp+'restoration/manifest.json':json.dumps(sm,indent=2)})
    write_zip(ROOT.parent/'SNL_G13_Project.zip',files)
    assert (ROOT.parent/'SNL_G13_Project.zip').stat().st_size < 512*1024*1024
    print('All baseline entries retained except the separately delivered comparison PDF; all 34 plates covered.',flush=True)
if __name__=='__main__':main()
