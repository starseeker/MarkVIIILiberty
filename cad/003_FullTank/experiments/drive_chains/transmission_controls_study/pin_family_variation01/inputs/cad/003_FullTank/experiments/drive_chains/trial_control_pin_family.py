"""Create the shared-pin revision and preserve a rejected low-fork datum trial."""
import argparse
from pathlib import Path
import shutil
import sys
import uuid

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.cad_build import metadata
from lib.camera_review import validate_native_bindings
from control_pin_family_parts import CHANGED, revise
from transmission_control_joint_parts import parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
cfg = read(a.controls)
C = H/'transmission_controls_study'
parent = C/'track_rods_integrated01'
pr, m = read(parent/'report.json'), read(parent/'isolated/manifest.json')
native = parent/pr['native_file']
assert sha(native) == pr['native_sha256'] == m['native_sha256']
assert read(parent/'qualification.json')['local_static_checks_passed']
for path, digest in cfg['evidence_hashes'].items():
    assert sha(ROOT/path) == digest
keys = set(CHANGED) | {'Def_ControlJoint_cotter', 'Def_USStdControlNut',
                      'Def_BrakeFront_lever', 'Def_RearControlFulcrum_lever_low_left',
                      'Def_RearControlFulcrum_lever_low_right'}
rows = {v['name']: v for v in m['occurrences'] if v['definition'] in CHANGED
        or v['name'].endswith(('HighSpeedBrakeControlCotter', 'HighSpeedBrakeControlNut',
                               'LowSpeedBrakeLever', 'LowHorizontalLever'))}
assert len(rows) == 16 and {v['definition'] for v in rows.values()} == keys
validate_native_bindings(dict(native_file=str(native), render_occurrences=list(rows), landmarks=[]), m)
old = {}
for key in sorted(keys):
    d = m['definitions'][key]
    assert sha(d['brep_path']) == d['brep_sha256']
    s = Part.Shape()
    s.read(d['brep_path'])
    old[key] = s
shapes = revise(old, cfg['controls']['pin_diameter_mm'], cfg['controls']['high_radial_gap_mm'])
out.mkdir(parents=True)
doc = App.newDocument('ControlPinFamily')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
made = {}
for key, shape in sorted(shapes.items()):
    body = doc.addObject('PartDesign::Body', key)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedPinFamily').Shape = shape
    for prop, value in m['definitions'][key]['properties'].items():
        metadata(body, **{prop: value})
    metadata(body, FamilyRevision='Common M568A diameter estimate; preserved source marks. '
             'Low-fork length datum and complete rods remain unresolved.')
    made[key] = body
for name, row in rows.items():
    link = doc.addObject('App::Link', name)
    root.addObject(link)
    link.setLink(made[row['definition']])
    link.LinkPlacement = App.Placement(App.Matrix(*row['frame']))
    metadata(link, Coverage='reconstruction_trial')
for obj in [root, library]:
    obj.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:pin-family:'+obj.Name))
library.Visibility = False
doc.recompute()
saved = out/'ControlPinFamily.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
inputs = [Path(__file__), H/'control_pin_family_parts.py', H/'transmission_control_joint_parts.py',
          H/'transmission_input_installation_parts.py', a.controls.resolve(),
          parent/'report.json', parent/'qualification.json', parent/'isolated/manifest.json',
          *[ROOT/path for path in cfg['evidence_hashes']],
          H.parents[1]/'lib/cad_build.py', H.parents[1]/'lib/evidence.py']
for f in inputs:
    path = out/'inputs'/f.relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, path)
specs = {n: dict(definition=v['definition'], frame=v['frame'],
                role='receiver' if 'Lever' in n else n.split('Control')[-1].lower())
         for n, v in rows.items()}
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      parent_native=str(native.relative_to(ROOT)), parent_native_sha256=sha(native),
      input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
      controls=cfg['controls'], specs=specs, changed_definitions=list(CHANGED),
      prototype_physical_occurrences=len(rows), prototype_definition_count=len(shapes),
      geometry_integrated=False, historical_geometry_qualified=False, installation_qualified=False))
# This diagnostic is not part of the accepted physical prototype or assembly.
# Literal 1-inch pin-centre-to-face interpretation with receiver-clearing throat.
low = read(C/'track_joint_controls02.json')['controls']
low.update(fork_length=25.4, fork_length_datum='pin_center_to_rod_seat',
           pin_length=41.275, pin_diameter=12.7, ear_stock=11.1125)
forks, detail = parts(low, old['Def_USStdControlNut'])
diagnostic = out/'diagnostics/low_fork_one_inch'
diagnostic.mkdir(parents=True)
dd = App.newDocument('LowForkDatumDiagnostic')
ob = dd.addObject('PartDesign::Feature', 'RejectedLowForkLengthInterpretation')
ob.Shape = forks['fork']
metadata(ob, SourcePartMark='M569A', SourceRecords=['SNL:87:002'],
         ReconstructionStatus='Diagnostic only: 25.4mm pin-centre-to-face leaves3.175mm socket; fails19.05mm engagement criterion.')
dd.recompute()
dd.saveAs(str(diagnostic/'LowForkDatumDiagnostic.FCStd'))
App.closeDocument(dd.Name)
write(diagnostic/'report.json', dict(source_printed_length_mm=25.4,
      assumed_datum='pin_center_to_rod_seat', receiver_clearing_throat_mm=22.225,
      available_thread_length_mm=detail['thread_envelope_length_mm'],
      chosen_minimum_engagement_mm=19.05, passes_engagement=False,
      minimum_engagement_is_modeling_criterion_not_historical_standard=True,
      disposition='Reject this combination of estimated profile and length datum. Source does not specify datum; no revised dimension accepted here.',
      native_sha256=sha(diagnostic/'LowForkDatumDiagnostic.FCStd'),
      geometry_integrated=False))
print('Saved16 occurrences/9 definitions; four local definition revisions and separate rejected low-fork datum.', flush=True)
