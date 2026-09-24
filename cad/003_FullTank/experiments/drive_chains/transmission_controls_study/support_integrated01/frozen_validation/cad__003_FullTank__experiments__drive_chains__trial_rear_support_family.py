"""Combine M4135/M4136 with two estimated M4129 cleats and drilled floor."""
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
from rear_right_cleat_parts import parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists()
cfg = read(a.controls)
c = cfg['controls']
C = H/'transmission_controls_study'
inputs = [a.controls.resolve(), Path(__file__), H/'rear_right_cleat_parts.py',
          H/'rear_control_channel_mount_parts.py', H/'transmission_frame_joint_parts.py',
          H/'transmission_brake_stop_parts.py', H.parents[1]/'lib/cad_build.py']
for file, digest in cfg['evidence_hashes'].items():
    assert sha(ROOT/file) == digest
    inputs.append(ROOT/file)
sources = {}
for name in ['channel_sources01/sources.json', 'spring_sources01/sources.json']:
    packet = C/name
    data = read(packet)
    for file, digest in data['source_hashes'].items():
        assert sha(ROOT/file) == digest
    sources.update({v['record_id']: v for v in data['source_records']})
    inputs.append(packet)
manifests, reports, natives = {}, {}, {}
for key in ['parent', 'low', 'high']:
    folder = C/c[key]
    r, m = read(folder/'report.json'), read(folder/'isolated/manifest.json')
    native = folder/r['native_file']
    assert sha(native) == r['native_sha256'] == m['native_sha256']
    manifests[key], reports[key], natives[key] = m, r, native
    inputs.extend([folder/'report.json', folder/'isolated/manifest.json'])


def row(key, name):
    return next(v for v in manifests[key]['occurrences'] if v['name'] == name)


def shape(key, name):
    one = row(key, name)
    validate_native_bindings(dict(native_file=str(natives[key]),
                                  render_occurrences=[name], landmarks=[]), manifests[key])
    d = manifests[key]['definitions'][one['definition']]
    assert sha(d['brep_path']) == d['brep_sha256']
    s = Part.Shape()
    s.read(d['brep_path'])
    assert s.Placement.isIdentity()
    return s


floor_pose = App.Placement(App.Matrix(*row('parent', 'hull_floor_7')['frame']))
shapes, details = parts(c, shape('parent', 'hull_floor_7'), floor_pose)
for role, key, name in [('channel', 'low', 'RearControlChannelStock'),
                         ('low_bracket', 'low', 'PortLowSpringBracket'),
                         ('high_bracket', 'high', 'PortHighSpringBracket'),
                         ('high_rivet', 'high', 'PortHighSpringRivet1'),
                         ('lock', 'parent', 'RearChannelLeftCleat1LockWasher'),
                         ('nut', 'parent', 'RearChannelLeftCleat1Nut')]:
    shapes[role] = shape(key, name)
out.mkdir(parents=True)
doc = App.newDocument('RearSupportFamily')
root = doc.addObject('App::Part', 'Root')
library = doc.addObject('App::Part', 'Definitions')
records = dict(channel=['SNL:63:010'], floor=['SNL:33:005'],
               cleat=['SNL:65:024', 'SNL:63:007'], bolt=['SNL:33:005'],
               lock=['SNL:33:005'], nut=['SNL:33:005'],
               low_bracket=['SNL:38:001', 'SNL:63:008'], low_rivet=['SNL:170:005'],
               high_bracket=reports['high']['record_ids']['bracket'],
               high_rivet=reports['high']['record_ids']['rivet'])
marks = dict(channel='M4128', floor='Existing floor7 with two additional holes',
             cleat='M4129', bolt='3/4 x 1-5/8 inch U.S. Standard bolt',
             lock='3/4 inch lock washer', nut='3/4 inch plain U.S. Standard nut',
             low_bracket='M4136', low_rivet='1/2 x 1-7/8 inch button-head rivet',
             high_bracket='M4135', high_rivet='1/2 x 3/4 inch button-head rivet')
made, specs = {}, {}
for role, s in shapes.items():
    body = doc.addObject('PartDesign::Body', 'Def_RearSupport_'+role)
    library.addObject(body)
    body.newObject('PartDesign::Feature', 'ReconstructedSupport').Shape = s
    metadata(body, SourceRecords=records[role], SourcePartMark=marks[role],
             SurveyIds=sorted({pid for rid in records[role] if rid in sources
                               for pid in sources[rid]['part_ids']}),
             Representation='unqualified_support_family_trial',
             ReconstructionStatus='Estimated M4129 shape and shared M4136 rivet stack; historical mounting not established.',
             ParameterUpdate='Regenerate '+a.controls.name+' with trial_rear_support_family.py')
    made[role] = body
    s.exportBrep(str(out/(role+'.brep')))


def install(name, role, owner, local):
    link = doc.addObject('App::Link', name)
    owner.addObject(link)
    link.setLink(made[role])
    link.LinkPlacement = local
    metadata(link, SourceRecords=records[role], Coverage='reconstruction_trial')
    specs[name] = dict(role=role, owner=owner.Name,
                      frame=list(owner.getGlobalPlacement().multiply(local).toMatrix().A))


install('RearControlChannelStock', 'channel', root,
        App.Placement(App.Matrix(*row('low', 'RearControlChannelStock')['frame'])))
install('hull_floor_7', 'floor', root, floor_pose)
for key, suffix in [('high', 'HighSpringSupport'), ('low', 'LowSpringSupport')]:
    for side, xyz in reports[key]['controls']['stations'].items():
        point = App.Vector(*xyz)
        if key == 'low':
            point.z += c['cleat']['stock']
        group = doc.addObject('App::Part', side+suffix)
        root.addObject(group)
        group.Placement = App.Placement(point, App.Rotation())
        for name, spec in reports[key]['specs'].items():
            if spec['owner'] != group.Name:
                continue
            previous = App.Placement(App.Matrix(*row(key, name)['frame']))
            local = App.Placement(App.Vector(*xyz), App.Rotation()).inverse().multiply(previous)
            install(name, key+'_'+spec['role'], group, local)
rotation = App.Rotation(App.Vector(1, 0, 0), 180)
for side, xyz in c['stations'].items():
    name = side+'RightChannelCleat'
    group = doc.addObject('App::Part', name+'Mount')
    root.addObject(group)
    group.Placement = App.Placement(App.Vector(*xyz), App.Rotation())
    install(name, 'cleat', group, App.Placement())
    x, y = c['cleat']['bolt_x'], c['cleat']['bolt_y']
    for suffix, role, z in [('Bolt', 'bolt', c['cleat']['stock']),
                            ('LockWasher', 'lock', -c['floor_thickness']),
                            ('Nut', 'nut', -c['floor_thickness']-c['lock_thickness'])]:
        install(name+suffix, role, group, App.Placement(App.Vector(x, y, z), rotation))
for group in [v for v in doc.Objects if v.TypeId == 'App::Part']:
    group.Uid = str(uuid.uuid5(uuid.NAMESPACE_URL, 'markviii:rear-support:'+group.Name))
library.Visibility = False
doc.recompute()
saved = out/'RearSupportFamily.FCStd'
doc.saveAs(str(saved))
App.closeDocument(doc.Name)
for file in inputs:
    # Parent/prototype report basenames repeat; preserve their repository paths.
    destination = out/'inputs'/file.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file, destination)
write(out/'report.json', dict(native_file=saved.name, native_sha256=sha(saved),
      parent_native=str(natives['parent'].relative_to(ROOT)),
      parent_native_sha256=sha(natives['parent']),
      prototype_inputs={key: dict(native=str(natives[key].relative_to(ROOT)),
                       native_sha256=sha(natives[key])) for key in ['low', 'high']},
      controls=c, details=details, specs=specs, record_ids=records,
      input_hashes={str(f.relative_to(ROOT)): sha(f) for f in inputs},
      new_physical_occurrences=20, prototype_physical_occurrences=22,
      prototype_definition_count=10, historical_geometry_qualified=False,
      installation_qualified=False, geometry_integrated=False))
print('Saved combined rear support trial:22 occurrences/10 definitions.', flush=True)
