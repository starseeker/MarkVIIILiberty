"""Save an alternative with the original transmission frame following its shaft."""
import argparse
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
ROOT = STAGE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
parent, out = a.source.resolve(), a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
native = out / 'PowertrainWithFollowingFrame.FCStd'
assert not native.exists(), 'Use a fresh output directory.'
r = read(parent / 'report.json')
source = parent / r['native_file']
assert sha(source) == r['native_sha256']
assert read(parent / 'independent_checks.json')['local_support_checks_passed']
baseline_path = HERE / 'transmission_core_build/report.json'
original_axis = read(baseline_path)['shaft_axis_world_mm']
paths = [Path(__file__), parent / 'report.json', parent / 'independent_checks.json',
         baseline_path, HERE / 'transmission_frame_controls.json',
         HERE / 'transmission_input_calibration.json']
locked = {str(f.relative_to(ROOT)): sha(f) for f in paths}

import FreeCAD as App

doc = App.openDocument(str(source))
axis = doc.TransmissionCore.getGlobalPlacement().Base
delta = axis - App.Vector(*original_axis)
group = doc.TransmissionMountingFrame
assert group.Placement.isIdentity() and group.getGlobalPlacement().isIdentity()
assert len(group.Group) == 15
assert doc.TransmissionCaseMounting.Placement.isIdentity()
group.Placement = App.Placement(delta, App.Rotation())
doc.Root.Label = 'Powertrain trial — transmission frame follows shaft'
doc.Root.RegistrationStatus = 'Frame follows shaft; source, hull interfaces, casings and full installation require review'
doc.recompute()
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(source) == r['native_sha256']
assert all(sha(ROOT / f) == digest for f, digest in locked.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for f in paths:
    shutil.copy2(f, frozen / (f.name if f.parent == HERE else f.parent.name + '_' + f.name))
write(out / 'report.json', dict(
    status='saved_following_frame_hypothesis_pending_checks',
    native_file=native.name, native_sha256=sha(native),
    source_native=str(source.relative_to(ROOT)), source_native_sha256=sha(source),
    input_hashes=locked, original_axis_mm=original_axis, shaft_axis_mm=list(axis),
    frame_translation_mm=list(delta), changed_assembly='TransmissionMountingFrame',
    expected_affected_occurrences=15, expected_physical_occurrences=2393,
    definition_geometry_intentionally_changed=False, historical_station_qualified=False,
    installation_qualified=False, standard_assembly_modified=False))
print('Saved frame-following alternative:', list(delta), flush=True)
