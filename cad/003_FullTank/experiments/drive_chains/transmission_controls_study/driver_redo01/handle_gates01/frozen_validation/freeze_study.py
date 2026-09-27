from pathlib import Path
import json,hashlib,shutil
root=Path.cwd();h=root/'cad/003_FullTank/experiments/drive_chains';f=h/'transmission_controls_study/driver_redo01';out=f/'handle_gates01';var=f/'handle_gate_variation01';rep=f/'handle_gate_reproduction01'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):
 assert not p.exists(),p
 p.write_text(json.dumps(d,indent=2)+'\n')
r=read(out/'report.json');render=read(out/'render_receipt.json')
assert render['native_sha256']==r['native_sha256']==sha(out/r['native_file'])
visual=dict(disposition='conditional_interface_study',reviewer='Codex',date='2026-09-27',native_sha256=r['native_sha256'],render_receipt_sha256=sha(out/'render_receipt.json'),images=render['images'],source_camera_refitted=False,findings=[
'All six final images inspected. Four short radial passages replace the provisional radial lips in this isolated pilot; the source figure motivates tangential actuation, but complete operating handles are still required to confirm engagement and form.',
'Gate-interface diagnostic displays the proposed jaw upper left and inherited jaw lower right. Orange solids are nonphysical through-stem tools. The original diagnostic looked at the backs; that image and renderer are retained in handle_gate_diagnostics01/back_view.',
'All lower geometry, rods, existing bores and world frames are preserved. Native bores retain the13.5251px high-eye discrepancy. Neither fixed source registration is changed.',
'Actual M746/M747 fulcrums, M738A/B handles and M776/M768 pivot joints are unbuilt. Remaining controls, exact jaw dimensions and historical installation stay open. No new tank occurrence is counted.'])
write(out/'visual_review.json',visual)
modules=[h/(n+'.py') for n in ['driver_handle_gate_parts','trial_driver_handle_gates','check_driver_handle_gates','render_driver_handle_gates','verify_driver_handle_gate_study','driver_control_linkage_parts_v3','driver_low_selector_parts','control_rebuild_io_v2','check_control_rebuild_context','exchange_control_rebuild_clutch_swing','check_control_rebuild_reproduction','pump_integration_worker']]
frozen=out/'frozen_validation';frozen.mkdir()
for file in modules:shutil.copy2(file,frozen/file.name)
shutil.copy2(Path(__file__),frozen/'freeze_study.py')
parent=(root/r['parent_native']).parent;parentq=parent/'qualification.json';deps=read(parentq)['dependencies'].copy()
def add(p,expected=None):
 p=Path(p);p=p if p.is_absolute() else root/p;digest=sha(p)
 assert expected is None or digest==expected,p
 deps[str(p.relative_to(root))]=digest
add(parentq)
for folder in [out,var,rep,f/'handle_source_views01',f/'handle_gate_diagnostics01']:
 for file in sorted(folder.rglob('*')):
  if file.is_file() and not any(s in ['runtime','__pycache__'] or s.endswith('_runtime') for s in file.parts):add(file)
for folder in [out,var,rep]:
 report=read(folder/'report.json')
 for file,digest in report['input_hashes'].items():add(file,digest)
for folder in [out,var]:
 report=read(folder/'report.json')
 for file in ['checks03/independent_checks.json','context_audit/report.json','exchange01/exchange_checks.json']:
  q=read(folder/file);assert q['passed'] and q['native_sha256']==report['native_sha256']
assert read(out/'reproduction_checks.json')['passed']
for file in modules:add(file)
for file,digest in read(f/'handle_source_review01.json')['source_hashes'].items():add(file,digest)
write(out/'study_receipt.json',dict(local_interface_checks_passed=True,native_sha256=r['native_sha256'],geometry_integrated=False,historical_geometry_qualified=False,handle_engagement_qualified=False,prototype_occurrences=140,new_tank_occurrences=0,changed_definitions=r['changed_definitions'],variation=str(var.relative_to(root)),reproduction=str(rep.relative_to(root)),parent_qualification=str(parentq.relative_to(root)),scope='Conditional four-jaw upper-geometry study. Nominal and wall variation each pass252 local,20 context and8 STEP checks; fresh rebuilding and six inspected images. Diagnostic stems are not handles or tank parts. Complete operating-handle geometry must confirm or revise this proposal before integration.',dependencies=deps))
print('Frozen conditional interface study;',len(deps),'dependencies.')
