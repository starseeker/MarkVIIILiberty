"""Review saved engine and transmission support registration without changing physical parts."""
import argparse
import base64
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
assert checks['local_frame_checks_passed'] and checks['native_sha256'] == r['native_sha256']

import FreeCAD as App
import Part
from lib.cad_build import COLORS
from lib.visual_review import shaded

COLORS.update(TrialChain=(.58, .61, .58), TrialEngine=(.43, .60, .52),
              TrialTransmission=(.57, .62, .69), TrialSupports=(.72, .55, .35),
              TrialOil=(.75, .65, .42), TrialWater=(.42, .65, .75),
              TrialFasteners=(.80,.66,.36), TrialLargeGear=(.74, .64, .40), TrialSmallGear=(.45, .62, .70))
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
transmission_mounts = []
mount_detail = []
oil_names = {'EngineOilPump_LowerBody', 'EngineOilPump_UpperBody', 'EngineOilPump_BottomCover'}
water_names = {'EngineWaterPump_BodyCasting', 'EngineWaterPump_InletCover'}
assert (oil_names | water_names).issubset(rows)
for name, row in rows.items():
    owners = set(row['owners'])
    role = None
    if 'TransmissionCaseMounting' in owners:
        role = 'TrialFasteners'
    elif name.startswith(('PortChain_', 'StarboardChain_')):
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
        if 'TransmissionMountingFrame' in owners or 'TransmissionCaseMounting' in owners or name.endswith(('FixedBearing_inner_bracket','FixedBearing_outer_bracket','TransmissionCore_bevel_case')):
            transmission_mounts.append(obj)
        if 'TransmissionCaseMounting' in owners or name in ['CenterTransmissionCore_bevel_case', 'TransmissionFrame_TopChannel', 'TransmissionFrame_BottomChannel']:
            mount_detail.append(obj)
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
    ('isometric', solids, context, (.65, -1, .55), 'Powertrain development | engine and transmission supports rebuilt; casing/installation work remains'),
    ('transmission_supports', transmission_mounts, [], (1, -1, .5), 'Transmission supports | retained frame, rebuilt cast webs and MX5 joints'),
    ('case_mounting', mount_detail, [], (-1, -.65, .5), 'Central case mounting | four source-length MX5 stud sets at retained channel seats'),
]
for name, selected, outlined, direction, title in views:
    if name == 'case_mounting':
        selected = [dict(v) for v in selected]
        clip = Part.makeBox(1000, 470, 1000, App.Vector(1300, -235, 450))
        for obj in selected:
            if obj['id'].startswith('TransmissionFrame_'):
                obj['shape'] = obj['shape'].common(clip)
    shaded(selected, out / (name + '.svg'), direction, title, context=outlined)
    print('Rendered', name, flush=True)

# Project actual case sections through the prior independent local calibration.
# Retain the source pixels; no fitting of the image to the new geometry.
cal = read(HERE / 'transmission_input_calibration.json')
source = STAGE.parents[1] / cal['image']
assert sha(source) == cal['image_sha256']
origin = App.Vector(*r['shaft_axis_mm'])
plane = Part.makePlane(1200, 1200, origin + App.Vector(-600, 118, -600), App.Vector(0, 1, 0))
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1094" height="1020">',
       '<rect width="1094" height="1020" fill="white"/>',
       '<image width="1094" height="921" opacity=".60" href="data:image/png;base64,' + base64.b64encode(source.read_bytes()).decode() + '"/>']
old_manifest = read((STAGE.parents[1] / r['source_native']).parent / 'isolated/manifest.json')
old_row = next(v for v in old_manifest['occurrences'] if v['name']=='CenterTransmissionCore_bevel_case')
old_def = old_manifest['definitions'][old_row['definition']]
old_shape = Part.Shape()
assert sha(Path(old_def['brep_path'])) == old_def['brep_sha256']
old_shape.read(old_def['brep_path'])
old_shape.Placement = App.Placement(App.Matrix(*old_row['frame']))
projections = [('previous_case', old_shape, '#b83d37'),
               ('revised_case', item('CenterTransmissionCore_bevel_case','TrialTransmission')['shape'], '#1466b5')]
for name in ['TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel']:
    projections.append((name,item(name,'TrialSupports')['shape'],'#41504b'))
for label, shape, color in projections:
    for edge in shape.section(plane).Edges:
        points = ' '.join(f'{cal["origin_px"][0]-(v.x-origin.x)/cal["mm_per_pixel"]:.3f},{cal["origin_px"][1]-(v.z-origin.z)/cal["mm_per_pixel"]:.3f}'
                          for v in edge.discretize(Deflection=.3))
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.3"/>')
svg += ['<text x="20" y="946" font-family="sans-serif" font-size="17">SNL23: previous case red; revised case blue; retained frame gray. Actual Y118 sections.</text>',
        '<text x="20" y="970" font-family="sans-serif" font-size="17">Prior local bearing calibration retained. Frame height and casting silhouette remain conditional.</text>',
        '<text x="20" y="994" font-family="sans-serif" font-size="17">Mechanical fit does not establish the historical station or resolve the source disagreements.</text></svg>']
(out / 'source_frame_comparison.svg').write_text('\n'.join(svg))
import fitz
with fitz.open(stream=(out/'source_frame_comparison.svg').read_bytes(),filetype='svg') as drawing:
    drawing[0].get_pixmap().save(str(out/'source_frame_comparison.png'))
write(out / 'render_receipt.json', dict(native_sha256=r['native_sha256'],
    manifest_sha256=sha(out / 'isolated/manifest.json'), renderer_sha256=sha(Path(__file__)),
    views={name: dict(solids=[v['id'] for v in selected], outlines=[v['id'] for v in outlined])
           for name, selected, outlined, direction, title in views},
    images={f.name: sha(f) for f in out.glob('*.png')},
    source='Actual saved native BReps and composed frames; detail channels cropped and source case sections for display only. No exploded placements or saved physical cuts.',
    source_image_sha256=sha(source), source_calibration_sha256=sha(HERE/'transmission_input_calibration.json'),
    installation_qualified=False, historical_station_qualified=False))
