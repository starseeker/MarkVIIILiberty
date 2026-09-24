"""Review saved planetary and support corrections without changing physical parts."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
sys.path[:0] = [str(HERE), str(STAGE)]
from lib.evidence import read, write, sha

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
r = read(out / 'report.json')
m = read(out / 'isolated/manifest.json')
assert sha(out / r['native_file']) == r['native_sha256'] == m['native_sha256']
checks = read(out / 'independent_checks.json')
assert checks['local_support_checks_passed'] and checks['native_sha256'] == r['native_sha256']

import FreeCAD as App
import Part
from lib.cad_build import COLORS
from lib.visual_review import shaded

COLORS.update(TrialChain=(.58, .61, .58), TrialEngine=(.43, .60, .52),
              TrialTransmission=(.57, .62, .69), TrialSupports=(.72, .55, .35),
              TrialOil=(.75, .65, .42), TrialWater=(.42, .65, .75),
              TrialLargeGear=(.74, .64, .40), TrialSmallGear=(.45, .62, .70))
rows = {v['name']: v for v in m['occurrences']}
definitions = {}

def item(name, role):
    row = rows[name]
    key = row['definition']
    if key not in definitions:
        d = m['definitions'][key]
        f = Path(d['brep_path'])
        assert sha(f) == d['brep_sha256']
        s = Part.Shape()
        s.read(str(f))
        assert s.Placement.isIdentity()
        definitions[key] = SimpleNamespace(Shape=s)
    target = definitions[key]
    s = target.Shape.copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return dict(id=name, shape=s, target=target, definition=key, system=role, representation='assembly')

solids, context, mounts, floors, gears, gear_context = [], [], [], [], [], []
oil_names = {'EngineOilPump_LowerBody', 'EngineOilPump_UpperBody', 'EngineOilPump_BottomCover'}
water_names = {'EngineWaterPump_BodyCasting', 'EngineWaterPump_InletCover'}
assert (oil_names | water_names).issubset(rows)
for name, row in rows.items():
    owners = set(row['owners'])
    role = None
    if name.startswith(('PortChain_', 'StarboardChain_')):
        role = 'TrialChain'
    elif name.startswith(('EngineCase_', 'EngineCrankcase_')):
        role = 'TrialEngine'
    elif owners.intersection({'FrontClutch', 'ClutchStack', 'ClutchOuterDrumAssembly',
                             'InputHousingAssembly', 'EngineFlywheelAssembly'}):
        role = 'TrialTransmission'
    elif name.startswith(('PortTransmissionOutput_', 'StarboardTransmissionOutput_')) or name.endswith(
            ('TransmissionCore_bevel_case', 'TransmissionCore_brake_case', 'TransmissionCore_plain_case')):
        role = 'TrialTransmission'
    elif 'TransmissionMountingFrame' in owners or 'EngineMounts' in owners or name in [
            'PortFixedBearing_inner_bracket', 'PortFixedBearing_outer_bracket',
            'StarboardFixedBearing_inner_bracket', 'StarboardFixedBearing_outer_bracket']:
        role = 'TrialSupports'
    elif name in oil_names:
        role = 'TrialOil'
    elif name in water_names:
        role = 'TrialWater'
    if role:
        obj = item(name, role)
        solids.append(obj)
        if 'EngineMounts' in owners or role in {'TrialEngine', 'TrialOil', 'TrialWater'}:
            mounts.append(obj)
    if name in ['hull_floor_5', 'hull_floor_6', 'hull_floor_7']:
        obj = item(name, 'TrialSupports')
        context.append(obj)
        floors.append(obj)
    elif name in ['PortCasing_Body', 'PortCasing_Cap', 'StarboardCasing_Body', 'StarboardCasing_Cap']:
        context.append(item(name, 'TrialSupports'))
    if name.startswith('PortPlanetTrain_') and name.split('_', 1)[1] in ['sun', 'ring', 'planet0', 'planet1', 'planet2']:
        gears.append(item(name, 'TrialLargeGear'))
    elif name.startswith('PortSmallPlanetTrain_') and name.split('_', 1)[1] in ['sun', 'ring', 'planet0', 'planet1', 'planet2']:
        gears.append(item(name, 'TrialSmallGear'))
    if name in ['PortTransmissionCore_planet_disk', 'PortTransmissionCore_plain_case']:
        gear_context.append(item(name, 'TrialTransmission'))
assert len(gears) == 10
views = [
    ('isometric', solids, context, (.65, -1, .55), 'Powertrain development | coupled phases and engine supports; casing/frame work remains'),
    ('engine_supports', mounts, floors, (.5, -1, .6), 'Rebuilt engine supports | fixed floor receivers, raised mounting plane'),
    ('planetary_phases', gears, gear_context, (.7, 1, .4), 'Two coupled planetary stages | actual saved tooth meshes and carrier locations'),
]
for name, selected, outlined, direction, title in views:
    shaded(selected, out / (name + '.svg'), direction, title, context=outlined)
    print('Rendered', name, flush=True)
write(out / 'render_receipt.json', dict(native_sha256=r['native_sha256'],
    manifest_sha256=sha(out / 'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
    views={name: dict(solids=[v['id'] for v in selected], outlines=[v['id'] for v in outlined])
           for name, selected, outlined, direction, title in views},
    images={f.name: sha(f) for f in out.glob('*.png')},
    source='Selected actual saved native BReps and composed frames; no exploded placements or physical cuts.',
    installation_qualified=False, historical_station_qualified=False))
