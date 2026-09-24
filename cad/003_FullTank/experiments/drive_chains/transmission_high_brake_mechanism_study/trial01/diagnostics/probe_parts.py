import sys,json
from pathlib import Path
import FreeCAD as A
import Part
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H));from transmission_high_brake_mechanism_parts import parts
c=json.loads((H/'transmission_high_brake_mechanism_study/controls.json').read_text())['controls'];r=json.loads((H/'transmission_high_brake_front_study/trial01/report.json').read_text());s,d,curves=parts(c,r)
p=R/'.work/high-brake-mechanism/probe01';p.mkdir()
for n,v in s.items():v.exportBrep(str(p/(n+'.brep')));print(n,len(v.Solids),v.isValid(),v.Volume,flush=True)
(p/'details.json').write_text(json.dumps(d,indent=2))
