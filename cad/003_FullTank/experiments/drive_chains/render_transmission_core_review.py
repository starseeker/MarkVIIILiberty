"""Compare native central case silhouette against source end view, without resaving."""
import argparse
import base64
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_core_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();candidate=args.candidate.resolve()
out=candidate/'source_review';sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import fitz
    from lib.cad_build import leaves
    from lib.visual_review import shaded
    report=read(candidate/'report.json');native=candidate/'TransmissionCoreCandidate.FCStd'
    assert sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    chosen=[i for i in items if i['id'] in ['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover']]
    assert len(chosen)==2
    shaded(chosen,out/'bevel_case_detail.svg',(1,1,.7),'M263 case and M264 cover | inferred cast contours and mounting webs')
    source=REPO/'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p295-geometry.png'
    image=base64.b64encode(source.read_bytes()).decode()
    width,height=1094,921;px,pz=595,492;scale=.9
    ox,oy,oz=report['shaft_axis_world_mm']
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height+82}">',
         f'<image width="{width}" height="{height}" href="data:image/png;base64,{image}" opacity=".66"/>']
    for item in chosen:
        color='#005bea' if item['id'].endswith('bevel_case') else '#b33511'
        for edge in item['shape'].Edges:
            coords=' '.join(f'{px-(v.x-ox)/scale:.3f},{pz-(v.z-oz)/scale:.3f}' for v in edge.discretize(Deflection=.5))
            svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.2"/>')
    rear=report['dimensions']['bevel_frame_local_mm']['rear']
    residual=px-rear/scale-866
    svg+=['<rect x="0" y="921" width="1094" height="82" fill="white"/>',
          '<text x="20" y="946" font-family="sans-serif" font-size="17">Blue: rear case; red: front cover. End projection, all edges; input bearings/gears omitted.</text>',
          '<text x="20" y="970" font-family="sans-serif" font-size="16">Inspection scale 0.9 mm/pixel, shaft center (595,492); estimated from case outline.</text>',
          f'<text x="20" y="991" font-family="sans-serif" font-size="15">Frame-front residual {residual:.1f} pixels. Shape comparison only; this is not an independent dimensional check.</text></svg>']
    path=out/'source_plate23_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as d:d[0].get_pixmap().save(str(path.with_suffix('.png')))
    assert sha(native)==report['native_sha256']
    write(out/'render_report.json',dict(passed=True,native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),
        renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),projection='end view, all native edges, source inspection only',
        source_center_px=[px,pz],inspection_mm_per_pixel=scale,frame_front_residual_px=residual,
        output_sha256={p.name:sha(p) for p in out.glob('*.png')},native_geometry_changed=False))
finally:runtime.close()
