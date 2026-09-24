from pathlib import Path
import json
import FreeCAD as App
import Part,Import
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
groups={n:App.ParamGet('User parameter:BaseApp/Preferences/Mod/'+p) for n,p in [('import','Import'),('step','Part/STEP')]}
rows=[]
for test in ('default','import','step'):
 for n,g in groups.items():g.SetBool('ExportKeepPlacement',n==test)
 doc=App.newDocument('ExportProbe');f=doc.addObject('PartDesign::Feature','Stock');f.Shape=Part.makeBox(10,20,30);f.Placement=App.Placement(App.Vector(100,200,300),App.Rotation());doc.recompute();path=out/(test+'.step');Import.export([f],str(path));s=Part.Shape();s.read(str(path));rows.append(dict(test=test,centroid=list(s.Solids[0].CenterOfMass)));App.closeDocument(doc.Name)
(out/'report.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows,flush=True)
