"""Independent saved-geometry witnesses and STEP exchange for the MX5 trial."""
import argparse,json,math,subprocess,sys
from pathlib import Path
from collections import Counter
REPO=next(p for p in Path(__file__).resolve().parents if (p/'cad/003_FullTank').is_dir());STAGE=REPO/'cad/003_FullTank';ROOT=STAGE/'experiments/drive_chains'
p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--candidate',type=Path,default=ROOT/'transmission_case_mount_trial_build')
a=p.parse_args();out=a.candidate.resolve();sys.path[:0]=[str(STAGE),str(ROOT)]
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'check_run.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker','--candidate',str(out)],env=runtime.environment(out/'check_runtime'),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from case_joint_mass import calculator
    r=read(out/'report.json');native=out/'MX5CaseMountTrial.FCStd';assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));doc.recompute();items={i['id']:i for i in leaves(doc.Root)}
    origin=doc.TransmissionCore.Placement.Base;shapes={n:i['shape'].copy() for n,i in items.items()}
    for s in shapes.values():s.translate(-origin)
    checks=[]
    def check(n,v,e=True,tol=1e-5):checks.append(dict(name=n,value=v,expected=e,passed=abs(v-e)<tol if isinstance(e,float) else v==e))
    def zero(n,s):check(n,s.Volume,0.0)
    def cx(rad,a,b,y,z):return Part.makeCylinder(rad,b-a,App.Vector(a,y,z),App.Vector(1,0,0))
    def box(a,b,y0,y1,z0,z1):return Part.makeBox(b-a,y1-y0,z1-z0,App.Vector(a,y0,z0))
    def shifted(s,delta):t=s.copy();t.translate(App.Vector(*delta));return t
    check('physical leaf count',len(items),1407)
    check('four source-owned copies of each fastener part',dict(Counter(pid for n in r['new_ids'] for pid in json.loads(items[n]['target'].SurveyIds))),
        {'P_c5b4d785b6867abb':4,'P_c3bb5fc9299bfab2':4,'P_715e37e46e3ce9b8':4,'P_6e5a15454080a055':4})
    case=shapes['CenterTransmissionCore_bevel_case'];addition_masks=[];hole_masks=[]
    tip=-265.3735714285713;end=tip+142.875;seat=-243.1485714285713;pinx=-258.6985714285713
    for label,sgn,base,member in [('Upper',1,318.63631878624517,'Top'),('Lower',-1,-262.33445920236954,'Bottom')]:
        channel=shapes['TransmissionFrame_'+member+'Channel']
        for side,y in [('Port',118),('Starboard',-118)]:
            name='CaseMount_'+label+side;z=base+sgn*25
            stud,nut,pin,washer=[shapes[name+'_'+k] for k in ['stud','nut','cotter','washer']]
            check(name+' detailed source stud length',stud.BoundBox.XLength,142.875)
            check(name+' nominal source diameter',stud.BoundBox.ZLength,19.05)
            zero(name+' receiver clear throughout printed US span',cx(9.525,end-38.1,end,y,z).common(case))
            wall=cx(13,end-37,end-1,y,z).cut(cx(9.8,end-38,end,y,z))
            zero(name+' continuous stock around embedded thread',wall.cut(case))
            check(name+' blind bore has closed end',case.isInside(App.Vector(end+1,y,z),1e-7,False))
            check(name+' advancing stud through blind clearance collides',shifted(stud,(.5,0,0)).common(case).Volume>1)
            check(name+' radial stud displacement collides with receiver',shifted(stud,(0,.5,0)).common(case).Volume>1)
            check(name+' nut uses existing shared definition',items[name+'_nut']['target']==items['PortFixedBearing_inner_Stud01_Nut']['target'])
            check(name+' nut lies inside printed SAE span',nut.BoundBox.XMin>=tip and nut.BoundBox.XMax<=tip+28.575)
            check(name+' displaced nut catches formed cotter',shifted(nut,(-3,0,0)).common(pin).Volume>.01)
            rotated=nut.copy();rotated.rotate(App.Vector(pinx,y,z),App.Vector(1,0,0),10)
            check(name+' turned nut catches cotter',rotated.common(pin).Volume>.001)
            for sign in [-1,1]:
                witness=Part.makeCylinder(.73375,26.5,App.Vector(pinx,y+13,z+sign*.84375),App.Vector(0,-1,0))
                zero(name+' intact straight pin leg '+str(sign),witness.cut(pin))
                endpoint=App.Vector(pinx,y-19.346653896957072,z+sign*4.861976772210879)
                check(name+' formed tail exists '+str(sign),pin.distToShape(Part.Vertex(endpoint))[0],0.0)
            check(name+' washer bears against channel',washer.distToShape(channel)[0],0.0)
            check(name+' washer carries nut face',washer.distToShape(nut)[0],0.0)
            check(name+' moving washer into flange collides',shifted(washer,(.3,0,0)).common(channel).Volume>1)
            wrong=washer.copy();wrong.rotate(App.Vector(seat,y,z),App.Vector(1,0,0),180)
            check(name+' reversing bevel orientation collides',wrong.common(channel).Volume>1)
            check(name+' nut clears nearest channel web',nut.distToShape(channel)[0],2.7125)
            addition_masks.append(cx(22.001,-227.149,end+4.601,y,z))
            hole_masks.append(cx(9.676,-228.15,end+.301,y,z))
    assert sha(out/'inputs/parent_case.brep')==r['parent_case_brep_sha256']
    previous=Part.Shape();previous.read(str(out/'inputs/parent_case.brep'))
    added=case.cut(previous);removed=previous.cut(case)
    zero('case additions confined to four inferred mounting bosses',added.cut(Part.makeCompound(addition_masks)))
    zero('case removals confined to four blind receivers',removed.cut(Part.makeCompound(hole_masks)))
    write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),checks=checks,
        native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
        case_added_mm3=added.Volume,case_removed_mm3=removed.Volume))
    print('Independent checks',len(checks),'failed',[v for v in checks if not v['passed']],flush=True)
    ids=r['new_ids']+r['changed_ids'];step=out/'MX5CaseMountParts.step'
    Part.makeCompound([items[n]['shape'] for n in ids]).exportStep(str(step));imported=Part.Shape();imported.read(str(step))
    assert imported.isValid() and len(imported.Solids)==len(ids)
    unmatched=list(imported.Solids);rows=[];mass=calculator(out/'check_runtime/mass')
    for name in ids:
        s=items[name]['shape'].Solids[0];idx=min(range(len(unmatched)),key=lambda i:(s.CenterOfMass-unmatched[i].CenterOfMass).Length);t=unmatched.pop(idx)
        ta,tb=s.getTolerance(1),t.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        raw_missing=s.cut(t).Volume;raw_added=t.cut(s).Volume;missing=s.cut(t,fuzzy);added=t.cut(s,fuzzy)
        mn,ms=mass(s,name+'_native'),mass(t,name+'_step');dv=abs(mn['volume_mm3']-ms['volume_mm3'])
        dc=(App.Vector(*mn['center_mm'])-App.Vector(*ms['center_mm'])).Length;bound=(s.Area+t.Area)/2*(ta+tb)
        passed=(s.isValid() and t.isValid() and raw_missing<1e-5 and raw_added<1e-5 and not missing.Faces and not added.Faces
            and ta<=1e-4 and tb<=max(1e-7,ta)+1e-10 and dv<=bound and dc<max(1e-6,ta+tb)
            and all(0<=m['estimated_relative_error']<1e-9 for m in [mn,ms]))
        rows.append(dict(id=name,passed=passed,native_tolerance_mm=ta,step_tolerance_mm=tb,raw_missing_mm3=raw_missing,
            raw_added_mm3=raw_added,missing_mm3=missing.Volume,added_mm3=added.Volume,native_mass=mn,step_mass=ms,
            volume_difference_mm3=dv,surface_tolerance_envelope_mm3=bound,center_difference_mm=dc))
        write(out/'exchange_progress.json',dict(completed=len(rows),failed=[x for x in rows if not x['passed']]))
    write(out/'exchange_checks.json',dict(passed=all(x['passed'] for x in rows),checks=rows,step_sha256=sha(step),native_sha256=sha(native),checker_sha256=sha(Path(__file__))))
    print('STEP checks',len(rows),'failed',[v for v in rows if not v['passed']],flush=True)
    sys.exit(0 if all(v['passed'] for v in checks+rows) else 1)
finally:runtime.close()
