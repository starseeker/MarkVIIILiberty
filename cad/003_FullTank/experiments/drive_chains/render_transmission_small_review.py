"""Compare actual saved small-train sections with the original SNL Plate22."""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_small_build');p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();candidate=args.candidate.resolve();out=candidate/'source_review';sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(candidate),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    import fitz
    from PIL import Image
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    from transmission_core_parts import box
    report=read(candidate/'report.json');native=candidate/'TransmissionSmallCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=App.Vector(*report['shaft_axis_world_mm']);keys=report['keys_by_id']
    COLORS.update(SmallGear=(.64,.51,.31),SmallMetal=(.52,.59,.62),SmallBush=(.69,.51,.24),SmallCase=(.43,.56,.49))
    selected=[]
    for item in items:
        name=item['id']
        if not name.startswith('PortSmallPlanetTrain_') and name not in ['CenterTransmissionCore_cross_shaft','PortTransmissionCore_plain_case','PortTransmissionCore_high_drum']:continue
        key=keys.get(name);color='SmallBush' if key=='sun_bush' else 'SmallGear' if key in ['sun','planet','ring'] else 'SmallMetal' if key else 'SmallCase'
        selected.append(dict(item,system=color))
    coupled=[];crop=box(origin.x-320,origin.x+320,190,640,origin.z-320,origin.z)
    for item in items:
        name=item['id']
        if not name.startswith(('PortSmallPlanetTrain_','PortPlanetTrain_','PortPlanetSupports_','PortTransmissionCore_')) and name!='CenterTransmissionCore_cross_shaft':continue
        s=item['shape'].common(crop)
        if s.isNull() or not s.Solids:continue
        key=keys.get(name)
        color='SmallBush' if key=='sun_bush' or '_bronze' in name else 'SmallGear' if key in ['sun','planet','ring'] or name.startswith('PortPlanetTrain_') else 'SmallCase' if 'TransmissionCore_' in name else 'SmallMetal'
        coupled.append(dict(item,system=color,shape=s,target=SimpleNamespace(Shape=s),definition=item['definition']+'_coupled_'+name))
    shaded(coupled,out/'coupled_trains_cutaway.svg',(1,-1,1.2),'Coupled planetary trains | small gears and riveted disk added; small pin supports remain pending')
    detail=[];crop=box(origin.x-95,origin.x+95,190,425,origin.z-70,origin.z)
    for item in selected:
        s=item['shape'].common(crop)
        if s.isNull() or not s.Solids:continue
        detail.append(dict(item,shape=s,target=SimpleNamespace(Shape=s),definition=item['definition']+'_section_'+item['id']))
    shaded(detail,out/'sun_sleeve_section.svg',(1,-1,1.4),'Small sun sleeve section | separate bush, smooth shaft journal and high-speed drum spline')
    joint=[];crop=box(origin.x+194,origin.x+230,350,422,origin.z-18,origin.z)
    for item in selected:
        s=item['shape'].common(crop)
        if s.isNull() or not s.Solids:continue
        joint.append(dict(item,shape=s,target=SimpleNamespace(Shape=s),definition=item['definition']+'_rivet_cut_'+item['id']))
    shaded(joint,out/'rivet_joint_section.svg',(1,-1,1.5),'Ring-to-disk joint | separate button-head rivet and inferred cast lap')
    cal=read(ROOT/'transmission_output_calibration.json');source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    rivet_y=byid['PortSmallPlanetTrain_rivet8']['shape'].Solids[0].CenterOfMass.y
    rivet_x=cal['sprocket_center_x_px']-(rivet_y-output_y)/cal['mm_per_pixel']
    rivet_residual=(rivet_x-1065)*cal['mm_per_pixel']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',
        f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".60"/>']
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    colors={'sun':'#00823c','planet':'#b16a00','ring':'#ba2631','disk':'#1764ba','sun_bush':'#af7700','rivet':'#832ca3'}
    for item in selected:
        color=colors.get(keys.get(item['id']),'#287886')
        for edge in item['shape'].section(plane).Edges:
            points=[f'{cal["sprocket_center_x_px"]-(v.y-output_y)/cal["mm_per_pixel"]:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.3)]
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.4"/>')
    svg+=['<rect x="25" y="1040" width="1670" height="84" fill="white"/>',
        '<text x="40" y="1070" font-family="sans-serif" font-size="18">Small train: green sun, ochre planets, red ring, blue disk, purple rivets; cyan retained case/drum and revised shaft.</text>',
        '<text x="40" y="1100" font-family="sans-serif" font-size="17">Original scale retained. Printed teeth/pitch control radii; casting profiles and sleeve/shaft bearing fits are approximations.</text></svg>']
    path=out/'small_train_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    def cropped(path):
        with Image.open(path) as im:
            buffer=io.BytesIO();im.crop((980,215,1330,900)).save(buffer,format='PNG');return base64.b64encode(buffer.getvalue()).decode()
    panels=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1160">','<rect width="1280" height="1160" fill="#f7f5ee"/>',
        '<text x="30" y="32" font-family="sans-serif" font-size="23">Small planetary train | source and actual native shaft-height section</text>',
        '<text x="30" y="62" font-family="sans-serif" font-size="17">30 / inferred 24 / 78 teeth at 5-7 DP. M276 disk tooth-row conflict remains documented.</text>']
    for x,im,title in [(30,source,'Original SNL Plate22'),(650,path.with_suffix('.png'),'Native section overlay')]:
        panels.append(f'<text x="{x}" y="100" font-family="sans-serif" font-size="20">{title}</text>')
        panels.append(f'<image x="{x+45}" y="120" width="480" height="940" href="data:image/png;base64,{cropped(im)}"/>')
    panels+=[f'<text x="30" y="1100" font-family="sans-serif" font-size="17">Planet-center radius is {report["dimensions"]["source_planet_center_residual_mm"]:.3f} mm above the chosen source pick. Small pin/bush/ring support stacks remain absent.</text>',
        f'<text x="30" y="1130" font-family="sans-serif" font-size="17">Rivet center differs axially by {abs(rivet_residual):.3f} mm; disk/rim casting contours and head form remain approximations.</text></svg>']
    path=out/'small_train_comparison.svg';path.write_text('\n'.join(panels))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    receipt=dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),
        rasters={p.name:sha(p) for p in out.glob('*.png')},view='Actual horizontal section at shaft height; no native placements changed.',
        planet_center_comparison=dict(source_y_px=739,native_y_px=560+137.16/cal['mm_per_pixel'],residual_mm=report['dimensions']['source_planet_center_residual_mm']),
        rivet_axial_comparison=dict(approximate_source_x_px=1065,native_center_x_px=rivet_x,residual_mm=rivet_residual,
            interpretation='The illustrated upper rim rivet is approximately centered atx1065. The modeled flat web and printed-rivet grip put it farther outboard. A swept disk/rim profile and case-envelope review remain needed; no silent image rescaling.'),
        limitations=['Input axial picks control face stations; not independent dimensions.','Rivet stock and quantity are printed; button-head contour, upsetting allowance and lap form are inferred.','Small pin supports and complete bearing/retention installations are unfinished.'])
    assert sha(native)==report['native_sha256'];write(out/'render_receipt.json',receipt)
    print('Rendered five source/detail images; saved native unchanged.',flush=True)
finally:runtime.close()
