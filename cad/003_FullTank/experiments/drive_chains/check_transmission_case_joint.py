"""Independent inspection of source counts, supported seals and captive fasteners."""
import argparse,json,math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_case_joint_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'interface_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionCaseJointCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    for n,h in report['input_hashes'].items():assert sha(ROOT/n)==h,n
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    old=App.openDocument(str(ROOT/'transmission_brake_bearing_build/TransmissionBrakeBearingCandidate.FCStd'));old.recompute();prior={i['id']:i for i in leaves(old.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);checks=[]
    def check(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def local(name,previous=False):
        s=(prior if previous else byid)[name]['shape'].copy();s.translate(-origin);return s
    def cyl(r,x0,x1,y,z):return Part.makeCylinder(r,x1-x0,App.Vector(x0,y,z),App.Vector(1,0,0))
    def zero(name,s):check(name,s.Volume,0.0)
    check('native occurrences',len(byid),1365)
    for key,n in [('bolt',14),('nut',14),('cotter',14),('gasket',2)]:
        instances=[i for i in byid.values() if i['id'].startswith('CentralCaseJoint_'+key)]
        check(key+' installed count',len(instances),n)
        check(key+' occurrences share one definition',len({i['target'].Name for i in instances}),1)
    assemblies=[o for o in doc.Objects if o.Name.startswith('CentralCaseBoltAssembly')]
    check('fourteen physical bolt assemblies',len(assemblies),14)
    check('each bolt assembly owns exactly three leaves',all(len(o.Group)==3 for o in assemblies))
    # Independent closed-form primitives plus quadrature for the intersection
    # of perpendicular cylinders; validates the adaptive mass calculation.
    from scipy.integrate import quad
    hole,_=quad(lambda z:4*math.sqrt(max(0,((2.38125/2+.08)**2-z*z)*(6.35**2-z*z))),
                -(2.38125/2+.08),2.38125/2+.08,epsabs=1e-10,epsrel=1e-12)
    analytic=math.pi*6.35**2*48+math.sqrt(3)/2*19.05**2*8-hole
    for r in report['exchange_roundtrip_checks']:
        if r['id'].startswith('CentralCaseJoint_bolt'):
            check(r['id']+' adaptive native mass against independent cylinder-intersection integral',r['adaptive_native']['volume_mm3'],analytic)
    for k,previous_name in [('nut','PortBrakeBearing_nut0'),('cotter','InputInstallation_mount_cotter0')]:
        s=byid['CentralCaseJoint_'+k+'0']['target'].Shape;t=prior[previous_name]['target'].Shape
        zero(k+' reused material missing',t.cut(s));zero(k+' reused material added',s.cut(t))
    case=local('CenterTransmissionCore_bevel_case');cover=local('CenterTransmissionCore_bevel_cover')
    # Bound every casting change to the fourteen joints, using measured bolt axes.
    axes=[]
    for n in range(14):
        bolt=local('CentralCaseJoint_bolt'+str(n));b=bolt.copy().cleaned().BoundBox
        y=doc.getObject('CentralCaseJoint_bolt'+str(n)).LinkPlacement.Base.y
        z=doc.getObject('CentralCaseJoint_bolt'+str(n)).LinkPlacement.Base.z;axes.append((y,z))
        radii=[f.Surface.Radius for f in bolt.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.x)>.9999]
        check('MX8 '+str(n)+' half-inch shank',max(radii)*2,12.7)
        check('MX8 '+str(n)+' inferred underhead length',b.XMax-(-16),48.0)
        passage=cyl(6.35,-16,16,y,z)
        zero('MX8 '+str(n)+' continuous receiver',passage.common(case).fuse(passage.common(cover)))
        # Measure supported bearing area with a thin annular probe behind each land.
        for side,s,x0,x1 in [('head',case,-16,-15.8),('nut',cover,15.8,16)]:
            witness=cyl(8.5,x0,x1,y,z).cut(cyl(6.6,x0-.1,x1+.1,y,z))
            zero('MX8 '+str(n)+' '+side+' supported seat',witness.cut(s))
        nut=local('CentralCaseJoint_nut'+str(n));cotter=local('CentralCaseJoint_cotter'+str(n))
        moved=nut.copy();moved.translate(App.Vector(2.5,0,0))
        check('MX8 '+str(n)+' cotter blocks nut withdrawal',moved.common(cotter).Volume>0.01)
        blocked=case.fuse(cyl(6.1,-.2,0,y,z))
        check('MX8 '+str(n)+' negative blocked receiver detected',passage.common(blocked).Volume>1)
        check('MX8 '+str(n)+' source bolt identity',json.loads(byid['CentralCaseJoint_bolt'+str(n)]['target'].SurveyIds),['P_34432e9c198c0ce2'])
    mask=Part.makeCompound([cyl(15.001,-51.001,51.001,y,z) for y,z in axes])
    for name,s in [('bevel_case',case),('bevel_cover',cover)]:
        previous=local('CenterTransmissionCore_'+name,True)
        zero(name+' removal limited to receivers/spotfaces',previous.cut(s).cut(mask))
        zero(name+' additions limited to joint lands',s.cut(previous).cut(mask))
        check(name+' connected casting',len(s.Solids),1)
    gaskets=[]
    for suffix in ['Upper','Lower']:
        g=local('CentralCaseJoint_gasket'+suffix);gaskets.append(g)
        check(suffix+' gasket thickness',g.copy().cleaned().BoundBox.XLength,.3)
        check(suffix+' gasket single connected solid',len(g.Solids),1)
        check(suffix+' M326 identity',json.loads(byid['CentralCaseJoint_gasket'+suffix]['target'].SurveyIds),['P_62e54703fd83da9a'])
        check(suffix+' full sealing land retained outside small radial relief',2700<g.Volume<2720)
        for prior_name in ['PortBevelWheelSupports_outer_bush','StarboardBevelWheelSupports_outer_bush',
                           'PortBevelWheelSupports_retainer','StarboardBevelWheelSupports_retainer']:
            check(suffix+' radial gap to '+prior_name,g.distToShape(local(prior_name))[0],.05)
        # Classify a 2mm grid through the actual thin gasket. Near-coincident
        # sheet/cover Booleans returned empty intersections despite interior
        # witnesses, so they cannot establish backing area. This is explicitly
        # a sampled support check, not exact area or sealing qualification.
        points=[];sign=1 if suffix=='Upper' else -1
        for y in range(-199,200,2):
            for z in range(59,232,2):
                v=App.Vector(0,y,sign*z)
                if g.isInside(v,1e-7,False):points.append(v)
        check(suffix+' sealing grid covers the full land',len(points)>1800)
        for label,s,x in [('case',case,-.1505),('cover',cover,.1505)]:
            unsupported=[list(v) for v in points if not s.isInside(App.Vector(x,v.y,v.z),1e-7,False)]
            check(suffix+' unsupported 2mm grid witnesses at '+label,len(unsupported),0)
            checks[-1].update(sample_count=len(points),unsupported_points_mm=unsupported,grid_spacing_mm=2)
        displaced=cover.copy();displaced.translate(App.Vector(1,0,0))
        check(suffix+' negative displaced cover fails backing witnesses',
              any(not displaced.isInside(App.Vector(.1505,v.y,v.z),1e-7,False) for v in points))
        for y,z in axes:
            zero(suffix+' gasket pierced at bolt '+str((y,z)),g.common(cyl(6.35,-1,1,y,z)))
    check('two seals separated around cross shaft',gaskets[0].distToShape(gaskets[1])[0]>100)
    passed=all(c['passed'] for c in checks)
    write(out/'interface_checks.json',dict(passed=passed,checks=checks,native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),scope='Local case joint and preservation checks, not complete transmission qualification.'))
    print('PASS' if passed else 'FAIL',len(checks),[c for c in checks if not c['passed']],flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
