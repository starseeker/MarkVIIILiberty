import sys,subprocess,math
from pathlib import Path
repo=Path(__file__).resolve().parents[2];stage=repo/'cad/003_FullTank';root=stage/'experiments/drive_chains';out=Path(__file__).parent
sys.path[:0]=[str(stage),str(root)]
from lib import runtime
if '--worker' not in sys.argv:
 with (out/'finger_exchange.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out/'finger_runtime'),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 from lib.evidence import read,write
 from transmission_vertical_parts import lever_blank,box
 from case_joint_mass import calculator
 c=read(root/'transmission_vertical_controls.json')['controls'];x,y=c['shaft_xy'];rx,z=c['rod_axis_xz'];reach=rx-x
 low=c['upper_bearing_base_z']-c['axial_gap']-c['lever_hub_height'];kz=low+c['lever_hub_height']/2
 r=c['finger_radius'];neck=c['finger_neck_radius'];start=reach-c['finger_neck_setback']-c['finger_overlap'];join=reach-math.sqrt(r*r-neck*neck)
 a=App.Vector(start,0,0);b=App.Vector(start,0,neck);d=App.Vector(join,0,neck);e=App.Vector(reach+r,0,0)
 profile=Part.Wire([Part.makeLine(a,b),Part.makeLine(b,d),Part.Arc(d,App.Vector(reach,0,r),e).toShape(),Part.makeLine(e,a)])
 finger=Part.Face(profile).revolve(App.Vector(),App.Vector(1,0,0));finger.translate(App.Vector(0,0,z))
 shape=lever_blank(c,reach-c['finger_neck_setback'],z,low).fuse(finger)
 shape=shape.cut(box(c['journal_radius']-1,c['journal_radius']+c['key_exposure']+c['key_gap'],-c['key_width']/2-c['key_gap'],c['key_width']/2+c['key_gap'],kz-c['key_radius']-c['key_gap'],kz+c['key_radius']+c['key_gap'])).removeSplitter()
 shape.translate(App.Vector(x+1825.2303627827532,y,849.2335104357661))
 shape.exportBrep(str(out/'revolved_finger_lever.brep'));shape.exportStep(str(out/'revolved_finger_lever.step'))
 other=Part.Shape();other.read(str(out/'revolved_finger_lever.step'));mass=calculator(out/'finger_runtime/mass')
 mn=mass(shape,'native');ms=mass(other,'step')
 r=dict(native_valid=shape.isValid(),step_valid=other.isValid(),native_tol=shape.getTolerance(1),step_tol=other.getTolerance(1),native=mn,step=ms,dc=(App.Vector(*mn['center_mm'])-App.Vector(*ms['center_mm'])).Length,missing=shape.cut(other).Volume,added=other.cut(shape).Volume)
 write(out/'finger_exchange.json',r);print(r,flush=True)
finally:runtime.close()
