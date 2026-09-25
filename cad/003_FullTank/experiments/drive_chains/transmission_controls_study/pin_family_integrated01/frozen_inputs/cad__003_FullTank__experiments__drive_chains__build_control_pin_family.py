"""Transfer four tested definition revisions without changing the full hierarchy."""
import argparse
from pathlib import Path
import shutil
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
from lib.evidence import read, write, sha
from lib.cad_build import metadata

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
C = H/'transmission_controls_study'
prototype = C/'pin_family01'
r, pm = read(prototype/'report.json'), read(prototype/'isolated/manifest.json')
source = ROOT/r['parent_native']
old = read(source.parent/'isolated/manifest.json')
q = read(source.parent/'qualification.json')
assert sha(source) == r['parent_native_sha256'] == old['native_sha256'] == q['native_sha256']
assert q['local_static_checks_passed']
trial = prototype/r['native_file']
assert sha(trial) == r['native_sha256'] == pm['native_sha256']
assert all(sha(ROOT/f) == h for f, h in r['input_hashes'].items())
receipts = [folder/file for folder in [prototype, C/'pin_family_variation01']
            for file in ['independent_checks.json', 'context_checks.json', 'exchange_checks.json']]
receipts.append(prototype/'reproduction_checks.json')
for file in receipts:
    receipt = read(file)
    assert receipt['passed'] and receipt['native_sha256'] == read(file.parent/'report.json')['native_sha256']
assert read(prototype/'visual_review.json')['disposition'] == 'reviewed_local_approximation'
inputs = [Path(__file__), H.parents[1]/'lib/cad_build.py', prototype/'report.json',
          prototype/'isolated/manifest.json', prototype/'operating_interfaces.json', trial,
          prototype/'visual_review.json', prototype/'render_receipt.json',
          source.parent/'qualification.json', source.parent/'isolated/manifest.json', *receipts]
doc = App.openDocument(str(trial))
try:
    shapes = {key: doc.getObject(key).Shape.copy() for key in r['changed_definitions']}
finally:
    App.closeDocument(doc.Name)
out.mkdir(parents=True)
doc = App.openDocument(str(source))
for key, shape in shapes.items():
    body = doc.getObject(key)
    assert body.Placement.isIdentity() and not hasattr(body, 'ControlPinFamilyUpdate')
    body.Tip.Shape = shape
    metadata(body, ControlPinFamilyUpdate='Common M568A12.7mm diameter estimate; high-speed receiver/fork bores13mm. '
             'Regenerate pin_family_controls01.json with trial_control_pin_family.py, then build_control_pin_family.py. '
             'Low-speed fork length datum and full rod routes remain open. See pin_family_integrated01/qualification.json.')
doc.Root.Label = 'Powertrain development — shared control-pin family'
doc.Root.RegistrationStatus = 'Shared M568A pin estimate reconciled with low-speed receivers. High-speed fork and paired lever bores revised locally; all frames retained. M569A fork-length datum, low rods, springs and complete controls remain unfinished.'
doc.recompute()
saved = out/'PowertrainWithControlPinFamily.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
assert sha(source) == r['parent_native_sha256']
frozen = out/'frozen_inputs'
frozen.mkdir()
for file in inputs:
    if file.suffix != '.FCStd':
        shutil.copy2(file, frozen/str(file.relative_to(ROOT)).replace('/', '__'))
prior = {v['name']: v for v in old['occurrences']}
expected = {n: dict(**spec, owners=prior[n]['owners'], prototype_occurrence=n) for n, spec in r['specs'].items()}
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      source_native=str(source.relative_to(ROOT)), source_native_sha256=sha(source),
      prototype=str(prototype.relative_to(ROOT)), prototype_native_sha256=sha(trial),
      controls=r['controls'], input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
      expected_affected_occurrences=expected, affected_occurrences=sorted(expected),
      changed_definitions=r['changed_definitions'], new_definitions=[], new_assemblies=[],
      expected_new_occurrences={}, added_children={}, changed_group_frames={},
      placement_changed_objects=[],
      added_inherited_properties={k: ['ControlPinFamilyUpdate'] for k in r['changed_definitions']},
      expected_physical_occurrences=3264, expected_definition_count=568, expected_assembly_count=359,
      historical_geometry_qualified=False, installation_qualified=False,
      standard_assembly_modified=False, channel_complete=False, packet_complete=False))
print('Saved3264 occurrences/568 definitions/359 groups; four definitions revised, all frames retained.', flush=True)
