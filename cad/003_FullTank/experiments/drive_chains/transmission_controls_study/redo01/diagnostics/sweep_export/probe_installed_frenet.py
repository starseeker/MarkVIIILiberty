from pathlib import Path
import sys
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(H),str(H.parents[1])]
from control_rebuild_io import App,Part,Saved,write
import Import
C=Saved(H/'transmission_controls_study/redo01/springs02');s=C.world('StarboardLowReturnSpring');D=R/'.work/control-redo-20260926/installed-frenet-probe';D.mkdir(exist_ok=False)
Part.setStaticValue('write.surfacecurve.mode',1);App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement',True)
doc=App.newDocument('Probe');o=doc.addObject('PartDesign::Feature','Spring');o.Shape=s;doc.recompute();f=D/'frenet.step';Import.export([o],str(f));App.closeDocument(doc.Name)
t=Part.Shape();t.read(str(f));r=dict(valid=t.isValid(),solids=len(t.Solids),tolerance=t.getTolerance(1))
if t.isValid():
 fuzz=min(1e-4,max(1e-7,s.getTolerance(1)+t.getTolerance(1)));r.update(missing=s.cut(t).Volume,added=t.cut(s).Volume,fuzzy_faces=[len(s.cut(t,fuzz).Faces),len(t.cut(s,fuzz).Faces)])
print(r,flush=True);write(D/'report.json',r)
