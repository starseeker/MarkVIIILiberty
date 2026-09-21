"""Render saved native ring/drum sections against the unchanged source scale."""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_sun_retention_build');p.add_argument('--worker',action='store_true')
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
    report=read(candidate/'report.json');native=candidate/'TransmissionSunRetentionCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(RetentionRing=(.78,.30,.20),RetentionSun=(.61,.52,.29),RetentionDrum=(.46,.57,.62),RetentionBush=(.70,.49,.22),RetentionCase=(.45,.56,.45))
    def color(name):
        return 'RetentionRing' if 'SunRetention' in name else 'RetentionBush' if 'bush' in name or 'bronze' in name else 'RetentionSun' if 'SmallPlanetTrain_sun' in name else 'RetentionDrum' if 'high_drum' in name else 'RetentionCase'
    def section(names,crop,path,direction,title):
        selected=[]
        for name in names:
            i=byid[name];s=i['shape'].common(crop)
            if s.isNull() or not s.Solids:continue
            selected.append(dict(i,shape=s,target=SimpleNamespace(Shape=s),definition=i['definition']+'_section_'+name,system=color(name)))
        shaded(selected,path,direction,title)
    names=['PortSunRetention_ring','PortSmallPlanetTrain_sun','PortSmallPlanetTrain_sun_bush','PortTransmissionCore_high_drum','CenterTransmissionCore_cross_shaft']
    section(names,box(origin.x-90,origin.x+90,195,382,origin.z-90,origin.z),out/'sun_retention_section.svg',(1,-1,1.2),
        'Small sun / high-speed drum | red M290 ring, groove collar and smooth outboard shoulder (inferred fits)')
    allnames=[i['id'] for i in items if i['id'].startswith(('PortSmallPlanetTrain_','PortSmallPlanetSupports_','PortPlanetTrain_','PortPlanetSupports_','PortTransmissionCore_','PortSunRetention_')) or i['id']=='CenterTransmissionCore_cross_shaft']
    section(allnames,box(origin.x-320,origin.x+320,190,640,origin.z-320,origin.z),out/'coupled_trains_cutaway.svg',(1,-1,1.2),
        'Coupled planetary trains | six shared M290 rings now installed; brake bearings and central bevel remain unfinished')
    cal=read(ROOT/'transmission_output_calibration.json');source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',
        f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".62"/>']
    plane=Part.makePlane(3000,3000,App.Vector(origin.x-1500,-1500,origin.z),App.Vector(0,0,1))
    colors=['#d13219','#8e7110','#97672e','#197798','#666666']
    for name,colorhex in zip(names,colors):
        for edge in byid[name]['shape'].section(plane).Edges:
            pts=[f'{cal["sprocket_center_x_px"]-(v.y-output_y)/cal["mm_per_pixel"]:.3f},{cal["shaft_axis_y_px"]+(v.x-origin.x)/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.2)]
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colorhex}" stroke-width="1.0"/>')
    svg.append('</svg>');path=out/'sun_retention_overlay.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    def crop64(p):
        with Image.open(p) as im:
            buf=io.BytesIO();im.crop((1090,420,1320,730)).save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()
    panels=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1040">','<rect width="1280" height="1040" fill="#f7f5ee"/>',
        '<text x="30" y="35" font-family="sans-serif" font-size="24">Small-sun retention | original and actual native shaft-height section</text>',
        '<text x="30" y="65" font-family="sans-serif" font-size="17">Red M290 ring, ochre M267 sleeve, blue M269 drum. Unchanged calibration; hub and casting contours remain inferred.</text>']
    for x,pic,title in [(30,source,'SNL Plate22'),(650,path.with_suffix('.png'),'Native section over source')]:
        panels.append(f'<text x="{x}" y="106" font-family="sans-serif" font-size="21">{title}</text>')
        panels.append(f'<image x="{x}" y="125" width="575" height="775" href="data:image/png;base64,{crop64(pic)}"/>')
    panels.extend(['<text x="30" y="944" font-family="sans-serif" font-size="18">Ring center uses source x1285. Groove collar and counterbores provide nominal static retention.</text>',
        '<text x="30" y="977" font-family="sans-serif" font-size="18">M265 bush / M266 cap joint is unresolved. This stage does not validate the adjacent bearing or drum profile.</text></svg>'])
    path=out/'sun_retention_comparison.svg';path.write_text('\n'.join(panels))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    ring=byid['PortSunRetention_ring']['shape'];station=(ring.BoundBox.YMin+ring.BoundBox.YMax)/2
    projected=cal['sprocket_center_x_px']-(station-output_y)/cal['mm_per_pixel']
    report.update(rendering_complete=True,output_raster_hashes={p.name:sha(p) for p in out.glob('*.png')})
    write(candidate/'report.json',report)
    receipt=dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),
        rasters={p.name:sha(p) for p in out.glob('*.png')},ring_station_source_x_px=projected,source_pick_x_px=1285,
        view='Actual shaft-height horizontal section and half cutaways of saved native solids; no installation placement changed.',
        limitations=['Ring section and shoulders are inferred.','Unchanged M269 OD381 differs from source-scaled outline about408mm.','M265/M266 cap joint and exact drum hub/case neck profiles require further reconstruction.'])
    assert sha(native)==report['native_sha256'];write(out/'render_receipt.json',receipt)
    print('Rendered four images; native unchanged.',flush=True)
finally:runtime.close()
