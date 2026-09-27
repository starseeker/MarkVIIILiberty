"""Freeze complete front clutch chain with declared foundation revisions and open driver mechanisms."""
import argparse,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256'];assert not (out/'qualification.json').exists()
checks={};counts={}
for name in ['independent_checks.json','definition_preservation_checks.json','reproduction_checks.json']:
    q=read(out/name);assert q['passed'] and q['native_sha256']==sha(native);checks[name]=sha(out/name)
assert read(out/'visual_review.json')['disposition']=='reviewed_local_approximation'
prototype,variation=ROOT/r['prototype'],ROOT/r['variation']
for folder in [prototype,variation]:
    pr=read(folder/'report.json');assert sha(folder/pr['native_file'])==pr['native_sha256'];counts[folder.name]={}
    for name,key in [('checks03/independent_checks.json','checks'),('context_audit/report.json','pairs'),('exchange01/exchange_checks.json','checks')]:
        q=read(folder/name);assert q['passed'] and q['native_sha256']==pr['native_sha256'];counts[folder.name][name]=len(q[key])
assert read(prototype/'reproduction_checks.json')['passed']
source=ROOT/r['details']['controls']['source_review'];source_data=read(source)
modules=[H/(name+'.py') for name in ['driver_control_mount_parts','driver_control_linkage_parts_v3','driver_low_control_parts_v2','trial_driver_low_controls_v2',
    'check_driver_foundation_interfaces','check_driver_low_controls_v2','render_driver_low_controls','build_driver_low_controls',
    'check_driver_low_control_installation','check_driver_low_control_preservation','transfer_driver_low_control_views','qualify_driver_low_controls',
    'control_rebuild_io','control_rebuild_io_v2','check_control_rebuild_context','exchange_control_rebuild_clutch_swing',
    'check_control_rebuild_reproduction','check_powertrain_frame_reproduction',
    'pump_integration_worker','verify_control_rebuild_checkpoint','control_rebuild_surface_mass_v3','control_rebuild_surface_mass_v5']]
modules += [H/'control_rebuild_surface_mass_v3.cpp',H/'control_rebuild_surface_mass_v5.cpp']
modules += [H.parents[1]/'lib'/(name+'.py') for name in ['evidence','cad_build','mass_properties','kronrod_mass','camera_review','source_camera','visual_review','step_matching','runtime','raster']]
modules += [H.parents[1]/'lib'/name for name in ['occt_mass_properties.cpp','occt_kronrod_mass.cpp','raster.c']]
modules += [ROOT/'skills/freecad-reconstruction/scripts/freecad_headless.py']
frozen=out/'frozen_validation';frozen.mkdir()
for file in modules:shutil.copy2(file,frozen/str(file.relative_to(ROOT)).replace('/','__'))
deps={}
def add(file,expected=None):
    file=Path(file);file=file if file.is_absolute() else ROOT/file;digest=sha(file);assert expected is None or digest==expected,str(file);deps[str(file.relative_to(ROOT))]=digest
for folder in [prototype,variation,out]:
    for file in sorted(folder.rglob('*')):
        if file.is_file() and not any(v.endswith('_runtime') or v in ['runtime','__pycache__'] for v in file.parts):add(file)
    for file,digest in read(folder/'report.json')['input_hashes'].items():add(file,digest)
    for entry in read(folder/'isolated/manifest.json')['definitions'].values():add(entry['brep_path'],entry['brep_sha256'])
for file in modules+[source,H/'transmission_controls_study/driver_redo01/low_checker_review01.json',H/'transmission_controls_study/driver_redo01/low_source_views01/hb113_joint_grid.png',H/'transmission_controls_study/driver_redo01/low_source_views01/receipt.json',H/'transmission_controls_study/redo01/diagnostics/trimmed_mass01/qualification.json']:add(file)
for file,digest in source_data['source_hashes'].items():add(file,digest)
standard=H/'transmission_brake_front_study/trial01/standard_context_manifest.json';add(standard)
# Reuse the parent checkpoint's byte-identical, durable standard context archive.
# The broad audit checked these hashes at their generated paths; no new geometry
# validation or duplicated native archive is needed for archival relocation.
parentq=read((ROOT/r['source_native']).parent/'qualification.json')
archives=[ROOT/file for file in parentq['dependencies'] if file.endswith('/standard_context_archive.json')]
assert len(archives)==1
archive=archives[0];add(archive)
mapping=read(archive)['native_files'];assert set(mapping)==set(read(standard)['native_files'])
for file,digest in read(standard)['native_files'].items():
    assert sha(ROOT/file)==digest==mapping[file]['sha256'];add(mapping[file]['archived_path'],digest)
progress=read(out/'progression_receipt.json')
for file,digest in (progress['prior']|progress['new']).items():add(file,digest)
write(out/'qualification.json',dict(local_static_checks_passed=True,native_sha256=sha(native),source_native_sha256=r['source_native_sha256'],parent_checkpoint=str((ROOT/r['source_native']).parent.relative_to(ROOT)),
    counts=dict(physical_occurrences=r['expected_physical_occurrences'],definitions=r['expected_definition_count'],assembly_groups=r['expected_assembly_count']),
    scope='30 additions: two each M760/M762/M763, full M761 pin/keeper and SH220A washer, complete source-length M574 rods with four physical clevis joints. Seven declared driver/floor/clutch definitions revised after source eye identities were separated. M762 front selector coupling, historical profiles/axial stack/pose, seat supports and other driver mechanisms remain unfinished',
    local_validation_counts=counts,geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,installation_qualified=False,packet_complete=False,source_camera_refitted=False,
    open_issues=source_data['approximations']+source_data['constraints'],checks=checks,dependencies=deps))
print('Frozen',len(deps),'dependencies; low-speed receiving chain statically checked.',flush=True)
