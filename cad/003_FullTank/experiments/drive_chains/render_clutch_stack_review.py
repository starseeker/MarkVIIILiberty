"""Compare the nested main-clutch stack with original source figures."""
import argparse,base64,hashlib,html,json
from pathlib import Path
import fitz
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_stack_build')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=json.loads((base/'report.json').read_text())
hb=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png'
snl=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
prior=HERE/'clutch_stack_build/rejected_trials/initial_ring_mapping/previews/section.png'
def embed(path,x,y,w,h):
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
def text(x,y,value,size=18):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}">{html.escape(value)}</text>'
crop=[0,0,1447,1055]
source_detail=f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1167" viewBox="{" ".join(map(str,crop))}">{embed(snl,0,0,1447,1055)}</svg>'
(out/'snl21_detail.svg').write_text(source_detail)
with fitz.open(stream=source_detail.encode(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/'snl21_detail.png'))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2220">','<rect width="1800" height="2220" fill="#f6f4ed"/>',
    text(30,38,'Main clutch | nested bearing, sleeve, keyed support and retention',26),
    text(30,70,'Catalogue arrangement with provisional HB dimensional transfers. Independent panel scales; engine and operating parts remain incomplete.'),
    text(30,115,'HB71: transmission left, engine right',21),embed(hb,20,130,865,630),
    text(915,115,'SNL21: 28 thrust collar; 30 external snap ring',21),embed(out/'snl21_detail.png',905,130,875,630),
    text(30,800,'Corrected native: thrust collar and external snap ring',21),
    text(920,800,'Rejected first core: internal snap-ring mapping',21),
    embed(base/'previews/section.png',20,820,880,495),embed(prior,900,820,880,495),
    text(30,1345,'Enclosing collars hidden and isolated positive sleeve',21),
    embed(base/'previews/internals.png',20,1360,880,495),embed(base/'previews/sleeve.png',900,1360,880,495)]
notes=[
    'SNL21 shows the sleeve nested in a rear bearing band and a wide internal relief between the two bearing bands; the new section follows that arrangement.',
    'SH999A now receives the bearing, four key beds and an external ring groove. Nine physical pieces bring the combined native to1549 leaves.',
    'SH869A cone-support identity agrees between sources. Catalogue SH998D,SH861B andSH861E differ from HB SH863A,SH864C andSH863C.',
    'HB sleeve2.687in length,3.531in ID and24splines are provisional transfers. Exact tooth form and crankshaft engagement remain unqualified.',
    'The larger SNL bearing profile does not use HB4.684in OD. Estimated OD152mm and stepped bores follow the pictured topology, not a measured original.',
    'Four keys use the literal HB .75in radial thickness and .375in tangential width. Their bands appear thicker than the source section; axis interpretation is unresolved.',
    'The support retains2.97mm nominal clearance from the previously modeled locking wire. Cone flange, stations and rivet attachment remain provisional.',
    'Full-plate callout tracing corrects the initial mapping: SH998B is the bearing-end thrust collar; SH861E is the separate external ring farther aft.',
    'The unsupported internal groove is removed. The external ring now sits in an outside groove; thrust-collar attachment and ball reaction remain unfinished.',
    'Sleeve-to-collar attachment is a nominal fitted surface, not a qualified torque connection. Ball reaction, cones, plungers and engine interfaces remain ahead.'
]
for n,note in enumerate(notes):svg.append(text(30,1888+32*n,note))
svg.append('</svg>');path=out/'comparison.svg';path.write_text(''.join(svg))
with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
inputs=[hb,snl,prior]+[base/'previews'/n for n in ['section.png','internals.png','sleeve.png']]
outputs=[path,path.with_suffix('.png'),out/'snl21_detail.svg',out/'snl21_detail.png']
receipt=dict(native_sha256=report['native_sha256'],renderer_sha256=sha(Path(__file__)),
    input_hashes={str(p.relative_to(REPO)):sha(p) for p in inputs},output_hashes={p.name:sha(p) for p in outputs},
    source_viewport=dict(asset=str(snl.relative_to(REPO)),viewBox=crop),
    orientation='Original source orientations preserved; both native sections follow HB. Independent panel scales, no metrology claim.',notes=notes)
(out/'render_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Main clutch stack source comparison</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}p{max-width:100ch}</style><h1>Main clutch bearing, sleeve and keyed support</h1><p>Full-plate callout tracing corrects the initial end-ring mapping: 28 is the SH998B thrust collar, while 30 is a separate external SH861E ring. The corrected and rejected sections use independent scales. HB/SNL transfers, key thickness and attachment details remain approximate; cones, ball reaction and engine interfaces are unfinished.</p><img src="comparison.png" alt="HB and SNL sources, corrected and rejected sections, bearing and positive sleeve"><p><a href="render_receipt.json">Source hashes, crop coordinates and limitations</a></p></html>')
print('Saved source comparison; visual inspection still required.')
