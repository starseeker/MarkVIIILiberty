"""Complete the rotating pinion's source leaf count in an unaccepted fixture."""
from pathlib import Path
from collections import Counter
import sys,subprocess,math,shutil,json
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'pin_build';sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
from lib.evidence import read,write,sha,fingerprint,database
from lib.track_parts import cylinder_y
from lib.roller_validation import bearing_face
base_path=ROOT/'rotor_build/PartialPinionRotor.FCStd';prior=read(ROOT/'rotor_build/report.json');assert sha(base_path)==prior['native_sha256']
lock=fingerprint();a=read(ROOT/'rotor_build/hypotheses.json')['values_mm']
p=dict(pin_length=5.593*25.4,pin_diameter=1.75*25.4,head_radius=27.5,head_stock=8.,
       cotter_nominal_diameter=5/16*25.4,cotter_nominal_length=1.75*25.4,
       cotter_center_spacing=4.04,cotter_from_inner_end=10.,cotter_hole_clearance=.2,
       oil_bore_diameter=10.4,oil_radial_diameter=3.,plug_shank_diameter=10.,plug_insertion=8.,plug_head_af=7.9375,plug_head_stock=4.)
p['pin_start']=a['casting_length']/2+p['head_stock']-p['pin_length']
p['roller_axis_on_pin']=a['bank_center']-p['pin_start']
p['cotter_wire_radius']=(p['cotter_nominal_diameter']-p['cotter_center_spacing'])/2
write(OUT/'hypotheses.json',dict(status='unaccepted_pin_assembly_fixture',values_mm=p,
    printed=['pin_length','pin_diameter','cotter_nominal_diameter','cotter_nominal_length'],
    note='Pin heads, drilling and pipe-thread envelope are inferred. Cotters use round legs with exact supplied stem length and combined nominal width; legs are intentionally unsplayed fixture stand-ins. Installed forming and mechanical retention are unqualified. 1/8-inch pipe size is a nominal thread designation, not the inferred10 mm shank diameter.'))
base=App.openDocument(str(base_path));cast_shape=base.Def_Casting.Shape.copy();roll_shape=base.Def_Roller.Shape.copy();App.closeDocument(base.Name)
doc=App.newDocument('PinionWithPins');root=doc.addObject('App::Part','Rotor');root.Label='73-leaf pinion rotor fixture; historical and installed fit unqualified'
source_rows={r['record_id']:r for r in read(ROOT/'source_rows.json')['rows']}
role_rows={'Casting':'SNL:144:004','Roller':'SNL:144:006','Pin':'SNL:143:009','Cotter':'SNL:143:010','Plug':'SNL:143:011'}
def definition(name,shape):
 shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1,name
 obj=doc.addObject('PartDesign::Body','Def_'+name);feat=obj.newObject('PartDesign::Feature','Reconstructed'+name);feat.Shape=shape
 for key,value in [('SurveyId',source_rows[role_rows[name]]['part_ids'][0]),('SourceRecord',role_rows[name]),('Coverage','partial')]:
  obj.addProperty('App::PropertyString',key,'Evidence');setattr(obj,key,value)
 doc.recompute();obj.Visibility=False;return obj
cast=definition('Casting',cast_shape);roll=definition('Roller',roll_shape)
L=p['pin_length'];r=p['pin_diameter']/2;head_start=L-p['head_stock']
shape=cylinder_y(r,head_start,y=head_start/2).fuse(cylinder_y(p['head_radius'],p['head_stock'],y=L-p['head_stock']/2))
shape=shape.cut(Part.makeCylinder(p['oil_bore_diameter']/2,L-p['roller_axis_on_pin']+11,App.Vector(0,L+1,0),App.Vector(0,-1,0)))
shape=shape.cut(Part.makeCylinder(p['oil_radial_diameter']/2,r+1,App.Vector(0,p['roller_axis_on_pin'],0),App.Vector(1,0,0)))
shape=shape.cut(Part.makeCylinder((p['cotter_nominal_diameter']+p['cotter_hole_clearance'])/2,2*r+2,App.Vector(0,p['cotter_from_inner_end'],-r-1),App.Vector(0,0,1)))
pin=definition('Pin',shape)
# A source-sized unspread split-pin stand-in. Do not invent a longer stem to
# create retaining bends around an undimensioned hole location.
wire=p['cotter_wire_radius'];half=p['cotter_center_spacing']/2;stem=p['cotter_nominal_length'];top=r;bottom=top-stem
pieces=[Part.makeCylinder(wire,stem,App.Vector(sign*half,0,bottom),App.Vector(0,0,1)) for sign in [-1,1]]
eye_radius=5.95;eye_z=top+4
points=[App.Vector(-half,0,top),App.Vector(-eye_radius,0,eye_z)]
points += [App.Vector(eye_radius*math.cos(t),0,eye_z+eye_radius*math.sin(t)) for t in [math.pi-i*math.pi/12 for i in range(1,13)]]
points.append(App.Vector(half,0,top))
for start,end in zip(points,points[1:]):
 d=end-start;pieces.append(Part.makeCylinder(wire,d.Length,start,d))
pieces += [Part.makeSphere(wire,v) for v in points]
cotter=definition('Cotter',pieces[0].multiFuse(pieces[1:]))
cotter.addProperty('App::PropertyLength','NominalStemLength','Source');cotter.NominalStemLength=stem
cotter.addProperty('App::PropertyString','InstalledForm','Evidence');cotter.InstalledForm='Unsplayed straight-stem fixture stand-in; deployed bends and retention not qualified'
shape=cylinder_y(p['plug_shank_diameter']/2,p['plug_insertion'],y=-p['plug_insertion']/2)
shape=shape.fuse(Part.makeBox(p['plug_head_af'],p['plug_head_stock'],p['plug_head_af'],App.Vector(-p['plug_head_af']/2,0,-p['plug_head_af']/2)))
plug=definition('Plug',shape)
items={};roles={};pin_assemblies=[]
def link(name,target,placement,parent=root):
 obj=doc.addObject('App::Link',name);obj.setLink(target);obj.Placement=placement;parent.addObject(obj)
 shape=target.Shape.copy();shape.Placement=placement.multiply(shape.Placement);items[name]=dict(id=name,definition=target.Name,target=target,shape=shape,system='RunningGear',representation='assembly');roles[name]=target.Name.removeprefix('Def_');return obj
link('Casting',cast,App.Placement())
for side,label in [(1,'A'),(-1,'B')]:
 for n in range(9):
  t=2*math.pi*n/9;x=a['roller_circle']*math.sin(t);z=a['roller_circle']*math.cos(t)
  # Rotate about Y for radial pin orientation, then reverse the opposite bank
  # about X to put both factory heads toward their respective outer end.
  rotation=App.Rotation(App.Vector(0,1,0),n*40).multiply(App.Rotation(App.Vector(1,0,0),0 if side==1 else 180))
  pose=App.Placement(App.Vector(x,side*p['pin_start'],z),rotation)
  name=label+str(n);group=doc.addObject('App::Part','PinAssembly'+name);root.addObject(group)
  group.addProperty('App::PropertyString','SourceRecord','Evidence');group.SourceRecord='SNL:143:007'
  link('Pin'+name,pin,pose,group)
  link('Cotter'+name,cotter,pose.multiply(App.Placement(App.Vector(0,p['cotter_from_inner_end'],0),App.Rotation())),group)
  link('Plug'+name,plug,pose.multiply(App.Placement(App.Vector(0,L,0),App.Rotation())),group)
  link('Roller'+name,roll,App.Placement(App.Vector(x,side*a['bank_center'],z),App.Rotation()))
  pin_assemblies.append(name)
doc.recompute();actual=Counter(roles.values());assert actual=={'Casting':1,'Roller':18,'Pin':18,'Cotter':18,'Plug':18}
# Source checks are independent of the constructed counter.
with database() as c:
 for role,rid in role_rows.items():
  row=c.execute('SELECT description FROM source_records WHERE record_id=?',(rid,)).fetchone();assert row,rid
  assert c.execute('SELECT1'.replace('SELECT1','SELECT 1')+' FROM part_evidence WHERE part_id=? AND record_id=?',(source_rows[rid]['part_ids'][0],rid)).fetchone()
 assert 'eighteen' in c.execute('SELECT description FROM source_records WHERE record_id="SNL:144:005"').fetchone()[0]
 assert 'eighteen' in c.execute('SELECT description FROM source_records WHERE record_id="SNL:144:006"').fetchone()[0]
pairs=[];overlaps=[];names=list(items)
for i,name in enumerate(names):
 first=items[name]['shape']
 for other in names[i+1:]:
  second=items[other]['shape']
  if first.BoundBox.intersect(second.BoundBox):
   volume=first.common(second).Volume;pairs.append(dict(a=name,b=other,overlap_mm3=volume))
   if volume>1e-5:overlaps.append(pairs[-1])
seats=[];gaps=[]
for name in pin_assemblies:
 gap,area=bearing_face(items['Pin'+name]['shape'],items['Casting']['shape']);seats.append(dict(pin=name,gap_mm=gap,area_mm2=area))
 assert gap<1e-5 and area>1,(name,gap,area)
 gap=items['Pin'+name]['shape'].distToShape(items['Roller'+name]['shape'])[0];gaps.append(dict(pin=name,radial_gap_mm=gap));assert abs(gap-.1)<1e-5,(name,gap)
file=OUT/'PinionWithPins.FCStd';doc.saveAs(str(file));App.closeDocument(doc.Name);fresh=App.openDocument(str(file));fresh.recompute()
assert len([o for o in fresh.Objects if o.TypeId=='App::Link'])==73
assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in fresh.Objects if o.TypeId=='PartDesign::Body')
report=dict(status='unaccepted_source_counted_rotor_fixture',passed=not overlaps,physical_occurrences=73,definitions=5,
 source_leaf_counts=dict(actual),source_rotor_leaf_count_complete=True,installed_cotter_form_qualified=False,
 shaft_bushes_mounts_and_chain_omitted=True,gear_engagement_qualified=False,historical_fit_qualified=False,
 native_sha256=sha(file),script_sha256=sha(__file__),authored_fingerprint=lock,candidate_pairs=len(pairs),overlaps=overlaps,pin_head_seats=seats,roller_pin_gaps=gaps)
write(OUT/'report.json',report);shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
App.closeDocument(fresh.Name);assert not overlaps,overlaps
print('PASS73-leaf source-counted pinion rotor fixture; cotter forming and installed interfaces unqualified')
