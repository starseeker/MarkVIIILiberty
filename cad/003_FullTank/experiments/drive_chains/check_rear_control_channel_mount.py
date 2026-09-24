"""Verify saved cleat counts, manufactured stock, receiving holes and complete contacts."""
import argparse
from collections import Counter
import itertools
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
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==m['native_sha256']==r['native_sha256'];assert not (out/'independent_checks.json').exists()
parent=ROOT/r['parent_native'];old=read(parent.parent/'isolated/manifest.json');assert sha(parent)==old['native_sha256']==r['parent_native_sha256']
rows,prior=[{v['name']:v for v in d['occurrences']} for d in (m,old)]
checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
with tempfile.TemporaryDirectory(prefix='relocated_',dir=out) as temp:
    path=Path(temp)/native.name;shutil.copy2(native,path);validate_native_bindings(dict(native_file=str(path),render_occurrences=list(rows),landmarks=[]),m)
    doc=App.openDocument(str(path))
    try:
        ck('All30 physical links reopen after relocation with local identity definitions',len(rows)==30 and all(doc.getObject(v['object']).LinkedObject.Document==doc and doc.getObject(v['object']).LinkedObject.Placement.isIdentity() for v in rows.values()))
        for i in range(1,5):
            group=doc.getObject('RearChannelLeftCleat'+str(i)+'Mount');ck('Cleat'+str(i)+' has seven physical children',len(group.Group)==7 and all(v.TypeId=='App::Link' for v in group.Group))
    finally:App.closeDocument(doc.Name)
roles={n:row['definition'].removeprefix('Def_ChannelMount_') for n,row in rows.items()}
ck('Source counts: one channel, four cleats/bolts/locks/nuts, twelve rivets, one receiver',Counter(roles.values())==dict(channel=1,cleat=4,bolt=4,lock=4,nut=4,rivet=12,floor=1) and len(m['definitions'])==7)
cache={}
def definition(key,manifest=m):
    rec=manifest['definitions'][key];hash_=rec['brep_sha256']
    if hash_ not in cache:
        assert sha(rec['brep_path'])==hash_;s=Part.Shape();s.read(rec['brep_path']);assert s.Placement.isIdentity();cache[hash_]=s
    return cache[hash_].copy()
def world(name,manifest=m):
    row=next(v for v in manifest['occurrences'] if v['name']==name);s=definition(row['definition'],manifest);s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def bounds(s):
    b=s.BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def material(s):return sum(abs(v.Volume) for v in s.Solids)
for key in m['definitions']:
    s=definition(key);ck(key+' is valid, closed, one solid within kernel tolerance',s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.getTolerance(1)<=1e-4)
c=r['controls'];ch=c['channel'];cl=c['cleat'];b=c['bolt'];ri=c['rivet'];lk=c['lock']
floor=world('hull_floor_7');original=world('hull_floor_7',old);channel=world('RearControlChannelStock');new={n:world(n) for n in rows}
# Reconstruct the four receiving cylinders independently in world coordinates.
holes=[];axes=[]
for y in cl['stations_y']:
    q=V(ch['placement'][0]-ch['width']/2+cl['bolt_x'],y+cl['bolt_y'],ch['placement'][2]);axes.append(q)
    holes.append(Part.makeCylinder(b['hole_diameter']/2,c['floor_thickness']+2,q-V(0,0,c['floor_thickness']+1)))
expected_removed=original.common(Part.makeCompound(holes));removed=original.cut(floor)
ck('Floor gains no material and loses only four independent bolt passages',material(floor.cut(original))<1e-5 and material(removed.cut(expected_removed))<1e-5 and material(expected_removed.cut(removed))<1e-5,removed_mm3=material(removed))
ck('Original floor frame retained',max(abs(x-y) for x,y in zip(rows['hull_floor_7']['frame'],prior['hull_floor_7']['frame']))<1e-7)
nut=definition('Def_ChannelMount_nut');oldnut=definition(r['shared_nut_definition'],old)
ck('Existing source-sized nut material reused without changes',material(nut.cut(oldnut))<1e-5 and material(oldnut.cut(nut))<1e-5)
def faces_at(s,q,normal):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.normalAt(0,0).cross(normal).Length<1e-7 and abs((f.CenterOfMass-q).dot(normal))<1e-6]
def bearing(one,two,q,normal):return sum(f.common(g).Area for f in faces_at(one,q,normal) for g in faces_at(two,q,normal))
base=V(*ch['placement']);area=bearing(channel,floor,base,V(0,0,1));ck('Two channel flanges remain fully seated on saved floor',abs(area-2*ch['stock']*ch['length'])<1e-5,area_mm2=area)
for i,station in enumerate(cl['stations_y'],1):
    name='RearChannelLeftCleat'+str(i);cleat=new[name];bolt=new[name+'Bolt'];washer=new[name+'LockWasher'];installed_nut=new[name+'Nut'];q=axes[i-1]
    origin=V(base.x-ch['width']/2,station,base.z)
    expected=sum(f.Area for f in faces_at(cleat,origin,V(0,0,1)));area=bearing(cleat,floor,origin,V(0,0,1))
    ck(name+' complete foot bears on floor',expected>2000 and abs(area-expected)<1e-5,area_mm2=area)
    area=bearing(cleat,channel,origin,V(1,0,0));expected=cl['width']*cl['height']-3*math.pi*(ri['hole_diameter']/2)**2
    ck(name+' upright seats against drilled channel flange',abs(area-expected)<1e-5,area_mm2=area,expected_mm2=expected)
    at=q+V(0,0,cl['stock']);area=bearing(bolt,cleat,at,V(0,0,1));expected=math.sqrt(3)/2*b['head_af']**2-math.pi*(b['hole_diameter']/2)**2
    ck(name+' full bolt-head bearing on triangular foot',abs(area-expected)<1e-5,area_mm2=area,expected_mm2=expected)
    area=bearing(washer,floor,q-V(0,0,c['floor_thickness']),V(0,0,1));expected=sum(f.Area for f in faces_at(washer,q-V(0,0,c['floor_thickness']),V(0,0,1)))
    ck(name+' complete compressed washer seats under floor',expected>400 and abs(area-expected)<1e-5,area_mm2=area)
    at=q-V(0,0,c['floor_thickness']+lk['thickness']);area=bearing(installed_nut,washer,at,V(0,0,1));ck(name+' nut bears on lock washer',area>400,area_mm2=area)
    lifted=installed_nut.copy();lifted.translate(V(0,0,-.1));ck(name+' lifted nut loses washer bearing',bearing(lifted,washer,at,V(0,0,1))<1e-5)
    # Verify actual tip/outer-nut geometry instead of relying on a builder length.
    bolt_tip=bounds(bolt)[2];nut_tip=bounds(installed_nut)[2];protrusion=nut_tip-bolt_tip
    ck(name+' nominal bolt reaches through full nut with exposed thread',protrusion>2.54 and abs(protrusion-(b['underhead_length']-cl['stock']-c['floor_thickness']-lk['thickness']-19.05))<1e-6,protrusion_mm=protrusion)
    socket=Part.makeCylinder(25,60,q+V(0,0,cl['stock']))
    interference=[(n,material(socket.common(s))) for n,s in new.items() if n!=name+'Bolt' and np.all(bounds(socket)[:3]<=bounds(s)[3:]+1e-7) and np.all(bounds(s)[:3]<=bounds(socket)[3:]+1e-7)]
    ck(name+' vertical25mm-radius socket envelope clears local material',all(v<1e-5 for _,v in interference),pairs=interference,scope='Conditional tool envelope only; not a complete service sequence.')
    for j,y in enumerate(cl['rivet_y'],1):
        rivet=new[name+'Rivet'+str(j)];front=origin+V(-cl['stock'],y,cl['rivet_z']);back=origin+V(ch['stock'],y,cl['rivet_z'])
        fa=bearing(rivet,cleat,front,V(1,0,0));ba=bearing(rivet,channel,back,V(1,0,0))
        ck(name+' rivet'+str(j)+' retains both actual faces',fa>200 and ba>300,factory_seat_mm2=fa,upset_seat_mm2=ba)
        witness=Part.makeCylinder(ri['diameter']/2,cl['stock']+ch['stock'],front,V(1,0,0))
        ck(name+' rivet'+str(j)+' nominal shank clears both bores',material(witness.common(cleat))<1e-5 and material(witness.common(channel))<1e-5)
rv=definition('Def_ChannelMount_rivet');radius=ri['diameter']/2;hr=radius*ri['factory_ratio'];hh=ri['diameter']*ri['factory_height_ratio'];factory=math.pi*hh*(3*hr**2+hh**2)/6
expected=math.pi*radius**2*ri['stock_length']+factory
ck('Rivet preserves source shank stock plus factory-head material',abs(rv.Volume-expected)<1e-5,actual_mm3=rv.Volume,expected_mm3=expected)
# Local pairs include the revised receiver; no overlap is waived for hardware.
pairs=[];names=sorted(new);boxes={n:bounds(s) for n,s in new.items()}
for i,n in enumerate(names):
    for other in names[i+1:]:
        b1,b2=boxes[n],boxes[other]
        if not(np.all(b1[:3]<=b2[3:]+1e-7) and np.all(b2[:3]<=b1[3:]+1e-7)):continue
        common=new[n].common(new[other]);valid=common.isNull() or common.isValid();volume=material(common)
        pairs.append(dict(first=n,second=other,common_mm3=volume,passed=valid and volume<1e-5))
ck('All new components and drilled receiver clear one another',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
q=dict(passed=all(v['passed'] for v in checks),checks=checks,material_pairs=pairs,native_sha256=sha(native),parent_native_sha256=sha(parent),manifest_sha256=sha(out/'isolated/manifest.json'),checker_sha256=sha(Path(__file__)),historical_geometry_qualified=False,installation_qualified=False,scope='All30 saved prototype occurrences: source counts, native relocation, source-stock rivets, full bearing faces and exact floor drilling. Full parent/standard context is a separate check.')
write(out/'independent_checks.json',q);print(len(checks),'mount checks;',len(pairs),'material pairs;',q['passed'],flush=True)
for v in checks:
    if not v['passed']:print(v,flush=True)
assert q['passed']
