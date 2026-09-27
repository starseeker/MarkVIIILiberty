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
 for name in ['checks02/independent_checks.json','context_audit/report.json','exchange01/exchange_checks.json']:
  q=read(folder/name);assert q['passed'] and q['native_sha256']==report['native_sha256']
assert read(prototype/'reproduction_checks.json')['passed']
D=prototype.parent
modules=[H/(name+'.py') for name in ['control_rebuild_io_v2','control_rebuild_intermediate_parts',
 'trial_control_rebuild_intermediate_v2','check_control_rebuild_intermediate','check_control_rebuild_context',
 'exchange_control_rebuild_center_foot','check_control_rebuild_reproduction','render_control_rebuild_intermediate',
 'build_control_rebuild_intermediate','transfer_control_rebuild_intermediate_views','check_control_rebuild_intermediate_installation',
 'check_control_rebuild_intermediate_preservation','check_powertrain_frame_reproduction','pump_integration_worker',
 'qualify_control_rebuild_intermediate','verify_control_rebuild_checkpoint',
 'rear_control_channel_mount_parts','transmission_frame_joint_parts','transmission_input_installation_parts']]
modules += [H.parents[1]/'lib/occt_mass_properties.cpp']
modules += [H.parents[1]/'lib'/(name+'.py') for name in ['evidence','cad_build','mass_properties',
 'camera_review','source_camera','visual_review','step_matching','runtime']]
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
for file in modules+[D/'intermediate_controls01.json',D/'intermediate_variation01.json',D/'intermediate_source_review01.json',
                     H/'transmission_controls_study/channel_local_registration01.json']:add(file)
for folder in [prototype,variation,out]:
 for file,digest in read(folder/'report.json')['input_hashes'].items():add(file,digest)
 for entry in read(folder/'isolated/manifest.json')['definitions'].values():add(entry['brep_path'],entry['brep_sha256'])
for file,digest in read(D/'intermediate_source_review01.json')['source_hashes'].items():add(file,digest)
progression=read(out/'progression_receipt.json')
for file,digest in (progression['prior']|progression['new']).items():add(file,digest)
write(out/'qualification.json',dict(local_static_checks_passed=True,native_sha256=sha(native),
 source_native_sha256=r['source_native_sha256'],parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
 counts=dict(physical_occurrences=r['expected_physical_occurrences'],definitions=r['expected_definition_count'],assembly_groups=r['expected_assembly_count']),
 scope='M638 intermediate shaft, three M639 mounts, eight shared single-ended M640 rockers, two M3019 strips and complete cap-screw/keeper receiving stock. Nominal/variation saved-solid, context, STEP and full-native preservation checks passed. Shaft station derives from printed M574 length against provisional driver interfaces; mounting interpretation and exact sizes remain approximate.',
 geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,
 installation_qualified=False,packet_complete=False,source_camera_refitted=False,
 open_issues=read(D/'intermediate_source_review01.json')['approximations']+[
  'Eight assigned rear and front eyes await complete rods; connected operation is not qualified.',
  'Floor3 is a development-context copy with six mounting holes; its source piece mark and M3019 mounting interpretation are unproven.',
  'M575/M563, M573/M579, SH944/M581 and driver interfaces remain to be rebuilt.'],
 checks=checks,dependencies=dependencies))
print('Frozen',len(dependencies),'dependencies; intermediate shaft/receiver static checkpoint.',flush=True)
