"""Show selected saved diagnostic solids with unchanged casings/floor in outline."""
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

import FreeCAD as App
import Part
from lib.cad_build import COLORS
from lib.visual_review import shaded

COLORS.update(RegistrationChain=(.58, .61, .58), RegistrationEngine=(.43, .60, .52),
              RegistrationTransmission=(.57, .62, .69), RegistrationSupports=(.72, .55, .35),
              RegistrationPump=(.75, .65, .42))
definitions = {}
solids = []
context = []
selected = []
outlines = []
for row in m['occurrences']:
    name = row['name']
    owners = row['owners']
    role = None
    outline = False
    if name.startswith(('PortChain_', 'StarboardChain_')):
        role = 'RegistrationChain'
    elif name.startswith(('EngineCase_', 'EngineCrankcase_')):
        role = 'RegistrationEngine'
    elif set(owners).intersection({'FrontClutch', 'ClutchStack', 'ClutchOuterDrumAssembly',
                                  'InputHousingAssembly', 'EngineFlywheelAssembly'}):
        role = 'RegistrationTransmission'
    elif name.startswith(('PortTransmissionOutput_', 'StarboardTransmissionOutput_')) or name.endswith(
            ('TransmissionCore_bevel_case', 'TransmissionCore_brake_case', 'TransmissionCore_plain_case')):
        role = 'RegistrationTransmission'
    elif 'TransmissionMountingFrame' in owners or name in [
            'EngineSuspension_LeftRail', 'EngineSuspension_RightRail', 'EngineSuspension_FrontBracket',
            'EngineSuspension_LeftBracket', 'EngineSuspension_RightBracket',
            'PortFixedBearing_inner_bracket', 'PortFixedBearing_outer_bracket',
            'StarboardFixedBearing_inner_bracket', 'StarboardFixedBearing_outer_bracket']:
        role = 'RegistrationSupports'
    elif name in ['EngineOilPump_LowerBody', 'EngineOilPump_UpperBody', 'EngineOilPump_BottomCover',
                  'EngineWaterPump_body', 'EngineWaterPump_cover']:
        role = 'RegistrationPump'
    elif name in ['hull_floor_5', 'hull_floor_6', 'hull_floor_7',
                  'PortCasing_Body', 'PortCasing_Cap', 'StarboardCasing_Body', 'StarboardCasing_Cap']:
        role = 'RegistrationSupports'
        outline = True
    if role is None:
        continue
    key = row['definition']
    if key not in definitions:
        definition = m['definitions'][key]
        f = Path(definition['brep_path'])
        assert sha(f) == definition['brep_sha256']
        s = Part.Shape()
        s.read(str(f))
        assert s.Placement.isIdentity()
        definitions[key] = SimpleNamespace(Shape=s)
    target = definitions[key]
    placed = target.Shape.copy()
    placed.Placement = App.Placement(App.Matrix(*row['frame']))
    item = dict(id=name, target=target, shape=placed, definition=key,
                system=role, representation='assembly')
    (context if outline else solids).append(item)
    (outlines if outline else selected).append(name)

shaded(solids, out / 'isometric.svg', (.65, -1, .55),
       'Placement diagnostic, selected solids | support and casing interfaces unresolved', context=context)
port = [v for v in solids if v['id'].startswith(('PortChain_', 'PortTransmissionOutput_'))]
port_case = [v for v in context if v['id'].startswith('PortCasing_')]
shaded(port, out / 'chain_elevation.svg', (0, 1, 0),
       'Reclosed port chain | outline shows obsolete casing location', context=port_case)
write(out / 'render_receipt.json', dict(native_sha256=r['native_sha256'],
    manifest_sha256=sha(out / 'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
    solid_occurrences=selected, outline_occurrences=outlines,
    images={f.name: sha(f) for f in out.glob('*.png')},
    purpose='Selected actual saved solids for placement review; omitted internals remain in native document.',
    installation_qualified=False, historical_station_qualified=False))
