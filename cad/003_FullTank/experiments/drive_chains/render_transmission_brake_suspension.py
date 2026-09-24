"""Native support views and registered source overlays; no physical poses changed."""
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
COLORS.update(Frame=(.63,.55,.41),BrakeSupport=(.85,.55,.24),BrakeStop=(.42,.66,.72),Bearing=(.51,.59,.68))
rows={v['name']:v for v in m['occurrences']};cache={}
def item(name,role):
    row=rows[name];key=row['definition']
    if key not in cache:
        d=m['definitions'][key];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
frame=[];context=[]
for name,row in rows.items():
    if 'TransmissionMountingFrame' in row['owners']:
        role='BrakeSupport' if name in r['expected_new_occurrences'] and name.endswith('Bracket') else 'BrakeStop' if name.endswith('TrackStop') else 'Frame'
        frame.append(item(name,role))
    elif 'FixedTransmissionBearings' in row['owners'] or name.endswith(('TransmissionOutput_drum','TransmissionCore_brake_case')):
        context.append(item(name,'Bearing'))
detail=[];clip=Part.makeBox(240,470,310,App.Vector(1410,425,970))
for obj in frame:
    s=obj['shape'].common(clip)
    if s.Faces:detail.append(dict(obj,shape=s,target=SimpleNamespace(Shape=s),definition=obj['id']+'_display_crop'))
views=[('isometric',frame,context,(1,-.8,.55),'Brake suspension geometry | four M338 brackets and two M385 stops; fastening pending'),
       ('support_detail',detail,[],(1,-.8,-.3),'Upper frame underside | estimated bracket feet, open pin bores and track-brake stop')]
for name,selected,outlined,direction,title in views:
    shaded(selected,out/(name+'.svg'),direction,title,context=outlined)
    print('Rendered',name,flush=True)
top=rows['TransmissionFrame_TopChannel']['frame'];d=r['dimensions'];c=r['controls']
overlays={}
for role,image_name,size,origin,sx,sz in [
    ('LowSpeed','plate134.png',(1448,1147),(c['source_channel_x_px'][0],c['source_channel_web_z_px'][0]),d['scale_x_mm_px'],d['scale_z_mm_px']),
    ('Track','plate135.png',(1514,1091),(1116,133),c['channel_depth']/(1333-1116),d['web_span_mm']/(956-133))]:
    source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'/image_name
    width,height=size;name=role.lower()+'_source_overlay';ids=['Port'+role+'Bracket']+(['PortTrackStop'] if role=='Track' else [])
    def pixel(v):return (40+origin[0]+(top[3]-v.x)/sx,80+origin[1]+(top[11]-v.z)/sz)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+210}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="35" y="36" font-family="sans-serif" font-size="24">HB {image_name[:-4]} | saved support outlines registered to the retained channels</text>',
         f'<image x="40" y="80" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
    for oid in ids:
        s=item(oid,'BrakeSupport')['shape'];color='#dd7000' if oid.endswith('Bracket') else '#007fa6'
        for edge in s.Edges:
            points=[pixel(v) for v in edge.discretize(Number=40)]
            path=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
            svg.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2.5" opacity=".85"/>')
    # Display the retained native shaft station as a held-out registration check.
    axis=r['interfaces']['Port'+role]['axis_center_mm'];x,y=pixel(App.Vector(*axis))
    svg.append(f'<path d="M{x-15},{y}h30 M{x},{y-15}v30" fill="none" stroke="#009654" stroke-width="3"/>')
    svg.extend([f'<text x="35" y="{height+130}" font-family="sans-serif" font-size="21">Orange: M338. Blue: M385. Green cross: native shaft axis. Thicknesses and hidden profiles remain estimated.</text>',
        f'<text x="35" y="{height+165}" font-family="sans-serif" font-size="20">Conditional X/Z registration; unprinted source dimensions and scan/drawing disagreements remain unresolved.</text></svg>'])
    path=out/(name+'.svg');path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/(name+'.png')))
    overlays[name]=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),source_channel_front_top_px=origin,
        scale_x_mm_px=sx,scale_z_mm_px=sz,occurrences=ids,shaft_axis_pixel=[x-40,y-80])
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],manifest_sha256=sha(out/'isolated/manifest.json'),
    renderer_sha256=sha(Path(__file__)),images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','support_detail',*overlays]},
    views={name:dict(direction=direction,solid_ids=[v['id'] for v in selected],context_ids=[v['id'] for v in outlined]) for name,selected,outlined,direction,title in views},
    overlays=overlays,display_only_crop=True,historical_geometry_qualified=False,installation_qualified=False))
