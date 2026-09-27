"""Freeze the fully checked coupled driver station checkpoint and visual progression."""
import argparse,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');native=out/r['native_file'];assert sha(native)==r['native_sha256'];assert not (out/'qualification.json').exists()
checks={}
for name in ['independent_checks.json','definition_preservation_checks.json','guide_geometry_checks.json','reproduction_checks.json']:
    q=read(out/name);assert q['passed'] and q['native_sha256']==sha(native);checks[name]=sha(out/name)
visual=read(out/'visual01/visual_review.json');render=read(out/'visual01/render_receipt.json')
assert visual['disposition']=='reviewed_local_approximation' and visual['native_sha256']==render['native_sha256']==sha(native)
assert visual['inspected_images']==render['images'] and render['renderer_sha256']==sha(H/'render_coupled_driver_integration.py')
assert not render['source_camera_refitted']
for f,h in render['images'].items():assert sha(out/'visual01'/f)==h
parent=(ROOT/r['source_native']).parent;prior=read(parent/'progression_receipt.json');old=prior['prior']|prior['new'];new={}
for kind,file in [('iso','isometric.png'),('development','development.png'),('station','station_isometric.png'),('connections','station_connections.png'),('source_section','station_source_section.png'),('clutch_source','station_clutch_source_comparison.png')]:
    target=ROOT/f'cad/intermediate_snapshot_{kind}_coupled_driver_integrated_001.png';assert not target.exists();shutil.copy2(out/'visual01'/file,target);new[str(target.relative_to(ROOT))]=sha(target)
write(out/'progression_receipt.json',dict(prior=old,new=new,previous_count=len(old),new_count=len(new),total_count=len(old)+len(new),native_sha256=sha(native),render_receipt_sha256=sha(out/'visual01/render_receipt.json'),note='Two new full-union views; four local/source views retained by strict saved-material/frame transfer.'))
modules=[H/(n+'.py') for n in ['plan_coupled_driver_integration','integrate_coupled_driver_station','check_coupled_driver_integration','check_coupled_driver_integration_v2','check_coupled_inherited_guides','check_coupled_guide_geometry','render_coupled_driver_integration','qualify_coupled_driver_integration','pump_integration_worker','control_rebuild_io_v2','check_powertrain_frame_reproduction','verify_control_rebuild_checkpoint']]
modules+=[H.parents[1]/'lib'/(n+'.py') for n in ['evidence','cad_build','camera_review','visual_review','raster','runtime']]+[H.parents[1]/'lib/raster.c',ROOT/'skills/freecad-reconstruction/scripts/freecad_headless.py']
frozen=out/'frozen_validation';frozen.mkdir()
for f in modules:shutil.copy2(f,frozen/str(f.relative_to(ROOT)).replace('/','__'))
deps={}
def add(path,expected=None):
    path=Path(path);path=path if path.is_absolute() else ROOT/path;d=sha(path);assert expected is None or d==expected,str(path);deps[str(path.relative_to(ROOT))]=d
# Preserve both ancestral qualification chains, including the durable standard archive.
for file in [parent/'qualification.json',H/'driver_support_outline_study/study_receipt.json',H/'seat_adjustment_study/evidence_receipt.json']:
    add(file)
    for f,h in read(file)['dependencies'].items():add(f,h)
for file in out.parent.rglob('*'):
    if file.is_file() and not any(p.endswith('_runtime') or p in ['runtime','__pycache__'] for p in file.parts):add(file)
for f,h in r['input_hashes'].items():add(f,h)
for f in modules:add(f)
for f,h in (old|new).items():add(f,h)
for f,h in render['input_hashes'].items():add(f,h)
prototype=ROOT/r['prototype'];review=read(H/'driver_support_outline_study/source_review.json')
q=dict(local_static_checks_passed=True,native_sha256=sha(native),source_native_sha256=r['source_native_sha256'],parent_checkpoint=str(parent.relative_to(ROOT)),counts=dict(physical_occurrences=3712,definitions=689,assembly_groups=456),
    scope='Complete reviewed coupled station integrated into the retained hierarchy:92 new seat/support occurrences plus38 replacement bow panels,54 new definitions,17 revised definitions and226 changed world frames.618 unrelated definitions and all inherited hierarchy preserved.18 new nonphysical guides plus13 inherited curves retained. Standard tank011 itself unchanged.',
    local_validation_counts=dict(integration_checks=108,canonical_material_comparisons=743,strict_material_comparisons=55,guide_checks=31,transferred_context_pairs=1174,fresh_archive_breps=2135,fresh_persistent_properties=184974),
    geometry_integrated=True,standard_assembly_modified=False,historical_geometry_qualified=False,installation_qualified=False,packet_complete=False,source_camera_refitted=False,
    open_issues=['Absolute shaft identities/station and handle37in datum remain conditional.','M772 delayed-set mid-blade profile is clearance-derived, with19.87px fixed-plan deviation; no historical bend validation.','Seat curves, support outline/stock, hole patterns and floor-angle section remain approximations.','SH291C/D/F mounts and D/F installed quantities remain unresolved.','Driver foot/reverse controls, springs, stops and remaining connecting fittings are unfinished.','Full tank integration, motion, force and service-path qualification remain open.'],
    checks=checks,dependencies=deps)
write(out/'qualification.json',q);print('QUALIFIED',len(deps),'dependencies; progression',len(old)+len(new),flush=True)
