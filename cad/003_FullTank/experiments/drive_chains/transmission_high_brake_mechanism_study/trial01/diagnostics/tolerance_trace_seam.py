from pathlib import Path
import sys,json
import FreeCAD as A
import Part
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H))
frozen=R/'.work/cad-pipeline/high_brake_mechanism01/candidate/frozen_inputs'
s=(frozen/'cad__003_FullTank__experiments__drive_chains__transmission_high_brake_mechanism_parts.py').read_text()
s=s.replace('lever=Part.Face(Part.Wire(edges)).extrude(V(0,width,0))','lever=Part.Face(Part.Wire(edges)).extrude(V(0,width,0));print("extruded",lever.getTolerance(1),flush=True)')
s=s.replace('lever=lever.fuse(boss)','lever=lever.fuse(boss);print("boss",lever.getTolerance(1),flush=True)')
s=s.replace('lever=lever.cut(tool)','lever=lever.cut(tool);print("seat",z,lever.getTolerance(1),flush=True)')
s=s.replace('lever=lever.cut(channel).cut(cy(bore,width+2,upper)).cut(cy(c[\'lever_end_bore_radius\'],width+2,V(*c[\'lever_end_center\'])))','lever=lever.cut(channel);print("channel",lever.getTolerance(1),flush=True)\n    lever=lever.cut(cy(bore,width+2,upper));print("pivot",lever.getTolerance(1),flush=True)\n    lever=lever.cut(cy(c[\'lever_end_bore_radius\'],width+2,V(*c[\'lever_end_center\'])));print("rod",lever.getTolerance(1),flush=True)')
s=s.replace('lever=lever.cut(cy(c[\'rivet_diameter\']/2+c[\'rivet_hole_clearance\'],width+2,V(x,0,z)))','lever=lever.cut(cy(c[\'rivet_diameter\']/2+c[\'rivet_hole_clearance\'],width+2,V(x,0,z)));print("rivet",x,z,lever.getTolerance(1),flush=True)')
s=s.replace("boss.Placement=screw_frame", "boss.rotate(V(),V(0,0,1),90);boss=Part.makeCompound([boss]);boss.Placement=screw_frame")
scope={};exec(compile(s,'instrumented_parts','exec'),scope)
c=json.loads((frozen/'cad__003_FullTank__experiments__drive_chains__transmission_high_brake_mechanism_study__controls.json').read_text())['controls'];front=json.loads((H/'transmission_high_brake_front_study/trial01/report.json').read_text());scope['parts'](c,front)
