"""Rebuild casing dependencies from source controls, verifying the original before changing route."""
import argparse
import copy
from pathlib import Path
import shutil
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
STAGE=HERE.parents[1]
ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,required=True)
p.add_argument('--standard-context',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
parent,out=a.source.resolve(),a.output.resolve()
out.mkdir(parents=True,exist_ok=True)
native=out/'PowertrainWithRebuiltChainCasings.FCStd'
assert not native.exists(),'Use a fresh output directory.'
pr=read(parent/'report.json'); source=parent/pr['native_file']
assert sha(source)==pr['native_sha256']
pc=read(parent/'independent_checks.json')
assert pc['local_frame_checks_passed'] and pc['native_sha256']==sha(source)
m=read(parent/'isolated/manifest.json'); assert m['native_sha256']==sha(source)
rows={v['name']:v for v in m['occurrences']}
standard_path=a.standard_context.resolve()/'manifest.json'
standard=read(standard_path)
assert all(sha(ROOT/f)==digest for f,digest in standard['native_files'].items())
controls_paths={
    'casing':HERE/'casing_front_build/inputs/casing_controls.json',
    'mount':HERE/'casing_mount_controls.json',
    'cap':HERE/'casing_cap_packing_build/inputs/casing_cap_controls.json',
    'trim':HERE/'casing_trim_build/inputs/casing_trim_controls.json',
    'support':HERE/'casing_support_build/inputs/casing_support_controls.json',
    'front':HERE/'casing_front_build/inputs/casing_front_controls.json'}
controls={key:{k:v['value'] for k,v in read(path)['controls'].items()}
          for key,path in controls_paths.items()}
paths=[Path(__file__),HERE/'powertrain_casing_registration_parts.py',parent/'report.json',
       parent/'independent_checks.json',HERE/'installed_pitch_route_report.json',
       HERE/'casing_support_build/report.json',HERE/'chain_candidate_controls.json',
       HERE/'casing_shell_passage_build/report.json']+list(controls_paths.values())
paths += [HERE/name for name in ['casing_parts.py','casing_mount_parts.py','casing_cap_parts.py',
                               'casing_trim_parts.py','casing_front_parts.py']]
locked={str(f.relative_to(ROOT)):sha(f) for f in paths}
original_route=read(HERE/'installed_pitch_route_report.json')
route=copy.deepcopy(original_route)
route['candidate_transmission_axis_xz_mm']=[pr['shaft_axis_mm'][i] for i in [0,2]]
support_joints=read(HERE/'casing_support_build/report.json')['joints']
small_hub=read(HERE/'chain_candidate_controls.json')['controls']['small_hub_radius']['value']
centers={hand:rows[hand+'Chain_RollerPinion']['frame'][7] for hand in ['Port','Starboard']}

import FreeCAD as App
import Part
from powertrain_casing_registration_parts import reconstruct

wallrow=next(v for v in standard['occurrences'] if v['name']=='hull_engine_back')
wd=standard['definitions'][wallrow['definition']]
assert sha(Path(wd['brep_path']))==wd['brep_sha256']
wall=Part.Shape();wall.read(wd['brep_path'])
wall.Placement=App.Placement(App.Matrix(*wallrow['frame']))
assert wall.Placement.isIdentity()
baselines=out/'baseline_shapes'; baselines.mkdir(exist_ok=True)
wall.exportBrep(str(baselines/'standard_bulkhead.brep'))
baseline_checks=[]
def saved(name):
    d=m['definitions'][name]; f=Path(d['brep_path']); assert sha(f)==d['brep_sha256']
    s=Part.Shape();s.read(str(f));return s
print('Reconstructing existing casing dependencies before changing route',flush=True)
old_shapes,old_poses,old_trim,old_details=reconstruct(controls,original_route,wall,centers,support_joints,85,small_hub)
for name,shape in old_shapes.items():
    original=saved(name)
    missing,added=original.cut(shape).Volume,shape.cut(original).Volume
    rec=dict(definition=name,missing_mm3=missing,added_mm3=added,
             passed=abs(missing)<1e-5 and abs(added)<1e-5)
    baseline_checks.append(rec)
    shape.exportBrep(str(baselines/(name+'_regenerated_original.brep')))
    write(out/'baseline_progress.json',baseline_checks)
    print('Baseline',name,rec,flush=True)
assert all(v['passed'] for v in baseline_checks),'Original reconstruction must preserve every saved feature.'
for name,pose in old_poses.items():
    assert max(abs(x-y) for x,y in zip(pose.toMatrix().A,rows[name]['frame']))<1e-7,name
for name,part in old_trim.items():
    original=saved(rows['PortCasingTrim_'+name]['definition'])
    assert abs(original.cut(part['shape']).Volume)<1e-5 and abs(part['shape'].cut(original).Volume)<1e-5,name
print('Reconstructing casings and joints at revised route',flush=True)
new_shapes,new_poses,new_trim,new_details=reconstruct(controls,route,wall,centers,support_joints,85,small_hub)
for name,part in new_trim.items():
    original=old_trim[name]['shape']
    assert abs(original.cut(part['shape']).Volume)<1e-5 and abs(part['shape'].cut(original).Volume)<1e-5,name
doc=App.openDocument(str(source))
for name,shape in new_shapes.items():
    obj=doc.getObject(name)
    (obj.Tip if obj.TypeId=='PartDesign::Body' else obj).Shape=shape
for name,pose in new_poses.items():
    row=rows[name]; obj=doc.getObject(row['object'])
    owner=doc.getObject(row['owners'][-1])
    obj.LinkPlacement=owner.getGlobalPlacement().inverse().multiply(pose)
doc.Root.Label='Powertrain trial — regenerated chain casing dependencies'
doc.Root.RegistrationStatus='Casings and dependent joints regenerated; independent local/source/installation review required'
doc.recompute();doc.saveAs(str(native));App.closeDocument(doc.Name)
assert sha(source)==pr['native_sha256']
assert all(sha(ROOT/f)==digest for f,digest in locked.items())
frozen=out/'frozen_inputs';frozen.mkdir()
for f in paths:
    key=str(f.relative_to(ROOT)).replace('/','__')
    shutil.copy2(f,frozen/key)
replaced=set(new_shapes)
affected=sorted({n for n,row in rows.items() if row['definition'] in replaced}|set(new_poses))
write(out/'report.json',dict(status='saved_casing_reconstruction_pending_independent_checks',
    native_file=native.name,native_sha256=sha(native),source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source),input_hashes=locked,controls=controls,
    original_route=original_route,revised_route=route,centers=centers,
    big_hub_radius_mm=85,small_hub_radius_mm=small_hub,support_joints=support_joints,
    standard_native_files=standard['native_files'],standard_manifest_sha256=sha(standard_path),
    baseline_checks=baseline_checks,baseline_brep_hashes={f.name:sha(f) for f in baselines.glob('*.brep')},
    original_details=old_details,revised_details=new_details,replaced_definitions=sorted(replaced),
    expected_occurrence_frames={n:list(p.toMatrix().A) for n,p in new_poses.items()},
    affected_occurrences=affected,expected_physical_occurrences=2393,
    historical_station_qualified=False,installation_qualified=False,standard_assembly_modified=False))
print('Saved casing trial:',len(replaced),'definitions;',len(affected),'affected occurrences',flush=True)
