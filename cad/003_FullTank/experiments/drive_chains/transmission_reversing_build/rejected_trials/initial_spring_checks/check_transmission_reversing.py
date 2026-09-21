"""Check saved fork passage, retention, detent seats and bounded case revisions."""
import argparse,json,math,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_reversing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'interface_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionReversingCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    for n,h in report['input_hashes'].items():assert sha(ROOT/n)==h,n
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    old=App.openDocument(str(ROOT/'transmission_case_joint_build/TransmissionCaseJointCandidate.FCStd'));old.recompute();prior={i['id']:i for i in leaves(old.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);checks=[]
    def check(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def local(name,previous=False):
        s=(prior if previous else byid)[name]['shape'].copy();s.translate(-origin);return s
    def cy(r,lo,hi,x=0,z=0):return Part.makeCylinder(r,hi-lo,App.Vector(x,lo,z),App.Vector(0,1,0))
    def cz(r,lo,hi,x,y):return Part.makeCylinder(r,hi-lo,App.Vector(x,y,lo))
    def zero(name,s):check(name,s.Volume,0.0)
    def gap(name,s,t,v):check(name,s.distToShape(t)[0],float(v))
    s={k:local('ReversingControl_'+k) for k in ['fork','rod','nut','cotter','plunger','spring','cap']}
    case=local('CenterTransmissionCore_bevel_case');clutch=local('CenterBevelDrive_clutch')
    x,z=-181.46496913580248,159.35756172839505
    check('1372 native physical leaves',len(byid),1372)
    expected={'fork':'P_117a97fb4550e40a','rod':'P_8de9acca6cd53a2f','nut':'P_4540b96b50f55041','cotter':'P_00e7a0eee38fd982',
        'plunger':'P_01fb49ee2f45f640','spring':'P_c74821e0eb58b782','cap':'P_1940e88a774bb304'}
    for k,pid in expected.items():
        check(k+' source identity',json.loads(byid['ReversingControl_'+k]['target'].SurveyIds),[pid])
        check(k+' one connected valid solid',s[k].isValid() and len(s[k].Solids)==1)
    check('rod assembly owns exactly rod/nut/pin',sorted(o.Name for o in doc.ReversingRodAssembly.Group),
        sorted('ReversingControl_'+k for k in ['rod','nut','cotter']))
    check('rod assembly identity on container',json.loads(doc.ReversingRodAssembly.SurveyIds),['P_00245f69dbd25d7d'])
    check('M314 shared native definition',byid['ReversingControl_nut']['target']==byid['PortSmallPlanetSupports_nut0']['target'])
    check('both ring hands share revised definition',byid['PortBevelDrive_clutch_ring']['target']==byid['StarboardBevelDrive_clutch_ring']['target'])
    check('fork has cubic B-spline profile edges',any(isinstance(e.Curve,Part.BSplineCurve) and e.Curve.Degree==3 for e in s['fork'].Edges))
    # A complete annular witness proves a rotating clutch has no material in
    # the fork path, rather than relying on a few angular collision samples.
    swept=cy(99,-18.7,-13.3).cut(cy(72.3,-20,-12))
    for name,shape in [('clutch',clutch),('port ring',local('PortBevelDrive_clutch_ring')),('starboard ring',local('StarboardBevelDrive_clutch_ring'))]:
        zero(name+' clear full fork annulus',swept.common(shape))
    check('negative old clutch obstructs full fork annulus',swept.common(local('CenterBevelDrive_clutch',True)).Volume>1000)
    check('negative old starboard ring obstructs full fork annulus',swept.common(local('StarboardBevelDrive_clutch_ring',True)).Volume>1000)
    wrong=s['fork'].copy();wrong.translate(App.Vector(0,-1,0))
    check('negative axially displaced fork collides',wrong.common(local('StarboardBevelDrive_clutch_ring')).Volume>1)
    groove=cy(111,-19,-13).cut(cy(72,-21,-11))
    oldclutch=local('CenterBevelDrive_clutch',True)
    zero('clutch has no added material',clutch.cut(oldclutch))
    zero('clutch removal confined to groove',oldclutch.cut(clutch).cut(groove))
    check('clutch standard ahead center unchanged',doc.CenterBevelDrive_clutch.LinkPlacement.Base.y,-16.0)
    for side,sign in [('Port',1),('Starboard',-1)]:
        n=side+'BevelDrive_clutch_ring';oldring=local(n,True);ring=local(n)
        band=cy(111,*sorted([sign*16.65,sign*19.15]))
        zero(side+' ring has no added material',ring.cut(oldring))
        zero(side+' ring removal confined to free tips',oldring.cut(ring).cut(band))
        check(side+' ring retains four driving lugs',sum(1 for a in [45,135,225,315] if ring.isInside(App.Vector(89*math.cos(math.radians(a)),sign*25,89*math.sin(math.radians(a))),1e-7,False)),4)
    gap('fork to clutch groove',s['fork'],clutch,.3)
    gap('fork to starboard ring',s['fork'],local('StarboardBevelDrive_clutch_ring'),.45)
    gap('fork clamped by rod shoulder',s['fork'],s['rod'],0)
    gap('fork clamped by M314 nut',s['fork'],s['nut'],0)
    moved=s['nut'].copy();moved.translate(App.Vector(0,3,0))
    check('split pin obstructs nut withdrawal',moved.common(s['cotter']).Volume>.1)
    # Each analytic straight leg must be present in the saved cotter.
    wire=1.5875;offset=.79375
    for sign in [-1,1]:
        witness=Part.makeCylinder(wire,37.5,App.Vector(x+18.5,5,z+sign*offset),App.Vector(-1,0,0))
        zero('cotter complete straight leg '+str(sign),witness.cut(s['cotter']))
    zero('rod continuous case passage',cy(16,-190,-27,x,z).common(case))
    support=cy(22,-145,-120,x,z).cut(cy(16.2,-146,-119,x,z))
    # The tower opening removes only a small sector of the journal boss.
    support=support.cut(cz(9.2,z,z+80,x,-135))
    zero('case supports rod journal wall',support.cut(case))
    for y in [-135,-151,-167]:
        check('rod detent recess '+str(y),not s['rod'].isInside(App.Vector(x,y,z+15),1e-7,False))
        check('rod retains stock under detent '+str(y),s['rod'].isInside(App.Vector(x,y,z+12),1e-7,False))
    gap('detent nose seated on selected pocket',s['rod'],s['plunger'],0)
    gap('spring lower seat',s['spring'],s['plunger'],0)
    gap('spring upper seat',s['spring'],s['cap'],0)
    b=s['spring'].copy().cleaned().BoundBox
    check('installed spring height',b.ZLength,28.0)
    check('source spring OD',max(b.XLength,b.YLength),17.4625,tol=.0001)
    check('source free length stored separately',float(byid['ReversingControl_spring']['target'].SourceFreeLengthMM),38.1)
    check('spring is visibly hollow',s['spring'].Volume<800)
    check('spring has at least six turns',len(s['spring'].section(Part.makePlane(40,50,App.Vector(x,-155,180),App.Vector(1,0,0))).Edges)>=12)
    mask=cy(29.001,-191,12.001,x,z).fuse(cz(17.001,z-.001,244.001,x,-135))
    previous=local('CenterTransmissionCore_bevel_case',True)
    zero('case additions bounded to rod/detent',case.cut(previous).cut(mask))
    zero('case removal bounded to rod/detent',previous.cut(case).cut(mask))
    passed=all(r['passed'] for r in checks)
    write(out/'interface_checks.json',dict(passed=passed,checks=checks,native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),scope='Local fork/rod/detent and bounded changes; not full transmission or motion qualification.'))
    print('PASS' if passed else 'FAIL',len(checks),[r for r in checks if not r['passed']],flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
