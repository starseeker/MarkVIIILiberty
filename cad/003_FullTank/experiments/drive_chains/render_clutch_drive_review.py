"""Compose native CAD sections beside original HB71 and SNL21 evidence."""
import argparse,base64,html,json
from pathlib import Path
import fitz
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_drive_build')
a=p.parse_args();base=a.candidate.resolve();out=base/'source_review';out.mkdir(parents=True,exist_ok=True)
import hashlib
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=json.loads((base/'report.json').read_text())
hb=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate71.png'
snl=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
def embed(path,x,y,w,h):
    data=base64.b64encode(path.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>'
def text(x,y,value,size=20):return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}">{html.escape(value)}</text>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1750">','<rect width="1800" height="1750" fill="#f6f4ed"/>',
    text(30,36,'Clutch-stop drive | source comparison, with independent panel scales',26),
    text(30,68,'Handbook shaft SH864A and catalogue shaft SH1000A remain distinct identities. Hidden transverse form is inferred.',18),
    text(30,110,'HB71 / printed116: transmission left, engine right'),embed(hb,20,130,860,675),
    text(910,110,'SNL Plate21: engine left, transmission right'),embed(snl,900,130,880,675),
    text(30,845,'Native section: transmission left, engine interface right; main clutch and brake band remain unfinished.'),
    embed(base/'previews/section.png',20,865,880,495),embed(base/'previews/open.png',900,865,880,495),
    text(30,1400,'Evidence comparison and remaining approximations',24)]
notes=[
    'Eight coupling-box fasteners agree across SNL31:013 and HB118. Both sources show an enclosing stop drum and captured shaft head.',
    'Nominal stop-drum diameter228.6mm: rough shaft-relative source picks suggest about241mm (HB) and227mm (SNL).',
    'Nominal drum axial extent99mm: rough source picks suggest about84mm (HB) and96mm (SNL); the HB discrepancy remains explicit.',
    'The head was widened from76 to100mm after comparison with roughly111mm (HB) and95mm (SNL) sections; transverse form remains inferred.',
    'The front spline form is approximate; its diameter/length transfer from HB does not prove applicability to the SNL shaft.',
    'The physical54in belt loop uses an assumed pitch convention. Junction scores do not identify/count the proprietary belt links.',
    'Pump support profiles remain unverified in the obscured installed source view. These panels do not establish historical fit.'
]
for n,note in enumerate(notes):svg.append(text(30,1440+37*n,note,18))
svg.append('</svg>');path=out/'comparison.svg';path.write_text(''.join(svg))
with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
picks=[dict(source='HB71',shaft_diameter_px=[508,615],drum_diameter_px=[308,815],drum_axial_px=[168,345],
    head_section_px=[445,679],estimated_head_section_mm=234/107*50.8,
    estimated_diameter_mm=507/107*50.8,estimated_axial_mm=177/107*50.8),
    dict(source='SNL21',shaft_diameter_px=[528,616],drum_diameter_px=[373,766],drum_axial_px=[1068,1235],
    head_section_px=[483,648],estimated_head_section_mm=165/88*50.8,
    estimated_diameter_mm=393/88*50.8,estimated_axial_mm=167/88*50.8)]
receipt=dict(native_sha256=report['native_sha256'],renderer_sha256=sha(Path(__file__)),
    input_hashes={str(p.relative_to(REPO)):sha(p) for p in [hb,snl,base/'previews/section.png',base/'previews/open.png']},
    output_hashes={p.name:sha(p) for p in [path,path.with_suffix('.png')]},
    manual_coarse_picks=picks,measurement_limit='Approximate pixel endpoints, at least +/-8px body-span uncertainty plus unknown figure/scan distortion. Shape comparison, not metrology.',
    orientation='Original source orientations retained; native section follows HB. Panels independently fitted; no matched-scale claim.',notes=notes)
(out/'render_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Clutch drive source review</title><style>body{font:18px system-ui;background:#f6f4ed;margin:24px}img{max-width:100%}p{max-width:100ch}</style><h1>Clutch-stop drive comparison</h1><p>Original HB and SNL sections, native reconstruction, and explicit differences. Independent scales; main clutch construction remains open.</p><img src="comparison.png" alt="Two original clutch sections above native section and exposed shaft assembly"><p><a href="render_receipt.json">Source hashes and coarse measurement notes</a></p></html>')
print('Source comparison saved; visual inspection still required.')
