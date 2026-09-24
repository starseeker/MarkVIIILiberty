"""Locate the failed preservation witness and inspect Boolean tool validity."""
import json
from pathlib import Path
import sys
import FreeCAD as App
import Part

ROOT=Path('/home/cyapp/MarkVIIILiberty')
H=ROOT/'cad/003_FullTank/experiments/drive_chains'
sys.path.insert(0,str(H))
from transmission_support_parts import box
from transmission_stud_parts import cylinder_x
OUT=ROOT/'.work/resume-2026-09-24/material_probe'
OUT.mkdir(exist_ok=True)
B=H/'transmission_bracket_mount_study/trial01'
r=json.loads((B/'report.json').read_text())
new=json.loads((B/'isolated/manifest.json').read_text())
old=json.loads((ROOT/r['source_native']).parent.joinpath('isolated/manifest.json').read_text())
def load(p):
 s=Part.Shape();s.read(str(p));return s
def details(s):
 b=s.BoundBox
 return dict(null=s.isNull(),valid=s.isValid(),solids=len(s.Solids),faces=len(s.Faces),volume=s.Volume,
             bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
records={}
for role,radius in [('inner',88),('outer',79)]:
 name='Def_FixedBearing_'+role+'_bracket'
 before=load(old['definitions'][name]['brep_path']);after=load(new['definitions'][name]['brep_path'])
 lost=before.common(box(-radius-8,300,-300,300,-200,200)).cut(after)
 lost.exportBrep(str(OUT/(role+'_witness_loss.brep')))
 records[role]={'witness_loss':details(lost),'lost_solids':[details(s) for s in lost.Solids]}
 removed=before.cut(after)
 if role=='inner':
  original=load(B/'baseline_shapes/inner_original_base.brep')
  revised=load(B/'baseline_shapes/inner_revised_base.brep')
  allowed=original.cut(revised)
  records[role]['allowed_web_revision']=details(allowed)
  records[role]['witness_loss_outside_declared_web_revision']=details(lost.cut(allowed))
  removed=removed.cut(allowed)
 records[role]['removal_after_web_allowance']=details(removed)
 records[role]['tool_sequence']=[]
 for j in [j for j in r['details']['joints'] if j['role']==role]:
  y,z=j['y_local_mm'],j['z_local_mm']
  ts=[('spotface',cylinder_x(18.5,r['details']['head_seat_x_mm'],0,y,z)),
      ('bore',cylinder_x(9.675,r['mount_controls']['frame_front_x']-1,r['details']['head_seat_x_mm']+1,y,z))]
  for label,tool in ts:
   item=dict(kind=label,y=y,z=z,before=details(removed),tool=details(tool))
   try:
    if removed.Solids:removed=removed.cut(tool)
    item['after']=details(removed)
   except Exception as e:
    item['error']=str(e)
   records[role]['tool_sequence'].append(item)
(OUT/'results.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2),flush=True)
