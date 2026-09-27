from pathlib import Path
import sys,math,json
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(H),str(H.parents[1])]
from control_rebuild_io import Saved,App,Part,write
import Import
C=Saved(H/'transmission_controls_study/redo01/springs01');key='Def_ControlReturnSpring_PortLow_Redo'
path=Part.Shape();path.read(str(C.folder/(key+'_centerline.brep')));edges=path.Edges;D=R/'.work/control-redo-20260926/sweep-exchange-probe';D.mkdir(exist_ok=False)
Part.setStaticValue('write.surfacecurve.mode',1);App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement',True)
results=[]
for mode in ['whole_parallel','pieces_frenet','pieces_parallel']:
 try:
  if mode=='whole_parallel':
   e=edges[0];prof=Part.Wire([Part.makeCircle(1.3,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))]);s=Part.Wire(edges).makePipeShell([prof],True,False)
  else:
   pipes=[]
   for e in edges:
    prof=Part.Wire([Part.makeCircle(1.3,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))]);p=Part.Wire([e]).makePipeShell([prof],True,mode=='pieces_frenet');pipes.append(p)
   s=pipes[0].multiFuse(pipes[1:])
  s.exportBrep(str(D/(mode+'.brep')))
  print(mode,'native',s.isValid(),len(s.Solids),s.getTolerance(1),s.Volume,flush=True)
  doc=App.newDocument('Probe');o=doc.addObject('PartDesign::Feature','Spring');o.Shape=s;doc.recompute();f=D/(mode+'.step');Import.export([o],str(f));App.closeDocument(doc.Name)
  t=Part.Shape();t.read(str(f));fuzz=min(1e-4,max(1e-7,s.getTolerance(1)+t.getTolerance(1)))
  missing,added=s.cut(t),t.cut(s);row=dict(mode=mode,valid=s.isValid() and t.isValid(),solids=[len(s.Solids),len(t.Solids)],tolerances=[s.getTolerance(1),t.getTolerance(1)],missing=missing.Volume,added=added.Volume,fuzzy_faces=[len(s.cut(t,fuzz).Faces),len(t.cut(s,fuzz).Faces)])
  print(row,flush=True);results.append(row)
 except Exception as e:print(mode,repr(e),flush=True);results.append(dict(mode=mode,error=repr(e)))
 write(D/'report.json',results)
