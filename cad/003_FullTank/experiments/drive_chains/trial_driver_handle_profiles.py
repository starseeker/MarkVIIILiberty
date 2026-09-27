"""Save complete-stock handle hypotheses without moving the accepted interfaces."""
import argparse
import copy
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_handle_profile_parts import handle

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--hypothesis', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
packet = read(a.controls)
parent = Saved(ROOT / packet['parent'])
assert sha(parent.native) == packet['parent_native_sha256']
assert read(parent.folder / 'qualification.json')['local_static_checks_passed']
assert all(sha(ROOT / file) == digest for file, digest in packet['source_hashes'].items())
prior = read(ROOT / packet['context_prototype'] / 'report.json')
details = copy.deepcopy(parent.report['details'])
controls = details['operating_controls']
hypothesis = packet['hypotheses'][a.hypothesis]
shapes, specs, props = {}, {}, {}
for name, spec in prior['specs'].items():
    row = parent.rows[name]
    key = row['definition']
    if key not in shapes:
        shapes[key] = parent.definition(key)
        props[key] = copy.deepcopy(parent.manifest['definitions'][key]['properties'])
    specs[name] = dict(definition=key, frame=row['frame'], owner=row['owners'][-1], role=spec['role'])
changed, dimensions = [], {}
for side in ['Port', 'Starboard']:
    key = specs[side + 'DriverOperatingHandle']['definition']
    shapes[key], dimensions[side] = handle(controls, hypothesis, side)
    props[key]['ReconstructionStatus'] = ('Unqualified complete-stock handle hypothesis: '
        + hypothesis['length_datum'] + '. Printed 37-inch datum unresolved. '
        'Upper blade/grip rebuilt; lower heel, joint and occurrence frame preserved. '
        'Do not integrate without source, context, exchange and independent geometry checks.')
    props[key]['ParameterUpdate'] = 'Regenerate trial_driver_handle_profiles.py with handle_profile_controls01.json and hypothesis ' + a.hypothesis
    changed.append(key)
details['handle_profile_hypothesis'] = dict(name=a.hypothesis, controls=hypothesis, dimensions=dimensions)
details['scope'] = 'Two revised full handle definitions; no added parts or changed frames. Diagnostic only.'
inputs = [Path(__file__), H / 'driver_handle_profile_parts.py', H / 'driver_operating_handle_parts_v2.py',
          H / 'control_rebuild_io_v2.py', a.controls, parent.folder / 'report.json',
          parent.folder / 'isolated/manifest.json', ROOT / packet['context_prototype'] / 'report.json']
inputs += [ROOT / f for f in packet['source_hashes']]
trial(a.output, parent, shapes, specs, props, details, inputs, changed_definitions=changed)
print('Saved complete handle hypothesis', a.hypothesis, dimensions['Port'], flush=True)
