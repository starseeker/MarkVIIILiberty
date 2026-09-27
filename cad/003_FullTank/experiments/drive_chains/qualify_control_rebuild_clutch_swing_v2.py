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
 for name in ['checks03/independent_checks.json','context_audit/report.json','exchange01/exchange_checks.json']:
  q=read(folder/name);assert q['passed'] and q['native_sha256']==report['native_sha256']
assert read(prototype/'reproduction_checks.json')['passed']
D=prototype.parent
modules=[H/(name+'.py') for name in ['control_rebuild_io_v2','trial_control_rebuild_clutch_swing_v7',
 'check_control_rebuild_clutch_swing_v3','check_control_rebuild_context','exchange_control_rebuild_clutch_swing',
 'check_control_rebuild_reproduction','render_control_rebuild_clutch_swing_v2','build_control_rebuild_clutch_swing_v2',
 'transfer_control_rebuild_clutch_swing_views','check_control_rebuild_clutch_swing_installation','check_control_rebuild_clutch_swing_preservation',
 'check_powertrain_frame_reproduction','pump_integration_worker','qualify_control_rebuild_clutch_swing_v2','verify_control_rebuild_checkpoint',
 'control_rebuild_surface_mass_v3','control_rebuild_surface_mass_v5','qualify_control_trimmed_mass']]
modules += [H/'control_rebuild_surface_mass_v3.cpp',H/'control_rebuild_surface_mass_v5.cpp']
modules += [H.parents[1]/'lib'/(name+'.py') for name in ['evidence','cad_build','mass_properties','kronrod_mass',
 'camera_review','source_camera','visual_review','step_matching','runtime']]
modules += [H.parents[1]/'lib/occt_mass_properties.cpp',H.parents[1]/'lib/occt_kronrod_mass.cpp']
frozen=out/'frozen_validation';frozen.mkdir()
for file in modules:shutil.copy2(file,frozen/str(file.relative_to(ROOT)).replace('/','__'))
dependencies={}
def add(file,expected=None):
 file=Path(file);file=file if file.is_absolute() else ROOT/file
 digest=sha(file);assert expected is None or digest==expected,str(file)
 dependencies[str(file.relative_to(ROOT))]=digest
for folder in [prototype,variation,out]:
 for file in sorted(folder.rglob('*')):
  if file.is_file() and not any(v.endswith('_runtime') or v in ['__pycache__','runtime'] for v in file.parts):add(file)
for file in modules+[D/'clutch_swing_controls08.json',D/'clutch_swing_variation05.json',D/'clutch_swing_source_review06.json',D/'diagnostics/trimmed_mass01/qualification.json',
                     H/'transmission_controls_study/channel_local_registration01.json']:add(file)
for folder in [prototype,variation,out]:
 for file,digest in read(folder/'report.json')['input_hashes'].items():add(file,digest)
 for entry in read(folder/'isolated/manifest.json')['definitions'].values():add(entry['brep_path'],entry['brep_sha256'])
for file,digest in read(D/'clutch_swing_source_review06.json')['source_hashes'].items():add(file,digest)
progression=read(out/'progression_receipt.json')
for file,digest in (progression['prior']|progression['new']).items():add(file,digest)
write(out/'qualification.json',dict(local_static_checks_passed=True,native_sha256=sha(native),
 source_native_sha256=r['source_native_sha256'],parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
 counts=dict(physical_occurrences=r['expected_physical_occurrences'],definitions=r['expected_definition_count'],assembly_groups=r['expected_assembly_count']),
 scope='SH944 short/long links, shaft, axial Woodruff keys, complete source-sized clamp/mount hardware, real floor receivers and M581 rear rod with distinct SH953E/M569C joint families, and complete93in SH229A center rod with M569C joints. Source center-rod stock length determines swing-bracket X. Nominal/variation, context, strict STEP and full-native preservation checks pass. Cast forms, mounting, key-size height and routing remain estimates.',
 geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,
 installation_qualified=False,packet_complete=False,source_camera_refitted=False,
 open_issues=read(D/'clutch_swing_source_review06.json')['limits']+read(D/'clutch_swing_source_review06.json')['approximations']+[
  'The exact modern/historical No15 segment height remains unverified; 10.31mm is an estimate. Quarter-inch thickness and one-inch diameter have modern corroboration only.',
  'SH229A selected from directly reviewed SNL192, superseding older HB M574 application. Printed93in interpreted as stock centerline length; fork engagement and bends remain estimates. Driver-control continuation and its front rods remain required.'],
 checks=checks,dependencies=dependencies))
print('Frozen',len(dependencies),'dependencies; complete rear/center clutch static checkpoint.',flush=True)
