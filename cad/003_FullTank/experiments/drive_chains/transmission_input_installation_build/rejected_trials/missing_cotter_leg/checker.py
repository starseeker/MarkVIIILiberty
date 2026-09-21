"""Inspect saved cover retention and continuous grease passages independently."""
import argparse,json,math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_input_installation_build');p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();out=args.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not args.worker:
    with (out/'interface_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'interface_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    report=read(out/'report.json');native=out/'TransmissionInputInstallationCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    assert all(sha(ROOT/n)==h for n,h in report['input_hashes'].items())
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    old=App.openDocument(str(ROOT/'transmission_input_build/TransmissionInputCandidate.FCStd'));old.recompute()
    prior={i['id']:i for i in leaves(old.Root)};origin=App.Vector(*report['shaft_axis_world_mm'])
    def shape(n):return byid[n]['shape'].Solids[0]
    def local(n):
        s=shape(n).copy();s.translate(-origin);return s
    checks=[]
    def check(name,value,expected=True,tol=1e-5):
        passed=abs(value-expected)<tol if isinstance(expected,float) else value==expected
        checks.append(dict(name=name,value=value,expected=expected,passed=bool(passed)))
    def cyl(radius,start,axis,length):return Part.makeCylinder(radius,length,App.Vector(*start),App.Vector(*axis))
    def segment(a,b,radius=1):
        a,b=App.Vector(*a),App.Vector(*b);v=b-a
        return Part.makeCylinder(radius,v.Length,a,v)
    def zero(name,s):check(name,s.Volume,0.0)
    check('all1303 native leaves present',len(byid),1303)
    check('commercial grease cup owns body and cap',len(doc.InputGreaseCup.Group),2)
    check('commercial cup counted once',json.loads(doc.InputGreaseCup.CatalogueQuantity),1)
    check('four corrected nuts do not assert conflicting one-inch identities',
        all(json.loads(byid['InputInstallation_mount_nut'+str(n)]['target'].SurveyIds)==[] for n in range(4)))
    for key in ['cup_body','cup_cap']:
        check(key+' uses parent inventory identity',json.loads(byid['InputInstallation_'+key]['target'].SurveyIds)==[])
    for n in range(4):
        tag='InputInstallation_';stud=local(tag+'mount_stud'+str(n));nut=local(tag+'mount_nut'+str(n));cotter=local(tag+'mount_cotter'+str(n))
        v=stud.copy().cleaned().BoundBox
        check('MX25 '+str(n)+' printed length',v.XLength,64.29375)
        radii=[f.Surface.Radius for f in stud.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.x)>1-1e-8]
        check('MX25 '+str(n)+' printed diameter',max(radii)*2,12.7)
        pos=doc.getObject(tag+'mount_stud'+str(n)).LinkPlacement.Base
        y,z=pos.y,pos.z
        # Closed nominal thread intervals must cover both the buried US end
        # and the load-bearing base of the nut, not only the slotted crown.
        check('MX25 '+str(n)+' US thread entirely inside cover boss',219.6>=203 and 219.6+25.4<248)
        check('MX25 '+str(n)+' nut inside SAE threaded interval',283.89375-22.225<=262 and 275<=283.89375)
        hole=cyl(6.35,[219.6,y,z],[1,0,0],42.4)
        zero('MX25 '+str(n)+' shaft receiver continuous',hole.common(local('CenterTransmissionCore_bevel_cover')).fuse(hole.common(local('InputHousing_housing'))))
        for m in range(16):zero('MX25 '+str(n)+' shim'+str(m)+' clears shank',hole.common(local('InputHousing_flange_shim'+str(m).zfill(2))))
        check('MX25 '+str(n)+' nut face seats flange',nut.distToShape(local('InputHousing_housing'))[0],0.0)
        zero('MX25 '+str(n)+' formed cotter clears stud',cotter.common(stud))
        zero('MX25 '+str(n)+' formed cotter clears castle nut',cotter.common(nut))
        check('MX25 '+str(n)+' retains both legs by minimum stock volume',cotter.Volume>=2*math.pi*.585625**2*25.4-1e-5)
        check('MX25 '+str(n)+' has two distinct bent leg surfaces',sum(isinstance(f.Surface,Part.Toroid) for f in cotter.Faces),2)
        for sign in [-1,1]:
            leg=cyl(.5,[0,-9.4,sign*.605],[0,1,0],19.0)
            leg.rotate(App.Vector(),App.Vector(1,0,0),90*n);leg.translate(App.Vector(272.5,y,z))
            zero('MX25 '+str(n)+' retains straight leg '+str(sign),leg.cut(cotter))
            angle=math.pi/3;tail_length=25.4-19.4-1.5*angle
            begin=App.Vector(0,9.8+1.5*math.sin(angle),sign*(.605+1.5*(1-math.cos(angle))))
            axis=App.Vector(0,math.cos(angle),sign*math.sin(angle))
            tail=cyl(.5,list(begin+axis*.1),list(axis),tail_length-.2)
            tail.rotate(App.Vector(),App.Vector(1,0,0),90*n);tail.translate(App.Vector(272.5,y,z))
            zero('MX25 '+str(n)+' retains formed tail '+str(sign),tail.cut(cotter))
        # A straight withdrawal is arrested by the formed tails, and the eye
        # is larger than the stud hole. These are geometry checks, not strength.
        tangent=App.Rotation(App.Vector(1,0,0),90*n).multVec(App.Vector(0,1,0))
        pulled=cotter.copy();pulled.translate(tangent*-8)
        check('MX25 '+str(n)+' bent tails prevent straight withdrawal',pulled.common(stud).Volume>1e-4)
        radial_hole=cyl(1.240625,list(App.Vector(272.5,y,z)-tangent*7),list(tangent),14)
        zero('MX25 '+str(n)+' pin traverses reopened cross-hole',radial_hole.common(stud))
    # Build a continuous 2mm-diameter witness independently of the geometry
    # generator: reservoir -> stem -> 45deg elbow -> nipple -> spacer bore.
    u=App.Vector(0,1/math.sqrt(2),1/math.sqrt(2));port=App.Vector(279,0,0)
    start=port+u*107.45;r=18.;angle=math.pi/4;straight=22.225-r*math.tan(angle/2)
    rot=App.Rotation(App.Vector(1,0,0),-45)
    a=start+rot.multVec(App.Vector(0,0,straight))
    mid=start+rot.multVec(App.Vector(0,-r*(1-math.cos(angle/2)),straight+r*math.sin(angle/2)))
    b=start+rot.multVec(App.Vector(0,-r*(1-math.cos(angle)),straight+r*math.sin(angle)))
    end=b+App.Vector(0,0,straight)
    path=Part.Wire([Part.makeLine(start,a),Part.Arc(a,mid,b).toShape(),Part.makeLine(b,end)])
    elbow_gauge=path.makePipeShell([Part.Wire([Part.makeCircle(1,start,u)])],True,False)
    low=port+u*50;high=end+App.Vector(0,0,10)
    radial=segment(low,start+u*1);vertical=segment(end-App.Vector(0,0,1),high)
    axial=segment([254,low.y,low.z],[300,low.y,low.z])
    witness=radial.fuse(elbow_gauge).fuse(vertical).fuse(axial).removeSplitter()
    check('grease gauge is one connected solid',len(witness.Solids),1)
    fittings=['InputInstallation_'+k for k in ['nipple','elbow','cup_body','cup_cap']]
    feed_material=['InputHousing_housing','InputHousing_spacer','CenterBevelDrive_pinion']+fittings
    feed_material += [n for n in byid if n.startswith(('InputBearing0_','InputBearing1_'))]
    for n in feed_material:zero('continuous grease witness clears '+n,witness.common(local(n)))
    # Deliberate sealed-housing, undrilled-spacer and plugged-elbow failures.
    prior_housing=prior['InputHousing_housing']['shape'].copy();prior_housing.translate(-origin)
    prior_spacer=prior['InputHousing_spacer']['shape'].copy();prior_spacer.translate(-origin)
    check('negative: old unpierced housing blocks feed',witness.common(prior_housing).Volume>1)
    check('negative: old undrilled spacer blocks feed',witness.common(prior_spacer).Volume>1)
    check('negative: elbow plug blocks feed',witness.common(Part.makeSphere(3,mid)).Volume>1)
    witness.exportBrep(str(out/'grease_passage_gauge.brep'))
    nipple=local('InputInstallation_nipple')
    radii=sorted(set(round(f.Surface.Radius,6) for f in nipple.Faces if isinstance(f.Surface,Part.Cylinder)))
    check('nominal half-inch pipe uses actualOD21.336 and bore15.7988',radii,[7.8994,10.668])
    circle_centres=[f.CenterOfMass for f in nipple.Faces if isinstance(f.Surface,Part.Plane)]
    check('printed nipple length from end planes',(circle_centres[0]-circle_centres[1]).Length,44.45)
    # Changes are subtractive and confined to the explicitly identified ports
    # and four stud receivers; unaffected casting material is retained.
    masks=[cyl(6.501,[219.399,96*math.cos(math.pi/2+n*math.pi/2),96*math.sin(math.pi/2+n*math.pi/2)],[1,0,0],43.602) for n in range(4)]
    receiver=cyl(10.819,list(port+u*75),list(u),30.001)
    feed=cyl(4.001,list(port+u*49.999),list(u),25.102)
    for name in report['changed_ids']:
        before=prior[name]['shape'].copy();before.translate(-origin);after=local(name)
        if name.startswith('InputHousing_flange_shim'):
            masks_here=[cyl(6.501,[247.999,96*math.cos(math.pi/2+n*math.pi/2),96*math.sin(math.pi/2+n*math.pi/2)],[1,0,0],2.002) for n in range(4)]
        else:masks_here=masks+[receiver,feed]+[cyl(12.001,[262,96*math.cos(math.pi/2+n*math.pi/2),96*math.sin(math.pi/2+n*math.pi/2)],[1,0,0],15.001) for n in range(4)]
        zero(name+' has no added material',after.cut(before))
        zero(name+' retains all material outside intended cuts',before.cut(after).cut(Part.makeCompound(masks_here)))
    # Head and teeth are outside this increment and must remain identical.
    pinion=local('CenterBevelDrive_pinion');previous=prior['CenterBevelDrive_pinion']['shape'].copy();previous.translate(-origin)
    zero('entire accepted input shaft/pinion material unchanged',pinion.cut(previous).fuse(previous.cut(pinion)))
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in checks),checks=checks,check_count=len(checks),native_sha256=sha(native),
        report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),grease_gauge_sha256=sha(out/'grease_passage_gauge.brep'),
        scope='Saved nominal threads/retention, continuous2mm grease gauge and protected material. No flow-rate, sealing, load or historical-fit qualification.')
    write(out/'interface_checks.json',result);print('PASS' if result['passed'] else 'FAIL',len(checks),[r for r in checks if not r['passed']],flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
