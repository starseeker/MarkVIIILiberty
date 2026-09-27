"""Independent saved-solid checks of the intermediate shaft and real mount stack."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();current=Saved(a.candidate);r=current.report;d=r['details'];c=d['controls'];out=current.folder/'checks02';out.mkdir(exist_ok=False)
parent=Saved((ROOT/r['parent_native']).parent)
assert all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
validate_native_bindings(dict(native_file=str(current.native),render_occurrences=list(current.rows),landmarks=[]),current.manifest)
checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'progress.json',checks)
def material(s):return sum(abs(v.Volume) for v in s.Solids)
def no_material(a,b):return material(a.common(b))<1e-5
def same(a,b):return material(a.cut(b))<1e-5 and material(b.cut(a))<1e-5 and not a.cut(b,1e-4).Faces and not b.cut(a,1e-4).Faces
def moved(s,v):
    t=s.copy();t.translate(v);return t
def cylinders(s,center,axis,radius):
    return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6
            and f.Surface.Axis.cross(axis).Length<1e-7 and (f.Surface.Center-center).cross(axis).Length<1e-6]
def span(f,center,axis):
    ps=[(v.Point-center).dot(axis) for v in f.Vertexes];return min(ps),max(ps)
def planes(s,point,axis):
    return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.Surface.Axis.cross(axis).Length<1e-7
            and abs((f.CenterOfMass-point).dot(axis))<1e-6]
def bearing(a,b,point,axis):return sum(x.common(y).Area for x in planes(a,point,axis) for y in planes(b,point,axis))

ck('23 additions including one standard floor-context replacement',len(current.rows)==23 and len(r['new_occurrences'])==23
   and len(r['new_definitions'])==6 and not r['changed_definitions'] and 'hull_floor_3' not in parent.rows)
for key in current.manifest['definitions']:
    s=current.definition(key)
    ck(key+' valid canonical solid',s.Placement.isIdentity() and s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:ck(key+' retained shared material',same(s,parent.definition(key)))
for n,row in current.rows.items():
    ck(n+' full frame',max(abs(x-y) for x,y in zip(row['frame'],r['specs'][n]['frame']))<1e-7)

origin=V(*d['shaft_origin_world_mm']);shaft=current.world('IntermediateControlShaft');floor=current.world('hull_floor_3')
oldfloor=Part.Shape();oldfloor.read(str(ROOT/c['floor_source']));holes=[]
for m in d['mounts']:
    base=V(*m['underhead_world_mm']);tool=Part.makeCylinder(c['mount_clearance']/2,c['floor_stock']+2,base-Z)
    holes.append(tool);faces=cylinders(floor,base,Z,c['mount_clearance']/2)
    ck(m['name']+' real floor receiving bore',len(faces)==1 and no_material(floor,tool)
       and abs(span(faces[0],base,Z)[1]-span(faces[0],base,Z)[0]-c['floor_stock'])<1e-6)
ck('Standard floor changed by exactly six declared holes',same(floor,oldfloor.cut(Part.makeCompound(holes)))
   and abs(oldfloor.Volume-floor.Volume-6*math.pi*(c['mount_clearance']/2)**2*c['floor_stock'])<1e-5)

for number,y in enumerate(c['bracket_stations_y'],1):
    name='IntermediateShaftMount'+str(number)+'Bracket';bracket=current.world(name);center=origin+Y*y
    faces=cylinders(bracket,center,Y,c['journal_bore']/2)
    core=Part.makeCylinder(c['shaft_diameter']/2,c['bracket_width'],center-Y*c['bracket_width']/2,Y)
    ck(name+' actual uninterrupted journal and complete shaft engagement',len(faces)==1 and no_material(core,bracket)
       and material(core.cut(shaft))<1e-5 and abs(span(faces[0],center,Y)[1]-span(faces[0],center,Y)[0]-c['bracket_width'])<1e-6)
    for label,sign in [('Rear',-1),('Front',1)]:
        strip=current.world(label+'IntermediateSupportStrip');seat=V(origin.x+sign*c['mount_pitch_x']/2,y,c['floor_top']+c['strip_thickness'])
        area=bearing(bracket,strip,seat,Z)
        ck(name+' '+label+' strip seating',area>1000 and no_material(bracket,strip)
           and bearing(moved(bracket,Z*.2),strip,seat,Z)<1e-6,bearing_mm2=area)

for label in ['Rear','Front']:
    strip=current.world(label+'IntermediateSupportStrip');seat=V(origin.x,0,c['floor_top'])
    ck(label+' strip fully supported by floor',bearing(strip,floor,seat,Z)>20000 and no_material(strip,floor)
       and bearing(moved(strip,Z*.2),floor,seat,Z)<1e-6)

for m in d['mounts']:
    name=m['name'];base=V(*m['underhead_world_mm']);screw=current.world(name);bracket=current.world(m['bracket']);strip=current.world(m['strip'])
    core=Part.makeCylinder(c['bolt_diameter']/2,c['bolt_length'],base)
    area=bearing(screw,floor,base,Z);seat=base+Z*(c['floor_stock']+c['strip_thickness'])
    faces=cylinders(bracket,seat,Z,c['mount_thread_envelope']/2)
    engagement=c['bolt_length']-c['floor_stock']-c['strip_thickness']
    ck(name+' source-sized unbroken stock and head bearing',material(core.cut(screw))<1e-5
       and area>250 and no_material(screw,floor) and no_material(screw,strip) and no_material(screw,bracket),bearing_mm2=area)
    ck(name+' actual blind thread envelope and stock engagement',len(faces)==1 and engagement>=2*c['bolt_diameter']
       and engagement<c['mount_blind_depth'] and abs(span(faces[0],seat,Z)[0])<1e-6
       and abs(span(faces[0],seat,Z)[1]-c['mount_blind_depth'])<1e-6,engagement_mm=engagement)
    ck(name+' lifted negative loses head bearing',bearing(moved(screw,Z*.2),floor,base,Z)<1e-6)

for label,sign in [('Starboard',-1),('Port',1)]:
    name=label+'IntermediateShaftKeeper';keeper=current.world(name);center=origin+Y*(sign*c['keeper_station_y'])
    faces=cylinders(shaft,center,Z,c['keeper_bore']/2)
    hole=Part.makeCylinder(c['keeper_bore']/2,c['shaft_diameter']+2,center-Z*(c['shaft_diameter']/2+1))
    support=current.world('IntermediateShaftMount'+('1' if sign<0 else '3')+'Bracket')
    ck(name+' cross bore outside bearing, keeper clear and stops shaft drift',len(faces)==1 and no_material(shaft,hole)
       and no_material(keeper,shaft) and no_material(keeper,support)
       and material(moved(keeper,-Y*sign*3).common(support))>1e-5)
    wire=(c['keeper']['cotter_diameter']-c['keeper']['cotter_center_spacing'])/2
    for direction in [-1,1]:
        point=center+X*(direction*c['keeper']['cotter_center_spacing']/2)
        witness=Part.makeCylinder(wire,c['shaft_diameter'],point-Z*c['shaft_diameter']/2)
        ck(name+' continuous through leg '+str(direction),material(witness.cut(keeper))<1e-5)

expected={'StarboardReverse','StarboardLow','StarboardHigh','StarboardFoot','PortFoot','PortHigh','PortLow','PortClutch'}
ck('Eight source applications have distinct receiving levers',set(d['receiving_interfaces'])==expected)
for name,j in d['receiving_interfaces'].items():
    rocker=current.world(name+'IntermediateRocker');pivot=V(*j['pivot_world_mm'])
    core=Part.makeCylinder(c['shaft_diameter']/2,34,pivot-Y*17,Y)
    ck(name+' full shaft bearing and clear journal',material(core.cut(shaft))<1e-5 and no_material(shaft,rocker))
    for end,radius in [('front',c['rocker_inner_radius']),('rear',c['rocker_outer_radius'])]:
        center=V(*j[end+'_pin_world_mm']);faces=cylinders(rocker,center,Y,6.5)
        ck(name+' '+end+' real receiver with same-side arm',len(faces)==1 and center.z<pivot.z
           and abs((center-pivot).Length-radius)<1e-6 and abs(span(faces[0],center,Y)[1]-span(faces[0],center,Y)[0]-12)<1e-6)
    if name.endswith('Low'):
        front=V(*c['front_low_pin']);front.y=math.copysign(front.y,pivot.y)
        actual=V(*j['front_pin_world_mm']);length=(front-actual).Length-2*(c['fork_face_distance']-c['rod_insertion'])
        ck(name+' printed front rod length closes provisional driver datum',abs(length-1257.3)<1e-6
           and abs(front.y-actual.y)<1e-6,core_length_mm=length,datum_qualified=False)
result=dict(passed=all(v['passed'] for v in checks),checks=checks,native_sha256=sha(current.native),
    checker_sha256=sha(Path(__file__)),parent_native_sha256=sha(parent.native),
    scope='Complete saved shaft/journal stock, actual mount receivers and seating, source-sized cap-screw engagement, keeper retention, eight real lever receivers and provisional printed-length closure.',
    historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result)
print(len(checks),'checks;',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
