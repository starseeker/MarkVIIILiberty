from pathlib import Path
import sys
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(H),str(H.parents[1])]
from control_rebuild_io import App,Part,Saved,write,pose
import Import
C=Saved(H/'transmission_controls_study/redo01/springs03');name='StarboardLowReturnSpring';row=C.rows[name];local=C.definition(row['definition']);world=C.world(name)
D=R/'.work/control-redo-20260926/placed-export-nested';D.mkdir(exist_ok=False)
Part.setStaticValue('write.surfacecurve.mode',1);App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import').SetBool('ExportKeepPlacement',True)
results=[]
for mode in ['part_frame']:
 doc=App.newDocument('PlacedProbe')
 if mode=='part_frame':
  root=doc.addObject('App::Part','Root');o=doc.addObject('PartDesign::Feature','Spring');o.Shape=local;root.addObject(o);root.Placement=pose(row['frame']);wrapper=doc.addObject('App::Part','Wrapper');wrapper.addObject(root);objects=[wrapper]
 elif mode=='link_frame':
  root=doc.addObject('App::Part','Root');o=doc.addObject('PartDesign::Feature','Spring');o.Shape=local
  link=doc.addObject('App::Link','Installed');link.setLink(o);link.LinkPlacement=pose(row['frame']);root.addObject(link);objects=[root]
 else:
  o=doc.addObject('PartDesign::Feature','Spring');o.Shape=local.transformGeometry(App.Matrix(*row['frame']));objects=[o]
 doc.recompute();f=D/(mode+'.step');Import.export(objects,str(f));App.closeDocument(doc.Name)
 t=Part.Shape();t.read(str(f));r=dict(mode=mode,valid=t.isValid(),solids=len(t.Solids),NAU=f.read_text().count('NEXT_ASSEMBLY_USAGE_OCCURRENCE'),tolerance=t.getTolerance(1))
 if t.isValid():
  fuzz=min(1e-4,max(1e-7,world.getTolerance(1)+t.getTolerance(1)));r.update(missing=world.cut(t).Volume,added=t.cut(world).Volume,fuzzy_faces=[len(world.cut(t,fuzz).Faces),len(t.cut(world,fuzz).Faces)])
 print(r,flush=True);results.append(r);write(D/'report.json',results)
