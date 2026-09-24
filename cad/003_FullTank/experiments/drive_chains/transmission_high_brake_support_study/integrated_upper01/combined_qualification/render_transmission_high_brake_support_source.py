"""Inspect saved prototype geometry through the unchanged HB133 registration."""
import argparse,base64,sys
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import fitz
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();candidate=a.candidate.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
r=read(candidate/'report.json');native=candidate/r['native_file'];m=read(candidate/'isolated/manifest.json');assert sha(native)==r['native_sha256']==m['native_sha256']
regpath=H/'transmission_high_brake_support_study/source_registration.json';reg=read(regpath);source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
from lib.camera_review import validate_native_bindings
names=[v['name'] for v in m['occurrences'] if v['name'].startswith('PortHighSpeedBrake')]+['CenterTransmissionCore_bevel_case'];validate_native_bindings(dict(native_file=str(native),render_occurrences=names,landmarks=[]),m)
shapes={}
for row in m['occurrences']:
 if row['name'] not in names:continue
 d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);s.Placement=App.Placement(App.Matrix(*row['frame']));shapes['Case' if row['name']=='CenterTransmissionCore_bevel_case' else row['name']]=s
center=read(H/'transmission_high_brake_mechanism_study/trial01/report.json')['interfaces']['PortHighSpeedBrake']['center_world_mm']
cx,cy=reg['center_px'];scale=reg['pixels_per_mm'];V=App.Vector
def pixel(v):return cx-(v.x-center[0])*scale,cy-(v.z-center[2])*scale
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1850">','<rect width="100%" height="100%" fill="white"/>',
 '<text x="30" y="34" font-family="sans-serif" font-size="22">HB133 | combined brake and support reconstruction in retained registration</text>',
 f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
def lines(shape,color,width=1.6):
 for edge in shape.Edges:
  pts=[pixel(v) for v in edge.discretize(Deflection=.3)]
  svg.append('<polyline points="'+' '.join(f'{u+40:.3f},{v+70:.3f}' for u,v in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" opacity=".8"/>')
sections=[]
for y,color in [(r['receiver_controls']['brake_station'],'#00a1ab'),(r['receiver_controls']['bearing_station'],'#b02397')]:
 corners=[V(center[0]+x,y,center[2]+z) for x,z in [(-450,-450),(450,-450),(450,450),(-450,450)]]
 section=shapes['Case'].section(Part.Face(Part.makePolygon(corners+corners[:1])));lines(section,color)
 sections.append(dict(y_mm=y,edge_count=len(section.Edges)))
for name,s in shapes.items():
 if name.startswith('Port'):lines(s,'#ba3022',1.9)
svg+=['<text x="30" y="1745" font-family="sans-serif" font-size="18">Red: all port brake parts. Cyan/magenta: case at brake/bearing depths.</text>',
 '<text x="30" y="1780" font-family="sans-serif" font-size="18">Hidden depths and stock are estimated. The drawing mixes local depth/section conventions.</text>',
 '<text x="30" y="1815" font-family="sans-serif" font-size="18">No camera refit. Same source scale and center; this is a diagnostic illustration comparison.</text></svg>']
assert not (out/'support_source.svg').exists()
(out/'support_source.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'support_source.svg').read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(out/'support_source.png'))
write(out/'source_render_receipt.json',dict(native_sha256=sha(native),source_registration_sha256=sha(regpath),source_sha256=sha(source),
 renderer_sha256=sha(Path(__file__)),render_occurrences=names,passed=True,image_sha256=sha(out/'support_source.png'),sections=sections,camera_refit=False,historical_geometry_qualified=False))
print('Rendered complete saved brake/support assembly in fixed source registration',flush=True)
