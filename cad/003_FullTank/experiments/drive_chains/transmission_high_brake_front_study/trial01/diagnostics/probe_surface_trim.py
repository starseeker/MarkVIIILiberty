import json
from pathlib import Path
import FreeCAD as A
import Part
p=Path('/home/cyapp/MarkVIIILiberty/.work/high-brake-front/trial02');m=json.loads((p/'isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
def get(n):
 row=rows[n];s=Part.Shape();s.read(m['definitions'][row['definition']]['brep_path']);s.Placement=A.Placement(A.Matrix(*row['frame']));return s
s=get('PortHighSpeedBrakeLongFrontEnd');b=get('PortHighSpeedBrakeLongBand');r=get('PortHighSpeedBrakeLongFrontSteelRivet3');v=A.Vector
fs=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-199.23125)<1e-6];gs=[f for f in b.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-199.23125)<1e-6]
miss=fs[0].cut(Part.makeCompound(gs));tool=Part.makeCylinder(4.11875,50,v(0,0,-5)).fuse(Part.makeCone(11.35,4.11875,7.23125,v(0,0,-5)));tool.Placement=r.Placement
for name,shape in [('missing_in_void',miss.common(tool)),('missing_outside_void',miss.cut(tool)),('missing_on_actual_ear',miss.common(s)),('ear_surface_in_void',fs[0].common(tool)),('ear_material_in_void',s.common(tool)),('trim_then_cover',fs[0].cut(tool).cut(Part.makeCompound(gs)))]:
 print(name, 'faces',len(shape.Faces),'area',shape.Area,'volume',shape.Volume,'valid',shape.isValid(),flush=True)
