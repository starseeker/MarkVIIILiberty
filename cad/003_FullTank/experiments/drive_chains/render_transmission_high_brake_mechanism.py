"""Render saved mechanism geometry and a fixed HB133 diagnostic comparison."""
import argparse,base64,sys
from pathlib import Path
from types import SimpleNamespace
import FreeCAD as App
import Part
import fitz
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
COLORS.update(Mechanism=(.57,.64,.70),Spring=(.70,.55,.34),Band=(.40,.56,.59),Lining=(.64,.43,.27),Frame=(.63,.52,.39))
cache={};items={};rows={v['name']:v for v in m['occurrences']};fresh=set(r['expected_new_occurrences'])
for row in m['occurrences']:
 owners=row['owners'];name=row['name']
 if not any(v in owners for v in ['TransmissionHighSpeedBrakes','TransmissionBrakeBands','TransmissionBrakeStops','TransmissionMountingFrame']) and not name.endswith('TransmissionCore_high_drum'):continue
 d=m['definitions'][row['definition']]
 if row['definition'] not in cache:
  assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[row['definition']]=SimpleNamespace(Shape=s)
 target=cache[row['definition']];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
 role='Spring' if name.endswith('AdjustingSpring') else 'Mechanism' if name in fresh else 'Lining' if name.endswith('Lining') else 'Frame' if 'TransmissionMountingFrame' in owners else 'Band'
 items[name]=dict(id=name,shape=s,target=target,definition=row['definition'],system=role,representation='assembly')
shaded([v for v in items.values() if v['system']!='Frame'],out/'isometric.svg',(1,-.8,.55),'High-speed operating mechanisms | anchor supports, stops and control rods pending',context=[v for v in items.values() if v['system']=='Frame'])
focus=[v for k,v in items.items() if k.startswith('PortHighSpeedBrake') and (k in fresh or k.endswith('FrontEnd'))]
shaded(focus,out/'high_brake_mechanism_detail.svg',(1,-1,.3),'M355 paired lever, M356 pins and M357/M358/M369 adjustment | estimated profiles')
regpath=H/'transmission_high_brake_mechanism_study/source_registration.json';reg=read(regpath);source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
cx,cy=reg['center_px'];scale=reg['pixels_per_mm'];center=r['interfaces']['PortHighSpeedBrake']['center_world_mm'];V=App.Vector
def pixel(v):return [cx-(v.x-center[0])*scale,cy-(v.z-center[2])*scale]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1810">','<rect width="100%" height="100%" fill="white"/>',f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>','<text x="30" y="34" font-family="sans-serif" font-size="23">HB133 | operating mechanism in retained planar registration</text>']
for name,item in items.items():
 if not name.startswith('PortHighSpeedBrake') or 'FrontSteelRivet' in name or 'Fastener' in name:continue
 color='#b12c1f' if name in fresh else '#008070'
 for edge in item['shape'].Edges:
  pts=[pixel(v) for v in edge.discretize(Deflection=.35)]
  svg.append('<polyline points="'+' '.join(f'{x+40:.3f},{y+70:.3f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="1.3" opacity=".75"/>')
svg+=['<text x="30" y="1745" font-family="sans-serif" font-size="18">Red: new mechanism; green: retained bands/fittings. Source profiles remain conditional estimates.</text>','<text x="30" y="1780" font-family="sans-serif" font-size="18">Fixed planar diagnostic, not calibrated photographic perspective. No camera refit.</text></svg>']
(out/'high_brake_mechanism_source.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'high_brake_mechanism_source.svg').read_bytes(),filetype='svg') as f:f[0].get_pixmap().save(str(out/'high_brake_mechanism_source.png'))
residuals=[]
def residual(label,world,pick):
 uv=pixel(world);residuals.append(dict(label=label,picked_px=pick,projected_px=uv,residual_px=[uv[i]-pick[i] for i in range(2)]))
for i,pick in enumerate(reg['additional_diagnostic_picks']['lever_rivet_centers_px'],1):
 s=items['PortHighSpeedBrakeLeverRivet'+str(i)]['shape'];f=next(f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-4.7625)<1e-6);residual('joining_rivet_'+str(i),f.Surface.Center,pick)
s=items['PortHighSpeedBrakeLeverLeft']['shape'];fs=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-r['controls']['lever_end_bore_radius'])<1e-6];residual('control_rod_pin',min(fs,key=lambda f:f.Surface.Center.z).Surface.Center,reg['additional_diagnostic_picks']['control_rod_pin_px'])
sf=App.Placement(App.Matrix(*rows['PortHighSpeedBrakeAdjustingScrew']['frame']));residual('screw_tip',sf.multVec(V(0,0,r['controls']['screw_length'])),reg['additional_diagnostic_picks']['screw_top_px'])
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in ['isometric','high_brake_mechanism_detail','high_brake_mechanism_source']},source_registration_sha256=sha(regpath),source_sha256=sha(source),diagnostic_residuals=residuals,source_pick_uncertainty_px=reg['additional_pick_uncertainty_px'],residuals_independent=False,camera_refit=False,historical_camera_qualified=False,packet_complete=False))
print('Rendered saved high-speed operating mechanisms with fixed HB133 comparison',flush=True)
