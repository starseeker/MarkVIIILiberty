"""Save a placement-only diagnostic; supports and housings remain unresolved.

Run through the project headless launcher. This deliberately does not promote
the station hypothesis or regenerate old support/casing stock as if it fitted.
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
p.add_argument('--output', type=Path, required=True)
p.add_argument('--station', default='common_horizontal_axis_mean')
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
native = out / 'PowertrainRegistrationDiagnostic.FCStd'
if native.exists():
    raise FileExistsError('Use a fresh trial directory: ' + str(native))
receiver = HERE / 'engine_pump_receiver_study'
source = receiver / 'assembly_trial02/DrivetrainWithBothPumps.FCStd'
parent_report = receiver / 'assembly_trial02/report.json'
stations_path = receiver / 'registration/station_candidates.json'
route_path = HERE / 'installed_pitch_route_report.json'
stations, old = read(stations_path), read(route_path)
selected = stations['candidates'][a.station]
assert selected['mathematical_checks_passed']
assert sha(source) == read(parent_report)['native_sha256']
for rel, digest in stations['input_hashes'].items():
    assert sha(ROOT / rel) == digest, rel
inputs = [source, parent_report, stations_path, route_path, Path(__file__)]
locked = {str(f.relative_to(ROOT)): sha(f) for f in inputs}

import FreeCAD as App
import Part

V = App.Vector
doc = App.openDocument(str(source))
translation = App.Placement(V(*selected['rigid_powertrain_translation_mm']), App.Rotation())
moving = [
    'TransmissionCore', 'FuelPressureInstallation', 'EngineFlywheelAssembly',
    'TankLibertyEngine', 'PortTransmissionOutput', 'StarboardTransmissionOutput',
    'FixedTransmissionBearings', 'LongitudinalSupports',
]
for name in moving:
    obj = doc.getObject(name)
    # These parents have identity world frames in the bound source document.
    parent = next(x for x in obj.InList if x.TypeId == 'App::Part' and obj in x.Group)
    assert parent.getGlobalPlacement().isIdentity(), name
    obj.Placement = translation.multiply(obj.Placement)

old_points = old['vertices_world_xz_mm']
new_points = selected['vertices_world_xz_mm']
assert len(old_points) == len(new_points) == 50

def unit(points, n, joint=False):
    x, z = points[n]
    end = points[(n + 1) % 50]
    start = points[(n - 1) % 50] if joint else (x, z)
    angle = -math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))
    if joint:
        angle += 180
    return App.Placement(V(x, 0, z), App.Rotation(V(0, 1, 0), angle))

old_axis = old['candidate_transmission_axis_xz_mm']
new_axis = selected['transmission_axis_xz_mm']
phase_delta = selected['small_pinion_phase_deg'] - old['small_pinion_candidate_phase_deg']
phase = App.Rotation(V(0, 1, 0), phase_delta)
about_old_axis = App.Placement(V(*[old_axis[0], 0, old_axis[1]]), phase).multiply(
    App.Placement(V(-old_axis[0], 0, -old_axis[1]), App.Rotation()))
small_delta = translation.multiply(about_old_axis)
changed_links = []
for side in ['Port', 'Starboard']:
    assert doc.getObject(side + 'Chain').Placement.isIdentity()
    for n in range(50):
        for joint, suffixes in [(False, ['Inboard', 'Outboard']), (True, ['Bush', 'Pin', 'Cotter'])]:
            delta = unit(new_points, n, joint).multiply(unit(old_points, n, joint).inverse())
            for suffix in suffixes:
                name = '%sChain_%s%02d_%s' % (side, 'Joint' if joint else 'Link', n, suffix)
                obj = doc.getObject(name)
                obj.LinkPlacement = delta.multiply(obj.LinkPlacement)
                changed_links.append(name)
    name = side + 'Chain_TransmissionPinion'
    obj = doc.getObject(name)
    obj.LinkPlacement = small_delta.multiply(obj.LinkPlacement)
    changed_links.append(name)
    # Output parent already receives the translation. Rotate its shaft and drum
    # together so the retained spline fits the newly phased chain pinion.
    for suffix in ['shaft', 'drum']:
        name = side + 'TransmissionOutput_' + suffix
        obj = doc.getObject(name)
        obj.LinkPlacement = about_old_axis.multiply(obj.LinkPlacement)
        changed_links.append(name)

doc.Root.Label = 'Powertrain station diagnostic — support/casing rebuild required'
for name, value in [
    ('RegistrationTrial', a.station),
    ('RegistrationStatus', 'Placement diagnostic only; installation unqualified'),
]:
    if name not in doc.Root.PropertiesList:
        doc.Root.addProperty('App::PropertyString', name, 'Registration study')
    setattr(doc.Root, name, value)
if 'InstallationQualified' not in doc.Root.PropertiesList:
    doc.Root.addProperty('App::PropertyBool', 'InstallationQualified', 'Registration study')
doc.Root.InstallationQualified = False
doc.recompute()
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert all(sha(ROOT / rel) == digest for rel, digest in locked.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for path in [Path(__file__), stations_path, route_path]:
    shutil.copy2(path, frozen / path.name)
write(out / 'report.json', dict(
    status='saved_placement_diagnostic_not_an_installed_solution',
    native_file=native.name, native_sha256=sha(native), source_native=str(source.relative_to(ROOT)),
    source_native_sha256=sha(source), input_hashes=locked, station=a.station,
    translation_mm=selected['rigid_powertrain_translation_mm'],
    small_pinion_phase_delta_deg=phase_delta, translated_assemblies=moving,
    separately_reposed_links=changed_links, expected_physical_occurrences=2393,
    definition_geometry_changed=False, standard_assembly_modified=False,
    installation_qualified=False, historical_station_qualified=False,
    pending_interfaces=[
        'Both chain casings and their wall, cap, trim and support interfaces require regeneration.',
        'Fixed-bearing seats follow the shaft, but their feet must reconnect to the unchanged transmission frame.',
        'Engine rails follow the engine; front and rear suspensions must reconnect to the unchanged floor attachments.',
        'Output shaft/drum and chain pinion share phase; internal transmission receiving splines/gearing need phase review.',
        'Hull-connected controls, fuel lines and surrounding equipment need renewed interface checks.',
        'Parent coupled-pump full material and oil STEP qualification are still pending.',
    ],
))
print('Saved', native, 'translation', selected['rigid_powertrain_translation_mm'], flush=True)
