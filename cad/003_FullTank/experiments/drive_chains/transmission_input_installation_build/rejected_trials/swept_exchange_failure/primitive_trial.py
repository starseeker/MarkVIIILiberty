import sys,subprocess,math
from pathlib import Path
stage=Path('cad/003_FullTank').resolve();sys.path.insert(0,str(stage));sys.path.insert(0,str(stage/'experiments/drive_chains'))
from lib import runtime
from lib.evidence import read,write
out=Path('.work/transmission-input-installation-study').resolve()
if '--worker' not in sys.argv:
 with (out/'primitive_trial.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out/'primitive_trial'),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 c=read(stage/'experiments/drive_chains/transmission_input_installation_controls.json')['mount']
 half=c['cotter_center_spacing']/2;wire=(c['cotter_diameter']-c['cotter_center_spacing'])/2;head=-c['crown_radius']-c['cotter_head_gap'];bend=c['crown_radius']+c['cotter_exit_gap'];r=c['cotter_bend_radius'];ang=math.radians(c['cotter_bend_angle']);tail=c['cotter_length']-(bend-head)-r*ang
 for sign in [-1,1]:
  p=lambda t:App.Vector(0,bend+r*math.sin(t),sign*(half+r*(1-math.cos(t))))
  start=App.Vector(0,head,sign*half);end=p(ang)+App.Vector(0,math.cos(ang),sign*math.sin(ang))*tail
  path=Part.Wire([Part.makeLine(start,p(0)),Part.Arc(p(0),p(ang/2),p(ang)).toShape(),Part.makeLine(p(ang),end)])
  sweep=path.makePipeShell([Part.Wire([Part.makeCircle(wire,start,App.Vector(0,1,0))])],True,False)
  torus=Part.makeTorus(r,wire,App.Vector(),App.Vector(0,0,1),-180,180,c['cotter_bend_angle']);torus.rotate(App.Vector(),App.Vector(0,1,0),sign*90);torus.translate(App.Vector(0,bend,sign*(half+r)))
  primitive=Part.makeCylinder(wire,bend-head,start,App.Vector(0,1,0)).fuse(torus).fuse(Part.makeCylinder(wire,tail,p(ang),end-p(ang))).removeSplitter()
  for label,s in [('sweep',sweep),('primitive',primitive)]:
   f=out/f'{label}_leg{sign}.step';s.exportStep(str(f));v=Part.Shape();v.read(str(f))
   print(label,sign,'valid',s.isValid(),'solidcount',len(s.Solids),'volume',s.Volume,'expected',math.pi*wire**2*c['cotter_length'],'stepVolume',v.Volume,'missing',s.cut(v).Volume,'added',v.cut(s).Volume,'faces',[(type(f.Surface).__name__,f.Orientation) for f in s.Faces],flush=True)
finally:runtime.close()
