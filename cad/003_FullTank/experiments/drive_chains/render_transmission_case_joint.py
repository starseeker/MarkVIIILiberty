"""Saved-native case-joint inspection and fixed-scale SNL23 comparison."""
import argparse,base64
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_case_joint_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();candidate=a.candidate.resolve();out=candidate/'source_review';sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO
if not a.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,fitz
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    report=read(candidate/'report.json');native=candidate/'TransmissionCaseJointCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(JointCase=(.44,.56,.47),JointSeal=(.81,.49,.22),JointHardware=(.66,.67,.61),JointInterior=(.40,.56,.67))
    def role(n):
        if 'gasket' in n:return 'JointSeal'
        if 'CentralCaseJoint_' in n:return 'JointHardware'
        if n in report['changed_ids']:return 'JointCase'
        return 'JointInterior'
    def draw(names,name,title,direction=(1,-1,1.1),clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n+'_view',system=role(n)))
        shaded(selected,out/(name+'.svg'),direction,title)
    central=report['new_ids']+report['changed_ids']
    interior=[n for n in byid if n.startswith(('CenterBevel','PortBevel','StarboardBevel','Input')) or n=='CenterTransmissionCore_cross_shaft']
    draw(central+interior,'case_joint_overview','Central transmission | fourteen MX8 sets and two M326 gaskets; flange pattern inferred')
    draw([n for n in central if n!='CenterTransmissionCore_bevel_cover']+interior,'case_joint_open','Case joint inspection | cover hidden; fitted gaskets, bolt sets and existing bevel drive')
    draw(report['new_ids'],'case_joint_pattern','Joint pattern | fourteen separate bolt, castle-nut and split-pin sets; two shared-definition gaskets',(1,0,0))
    clip=Part.makeBox(110,36,45,origin+App.Vector(-55,-18,195))
    draw(central,'case_joint_section','Upper joint section | mating lands, gasket stock, through bolt and retained castle nut',(1,-1,1),clip)
    cal=read(ROOT/'transmission_input_calibration.json');src=REPO/cal['image'];assert sha(src)==cal['image_sha256']
    plane=Part.makePlane(1200,1200,origin+App.Vector(-600,0,-600),App.Vector(0,1,0))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="921">',f'<image width="1094" height="921" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}" opacity=".65"/>']
    colors={'JointCase':'#237b42','JointSeal':'#c56c15','JointHardware':'#c52b26','JointInterior':'#216fb0'}
    for n in central:
        for edge in byid[n]['shape'].section(plane).Edges:
            pts=[f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[role(n)]}" stroke-width="1.2"/>')
    svg.append('</svg>');path=out/'case_joint_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    panel=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="850">','<rect width="1600" height="850" fill="#f7f5ee"/>',
        '<text x="25" y="35" font-family="sans-serif" font-size="24">Central case joint | SNL23 and native section overlay</text>',
        '<text x="25" y="65" font-family="sans-serif" font-size="17">Unchanged input-bearing scale and shaft origin. Green case, orange gasket, red fasteners.</text>']
    for x,pic in [(25,src),(810,path.with_suffix('.png'))]:
        panel.append(f'<image x="{x}" y="90" width="760" height="640" href="data:image/png;base64,{base64.b64encode(pic.read_bytes()).decode()}"/>')
    panel+=['<text x="25" y="778" font-family="sans-serif" font-size="17">The drawing does not establish the complete transverse bolt pattern. Casting and flange contours remain inferred.</text>',
        '<text x="25" y="812" font-family="sans-serif" font-size="17">SNL27/252: fourteen MX8 sets and two M326 seals. HB121 uses different joint hardware marks; discrepancy retained.</text></svg>']
    path=out/'case_joint_comparison.svg';path.write_text('\n'.join(panel))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256={str(src.relative_to(REPO)):sha(src)},
        calibration_sha256=sha(ROOT/'transmission_input_calibration.json'),rasters={p.name:sha(p) for p in out.glob('*.png')},native_placements_changed=False,source_warping=False))
    assert sha(native)==report['native_sha256'];print('Rendered six case-joint views; native unchanged.',flush=True)
finally:runtime.close()
