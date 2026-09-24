import json,sys
from pathlib import Path
import FreeCAD as A
import Part
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(h));from transmission_high_brake_front_parts import parts,rotate_theta
p=h/'transmission_high_brake_joint_study/trial01';m=json.loads((p/'isolated/manifest.json').read_text());r=json.loads((p/'report.json').read_text());c=json.loads((h/'transmission_high_brake_front_study/controls.json').read_text())['controls'];bands={}
for role in ['long','short']:
 s=Part.Shape();s.read(m['definitions']['Def_HighBrake_'+role+'_band']['brep_path']);bands[role]=s
new,changed,d=parts(c,r,bands)
for role in ['long','short']:
 s=new[role+'_end'];b=changed['Def_HighBrake_'+role+'_band'];b.Placement=A.Placement(A.Vector(),rotate_theta(r['details']['placement_angles_rad'][role]));rad=199.23125
 fs=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-rad)<1e-6];gs=[f for f in b.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-rad)<1e-6]
 for i,f in enumerate(fs):
  missing=f.cut(Part.makeCompound(gs));print(role,i,len(missing.Faces),missing.Area,flush=True)
 s.exportBrep(str(root/('.work/high-brake-front/default_seam_'+role+'.brep')))
