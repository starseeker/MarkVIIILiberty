"""Independent section, floor interface, neighbor and STEP checks for stock trials."""
import argparse
import math
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
import Import
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
from lib.visual_review import shaded
from lib.cad_build import COLORS
from lib.mass_properties import AdaptiveMass
V=App.Vector
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256'];assert not (out/'independent_checks.json').exists()
checks=[]
def ck(name,passed,**kw):checks.append(dict(name=name,passed=bool(passed),**kw))
with tempfile.TemporaryDirectory(prefix='relocated_',dir=out) as temp:
    copy=Path(temp)/native.name;shutil.copy2(native,copy);doc=App.openDocument(str(copy))
    try:
        body=doc.getObject('Def_RearControlChannelStock');link=doc.getObject('RearControlChannelStock')
        one=body.Shape.copy();pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement)
        installed=one.copy();installed.Placement=pose
        ck('Saved local definition, one physical occurrence and direct root ownership',
           body.Placement.isIdentity() and one.Placement.isIdentity() and len(doc.Definitions.Group)==1
           and link.LinkedObject==body and link.LinkedObject.Document==doc and list(doc.Root.Group)==[link])
        ck('Actual saved metadata identifies unfinished M4128 stock',body.PieceMark=='M4128' and body.GeometryStatus=='unfinished_stock_hypothesis')
        ck('Saved placement equals documented floor/station datum',math.dist(list(pose.Base),r['controls']['placement_world_mm'])<1e-7 and pose.Rotation.isSame(App.Rotation(),1e-9))
    finally:App.closeDocument(doc.Name)
d=r['controls']['dimensions_mm'];w,h,t,L=[d[n] for n in ('width','height','stock','length')]
ck('One valid closed solid within unchanged kernel tolerance',one.isValid() and len(one.Solids)==1 and one.Solids[0].isClosed() and one.getTolerance(1)<=1e-4)
b=one.BoundBox
ck('Saved envelope and transverse centered span',max(abs(x-y) for x,y in zip([b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax],[-w/2,w/2,-L/2,L/2,0,h]))<1e-7)
# Independent reference material: top rectangular web and two lower legs.
web=Part.makeBox(w,L,t,V(-w/2,-L/2,h-t))
legs=[Part.makeBox(t,L,h-t,V(x,-L/2,0)) for x in (-w/2,w/2-t)]
reference=web.fuse(legs[0]).fuse(legs[1]);missing=reference.cut(one);added=one.cut(reference)
ck('Independent web and leg material agree in both directions',abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5,missing_mm3=missing.Volume,added_mm3=added.Volume)
void=Part.makeBox(w-2*t,L,h-t,V(-w/2+t,-L/2,0))
ck('Underside void remains open over the complete length',abs(one.common(void).Volume)<1e-5)
analytic_volume=L*(w*t+2*t*(h-t));analytic_z=(w*t*(h-t/2)+2*t*(h-t)*(h-t)/2)/(w*t+2*t*(h-t))
ck('Independent prismatic mass and centroid',abs(one.Volume-analytic_volume)<1e-5 and math.dist(list(one.CenterOfMass),[0,0,analytic_z])<1e-7,volume_mm3=one.Volume,centroid_mm=list(one.CenterOfMass))

packet=H/'transmission_controls_study';parent=packet/'us_nuts01';m=read(parent/'isolated/manifest.json');pr=read(parent/'report.json');parent_native=parent/pr['native_file']
assert sha(parent_native)==m['native_sha256'];study=read(packet/'channel_context01/report.json');assert study['native_sha256']==m['native_sha256'] and sha(parent/'isolated/manifest.json')==study['manifest_sha256']
sm=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';standard=read(sm);assert sha(sm)==study['standard_manifest_sha256'];assert all(sha(ROOT/f)==digest for f,digest in standard['native_files'].items())
maps={origin:{v['name']:v for v in data['occurrences']} for origin,data in [('development',m),('retained_standard',standard)]};cache={}
def shape(name,origin='development'):
    row=maps[origin][name];data=m if origin=='development' else standard;rec=data['definitions'][row['definition']];key=rec['brep_sha256']
    if key not in cache:
        assert sha(rec['brep_path'])==key;s=Part.Shape();s.read(rec['brep_path']);assert s.Placement.isIdentity();cache[key]=s
    s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s,key
def bounds(s):
    b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def overlap(b,c):return all(b[i]<=c[i+3]+1e-7 and b[i+3]>=c[i]-1e-7 for i in range(3))
bb=bounds(installed);region=study['region_world_mm']
ck('Whole stock lies within measured context region',all(bb[i]>=region[i] and bb[i+3]<=region[i+3] for i in range(3)))
pairs=[];selected=[]
for v in study['measurements']:
    if not overlap(bb,v['bounds_mm']):continue
    other,_=shape(v['name'],v['origin']);common=installed.common(other);volume=sum(abs(s.Volume) for s in common.Solids);valid=common.isNull() or common.isValid()
    pairs.append(dict(other=v['name'],origin=v['origin'],common_mm3=volume,valid_common=valid,passed=valid and volume<1e-5))
    if v['origin']=='development':selected.append(v['name'])
validate_native_bindings(dict(native_file=str(parent_native),render_occurrences=selected,landmarks=[]),m)
ck('Channel material clears all neighboring development and retained standard solids',all(v['passed'] for v in pairs),pairs=len(pairs),failed=[v for v in pairs if not v['passed']])
floor,_=shape('hull_floor_7');z=r['controls']['placement_world_mm'][2]
def plane_faces(s,z):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and abs(abs(f.normalAt(0,0).z)-1)<1e-7 and abs(f.CenterOfMass.z-z)<1e-7]
def seat(s):return sum(f.common(g).Area for f in plane_faces(s,z) for g in plane_faces(floor,z))
area=seat(installed);ck('Both lower flanges bear on actual floor upper face',abs(area-2*t*L)<1e-5,area_mm2=area,expected_mm2=2*t*L)
lift=installed.copy();lift.translate(V(0,0,.1));ck('Lifted stock loses floor bearing',seat(lift)<1e-5)
intrusion=installed.copy();intrusion.translate(V(0,0,-1));volume=intrusion.common(floor).Volume;ck('Floor intrusion negative control is detected',volume>1,common_mm3=volume)
q=dict(passed=all(v['passed'] for v in checks),checks=checks,material_pairs=pairs,native_sha256=sha(native),parent_native_sha256=sha(parent_native),checker_sha256=sha(Path(__file__)),context_sha256=sha(packet/'channel_context01/report.json'),scope='Unfinished channel stock section, floor bearing and all solids within the independently measured enclosing region. No cleat/rivet/hole qualification.',historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',q);print('Stock checks',len(checks),'pairs',len(pairs),'passed',q['passed'],flush=True)
if not q['passed']:
    print([v for v in checks if not v['passed']],flush=True)

Part.setStaticValue('write.surfacecurve.mode',1)
# Explicit task-local setting: default single-object export drops its placement.
# The retained default/import/step probe establishes the actual preference group.
App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement',True)
mass=AdaptiveMass(out/'adaptive_mass_runtime');exchange=[]
for name,s in [('Definition',one),('Installed',installed)]:
    path=out/('RearControlChannelStock'+name+'.step');assert not path.exists();doc=App.newDocument('ChannelExport'+name)
    try:
        obj=doc.addObject('PartDesign::Feature','Channel');obj.Shape=s;doc.recompute();Import.export([obj],str(path))
    finally:App.closeDocument(doc.Name)
    text=path.read_text();restored=Part.Shape();restored.read(str(path));assert len(restored.Solids)==1
    two=restored.Solids[0];ta,tb=s.getTolerance(1),two.getTolerance(1);fuzz=min(1e-4,max(1e-7,ta+tb));missing=s.cut(two);added=two.cut(s);fm,fa=len(s.cut(two,fuzz).Faces),len(two.cut(s,fuzz).Faces)
    ma,mb=mass.measure(s),mass.measure(two);delta=math.dist(ma['centroid_mm'],mb['centroid_mm'])
    passed=two.isValid() and two.isClosed() and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10 and ma['converged'] and mb['converged'] and delta<1e-5 and 'PCURVE(' in text and text.count('NEXT_ASSEMBLY_USAGE_OCCURRENCE')==0
    exchange.append(dict(scope=name,passed=passed,step_sha256=sha(path),missing_mm3=missing.Volume,added_mm3=added.Volume,fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_tolerance_mm=ta,step_tolerance_mm=tb,native_mass=ma,step_mass=mb,centroid_error_mm=delta))
write(out/'exchange_checks.json',dict(passed=all(v['passed'] for v in exchange),checks=exchange,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),mass_provenance=mass.provenance,export_settings={'write.surfacecurve.mode':1,'Mod/Import/ExportKeepPlacement':True}))
COLORS.update(Channel=(.77,.50,.26),Context=(.52,.59,.62))
item=dict(id='RearControlChannelStock',shape=installed,target=SimpleNamespace(Shape=one),definition='M4128_unfinished_stock_'+sha(native),system='Channel',representation='assembly')
context=[]
for name in ['hull_floor_7','ClutchSupport_LeftBracket','ClutchSupport_RightBracket','ClutchSupport_AuxShaft','ClutchThrowout_Shaft','EngineFrame_RearChannel']:
    s,key=shape(name);context.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=cache[key]),definition=key,system='Context',representation='assembly'))
shaded([item],out/'channel_stock_context.svg',(1,-1,.6),'M4128 | unfinished channel stock and existing floor/clutch supports',context=context)
shaded([item],out/'channel_stock_section.svg',(0,-1,.05),'M4128 | open underside and two floor-bearing flanges')
write(out/'render_receipt.json',dict(native_sha256=sha(native),parent_native_sha256=sha(parent_native),images={f:sha(out/f) for f in ['channel_stock_context.png','channel_stock_section.png']},checker_sha256=sha(Path(__file__)),historical_camera_fitted=False))
print('STEP comparisons',len(exchange),'passed',all(v['passed'] for v in exchange),flush=True)
assert q['passed'] and all(v['passed'] for v in exchange)
