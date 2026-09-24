"""Rebuild three suspension castings between fixed floor and trial engine height.

Retain existing rails and hardware as physical definitions. Rail X stations stay
registered to the crossmembers; their trial-only X translation is removed.
"""
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
native = out / 'PowertrainWithRebuiltEngineSupports.FCStd'
if native.exists():
    raise FileExistsError('Use a fresh output directory.')
pr = read(parent / 'report.json')
pn = parent / pr['native_file']
assert sha(pn) == pr['native_sha256']
pc = read(parent / 'independent_checks.json')
assert pc['local_phase_checks_passed'] and pc['native_sha256'] == pr['native_sha256']
m = read(parent / 'isolated/manifest.json')
assert m['native_sha256'] == pr['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
case_report = HERE / 'engine_case_build/report.json'
cr = read(case_report)
sc, cc, case = dict(cr['suspension_controls']), dict(cr['crossmember_controls']), dict(cr['controls'])
paths = [Path(__file__), case_report, parent / 'report.json', parent / 'independent_checks.json',
         HERE / 'engine_suspension_parts.py', HERE / 'engine_case_supports.py',
         HERE / 'engine_crossmember_parts.py']
locked = {str(path.relative_to(ROOT)): sha(path) for path in paths}

import FreeCAD as App
import Part
from engine_suspension_parts import parts
from engine_case_supports import front_yoke
from engine_crossmember_parts import box

V = App.Vector
doc = App.openDocument(str(pn))
axis_z = doc.TankLibertyEngine.getGlobalPlacement().Base.z
originals = {}
for name, x in [('EngineFrame_RearChannel', cc['rear_x']), ('EngineFrame_FrontCleat', cc['front_x'])]:
    row = rows[name]
    shape = doc.getObject(row['object']).LinkedObject.Shape.copy()
    shape.Placement = App.Placement(App.Matrix(*row['frame']))
    shape.translate(-V(x, 0, cc['floor_top']))
    if name == 'EngineFrame_FrontCleat':
        shape = shape.common(box(-100, 200, -100, 100, -1, cc['channel_height']))
    originals[name] = shape
definitions, occurrences, unused_receivers, datums = parts(sc, cc, axis_z, originals)
definitions['front_bracket'], front_profile = front_yoke(case, sc, cc, axis_z)
replacements = { 'EngineSuspension_' + name: key for name, key in [
    ('LeftBracket', 'left_bracket'), ('RightBracket', 'right_bracket'), ('FrontBracket', 'front_bracket')]}
for name, key in replacements.items():
    target = doc.getObject(rows[name]['object']).LinkedObject
    assert target.Shape.Placement.isIdentity()
    if target.TypeId == 'PartDesign::Body':
        target.Tip.Shape = definitions[key]
    else:
        target.Shape = definitions[key]
    if 'RegistrationAxisZ' not in target.PropertiesList:
        target.addProperty('App::PropertyLength', 'RegistrationAxisZ', 'Reconstruction')
    target.RegistrationAxisZ = axis_z
    if 'RegistrationSupportRevision' not in target.PropertiesList:
        target.addProperty('App::PropertyString', 'RegistrationSupportRevision', 'Reconstruction')
    target.RegistrationSupportRevision = 'Regenerated bracket profile between retained floor receivers and trial rail height; printed hardware/stock unchanged.'

rail_group = doc.LongitudinalSupports
assert rail_group.Placement.Rotation.isSame(App.Rotation(), 1e-12)
offset = rail_group.Placement.Base
rail_group.Placement = App.Placement(V(0, 0, offset.z), App.Rotation())
for row in occurrences:
    obj = doc.getObject(rows[row['name']]['object'])
    owners = [v for v in obj.InList if v.TypeId == 'App::Part' and obj in v.Group]
    assert len(owners) == 1
    world = App.Placement(V(*row['xyz']), App.Rotation(*row['rotation']))
    obj.LinkPlacement = owners[0].getGlobalPlacement().inverse().multiply(world)
doc.Root.Label = 'Powertrain trial — coupled phases and rebuilt engine supports'
doc.Root.RegistrationStatus = 'Engine supports rebuilt; transmission frame/casings and installation qualification remain open'
doc.recompute()
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(pn) == pr['native_sha256']
assert all(sha(ROOT / path) == digest for path, digest in locked.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for path in paths:
    shutil.copy2(path, frozen / (path.name if path.parent == HERE else path.parent.name + '_' + path.name))
write(out / 'report.json', dict(
    status='saved_support_trial_pending_independent_checks', native_file=native.name,
    native_sha256=sha(native), source_native=str(pn.relative_to(ROOT)), source_native_sha256=sha(pn),
    input_hashes=locked, controls=sc, crossmember_controls=cc, case_controls=case,
    crankshaft_axis_z=axis_z, datums=datums, front_yoke_profile=front_profile,
    replacement_definitions={name: rows[name]['definition'] for name in replacements},
    support_occurrences=occurrences, expected_physical_occurrences=2393,
    rail_policy='Retain source rail stock, bores and longitudinal stations 2940..4120; raise to engine mounting plane. No floor/crossmember geometry changes.',
    floor_receivers_changed=False, standard_assembly_modified=False,
    historical_station_qualified=False, engine_mount_holes_complete=False,
    installation_qualified=False,
))
print('Saved three rebuilt castings and 61 support occurrences at engine Z', axis_z, flush=True)
