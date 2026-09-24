"""Test per-component STEP representations using unchanged saved definitions."""
from pathlib import Path
import sys
import re
import FreeCAD as App
import Part
import Import
ROOT = Path(__file__).resolve().parents[2]
H = ROOT / 'cad/003_FullTank/experiments/drive_chains'
sys.path.insert(0, str(H.parents[1]))
from lib.evidence import read, write, sha
from lib.step_matching import StepSolidMatcher
trial = H / 'transmission_brake_stop_study/trial04'
out = trial / 'diagnostics/step_products'
out.mkdir(parents=True, exist_ok=True)
m = read(trial / 'isolated/manifest.json')
r = read(trial / 'report.json')
shapes = {}
for name in sorted(set(r['new_definitions']) | set(r['changed_definitions'])):
    rec = m['definitions'][name]
    assert sha(Path(rec['brep_path'])) == rec['brep_sha256']
    s = Part.Shape(); s.read(rec['brep_path']); shapes[name] = s
Part.setStaticValue('write.surfacecurve.mode', 1)
results = []
for mode in (1,):
    Part.setStaticValue('write.step.assembly', mode)
    path = out / ('mode'+str(mode)+'.step')
    doc=App.newDocument('StepProductProbe')
    features=[]
    for name,s in shapes.items():
        f=doc.addObject('PartDesign::Feature', name); f.Label=name; f.Shape=s; features.append(f)
    doc.recompute()
    Import.export(features, str(path))
    App.closeDocument(doc.Name)
    imported = Part.Shape(); imported.read(str(path))
    assert imported.isValid() and len(imported.Solids) == len(shapes)
    matcher = StepSolidMatcher(imported.Solids)
    comparisons = []
    for name, one in shapes.items():
        index, two = matcher.pop(one)
        ta, tb = one.getTolerance(1), two.getTolerance(1)
        missing, added = one.cut(two), two.cut(one)
        fuzzy = min(1e-4, max(1e-7, ta+tb))
        fm, fa = len(one.cut(two, fuzzy).Faces), len(two.cut(one, fuzzy).Faces)
        passed = (one.isValid() and two.isValid() and len(two.Solids) == 1
                  and abs(missing.Volume) < 1e-5 and abs(added.Volume) < 1e-5 and not fm and not fa
                  and ta <= 1e-4 and tb <= max(ta, 1e-7)+1e-10)
        comparisons.append(dict(name=name, native_tolerance_mm=ta, step_tolerance_mm=tb,
            missing_mm3=missing.Volume, added_mm3=added.Volume, fuzzy_missing_faces=fm,
            fuzzy_added_faces=fa, passed=passed))
        print(mode, name, passed, ta, tb, flush=True)
    results.append(dict(assembly_mode=mode, comparisons=comparisons,
        uncertainty_mm=re.findall(r'UNCERTAINTY_MEASURE_WITH_UNIT\(LENGTH_MEASURE\(([^)]+)\)', path.read_text()),
        file_sha256=sha(path)))
    write(out / 'results.json', dict(native_sha256=m['native_sha256'],
         script_sha256=sha(Path(__file__)), results=results,
         scope='Material/tolerance diagnostic only; full89 converged mass comparisons still required.'))
