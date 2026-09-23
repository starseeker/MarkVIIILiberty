from pathlib import Path
import sys,json,os
os.environ.setdefault('MARKVIII_RESOLVED_FREECAD',str(Path('/snap/freecad/current').resolve()))
HERE=Path(__file__).resolve().parent;h=HERE.parents[2];sys.path[:0]=[str(h),str(h.parents[1])]
import FreeCAD as App
import Part,math
from engine_crankshaft_parts import ring
from engine_water_pump_parts import clean
from case_joint_mass import calculator
V=App.Vector;X=V(1,0,0);c=json.loads((HERE/'controls.json').read_text())['controls'];out=Path.cwd();mass=calculator(out/'mass')
old=Part.Shape();old.read(str(HERE/'original.brep'))
center=c['bearing_start']+c['bearing_width']/2;results=[]
for method in ['saved_original','radial_poles','tangent_poles']:
 if method=='saved_original':s=old.copy()
 else:
  s=ring(c['cage_outer'],c['cage_inner'],center-c['cage_width']/2,center+c['cage_width']/2)
  for i in range(c['ball_count']):
   t=2*math.pi*i/c['ball_count'];direction=V(0,math.cos(t),math.sin(t));pos=V(center,0,0)+direction*c['ball_pitch_radius']
   axis=direction if method=='radial_poles' else V(0,-math.sin(t),math.cos(t))
   s=s.cut(Part.makeSphere(c['ball_radius']+c['cage_ball_gap'],pos,axis))
  s=clean(s)
 s.exportBrep(str(out/(method+'.brep')));s.exportStep(str(out/(method+'.step')));other=Part.Shape();other.read(str(out/(method+'.step')))
 result=dict(method=method,native_valid=s.isValid(),native_solids=len(s.Solids),native_max_tolerance=s.getTolerance(1),step_valid=other.isValid(),step_solids=len(other.Solids),native_material_missing=old.cut(s).Volume,native_material_added=s.cut(old).Volume)
 if other.isValid():
  one,two=s.Solids[0],other.Solids[0];a,b=mass(one,method+'_native'),mass(two,method+'_step');ta,tb=one.getTolerance(1),two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb));dv=abs(a['volume_mm3']-b['volume_mm3']);dc=(V(*a['center_mm'])-V(*b['center_mm'])).Length
  result.update(step_max_tolerance=tb,missing=one.cut(two).Volume,added=two.cut(one).Volume,mass_difference=dv,center_difference=dc)
  result['strict_passed']=abs(result['missing'])<1e-5 and abs(result['added'])<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
 results.append(result);(out/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(result,flush=True)

assert results[1]["strict_passed"] and abs(results[1]["native_material_missing"])<1e-5 and abs(results[1]["native_material_added"])<1e-5
