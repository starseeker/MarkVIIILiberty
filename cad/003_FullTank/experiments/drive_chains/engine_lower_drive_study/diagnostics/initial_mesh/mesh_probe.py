"""Probe the real saved crank bevel against its lower 22-tooth mate.

Temporary geometric experiment, not an accepted assembly or historical dimension.
"""
import hashlib
import json
from pathlib import Path
import sys
import time
import FreeCAD as App
import Part

REPO = Path('/home/cyapp/MarkVIIILiberty')
STAGE = REPO / 'cad/003_FullTank'
HELPERS = STAGE / 'experiments/drive_chains'
sys.path[:0] = [str(STAGE), str(HELPERS)]
from lib.cad_build import leaves
from transmission_bevel_tooth import tooth, repeated_teeth
from transmission_core_parts import revolve

OUT = Path(__file__).resolve().parent / 'mesh_probe'
OUT.mkdir(exist_ok=True)
PARENT = HELPERS / 'engine_gear_build'
native = PARENT / 'DrivetrainWithEngineGear.FCStd'
report = json.loads((PARENT / 'report.json').read_text())
assert hashlib.sha256(native.read_bytes()).hexdigest() == report['native_sha256']
V = App.Vector
origin = V(report['datums']['gear_apex'], 0, 0)
c = report['controls']
doc = App.openDocument(str(native))
try:
    items = {i['id']: i for i in leaves(doc.Root)}
    inverse = doc.TankLibertyEngine.getGlobalPlacement().inverse()
    def local(name):
        s = items[name]['shape'].copy()
        s.Placement = inverse.multiply(s.Placement)
        return s
    main = local('EngineGear_DrivingBevel')
    cases = {n: local(n) for n in ['EngineCase_upper', 'EngineCase_lower']}
    single, td = tooth(22, 33, 25.4/c['module'], 25.4/c['module'],
                       c['face_width'], c['pressure_angle_deg'], c['tooth_thinning'], c['flank_samples'])
    ro, yo = td['root_radial_axial_outer_mm']
    ri, yi = td['root_radial_axial_inner_mm']
    # Root disk with a short central shaft tail: full lower shaft follows later.
    blank = revolve([(0, yi-.1), (ri, yi-.1), (ro, yo-.1),
                     (ro, yo+.1), (16, yo+.1), (16, yo+3), (0, yo+3)])
    observations = []
    for phase in [0, 180/22]:
        pinion = blank.multiFuse(repeated_teeth(single, 22, phase))
        assert pinion.isValid() and len(pinion.Solids) == 1
        pinion.rotate(V(), V(1, 0, 0), -90)
        pinion.translate(origin)
        tag = 'centered' if phase == 0 else 'half_tooth'
        pinion.exportBrep(str(OUT / (tag+'.brep')))
        case_contacts = {name: pinion.common(s).Volume for name, s in cases.items()}
        for theta in [0, 360/33/4, 360/33/2]:
            a, b = main.copy(), pinion.copy()
            a.rotate(origin, V(1, 0, 0), theta)
            b.rotate(origin, V(0, 0, 1), -33/22*theta)
            start = time.time()
            volume = a.common(b).Volume
            gap = a.distToShape(b)[0] if volume < 1e-5 else None
            row = dict(phase_deg=phase, main_angle_deg=theta, pinion_angle_deg=-33/22*theta,
                       overlap_mm3=volume, minimum_gap_mm=gap, elapsed_s=time.time()-start)
            observations.append(row)
            print(json.dumps(row), flush=True)
            (OUT / 'progress.json').write_text(json.dumps(observations, indent=2))
        print(json.dumps(dict(phase=phase, case_overlaps=case_contacts)), flush=True)
    main.exportBrep(str(OUT / 'saved_main.brep'))
    for name, s in cases.items():
        s.exportBrep(str(OUT / (name+'.brep')))
    result = dict(parent_sha256=report['native_sha256'], gear_apex=list(origin),
                  pinion_tooth=td, samples=observations, case_overlaps=case_contacts,
                  scope='Mesh/envelope probe only; no accepted new assembly or parameter qualification.')
    (OUT / 'result.json').write_text(json.dumps(result, indent=2)+'\n')
finally:
    App.closeDocument(doc.Name)
