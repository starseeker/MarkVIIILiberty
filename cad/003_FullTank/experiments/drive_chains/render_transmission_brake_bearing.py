"""Render actual saved brake-bearing geometry and the unchanged SNL22 section."""
import argparse,base64,io
from pathlib import Path
import subprocess,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_brake_bearing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();candidate=a.candidate.resolve();out=candidate/'source_review';sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO
if not a.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,fitz
    from PIL import Image
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    report=read(candidate/'report.json');native=candidate/'TransmissionBrakeBearingCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(BearingCase=(.43,.53,.45),BearingCap=(.49,.63,.52),BearingBush=(.76,.55,.26),BearingJournal=(.35,.56,.69),BearingHardware=(.72,.33,.23),BearingShaft=(.62,.62,.57))
    def role(n):
        if 'BrakeBearing_bush' in n or n.endswith('dowel'):return 'BearingBush'
        if 'BrakeBearing_cap' in n:return 'BearingCap'
        if 'BrakeBearing_' in n:return 'BearingHardware'
        if n.endswith(('high_drum','plain_case')):return 'BearingJournal'
        if any(k in n for k in ['shaft','sun','ring']):return 'BearingShaft'
        return 'BearingCase'
    def draw(names,cut,name,title,direction=(1,-1,1.1),clip=None):
        selected=[]
        for n in names:
            i=byid[n];s=i['shape'].cut(cut) if cut is not None else i['shape']
            if clip is not None:s=s.common(clip)
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_view_'+n,system=role(n)))
        shaded(selected,out/(name+'.svg'),direction,title)
    names=report['new_ids']+['CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover','PortTransmissionCore_high_drum','StarboardTransmissionCore_high_drum','PortTransmissionCore_plain_case','StarboardTransmissionCore_plain_case']
    names += [n for n in byid if n.startswith('Input')]
    draw(names,None,'brake_bearings_overview','Transmission supports | paired M265 bushes, M266 caps and MX14 fasteners; casting architecture inferred')
    port=[n for n in report['new_ids'] if n.startswith('Port')]+['PortTransmissionCore_plain_case','PortTransmissionCore_high_drum','CenterTransmissionCore_bevel_case','PortSmallPlanetTrain_sun','PortSmallPlanetTrain_sun_bush','PortSunRetention_ring','CenterTransmissionCore_cross_shaft']
    cut=Part.makeBox(1000,2000,1000,origin+App.Vector(-500,-1000,0))
    draw(port,cut,'brake_bearing_section','Brake-bearing section | bronze bush spans adjacent case and drum journals; inference, not a proven original fit')
    clip=Part.makeBox(244,80,122,origin+App.Vector(-122,240,-122))
    draw(port,None,'brake_bearing_close_section','Brake bearing close section | common bronze bush, adjacent journals, cap dowel and lower stud; clipped for inspection',clip=clip)
    draw([n for n in report['new_ids'] if n.startswith('Port')],None,'brake_bearing_joint','M265/M266 joint | separate flanged bush, cap, M300 dowel and two MX14 sets; rear saddle omitted for inspection')
    draw(['PortBrakeBearing_'+k+'0' for k in ['stud','nut','cotter']],None,'brake_bearing_fastener','MX14 stud | detailed-list length1-11/16in; owning-list1-9/16in conflict retained; half-inch castle nut')
    cal=read(ROOT/'transmission_output_calibration.json');src=REPO/cal['image'];assert sha(src)==cal['image_sha256']
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    plane=Part.makePlane(3000,3000,origin+App.Vector(-1500,-1500,0),App.Vector(0,0,1))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}" opacity=".65"/>']
    colors={'BearingCase':'#426d43','BearingCap':'#317836','BearingBush':'#b26f08','BearingJournal':'#166f98','BearingHardware':'#c63524','BearingShaft':'#696969'}
    for n in port:
        for edge in byid[n]['shape'].section(plane).Edges:
            pts=[f'{cal["sprocket_center_x_px"]-(v.y-output_y)/cal["mm_per_pixel"]:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.15)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[role(n)]}" stroke-width="1"/>')
    svg.append('</svg>');path=out/'brake_bearing_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    panels=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1000">','<rect width="1440" height="1000" fill="#f7f5ee"/>',
        '<text x="25" y="35" font-family="sans-serif" font-size="24">Brake-bearing reconstruction | original section and saved native section</text>',
        '<text x="25" y="65" font-family="sans-serif" font-size="17">Green cap/case, bronze bush/dowel, blue journals. Unchanged output scale; no image warping.</text>']
    for x,pic,title in [(25,src,'SNL Plate22'),(735,path.with_suffix('.png'),'Native geometry over source')]:
        with Image.open(pic) as im:
            buf=io.BytesIO();im.crop((1100,220,1420,740)).save(buf,format='PNG');encoded=base64.b64encode(buf.getvalue()).decode()
        panels += [f'<text x="{x}" y="100" font-family="sans-serif" font-size="21">{title}</text>',f'<image x="{x}" y="120" width="448" height="728" href="data:image/png;base64,{encoded}"/>']
    panels += ['<text x="25" y="893" font-family="sans-serif" font-size="17">M263 bridge and joint architecture inferred. M269 hub thickened to the inherited M277 journal radius.</text>',
        '<text x="25" y="923" font-family="sans-serif" font-size="17">Printed381mm drum OD retained despite source-outline difference. Dowel size is printed; its position is assumed.</text>',
        '<text x="25" y="953" font-family="sans-serif" font-size="17">Prior32.113mm bevel/output registration difference remains; this view does not resolve it.</text></svg>']
    path=out/'brake_bearing_comparison.svg';path.write_text('\n'.join(panels))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(path.with_suffix('.png')))
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256={str(src.relative_to(REPO)):sha(src)},calibration_sha256=sha(ROOT/'transmission_output_calibration.json'),rasters={p.name:sha(p) for p in out.glob('*.png')},native_placements_changed=False,source_warping=False,limitations=report['limitations']))
    assert sha(native)==report['native_sha256'];print('Rendered seven brake-bearing views; native unchanged.',flush=True)
finally:runtime.close()
