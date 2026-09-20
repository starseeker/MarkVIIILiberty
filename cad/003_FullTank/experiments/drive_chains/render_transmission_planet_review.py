"""Render saved-native planetary retention and a close Plate22 section comparison."""
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
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_planet_build')
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
    from lib.cad_build import leaves,COLORS
    from lib.visual_review import shaded
    from transmission_core_parts import box
    import fitz
    from PIL import Image
    report=read(candidate/'report.json');native=candidate/'TransmissionPlanetCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    origin=App.Vector(*report['shaft_axis_world_mm'])
    COLORS.update(PlanetGear=(.69,.55,.31),PlanetShell=(.42,.55,.48),PlanetRetainer=(.53,.57,.61))
    wanted={'PortPlanetTrain_sun','PortPlanetTrain_retainer','PortPlanetTrain_washer','CenterTransmissionCore_cross_shaft',
            'PortTransmissionCore_planet_disk','PortTransmissionOutput_shaft','PortTransmissionBearing_InnerBush','PortTransmissionBearing_InnerRing'}
    crop=box(origin.x-90,origin.x+90,420,650,origin.z-90,origin.z)
    detail=[]
    for item in items:
        if item['id'] not in wanted:continue
        shape=item['shape'].common(crop)
        if shape.isNull() or not shape.Solids:continue
        color='PlanetGear' if item['id'].endswith('_sun') else 'PlanetRetainer' if 'PlanetTrain_' in item['id'] else 'PlanetShell'
        detail.append(dict(item,system=color,definition=item['definition']+'_cut_'+item['id'],shape=shape,target=SimpleNamespace(Shape=shape)))
    shaded(detail,out/'shaft_retention_section.svg',(1,1,1.2),'Shaft retention cutaway | separate sun clip, carrier washer and output bearing')
    cal=read(ROOT/'transmission_output_calibration.json')
    source=REPO/cal['image'];assert sha(source)==cal['image_sha256']
    # Two panels retain exactly the same source image coordinates and scale.
    overlay=candidate/'source_plate22_overlay.png'
    def crop_png(path):
        with Image.open(path) as bitmap:
            cropped=bitmap.crop((710,130,1190,1000))
            stream=io.BytesIO();cropped.save(stream,format='PNG')
            return base64.b64encode(stream.getvalue()).decode()
    original=crop_png(source)
    overlay_encoded=crop_png(overlay)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="1140">',
         '<rect width="1450" height="1140" fill="#f7f5ee"/>',
         '<text x="30" y="32" font-family="sans-serif" font-size="23">Large planetary stack | original SNL Plate22 and native horizontal section</text>',
         '<text x="30" y="62" font-family="sans-serif" font-size="17">Unchanged source coordinates; printed tooth dimensions take precedence over inconsistent drawn proportions.</text>']
    for x,data,mime,title in [(30,original,'image/png','Original section'),(745,overlay_encoded,'image/png','Native section overlay')]:
        svg.append(f'<text x="{x}" y="100" font-family="sans-serif" font-size="20">{title}</text>')
        svg.append(f'<image x="{x+70}" y="120" width="524" height="950" href="data:{mime};base64,{data}"/>')
    svg+=['<text x="30" y="1110" font-family="sans-serif" font-size="17">Sun proportions and case shoulder differ; some planet section silhouettes depend on angular station. Pin supports remain absent.</text></svg>']
    path=out/'source_detail.svg';path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as drawing:drawing[0].get_pixmap().save(str(path.with_suffix('.png')))
    d=report['dimensions'];output_y=read(ROOT/'transmission_core_build/report.json')['output_center_y_mm']
    face_pixels=[cal['sprocket_center_x_px']-(y-output_y)/cal['mm_per_pixel'] for y in reversed(d['gear_band_y_mm'])]
    picks=read(ROOT/'transmission_planet_controls.json')['controls']['gear_face_picks_px']['value']
    result=dict(native_sha256=sha(native),report_sha256=sha(candidate/'report.json'),renderer_sha256=sha(Path(__file__)),
        source_sha256=sha(source),input_overlay_sha256=sha(overlay),
        rasters={p.name:sha(p) for p in out.glob('*.png')},
        axial_width_review=dict(source_picks_px=picks,native_faces_px=face_pixels,
            residual_px=[a-b for a,b in zip(face_pixels,picks)],
            residual_mm=[(a-b)*cal['mm_per_pixel'] for a,b in zip(face_pixels,picks)],
            interpretation='Width uses picked span; placement follows actual carrier rim plus 1.5mm gap. The ~7px station discrepancy exceeds the earlier four-pixel pick allowance and remains explicit.'),
        comparison_scope='Visual section comparison, not independent dimensional metrology. Detailed sun outline and ring/case profile mismatch remains; no automatic scan fit.')
    assert sha(native)==report['native_sha256']
    write(out/'render_receipt.json',result)
    print('Rendered retention section and Plate22 detail; native unchanged.',flush=True)
finally:runtime.close()
