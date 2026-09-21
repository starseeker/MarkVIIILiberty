"""Compare saved front-clutch sections with original HB and SNL figures."""
import argparse,base64,hashlib,html,json
from pathlib import Path
import fitz
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'front_clutch_build')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
report=read(base/'report.json')
hb=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png'
snl=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
inputs=[hb,snl]+[base/'previews'/n for n in ['section.png','mechanism.png','clamp_section.png','spring_hidden.png']]
def embed(path,x,y,w,h):
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
def text(x,y,value,size=18):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}">{html.escape(value)}</text>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2210">','<rect width="1800" height="2210" fill="#f6f4ed"/>',
    text(30,38,'Front clutch coupling and spring | original evidence and native reconstruction',27),
    text(30,70,'Independent panel scales; original orientations retained. The main compound clutch remains under construction.'),
    text(30,110,'HB71 / printed116: transmission left, engine right',21),embed(hb,20,125,860,640),
    text(910,110,'SNL Plate21: engine left, transmission right',21),embed(snl,900,125,880,640),
    text(30,805,'Native centre section: transmission left, future main clutch to the right',21),
    embed(base/'previews/section.png',20,820,880,495),embed(base/'previews/mechanism.png',900,820,880,495),
    text(30,1345,'Transverse collar section and exposed coupling interfaces',21),
    embed(base/'previews/clamp_section.png',20,1360,880,495),embed(base/'previews/spring_hidden.png',900,1360,880,495)]
notes=[
    'Both originals show the external coil between a shaft clamp and the front coupling flange; the rounded shaft shoulders are retained.',
    'HB identifies this coupling as SH864B; SNL identifies SH945A. Transferred 9in flange and 5in body diameters remain provisional.',
    'SH849A/B identities agree. HB gives five free coils plus two seating coils, 5-3/8in spiral diameter and 4-1/4in coil length.',
    'The selected diameter is interpreted as inside diameter; 1/2in wire, installed length, end grinding and spring clocking are inferred.',
    'SNL33:004 lists two bolt/nut/washer sets for the two flange halves. The transverse bolt positions and lug profiles are estimates.',
    'Plate21 callout25 is indexed at SNL33:005 to a different cleat bolt; retain that mismatch. Selection follows the SH849A allocation.',
    'The source centre sections project clamp hardware into view; the true CAD centre cut misses those off-axis bolts. See transverse cut.',
    'Six empty flange holes reserve the HB118 collar joint. SH999A, its actual fasteners, bearings, cones and SH849C are still pending.',
    'Hidden coupling profiles, axial stations and fillet sizes remain approximations; these panels do not establish exact historical fit.'
]
for n,note in enumerate(notes):svg.append(text(30,1890+36*n,note))
svg.append('</svg>');path=out/'comparison.svg';path.write_text(''.join(svg))
with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
receipt=dict(native_sha256=report['native_sha256'],renderer_sha256=sha(Path(__file__)),
    input_hashes={str(p.relative_to(REPO)):sha(p) for p in inputs},
    output_hashes={p.name:sha(p) for p in [path,path.with_suffix('.png')]},
    orientation='Native section follows HB; SNL reversed in the original. Each panel independently fitted; no matched-scale claim.',
    measurement_limit='Visual structure and source identity comparison; no pixel calibration or scan-distortion correction added.',notes=notes)
(out/'render_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Front clutch source comparison</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}p{max-width:100ch}</style><h1>Front clutch comparison</h1><p>Original HB and SNL sections beside the native reconstruction. Independent scales and opposite source orientations. Dimensional transfers and inferred details remain documented approximations.</p><img src="comparison.png" alt="Original clutch sections, native spring and coupling, and transverse split-collar section"><p><a href="render_receipt.json">Source hashes and comparison notes</a></p></html>')
print('Saved comparison; visual inspection remains required.')
