"""Unaccepted native casting/roller study; shafts, roller pins and mounts omitted."""
from pathlib import Path
import sys,subprocess,math,shutil
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'rotor_build'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
from lib.evidence import read,write,sha,fingerprint
from lib.track_parts import cylinder_y
# This experiment deliberately does not import mutable accepted-model geometry.
# Shared bush/shaft incorporation and source-BOM completion are later gates.
a=dict(casting_length=495.3,boss_envelope_radius=13.687*25.4/2,boss_radius=27.5,
       hub_radius=85.,casting_bore_radius=65.2,bank_web_radius=128.,bank_center=190.,
       roller_radius=25.4,roller_length=2.37*25.4,roller_bore_radius=22.325,
       roller_end_gap=.2,pin_bore_radius=22.325,teeth=23,chain_pitch=76.2,
       sprocket_radius=23.031*25.4/2,tooth_width=1.39*25.4,
       chain_relief_radius=22.525,web_hole_radius=40.,web_hole_circle=175.)
a['roller_circle']=a['boss_envelope_radius']-a['boss_radius']
a['chain_pitch_radius']=a['chain_pitch']/(2*math.sin(math.pi/a['teeth']))
a['flange_stock']=a['casting_length']/2-a['bank_center']-a['roller_length']/2-a['roller_end_gap']
assert a['flange_stock']>0
write(OUT/'hypotheses.json',dict(status='unaccepted_casting_and_roller_envelopes',values_mm=a,
    printed=['casting_length','boss_envelope_radius','roller_radius','roller_length','teeth','chain_pitch','sprocket_radius','tooth_width'],
    interpretation='The printed boss diameter is provisionally treated as a circle through outer boss extremities. Bank centering follows the existing wheel rings. All other dimensions and profiles are inferred; no assembly source composition, mounting or gear engagement is qualified.'))
lock=fingerprint();doc=App.newDocument('PinionRotorStudy');root=doc.addObject('App::Part','Rotor');root.Label='Partial pinion rotor: casting and18 rollers only'
def definition(name,shape):
 shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1,name
 obj=doc.addObject('PartDesign::Body','Def_'+name);feature=obj.newObject('PartDesign::Feature','Reconstructed'+name);feature.Shape=shape;doc.recompute();obj.Visibility=False;return obj
gear=cylinder_y(a['sprocket_radius'],a['tooth_width']);tools=[]
for n in range(a['teeth']):
 t=2*math.pi*n/a['teeth'];tools.append(cylinder_y(a['chain_relief_radius'],a['tooth_width']+2,x=a['chain_pitch_radius']*math.sin(t),z=a['chain_pitch_radius']*math.cos(t)))
for n in range(6):
 t=2*math.pi*(n+.5)/6;tools.append(cylinder_y(a['web_hole_radius'],a['tooth_width']+2,x=a['web_hole_circle']*math.sin(t),z=a['web_hole_circle']*math.cos(t)))
gear=gear.cut(Part.makeCompound(tools));pieces=[cylinder_y(a['hub_radius'],a['casting_length']),gear];pin_cuts=[]
for side in [-1,1]:
 center=side*a['bank_center']
 for end in [-1,1]:
  y=center+end*(a['roller_length']/2+a['roller_end_gap']+a['flange_stock']/2)
  bank=cylinder_y(a['bank_web_radius'],a['flange_stock'],y=y);bosses=[]
  for n in range(9):
   t=2*math.pi*n/9;x=a['roller_circle']*math.sin(t);z=a['roller_circle']*math.cos(t)
   bosses.append(cylinder_y(a['boss_radius'],a['flange_stock'],x=x,y=y,z=z))
   pin_cuts.append(cylinder_y(a['pin_bore_radius'],a['flange_stock']+2,x=x,y=y,z=z))
  pieces.append(bank.multiFuse(bosses))
casting=pieces[0].multiFuse(pieces[1:]);casting=casting.cut(Part.makeCompound(pin_cuts+[cylinder_y(a['casting_bore_radius'],a['casting_length']+2)]))
cast=definition('Casting',casting);roll=definition('Roller',cylinder_y(a['roller_radius'],a['roller_length']).cut(cylinder_y(a['roller_bore_radius'],a['roller_length']+2)))
occ=[]
def link(name,target,pos):
 obj=doc.addObject('App::Link',name);obj.setLink(target);obj.Placement=App.Placement(App.Vector(*pos),App.Rotation());root.addObject(obj);shape=target.Shape.copy();shape.translate(App.Vector(*pos));occ.append((name,shape));return obj
link('Casting',cast,[0,0,0])
for side,label in [(-1,'A'),(1,'B')]:
 for n in range(9):
  t=2*math.pi*n/9;link('Roller'+label+str(n),roll,[a['roller_circle']*math.sin(t),side*a['bank_center'],a['roller_circle']*math.cos(t)])
doc.recompute();pairs=[]
for index,(name,shape) in enumerate(occ):
 for other,second in occ[index+1:]:
  if shape.BoundBox.intersect(second.BoundBox):
   volume=shape.common(second).Volume;pairs.append(dict(a=name,b=other,overlap_mm3=volume));assert volume<1e-5,(name,other,volume)
# Verify roller axial end gaps without claiming pin support or retention.
gaps=[]
for name,shape in occ[1:]:
 gap=shape.distToShape(cast.Shape)[0];assert abs(gap-a['roller_end_gap'])<1e-5,(name,gap);gaps.append(dict(roller=name,casting_gap_mm=gap))
file=OUT/'PartialPinionRotor.FCStd';doc.saveAs(str(file));App.closeDocument(doc.Name);restored=App.openDocument(str(file));restored.recompute()
assert len(restored.Rotor.Group)==19
assert all(x.LinkedObject.Shape.isValid() and len(x.LinkedObject.Shape.Solids)==1 for x in restored.Rotor.Group)
write(OUT/'report.json',dict(status='native_partial_rotor_only',passed=True,physical_occurrences=19,definitions=2,
    omitted_source_rotor_leaves=54,shaft_bushes_mounts_and_chain_omitted=True,source_rotor_complete=False,
    native_sha256=sha(file),script_sha256=sha(__file__),authored_fingerprint=lock,
    candidate_pairs=pairs,roller_end_gaps=gaps,gear_engagement_qualified=False,historical_fit_qualified=False))
assert fingerprint()==lock;shutil.copy2(__file__,OUT/'executed_probe.py');App.closeDocument(restored.Name)
print('PASS partial19-leaf pinion rotor; source rotor remains54 leaves short')
