from pathlib import Path
import json,math,sys
H=Path('/home/cyapp/MarkVIIILiberty/cad/003_FullTank/experiments/drive_chains');sys.path.insert(0,str(H))
import FreeCAD as App
import Part
from transmission_high_brake_band_parts import parts as initial_parts
from transmission_brake_band_parts import sector,point,rotate_theta
from transmission_brake_anchor_parts import steel_rivet
V=App.Vector
out=Path('/home/cyapp/MarkVIIILiberty/.work/high-brake-joint/short_cut_probe');out.mkdir(exist_ok=True)
c=json.loads((H/'transmission_high_brake_study/joint_controls.json').read_text())['controls'];bc=json.loads((H/'transmission_high_brake_study/band_controls.json').read_text())['controls']
_,base=initial_parts(bc);neutral=bc['inner_radius']+bc['lining_stock']/2;ri=bc['inner_radius']+bc['lining_stock'];ro=ri+bc['steel_stock'];width=bc['width'];tail=c['rear_tail_length']/neutral
stock=sector(ri,ro,-tail,base['short']['sweep_rad']+bc['steel_terminal_margin']/neutral,width)
lining=[]
for h in base['short']['holes']:
 t=Part.makeCylinder(bc['steel_hole_radius'],bc['lining_stock']+bc['steel_stock']+4,V(0,0,-2));t.Placement=App.Placement(App.Matrix(*h['frame']));lining.append(t)
blank=stock.cut(Part.makeCompound(lining));blank.exportBrep(str(out/'blank.brep'))
rivet,rd=steel_rivet(dict(c,foot_stock=c['anchor_outer_stock']),bc['steel_stock'])
env=Part.makeCylinder(ro,width,V(0,-width/2,0),V(0,1,0));results=[]
for mode in ['fused_sequential','fused_compound','separate_sequential','separate_compound','rotated_compound']:
 s=blank.copy();tools=[];posed_rivets=[]
 for i,along in enumerate(c['attachment_columns_mm']):
  for j,y in enumerate(c['attachment_rows_mm']):
   theta=-tail+along/neutral;pose=App.Placement(point(ri+c['steel_head_recess'],theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
   hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
   drill=Part.makeCylinder(hole,rd['grip_mm']+20,V(0,0,-5));cone=Part.makeCone(c['steel_head_radius']+5*slope,hole,rd['head_depth_mm']+5,V(0,0,-5))
   if mode.startswith('fused') or mode=='rotated_compound': ts=[drill.fuse(cone)]
   else: ts=[drill,cone]
   for t in ts:
    if mode=='rotated_compound':t.rotate(V(),V(0,0,1),90)
    t.Placement=pose.multiply(t.Placement);tools.append(t)
    if mode.endswith('sequential'):s=s.cut(t)
   rv=rivet.copy();rv.Placement=pose;posed_rivets.append(rv)
 if mode.endswith('compound'):s=s.cut(Part.makeCompound(tools))
 extra=s.cut(env);overlaps=[s.common(rv).Volume for rv in posed_rivets]
 r=dict(mode=mode,valid=s.isValid(),solids=len(s.Solids),outside_volume=extra.Volume,outside_faces=len(extra.Faces),overlaps=overlaps,tolerance=s.getTolerance(1));results.append(r);print(r,flush=True)
 s.exportBrep(str(out/(mode+'.brep')));(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
