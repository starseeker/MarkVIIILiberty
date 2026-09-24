from pathlib import Path
import sys,json
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');H=ROOT/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H))
from transmission_brake_anchor_parts import parts
read=lambda p:json.loads(p.read_text())
c=read(H/'transmission_brake_anchor_study/controls.json')['controls'];b=read(H/'transmission_brake_band_study/controls.json')['controls'];l=read(H/'transmission_brake_link_study/trial03/report.json')
new,changed,d=parts(c,b,l);Part.setStaticValue('write.surfacecurve.mode',1);rows=[]
for name,s in {**new,**changed}.items():
 s.exportBrep(str(Path(name+'.brep')));s.exportStep(str(Path(name+'.step')));t=Part.Shape();t.read(str(Path(name+'.step')))
 missing=s.cut(t);added=t.cut(s)
 rows.append(dict(name=name,valid=s.isValid(),solids=len(s.Solids),step_valid=t.isValid(),step_solids=len(t.Solids),native_tolerance=s.getTolerance(1),step_tolerance=t.getTolerance(1),missing_mm3=missing.Volume,added_mm3=added.Volume))
 print(name,rows[-1],flush=True)
Path('report.json').write_text(json.dumps(dict(dimensions=d,checks=rows),indent=2)+'\n')
