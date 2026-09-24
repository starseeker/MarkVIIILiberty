"""Render saved MX1 joints and a qualitative comparison with the handbook photograph."""
import argparse
import base64
from pathlib import Path
import sys
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
import FreeCAD as App
import Part
import fitz
from lib.cad_build import COLORS
from lib.visual_review import shaded
COLORS.update(TrialCasing=(.47,.58,.44),TrialEngine=(.43,.60,.52),
    TrialTransmission=(.57,.62,.69),TrialSupports=(.72,.55,.35),TrialFasteners=(.85,.68,.32),
    TrialOil=(.75,.65,.42),TrialWater=(.42,.65,.75))
rows={v['name']:v for v in m['occurrences']};cache={}
def item(name,role):
    row=rows[name];key=row['definition']
    if key not in cache:
        d=m['definitions'][key];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
solids=[];context=[];transmission=[];mounts=[]
for name,row in rows.items():
    owners=set(row['owners']);role=None
    fastening=name in r['expected_new_occurrences'] or 'TransmissionCaseMounting' in owners
    if fastening:role='TrialFasteners'
    elif name.startswith(('PortCasing','StarboardCasing')):role='TrialCasing'
    elif name.startswith(('EngineCase_','EngineCrankcase_')):role='TrialEngine'
    elif name in ['EngineOilPump_LowerBody','EngineOilPump_UpperBody','EngineOilPump_BottomCover']:role='TrialOil'
    elif name in ['EngineWaterPump_BodyCasting','EngineWaterPump_InletCover']:role='TrialWater'
    elif 'TransmissionMountingFrame' in owners or 'EngineMounts' in owners:role='TrialSupports'
    elif name.endswith(('FixedBearing_inner_bracket','FixedBearing_outer_bracket')):role='TrialSupports'
    elif 'FixedTransmissionBearings' in owners or name.startswith(('PortTransmissionOutput_','StarboardTransmissionOutput_')):role='TrialTransmission'
    elif name.endswith(('TransmissionCore_bevel_case','TransmissionCore_bevel_cover','TransmissionCore_brake_case','TransmissionCore_plain_case')):role='TrialTransmission'
    elif owners.intersection({'FrontClutch','ClutchStack','ClutchOuterDrumAssembly','InputHousingAssembly','EngineFlywheelAssembly'}):role='TrialTransmission'
    if role:
        obj=item(name,role);solids.append(obj)
        if ('FixedTransmissionBearings' in owners or 'TransmissionMountingFrame' in owners or 'InputHousingAssembly' in owners
            or 'TransmissionCaseMounting' in owners or name.startswith(('PortTransmissionOutput_','StarboardTransmissionOutput_'))
            or name.endswith(('TransmissionCore_bevel_case','TransmissionCore_bevel_cover','TransmissionCore_brake_case','TransmissionCore_plain_case'))):
            transmission.append(obj)
        if name in r['affected_occurrences'] or 'TransmissionCaseMounting' in owners:
            mounts.append(obj)
    if name in ['hull_floor_5','hull_floor_6','hull_floor_7']:context.append(item(name,'TrialSupports'))
detail=[]
clip=Part.makeBox(500,680,900,App.Vector(1400,540,480))
for obj in mounts:
    if obj['id'].startswith(('PortInner','PortOuter')) or obj['id'] in ['PortFixedBearing_inner_bracket','PortFixedBearing_outer_bracket']:
        detail.append(obj)
    elif obj['id'].startswith('TransmissionFrame_'):
        shape=obj['shape'].common(clip)
        detail.append(dict(obj,shape=shape,target=SimpleNamespace(Shape=shape),definition=obj['id']+'_display_crop'))
views=[
    ('isometric',solids,context,(.65,-1,.55),'Powertrain development | twenty MX1 bracket joints added; mounting geometry remains provisional'),
    ('bracket_joints',detail,[],(-1,-.6,.65),'Bracket mounting detail | castle nuts, bevel washers and 1.5-inch split pins'),
    ('transmission_photo_view',transmission,[],(.35,.015,1),'Transmission removed-unit comparison | forward input axis shown upward, as in HB126 Plate79'),
]
for name,selected,outlined,direction,title in views:
    # The removed unit in Plate79 rests on its rear mounting frame: its input
    # axis points upward in the photograph. This is a camera orientation only;
    # every saved occurrence stays in its standard installed frame.
    up=(1,0,0) if name=='transmission_photo_view' else (0,0,1)
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined,up_direction=up)
    print('Rendered',name,flush=True)
source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate79.png'
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1750">',
     '<rect width="1600" height="1750" fill="white"/>',
     '<text x="40" y="38" font-family="sans-serif" font-size="24">HB126 Plate79 | removed transmission photograph; qualitative comparison</text>',
     '<image x="100" y="60" width="1400" height="700" href="data:image/png;base64,'+base64.b64encode(source.read_bytes()).decode()+'"/>',
     '<image x="0" y="790" width="1600" height="900" href="data:image/png;base64,'+base64.b64encode((out/'transmission_photo_view.png').read_bytes()).decode()+'"/>',
     '<text x="40" y="1720" font-family="sans-serif" font-size="21">Camera direction chosen for visibility; no metric calibration or fit. Hidden fastener pattern remains inferred.</text></svg>']
(out/'source_bracket_comparison.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'source_bracket_comparison.svg').read_bytes(),filetype='svg') as doc:
    doc[0].get_pixmap().save(str(out/'source_bracket_comparison.png'))
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],manifest_sha256=sha(out/'isolated/manifest.json'),
    renderer_sha256=sha(Path(__file__)),source_image=str(source.relative_to(ROOT)),source_image_sha256=sha(source),
    images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','bracket_joints','transmission_photo_view','source_bracket_comparison']},
    views={name:dict(direction=direction,up_direction=(1,0,0) if name=='transmission_photo_view' else (0,0,1),
                    solid_ids=[v['id'] for v in selected],context_ids=[v['id'] for v in outlined])
           for name,selected,outlined,direction,title in views},display_only_channel_crop=True,
    source_comparison='Qualitative photograph; input-axis-up camera follows the removed-unit orientation. No metric calibration or source/CAD fit; no occurrence placements changed.',
    historical_joint_layout_qualified=False,installation_qualified=False))
