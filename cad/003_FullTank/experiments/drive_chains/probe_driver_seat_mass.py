"""Diagnose the saved seat splines with the existing independent integrator."""
import argparse
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from control_rebuild_surface_mass_v5 import TrimmedSurfaceMassV5

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=False)
m = read(a.candidate / 'isolated/manifest.json')
proof_path = H / 'transmission_controls_study/redo01/diagnostics/trimmed_mass01/qualification.json'
proof = read(proof_path)
assert proof['passed']
for key, name in [('adapter_sha256', 'control_rebuild_surface_mass_v5.py'),
                  ('source_sha256', 'control_rebuild_surface_mass_v5.cpp')]:
    assert proof['provenance'][key] == sha(H / name)
mass = TrimmedSurfaceMassV5(a.output / 'runtime')
rows = []
for name in ['Def_DriverSeat_Frame', 'Def_DriverSeat_BackPadding']:
    entry = m['definitions'][name]
    assert sha(Path(entry['brep_path'])) == entry['brep_sha256']
    shape = Part.Shape()
    shape.read(entry['brep_path'])
    result = mass.measure(shape)
    rows.append(dict(name=name, measurement=result))
    write(a.output / 'progress.json', rows)
    print(name, result['converged'], result['volume_convergence_mm3'], flush=True)
write(a.output / 'report.json', dict(
    passed=all(v['measurement']['converged'] for v in rows),
    native_sha256=m['native_sha256'], checker_sha256=sha(Path(__file__)),
    analytic_controls_sha256=sha(proof_path), provenance=mass.provenance, checks=rows))
