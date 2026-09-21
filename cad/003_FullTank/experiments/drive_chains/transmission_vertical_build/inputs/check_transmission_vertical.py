"""Independent saved-CAD checks for vertical controls and bounded receivers."""
import argparse,json,math,subprocess,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_vertical_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'interface_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionVerticalCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    for n,h in report['input_hashes'].items():assert sha(ROOT/n)==h,n
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    old=App.openDocument(str(ROOT/'transmission_reversing_build/TransmissionReversingCandidate.FCStd'));old.recompute();prior={i['id']:i for i in leaves(old.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);checks=[]
    def check(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def local(name,previous=False):
        s=(prior if previous else byid)[name]['shape'].copy();s.translate(-origin);return s
    def box(x0,x1,y0,y1,z0,z1):return Part.makeBox(x1-x0,y1-y0,z1-z0,App.Vector(x0,y0,z0))
    def cz(r,z0,z1,x=-295,y=-179):return Part.makeCylinder(r,z1-z0,App.Vector(x,y,z0))
    def cx(r,x0,x1,y,z):return Part.makeCylinder(r,x1-x0,App.Vector(x0,y,z),App.Vector(1,0,0))
    def zero(name,s):check(name,s.Volume,0.0)
    def gap(name,s,t,v):check(name,s.distToShape(t)[0],float(v))
    check('1391 valid physical leaves',len(byid),1391)
    ids={'shaft':('P_14010afada4618c8',1),'upper_lever':('P_11e9d5231c9bfdc8',1),'lower_lever':('P_d75b882a9bf0c742',1),
         'key':('P_8affb0bb2aaafb99',2),'bearing':('P_96be96ec37ce54fe',2),'bolt':('P_219a5dda19fd7e88',2),
         'stud':('P_b473d025bdb9232b',2),'nut':('P_fa532874f22959fa',4),'cotter':('P_45c99004b6de95df',4)}
    check('source-owned new quantity',dict(Counter(pid for n in report['new_ids'] for pid in json.loads(byid[n]['target'].SurveyIds))),{pid:qty for pid,qty in ids.values()})
    check('shaft assembly owns shaft, two levers and two keys',sorted(o.Name for o in doc.VerticalShaftAssembly.Group),sorted('VerticalControl_'+n for n in ['shaft','upper_lever','lower_lever','key0','key1']))
    check('shaft assembly identity on container',json.loads(doc.VerticalShaftAssembly.SurveyIds),['P_ad50f346cbed4ec0'])
    check('ambiguous SNL254 identity remains conditional reference',json.loads(doc.VerticalShaftAssembly.ReferencedSurveyIds),['P_01da08ec0627f5ee'])
    check('two bearings share one definition',byid['UpperVertical_bearing']['target']==byid['LowerVertical_bearing']['target'])
    check('two keys share one definition',byid['VerticalControl_key0']['target']==byid['VerticalControl_key1']['target'])
    check('No.C size is explicitly unverified',not byid['VerticalControl_key0']['target'].SizeMappingVerified)
    shapes={n:local(n) for n in report['new_ids']}
    shaft=shapes['VerticalControl_shaft'];rod=local('ReversingControl_rod');case=local('CenterTransmissionCore_bevel_case')
    for n,s in shapes.items():check(n+' one connected valid solid',s.isValid() and len(s.Solids)==1)
    check('shaft straight axial extent',shaft.BoundBox.ZLength,436.7)
    for label,base,sgn,lever,kz in [('Upper',182,1,'upper_lever',166.85),('Lower',-205,-1,'lower_lever',-189.85)]:
        b=shapes[label+'Vertical_bearing'];l=shapes['VerticalControl_'+lever]
        gap(label+' blind journal axial/radial clearance',b,shaft,.15)
        gap(label+' lever captured at bearing',b,l,.15)
        gap(label+' hub seats on turned shaft shoulder',l,shaft,0)
        gap(label+' bearing seated on case land',b,case,0)
        check(label+' bearing closed end stock',b.isInside(App.Vector(-295,-179,base+sgn*29),1e-7,False))
        check(label+' bearing journal open',not b.isInside(App.Vector(-295,-179,base+sgn*12),1e-7,False))
        lo,hi=sorted([base+sgn*1,base+sgn*24])
        wall=cz(20,lo,hi).cut(cz(19.3,lo-1,hi+1))
        zero(label+' continuous journal support wall',wall.cut(b))
        moved=shaft.copy();moved.translate(App.Vector(0,0,sgn*.3))
        check(label+' negative shaft beyond end clearance collides',moved.common(b).Volume>1)
        check(label+' lever uses smooth B-spline arm edges',any(isinstance(e.Curve,Part.BSplineCurve) for e in l.Edges))
        key=shapes['VerticalControl_key'+('0' if label=='Upper' else '1')]
        gap(label+' key to shaft pocket',key,shaft,.05)
        gap(label+' key to lever slot',key,l,.05)
        moved=l.copy();moved.rotate(App.Vector(-295,-179,0),App.Vector(0,0,1),5)
        check(label+' key obstructs independent lever rotation',moved.common(key).Volume>1)
        z=base+sgn*16
        for kind,yy in [('bolt',-143),('stud',-215)]:
            name=label+'Vertical_'+kind;fast=shapes[name];nut=shapes[name+'_nut'];cotter=shapes[name+'_cotter']
            group=doc.getObject(name+'Assembly')
            check(name+' owns exactly fastener nut pin',sorted(o.Name for o in group.Group),sorted([name,name+'_nut',name+'_cotter']))
            check(name+' assembly identity',json.loads(group.SurveyIds),['P_ba9597468c62bb1a' if kind=='bolt' else 'P_ddcfcf306dc79587'])
            check(name+' reuses castle nut',byid[name+'_nut']['target']==byid['PortBrakeBearing_nut0']['target'])
            check(name+' reuses repaired small cotter',byid[name+'_cotter']['target']==byid['InputInstallation_mount_cotter0']['target'])
            gap(name+' nut bears on spotface',nut,b,0)
            moved=nut.copy();moved.translate(App.Vector(-3,0,0))
            check(name+' pin obstructs nut withdrawal',moved.common(cotter).Volume>.01)
            for sign in [-1,1]:
                witness=Part.makeCylinder(.585625,18,App.Vector(-315.5,yy+9,z+sign*.605),App.Vector(0,-1,0))
                zero(name+' intact straight cotter leg '+str(sign),witness.cut(cotter))
            check(name+' has nominal source half-inch shaft',any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-6.35)<1e-7 for f in fast.Faces))
            if kind=='stud':
                check(name+' printed 3-7/8in overall length',fast.BoundBox.XLength,98.425)
                target=byid[name]['target']
                check(name+' source US thread length',float(target.SourceUSThreadLengthMM),20.6375)
                check(name+' source SAE thread length',float(target.SourceSAEThreadLengthMM),22.225)
                # Nominal thread receiver includes the complete inner threaded
                # span, with material outside it and a closed inner end.
                zero(name+' inner threaded span unobstructed',cx(6.35,-243.2125,-222.575,yy,z).common(case))
                check(name+' closed blind inner end',case.isInside(App.Vector(-221.5,yy,z),1e-7,False))
                zero(name+' supported inner threaded span',cx(8,-242,-224,yy,z).cut(cx(6.6,-243,-223,yy,z)).cut(case))
            else:
                gap(name+' head seats on case spotface',fast,case,0)
                check(name+' inferred underhead length',-211-fast.BoundBox.XMin,110.0)
    finger=App.Vector(-181.46496913580248,-179,159.35756172839505)
    upper=shapes['VerticalControl_upper_lever']
    check('integral upper finger occupies linkage socket center',upper.isInside(finger,1e-7,False))
    check('rod has open cross-socket',not rod.isInside(finger,1e-7,False))
    gap('finger radial running clearance',upper,rod,.15)
    wrong=rod.copy();wrong.translate(App.Vector(0,1,0))
    check('negative displaced rod catches integral finger',wrong.common(upper).Volume>1)
    lower=shapes['VerticalControl_lower_lever']
    check('lower eye open at linkage datum',not lower.isInside(App.Vector(-295,-291,-189.85),1e-7,False))
    check('lower eye surrounding stock',lower.isInside(App.Vector(-295,-300,-189.85),1e-7,False))
    previous=local('ReversingControl_rod',True)
    rodmask=box(finger.x-17,finger.x+17,-191,-165, finger.z-17,finger.z+17)
    zero('rod additions confined to former end hole',rod.cut(previous).cut(rodmask))
    zero('rod removals confined to linkage socket',previous.cut(rod).cut(rodmask))
    # Compare saved geometry, not the unrefined intermediate Boolean result.
    previous=local('CenterTransmissionCore_bevel_case',True)
    mask=Part.makeCompound([box(-253.001,-189.999,-231.001,-114.999,z-18.001,z+18.001) for z in [198,-221]])
    added=case.cut(previous);removed=previous.cut(case)
    zero('case additions confined to two mounting lands',added.cut(mask))
    zero('case removal confined to attachment receivers',removed.cut(mask))
    check('case preserves most prior material',removed.Volume<5000)
    check('case has actual new mounting stock',added.Volume>300000)
    passed=all(r['passed'] for r in checks)
    write(out/'interface_checks.json',dict(passed=passed,checks=checks,case_change_mm3=dict(added=added.Volume,removed=removed.Volume),
        native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),scope='Saved standard vertical linkage geometry and bounded case/rod revisions. Not motion or load qualification.'))
    print('PASS' if passed else 'FAIL',len(checks),[r for r in checks if not r['passed']],flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
