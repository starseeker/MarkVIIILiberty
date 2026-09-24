"""Recheck five spring pairs in the immutable initial 142-pair exchange.

Preserve the 137 passing results byte for byte as JSON values, tied to the
unchanged native and STEP hashes. Recheck every geometric criterion for the
five springs, replacing only the failed whole-face mass integration method.
"""
import argparse,copy,math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
from lib.mass_properties import AdaptiveMass
from lib.partitioned_mass import PartitionedMass
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--method-controls',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');rows={v['name']:v for v in m['occurrences']}
diag=out/'diagnostics/spring_mass';initial_path=diag/'initial_exchange_checks.json';initial=read(initial_path)
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']==initial['native_sha256']
assert sha(diag/'initial_exchange_checker.py')==initial['checker_sha256']
assert all(sha(out/f)==digest for f,digest in initial['step_hashes'].items())
controls=read(a.method_controls);assert controls['passed'] and controls['provenance']['adapter_sha256']==sha(STAGE/'lib/partitioned_mass.py')
results=copy.deepcopy(initial['checks']);assert len(results)==142
failed=[v for v in results if not v['passed']]
assert {(v['scope'],v['name']) for v in failed}=={('Definitions','Def_BrakeFront_spring')}|{('Installation',hand+role+'BrakeAdjustingSpring') for hand in ['Port','Starboard'] for role in ['LowSpeed','Track']}
mass=AdaptiveMass(out/'spring_exchange_mass_runtime');partitioned=PartitionedMass(mass,out/'partitioned_mass_runtime')
rechecked=[];definition=m['definitions']['Def_BrakeFront_spring'];f=Path(definition['brep_path']);assert sha(f)==definition['brep_sha256']
base=Part.Shape();base.read(str(f));assert base.Placement.isIdentity()
for scope,expected_count in [('Definitions',10),('Installation',132)]:
    step=Part.Shape();step.read(str(out/('BrakeFront'+scope+'.step')))
    assert step.isValid() and len(step.Solids)==expected_count
    for record in results:
        if record['passed'] or record['scope']!=scope:continue
        name=record['name'];one=base.copy();frame=App.Placement() if scope=='Definitions' else App.Placement(App.Matrix(*rows[name]['frame']))
        one.Placement=frame;two=step.Solids[record['imported_solid_index']]
        ta,tb=one.getTolerance(1),two.getTolerance(1);missing,added=one.cut(two),two.cut(one)
        fuzzy=min(1e-4,max(1e-7,ta+tb));fm,fa=len(one.cut(two,fuzzy).Faces),len(two.cut(one,fuzzy).Faces)
        ma,mb=partitioned.measure(one,frame),partitioned.measure(two,frame)
        dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
        geometry=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1 and abs(missing.Volume)<1e-5 and abs(added.Volume)<1e-5 and not fm and not fa and ta<=1e-4 and tb<=max(ta,1e-7)+1e-10
        record.update(initial_whole_mass=dict(native=record['native_mass'],step=record['step_mass']),
            native_mass=ma,step_mass=mb,adaptive_centroid_error_mm=dc,missing_mm3=missing.Volume,added_mm3=added.Volume,
            fuzzy_missing_faces=fm,fuzzy_added_faces=fa,native_tolerance_mm=ta,step_tolerance_mm=tb,
            centroid_error_mm=(one.Solids[0].CenterOfMass-two.CenterOfMass).Length,
            passed=geometry and ma['converged'] and mb['converged'] and dc<1e-5)
        rechecked.append(dict(scope=scope,name=name,passed=record['passed']));print(rechecked[-1],flush=True)
        write(out/'spring_exchange_progress.json',dict(rechecked=rechecked,checks=results))
assert len(rechecked)==5
retained=[v for v in initial['checks'] if v['passed']]
assert [v for v in results if (v['scope'],v['name']) not in {(w['scope'],w['name']) for w in rechecked}]==retained
result=dict(initial,passed=all(v['passed'] for v in results),checks=results,checker_sha256=sha(Path(__file__)),
    initial_report_sha256=sha(initial_path),retained_passing_pairs=len(retained),rechecked_spring_pairs=rechecked,
    mass_provenance=mass.provenance,partitioned_mass_provenance=partitioned.provenance,method_controls_sha256=sha(a.method_controls),
    scope='All 142 unchanged native/STEP pairs: 137 initial strict passes retained; five springs fully rechecked using verified disjoint partitions with the original integration and material tolerances. Historical and service qualification remain false.')
write(out/'exchange_checks.json',result);assert result['passed']
