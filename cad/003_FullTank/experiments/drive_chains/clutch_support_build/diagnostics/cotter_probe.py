import json,sys,os
from pathlib import Path
import FreeCAD as App,Part
HERE=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'inputs'),str(HERE)]
from transmission_input_installation_parts import formed_pin
from case_joint_mass import calculator
s,d=formed_pin(dict(cotter_center_spacing=1.65,cotter_diameter=3.175,crown_radius=8,cotter_head_gap=.8,cotter_exit_gap=.8,cotter_bend_radius=2,cotter_bend_angle=35,cotter_length=22.225,cotter_eye_radius=3,cotter_eye_rise=2,cotter_eye_join_overlap=.03))
s.rotate(App.Vector(),App.Vector(0,0,1),-90)
os.environ['MARKVIII_RESOLVED_FREECAD']=str(Path('/snap/freecad/current').resolve())
mass=calculator(Path('probe_mass'))
rows=[]
for name,rot,shift in [('definition',0,[0,0,0]),('main',0,[2708.680362782753,229,676.3278631357661]),('aux',180,[2868.680362782753,229,676.3278631357661])]:
 a=s.copy();a.rotate(App.Vector(),App.Vector(0,1,0),rot);a.translate(App.Vector(*shift))
 a.exportStep(name+'.step');b=Part.Shape();b.read(name+'.step');ma=mass(a,name+'_native');mb=mass(b,name+'_step')
 row=dict(name=name,valid=b.isValid(),missing=a.cut(b).Volume,added=b.cut(a).Volume,dv=abs(ma['volume_mm3']-mb['volume_mm3']),dc=(App.Vector(*ma['center_mm'])-App.Vector(*mb['center_mm'])).Length)
 rows.append(row);print(row,flush=True)
Path('cotter_probe.json').write_text(json.dumps(rows,indent=2)+'\n')
assert all(r['valid'] and abs(r['missing'])<1e-5 and abs(r['added'])<1e-5 and r['dc']<1e-6 for r in rows)
