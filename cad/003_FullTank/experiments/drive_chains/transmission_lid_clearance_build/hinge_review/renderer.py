"""Render a cap-only source comparison from the saved closed hinge candidate."""
import argparse
import base64
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_lid_clearance_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();candidate=args.candidate.resolve();out=candidate/'hinge_review'
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO

if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    from lib.cad_build import leaves
    from lib.visual_review import shaded
    import fitz
    r=read(candidate/'report.json');assert r['rendering_complete']
    native=candidate/'TransmissionLidCandidate.FCStd';assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));doc.recompute()
    names={'PortFixedBearing_outer_'+suffix for suffix in ['cap','lid','cover_pin']}
    selected=[i for i in leaves(doc.Root) if i['id'] in names];assert len(selected)==3
    shaded(selected,out/'closed_cap_detail.svg',(1,.8,.8),'Closed M298 cap, M295 cover and steel pin | hinge detail')
    shaded([i for i in selected if not i['id'].endswith('_lid')],out/'cap_receiver_detail.svg',
           (1,.6,1),'Cap and pin | cover omitted to inspect the integral receiving lugs')
    source=REPO/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/original_scans/MarkVIII011.jpg'
    source_data=base64.b64encode(source.read_bytes()).decode()
    native_data=base64.b64encode((out/'closed_cap_detail.png').read_bytes()).decode()
    scale=590/510
    svg=('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900">'
         '<rect width="1600" height="900" fill="#f6f4ed"/>'
         '<defs><clipPath id="source_clip"><rect x="30" y="80" width="590" height="650"/></clipPath></defs>'
         f'<g clip-path="url(#source_clip)"><image x="{30-240*scale}" y="{80-680*scale}" '
         f'width="{1849*scale}" height="{1343*scale}" preserveAspectRatio="none" href="data:image/jpeg;base64,{source_data}"/></g>'
         # MuPDF's SVG image rendering ignores this clipPath. Explicit paper
         # masks keep the same source crop in both browser and PNG outputs.
         '<g fill="#f6f4ed"><rect x="0" y="0" width="1600" height="80"/>'
         '<rect x="0" y="80" width="30" height="650"/>'
         '<rect x="620" y="80" width="980" height="650"/>'
         '<rect x="0" y="730" width="1600" height="170"/></g>'
         '<text x="30" y="36" font-family="sans-serif" font-size="24">Oil-cup cover hinge | handbook illustration and closed native candidate</text>'
         f'<image x="635" y="135" width="940" height="529" href="data:image/png;base64,{native_data}"/>'
         '<text x="30" y="779" font-family="sans-serif" font-size="19">HB20 Plate11: rear hinge with lid open. Native: closed cap only. Perspective views are not registered.</text>'
         '<text x="30" y="811" font-family="sans-serif" font-size="19">SNL56 pin:3/16 x2-1/2in. Integral knuckle sizes and the simplified casting profile remain inferred.</text>'
         '<text x="30" y="843" font-family="sans-serif" font-size="19">Visible differences: rounded cup/cast transitions, cap nuts, oil inlet and wool remain incomplete.</text>'
         '<text x="30" y="875" font-family="sans-serif" font-size="19">Static hinge fit is checked separately; pin retention and cover motion are not qualified.</text></svg>')
    (out/'source_hinge_detail.svg').write_text(svg)
    with fitz.open(stream=svg.encode(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(out/'source_hinge_detail.png'))
    result=dict(native_sha256=sha(native),candidate_report_sha256=sha(candidate/'report.json'),
                source_sha256=sha(source),script_sha256=sha(Path(__file__)),
                output_hashes={p.name:sha(p) for p in sorted(out.iterdir()) if p.suffix in ['.png','.svg']},
                camera_direction=[1,.8,.8],standard_closed_placement_retained=True,
                source_display_crop_not_dimensional_calibration=True)
    write(out/'render_report.json',result)
    (out/'renderer.py').write_bytes(Path(__file__).read_bytes())
    assert sha(native)==r['native_sha256']
    print('Saved cap-only review views.',flush=True)
finally:runtime.close()
