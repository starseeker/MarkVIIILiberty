"""Check saved M769 profile-study solids, voids, stock, receivers and negative controls.

This is CAD construction qualification only. It cannot resolve the source's
occluded joint graph or certify an inferred rod socket as historical geometry.
"""
import argparse, math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);parent=Saved((ROOT/s.report['parent_native']).parent)
out=s.folder/'checks03';out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
assert all(sha(ROOT/f)==h for f,h in s.report['input_hashes'].items())
d=s.report['details'];c=d['controls'];V=App.Vector;Y=V(0,1,0);checks=[]
def check(name,value,**kw):
    checks.append(dict(name=name,passed=bool(value),**kw))
    if not value:print('FAILED',name,kw,flush=True)
def vol(q):return sum(abs(x.Volume) for x in q.Solids)
def contains(q,w):return vol(w.cut(q))<1e-5
def empty(q,w):return vol(w.common(q))<1e-5
def cylinders(q,point,axis,r):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Cylinder) and
            abs(f.Surface.Radius-r)<1e-7 and f.Surface.Axis.cross(axis).Length<1e-7 and
            (f.Surface.Center-point).cross(axis).Length<1e-6]
def planes(q,point,axis):
    return [f for f in q.Faces if isinstance(f.Surface,Part.Plane) and
            f.normalAt(0,0).cross(axis).Length<1e-7 and abs((f.CenterOfMass-point).dot(axis))<1e-6]
check('One new shared definition and two occurrences',s.report['new_definitions']==['Def_DriverFootLink_M769'] and
      set(s.report['new_occurrences'])=={'PortDriverFootLink','StarboardDriverFootLink'} and len(s.rows)==8)
check('No inherited definition revision',not s.report['changed_definitions'])
for key in s.manifest['definitions']:
    q=s.definition(key)
    check(key+' canonical single closed solid',q.Placement.isIdentity() and q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed() and q.getTolerance(1)<=1e-4)
    if key in parent.manifest['definitions']:
        other=parent.definition(key);fuzz=min(1e-4,max(1e-7,q.getTolerance(1)+other.getTolerance(1)))
        check(key+' complete receiver material preserved',vol(q.cut(other))<1e-5 and vol(other.cut(q))<1e-5 and
              not q.cut(other,fuzz).Faces and not other.cut(q,fuzz).Faces)
for name,row in s.rows.items():
    if name in parent.rows:
        old=parent.rows[name];check(name+' retained definition and frame',row['definition']==old['definition'] and row['frame']==old['frame'])
q=s.definition('Def_DriverFootLink_M769');stock=8.+d['stock_offset_mm']
check('Supported stock variation',d['stock_offset_mm'] in [0.,1.] and c['web_stock_mm']==stock)
scale=complex(*c['side_complex_scale']);center=complex(*c['front_eyes_px'][0])
def local(pixel):
    z=-(complex(*pixel)-center)/scale;return V(z.real,0,z.imag)
for i,pixel in enumerate(c['front_eyes_px']):
    point=local(pixel);void=Part.makeCylinder(6.4,stock+2,point-Y*(stock/2+1),Y)
    ring=Part.makeCylinder(9,stock-.02,point-Y*(stock/2-.01),Y).cut(Part.makeCylinder(7,stock,point-Y*stock/2,Y))
    check(f'Eye{i+1} actual thirteen-mm through bore',bool(cylinders(q,point,Y,6.5)) and empty(q,void))
    check(f'Eye{i+1} complete surrounding stock',contains(q,ring))
check('Both actual web planes',bool(planes(q,V(0,-stock/2,0),Y)) and bool(planes(q,V(0,stock/2,0),Y)))
web_witnesses=[]
for i,pixel in enumerate([(380,408),(405,418),(430,418)]):
    point=local(pixel);w=Part.makeCylinder(1.25,stock-.02,point-Y*(stock/2-.01),Y);web_witnesses.append(w)
    check(f'Bowed web station{i+1} full material',contains(q,w))
    check(f'Bowed web station{i+1} finite thickness',all(empty(q,Part.makeSphere(.2,point+Y*sign*(stock/2+.4))) for sign in [-1,1]))
rear=local(c['socket_rear_px']);axis=rear-local(c['socket_front_px']);axis.normalize();front=rear-axis*38.1
socket_void=Part.makeCylinder(9.525,31.73,rear-axis*.01,-axis)
socket_cap=Part.makeCylinder(8,6.25,front+axis*.05,axis)
socket_wall=Part.makeCylinder(15,38.08,front+axis*.01,axis).cut(Part.makeCylinder(11,38.1,front,axis))
check('Socket actual coaxial analytic surfaces',bool(cylinders(q,rear,axis,15.875)) and bool(cylinders(q,rear,axis,9.575)))
check('Socket admits complete nominal nineteen-mm rod envelope',empty(q,socket_void))
check('Socket retains six-mm blind-end material',contains(q,socket_cap) and bool(planes(q,rear-axis*31.75,axis)))
check('Socket complete wall and full thirty-eight-mm stock',contains(q,socket_wall) and bool(planes(q,rear,axis)) and bool(planes(q,front,axis)))
check('Curved web remains analytic extrusion of a spline',any(isinstance(f.Surface,Part.SurfaceOfExtrusion) or isinstance(f.Surface,Part.BSplineSurface) for f in q.Faces))
one,two=[s.rows[x] for x in ['PortDriverFootLink','StarboardDriverFootLink']]
p1,p2=pose(one['frame']),pose(two['frame'])
check('Repeated geometry differs only by transverse translation',one['definition']==two['definition'] and
      (p1.Base-p2.Base-V(0,140,0)).Length<1e-8 and p1.Rotation.isSame(p2.Rotation,1e-10))
doc=App.openDocument(str(s.native));prior=App.openDocument(str(parent.native))
try:
    for key in s.manifest['definitions']:
        obj=doc.getObject(key)
        if key in parent.manifest['definitions']:
            old=prior.getObject(key);fields=[f for f in old.PropertiesList if old.getGroupOfProperty(f)=='Reconstruction']
            check(key+' complete retained source metadata',all(f in obj.PropertiesList and getattr(obj,f)==getattr(old,f) for f in fields))
    obj=doc.getObject('Def_DriverFootLink_M769')
    check('Actual stock and correct regeneration worker recorded',float(obj.WebStockMM)==stock and 'build_driver_foot_link_profile_v3.py' in obj.ParameterUpdate and 'inferred' in obj.ReconstructionStatus and 'unresolved' in obj.ReconstructionStatus)
    guides=doc.NonphysicalCenterlines.Group
    check('Four separate nonphysical spline guides',len(guides)==4 and all(g not in doc.Root.Group and not g.Shape.Solids and len(g.Shape.Edges)==1 and isinstance(g.Shape.Edges[0].Curve,Part.BSplineCurve) for g in guides))
    check('Guide objects excluded from all physical links',not set(g.Name for g in guides)&set(row['object'] for row in s.rows.values()))
finally:App.closeDocument(doc.Name);App.closeDocument(prior.Name)
# Mutations exercise the acceptance predicates; no candidate material is changed.
eye=local(c['front_eyes_px'][0]);plugged=q.fuse(Part.makeCylinder(6.5,stock,eye-Y*stock/2,Y))
check('Negative control rejects a filled pin hole',not empty(plugged,Part.makeCylinder(6.4,stock+2,eye-Y*(stock/2+1),Y)))
drilled=q.cut(Part.makeCylinder(9.575,50,rear+axis,-axis))
check('Negative control rejects a socket drilled through its cap',not contains(drilled,socket_cap))
bb=q.BoundBox;thinned=q.cut(Part.makeBox(bb.XLength+2,100,bb.ZLength+2,V(bb.XMin-1,stock/2-.5,bb.ZMin-1)))
check('Negative control rejects missing web thickness',not contains(thinned,web_witnesses[1]))
check('Scope remains unintegrated and mechanically unresolved',not s.report['geometry_integrated'] and not s.report['historical_geometry_qualified'] and not s.report['installation_qualified'] and bool(d['open_interfaces']))
result=dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(s.native),parent_native_sha256=sha(parent.native),
    manifest_sha256=sha(s.folder/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),
    geometry_integrated=False,mechanism_connectivity_qualified=False,historical_geometry_qualified=False,
    scope='CAD-only profile study: complete inferred web, two pin bores, blind nominal rod socket and exact retained receivers. Mechanical topology and historical identification of individual features remain unresolved.')
write(out/'independent_checks.json',result);print(len(checks),'profile-study checks, passed',result['passed'],flush=True)
assert result['passed']
