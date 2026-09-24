"""Inspect saved prototype geometry through the unchanged HB133 registration."""
import argparse,base64,sys
from types import SimpleNamespace
from pathlib import Path
H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1];sys.path.insert(0,str(STAGE))
from lib.evidence import read,write,sha
import FreeCAD as App
import Part
import fitz
from lib.visual_review import shaded
from lib.cad_build import COLORS
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');native=out/'HighBrakeBottomStopStudy.FCStd';assert sha(native)==r['prototype_native_sha256']
regpath=H/'transmission_high_brake_support_study/source_registration.json';reg=read(regpath);source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
doc=App.openDocument(str(native));shapes={};definitions={};roles={}
try:
 for body in doc.Definitions.Group:definitions[body.Name]=body.Shape.copy()
 for link in doc.Root.Group:
  s=link.LinkedObject.Shape.copy();s.Placement=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);shapes[link.Name]=s;roles[link.Name]=link.LinkedObject.Name
finally:App.closeDocument(doc.Name)
center=read(H/'transmission_high_brake_mechanism_study/trial01/report.json')['interfaces']['PortHighSpeedBrake']['center_world_mm']
cx,cy=reg['center_px'];scale=reg['pixels_per_mm'];V=App.Vector
def pixel(v):return cx-(v.x-center[0])*scale,cy-(v.z-center[2])*scale
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1850">','<rect width="100%" height="100%" fill="white"/>',
 '<text x="30" y="34" font-family="sans-serif" font-size="22">HB133 | anchor retention and M366 bottom stop in retained registration</text>',
 f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
def lines(shape,color,width=1.6):
 for edge in shape.Edges:
  pts=[pixel(v) for v in edge.discretize(Deflection=.3)]
  svg.append('<polyline points="'+' '.join(f'{u+40:.3f},{v+70:.3f}' for u,v in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}" opacity=".8"/>')
sections=[]
for name,s in shapes.items():
 if name.startswith('Port'):lines(s,'#ba3022',1.9)
svg+=['<text x="30" y="1745" font-family="sans-serif" font-size="18">Red: saved bracket, anchor pin/cotter, bottom stop and hardware. Fixed source registration.</text>',
 '<text x="30" y="1780" font-family="sans-serif" font-size="18">Hidden stock, transverse mounting pitch and cotter form are estimates. Top/back stop and clip remain pending.</text>',
 '<text x="30" y="1815" font-family="sans-serif" font-size="18">No camera refit. Same source scale and center; this is a diagnostic illustration comparison.</text></svg>']
# Keep the earlier source overlay: this renderer revision only adds saved-native isometrics.
if (out/'bottom_stop_source.svg').exists():assert (out/'bottom_stop_source.svg').read_text()=='\n'.join(svg)
(out/'bottom_stop_source.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'bottom_stop_source.svg').read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(out/'bottom_stop_source.png'))
# Cache tessellation by the actual identity-frame definition. World-posed
# targets with a shared key would reuse the first occurrence at the wrong pose.
COLORS.update(Bracket=(.64,.46,.29),Stop=(.48,.55,.60),Hardware=(.67,.69,.70),Retained=(.51,.61,.68))
items=[]
for name,s in shapes.items():
 role=roles[name];system='Bracket' if role=='Def_anchor_bracket' else 'Stop' if role in ['Def_bottom_stop','Def_bottom_lock_plate'] else 'Hardware'
 items.append(dict(id=name,shape=s,target=SimpleNamespace(Shape=definitions[role]),definition=role,system=system,representation='assembly'))
parent=H/'transmission_high_brake_support_study/integrated01';m=read(parent/'isolated/manifest.json');context=[]
for row in m['occurrences']:
 if row['name'] not in [hand+'HighSpeedBrake'+part for hand in ['Port','Starboard'] for part in ['LongBand','ShortBand','AnchorEnd']]:continue
 d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);s.Placement=App.Placement(App.Matrix(*row['frame']))
 context.append(dict(id=row['name'],shape=s,target=SimpleNamespace(Shape=s),definition=row['name'],system='Retained',representation='assembly'))
shaded(items,out/'bottom_stop_isometric_reviewed.svg',(1,-1,.45),'High-speed anchor retention and bottom stops | both installed sides',context=context)
shaded([v for v in items if v['id'].startswith('Port')],out/'bottom_stop_detail.svg',(.5,-1,.7),'Port anchor pin and bottom stop | source-sized cotter, estimated cast shelf',context=[v for v in context if v['id']=='PortHighSpeedBrakeAnchorEnd'])
write(out/'review_render_receipt.json',dict(native_sha256=sha(native),source_registration_sha256=sha(regpath),source_sha256=sha(source),
 renderer_sha256=sha(Path(__file__)),image_sha256=sha(out/'bottom_stop_source.png'),additional_images={n:sha(out/n) for n in ['bottom_stop_isometric_reviewed.png','bottom_stop_detail.png']},sections=sections,camera_refit=False,historical_geometry_qualified=False))
print('Rendered saved bottom-stop prototype in fixed source registration',flush=True)
