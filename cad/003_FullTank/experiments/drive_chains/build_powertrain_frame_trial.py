"""Rebuild fixed bearing and bevel-case webs between trial axes and retained frame."""
import argparse
import copy
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

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
native = out / 'PowertrainWithRebuiltTransmissionSupports.FCStd'
assert not native.exists(), 'Use a fresh output directory.'
r = read(parent / 'report.json')
pn = parent / r['native_file']
assert sha(pn) == r['native_sha256']
assert read(parent / 'independent_checks.json')['local_support_checks_passed']
m = read(parent / 'isolated/manifest.json')
assert m['native_sha256'] == r['native_sha256']
rows = {v['name']: v for v in m['occurrences']}
paths = [Path(__file__), HERE / 'powertrain_frame_registration_parts.py',
         HERE / 'transmission_frame_parts.py', HERE / 'transmission_core_parts.py',
         HERE / 'transmission_support_parts.py', parent / 'report.json',
         parent / 'independent_checks.json', HERE / 'transmission_frame_research.json',
         HERE / 'transmission_case_mount_parts.py',
         HERE / 'transmission_case_mount_trial_build/report.json',
         HERE / 'transmission_case_mount_trial_build/inputs/parent_case.brep']
reports = {}
for key, folder in [('support', 'transmission_support_clearance_build'),
                    ('frame', 'transmission_frame_clearance_build'), ('core', 'transmission_core_build')]:
    path = HERE / folder / 'report.json'
    reports[key] = read(path)
    paths.append(path)
controls_paths = {
    'frame': HERE / 'transmission_frame_clearance_build/inputs/transmission_frame_controls.json',
    'support': HERE / 'transmission_frame_clearance_build/inputs/transmission_support_controls.json',
    'core': HERE / 'transmission_core_build/inputs/transmission_core_controls.json'}
paths.extend(controls_paths.values())
fc, sc = [{k: v['value'] for k, v in read(controls_paths[name])['controls'].items()}
          for name in ['frame', 'support']]
cc = read(controls_paths['core'])['controls']
locked = {str(path.relative_to(ROOT)): sha(path) for path in paths}

import FreeCAD as App
import Part
from transmission_frame_parts import revised_bracket
from powertrain_frame_registration_parts import bevel_case, replay_features
from transmission_case_mount_parts import case_mount_parts

base_dir = out / 'baseline_shapes'
base_dir.mkdir(exist_ok=True)
archives = {}

def archived(folder, filename, definition, report_key, label):
    path = HERE / folder / filename
    assert sha(path) == reports[report_key]['native_sha256']
    with zipfile.ZipFile(path) as z:
        xml = ET.fromstring(z.read('Document.xml'))
        prop = xml.find('./ObjectData/Object[@name="' + definition + '"]/Properties/Property[@name="Shape"]/Part')
        assert prop is not None, definition
        data = z.read(prop.get('file'))
    dest = base_dir / (label + '.brep')
    dest.write_bytes(data)
    s = Part.Shape()
    s.read(str(dest))
    assert s.Placement.isIdentity() and s.isValid() and len(s.Solids) == 1
    archives[label] = dict(native=str(path.relative_to(ROOT)), native_sha256=sha(path),
                           definition=definition, brep_sha256=sha(dest))
    return s

doc = App.openDocument(str(pn))
axis = doc.TransmissionCore.getGlobalPlacement().Base
old_axis = App.Vector(*reports['core']['shaft_axis_world_mm'])
dx = axis.x - old_axis.x
dimensions = copy.deepcopy(reports['support']['dimensions'])
changes = {}
replacements = {}
for role in ['inner', 'outer']:
    name = 'Def_FixedBearing_' + role + '_bracket'
    minimal = archived('transmission_support_clearance_build', 'TransmissionSupportCandidate.FCStd',
                       name, 'support', role + '_minimal')
    old_base = archived('transmission_frame_clearance_build', 'TransmissionFrameCandidate.FCStd',
                        name, 'frame', role + '_original_base')
    dimensions[role]['foot_aft_x_mm'] -= dx
    dimensions[role]['foot_front_x_mm'] -= dx
    revised, details = revised_bracket(minimal, role, fc, sc, dimensions, axis)
    target = doc.getObject(name)
    final, features = replay_features(old_base, revised, target.Shape)
    for label, shape in [('revised_base', revised), ('detailed_before', target.Shape)]:
        shape.exportBrep(str(base_dir / (role + '_' + label + '.brep')))
    (target.Tip if target.TypeId == 'PartDesign::Body' else target).Shape = final
    changes[role] = dict(**details, **features)
    replacements[name] = [hand + 'FixedBearing_' + role + '_bracket' for hand in ['Port', 'Starboard']]

name = 'Def_TransmissionCore_bevel_case'
old_base = archived('transmission_core_build', 'TransmissionCoreCandidate.FCStd', name, 'core', 'case_raw_original_base')
old_frame = reports['core']['dimensions']['bevel_frame_local_mm']
regenerated, _ = bevel_case(cc, old_frame)
assert abs(regenerated.cut(old_base).Volume) < 1e-5 and abs(old_base.cut(regenerated).Volume) < 1e-5
new_frame = dict(rear=fc['frame_front_x'] - axis.x, top=fc['top_web_z'] - axis.z,
                 bottom=fc['bottom_web_z'] - axis.z, height=fc['channel_height'])
revised, outline = bevel_case(cc, new_frame)
target = doc.getObject(name)
mount_report = read(HERE / 'transmission_case_mount_trial_build/report.json')
premount_path = HERE / 'transmission_case_mount_trial_build/inputs/parent_case.brep'
assert sha(premount_path) == mount_report['parent_case_brep_sha256']
premount = Part.Shape()
premount.read(str(premount_path))
revised_detailed, features = replay_features(old_base, revised, premount)
mount_controls = dict(mount_report['controls'])
new_mount_controls = dict(mount_controls, frame_front_x=new_frame['rear'],
                         top_web_z=new_frame['top'], bottom_web_z=new_frame['bottom'])
channels = {key: doc.getObject(rows['TransmissionFrame_' + label + 'Channel']['object']).LinkedObject.Shape.copy()
            for key, label in [('top', 'Top'), ('bottom', 'Bottom')]}
nut = doc.getObject(rows['CaseMount_UpperPort_nut']['object']).LinkedObject.Shape.copy()
pc = mount_report['pin_controls']
def mounted(shape, controls):
    return case_mount_parts(controls, shape, channels, nut, pc)
_, original_mount, _, _ = mounted(premount, mount_controls)
assert abs(original_mount['case'].cut(target.Shape).Volume) < 1e-5
assert abs(target.Shape.cut(original_mount['case']).Volume) < 1e-5
_, revised_mount, installed_mounts, mount_datums = mounted(revised_detailed, new_mount_controls)
_, original_base_mount, _, _ = mounted(old_base, mount_controls)
_, revised_base_mount, _, _ = mounted(revised, new_mount_controls)
final = revised_mount['case']
for label, shape in [('original_base', original_base_mount['case']),
                     ('revised_base', revised_base_mount['case']), ('detailed_before', target.Shape)]:
    shape.exportBrep(str(base_dir / ('case_' + label + '.brep')))
(target.Tip if target.TypeId == 'PartDesign::Body' else target).Shape = final
changes['case'] = dict(**features, outline_xz_mm=outline, frame_local_mm=new_frame)
replacements[name] = ['CenterTransmissionCore_bevel_case']
mount_group = doc.TransmissionCaseMounting
assert mount_group.Placement.isIdentity()
mount_group.Placement = App.Placement(V := App.Vector(-dx, 0, old_axis.z - axis.z), App.Rotation())
mount_frames = {name: list(doc.TransmissionCore.getGlobalPlacement().multiply(s.Placement).toMatrix().A)
                for key, s in installed_mounts.items()
                if key not in ['case', 'Upper_channel', 'Lower_channel']
                for name in ['CaseMount_' + key]}
assert len(mount_frames) == 16
channel_regeneration = {}
for key, label in [('top', 'Upper'), ('bottom', 'Lower')]:
    one, two = channels[key], revised_mount[label]
    channel_regeneration[key] = dict(missing_mm3=one.cut(two).Volume, added_mm3=two.cut(one).Volume)
    assert abs(channel_regeneration[key]['missing_mm3']) < 1e-5 and abs(channel_regeneration[key]['added_mm3']) < 1e-5
for name in replacements:
    obj = doc.getObject(name)
    obj.addProperty('App::PropertyString', 'RegistrationWebRevision', 'Reconstruction')
    obj.RegistrationWebRevision = 'Frame-reaching webs rebuilt; later saved bosses and pockets replayed as material deltas. Local and installation validation required.'
doc.Root.Label = 'Powertrain trial — engine and transmission supports rebuilt'
doc.Root.RegistrationStatus = 'Transmission webs rebuilt; frame packing/fasteners, casings and installation qualification remain open'
doc.recompute()
doc.saveAs(str(native))
App.closeDocument(doc.Name)
assert sha(pn) == r['native_sha256']
assert all(sha(ROOT / key) == digest for key, digest in locked.items())
frozen = out / 'frozen_inputs'
frozen.mkdir()
for path in paths:
    shutil.copy2(path, frozen / (path.name if path.parent == HERE else path.parent.parent.name + '_' + path.parent.name + '_' + path.name))
write(out / 'report.json', dict(status='saved_frame_trial_pending_independent_checks',
    native_file=native.name, native_sha256=sha(native), source_native=str(pn.relative_to(ROOT)),
    source_native_sha256=sha(pn), input_hashes=locked, baseline_archives=archives,
    baseline_brep_hashes={p.name: sha(p) for p in base_dir.glob('*.brep')},
    frame_controls=fc, support_controls=sc, core_controls=cc,
    original_axis_mm=list(old_axis), shaft_axis_mm=list(axis), bracket_dimensions=dimensions,
    original_bracket_dimensions=reports['support']['dimensions'], changes=changes,
    replacement_definitions=replacements, expected_physical_occurrences=2393,
    mount_controls=new_mount_controls, mount_datums=mount_datums,
    mount_occurrence_frames=mount_frames, channel_regeneration=channel_regeneration,
    frame_and_floor_unchanged=True, occurrence_frames_unchanged=False,
    source_interpretation='HB125/126 and SNL Plate23 show fixed frame behind case and brackets. Rebuilt webs retain existing provisional frame planes; inner packing gap remains unresolved.',
    source_review='Original MarkVIII063/064 and SNL p295-geometry directly inspected on 23 September 2026.',
    historical_station_qualified=False, installation_qualified=False, standard_assembly_modified=False))
print('Saved three rebuilt transmission casting definitions at', list(axis), flush=True)
