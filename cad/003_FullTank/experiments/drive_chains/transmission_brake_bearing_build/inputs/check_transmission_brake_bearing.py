"""Independent native inspection of the brake-bearing joint and preserved rotors."""
import argparse,json,math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_brake_bearing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'interface_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionBrakeBearingCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    for n,h in report['input_hashes'].items():assert sha(ROOT/n)==h,n
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    old=App.openDocument(str(ROOT/'transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd'));old.recompute();prior={i['id']:i for i in leaves(old.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);checks=[]
    def check(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def local(name,previous=False):
        s=(prior if previous else byid)[name]['shape'].copy();s.translate(-origin)
        if name.startswith('Starboard'):s.rotate(App.Vector(),App.Vector(1,0,0),180)
        return s
    def cyl(r,base,axis,h):return Part.makeCylinder(r,h,App.Vector(*base),App.Vector(*axis))
    def zero(name,s):check(name,s.Volume,0.0)
    def difference(name,a,b):zero(name+' missing',a.cut(b));zero(name+' added',b.cut(a))
    check('native occurrence count',len(byid),1321)
    for key in ['dowel','cotter']:
        target=byid['PortBrakeBearing_'+key+('0' if key=='cotter' else '')]['target']
        previous=prior['PortTransmissionBearing_InnerDowel' if key=='dowel' else 'InputInstallation_mount_cotter0']['target']
        difference('reused '+key+' definition',target.Shape,previous.Shape)
    dowels=[i for i in byid.values() if 'P_639003647733b1a1' in json.loads(i['target'].SurveyIds)]
    check('all eight source M300 installed dowels',len(dowels),8)
    check('M300 instances share one definition',len({i['target'].Name for i in dowels}),1)
    case=local('CenterTransmissionCore_bevel_case');old_case=local('CenterTransmissionCore_bevel_case',True)
    zero('M263 original material retained',old_case.cut(case))
    check('M263 remains one connected casting',len(case.Solids),1)
    masks=[]
    for sign in [-1,1]:
        lo,hi=sorted([sign*109.99,sign*309.0]);masks.append(Part.makeBox(224.02,hi-lo,253.1,App.Vector(-224.01,lo,-126.55)))
    zero('M263 additions confined to two rear bearing wings',case.cut(old_case).cut(Part.makeCompound(masks)))
    for hand in ['Port','Starboard']:
        pre=hand+'BrakeBearing_';bush=local(pre+'bush');cap=local(pre+'cap');dowel=local(pre+'dowel');drum=local(hand+'TransmissionCore_high_drum');plain=local(hand+'TransmissionCore_plain_case')
        rear=case.copy()
        if hand=='Starboard':rear.rotate(App.Vector(),App.Vector(1,0,0),180)
        assembly=doc.getObject(hand+'BrakeBearingCapAssembly')
        check(hand+' cap assembly owns cap and dowel',len(assembly.Group),2)
        check(hand+' cap assembly identity kept on container',json.loads(assembly.SurveyIds),['P_9d5234e76b63a5a1'])
        radii=sorted(set(round(f.Surface.Radius,5) for f in bush.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.y)>.999999))
        check(hand+' bush analytic bore/body/flanges',radii,[76.35,84.5,88.0])
        check(hand+' bush length from analytic end planes',bush.copy().cleaned().BoundBox.YLength,65.46571428571434)
        check(hand+' drum printed outer diameter retained',max(f.Surface.Radius for f in drum.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.y)>.99999)*2,381.0)
        old_drum=local(hand+'TransmissionCore_high_drum',True)
        zero(hand+' old drum material retained',old_drum.cut(drum))
        mask=cyl(76.201,[0,213.026,0],[0,1,0],76.0).cut(cyl(57.899,[0,213.025,0],[0,1,0],76.01))
        zero(hand+' drum additions restricted to hub exterior',drum.cut(old_drum).cut(mask))
        inner=cyl(57.8,[0,198,0],[0,1,0],93)
        difference(hand+' spline and ring pocket unchanged',old_drum.common(inner),drum.common(inner))
        for key,s in [('drum',drum),('plain case',plain)]:
            check(hand+' '+key+' nominal bush radial clearance',bush.distToShape(s)[0],.15)
            rotated=s.copy();rotated.rotate(App.Vector(),App.Vector(0,1,0),7)
            zero(hand+' '+key+' journal can turn within bush',rotated.common(bush))
        for y in [260,302]:
            # Both distinct journal stations support the common bore.
            witness=cyl(.4,[76.9,y-1,0],[0,1,0],2)
            zero(hand+' bush stock remains at journal station'+str(y),witness.cut(bush))
        for sign in [-1,1]:
            moved=bush.copy();moved.translate(App.Vector(0,sign,0))
            check(hand+' flange arrests axial bush shift'+str(sign),moved.common(cap).Volume+moved.common(rear).Volume>1)
        rotated=bush.copy();rotated.rotate(App.Vector(),App.Vector(0,1,0),3)
        check(hand+' dowel arrests bush rotation',rotated.common(dowel).Volume>1)
        radii=[f.Surface.Radius for f in dowel.Faces if isinstance(f.Surface,Part.Cylinder)]
        check(hand+' dowel printed diameter',max(radii)*2,15.875)
        check(hand+' dowel printed length',dowel.copy().cleaned().BoundBox.XLength,12.7)
        check(hand+' dowel radial engagement across cap/bush seat',dowel.BoundBox.XMin<84.5<dowel.BoundBox.XMax)
        zero(hand+' dowel stays clear of rotating journals',dowel.common(drum).fuse(dowel.common(plain)))
        # Assembly witness: with cap and high-speed drum removed, bush passes
        # axially over the existing M277 neck and seats short of its shoulder.
        # The swept material is ANNULAR; the bore itself contains the journal.
        travel=cyl(88,[0,245,0],[0,1,0],66.938).cut(cyl(76.35,[0,244,0],[0,1,0],69))
        zero(hand+' M277 neck fits through bush insertion bore',travel.common(plain))
        blocked=plain.fuse(cyl(78,[0,300,0],[0,1,0],3))
        check(hand+' negative oversized neck obstructs bush installation',travel.common(blocked).Volume>1)
        check(hand+' open journal gap retained',plain.copy().cleaned().BoundBox.YMin-drum.copy().cleaned().BoundBox.YMax,4.354285714285595)
        for n,z in enumerate([-110,110]):
            stud=local(pre+'stud'+str(n));nut=local(pre+'nut'+str(n));cotter=local(pre+'cotter'+str(n));y=279.2057142857143
            check(hand+' MX14 '+str(n)+' component-list length',stud.copy().cleaned().BoundBox.XLength,42.8625)
            sr=[f.Surface.Radius for f in stud.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.x)>.99999]
            check(hand+' MX14 '+str(n)+' half-inch diameter',max(sr)*2,12.7)
            check(hand+' MX14 '+str(n)+' nut catalogue identity',json.loads(byid[pre+'nut'+str(n)]['target'].SurveyIds),['P_fa532874f22959fa'])
            check(hand+' MX14 '+str(n)+' US threaded interval buried',-12.85+12.7<=-.15+1e-8)
            check(hand+' MX14 '+str(n)+' SAE interval covers nut',30.0125-22.225<=12.5 and 25.5<=30.0125)
            receiver=cyl(6.35,[-12.85,y,z],[1,0,0],25.35)
            zero(hand+' MX14 '+str(n)+' continuous shank passage',receiver.common(cap).fuse(receiver.common(rear)))
            check(hand+' MX14 '+str(n)+' nut seats cap',nut.distToShape(cap)[0],0.0)
            zero(hand+' MX14 '+str(n)+' cotter clears nut and stud',cotter.common(nut).fuse(cotter.common(stud)))
            for sign in [-1,1]:
                gauge=cyl(.5,[23,y-9.4,z+sign*.605],[0,1,0],19)
                zero(hand+' MX14 '+str(n)+' both cotter legs '+str(sign),gauge.cut(cotter))
            check(hand+' MX14 '+str(n)+' minimum two-leg stock',cotter.Volume>=2*math.pi*.585625**2*25.4)
            pulled=cotter.copy();pulled.translate(App.Vector(0,-8,0))
            check(hand+' MX14 '+str(n)+' bent cotter blocks withdrawal',pulled.common(stud).Volume>1e-4)
    check('stored STEP tolerances obey declared reporting allowance',all(r['step_max_tolerance_mm']<=max(1e-7,r['native_max_tolerance_mm'])+1e-10 for r in report['exchange_roundtrip_checks']))
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in checks),checks=checks,check_count=len(checks),native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),scope='Independent saved-geometry checks; no proof of historical bearing architecture, loads, lubrication, gear-train movement or full installation sequence.')
    write(out/'interface_checks.json',result);print('PASS' if result['passed'] else 'FAIL',len(checks),[r for r in checks if not r['passed']],flush=True);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
