"""Render native bevel geometry and preserve both conflicting source registrations."""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_bevel_gear_build');p.add_argument('--worker',action='store_true')
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
    report=read(candidate/'report.json');native=candidate/'TransmissionBevelGearCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(BevelGear=(.31,.54,.68),BevelBush=(.75,.52,.24),BevelClutch=(.76,.31,.22),BevelShaft=(.53,.57,.59),BevelCase=(.43,.55,.43),BevelBearing=(.68,.65,.53))
    def color(name):
        if 'clutch' in name or 'rivet' in name or 'shim' in name:return 'BevelClutch'
        if 'bush' in name or 'dowel' in name:return 'BevelBush'
        if 'ThrustBearing' in name:return 'BevelBearing'
        if 'wheel' in name or 'pinion' in name or name.endswith(('sleeve','sun')):return 'BevelGear'
        if 'shaft' in name:return 'BevelShaft'
        return 'BevelCase'
    def section(names,crop,path,direction,title):
        selected=[]
        for name in names:
            i=byid[name];s=i['shape'].common(crop) if crop is not None else i['shape']
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_section_'+name,system=color(name)))
        shaded(selected,path,direction,title)
    central=[i['id'] for i in items if i['id'].startswith(('PortBevel','StarboardBevel','PortThrustBearing','StarboardThrustBearing','CenterTransmissionCore_','CenterBevelDrive_'))]
    section(central,box(origin.x-280,origin.x+460,-230,230,origin.z-260,origin.z),out/'bevel_drive_section.svg',(1,-1,1.2),
        'Bevel drive cutaway | 14/46 teeth, four-dog clutch in ahead engagement; bearing internals inferred')
    exposed=[n for n in central if not n.endswith(('bevel_case','bevel_cover'))]
    section(exposed,None,out/'bevel_mesh_isometric.svg',(1,-1,1.2),
        'Bevel drive | actual native gears and clutch; case hidden for inspection, no placements changed')
    overview=[i['id'] for i in items if i['id'].startswith(('PortSmallPlanet','PortPlanet','PortTransmissionCore_','PortSunRetention_'))]+central
    section(overview,box(origin.x-320,origin.x+460,-230,650,origin.z-320,origin.z),out/'transmission_bevel_cutaway.svg',(1,-1,1.2),
        'Transmission cutaway | bevel drive and thrust stack populated; controls, input bearings and other details pending')
    bearing=[n for n in central if n.startswith(('PortBevelWheelSupports_','PortThrustBearing_'))]+['PortBevelDrive_shim','PortBevelDrive_wheel','CenterTransmissionCore_bevel_case','CenterTransmissionCore_bevel_cover','CenterTransmissionCore_cross_shaft']
    section(bearing,box(origin.x-100,origin.x+100,55,210,origin.z-100,origin.z),out/'thrust_bearing_section.svg',(1,-1,1.2),
        'Thrust bearing section | printed105 x155 x40mm envelope; races, cage and16 balls are inferred')
    cal=read(ROOT/'transmission_output_calibration.json');source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    names=[n for n in central if not n.startswith('Starboard')]
    colors=dict(BevelGear='#197798',BevelBush='#9e6813',BevelClutch='#d13219',BevelShaft='#63717b',BevelCase='#247443',BevelBearing='#945eb0')
    for registration in ['local','output']:
        svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1300">',
            '<rect width="1724" height="1300" fill="#f7f5ee"/>',
            f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".62"/>']
        for name in names:
            for edge in byid[name]['shape'].section(plane).Edges:
                pts=[]
                for v in edge.discretize(Deflection=.2):
                    x=1534-v.y/cal['mm_per_pixel'] if registration=='local' else cal['sprocket_center_x_px']-(v.y-output_y)/cal['mm_per_pixel']
                    pts.append(f'{x:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}')
                svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[color(name)]}" stroke-width="1.0"/>')
        svg.append('</svg>');path=out/f'bevel_drive_overlay_{registration}.svg';path.write_text('\n'.join(svg))
        with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    def crop64(p):
        with Image.open(p) as im:
            canvas=Image.new('RGB',(1724,1300),'#f7f5ee');canvas.paste(im,(0,0))
            buf=io.BytesIO();canvas.crop((1230,270,1680,1220)).save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1480">','<rect width="1800" height="1480" fill="#f7f5ee"/>',
        '<text x="30" y="36" font-family="sans-serif" font-size="24">Bevel drive | source and actual native shaft-height sections</text>',
        '<text x="30" y="67" font-family="sans-serif" font-size="18">Blue gears/sleeves, red clutch/rivets/shim, purple bearings, green case. Scale retained; no image fitting.</text>']
    for x,pic,title in [(30,source,'Original SNL Plate22'),(620,out/'bevel_drive_overlay_local.png','Local bevel-center registration'),(1210,out/'bevel_drive_overlay_output.png','Inherited output registration')]:
        svg.append(f'<text x="{x}" y="108" font-family="sans-serif" font-size="22">{title}</text>')
        svg.append(f'<image x="{x}" y="126" width="550" height="1161" href="data:image/png;base64,{crop64(pic)}"/>')
    offset=report['dimensions']['registration_difference_from_output_mm']
    svg.extend([f'<text x="30" y="1320" font-family="sans-serif" font-size="19">Axial conflict remains: {offset:.3f}mm. Printed tooth pitch and bearing envelope constrain the reconstruction.</text>',
        '<text x="30" y="1358" font-family="sans-serif" font-size="19">Support lengths now meet the retained sun/drum datums; this mechanical fit does not establish historical proportions.</text>',
        '<text x="30" y="1396" font-family="sans-serif" font-size="19">The provisional input shaft extends beyond the illustrated end; its bearing/housing/coupling stack is still absent.</text>',
        '<text x="30" y="1434" font-family="sans-serif" font-size="19">Shaft steps, clutch profile, rivet pattern and bearing internals remain inferred; no source pixels are stretched.</text></svg>'])
    path=out/'bevel_drive_comparison.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    rasters={p.name:sha(p) for p in out.glob('*.png')}
    report.update(rendering_complete=True,output_raster_hashes=rasters);write(candidate/'report.json',report)
    write(out/'render_receipt.json',dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),rasters=rasters,
        registration_difference_mm=offset,source_scale_mm_per_pixel=cal['mm_per_pixel'],local_origin_x_px=1534,
        view='Actual native sections and cutaways; no stored placements changed.',
        limitations=['Two source registrations disagree.','Inferred gear corrections, cast forms, joints and bearing internals.',
            'Provisional input shaft extends beyond the illustrated end; input bearings/housing and complete transmission remain pending.']))
    assert sha(native)==report['native_sha256'];print('Rendered seven images; native unchanged.',flush=True)
finally:runtime.close()
