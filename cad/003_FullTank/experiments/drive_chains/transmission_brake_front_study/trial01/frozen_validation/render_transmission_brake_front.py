"""Render saved native front-brake BReps and fixed-datum handbook overlays."""
import argparse,base64
from pathlib import Path
from types import SimpleNamespace
import sys
import FreeCAD as App
import Part
import fitz
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
allrows={v['name']:v for v in m['occurrences']}
rows={n:allrows[n] for n in r['expected_new_occurrences']}
cache={}
COLORS.update(FrontEar=(.69,.48,.22),Spring=(.34,.65,.70),Steel=(.56,.62,.68),
    Lever=(.72,.45,.22),Band=(.43,.51,.58),Lining=(.62,.47,.32),Copper=(.84,.49,.26),Frame=(.64,.55,.42))
def item(name):
    row=allrows[name];key=row['definition'];definition=m['definitions'][key]
    if key not in cache:
        f=Path(definition['brep_path']);assert sha(f)==definition['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    role='FrontEar' if name.endswith('FrontEar') else 'Spring' if name.endswith('AdjustingSpring') else 'Lever' if name.endswith('Lever') else 'Band' if name.endswith('Band') else 'Lining' if name.endswith('Lining') else 'Copper' if 'Segment' in name and 'Rivet' in name else 'Frame' if 'TransmissionMountingFrame' in row['owners'] else 'Steel'
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
brake_names=[n for n,r in allrows.items() if 'TransmissionBrakeBands' in r['owners']]
frame_names=[n for n,r in allrows.items() if 'TransmissionMountingFrame' in r['owners']]
brakes=[item(n) for n in brake_names];frame=[item(n) for n in frame_names]
clip=Part.makeBox(300,170,530,App.Vector(2050,450,535));detail=[]
for obj in brakes:
    if not obj['id'].startswith('PortLowSpeed'):continue
    shape=obj['shape'].common(clip)
    if shape.Faces:detail.append(dict(obj,shape=shape,target=SimpleNamespace(Shape=shape),definition=obj['id']+'_display_crop'))
views=[('isometric',brakes,frame,(1,-.8,.55),'Front brake adjustment mechanisms | saved native assembly; historical dimensions estimated'),
       ('front_detail',detail,[],(1,-1,.3),'Low-speed front joint | paired ears, M336 pins, M333 screw, M335 spring, M331 swivel and M330 lever'),
       ('front_outer',detail,[],(1,1,.3),'Low-speed front joint | outer view; one cotter per free-end pin')]
for name,selected,outlined,direction,title in views:
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined);print('Rendered',name,flush=True)
parent=read(H/'transmission_brake_anchor_study/trial01/isolated/manifest.json')
top=next(v for v in parent['occurrences'] if v['name']=='TransmissionFrame_TopChannel')['frame']
support=read(H/'transmission_brake_suspension_study/trial02/report.json');d=support['dimensions'];c=support['controls']
overlays={}
for role,image_name,size,origin,sx,sz in [
    ('LowSpeed','plate134.png',(1448,1147),(c['source_channel_x_px'][0],c['source_channel_web_z_px'][0]),d['scale_x_mm_px'],d['scale_z_mm_px']),
    ('Track','plate135.png',(1514,1091),(1116,133),c['channel_depth']/(1333-1116),d['web_span_mm']/(956-133))]:
    source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'/image_name
    width,height=size;name=role.lower()+'_source_overlay'
    ids=[n for n in rows if n.startswith('Port'+role) and not any(t in n for t in ['Rivet','Cotter','FrontPin'])]
    def pixel(v):return (40+origin[0]+(top[3]-v.x)/sx,80+origin[1]+(top[11]-v.z)/sz)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+210}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="35" y="36" font-family="sans-serif" font-size="24">HB {image_name[:-4]} | saved front joints with retained channel registration</text>',
         f'<image x="40" y="80" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
    for oid in ids:
        s=item(oid)['shape'];color='#c02065' if oid.endswith('Lever') else '#009088' if oid.endswith('FrontEar') else '#007fa6'
        for edge in s.Edges:
            points=[pixel(v) for v in edge.discretize(Number=40)]
            svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="2" opacity=".85"/>')
    svg.extend([f'<text x="35" y="{height+130}" font-family="sans-serif" font-size="20">Green: ears. Magenta: lever. Blue: adjusting screw, spring, swivel and nut. All front dimensions estimated.</text>',
        f'<text x="35" y="{height+165}" font-family="sans-serif" font-size="20">Registration is unchanged; model/source residuals remain visible. Historical layout and service sequence remain unqualified.</text></svg>'])
    path=out/(name+'.svg');path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/(name+'.png')))
    overlays[name]=dict(source_sha256=sha(source),source_channel_front_top_px=origin,scale_x_mm_px=sx,scale_z_mm_px=sz,occurrences=ids)
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),
    images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','front_detail','front_outer',*overlays]},overlays=overlays,
    display_only_crop=True,accepted_geometry=False))
