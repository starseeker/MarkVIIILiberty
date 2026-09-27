"""Independent saved-solid checks for the connected central pedal-group hypothesis."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
out=s.folder/'checks03';out.mkdir(exist_ok=False);d=s.report['details'];c=d['controls'];V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in s.report['input_hashes'].items())
checks=[]
def check(name,value,**detail):
    checks.append(dict(name=name,passed=bool(value),**detail))
    if not value:print('FAILED',name,detail,flush=True)
def volume(q):return sum(abs(v.Volume) for v in q.Solids)
def contains(q,w):return volume(w.cut(q))<1e-5
def empty(q,w):return volume(q.common(w))<1e-5
def planes(q,p,n):return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(n).Length<1e-7 and abs((f.CenterOfMass-p).dot(n))<1e-5]
def contact(q,r,p,n):return sum(f.common(g).Area for f in planes(q,p,n) for g in planes(r,p,n))
def bore(q,p,n,r):return any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-r)<1e-7 and f.Surface.Axis.cross(n).Length<1e-7 and (f.Surface.Center-p).cross(n).Length<1e-6 for f in q.Faces)
check('Ten physical additions and two exact shaft receivers',len(s.report['new_occurrences'])==10 and len(s.rows)==12 and len(s.report['new_definitions'])==7 and not s.report['changed_definitions'])
for key in s.manifest['definitions']:
    q=s.definition(key)
    check(key+' canonical single closed solid',q.isValid() and q.Placement.isIdentity() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:
        old=parent.definition(key);f=min(1e-4,max(1e-7,q.getTolerance(1)+old.getTolerance(1)))
        check(key+' exact retained material',volume(q.cut(old))<1e-5 and volume(old.cut(q))<1e-5 and not q.cut(old,f).Faces and not old.cut(q,f).Faces)
for name in ['DriverMainShaft','DriverSwingShaft']:
    check(name+' exact retained frame',s.rows[name]['frame']==parent.rows[name]['frame'] and s.rows[name]['definition']==parent.rows[name]['definition'])
main,swing,front,rear=[V(*d[k]) for k in ['main_world_mm','swing_world_mm','front_joint_world_mm','rear_joint_world_mm']]
pedal=s.world('DriverBrakePedal');bridle=s.world('DriverBrakeBridle');susp=s.world('DriverBrakeSuspension');sleeve=s.world('DriverBrakeSuspensionSleeve');spacer=s.world('DriverBrakeDistance')
check('Pedal main journal receives complete retained shaft',bore(pedal,main,Y,19.1619) and empty(pedal,Part.makeCylinder(19.0119,38.1,main-Y*19.05,Y)) and volume(pedal.common(s.world('DriverMainShaft')))<1e-5)
check('Sleeve has open coaxial shaft journal',bore(sleeve,swing,Y,12.825) and bore(sleeve,swing,Y,15.875) and volume(sleeve.common(s.world('DriverSwingShaft')))<1e-5)
check('Suspension upper journal receives actual sleeve',bore(susp,swing,Y,16.025) and volume(susp.common(sleeve))<1e-5)
check('Aligned oilway through suspension and sleeve',all(bore(q,swing,V(1,0,0),1.5) for q in [susp,sleeve]))
local=s.definition('Def_DriverBrakePedal_M764A').transformGeometry(App.Rotation(Y,c['pedal_long_axis_deg']).toMatrix())
bb=local.BoundBox
check('Full35-1/4in interpreted overall pedal extent',abs(bb.XLength-895.35)<1e-5,actual_mm=bb.XLength,datum='Unrotated long-arm-axis extrema; source applicability/datum interpretation remain provisional.')
padfaces=planes(local,V(0,0,22.225),Z)
check('Complete eight-by-five-inch pad top',len(padfaces)==1 and abs(padfaces[0].BoundBox.XLength-203.2)<1e-5 and abs(padfaces[0].BoundBox.YLength-127)<1e-5)
expected=203.2*127-(4-math.pi)*12.7**2
check('Pad rounded-corner area and physical thickness',len(padfaces)==1 and abs(padfaces[0].Area-expected)<1e-5 and bool(planes(local,V(0,0,15.875),Z)),expected_top_area_mm2=expected)
check('I-section complete central web',contains(local,Part.makeBox(20,6.33,31.73,V(200,-3.165,-15.865))))
for sign in [-1,1]:
    y0=3.3 if sign>0 else -12.6
    check(('Port' if sign>0 else 'Starboard')+' I-section channel is empty',empty(local,Part.makeBox(20,9.3,21.8,V(200,y0,-10.9))))
for z in [-15.865,11.1225]:check('Full I-section flange at'+str(z),contains(local,Part.makeBox(20,25.38,4.7425,V(200,-12.69,z))))
head_y=d['pedal']['fork_head_seat_y_mm'];pin=s.world('DriverBrakePedalJointPin');keeper=s.world('DriverBrakePedalJointCotter')
check('Front pin coaxial with both fork cheeks and tongue',bore(pedal,front,Y,9.625) and bore(bridle,front,Y,9.625) and bore(pin,front,Y,9.525))
check('Complete front pin head physically seated',contact(pin,pedal,front+Y*head_y,Y)>150,contact_mm2=contact(pin,pedal,front+Y*head_y,Y))
check('Front pin keeper passes its actual cross drill',bore(pin,front+Y*(head_y-25.9),V(1,0,0),2.5) and volume(pin.common(keeper))<1e-5)
check('Front tongue side clearances',abs(c['pedal_fork_throat_mm']-c['bridle_stock_mm']-.4)<1e-8 and volume(pedal.common(bridle))<1e-5)
outer=d['bridle']['rear_outside_y_mm'];inner=d['bridle']['spacer_halfspan_mm']
bolt=s.world('DriverBrakeBridleBolt');nut=s.world('DriverBrakeBridleNut');cotter=s.world('DriverBrakeBridleCotter')
check('Rear bolt coaxial with both ears and distance tube',bore(bridle,rear,Y,11.2125) and bore(spacer,rear,Y,11.2125) and bore(bolt,rear,Y,11.1125))
check('Suspension lower eye receives distance-tube exterior',bore(susp,rear,Y,16.025) and bore(spacer,rear,Y,15.875) and volume(spacer.common(susp))<1e-5)
check('Actual rear bolt head seating',contact(bolt,bridle,rear+Y*outer,Y)>200,contact_mm2=contact(bolt,bridle,rear+Y*outer,Y))
check('Actual rear nut seating',contact(nut,bridle,rear-Y*outer,Y)>200,contact_mm2=contact(nut,bridle,rear-Y*outer,Y))
for sign in [-1,1]:check('Distance tube end seated '+str(sign),contact(spacer,bridle,rear+Y*sign*inner,Y)>300,contact_mm2=contact(spacer,bridle,rear+Y*sign*inner,Y))
check('Rear bolt has full132mm shank',abs(s.definition('Def_DriverBrakeBridleBolt').BoundBox.ZMax-132)<1e-7)
localbolt=s.definition('Def_DriverBrakeBridleBolt');tipw=Part.makeCylinder(8,1,V(0,0,131),Z)
check('Rear bolt retains physical tip material',contains(localbolt,tipw))
hc=d['rear_hardware_controls'];station=d['rear_hardware']['cotter_axis_mm']
check('Rear keeper crosses bolt and clears complete nut',bore(localbolt,V(0,0,station),V(1,0,0),2.48125) and volume(bolt.common(cotter))<1e-5 and volume(nut.common(cotter))<1e-5)
# Centerline material witnesses for both complete source-length cotter legs.
cp=s.definition('Def_DriverBrakeBridleCotter');conf=hc['cotter'];head=-conf['crown_radius']-conf['cotter_head_gap'];bend=conf['crown_radius']+conf['cotter_exit_gap'];r=conf['cotter_bend_radius'];ang=math.radians(conf['cotter_bend_angle']);half=conf['cotter_center_spacing']/2
tail=38.1-(bend-head)-r*ang;rot=App.Rotation(Z,-90);witnesses=[]
for sign in [-1,1]:
    points=[V(0,head,sign*half),V(0,bend,sign*half)]
    points += [V(0,bend+r*math.sin(ang*i/12),sign*(half+r*(1-math.cos(ang*i/12)))) for i in range(1,13)]
    end=points[-1]+V(0,math.cos(ang),sign*math.sin(ang))*tail;points.append(end)
    points=[rot.multVec(v) for v in points]
    witness=Part.makeCompound([Part.makeSphere(.15,v) for v in points]);witnesses.append(witness)
    check('Complete38.1mm cotter leg material '+str(sign),tail>0 and contains(cp,witness))
check('Curved bridle has actual spline faces',any(isinstance(f.Surface,Part.BSplineSurface) for f in bridle.Faces))
doc=App.openDocument(str(s.native));prior=App.openDocument(str(parent.native))
try:
    for key in s.manifest['definitions']:
        obj=doc.getObject(key)
        if key in parent.manifest['definitions']:
            old=prior.getObject(key);fields=[f for f in old.PropertiesList if old.getGroupOfProperty(f)=='Reconstruction']
            check(key+' complete inherited metadata',all(f in obj.PropertiesList and getattr(obj,f)==getattr(old,f) for f in fields))
    check('Correct M767 source identity', 'SNL:023:021' in doc.getObject('Def_DriverBrakeBridleBolt').SourceRecords)
    check('Correct bridle cotter source identity','SNL:023:023' in doc.getObject('Def_DriverBrakeBridleCotter').SourceRecords)
    check('Two construction guides excluded from physical links',len(doc.NonphysicalCenterlines.Group)==2 and all(not g.Shape.Solids and g.Name not in {r['object'] for r in s.rows.values()} for g in doc.NonphysicalCenterlines.Group))
finally:App.closeDocument(doc.Name);App.closeDocument(prior.Name)
plugged=pedal.fuse(Part.makeCylinder(19.2,38.1,main-Y*19.05,Y))
check('Negative control rejects filled main journal',not empty(plugged,Part.makeCylinder(19.0119,38.1,main-Y*19.05,Y)))
short=localbolt.cut(Part.makeBox(50,50,5,V(-25,-25,129)))
check('Negative control rejects shortened bolt',not contains(short,tipw))
check('Whole brake mechanism remains explicitly incomplete',not d['mechanism_complete'] and not s.report['geometry_integrated'] and not s.report['historical_geometry_qualified'])
result=dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),
    checker_sha256=sha(Path(__file__)),manifest_sha256=sha(s.folder/'isolated/manifest.json'),
    scope='Saved central pedal-group material, real journals, pin/head/nut/spacer seating and complete source-sized pad/cotter. Source graph, standard pedal angle and full brake function remain reconstruction assumptions.',mechanism_complete=False,geometry_integrated=False)
write(out/'independent_checks.json',result);print(len(checks),'central pedal checks passed',result['passed'],flush=True);assert result['passed']
