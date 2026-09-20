"""Render bar-aligned oil-passage sections from the saved chain-detail native file."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', type=Path, required=True)
parser.add_argument('--candidate', type=Path, default=ROOT / 'chain_detail_build')
parser.add_argument('--worker', action='store_true')
args = parser.parse_args()
stage, candidate = args.stage.resolve(), args.candidate.resolve()
out = candidate / 'oil_sections'
sys.path.insert(0, str(stage))
from lib import runtime
from lib.evidence import read, write, sha

if not args.worker:
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'run.log').open('w') as log:
        sys.exit(subprocess.run([
            sys.executable, __file__, '--stage', str(stage), '--candidate', str(candidate), '--worker'
        ], env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode)

try:
    App, Gui = runtime.start_gui()
    import Part
    from types import SimpleNamespace
    from lib.cad_build import leaves
    from lib.visual_review import shaded

    native = candidate / 'ChainDetailCandidate.FCStd'
    report_path = candidate / 'report.json'
    native_hash, report_hash, script_hash = sha(native), sha(report_path), sha(Path(__file__))
    report = read(report_path)
    assert report['passed'] and report['native_sha256'] == native_hash
    doc = App.openDocument(str(native))
    doc.recompute()
    items = leaves(doc.Root)
    pin = next(i for i in items if i['id'] == 'PortChain_Joint00_Pin')
    inputs = candidate / 'inputs'
    a = {k: v['value'] for k, v in read(inputs / 'chain_candidate_controls.json')['controls'].items()}
    views = {}
    for key, occurrence, stock_key, bore_x in [
        ('inner', 'PortChain_Link00_Inboard', 'inner_stock', 0),
        ('outer', 'PortChain_Link49_Inboard', 'outer_stock', a['pitch']),
    ]:
        bar = next(i for i in items if i['id'] == occurrence)
        pose = bar['shape'].Placement.multiply(bar['target'].Shape.Placement.inverse())
        stock = a[stock_key]
        crop = Part.makeBox(.6, stock + 4, 12.5,
                            App.Vector(bore_x - .3, -stock / 2 - 2, -a['bar_end_radius'] - 1))
        cut_items = []
        for item in [bar, pin]:
            shape = item['shape'].copy()
            shape.Placement = pose.inverse().multiply(shape.Placement)
            shape = shape.common(crop)
            assert not shape.isNull() and shape.isValid()
            shape.translate(App.Vector(-bore_x, 0, 0))
            shape.rotate(App.Vector(), App.Vector(1, 0, 0), 180)
            cut_items.append(dict(item, shape=shape, target=SimpleNamespace(Shape=shape),
                                  definition=item['id'] + '_oil_section'))
        name = key + '_bar_oil_section'
        shaded(cut_items, out / (name + '.svg'), (1, 0, 0),
               key.capitalize() + ' bar | inferred oil passage reaches pin clearance; bar-aligned native section',
               canvas=(1200, 900))
        views[name + '.png'] = sha(out / (name + '.png'))
    assert sha(native) == native_hash and sha(report_path) == report_hash and sha(Path(__file__)) == script_hash
    write(out / 'render_receipt.json', dict(
        complete=True, native_sha256=native_hash, candidate_report_sha256=report_hash,
        script_sha256=script_hash, images=views, native_modified=False,
        interpretation='Separate local sections align with each bar. The curved-joint overview is oblique to the oil paths.',
        visual_review_status='pending'))
finally:
    runtime.close()
