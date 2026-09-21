"""Render saved reversing controls and their unchanged-scale SNL23 comparison."""
import argparse,base64,subprocess,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_reversing_build');p.add_argument('--worker',action='store_true')
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
    report=read(candidate/'report.json');native=candidate/'TransmissionReversingCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)};origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(Control=(.76,.50,.20),Case=(.44,.56,.47),Seal=(.82,.5,.25),Hardware=(.66,.67,.61),Interior=(.40,.56,.67))
    def role(n):
        if n.startswith('ReversingControl'):return 'Control'
        if 'gasket' in n:return 'Seal'
        if 'CentralCaseJoint_' in n:return 'Hardware'
        if n.startswith('CenterTransmissionCore_bevel'):return 'Case'
        return 'Interior'
    def draw(names,name,title,direction=(1,1,1.1),clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'] if clip is None else i['shape'].common(clip)
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=n+'_view',system=role(n)))
        shaded(selected,out/(name+'.svg'),direction,title)
    central=[n for n in byid if n.startswith(('ReversingControl','CentralCaseJoint','CenterBevel','PortBevel','StarboardBevel','Input')) or n in ['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover','CenterTransmissionCore_cross_shaft']]
    draw(central,'reversing_overview','Central transmission | reversing fork, sliding rod and spring detent added')
    draw([n for n in central if n not in ['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover']],'reversing_open','Reversing controls | both case halves hidden to expose installed mechanism')
    draw(report['new_ids']+['CenterBevelDrive_clutch','PortBevelDrive_clutch_ring','StarboardBevelDrive_clutch_ring'],
        'reversing_mechanism','Fork and detent | inferred profiles, continuous groove and shortened ring tips')
    x,z=-181.46496913580248,159.35756172839505
    clip=Part.makeBox(45,70,90,origin+App.Vector(x,-166,145))
    draw(report['new_ids']+['CenterTransmissionCore_bevel_case'],'reversing_detent',
        'Detent section | bored case, seated plunger, compressed spring and hollow screw cap',(1,.7,.6),clip)
    cal=read(ROOT/'transmission_input_calibration.json');src=REPO/cal['image'];assert sha(src)==cal['image_sha256']
    plane=Part.makePlane(1200,1200,origin+App.Vector(-600,0,-600),App.Vector(0,1,0))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="921">',f'<image width="1094" height="921" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}" opacity=".65"/>']
    for n in report['new_ids']+['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover']:
        s=byid[n]['shape'];s=s.section(plane) if n.startswith('CenterTransmissionCore') else s
        color='#237b42' if n.startswith('CenterTransmissionCore') else '#a22b17'
        for edge in s.Edges:
            pts=[f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.1"/>')
    svg.append('</svg>');path=out/'reversing_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    panel=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="850">','<rect width="1600" height="850" fill="#f7f5ee"/>',
        '<text x="25" y="35" font-family="sans-serif" font-size="24">Reversing fork and rod | SNL23 and saved native projection</text>',
        '<text x="25" y="65" font-family="sans-serif" font-size="17">Unchanged input-bearing scale and shaft origin. Red controls, green central case section.</text>']
    for xx,pic in [(25,src),(810,path.with_suffix('.png'))]:
        panel.append(f'<image x="{xx}" y="90" width="760" height="640" href="data:image/png;base64,{base64.b64encode(pic.read_bytes()).decode()}"/>')
    panel+=['<text x="25" y="778" font-family="sans-serif" font-size="17">Rod axis follows the source pick; fork width, hub, detent and transverse offsets remain inferred.</text>',
        '<text x="25" y="812" font-family="sans-serif" font-size="17">M303–M306 vertical linkage and its MX11/MX12 attachments remain pending. Standard forward assembly only.</text></svg>']
    path=out/'reversing_comparison.svg';path.write_text('\n'.join(panel))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256={str(src.relative_to(REPO)):sha(src)},
        calibration_sha256=sha(ROOT/'transmission_input_calibration.json'),rasters={p.name:sha(p) for p in out.glob('*.png')},native_placements_changed=False,source_warping=False))
    assert sha(native)==report['native_sha256'];print('Rendered six reversing-control views; native unchanged.',flush=True)
finally:runtime.close()
