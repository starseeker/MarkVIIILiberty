"""Review saved bearing stacks with both explicit source registrations."""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_bevel_sleeve_build');p.add_argument('--worker',action='store_true')
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
    report=read(candidate/'report.json');native=candidate/'TransmissionBevelSleeveCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(BevelSleeve=(.29,.55,.68),BevelBush=(.74,.51,.24),BevelRetainer=(.78,.30,.20),BevelShaft=(.53,.57,.59),BevelCase=(.43,.55,.43))
    def color(name):
        if 'bush' in name or 'dowel' in name:return 'BevelBush'
        if 'retainer' in name or 'screw' in name or 'SunRetention' in name:return 'BevelRetainer'
        if name.endswith('sleeve') or name.endswith('sun'):return 'BevelSleeve'
        if 'shaft' in name:return 'BevelShaft'
        return 'BevelCase'
    def section(names,crop,path,direction,title):
        selected=[]
        for name in names:
            i=byid[name];s=i['shape'].common(crop)
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_section_'+name,system=color(name)))
        shaded(selected,path,direction,title)
    central=[i['id'] for i in items if i['id'].startswith(('PortBevelWheelSupports_','StarboardBevelWheelSupports_','CenterTransmissionCore_'))]
    section(central,box(origin.x-280,origin.x+280,-180,180,origin.z-260,origin.z),out/'bevel_support_section.svg',(1,-1,1.2),
        'Central bevel supports | blue sleeves, bronze bushes, red oil retainers; bevel wheels and clutch pending')
    overview=[i['id'] for i in items if i['id'].startswith(('PortSmallPlanet','PortPlanet','PortTransmissionCore_','PortSunRetention_','PortBevelWheelSupports_','StarboardBevelWheelSupports_','CenterTransmissionCore_'))]
    section(overview,box(origin.x-320,origin.x+320,-180,650,origin.z-320,origin.z),out/'transmission_support_cutaway.svg',(1,-1,1.2),
        'Transmission cutaway | bevel support stack and assembly-compatible shaft journals (inferred dimensions)')
    journal=['CenterTransmissionCore_cross_shaft','PortSmallPlanetTrain_sun','PortSmallPlanetTrain_sun_bush','PortSunRetention_ring']+[n for n in central if n.startswith('PortBevelWheelSupports_')]
    section(journal,box(origin.x-80,origin.x+80,-70,430,origin.z-90,origin.z),out/'shaft_bearing_section.svg',(1,-1,1.2),
        'Shaft and bearing section | larger central spline; bushes pass smaller outboard splines')
    cal=read(ROOT/'transmission_output_calibration.json');source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    names=[n for n in central if not n.startswith('Starboard')]
    colors=dict(BevelSleeve='#197798',BevelBush='#9e6813',BevelRetainer='#d13219',BevelShaft='#63717b',BevelCase='#247443')
    for registration in ['local','output']:
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',
            f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".62"/>']
        for name in names:
            for edge in byid[name]['shape'].section(plane).Edges:
                pts=[]
                for v in edge.discretize(Deflection=.2):
                    x=1534-v.y/cal['mm_per_pixel'] if registration=='local' else cal['sprocket_center_x_px']-(v.y-output_y)/cal['mm_per_pixel']
                    pts.append(f'{x:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}')
                svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[color(name)]}" stroke-width="1.0"/>')
        svg.append('</svg>');path=out/f'bevel_support_overlay_{registration}.svg';path.write_text('\n'.join(svg))
        with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    def crop64(p):
        with Image.open(p) as im:
            buf=io.BytesIO();im.crop((1240,280,1650,840)).save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1070">','<rect width="1800" height="1070" fill="#f7f5ee"/>',
        '<text x="30" y="36" font-family="sans-serif" font-size="24">Bevel sleeve supports | source and actual native shaft-height sections</text>',
        '<text x="30" y="67" font-family="sans-serif" font-size="18">Blue M259, bronze M261/M262, red M310/screw, green case. Source scale retained; two axial registrations shown explicitly.</text>']
    for x,pic,title in [(30,source,'Original SNL Plate22'),(620,out/'bevel_support_overlay_local.png','Local bevel-center registration'),(1210,out/'bevel_support_overlay_output.png','Inherited output registration')]:
        svg.append(f'<text x="{x}" y="108" font-family="sans-serif" font-size="22">{title}</text>')
        svg.append(f'<image x="{x}" y="126" width="560" height="765" href="data:image/png;base64,{crop64(pic)}"/>')
    offset=report['dimensions']['registration_difference_from_output_mm']
    svg.extend([f'<text x="30" y="935" font-family="sans-serif" font-size="19">Axial conflict: {offset:.3f} mm. Local origin x1534 aligns the already centered case; the output datum is not changed.</text>',
        '<text x="30" y="972" font-family="sans-serif" font-size="19">Enlarged journals and bush/sleeve diameters are assembly-path hypotheses; outlines differ from the drawing.</text>',
        '<text x="30" y="1009" font-family="sans-serif" font-size="19">Bevel gear wheels, clutch rings, central clutch, shims and rivets remain absent. These supports do not complete the axial stack.</text></svg>'])
    path=out/'bevel_support_comparison.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    rasters={p.name:sha(p) for p in out.glob('*.png')}
    report.update(rendering_complete=True,output_raster_hashes=rasters);write(candidate/'report.json',report)
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),rasters=rasters,
        registration_difference_mm=offset,source_scale_mm_per_pixel=cal['mm_per_pixel'],local_origin_x_px=1534,
        view='Actual native shaft-height sections and lower-half cutaways; no stored placements changed.',
        limitations=['Two source registrations disagree.','Journal steps, diameters and bearing/casting forms inferred.','Central bevel gears and complete axial retention remain pending.']))
    assert sha(native)==report['native_sha256'];print('Rendered six images; native unchanged.',flush=True)
finally:runtime.close()
