"""Rephase both coupled epicyclic trains for the standard registration trial.

This is one static assembly, not a motion/pose feature. Keep the cross shaft,
its large suns, small rings and upstream bevel/input geometry at their existing
phases. Propagate the new output-carrier phase through both epicyclic stages.
"""
import argparse
import math
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
parent = a.source.resolve()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
native = out / 'PowertrainCoupledPhaseTrial.FCStd'
if native.exists():
    raise FileExistsError('Retain previous experiments; select a fresh output directory.')
r = read(parent / 'report.json')
source_native = parent / r['native_file']
assert sha(source_native) == r['native_sha256']
m = read(parent / 'isolated/manifest.json')
assert m['native_sha256'] == r['native_sha256']
checks = read(parent / 'independent_checks.json')
assert checks['placement_and_selected_interface_checks_passed']
assert checks['native_sha256'] == r['native_sha256']
paths = [Path(__file__), parent / 'report.json', parent / 'independent_checks.json',
         HERE / 'transmission_planet_controls.json', HERE / 'transmission_small_controls.json',
         HERE / 'transmission_planet_sources.json', HERE / 'transmission_small_sources.json']
locked = {str(f.relative_to(ROOT)): sha(f) for f in paths}
for key in ['transmission_planet_sources.json', 'transmission_small_sources.json']:
    for path, digest in read(HERE / key)['inspected_source_hashes'].items():
        assert sha(ROOT / path) == digest, path

large = {k: v['value'] for k, v in read(HERE / 'transmission_planet_controls.json')['controls'].items()}
small = {k: v['value'] for k, v in read(HERE / 'transmission_small_controls.json')['controls'].items()}
ns, np_, nr = [large['teeth_' + k] for k in ['sun', 'planet', 'ring']]
ss, sp, sr = [small['teeth_' + k] for k in ['sun', 'planet', 'ring']]
assert nr == ns + 2 * np_ and sr == ss + 2 * sp
carrier = r['small_pinion_phase_delta_deg']
case = (ns + nr) / nr * carrier
large_planet = (ns + np_) / np_ * carrier
small_sun = (ss + sr) / ss * case
small_planet = (ss + sp) / sp * case - ss / sp * small_sun
angles = dict(output_and_large_carrier=carrier, case_and_small_carrier=case,
              large_planet_spin=large_planet, small_sun_and_high_drum=small_sun,
              small_planet_spin=small_planet, cross_shaft_and_attached_gears=0.0)

import FreeCAD as App
import Part

doc = App.openDocument(str(source_native))
origin = doc.TransmissionCore.getGlobalPlacement().Base
V = App.Vector
source_rows = {v['name']: v for v in m['occurrences']}
modified = []

def around(point, degrees):
    return App.Placement(point, App.Rotation(V(0, 1, 0), degrees)).multiply(
        App.Placement(-point, App.Rotation()))

def parent_of(obj):
    parents = [v for v in obj.InList if v.TypeId == 'App::Part' and obj in v.Group]
    assert len(parents) == 1, obj.Name
    return parents[0]

def set_world(obj, world):
    local = parent_of(obj).getGlobalPlacement().inverse().multiply(world)
    if obj.TypeId == 'App::Link':
        obj.LinkPlacement = local
    else:
        obj.Placement = local

def rotate_group(name, degrees):
    obj = doc.getObject(name)
    set_world(obj, around(origin, degrees).multiply(obj.getGlobalPlacement()))
    modified.extend(v['name'] for v in m['occurrences'] if name in v['owners'])

def rotate_link(name, orbit_degrees, spin_degrees=None):
    row = source_rows[name]
    obj = doc.getObject(row['object'])
    assert obj.LinkedObject.Shape.Placement.isIdentity()
    before = App.Placement(App.Matrix(*row['frame']))
    world = around(origin, orbit_degrees).multiply(before)
    if spin_degrees is not None:
        # Orbit changes the gear's orientation too. Apply only the remaining
        # spin about its moved center, expressed in the common world Y direction.
        world = around(world.Base, spin_degrees - orbit_degrees).multiply(world)
    set_world(obj, world)
    modified.append(name)

for hand in ['Port', 'Starboard']:
    rotate_group(hand + 'PlanetSupports', carrier)
    rotate_group(hand + 'SmallPlanetSupports', case)
    rotate_link(hand + 'TransmissionCore_planet_disk', carrier)
    for suffix in ['brake_case', 'plain_case']:
        rotate_link(hand + 'TransmissionCore_' + suffix, case)
    for suffix in ['ring', 'gasket0', 'gasket1']:
        rotate_link(hand + 'PlanetTrain_' + suffix, case)
    rotate_link(hand + 'TransmissionCore_high_drum', small_sun)
    rotate_link(hand + 'SmallPlanetTrain_sun', small_sun)
    rotate_link(hand + 'SunRetention_ring', small_sun)
    for n in range(3):
        rotate_link(hand + 'PlanetTrain_planet' + str(n), carrier, large_planet)
        rotate_link(hand + 'SmallPlanetTrain_planet' + str(n), case, small_planet)

assert len(modified) == len(set(modified)) == 142
doc.Root.Label = 'Powertrain registration trial — coupled planetary phases'
doc.Root.RegistrationStatus = 'Coupled phase trial; support/casing installation still unqualified'
doc.recompute()
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(source_native) == r['native_sha256']
assert all(sha(ROOT / path) == digest for path, digest in locked.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for path in paths:
    shutil.copy2(path, frozen / (path.name if path.parent == HERE else path.parent.name + '_' + path.name))
write(out / 'report.json', dict(
    status='saved_coupled_phase_trial_pending_independent_checks', native_file=native.name,
    native_sha256=sha(native), source_native=str(source_native.relative_to(ROOT)),
    source_native_sha256=sha(source_native), source_manifest_sha256=sha(parent / 'isolated/manifest.json'),
    input_hashes=locked, angle_changes_world_y_deg=angles,
    teeth=dict(large=[ns, np_, nr], small=[ss, sp, sr]),
    changed_occurrences=modified, expected_physical_occurrences=2393,
    source_interpretation='HB120/122: large sun and small ring follow cross shaft; large ring/case carries small planets; output follows large carrier.',
    source_review='Original MarkVIII061 and MarkVIII062 scans directly inspected on 23 September 2026.',
    all_definition_shapes_untouched_by_builder=True, installation_qualified=False,
    historical_station_qualified=False, continuous_motion_qualified=False,
    standard_assembly_modified=False,
))
print('Saved coupled phase trial', angles, 'changed leaves', len(modified), flush=True)
