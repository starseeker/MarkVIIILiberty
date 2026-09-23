import json,sys
from pathlib import Path
import FreeCAD as App,Part
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';b=h/'engine_crankshaft_build';sys.path.insert(0,str(root/'cad/003_FullTank'))
from lib.cad_build import leaves
r=json.loads((b/'report.json').read_text());doc=App.openDocument(str(b/'DrivetrainWithEngineCrankshaft.FCStd'));result={}
try:
 byid={i['id']:i for i in leaves(doc.Root)}
 for label,expected in [('Definitions',[(n,doc.getObject(n).Shape) for n in json.loads((b/'definition_order.json').read_text())]),('Installation',[(n,byid[n]['shape']) for n in r['exchange_ids']])]:
  loaded=Part.Shape();loaded.read(str(b/('EngineCrankshaft'+label+'.step')));remaining=[s for s in loaded.Solids];bad=[]
  for name,s in expected:
   if not remaining:bad.append({'name':name,'missing':True});continue
   one=s.Solids[0];i=min(range(len(remaining)),key=lambda i:(one.CenterOfMass-remaining[i].CenterOfMass).Length+abs(one.Volume-remaining[i].Volume)/max(1,one.Area));other=remaining.pop(i)
   if not other.isValid():
    record={'name':name,'native_valid':one.isValid(),'native_tolerance':one.getTolerance(1),'step_tolerance':other.getTolerance(1),'native_volume':one.Volume,'step_volume':other.Volume,'native_faces':len(one.Faces),'step_faces':len(other.Faces)};bad.append(record)
    other.exportBrep(str(root/'.work/engine-crankshaft'/('bad_step_'+label+'_'+name+'.brep')))
  result[label]={'valid':loaded.isValid(),'solids':len(loaded.Solids),'expected':len(expected),'bad':bad};print(label,json.dumps(result[label]),flush=True)
finally:App.closeDocument(doc.Name)
(root/'.work/engine-crankshaft/step_diagnostic.json').write_text(json.dumps(result,indent=2)+'\n')
