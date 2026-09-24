"""Native diagnostic views of the conditional shared brake-stop installation."""
import argparse
import base64
from pathlib import Path
from types import SimpleNamespace
import sys
import FreeCAD as App
import Part
import fitz
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path[:0]=[str(H),str(H.parents[1])]
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};cache={}
COLORS.update(StopLug=(.72,.49,.23),StopBar=(.30,.65,.66),StopBracket=(.65,.52,.31),
    Steel=(.62,.67,.70),Band=(.43,.51,.58),Lining=(.62,.47,.32),Copper=(.84,.49,.26),Frame=(.64,.55,.42))
def item(name):
    row=rows[name];key=row['definition'];d=m['definitions'][key]
    if key not in cache:
        f=Path(d['brep_path']);assert sha(f)==d['brep_sha256'];s=Part.Shape();s.read(str(f));cache[key]=SimpleNamespace(Shape=s)
    target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    role='StopLug' if name.endswith('StopLug') else 'StopBar' if name.endswith('BrakeStopBar') else 'StopBracket' if name.endswith('BrakeStopBracket') else 'Band' if name.endswith('Band') else 'Lining' if name.endswith('Lining') else 'Copper' if 'Segment' in name and 'Rivet' in name else 'Frame' if 'TransmissionMountingFrame' in row['owners'] else 'Steel'
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
names=[n for n,row in rows.items() if 'TransmissionBrakeBands' in row['owners'] or 'TransmissionBrakeStops' in row['owners']]
frame_names=[n for n,row in rows.items() if 'TransmissionMountingFrame' in row['owners']]
frame_names += [hand+'FixedBearing_inner_'+part for hand in ['Port','Starboard'] for part in ['bracket','cap']]
frame_names += [n for n in r['expected_revised_occurrences'] if 'FixedBearing_inner_Stud' in n]
selected=[item(n) for n in names];frame=[item(n) for n in frame_names]
shaded(selected,out/'isometric.svg',(1,-.8,.55),'Brake-stop trial | shared bars and perpendicular adjusters; mounting hypothesis unqualified',context=frame)
print('Rendered isometric',flush=True)
clip=Part.makeBox(540,425,370,App.Vector(1750,440,510));detail=[]
mount_context=['PortFixedBearing_inner_bracket','PortFixedBearing_inner_cap']
mount_context += [n for n in r['expected_revised_occurrences'] if n.startswith('PortFixedBearing_inner_Stud')]
for name in names+mount_context:
    if not name.startswith('Port'):continue
    obj=item(name);shape=obj['shape'].common(clip)
    if shape.Faces:detail.append(dict(obj,shape=shape,target=SimpleNamespace(Shape=shape),definition=name+'_display_crop'))
shaded(detail,out/'support_detail.svg',(1,-1,.5),'Port brake stops | cyan crossbar, brown support, curved lugs; experimental mounting')
print('Rendered support detail',flush=True)
source_support=read(H/'transmission_brake_suspension_study/trial02/report.json');d=source_support['dimensions'];c=source_support['controls']
top=rows['TransmissionFrame_TopChannel']['frame'];overlays={}
for role,img,size,origin,sx,sz in [
    ('LowSpeed','plate134.png',(1448,1147),(1136,122),d['scale_x_mm_px'],d['scale_z_mm_px']),
    ('Track','plate135.png',(1514,1091),(1116,133),c['channel_depth']/(1333-1116),d['web_span_mm']/(956-133))]:
    source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'/img
    width,height=size;name=role.lower()+'_source_overlay'
    ids=[n for n in r['expected_new_occurrences'] if (n.startswith('Port'+role) or n in ['PortBrakeStopBar','PortBrakeStopBracket']) and 'Rivet' not in n]
    def pixel(v):return 40+origin[0]+(top[3]-v.x)/sx,80+origin[1]+(top[11]-v.z)/sz
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+200}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="35" y="36" font-family="sans-serif" font-size="24">HB {img[:-4]} | experimental stop geometry; retained channel registration</text>',
        f'<image x="40" y="80" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
    for oid in ids:
        color='#009088' if oid.endswith('StopLug') else '#c02065' if oid.endswith('Bracket') or oid.endswith('Bar') else '#007fa6'
        for edge in item(oid)['shape'].Edges:
            points=[pixel(v) for v in edge.discretize(Number=40)]
            svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="2" opacity=".85"/>')
    svg.append(f'<text x="35" y="{height+130}" font-family="sans-serif" font-size="19">Green: lug. Magenta: bracket/bar. Blue: screws/nuts. Geometry and part-mark mapping remain conditional.</text></svg>')
    f=out/(name+'.svg');f.write_text('\n'.join(svg))
    with fitz.open(stream=f.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/(name+'.png')))
    overlays[name]=dict(source_sha256=sha(source),origin_px=origin,scale_mm_per_pixel=[sx,sz],occurrences=ids)
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),
    images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','support_detail',*overlays]},overlays=overlays,
    display_only_crop=True,accepted_geometry=False))
print('Rendered source overlays',flush=True)
