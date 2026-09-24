"""Render the saved high-speed forward fittings and lining hardware with fixed registration."""
import argparse,base64,math
import fitz
from pathlib import Path
from types import SimpleNamespace
import sys
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
COLORS.update(Anchor=(.71,.47,.29),Rivet=(.62,.56,.45),Screw=(.69,.72,.74),HighBand=(.38,.54,.61),HighLining=(.70,.47,.25),Steel=(.58,.62,.68),Frame=(.62,.53,.40),Copper=(.76,.43,.23),Brass=(.83,.67,.28),End=(.48,.56,.60))
cache={};items={}
for row in m['occurrences']:
    owners=row['owners'];name=row['name']
    if not any(v in owners for v in ['TransmissionHighSpeedBrakes','TransmissionBrakeBands','TransmissionBrakeStops','TransmissionMountingFrame']) and not name.endswith('TransmissionCore_high_drum'):continue
    d=m['definitions'][row['definition']]
    if row['definition'] not in cache:
        assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[row['definition']]=SimpleNamespace(Shape=s)
    target=cache[row['definition']];s=target.Shape.copy();s.Placement=App.Placement(App.Matrix(*row['frame']))
    role='End' if name.endswith('FrontEnd') else 'Brass' if row['definition'].endswith('lining_brass') else 'Copper' if 'LiningFastener' in name else 'Rivet' if ('AnchorEndRivet' in name or 'FrontSteelRivet' in name) else 'Anchor' if name.endswith('AnchorEnd') else 'Screw' if 'CouplingScrew' in name else 'HighLining' if 'HighSpeedBrake' in name and name.endswith('Lining') else 'HighBand' if 'HighSpeedBrake' in name and name.endswith('Band') else 'Frame' if 'TransmissionMountingFrame' in owners else 'Steel'
    items[name]=dict(id=name,shape=s,target=target,definition=row['definition'],system=role,representation='assembly')
context=[v for v in items.values() if v['system']=='Frame']
shaded([v for v in items.values() if v['system']!='Frame'],out/'isometric.svg',(1,-.8,.55),'High-speed brake development | forward fittings and lining fasteners; controls and supports pending',context=context)
focus=[v for k,v in items.items() if k.startswith('PortHighSpeedBrake') and ('FrontEnd' in k or 'FrontSteelRivet' in k or any(k.endswith(v) for v in ['LongLiningFastener1','LongLiningFastener2','ShortLiningFastener5','ShortLiningFastener6']))]
bb=Part.makeCompound([v['shape'] for v in focus]).BoundBox
window=Part.makeBox(bb.XLength+24,bb.YLength+24,bb.ZLength+24,App.Vector(bb.XMin-12,bb.YMin-12,bb.ZMin-12))
for name,item in items.items():
    if name.startswith('PortHighSpeedBrake') and item['system'] in ['HighBand','HighLining']:
        cut=item['shape'].common(window)
        if cut.Solids:
            focus.append(dict(item,shape=cut,target=SimpleNamespace(Shape=cut),definition=name+'_display_cut'))
shaded(focus,out/'high_brake_detail.svg',(1,-1,.3),'Forward band ends | separate fittings, steel rivets and lining hardware; pins and controls pending')
reg_path=H/'transmission_high_brake_study/joint_source_registration.json';reg=read(reg_path)
root=H.parents[3];source=root/reg['source_image'];assert sha(source)==reg['source_sha256']
cx,cy=reg['center_px'];scale=reg['pixels_per_mm'];center=r['interfaces']['PortHighSpeedBrake']['center_world_mm']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1810">','<rect width="100%" height="100%" fill="white"/>',f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>','<text x="30" y="34" font-family="sans-serif" font-size="23">HB133 | fixed planar registration: forward fittings and source-counted lining hardware</text>']
for name,item in items.items():
    if not name.startswith('PortHighSpeedBrake') or 'Rivet' in name:continue
    color='#b05a12' if name.endswith(('AnchorEnd','FrontEnd')) else '#3870b0' if 'CouplingScrew' in name else '#009070' if name.endswith('Lining') else '#6685a0'
    for edge in item['shape'].Edges:
        points=[(40+cx-(v.x-center[0])*scale,70+cy-(v.z-center[2])*scale) for v in edge.discretize(Deflection=.4)]
        svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="1.5" opacity=".80"/>')
anchor=items['PortHighSpeedBrakeAnchorEnd']['shape']
bores=[f.Surface for f in anchor.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-r['rear_controls']['anchor_eye_bore_radius'])<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-6]
assert len(bores)==1
point=bores[0].Center;pixel=[cx-(point.x-center[0])*scale,cy-(point.z-center[2])*scale];pick=reg['diagnostic_picks']['anchor_pin_center_px']
residual=[pixel[i]-pick[i] for i in range(2)]
svg+=['<text x="30" y="1745" font-family="sans-serif" font-size="18">Green: lining; blue: bands/hardware; brown: end fittings. Pins, controls and supports remain absent.</text>','<text x="30" y="1780" font-family="sans-serif" font-size="18">Illustration-based planar diagnostic, not a calibrated camera. Printed radius supplies the scale.</text></svg>']
f=out/'high_brake_source.svg';f.write_text('\n'.join(svg))
with fitz.open(stream=f.read_bytes(),filetype='svg') as document:document[0].get_pixmap().save(str(out/'high_brake_source.png'))
front_residuals={}
for role,key in [('Long','upper_free_pin_center_px'),('Short','lower_free_pin_center_px')]:
    end=items['PortHighSpeedBrake'+role+'FrontEnd']['shape']
    face=next(f for f in end.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-r['controls']['pin_bore_radius'])<1e-6)
    point=face.Surface.Center;projected=[cx-(point.x-center[0])*scale,cy-(point.z-center[2])*scale];picked=reg['diagnostic_picks'][key]
    front_residuals[role]=dict(projected_px=projected,picked_px=picked,residual_px=[projected[i]-picked[i] for i in range(2)])
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),images={n+'.png':sha(out/(n+'.png')) for n in ['isometric','high_brake_detail','high_brake_source']},source_registration_sha256=sha(reg_path),source_sha256=sha(source),anchor_eye_projection_px=pixel,anchor_pick_px=pick,anchor_residual_px=residual,front_pin_residuals=front_residuals,camera_refit=False,historical_camera_qualified=False,packet_complete=False))
print('Rendered forward fittings and lining hardware and fixed source comparison',flush=True)
