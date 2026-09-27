"""Reconstruct upper jaws in an isolated, explicitly conditional interface pilot."""
import argparse
import copy
import sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_handle_gate_parts import selector

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
c = read(a.controls)
parent = Saved(ROOT / c['parent'])
assert sha(parent.native) == c['parent_native_sha256']
assert read(parent.folder / 'qualification.json')['local_static_checks_passed']
source = ROOT / c['source_review']
assert sha(source) == c['source_review_sha256']
assert all(sha(ROOT / file) == digest for file, digest in read(source)['source_hashes'].items())
prior = read(ROOT / c['context_prototype'] / 'report.json')
details = copy.deepcopy(parent.report['details'])
shapes, specs, properties = {}, {}, {}
for name, spec in prior['specs'].items():
    row = parent.rows[name]
    key = row['definition']
    if key not in shapes:
        shapes[key] = parent.definition(key)
        properties[key] = copy.deepcopy(parent.manifest['definitions'][key]['properties'])
    specs[name] = dict(definition=key, frame=row['frame'], owner=row['owners'][-1], role=spec['role'])

changed = []
for side in ['Port', 'Starboard']:
    for kind, control_key in [('High', 'high_selector_controls'), ('Low', 'selector_controls')]:
        name = side + 'Driver' + kind + 'Selector'
        key = specs[name]['definition']
        shapes[key] = selector(details[control_key], c, side, kind)
        properties[key]['ReconstructionStatus'] = (
            'Conditional tangential drive-wall jaw with radial passage. Journal and lower linkage '
            'preserved; full operating-handle engagement and historical form remain unqualified.')
        properties[key]['ParameterUpdate'] = 'Regenerate trial_driver_handle_gates.py from handle_gate_controls01.json'
        changed.append(key)

details['handle_gate_controls'] = c
details['scope'] = ('Only four upper selector jaws revised. No new physical occurrences. '
                    'Conditional interface pilot; operating handles, fulcrums and hardware unfinished.')
inputs = [Path(__file__), a.controls, source, ROOT / c['context_prototype'] / 'report.json',
          parent.folder / 'report.json', parent.folder / 'isolated/manifest.json']
inputs += sorted({Path(m.__file__).resolve() for m in list(sys.modules.values())
                  if getattr(m, '__file__', None) and Path(m.__file__).resolve().parent == H
                  and str(m.__file__).endswith('.py')})
trial(a.output, parent, shapes, specs, properties, details, inputs, changed_definitions=changed)
print('Saved four conditional upper-jaw revisions; complete handle validation pending.', flush=True)
