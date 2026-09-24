"""Test optional topology cleanup on copies; retain original and failed transfer."""
import hashlib
import json
from pathlib import Path
import sys
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]
H = ROOT / 'cad/003_FullTank/experiments/drive_chains'
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha
from lib.mass_properties import AdaptiveMass

trial = H / 'transmission_brake_stop_study/trial04'
out = trial / 'diagnostics/lug_step'
out.mkdir(parents=True, exist_ok=True)
m = read(trial / 'isolated/manifest.json')
rec = m['definitions']['Def_BrakeStop_track_lug']
assert sha(Path(rec['brep_path'])) == rec['brep_sha256']
original = Part.Shape(); original.read(rec['brep_path'])
mass = AdaptiveMass(out / 'mass_runtime')
Part.setStaticValue('write.surfacecurve.mode', 1)
def fingerprint(s): return hashlib.sha256(s.exportBrepToString().encode()).hexdigest()
before = fingerprint(original)
variants = {'original': original.copy(), 'unified_copy': original.copy().removeSplitter()}
assert fingerprint(original) == before
records = []
rows = {row['name']: row for row in m['occurrences']}
for name, candidate in variants.items():
    candidate.exportBrep(str(out / (name+'.brep')))
    valid = candidate.isValid() and len(candidate.Solids) == 1 and candidate.isClosed()
    missing, added = original.cut(candidate), candidate.cut(original)
    record = dict(variant=name, valid=valid, source_preserved=not missing.Faces and not added.Faces,
                  missing_mm3=missing.Volume, added_mm3=added.Volume,
                  missing_faces=len(missing.Faces), added_faces=len(added.Faces),
                  native_tolerance_mm=candidate.getTolerance(1), comparisons=[])
    if valid:
        for installed in (None, 'PortTrackBrakeStopLug', 'StarboardTrackBrakeStopLug'):
            s = candidate.copy()
            if installed: s.Placement = App.Placement(App.Matrix(*rows[installed]['frame']))
            filename = name+'_'+(installed or 'definition')+'.step'
            s.exportStep(str(out / filename))
            imported = Part.Shape(); imported.read(str(out / filename))
            ta, tb = s.getTolerance(1), imported.getTolerance(1)
            missing, added = s.cut(imported), imported.cut(s)
            fuzzy = min(1e-4, max(1e-7, ta+tb))
            fm, fa = len(s.cut(imported, fuzzy).Faces), len(imported.cut(s, fuzzy).Faces)
            ma, mb = mass.measure(s), mass.measure(imported)
            error = (App.Vector(*ma['centroid_mm'])-App.Vector(*mb['centroid_mm'])).Length
            passed = (imported.isValid() and len(imported.Solids) == 1 and imported.isClosed()
                      and abs(missing.Volume) < 1e-5 and abs(added.Volume) < 1e-5 and not fm and not fa
                      and ta <= 1e-4 and tb <= max(ta, 1e-7)+1e-10
                      and ma['converged'] and mb['converged'] and error < 1e-5)
            row = dict(installed=installed, native_tolerance_mm=ta, step_tolerance_mm=tb,
                       missing_mm3=missing.Volume, added_mm3=added.Volume,
                       fuzzy_missing_faces=fm, fuzzy_added_faces=fa,
                       native_mass=ma, step_mass=mb, adaptive_centroid_error_mm=error, passed=passed)
            record['comparisons'].append(row)
            print(name, installed, passed, ta, tb, flush=True)
    records.append(record)
    write(out / 'results.json', dict(source_native_sha256=m['native_sha256'],
          source_brep_sha256=rec['brep_sha256'], script_sha256=sha(Path(__file__)),
          original_unchanged=fingerprint(original) == before, variants=records))
