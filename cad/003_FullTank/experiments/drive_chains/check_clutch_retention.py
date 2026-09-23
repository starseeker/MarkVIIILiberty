"""Independent saved wire, six head bores, parent preservation and STEP checks."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'clutch_retention_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'check_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,shape_signature
    from lib.worker import same_shape,placement_errors
    from case_joint_mass import calculator
    native=out/'TransmissionWithClutchRetention.FCStd';nh=sha(native);r=read(out/'report.json');assert r['native_sha256']==nh
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)};origin=doc.TransmissionCore.Placement.Base
    c=r['controls'];d=r['datums'];checks=[]
    def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    def near(name,a,b,tol=1e-6):ck(name,abs(a-b)<tol,dict(actual=a,expected=b,tolerance=tol))
    shapes={}
    for name in r['affected_ids']:
        s=byid[name]['shape'].copy();s.translate(-origin);shapes[name]=s
    wire=shapes['ClutchRetention_Wire'];spine=Part.Shape();spine.read(str(out/'inputs/wire_centerline.brep'))
    blank=Part.Shape();blank.read(str(out/'inputs/plunger_blank.brep'))
    ck('1653 physical occurrences',len(byid)==1653)
    ck('one new wire and six revised existing plungers',r['new_ids']==['ClutchRetention_Wire'] and r['changed_ids']==[f'ClutchCone_Plunger{n}' for n in range(1,7)])
    ck('all affected single valid solids',all(s.isValid() and len(s.Solids)==1 for s in shapes.values()))
    ck('one shared plunger definition',len({byid[n]['target'].Name for n in r['changed_ids']})==1)
    ck('spring container owns all seven components',all(byid[n]['object'].getParentGeoFeatureGroup()==doc.ClutchConeSprings for n in r['affected_ids']))
    ck('definition library hidden',not doc.Definitions.Visibility)
    ck('source mapping and piece mark',byid['ClutchRetention_Wire']['target'].OriginalMark=='SH861K' and byid['ClutchRetention_Wire']['object'].SourceRecord=='SNL:275:024')
    ck('one continuous open centreline',len(spine.Edges)==1 and len(spine.Vertexes)==2)
    near('printed30in cut length',spine.Length,30*25.4,1e-5)
    near('two separate twisted ends',(spine.Vertexes[0].Point-spine.Vertexes[1].Point).Length,2*c['wire_twist_radius'],1e-5)
    near('round wire material volume',wire.Volume,math.pi*(c['wire_diameter']/2)**2*762,.05)
    for v in spine.Vertexes:near('wire end lies on actual end face',Part.Vertex(v.Point).distToShape(wire)[0],0)
    shifted=wire.copy();shifted.translate(App.Vector(1,0,0))
    target=byid['ClutchCone_Plunger1']['target'].Shape
    extra=target.cut(blank,1e-7);ck('drilling adds no material to inherited plunger',abs(extra.Volume)<1e-5 and not extra.Faces)
    # Check the unchanged shaft region in both directions, independent of head bore settings.
    region=Part.makeBox(119.825,30,30,App.Vector(0,-15,-15))
    a=blank.common(region);b=target.common(region)
    ck('shaft and tail material preserved',not a.cut(b,1e-7).Faces and not b.cut(a,1e-7).Faces)
    near('printed plunger overall length',target.BoundBox.XLength,4.875*25.4)
    for n in range(1,7):
        name=f'ClutchCone_Plunger{n}';s=shapes[name];theta=math.radians(30+(n-1)*60)
        radial=App.Vector(0,math.cos(theta),math.sin(theta));tangent=App.Vector(0,-math.sin(theta),math.cos(theta))
        point=App.Vector(1019.3,0,0)+radial*114
        line=Part.makeLine(point-tangent*8,point+tangent*8)
        ck(name+'/actual through passage',not s.section(line).Vertexes)
        ck(name+'/wire through head centre',wire.isInside(point,1e-7,False) and not s.isInside(point,1e-7,False))
        for offset in [-5,0,5]:
            p=point+tangent*offset
            ck(name+f'/void witness {offset}',abs(s.common(Part.makeSphere(.05,p)).Volume)<1e-8)
        ck(name+'/head material above and below bore',all(s.isInside(point+App.Vector(v,0,0),1e-7,False) for v in [-1.7,1.7]))
        near(name+'/wire clears head',s.common(wire).Volume,0,1e-5)
        ck(name+'/misaligned wire catches solid head',s.common(shifted).Volume>.001)
        # Frame witnesses ensure the shared hole is correctly clocked, without relying on BBoxes.
        obj=byid[name]['object'];frame=obj.getParentGeoFeatureGroup().getGlobalPlacement().multiply(obj.LinkPlacement)
        expected=point+origin
        near(name+'/head centre frame',(frame.multVec(App.Vector(121.825,0,0))-expected).Length,0)
        near(name+'/bore tangent frame',(frame.multVec(App.Vector(121.825,0,1))-expected-tangent).Length,0)
        near(name+'/radial frame',(frame.multVec(App.Vector(121.825,1,0))-expected-radial).Length,0)
    parent=App.openDocument(str(HERE/'clutch_cone_build/TransmissionWithClutchCone.FCStd'));old={i['id']:i for i in leaves(parent.Root)}
    bad=[]
    for name,i in old.items():
        if name in r['changed_ids']:continue
        j=byid[name];t,angle=placement_errors(i['shape'].Placement,j['shape'].Placement)
        if not same_shape(shape_signature(i['shape']),shape_signature(j['shape'])) or t>=1e-6 or angle>=1e-8:bad.append(name)
    ck('1646 other parent occurrences preserved',len(old)-6==1646 and not bad,bad)
    ck('input blank matches actual parent definition',not blank.cut(old['ClutchCone_Plunger1']['target'].Shape,1e-7).Faces and not old['ClutchCone_Plunger1']['target'].Shape.cut(blank,1e-7).Faces)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks))
    print('Independent checks',len(checks),'failed',[x for x in checks if not x['passed']],flush=True)
    assert all(x['passed'] for x in checks)
    mass=calculator(out/'check_runtime/mass');exchange=[]
    for label,expected in [('Definitions',[(k,doc.getObject(k).Shape) for k in read(out/'definition_order.json')]),
                           ('Installation',[(n,byid[n]['shape']) for n in r['affected_ids']])]:
        path=out/('ClutchRetention'+label+'.step');loaded=Part.Shape();loaded.read(str(path))
        assert loaded.isValid() and len(loaded.Solids)==len(expected)
        remaining=[(s,s.CenterOfMass,s.Volume) for s in loaded.Solids]
        for key,shape in expected:
            one=shape.Solids[0];center=one.CenterOfMass;vol=one.Volume;area=one.Area
            idx=min(range(len(remaining)),key=lambda j:(center-remaining[j][1]).Length+abs(vol-remaining[j][2])/max(area,1));two=remaining.pop(idx)[0]
            ma=mass(one,label+'_'+key+'_native');mb=mass(two,label+'_'+key+'_step')
            ta=one.getTolerance(1);tb=two.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
            missing=one.cut(two).Volume;added=two.cut(one).Volume;dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length
            passed=abs(missing)<1e-5 and abs(added)<1e-5 and not one.cut(two,fuzzy).Faces and not two.cut(one,fuzzy).Faces and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=(one.Area+two.Area)/2*(ta+tb) and dc<max(1e-6,ta+tb)
            exchange.append(dict(scope=label,part=key,passed=passed,missing_mm3=missing,added_mm3=added,mass_difference_mm3=dv,centroid_difference_mm=dc))
            print(label,key,passed,flush=True)
            write(out/'exchange_progress.json',dict(checks=exchange))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in exchange),native_sha256=nh,checker_sha256=sha(Path(__file__)),
        artifact_hashes={n:sha(out/n) for n in ['ClutchRetentionDefinitions.step','ClutchRetentionInstallation.step']},checks=exchange))
    assert all(x['passed'] for x in exchange)
finally:
    runtime.close()
