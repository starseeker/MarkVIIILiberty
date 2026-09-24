import json,sys
from pathlib import Path
import FreeCAD as App
import Part
p=Path('/home/cyapp/MarkVIIILiberty/.work/high-brake-front/trial02');m=json.loads((p/'isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
def shape(n):
 row=rows[n];s=Part.Shape();s.read(m['definitions'][row['definition']]['brep_path']);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
for role in ['Long','Short']:
 ear=shape('PortHighSpeedBrake'+role+'FrontEnd');band=shape('PortHighSpeedBrake'+role+'Band');rad=199.23125
 es=[f for f in ear.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-rad)<1e-6]
 bs=[f for f in band.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-rad)<1e-6]
 for i,f in enumerate(es):
  miss=f.cut(Part.makeCompound(bs));bb=miss.BoundBox
  print(role,i,'area',f.Area,'miss',miss.Area,'faces',len(miss.Faces),'valid',miss.isValid(),'bounds',bb,'centers',[f.CenterOfMass for f in miss.Faces],flush=True)
  if miss.Faces:miss.exportBrep(str(p/('foot_missing_'+role+str(i)+'.brep')))

print('LONG JOINTS',flush=True)
ear=shape('PortHighSpeedBrakeLongFrontEnd')
r=json.loads((p/'report.json').read_text());c=r['controls']
for i in range(1,4):
 rivet=shape('PortHighSpeedBrakeLongFrontSteelRivet'+str(i));pose=rivet.Placement
 hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];depth=c['steel_head_radius']-hole
 tool=Part.makeCylinder(hole,50,App.Vector(0,0,-5)).fuse(Part.makeCone(c['steel_head_radius']+5,hole,depth+5,App.Vector(0,0,-5)));tool.Placement=pose
 got=ear.common(tool)
 print(i,'void intersect',got.Volume,'faces',len(got.Faces),'valid',got.isValid(),flush=True)
