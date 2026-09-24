"""Saved spacer/spring diagnostic views; keep the existing source registration."""
import argparse,base64
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
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};cache={}
COLORS.update(Spacer=(.84,.61,.20),Spring=(.28,.65,.70),Steel=(.58,.63,.69),Lever=(.69,.42,.24),Band=(.43,.51,.58),Lining=(.62,.47,.32),Copper=(.84,.49,.26),Frame=(.64,.55,.42))
def item(name):
 row=rows[name];key=row['definition'];d=m['definitions'][key]
 if key not in cache:
  path=Path(d['brep_path']);assert sha(path)==d['brep_sha256'];s=Part.Shape();s.read(str(path));cache[key]=SimpleNamespace(Shape=s)
 target=cache[key];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
 role='Spacer' if name.endswith('SpringSpacer') else 'Spring' if name.endswith('AdjustingSpring') else 'Lever' if name.endswith('Lever') else 'Band' if name.endswith('Band') else 'Lining' if name.endswith('Lining') else 'Copper' if 'Segment' in name and 'Rivet' in name else 'Frame' if 'TransmissionMountingFrame' in row['owners'] else 'Steel'
 return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
names=[n for n,row in rows.items() if 'TransmissionBrakeBands' in row['owners'] or 'TransmissionBrakeStops' in row['owners']]
context=[item(n) for n,row in rows.items() if 'TransmissionMountingFrame' in row['owners']]
shaded([item(n) for n in names],out/'isometric.svg',(1,-.8,.55),'Brake adjustment | four conditional SH687A spacers; shortened estimated springs',context=context)
focus=[item(n) for n,row in rows.items() if 'PortLowSpeedBrakeFrontMechanism' in row['owners']]
shaded(focus,out/'spacer_detail.svg',(1,-1,.3),'Swivel-side spacer hypothesis | gold: SH687A, cyan: shortened M335; other geometry retained')
# Direct comparison remains tied to the channel; no camera optimization.
support=read(H/'transmission_brake_suspension_study/trial02/report.json');d=support['dimensions'];c=support['controls'];top=rows['TransmissionFrame_TopChannel']['frame']
source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate134.png';width,height=1448,1147;origin=(c['source_channel_x_px'][0],c['source_channel_web_z_px'][0]);sx,sz=d['scale_x_mm_px'],d['scale_z_mm_px']
ids=['PortLowSpeedBrake'+suffix for suffix in ['AdjustingSpring','AdjustingSpringSpacer','AdjustingScrew','Swivel']]
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+80}" height="{height+210}">','<rect width="100%" height="100%" fill="white"/>',f'<image x="40" y="80" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>','<text x="35" y="36" font-family="sans-serif" font-size="24">HB134 | conditional spacer and spring; retained channel registration</text>']
for name in ids:
 color='#bf7900' if name.endswith('Spacer') else '#009088' if name.endswith('Spring') else '#3366b0'
 for edge in item(name)['shape'].Edges:
  pts=[(40+origin[0]+(top[3]-v.x)/sx,80+origin[1]+(top[11]-v.z)/sz) for v in edge.discretize(Deflection=.4)]
  svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="2" opacity=".85"/>')
svg += [f'<text x="35" y="{height+135}" font-family="sans-serif" font-size="19">Gold: spacer hypothesis. Green: spring. Blue: retained screw/swivel. SH687A is not separately identified here.</text>',f'<text x="35" y="{height+170}" font-family="sans-serif" font-size="19">Pictorial section: fixed 2D datum comparison, not a calibrated photograph or proof of the spacer position.</text></svg>']
f=out/'spacer_source_overlay.svg';f.write_text('\n'.join(svg))
with fitz.open(stream=f.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/'spacer_source_overlay.png'))
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),images={name+'.png':sha(out/(name+'.png')) for name in ['isometric','spacer_detail','spacer_source_overlay']},source_sha256=sha(source),source_registration=dict(origin_px=origin,scale_mm_px=[sx,sz],mode='Inherited fixed 2D channel datum; no refit',projection_classification='Pictorial section with local depth depiction; diagnostic registration only'),historical_geometry_qualified=False))
print('Rendered assembly, mechanism detail and unchanged-registration source comparison',flush=True)
