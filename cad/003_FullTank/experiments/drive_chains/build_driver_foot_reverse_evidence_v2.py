"""Collect next driver controls' source rows, original views and retained native interfaces."""
import argparse,hashlib,importlib,json,sys,re
from pathlib import Path
from PIL import Image
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
SNL=ROOT/'references/1928-03-30_SNL_G13/SNL_G13_Project';HB=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);parent=a.parent.resolve()
deps={}
def bind(p):deps[str(p.relative_to(ROOT))]=sha(p)
bind(Path(__file__));terms=['M764A','M765','M766','M767','M769','M770','M771','M775','M777','M778','M779','M780','M781','M795','M571','M570','M566','M576','SH98B','SH98C','SH98D']
sys.path.insert(0,str(SNL));selected=[];pages={}
for f in sorted((SNL/'data').glob('*.py')):
    module=importlib.import_module('data.'+f.stem)
    if not hasattr(module,'TABLES'):continue
    bind(f)
    for page,rows in module.TABLES.items():
        for i,row in enumerate(rows,1):
            matches=[t for t in terms if re.search(r'(?<![A-Za-z0-9])'+re.escape(t)+r'(?![A-Za-z0-9])',json.dumps(row))]
            if matches:
                selected.append(dict(source_id=f'SNL:{page:03d}:{i:03d}',matched_terms=matches,**row))
                # Keep the enclosing rows: blank-mark assembly children alone lose dimensions.
                pages[page]=[dict(source_id=f'SNL:{page:03d}:{j:03d}',**v) for j,v in enumerate(rows,1)]
images=[]
for page in sorted(pages):
    source=SNL/'sources'/f'p{page:03d}.jpg';bind(source);im=Image.open(source).rotate(-90,expand=True);im.thumbnail((2100,2100));f=out/f'snl{page:03d}.png';im.save(f);images.append(dict(file=f.name,source=str(source.relative_to(ROOT)),rotation_degrees=-90,sha256=sha(f)))
for file in ['plate92.png','plate94.png','plate113.png']:
    source=HB/'Handbook_Project/assets'/file;bind(source);im=Image.open(source);im.thumbnail((2000,2000));f=out/('hb_'+file);im.save(f);images.append(dict(file=f.name,source=str(source.relative_to(ROOT)),sha256=sha(f)))
source=SNL/'assets/p280-geometry.png';bind(source);im=Image.open(source);im.thumbnail((2100,2100));f=out/'snl_plate6.png';im.save(f);images.append(dict(file=f.name,source=str(source.relative_to(ROOT)),sha256=sha(f)))
body=HB/'Handbook_Project/data/body_batch08.json';bind(body);text=read(body);texts={k:[v['text'] for v in text[k]] for k in ['146','148','149','150']}
# Use the existing exact original-page splitter; no reconstructed lettering.
sys.path.insert(0,str(HB/'Handbook_Project'));from prepare_assets import page as hb_page
bind(HB/'Handbook_Project/prepare_assets.py')
for n in [146,148,150]:
    source=HB/'original_scans'/f'MarkVIII{n//2+1:03d}.jpg';bind(source)
    im=hb_page(n,HB/'original_scans');im.thumbnail((1700,2200));f=out/f'hb{n:03d}_original.png';im.save(f);images.append(dict(file=f.name,source=str(source.relative_to(ROOT)),printed_page=n,sha256=sha(f)))
r=read(parent/'report.json');m=read(parent/'isolated/manifest.json');native=parent/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
for f in [parent/'report.json',parent/'isolated/manifest.json',native]:bind(f)
interfaces={v['name']:v for v in m['occurrences'] if any(t in v['name'] for t in ['FootIntermediate','ReverseIntermediate','ReverseDriverSwing','DriverMainShaft','DriverSwingShaft','DriverOperatingHandle','DriverClutchOperatingLever'])}
material={v['definition']:m['definitions'][v['definition']] for v in interfaces.values()}
for v in material.values():bind(Path(v['brep_path']))
report=dict(evidence_only=True,geometry_created=False,parent_native=str(native.relative_to(ROOT)),parent_native_sha256=sha(native),input_hashes=deps,selected_rows=selected,complete_selected_pages=pages,handbook_text=texts,images=images,retained_interfaces=interfaces,retained_interface_definitions=material,
    classification='Selection and exact retained interfaces only. Original images still require explicit source/topology review before construction.',source_camera_refitted=False,
    constraints=['Five M576 applications must retain one shared definition: high-speed2, foot2, clutch1. Two foot rods remain absent.','Two SH946F special fork ends belong to the two foot M576 applications; do not replace them automatically with M569C.','HB148 neutral-selective braking requires the M771 interconnection with existing selectors; do not model two permanently independent pedal-to-rod drives.','HB150 gives27.968in hand reach,6in bell arm and52in reverse rod; confirm original text, length datum and front/center/rear identity before applying.','All existing printed M574 and SH229A stock must be preserved; new interfaces may require a coupled closure solve.','SNL71 front-control assembly, SNL72 continuation and application-specific bolt/pin rows control inventory; generic fastener totals are not local counts.'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(len(selected),'selected rows;',len(images),'source views;',len(interfaces),'retained interfaces')
