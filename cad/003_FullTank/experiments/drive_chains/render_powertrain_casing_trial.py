"""Render rebuilt casings, dependent joints and fixed-calibration source comparison."""
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
assert checks['local_casing_checks_passed'] and checks['native_sha256'] == r['native_sha256']

import FreeCAD as App
import Part
from lib.cad_build import COLORS
from lib.visual_review import shaded

COLORS.update(TrialCasing=(.58,.66,.56), TrialChain=(.58, .61, .58), TrialEngine=(.43, .60, .52),
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
    if name.startswith(('PortCasing','StarboardCasing')):
        role = 'TrialCasing'
    elif 'TransmissionCaseMounting' in owners:
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
    if name.startswith('PortPlanetTrain_') and name.split('_', 1)[1] in ['sun', 'ring', 'planet0', 'planet1', 'planet2']:
        gears.append(item(name, 'TrialLargeGear'))
    elif name.startswith('PortSmallPlanetTrain_') and name.split('_', 1)[1] in ['sun', 'ring', 'planet0', 'planet1', 'planet2']:
        gears.append(item(name, 'TrialSmallGear'))
    if name in ['PortTransmissionCore_planet_disk', 'PortTransmissionCore_plain_case']:
        gear_context.append(item(name, 'TrialTransmission'))
assert len(gears) == 10
port = [item(name,'TrialCasing') for name in rows if name.startswith('PortCasing')]
chains = [item(name,'TrialChain') for name in rows if name.startswith('PortChain_')]
transmission = [item(name,'TrialTransmission') for name in rows if
    name.startswith('PortTransmissionOutput_') or name in
    ['PortFixedBearing_inner_bracket','PortFixedBearing_outer_bracket']]
cy = r['centers']['Port']
cut_tool = Part.makeBox(6000,4000,5000,App.Vector(-1000,cy,-1000))
section = []
for obj in port:
    if obj['id'] in ['PortCasing_Body','PortCasing_Cap']:
        shape = obj['shape'].cut(cut_tool)
        section.append(dict(obj,shape=shape,target=SimpleNamespace(Shape=shape),definition=obj['id']+'_display_section'))
    elif obj['shape'].BoundBox.YMax < cy:
        section.append(obj)
views = [
    ('isometric',solids,context,(.65,-1,.55),'Powertrain development | constant-stock casings regenerated around the revised chain route'),
    ('casing_section',section+chains+transmission,[],(1,1,.55),'Port casing section | separate chain, rivets and supports; physical parts remain uncut'),
    ('casing_joints',port,[],(-1,-1,.6),'Casing assembly | rebuilt collar and cap cleats; retained seam trim and hull supports'),
]
for name,selected,outlined,direction,title in views:
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined)
    print('Rendered',name,flush=True)

from lib.model import load,point
import fitz
model=load()
cal=model['calibrations']['snl_2']
source=STAGE.parents[1]/cal['image']
ox,oz=point(model,'snl_2',[0,0]);x1,z1=point(model,'snl_2',[1,1]);sx,sz=x1-ox,z1-oz
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="1320 300 430 268.75">',
     '<rect x="1320" y="300" width="430" height="268.75" fill="white"/>',
     '<image width="1900" height="750" opacity=".65" href="data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()+'"/>']
old_manifest=read((STAGE.parents[1]/r['source_native']).parent/'isolated/manifest.json')
old_rows={v['name']:v for v in old_manifest['occurrences']}
for name in ['PortCasing_Body','PortCasing_Cap']:
    row=old_rows[name];rec=old_manifest['definitions'][row['definition']]
    path=Path(rec['brep_path']);assert sha(path)==rec['brep_sha256']
    old=Part.Shape();old.read(str(path));old.Placement=App.Placement(App.Matrix(*row['frame']))
    for s,color in [(old,'#b83d37'),(item(name,'TrialCasing')['shape'],'#1466b5')]:
        # A central longitudinal section shows shell contour without duplicated
        # side-wall holes. The section is display-only and uses actual solids.
        plane=Part.makePlane(2600,2200,App.Vector(0,cy,-100),App.Vector(0,1,0))
        for edge in s.section(plane).Edges:
            pts=' '.join(f'{(v.x-ox)/sx:.3f},{(v.z-oz)/sz:.3f}' for v in edge.discretize(Deflection=.5))
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width=".6"/>')
svg += ['<rect x="1320" y="535" width="430" height="33.75" fill="white"/>',
        '<text x="1324" y="544" font-family="sans-serif" font-size="5.5">SNL2: previous casing red, revised casing blue. Actual central sections.</text>',
        '<text x="1324" y="553" font-family="sans-serif" font-size="5.5">Original global calibration retained; no source fitting. Shaft station remains conditional.</text>',
        '<text x="1324" y="562" font-family="sans-serif" font-size="5.5">Sheet thickness, local taper, cap seam and fastener layout retain documented approximations.</text></svg>']
(out/'source_casing_comparison.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'source_casing_comparison.svg').read_bytes(),filetype='svg') as doc:
    doc[0].get_pixmap().save(str(out/'source_casing_comparison.png'))
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),
    manifest_sha256=sha(out/'isolated/manifest.json'),checks_sha256=sha(out/'independent_checks.json'),
    source_image=str(source.relative_to(STAGE.parents[1])),source_image_sha256=sha(source),
    calibration_sha256=sha(STAGE/'data/calibrations.json'),parameters_sha256=sha(STAGE/'data/parameters.json'),
    model_projection=dict(origin_mm=[ox,oz],mm_per_pixel=[sx,sz],fitting_performed=False),
    images={f.name:sha(f) for f in out.glob('*.png')},
    views={name:dict(solids=[v['id'] for v in selected],outlines=[v['id'] for v in outlined])
           for name,selected,outlined,direction,title in views},
    display_only_sections=True,standard_assembly_modified=False,installation_qualified=False))
