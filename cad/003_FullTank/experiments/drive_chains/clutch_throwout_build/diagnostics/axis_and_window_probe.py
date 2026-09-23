from pathlib import Path
import sys,json,math
ROOT=Path('/home/cyapp/MarkVIIILiberty');HERE=ROOT/'cad/003_FullTank/experiments/drive_chains'
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
import FreeCAD as A,Part
from clutch_throwout_parts import parts
from case_joint_mass import calculator
c=json.loads((HERE/'clutch_throwout_controls.json').read_text())['controls']
p,_,d=parts(c)
mass=calculator(Path.cwd()/'mass')
rows=[]
for key in ['bearing_outer','bearing_cage']:
 s=p[key];s.exportBrep(key+'.brep');s.exportStep(key+'.step');t=Part.Shape();t.read(key+'.step')
 a=mass(s,key+'_native');b=mass(t,key+'_step')
 row=dict(key=key,native_valid=s.isValid(),step_valid=t.isValid(),native_mass=a,step_mass=b,missing=s.cut(t).Volume,added=t.cut(s).Volume,native_faces=len(s.Faces),step_faces=len(t.Faces),tolerances=[s.getTolerance(1),t.getTolerance(1)])
 if key=='bearing_outer':row['analytic_volume']=math.pi*c['bearing_width']*((c['bearing_diameter']/2)**2-d['spherical_outer_race_radius']**2)+math.pi*c['bearing_width']**3/12
 rows.append(row);print(json.dumps(row),flush=True)
Path('result.json').write_text(json.dumps(rows,indent=2))
