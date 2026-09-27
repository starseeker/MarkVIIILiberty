from pathlib import Path
import sys,json
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(H),str(H.parents[1])]
from control_rebuild_io import App,Part,Saved,write
D=H/'transmission_controls_study/redo01';rows=[]
for name in ['springs03','springs_variation03']:
 f=D/name/'exchange01/RebuiltControlAdditionsInstalled.step'
 if not f.exists():continue
 s=Part.Shape();s.read(str(f));r=dict(candidate=name,valid=s.isValid(),solids=len(s.Solids),checks=[])
 for n,t in enumerate(s.Solids):
  q=dict(index=n,valid=t.isValid(),tolerance=t.getTolerance(1),centroid=list(t.CenterOfMass),volume=t.Volume)
  if not q['valid']:
   try:q['check']=t.check(True)
   except Exception as ex:q['check']=repr(ex)
  r['checks'].append(q)
 rows.append(r)
write(R/'.work/control-redo-20260926/installed_step_diagnostic.json',rows)
print(json.dumps(rows,indent=2),flush=True)
