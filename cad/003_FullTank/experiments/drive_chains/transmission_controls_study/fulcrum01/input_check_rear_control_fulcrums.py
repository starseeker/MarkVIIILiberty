"""Inspect saved fulcrum stock, receiving holes, lever bearings and axial retention."""
import argparse
from collections import Counter
import math
from pathlib import Path
import shutil
import sys
import tempfile
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
V=App.Vector
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']==m['native_sha256']
source=ROOT/r['parent_native'];old=read(source.parent/'isolated/manifest.json');assert sha(source)==r['parent_native_sha256']==old['native_sha256']
assert not (out/'independent_checks.json').exists()
rows={v['name']:v for v in m['occurrences']};c=r['controls'];b=c['bracket'];l=c['lever'];w=c['washer'];ri=c['rivet'];checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
def volume(s):return sum(abs(v.Volume) for v in s.Solids)
with tempfile.TemporaryDirectory(prefix='relocated_fulcrums_',dir=out) as temp:
    path=Path(temp)/native.name;shutil.copy2(native,path)
    validate_native_bindings(dict(native_file=str(path),render_occurrences=list(rows),landmarks=[]),m)
    doc=App.openDocument(str(path))
    try:
        ck('All25 physical links remain local and identity-defined after relocation',len(rows)==25 and all(doc.getObject(row['object']).LinkedObject.Document==doc and doc.getObject(row['object']).LinkedObject.Placement.isIdentity() for row in rows.values()))
        for name in c['stations']:
            group=doc.getObject(name+'ControlFulcrum');ck(name+' owns six physical members',len(group.Group)==6 and all(v.TypeId=='App::Link' for v in group.Group))
    finally:App.closeDocument(doc.Name)
roles=Counter(v['definition'].removeprefix('Def_ControlFulcrum_') for v in rows.values())
ck('Source counts and shared foot-lever definition',roles==dict(channel=1,bracket=4,cotter=4,washer=4,rivet=8,lever_track=2,lever_low_left=1,lever_low_right=1) and len(m['definitions'])==8)
cache={}
def definition(key,manifest=m):
    d=manifest['definitions'][key];digest=d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path'])==digest;s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[digest]=s
    return cache[digest].copy()
def world(name,manifest=m):
    row=next(v for v in manifest['occurrences'] if v['name']==name);s=definition(row['definition'],manifest);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
for key in m['definitions']:
    s=definition(key);ck(key+' valid closed one-solid definition',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
shapes={n:world(n) for n in rows};channel=shapes[c['channel_occurrence']];original=world(c['channel_occurrence'],old)
holes=[]
for station in c['stations'].values():
    pose=App.Placement(V(*station['pivot']),App.Rotation(V(0,0,1),station['inboard_clock']))
    for y in b['rivet_y']:
        q=pose.multVec(V(b['rivet_x'],y,0));holes.append(Part.makeCylinder(ri['hole_diameter']/2,c['channel_stock']+2,q-V(0,0,c['channel_stock']+1)))
expected=original.common(Part.makeCompound(holes));removed=original.cut(channel)
ck('Channel loses exactly eight vertical rivet passages and gains no material',volume(channel.cut(original))<1e-5 and volume(removed.cut(expected))<1e-5 and volume(expected.cut(removed))<1e-5,removed_mm3=volume(removed))
def faces(s,z):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and abs(abs(f.normalAt(0,0).z)-1)<1e-7 and abs(f.CenterOfMass.z-z)<1e-6]
def bearing(one,two,z):return sum(f.common(g).Area for f in faces(one,z) for g in faces(two,z))
for name,station in c['stations'].items():
    bracket=shapes[name+'FulcrumBracket'];lever=shapes[name+'HorizontalLever'];washer=shapes[name+'FulcrumSpringWasher'];cotter=shapes[name+'FulcrumCotter']
    base=V(*station['pivot']);pose=App.Placement(App.Matrix(*rows[name+'FulcrumBracket']['frame']));seat=base.z+b['foot_stock']
    expected=math.pi*(l['hub_radius']**2-(l['bore_diameter']/2)**2);area=bearing(bracket,lever,seat)
    center=V(base.x,base.y,seat)
    annulus=Part.Face(Part.Wire([Part.makeCircle(l['hub_radius'],center)])).cut(Part.Face(Part.Wire([Part.makeCircle(l['bore_diameter']/2,center)])))
    contact=Part.makeCompound([f.common(g) for f in faces(bracket,seat) for g in faces(lever,seat)])
    uncovered=annulus.cut(contact)
    ck(name+' full annular hub bearing',not uncovered.Faces and area>=expected-1e-5,full_contact_area_mm2=area,hub_annulus_mm2=expected,uncovered_hub_area_mm2=uncovered.Area)
    witness=Part.makeCylinder(b['journal_diameter']/2,l['hub_height']+w['stock'],V(base.x,base.y,seat))
    ck(name+' journal clears full lever and washer bores',volume(witness.common(lever))<1e-5 and volume(witness.common(washer))<1e-5)
    expected=math.pi*(w['outer_radius']**2-w['bore_radius']**2);area=bearing(lever,washer,seat+l['hub_height'])
    ck(name+' full spring-washer bearing on hub',abs(area-expected)<1e-5,area_mm2=area)
    ck(name+' cotter touches washer without interference',cotter.distToShape(washer)[0]<1e-6 and volume(cotter.common(washer))<1e-5)
    lifted=washer.copy();lifted.translate(V(0,0,.1));blocked=volume(lifted.common(cotter))
    ck(name+' cotter blocks upward washer motion',blocked>1e-5,overlap_at_point1mm_lift=blocked)
    lifted=lever.copy();lifted.translate(V(0,0,.1));ck(name+' lifted lever loses thrust bearing',bearing(bracket,lifted,seat)<1e-5)
    # Pin-size witness and actual tip remaining beyond its transverse bore.
    hole=Part.makeCylinder(c['cotter']['cotter_diameter']/2,b['journal_diameter']+2,pose.multVec(V(0,-b['journal_diameter']/2-1,r['details']['cotter_center_z_mm'])),pose.Rotation.multVec(V(0,1,0)))
    ck(name+' nominal cotter passage clear through journal',volume(hole.common(bracket))<1e-5)
    ck(name+' journal cap remains beyond cotter bore',b['foot_stock']+b['journal_height']-r['details']['cotter_center_z_mm']-b['cotter_hole_diameter']/2>4)
    for i,y in enumerate(b['rivet_y'],1):
        q=pose.multVec(V(b['rivet_x'],y,0));rv=shapes[name+'FulcrumRivet'+str(i)]
        expected=math.pi*((ri['diameter']/2*ri['factory_ratio'])**2-(ri['hole_diameter']/2)**2)
        fa=bearing(rv,bracket,seat);ba=bearing(rv,channel,base.z-c['channel_stock'])
        ck(name+' rivet'+str(i)+' retains both full head annuli',abs(fa-expected)<1e-5 and abs(ba-expected)<1e-5,front_mm2=fa,back_mm2=ba)
        pad=Part.Face(Part.Wire([Part.makeCircle(b['rivet_pad_radius'],q)]))
        bore=Part.Face(Part.Wire([Part.makeCircle(ri['hole_diameter']/2,q)]));pad=pad.cut(bore)
        contact=Part.makeCompound([f.common(g) for f in faces(bracket,base.z) for g in faces(channel,base.z)])
        uncovered=pad.cut(contact)
        ck(name+' rivet'+str(i)+' root pad fully supported',not uncovered.Faces,uncovered_area_mm2=uncovered.Area,scope='Full root pad, with documented cantilevered pivot outside channel.')
        witness=Part.makeCylinder(ri['diameter']/2,b['foot_stock']+c['channel_stock'],q-V(0,0,c['channel_stock']))
        ck(name+' rivet'+str(i)+' shank clears both holes',volume(witness.common(bracket))<1e-5 and volume(witness.common(channel))<1e-5)
    lp=App.Placement(App.Matrix(*rows[name+'HorizontalLever']['frame']))
    for role,xy in c['lever_profiles'][station['lever_profile']].items():
        q=lp.multVec(V(*xy,0));tool=Part.makeCylinder(l['end_bore_diameter']/2,l['stock']+2,q-V(0,0,1))
        ck(name+' '+role+' rod-end bore traverses lever',volume(tool.common(lever))<1e-5)
rv=definition('Def_ControlFulcrum_rivet');rad=ri['diameter']/2;hr=rad*ri['factory_ratio'];hh=ri['diameter']*ri['factory_height_ratio'];expected=math.pi*rad**2*ri['stock_length']+math.pi*hh*(3*hr**2+hh**2)/6
ck('Rivet preserves literal shank stock plus factory head',abs(rv.Volume-expected)<1e-5,actual_mm3=rv.Volume,expected_mm3=expected)
ck('Split pin retains source50.8mm under-eye centerline per leg',abs(r['details']['cotter']['total_leg_centerline_mm']-50.8)<1e-8,scope='Analytic formed-pin construction; eye lead junctions overlap by the documented allowance, not an exact whole-wire stock-volume claim.')
def box(s):
    b=s.BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
boxes={n:box(s) for n,s in shapes.items()};pairs=[];names=sorted(shapes)
for i,n in enumerate(names):
    for other in names[i+1:]:
        a,bx=boxes[n],boxes[other]
        if not(np.all(a[:3]<=bx[3:]+1e-7) and np.all(bx[:3]<=a[3:]+1e-7)):continue
        common=shapes[n].common(shapes[other]);valid=common.isNull() or common.isValid();v=volume(common)
        pairs.append(dict(first=n,second=other,common_mm3=v,passed=valid and v<1e-5))
ck('All25 saved occurrences clear one another',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
result=dict(passed=all(v['passed'] for v in checks),checks=checks,material_pairs=pairs,native_sha256=sha(native),parent_native_sha256=sha(source),manifest_sha256=sha(out/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),scope='Saved local25-occurrence fulcrum assembly. Independent holes, bearing faces, root-pad support, axial retention and actual material; whole parent/standard context checked separately.',historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result);print(len(checks),'fulcrum checks;',len(pairs),'local pairs;',result['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert result['passed']
