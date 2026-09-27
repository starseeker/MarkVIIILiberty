"""Freeze an additive control checkpoint and retain its historical limitations."""
import argparse
from pathlib import Path
import shutil
import sys
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file']
assert not (out/'qualification.json').exists()
assert sha(native)==r['native_sha256']
checks={}
for name in ['independent_checks.json','definition_preservation_checks.json','reproduction_checks.json']:
 q=read(out/name);assert q['passed'] and q['native_sha256']==sha(native);checks[name]=sha(out/name)
assert read(out/'visual_review.json')['disposition']=='reviewed_local_approximation'
prototype,variation=ROOT/r['prototype'],ROOT/r['variation']
for folder in [prototype,variation]:
 report=read(folder/'report.json');assert sha(folder/report['native_file'])==report['native_sha256']
 for name in ['checks02/independent_checks.json','context_audit/report.json','exchange05/exchange_checks.json']:
  q=read(folder/name);assert q['passed'] and q['native_sha256']==report['native_sha256']
assert read(prototype/'reproduction_checks.json')['passed']
D=prototype.parent
mass_receipt=D/'diagnostics/surface_mass02/qualification.json'
assert read(mass_receipt)['passed']
assert read(D/'diagnostics/surface_mass04/qualification.json')['passed']
modules=[H/(name+'.py') for name in ['control_rebuild_io','control_rebuild_spring_parts_v3',
 'trial_control_rebuild_springs_v3','control_rebuild_surface_mass','control_rebuild_surface_mass_v3','control_rebuild_wire_measure',
 'qualify_control_surface_mass','qualify_control_surface_mass_v3','check_control_rebuild_springs','check_control_rebuild_context',
 'exchange_control_rebuild_v5','check_control_rebuild_reproduction','render_control_rebuild_springs',
 'build_control_rebuild_additions','transfer_control_rebuild_views','check_control_rebuild_installation','check_control_rebuild_preservation',
 'check_powertrain_frame_reproduction','pump_integration_worker','qualify_control_rebuild_additions',
 'verify_control_rebuild_checkpoint']]
modules += [H/'control_rebuild_surface_mass.cpp',H/'control_rebuild_surface_mass_v3.cpp']
modules += [H.parents[1]/'lib'/(name+'.py') for name in ['evidence','cad_build','mass_properties',
 'camera_review','source_camera','visual_review','step_matching','runtime']]
frozen=out/'frozen_validation';frozen.mkdir()
for file in modules:shutil.copy2(file,frozen/str(file.relative_to(ROOT)).replace('/','__'))
dependencies={}
def add(file,expected=None):
 file=Path(file);file=file if file.is_absolute() else ROOT/file
 digest=sha(file);assert expected is None or digest==expected,str(file)
 dependencies[str(file.relative_to(ROOT))]=digest
for folder in [prototype,variation,out,D/'diagnostics/surface_mass02',D/'diagnostics/surface_mass04']:
 for file in sorted(folder.rglob('*')):
  if file.is_file() and not any(v.endswith('_runtime') or v in ['__pycache__','runtime'] for v in file.parts):add(file)
for file in modules+[D/'spring_controls01.json',D/'spring_variation01.json',D/'spring_source_review.json',
                     H/'transmission_controls_study/channel_local_registration01.json']:add(file)
for folder in [prototype,variation,out]:
 for file,digest in read(folder/'report.json')['input_hashes'].items():add(file,digest)
 for entry in read(folder/'isolated/manifest.json')['definitions'].values():add(entry['brep_path'],entry['brep_sha256'])
for file,digest in read(D/'spring_source_review.json')['source_hashes'].items():add(file,digest)
progression=read(out/'progression_receipt.json')
for file,digest in (progression['prior']|progression['new']).items():add(file,digest)
write(out/'qualification.json',dict(local_static_checks_passed=True,native_sha256=sha(native),
 source_native_sha256=r['source_native_sha256'],parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
 counts=dict(physical_occurrences=r['expected_physical_occurrences'],definitions=r['expected_definition_count'],assembly_groups=r['expected_assembly_count']),
 scope='Four M564 return-spring installed states and eight compressed M567 washers. Explicit estimated attachment to fork sockets/jam nuts and M4136 bracket holes; complete wire stock, capture, nominal/variation material context, strict STEP exchange and additive full-native preservation checked. Historical shape and operating motion remain unqualified.',
 geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,
 installation_qualified=False,packet_complete=False,source_camera_refitted=False,
 open_issues=read(D/'spring_source_review.json')['approximations']+[
  'Fixed SNL6 registration retains inherited operating-lever/profile and spring-height discrepancies; reconstructed spring contours are not proven source geometry.',
  'M575/M563 complete routes and seats, center/forward rods, shaft supports and clutch/front controls remain to be rebuilt from withheld Gemini work.',
  'Native spring material is retained. Installed STEP export uses a rigidly transformed temporary copy to avoid a located-export kernel defect.'],
 checks=checks,dependencies=dependencies))
print('Frozen',len(dependencies),'dependencies; additive spring/washer static checkpoint.',flush=True)
