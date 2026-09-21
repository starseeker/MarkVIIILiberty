import sys,math,json
from pathlib import Path
root=Path('cad/003_FullTank/experiments/drive_chains').resolve();sys.path.insert(0,str(root))
import FreeCAD as App,Part
from transmission_bevel_gear_parts import thrust_bearing
from transmission_core_parts import cylinder
c={k:v['value'] for k,v in json.loads((root/'transmission_bevel_gear_controls.json').read_text())['controls'].items()}
station=82.73142857142857;center=station+20
baseline=thrust_bearing(c,station)[0]['cage'];report=[]
for key,axis in [('axial',App.Vector(0,1,0)),('radial',None)]:
 cage=cylinder(76,center-3,center+3).cut(cylinder(54,center-6,center+6))
 for n in range(16):
  angle=2*math.pi*n/16;rad=App.Vector(math.cos(angle),0,math.sin(angle));pos=App.Vector(65*rad.x,center,65*rad.z)
  cage=cage.cut(Part.makeSphere(10.2,pos,axis if axis is not None else rad))
 cage=cage.removeSplitter();step=Path('.work/transmission-bevel-gear-study')/('cage_'+key+'.step');cage.exportStep(str(step.resolve()))
 b=Part.Shape();b.read(str(step.resolve()));b=b.Solids[0]
 row=dict(method=key,native_valid=cage.isValid(),step_valid=b.isValid(),native_tol=cage.getTolerance(1),step_tol=b.getTolerance(1),
  baseline_missing=baseline.cut(cage).Volume,baseline_extra=cage.cut(baseline).Volume,step_missing=cage.cut(b).Volume,step_extra=b.cut(cage).Volume)
 print(row,flush=True);report.append(row)
Path('.work/transmission-bevel-gear-study/cage_exchange_report.json').write_text(json.dumps(report,indent=2)+'\n')
