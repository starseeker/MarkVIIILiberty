"""Saved rear-anchor and support views with source overlays; display changes only."""
import argparse
import base64
from pathlib import Path
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
import FreeCAD as App
import Part
import fitz
from lib.cad_build import COLORS
from lib.visual_review import shaded
COLORS.update(Anchor=(.64,.48,.26),Spring=(.38,.66,.70),Steel=(.55,.60,.65),Link=(.75,.48,.24),Pin=(.72,.76,.8),Band=(.42,.50,.57),Lining=(.6,.46,.32),Copper=(.83,.48,.27),Frame=(.63,.55,.41),BrakeSupport=(.85,.55,.24),BrakeStop=(.42,.66,.72),Bearing=(.51,.59,.68))
rows={v['name']:v for v in m['occurrences']};cache={}
def item(name,role):
    row=rows[name];key=row['definition']
    if key not in cache:
        d=m['definitions'][key];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
frame=[];brakes=[];links=[]
for name,row in rows.items():
    if name in r['affected_occurrences'] or name.endswith(('SuspensionLink','SuspensionPin')) or 'SuspensionCotter' in name:
        role='Link' if name.endswith('SuspensionLink') else 'Anchor' if name.endswith('AnchorBracket') else 'Spring' if name.endswith('RetainerSpring') else 'Band' if name.endswith('Band') else 'Lining' if name.endswith('Lining') else 'Copper' if 'Segment' in name and 'Rivet' in name else 'Steel'
        links.append(item(name,role))
    elif 'TransmissionMountingFrame' in row['owners']:frame.append(item(name,'Frame'))
    elif 'TransmissionBrakeBands' in row['owners'] or name.endswith(('TransmissionOutput_drum','TransmissionCore_brake_case')):
        role='Copper' if 'Rivet' in name else 'Lining' if name.endswith('Lining') else 'Band' if name.endswith('Band') else 'Bearing'
        brakes.append(item(name,role))
clip=Part.makeBox(165,455,190,App.Vector(1435,395,815));detail=[];detail_context=[]
for selected,collection in [(links,detail),(frame+brakes,detail_context)]:
    for obj in selected:
        shape=obj['shape'].common(clip)
        if shape.Faces:collection.append(dict(obj,shape=shape,target=SimpleNamespace(Shape=shape),definition=obj['id']+'_display_crop'))
views=[('isometric',brakes+links,frame,(1,-.8,.55),'Transmission brakes | eight rear brackets and four retained anchor pins; front controls pending'),
       ('anchor_detail',detail,detail_context,(1,-1,.35),'Rear-anchor detail | interleaved lugs, riveted feet, extended lining rivets and outboard retainers'),
       ('anchor_back',detail,detail_context,(-1,1,.35),'Rear-anchor outer faces | steel upset heads, longer copper rivets and retaining springs')]
for name,selected,outlined,direction,title in views:
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined)
    print('Rendered',name,flush=True)
top=rows['TransmissionFrame_TopChannel']['frame']
support=read(HERE/'transmission_brake_suspension_study/trial02/report.json');d=support['dimensions'];c=support['controls']
overlays={}
for role,image_name,size,origin,sx,sz in [
    ('LowSpeed','plate134.png',(1448,1147),(c['source_channel_x_px'][0],c['source_channel_web_z_px'][0]),d['scale_x_mm_px'],d['scale_z_mm_px']),
    ('Track','plate135.png',(1514,1091),(1116,133),c['channel_depth']/(1333-1116),d['web_span_mm']/(956-133))]:
    source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'/image_name
    width,height=size;name=role.lower()+'_source_overlay';ids=['Port'+role+'Bracket','Port'+role+'SuspensionLink']+(['PortTrackStop'] if role=='Track' else [])+['Port'+role+'Brake'+half+'AnchorBracket' for half in ['Upper','Lower']]+['Port'+role+'BrakeAnchorPin','Port'+role+'Brake'+('Lower' if role=='LowSpeed' else 'Upper')+'RetainerSpring']
    def pixel(v):return (40+origin[0]+(top[3]-v.x)/sx,80+origin[1]+(top[11]-v.z)/sz)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+210}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="35" y="36" font-family="sans-serif" font-size="24">HB {image_name[:-4]} | saved rear-anchor outlines registered to the retained channels</text>',
         f'<image x="40" y="80" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
    for oid in ids:
        s=item(oid,'BrakeSupport')['shape'];color='#007fa6' if 'Brake' in oid else '#bd2062' if oid.endswith('SuspensionLink') else '#dd7000'
        for edge in s.Edges:
            points=[pixel(v) for v in edge.discretize(Number=40)]
            path=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
            svg.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2.5" opacity=".85"/>')
    # Display the retained native shaft station as a held-out registration check.
    axis=support['interfaces']['Port'+role]['axis_center_mm'];x,y=pixel(App.Vector(*axis))
    svg.append(f'<path d="M{x-15},{y}h30 M{x},{y-15}v30" fill="none" stroke="#009654" stroke-width="3"/>')
    svg.extend([f'<text x="35" y="{height+130}" font-family="sans-serif" font-size="21">Orange: support/stop. Magenta: M337. Blue: rear brackets/pin/spring. Green: shaft axis. Hidden joint estimated.</text>',
        f'<text x="35" y="{height+165}" font-family="sans-serif" font-size="20">Original channel registration retained. Rear joint fits the retained frame; source station disagreement remains visible.</text></svg>'])
    path=out/(name+'.svg');path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/(name+'.png')))
    overlays[name]=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),source_channel_front_top_px=origin,
        scale_x_mm_px=sx,scale_z_mm_px=sz,occurrences=ids,shaft_axis_pixel=[x-40,y-80])
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],manifest_sha256=sha(out/'isolated/manifest.json'),
    renderer_sha256=sha(Path(__file__)),images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','anchor_detail','anchor_back',*overlays]},
    views={name:dict(direction=direction,solid_ids=[v['id'] for v in selected],context_ids=[v['id'] for v in outlined]) for name,selected,outlined,direction,title in views},
    overlays=overlays,display_only_crop=True,historical_geometry_qualified=False,installation_qualified=False))
