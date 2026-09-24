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
for mode in ['rotated_compound','wedge_compound','wedge_direct','sector_direct']:
 try:
  a0=-tail;a1=base['short']['sweep_rad']+bc['steel_terminal_margin']/neutral
  if mode.startswith('wedge'):
   ring=Part.makeCylinder(ro,width,V(0,-width/2,0),V(0,1,0)).cut(Part.makeCylinder(ri,width+2,V(0,-width/2-1,0),V(0,1,0)))
   ps=[V(0,-width/2-1,0),point(500,a0,-width/2-1),point(500,a1,-width/2-1)]
   wedge=Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,width+2,0))
   raw=ring.common(wedge)
  else:raw=stock.copy()
  s=raw.cut(Part.makeCompound(lining));tools=[];posed_rivets=[]
  print(mode,'blank',s.isValid(),s.Volume,flush=True)
  for i,along in enumerate(c['attachment_columns_mm']):
   for j,y in enumerate(c['attachment_rows_mm']):
    theta=-tail+along/neutral;axis=point(1,theta,0);origin=point(ri+c['steel_head_recess'],theta,y)
    pose=App.Placement(origin,App.Rotation(V(0,0,1),axis))
    hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
    if mode.endswith('direct'):
     drill=Part.makeCylinder(hole,rd['grip_mm']+20,origin-axis*5,axis)
     cone=Part.makeCone(c['steel_head_radius']+5*slope,hole,rd['head_depth_mm']+5,origin-axis*5,axis)
     tool=drill.fuse(cone)
    else:
     drill=Part.makeCylinder(hole,rd['grip_mm']+20,V(0,0,-5));cone=Part.makeCone(c['steel_head_radius']+5*slope,hole,rd['head_depth_mm']+5,V(0,0,-5))
     tool=drill.fuse(cone)
     if mode=='rotated_compound':tool.rotate(V(),V(0,0,1),90)
     tool.Placement=pose.multiply(tool.Placement)
    tools.append(tool)
    rv=rivet.copy();rv.Placement=pose;posed_rivets.append(rv)
  s=s.cut(Part.makeCompound(tools))
  extra=s.cut(env);overlaps=[s.common(rv).Volume for rv in posed_rivets]
  r=dict(mode=mode,valid=s.isValid(),solids=len(s.Solids),outside_volume=extra.Volume,outside_faces=len(extra.Faces),overlaps=overlaps,tolerance=s.getTolerance(1))
  s.exportBrep(str(out/(mode+'.brep')))
 except Exception as exc:r=dict(mode=mode,error=str(exc))
 results.append(r);print(r,flush=True);(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
