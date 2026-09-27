import sys
from pathlib import Path
h=Path('/home/cyapp/MarkVIIILiberty/cad/003_FullTank/experiments/drive_chains');sys.path.insert(0,str(h))
from control_rebuild_io_v2 import *
s=Saved(h/'coupled_driver_integration/integrated01');doc=App.openDocument(str(s.native))
for name in ['SeatBackGuide0','ClutchCenterRodWirePath']:
 v=s.report['nonphysical_guides'][name];src=App.openDocument(str(ROOT/v['source_native']));x,y=src.getObject(v['source_object']),doc.getObject(name)
 props={k:getattr(y,k) for k in y.PropertiesList if y.getGroupOfProperty(k)=='Reconstruction'}
 f1,f2=Path('/tmp/source-guide.brep'),Path('/tmp/target-guide.brep');x.Shape.exportBrep(str(f1));y.Shape.exportBrep(str(f2))
 print(name,'bytes',sha(f1)==sha(f2),'solids',len(y.Shape.Solids),'group',y in doc.getObject(v['group']).Group,'properties',props==v['properties'])
 print('properties',props,v['properties']);print('placements',list(x.Shape.Placement.toMatrix().A),list(y.Shape.Placement.toMatrix().A));print('lengths',x.Shape.Length,y.Shape.Length)
 import difflib
 print('diff',list(difflib.unified_diff(f1.read_text().splitlines(),f2.read_text().splitlines()))[:35]);App.closeDocument(src.Name)
App.closeDocument(doc.Name)
