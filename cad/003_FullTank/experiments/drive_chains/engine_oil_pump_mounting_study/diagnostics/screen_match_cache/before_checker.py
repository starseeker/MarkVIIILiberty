"""Reuse completed strict comparisons only for exact geometry pairs at identity pose.

This does not accept merely valid STEP, a matching volume, or an unfinished
comparison. It combines the independently checked nonscreen coverage with eight
screen pairs, each identical to a completed strict definition comparison.
"""
import argparse,json,subprocess,sys,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve();ref=a.reference.resolve();work=out/'screen_reuse_runtime';work.mkdir(exist_ok=True)
if not a.worker:
    with (out/'screen_reuse.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--reference',str(ref),'--worker'],env=runtime.environment(work),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    I=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]
    def identity(placement):return list(placement.toMatrix().A)==I
    def unit_scale(link):return link.Scale==1. and list(link.ScaleVector)==[1.,1.,1.]
    def reusable(passed,one,two,expected_one,expected_two,at_identity):
        return passed is True and at_identity and one==expected_one and two==expected_two
    r=read(out/'report.json');old=read(ref/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256']
    assert sha(ref/old['native_file'])==old['native_sha256']
    original=ref/'inputs/check_engine_oil_pump_exchange.py'
    assert sha(original)==sha(HERE/'check_engine_oil_pump_exchange.py')
    assert all(sha(ref/'inputs'/name)==sha(HERE/name) for name in ['case_joint_mass.py','case_joint_mass.cpp'])
    subset=read(out/'exchange_nonscreen_checks.json');assert subset['passed'] and subset['native_sha256']==sha(native)
    assert all(row['passed'] is True for row in subset['checks'])
    assert subset['checker_sha256']==sha(HERE/'check_engine_oil_pump_exchange_nonscreen.py')
    assert all(sha(out/n)==digest for n,digest in subset['step_hashes'].items())
    keys=['upper_side_screen','upper_end_screen','lower_side_screen','lower_end_screen']
    progress=read(ref/'exchange_progress.json');completed={row['part']:row for row in progress if row['scope']=='Definitions' and row['part'] in keys}
    assert set(completed)==set(keys) and all(row['passed'] is True for row in completed.values())
    reference_parts=out/'screen_reference';reference_parts.mkdir(exist_ok=True);bindings={}
    for key in keys:
        for suffix in ['native','step']:
            source=ref/'exchange_runtime/mass'/('Definitions_'+key+'_'+suffix+'.brep')
            target=reference_parts/source.name
            if target.exists():assert sha(target)==sha(source)
            else:shutil.copy2(source,target)
        bindings[key]=dict(check=completed[key],native_brep_sha256=sha(reference_parts/('Definitions_'+key+'_native.brep')),step_brep_sha256=sha(reference_parts/('Definitions_'+key+'_step.brep')))
    source_evidence=dict(source_native_sha256=sha(ref/old['native_file']),source_definitions_step_sha256=sha(ref/'OilPumpDefinitions.step'),strict_checker_sha256=sha(original),mass_helper_hashes={name:sha(HERE/name) for name in ['case_joint_mass.py','case_joint_mass.cpp']},completed_definition_comparisons=bindings,source_whole_exchange_complete=(ref/'exchange_checks.json').exists() and read(ref/'exchange_checks.json')['passed'])
    write(reference_parts/'completed_comparisons.json',source_evidence)
    doc=App.openDocument(str(native));checks=[];negative=[]
    for scope,filename in [('Definitions','OilPumpDefinitions.step'),('Assembly','OilPumpAssembly.step')]:
        loaded=Part.Shape();loaded.read(str(out/filename));expected_count=r['definition_count'] if scope=='Definitions' else r['physical_count']
        assert loaded.isValid() and len(loaded.Solids)==expected_count
        available=list(loaded.Solids)
        for key in keys:
            definition=doc.getObject('Def_'+key);shape=definition.Shape
            assert identity(definition.Placement) and identity(shape.Placement)
            name=key;pose_ok=True
            if scope=='Assembly':
                rows=[row for row in r['occurrences'] if row['key']==key];assert len(rows)==1
                row=rows[0];name=row['name'];link=doc.getObject(name);parent=doc.getObject(row['assembly'])
                assert link.LinkedObject==definition and link in parent.Group
                assert unit_scale(link),name+' has an unsupported link scale'
                pose_ok=identity(parent.getGlobalPlacement().multiply(link.LinkPlacement))
                # Only exact identity placements can use the saved definition
                # directly. Avoid a needless OCC copy, which changes BRep flags.
                assert pose_ok
            one=shape.Solids[0];center=one.CenterOfMass
            idx=min(range(len(available)),key=lambda i:(available[i].CenterOfMass-center).Length+abs(available[i].Volume-one.Volume)/max(one.Area,1));two=available.pop(idx)
            n=work/(scope+'_'+key+'_native.brep');s=work/(scope+'_'+key+'_step.brep');one.exportBrep(str(n));two.exportBrep(str(s))
            nh,sh=sha(n),sha(s);b=bindings[key]
            passed=reusable(b['check']['passed'],nh,sh,b['native_brep_sha256'],b['step_brep_sha256'],pose_ok)
            checks.append(dict(scope=scope,part=name,definition_key=key,passed=passed,method='Exact serialized native/STEP pair with verified identity placement and unit scale; reuse completed strict comparison',native_brep_sha256=nh,step_brep_sha256=sh,reference_key=key))
            write(out/'screen_reuse_progress.json',checks);print(scope,key,passed,flush=True)
            if scope=='Definitions' and key=='upper_side_screen':
                changed=one.copy();changed.translate(App.Vector(.01,0,0));changed.exportBrep(str(work/'negative_native.brep'))
                shifted=two.copy();shifted.translate(App.Vector(.01,0,0));shifted.exportBrep(str(work/'negative_step.brep'))
                negative=[not reusable(True,sha(work/'negative_native.brep'),sh,b['native_brep_sha256'],b['step_brep_sha256'],True),
                    not reusable(True,nh,sha(work/'negative_step.brep'),b['native_brep_sha256'],b['step_brep_sha256'],True),
                    not reusable(False,nh,sh,b['native_brep_sha256'],b['step_brep_sha256'],True),
                    not reusable(True,nh,sh,b['native_brep_sha256'],b['step_brep_sha256'],False)]
    expected={('Definitions',k) for k in r['definition_order']}|{('Assembly',row['name']) for row in r['occurrences']}
    direct={(row['scope'],row['part']) for row in subset['checks']};reused={(row['scope'],row['part']) for row in checks}
    deferred={(row['scope'],row['part']) for row in subset['deferred']}
    coverage=not direct.intersection(reused) and direct|reused==expected and reused==deferred and len(direct)==len(subset['checks']) and len(reused)==len(checks)
    accepted=all(row['passed'] for row in checks) and all(negative) and coverage
    report=dict(passed=accepted,complete_exchange=accepted,native_sha256=sha(native),step_hashes=subset['step_hashes'],checker_sha256=sha(Path(__file__)),nonscreen_report_sha256=sha(out/'exchange_nonscreen_checks.json'),source_evidence=source_evidence,direct_comparisons=len(direct),reused_comparisons=len(reused),total_comparisons=len(expected),coverage_complete=coverage,negative_controls=dict(changed_native_rejected=negative[0],changed_step_rejected=negative[1],unpassed_source_rejected=negative[2],nonidentity_pose_rejected=negative[3]),checks=subset['checks']+checks,freecad=App.Version(),occ=Part.OCC_VERSION)
    write(out/'exchange_checks.json',report);assert accepted
finally:
    runtime.close()
