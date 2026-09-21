"""Expose the catalogue topology correction beside both original clutch figures."""
import argparse,base64,hashlib,html,json
from pathlib import Path
import fitz
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_collar_build')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=json.loads((base/'report.json').read_text())
hb=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png'
snl=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
prior=HERE/'front_clutch_build/previews/section.png'
def embed(path,x,y,w,h):
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
def text(x,y,value,size=18):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}">{html.escape(value)}</text>'
crop=[310,290,970,560]
source_detail=f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="924" viewBox="{" ".join(map(str,crop))}">{embed(snl,0,0,1447,1055)}</svg>'
(out/'snl21_detail.svg').write_text(source_detail)
with fitz.open(stream=source_detail.encode(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/'snl21_detail.png'))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2190">','<rect width="1800" height="2190" fill="#f6f4ed"/>',
    text(30,38,'Clutch collar joint | catalogue topology correction and end-bearing reconstruction',26),
    text(30,70,'SNL controls the new coupling arrangement. HB dimensional transfers remain provisional. Panels use independent scales.'),
    text(30,115,'HB71: transmission left, engine right',21),embed(hb,20,130,865,630),
    text(915,115,'SNL21 detail: engine left, transmission right',21),embed(out/'snl21_detail.png',905,130,875,630),
    text(30,800,'New native: separate spring flange, bearing pocket and collar joint',21),
    text(920,800,'Previous approximation: single front flange',21),
    embed(base/'previews/section.png',20,820,880,495),embed(prior,900,820,880,495),
    text(30,1345,'Actual joint section and locking-wire route',21),
    embed(base/'previews/joint_section.png',20,1360,880,495),embed(base/'previews/locking_wire.png',900,1360,880,495)]
notes=[
    'Closer catalogue inspection showed that the previous single-flange approximation could not receive the illustrated bearing and collar.',
    'The corrected SH945A has a rear spring flange and a forward joint flange, with a separate SH997A ring and SH997B bush in its pocket.',
    'Spring and split clamp move67mm aft together; the spring flange now lies aft of the enlarged cardan head, as in the catalogue section.',
    'SNL200:002 specifies six3/8 x5/8in drilled cap screws for SH999A. Their blind receivers retain9.525mm nominal axial engagement.',
    'SNL276:003 specifies26in of W.&M.No16 soft-steel wire. The route and paired twist are inferred;1.5mm diameter is an approximation.',
    'HB and SNL coupling/collar/bearing marks differ. The new axial stations, pocket diameters, bush clearance and collar stock are estimates.',
    'The collar main bearing, positive sleeve, four keys, cone-support collar and thrust/ball stack remain unbuilt; the bore is visibly vacant.',
    'The original bolt-callout25 mismatch remains open. Current spring-clamp hardware follows the explicit SH849A written allocation.',
    'This corrects a structural discrepancy; it does not establish exact historical contours, crankshaft fit, preload or locking-wire strength.'
]
for n,note in enumerate(notes):svg.append(text(30,1888+32*n,note))
svg.append('</svg>');path=out/'comparison.svg';path.write_text(''.join(svg))
with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
inputs=[hb,snl,prior]+[base/'previews'/n for n in ['section.png','joint_section.png','locking_wire.png']]
outputs=[path,path.with_suffix('.png'),out/'snl21_detail.svg',out/'snl21_detail.png']
receipt=dict(native_sha256=report['native_sha256'],renderer_sha256=sha(Path(__file__)),
    input_hashes={str(p.relative_to(REPO)):sha(p) for p in inputs},output_hashes={p.name:sha(p) for p in outputs},
    source_viewport=dict(asset=str(snl.relative_to(REPO)),viewBox=crop),
    orientation='Original source orientations preserved; both native sections follow HB. Independent panel scales, no metrology claim.',notes=notes)
(out/'render_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch collar source comparison</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}p{max-width:100ch}</style><h1>Clutch collar and bearing pocket</h1><p>The closer catalogue section required a second coupling flange and a forward bearing pocket. The earlier approximation remains available beside the corrected native section. Independent scales; internal clutch construction continues.</p><img src="comparison.png" alt="HB and SNL sources, corrected and prior native sections, collar joint and locking wire"><p><a href="render_receipt.json">Source hashes, crop coordinates and limitations</a></p></html>')
print('Saved source comparison; visual inspection still required.')
