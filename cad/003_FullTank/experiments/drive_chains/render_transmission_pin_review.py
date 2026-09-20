"""Show one actual pin-axis section and the remaining Plate22 contour differences."""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_pin_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();candidate=args.candidate.resolve();out=candidate/'source_review'
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
    import Part
    import fitz
    from PIL import Image
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    from transmission_core_parts import box
    report=read(candidate/'report.json');native=candidate/'TransmissionPinCandidate.FCStd'
    assert report['passed'] and report['native_sha256']==sha(native)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    carrier=byid['PortTransmissionCore_planet_disk'];frame=carrier['shape'].Placement.multiply(carrier['target'].Shape.Placement.inverse())
    inverse=frame.inverse();selected=[]
    COLORS.update(PinMetal=(.57,.61,.65),PinBronze=(.68,.50,.24),PinCarrier=(.43,.56,.49),PinGear=(.56,.49,.38))
    for item in items:
        name=item['id']
        if not name.startswith(('PortPlanetSupports_','PortPlanetTrain_')) and name not in ['PortTransmissionCore_planet_disk','PortTransmissionCore_plain_case','PortTransmissionCore_brake_case']:continue
        shape=item['shape'].copy();shape.Placement=inverse.multiply(shape.Placement)
        key=report['keys_by_id'].get(name)
        color='PinBronze' if key=='bronze' else 'PinMetal' if key and key!='pin_ring' else 'PinCarrier' if key=='pin_ring' or 'TransmissionCore_' in name else 'PinGear'
        selected.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['definition']+'_local_'+name,system=color))
    # This is a view-coordinate transform; no occurrence placement is resaved.
    detail=[];crop=box(92,183,405,630,-48,0)
    for item in selected:
        shape=item['shape'].common(crop)
        if shape.isNull() or not shape.Solids:continue
        detail.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['definition']+'_cut'))
    shaded(detail,out/'pin_axis_section.svg',(1,1,1.3),'One planet-axis section | bronze bush, steel sleeve, hollow pin and retention')
    cal=read(ROOT/'transmission_output_calibration.json');yout=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1724" height="1147">',
         f'<image width="1724" height="1147" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}" opacity=".62"/>']
    plane=Part.makePlane(3000,3000,App.Vector(-1500,-1500,0),App.Vector(0,0,1))
    for item in selected:
        name=item['id'];key=report['keys_by_id'].get(name)
        color='#b77c0f' if key=='bronze' else '#a91f32' if key=='pin_ring' else '#1764ba' if key else '#178350'
        for edge in item['shape'].section(plane).Edges:
            points=[f'{cal["sprocket_center_x_px"]-(v.y-yout)/cal["mm_per_pixel"]:.3f},{cal["shaft_axis_y_px"]+v.x/cal["mm_per_pixel"]:.3f}' for v in edge.discretize(Deflection=.3)]
            svg.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.4"/>')
    svg.append('</svg>');overlay=out/'pin_axis_overlay.svg';overlay.write_text('\n'.join(svg))
    with fitz.open(stream=overlay.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(overlay.with_suffix('.png')))
    def cropped(path):
        with Image.open(path) as image:
            buffer=io.BytesIO();image.crop((710,130,1190,1000)).save(buffer,format='PNG')
            return base64.b64encode(buffer.getvalue()).decode()
    panels=['<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1170">','<rect width="1450" height="1170" fill="#f7f5ee"/>',
        '<text x="30" y="32" font-family="sans-serif" font-size="23">Planet-pin support | original Plate22 and a native section through one pin axis</text>',
        '<text x="30" y="64" font-family="sans-serif" font-size="17">Native inspection plane follows the carrier phase. Recessed nut seats use the original axial scale.</text>']
    for x,path,title in [(30,source,'Original source'),(745,overlay.with_suffix('.png'),'Native pin-axis section')]:
        panels.append(f'<text x="{x}" y="102" font-family="sans-serif" font-size="20">{title}</text>')
        panels.append(f'<image x="{x+70}" y="120" width="524" height="950" href="data:image/png;base64,{cropped(path)}"/>')
    panels+=['<text x="30" y="1110" font-family="sans-serif" font-size="17">Pocket contours remain inferred. Printed tooth dimensions retain a radial mismatch to the illustrated pin station.</text>',
             '<text x="30" y="1138" font-family="sans-serif" font-size="17">Upper ring bolt is substantially inboard of the illustrated station; carrier outer rim and bolt circle need review.</text></svg>']
    path=out/'source_pin_comparison.svg';path.write_text('\n'.join(panels))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    nut_y=report['dimensions']['pin_fastening']['nut_seat_y_mm'];nut_px=cal['sprocket_center_x_px']-(nut_y-yout)/cal['mm_per_pixel']
    receipt=dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),source_sha256=sha(source),
        rasters={p.name:sha(p) for p in out.glob('*.png')},
        section_frame='Inverse actual port-carrier frame; local Z=0 passes through planet0 and shaft. View-only transform; saved assembly unchanged.',
        nut_seat_comparison=dict(approximate_source_pixel_x=849,native_pixel_x=nut_px,residual_pixels=nut_px-849,
                                residual_mm=(nut_px-849)*cal['mm_per_pixel'],status='Nut seat follows approximate axial source pick; pocket diameter and cast transitions remain inferred.'),
        pin_center_comparison=dict(approximate_source_pixel_y=741,
            native_pixel_y=cal['shaft_axis_y_px']+report['gear_dimensions']['planet_center_radius_mm']/cal['mm_per_pixel'],
            residual_mm=report['gear_dimensions']['planet_center_radius_mm']-(741-cal['shaft_axis_y_px'])*cal['mm_per_pixel'],
            status='Printed gear tooth counts and pitch retain the inherited center radius; source axial scale is not adjusted to hide the radial mismatch.'),
        ring_bolt_comparison=dict(approximate_upper_source_pixel_y=200,
            native_upper_pixel_y=cal['shaft_axis_y_px']-report['stations_by_id']['PortPlanetSupports_bolt1']['radius_mm']/cal['mm_per_pixel'],
            approximate_source_radius_mm=(cal['shaft_axis_y_px']-200)*cal['mm_per_pixel'],
            native_radius_mm=report['stations_by_id']['PortPlanetSupports_bolt1']['radius_mm'],
            status='Substantial radial discrepancy. Existing carrier rim/gear-case envelope needs source reconciliation before enlarging the bolt circle; this is not historical-fit acceptance.'),
        source_pin_diameter_comparison=dict(approximate_source_pixels=[722,760],scaled_mm=38*cal['mm_per_pixel'],native_mm=28,
                                           status='Conditional scaled estimate; four-pixel pick allowance and illustration/calibration uncertainty retained.'))
    assert sha(native)==report['native_sha256'];write(out/'render_receipt.json',receipt)
    print('Rendered actual pin-axis detail and source comparison; native unchanged.',flush=True)
finally:runtime.close()
