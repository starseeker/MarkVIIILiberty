"""Isolated drive mounting hypothesis; proxy receivers are not accepted hull parts."""
from pathlib import Path
import sys,subprocess,math
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=ROOT/'build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)

import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import leaves,frame
from lib.track_parts import cylinder_y
from lib.idler_parts import hex_y,block
from lib.wheel_parts import button_rivet
from lib.roller_validation import bearing_face
from lib.visual_review import shaded

lock=fingerprint();assert lock==read(ROOT/'authored_input_fingerprint.json'),'Archived study inputs changed; review before regeneration'
reference=ROOT/'reference_native';manifest=read(ROOT/'reference_native_manifest.json')
for path,digest in manifest['files'].items():assert sha(reference/path)==digest
base=App.openDocument(str(reference/'MarkVIII.FCStd'));data=load();items=leaves(base.Root)
source={i['definition']:i['target'] for i in items}
v={k:q.value for k,q in data['values'].items()}
# Printed dimensions plus explicit fixture hypotheses; none are main parameters.
a=read(ROOT/'hypotheses.json')['values_mm']
end=a['shaft_length']/2;r=a['shaft_diameter']/2;j=a['journal_diameter']/2
wall=v['hull_side_thickness'];shell=v['hull_frame_clear']/2
outside=shell+wall;face=end-a['end_projection']-v['idler_nut_stock']
shoulder=v['wheel_boss_length']/2+a['boss_end_gap'];flange=face-outside
plate=a['backing_stock'];keyL=a['key_length'];keyW=a['key_width'];keyH=a['key_height']
key_end=face-a['key_end_inset'];key_start=key_end-keyL
key_bottom=j-keyH/2;key_top=j+keyH/2
bolts=[(a['bearing_bolt_radius']*math.sin(math.radians(30+n*60)),
        a['bearing_bolt_radius']*math.cos(math.radians(30+n*60))) for n in range(6)]
rivets=[(a['backing_rivet_radius']*math.sin(math.radians(45+n*90)),
         a['backing_rivet_radius']*math.cos(math.radians(45+n*90))) for n in range(4)]
lock_z=-v['idler_nut_af']/2;lock_x=a['locking_screw_x'];lock_center=lock_z-a['locking_plate_width']/2

def annulus(ro,ri,y0,y1):
    return cylinder_y(ro,y1-y0,y=(y0+y1)/2).cut(cylinder_y(ri,y1-y0+2,y=(y0+y1)/2))
def drill(shape,points,d):
    return shape.cut(Part.makeCompound([cylinder_y(d/2,1000,x=x,z=z) for x,z in points]))
def keytool(z0,z1):return block(-keyW/2,keyW/2,key_start,key_end,z0,z1)
def screw(d,length,af,h):
    return cylinder_y(d/2,length,y=-length/2).fuse(hex_y(af,0,h))

shapes={}
shaft=cylinder_y(r,2*shoulder)
for side in [-1,1]:shaft=shaft.fuse(cylinder_y(j,end-shoulder,y=side*(end+shoulder)/2))
shaft=shaft.cut(keytool(key_bottom,r+1))
shaft=shaft.cut(cylinder_y(v['roller_oil_bore']/2,end+1,y=(end+1)/2))
shaft=shaft.cut(Part.makeCylinder(a['radial_oil_bore']/2,r+1,App.Vector(),App.Vector(0,0,1)))
shapes['shaft']=shaft;shapes['key']=keytool(key_bottom,key_top)
for role in ['inner_bearing','outer_bearing']:
    bearing=annulus(a['barrel_radius'],j+a['journal_running_gap'],shoulder,face)
    bearing=bearing.fuse(annulus(a['flange_radius'],j+a['journal_running_gap'],outside,face))
    bearing=drill(bearing,bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance'])
    bearing=bearing.cut(cylinder_y(a['locking_screw_diameter']/2,2*a['locking_screw_length'],
                                  x=lock_x,y=face,z=lock_center))
    if role=='outer_bearing':bearing=bearing.cut(keytool(0,key_top))
    shapes[role]=bearing
back=annulus(a['backing_radius'],a['barrel_radius'],shell-plate,shell)
back=drill(back,bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance'])
shapes['backing_plate']=drill(back,rivets,a['backing_rivet_diameter']+a['fastener_hole_clearance'])
locking=block(a['locking_plate_x0'],a['locking_plate_x1'],0,a['locking_stock'],lock_z-a['locking_plate_width'],lock_z)
locking=locking.cut(cylinder_y((a['locking_screw_diameter']+a['fastener_hole_clearance'])/2,1000,x=lock_x,z=lock_center))
shapes['locking_plate']=locking
shapes['bearing_screw']=screw(a['bearing_screw_diameter'],a['bearing_screw_length'],31.75,12.7)
shapes['locking_screw']=screw(a['locking_screw_diameter'],a['locking_screw_length'],22.225,8.73125)
# Explicit fixture-only receiving coupons. Their identities are NOT M1977/M1978.
for role,points in [('outer_coupon',bolts+rivets),('inner_coupon',bolts)]:
    coupon=block(-190,190,shell,outside,-190,190).cut(cylinder_y(a['barrel_radius'],1000))
    coupon=drill(coupon,bolts,a['bearing_screw_diameter']+a['fastener_hole_clearance'])
    if role=='outer_coupon':coupon=drill(coupon,rivets,a['backing_rivet_diameter']+a['fastener_hole_clearance'])
    shapes[role]=coupon

doc=App.newDocument('DriveMountStudy');library=doc.addObject('App::Part','Library');root=doc.addObject('App::Part','Fixture')
targets={};physical=[]
def target(role,shape,source_ids=()):
    shape=shape.removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1,'Invalid fixture part '+role
    obj=doc.addObject('PartDesign::Feature','Def_'+role);obj.Shape=shape;library.addObject(obj)
    obj.addProperty('App::PropertyStringList','SurveyIdentities');obj.SurveyIdentities=list(source_ids)
    obj.addProperty('App::PropertyString','Qualification');obj.Qualification='Isolated inferred fixture; actual receiver mapping and threads unqualified'
    targets[role]=obj;return obj
rows=read(ROOT/'source_rows.json')
for role,shape in shapes.items():target(role,shape,rows.get(role,{}).get('survey_ids',[]))
for role,diameter,length,grip in [('inner_rivet',a['bearing_screw_diameter'],a['inner_rivet_length'],flange+wall),
                                ('backing_rivet',a['backing_rivet_diameter'],a['backing_rivet_length'],plate+wall)]:
    obj=button_rivet(doc,'Def_'+role,diameter,length,grip);library.addObject(obj);targets[role]=obj
    obj.addProperty('App::PropertyStringList','SurveyIdentities');obj.SurveyIdentities=rows[role]['survey_ids']
for role,original in [('nut','idler_nut'),('oil_plug','roller_plug')]:
    target(role,source[original].Shape.copy(),data['definitions'][original]['survey_ids'])

def add(role,name,placement=None,representation='assembly'):
    obj=doc.addObject('App::Link',name);obj.setLink(targets[role]);root.addObject(obj)
    obj.Placement=placement or App.Placement()
    shape=targets[role].Shape.copy();shape.Placement=obj.Placement.multiply(shape.Placement)
    physical.append(dict(id=name,definition=role,target=targets[role],shape=shape,representation=representation,system='RunningGear'))
    return obj
local=frame('port_drive',data).inverse()
for item in [i for i in items if i['id'].startswith('PortDrive_')]:
    role=item['definition']
    if role not in targets:target(role,item['target'].Shape.copy(),data['definitions'][role]['survey_ids'])
    add(role,item['id'].replace('PortDrive_Unit000_',''),local.multiply(frame(item['id'],data)))
add('shaft','Shaft');add('key','Key')
for side in [-1,1]:
    rotation=App.Rotation(0,0,180) if side==-1 else App.Rotation()
    suffix='Inner' if side==-1 else 'Outer'
    add('inner_bearing' if side==-1 else 'outer_bearing','Bearing'+suffix,App.Placement(App.Vector(),rotation))
    add('nut','Nut'+suffix,App.Placement(App.Vector(0,side*face,0),rotation))
    add('locking_plate','LockingPlate'+suffix,App.Placement(App.Vector(0,side*face,0),rotation))
    add('locking_screw','LockingScrew'+suffix,App.Placement(App.Vector(lock_x,side*(face+a['locking_stock']),side*lock_center),rotation))
    add('inner_coupon' if side==-1 else 'outer_coupon','Receiver'+suffix,App.Placement(App.Vector(),rotation),'inspection')
add('backing_plate','BackingPlate')
add('oil_plug','OilPlug',App.Placement(App.Vector(0,end,0),App.Rotation(0,0,180)))
for n,(x,z) in enumerate(bolts):
    add('bearing_screw','BearingScrew'+str(n),App.Placement(App.Vector(x,face,z),App.Rotation()))
    # Inner factory head faces -Y; the rivet's own factory head is local -Y.
    add('inner_rivet','InnerRivet'+str(n),App.Placement(App.Vector(x,-(face+shell)/2,-z),App.Rotation()))
for n,(x,z) in enumerate(rivets):
    add('backing_rivet','BackingRivet'+str(n),App.Placement(App.Vector(x,(outside+shell-plate)/2,z),App.Rotation(0,0,180)))
doc.recompute()
assert len([i for i in physical if i['representation']=='assembly'])==149

def bounds(s):
    b=s.optimalBoundingBox(False);return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
boxes=np.array([bounds(i['shape']) for i in physical]);overlaps=[];tested=0
for index,item in enumerate(physical):
    b=boxes[index];near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
    for other in near:
        if other<=index:continue
        tested+=1;volume=item['shape'].common(physical[other]['shape']).Volume
        if volume>1e-5:overlaps.append(dict(a=item['id'],b=physical[other]['id'],volume_mm3=volume))
by_id={i['id']:i['shape'] for i in physical};seats=[]
pairs=[('Nut'+s,'Bearing'+s) for s in ['Inner','Outer']]
pairs += [('LockingPlate'+s,'Nut'+s) for s in ['Inner','Outer']]
pairs += [('LockingPlate'+s,'Bearing'+s) for s in ['Inner','Outer']]
pairs += [('LockingScrew'+s,'LockingPlate'+s) for s in ['Inner','Outer']]
pairs += [('Bearing'+s,'Receiver'+s) for s in ['Inner','Outer']]
pairs += [('BackingPlate','ReceiverOuter'),('Key','Shaft'),('Key','BearingOuter')]
for n in range(6):pairs += [('BearingScrew'+str(n),'BearingOuter'),('InnerRivet'+str(n),'BearingInner'),('InnerRivet'+str(n),'ReceiverInner')]
for n in range(4):pairs += [('BackingRivet'+str(n),'BackingPlate'),('BackingRivet'+str(n),'ReceiverOuter')]
for left,right in pairs:
    gap,area=bearing_face(by_id[left],by_id[right]);seats.append(dict(a=left,b=right,gap_mm=gap,area_mm2=area,passed=gap<1e-5 and area>1e-4))
bush_gaps=[]
for suffix in ['A','B']:
    gap=by_id['Shaft'].distToShape(by_id['ShaftAssembly_Bush'+suffix])[0]
    bush_gaps.append(dict(side=suffix,gap_mm=gap,expected_mm=(v['wheel_bush_id']-a['shaft_diameter'])/2))
    assert abs(gap-bush_gaps[-1]['expected_mm'])<1e-5
for p in [App.Vector(0,end-15,0),App.Vector(0,0,r-1)]:assert not by_id['Shaft'].isInside(p,1e-7,True)
assert by_id['Shaft'].isInside(App.Vector(25,0,0),1e-7,True)
shaded([i for i in physical if i['representation']=='assembly'],OUT/'assembled.svg',(1,1,.6),'Drive shaft and support hypothesis | proxy hull receivers; historical fit unresolved')
shaded([i for i in physical if not i['definition'].startswith(('wheel_','drive_rim'))],OUT/'mounts.svg',(1,1,.6),'Drive mounting fixture | explicit receiver coupons, not accepted hull plates')
native=OUT/'DriveMountStudy.FCStd';doc.saveAs(str(native))
assert fingerprint()==lock
write(OUT/'report.json',dict(complete=True,integrated=False,physical_occurrences=149,proxy_receivers=2,
    candidate_pairs=tested,overlaps=overlaps,bearing_faces=seats,bush_gaps=bush_gaps,
    passed=not overlaps and all(s['passed'] for s in seats),native_sha256=sha(native),authored_fingerprint=lock,
    executed_script_sha256=sha(Path(__file__)),source_rows_sha256=sha(ROOT/'source_rows.json'),hypotheses_sha256=sha(ROOT/'hypotheses.json'),
    limitation='Receiver coupons only: M1977/M1978 mapping, remaining M1552 rivets, threads and actual installation remain unresolved.'))
for name in list(App.listDocuments()):App.closeDocument(name)
print('MOUNT STUDY COMPLETE',len(overlaps),'overlaps',flush=True)
