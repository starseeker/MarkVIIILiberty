"""Recheck all saved STEP mass properties with converged adaptive integration.

Reuse completed, hash-bound strict material comparisons from the initial export;
the initial default-centroid failure remains evidence, not an accepted result.
"""
import argparse
import math
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
from lib.mass_properties import AdaptiveMass
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json');base=read(out/'exchange_checks.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']==base['native_sha256']
assert base['checker_sha256']==sha(HERE/'exchange_transmission_brake_bands.py')
assert all(sha(out/f)==v for f,v in base['step_hashes'].items())
assert len(base['checks'])==259 and base['export_settings']=={'write.surfacecurve.mode':1}
rows={v['name']:v for v in m['occurrences']}
expected={('Definitions',name) for name in r['new_definitions']+r['changed_definitions']}|{('Installation',name) for name in r['affected_occurrences']}
assert {(v['scope'],v['name']) for v in base['checks']}==expected
import FreeCAD as App
import Part
mass=AdaptiveMass(out/'adaptive_mass_runtime');definitions={};imports={};results=[]
for name in r['new_definitions']+r['changed_definitions']:
    record=m['definitions'][name];path=Path(record['brep_path']);assert sha(path)==record['brep_sha256']
    s=Part.Shape();s.read(str(path));definitions[name]=s
for scope,count in [('Definitions',7),('Installation',252)]:
    s=Part.Shape();s.read(str(out/('BrakeBands'+scope+'.step')))
    assert s.isValid() and len(s.Solids)==count;imports[scope]=s.Solids
for row in base['checks']:
    name=row['name'];scope=row['scope']
    if scope=='Definitions':one=definitions[name].copy()
    else:
        pose=rows[name];one=definitions[pose['definition']].copy();one.Placement=App.Placement(App.Matrix(*pose['frame']))
    two=imports[scope][row['imported_solid_index']]
    # Check all original non-mass acceptance predicates, tied to unchanged
    # native/STEP bytes. Do not turn an unexplained material failure green.
    material_pass=abs(row['missing_mm3'])<1e-5 and abs(row['added_mm3'])<1e-5 and not row['fuzzy_missing_faces'] and not row['fuzzy_added_faces']
    tolerance_pass=row['native_tolerance_mm']<=1e-4 and row['step_tolerance_mm']<=max(row['native_tolerance_mm'],1e-7)+1e-10
    valid=one.isValid() and two.isValid() and len(one.Solids)==len(two.Solids)==1
    assert abs(one.getTolerance(1)-row['native_tolerance_mm'])<1e-12
    assert abs(two.getTolerance(1)-row['step_tolerance_mm'])<1e-12
    default_error=(one.Solids[0].CenterOfMass-two.CenterOfMass).Length
    assert abs(default_error-row['centroid_error_mm'])<1e-9
    ma,mb=mass.measure(one),mass.measure(two)
    dv=abs(ma['volume_mm3']-mb['volume_mm3']);dc=math.dist(ma['centroid_mm'],mb['centroid_mm'])
    result=dict(scope=scope,name=name,imported_solid_index=row['imported_solid_index'],
        default_centroid_error_mm=default_error,adaptive_centroid_error_mm=dc,adaptive_volume_error_mm3=dv,
        adaptive_volume_relative_difference=dv/ma['volume_mm3'],
        native_mass=ma,step_mass=mb,material_pass=material_pass,tolerance_pass=tolerance_pass,
        # Retain the original export criteria: centroid plus strict missing/
        # added material, topology and tolerances. Net integrated volume is a
        # diagnostic, not a substitute for either material difference. An
        # added absolute net-volume gate rejected large drums at 2e-11 relative
        # difference; that failed diagnostic and centered replay are retained.
        passed=material_pass and tolerance_pass and valid and ma['converged'] and mb['converged'] and dc<1e-5)
    results.append(result);write(out/'adaptive_exchange_progress.json',results)
    print(scope,name,result['passed'],dv,dc,flush=True)
result=dict(passed=all(v['passed'] for v in results),native_sha256=r['native_sha256'],step_hashes=base['step_hashes'],
    checker_sha256=sha(Path(__file__)),mass_provenance=mass.provenance,checks=results,
    material_check_report_sha256=sha(out/'exchange_checks.json'),material_checker_sha256=base['checker_sha256'],
    acceptance=dict(missing_material_mm3=1e-5,added_material_mm3=1e-5,centroid_error_mm=1e-5,
        empty_fuzzy_material_differences_required=True,unchanged_kernel_tolerance_required=True,
        converged_mass_integration_required=True,net_integrated_volume_difference='recorded diagnostic; not an acceptance predicate'),
    scope='All seven changed/new definitions and all 252 affected installed components; strict material/tolerance criteria retained, converged adaptive mass properties added.',
    installation_qualified=False,historical_geometry_qualified=False)
write(out/'exchange_adaptive_checks.json',result)
assert result['passed']
