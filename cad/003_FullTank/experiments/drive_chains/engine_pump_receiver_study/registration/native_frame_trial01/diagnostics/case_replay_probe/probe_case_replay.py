import json
from pathlib import Path
import sys
ROOT = Path('/home/cyapp/MarkVIIILiberty')
H = ROOT / 'cad/003_FullTank/experiments/drive_chains'
sys.path.insert(0, str(H))
import FreeCAD as App
import Part
from powertrain_frame_registration_parts import bevel_case
read = lambda p: json.loads(p.read_text())
out = H / 'engine_pump_receiver_study/registration/native_frame_trial01/diagnostics/case_replay_probe'
out.mkdir(parents=True, exist_ok=True)
m = read(H / 'engine_pump_receiver_study/registration/native_support_trial01/saved_native_manifest.json')
c, sc = [{k: v['value'] for k, v in read(H / name)['controls'].items()}
         for name in ['transmission_frame_controls.json','transmission_support_controls.json']]
d = read(H / 'transmission_support_clearance_build/report.json')['dimensions']
core = read(H / 'transmission_core_build/report.json')
axis = App.Vector(*m['assemblies']['TransmissionCore']['world'][3:12:4])
dx = axis.x - core['shaft_axis_world_mm'][0]
def shape(path):
    s = Part.Shape(); s.read(str(path)); return s
original = shape(out.parent.parent / 'baseline_shapes/case_original_base.brep')
current = shape(m['definitions']['Def_TransmissionCore_bevel_case']['brep_path'])
cc = read(H / 'transmission_core_build/inputs/transmission_core_controls.json')['controls']
new_frame = dict(rear=c['frame_front_x']-axis.x, top=c['top_web_z']-axis.z,
                 bottom=c['bottom_web_z']-axis.z, height=c['channel_height'])
new, _ = bevel_case(cc, new_frame)
added, removed = current.cut(original), original.cut(current)
joined = new.fuse(added)
final = joined.cut(removed)
clean = final.copy().removeSplitter()
rejoin = new.fuse(added, 1e-7).cut(removed, 1e-7)
shapes = dict(original=original, current=current, new=new,
              added=added, removed=removed, joined=joined, final=final, clean=clean, fuzzy_replay=rejoin)
results = {}
for name, s in shapes.items():
    s.exportBrep(str(out / (name+'.brep')))
    results[name] = dict(valid=s.isValid(), solids=len(s.Solids), faces=len(s.Faces),volume=s.Volume,
                         tolerance=s.getTolerance(1),solid_volumes=[v.Volume for v in s.Solids])
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2),flush=True)
