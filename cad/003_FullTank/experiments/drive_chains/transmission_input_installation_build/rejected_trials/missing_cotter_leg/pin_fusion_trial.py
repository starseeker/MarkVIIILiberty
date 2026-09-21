import sys,subprocess,math
from pathlib import Path
stage=Path('cad/003_FullTank').resolve();sys.path.insert(0,str(stage));sys.path.insert(0,str(stage/'experiments/drive_chains'))
from lib import runtime
from lib.evidence import read
out=Path('.work/transmission-input-installation-study').resolve()
if '--worker' not in sys.argv:
 with (out/'pin_fusion_trial.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out/'pin_fusion'),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
 App,Gui=runtime.start_gui();import Part
 c=read(stage/'experiments/drive_chains/transmission_input_installation_controls.json')['mount']
 half=c['cotter_center_spacing']/2;w=(c['cotter_diameter']-c['cotter_center_spacing'])/2;head=-9.6;bend=9.8;r=1.5;angle=math.pi/3;tail=25.4-19.4-r*angle
 legs=[]
 for sign in [-1,1]:
  start=App.Vector(0,head,sign*half);end=App.Vector(0,bend+r*math.sin(angle),sign*(half+r*(1-math.cos(angle))));axis=App.Vector(0,math.cos(angle),sign*math.sin(angle))
  t=Part.makeTorus(r,w,App.Vector(),App.Vector(0,0,1),-180,180,60);t.rotate(App.Vector(),App.Vector(0,1,0),sign*90);t.translate(App.Vector(0,bend,sign*(half+r)))
  s=Part.makeCylinder(w,19.4,start,App.Vector(0,1,0)).fuse(t).fuse(Part.makeCylinder(w,tail,end,axis)).removeSplitter();legs.append(s)
  print('leg',sign,s.Volume,len(s.Solids),flush=True)
 eye=2.2;top=head-1.8
 points=[App.Vector(0,head,-half),App.Vector(0,top,-eye)]+[App.Vector(0,top-eye*math.sin(a),eye*math.cos(a)) for a in [math.pi-i*math.pi/16 for i in range(1,17)]]+[App.Vector(0,head,half)]
 pieces=[Part.makeCylinder(w,(b-a).Length,a,b-a) for a,b in zip(points,points[1:])]+[Part.makeSphere(w,p) for p in points]
 eye_s=pieces[0].multiFuse(pieces[1:]).removeSplitter();print('eye',eye_s.Volume,len(eye_s.Solids),eye_s.isValid(),flush=True)
 for label,s in [('grouped',eye_s.fuse(legs[0]).fuse(legs[1]).removeSplitter()),('group_multifuse',eye_s.multiFuse(legs).removeSplitter())]:
  print(label,'vol',s.Volume,'solids',len(s.Solids),'valid',s.isValid(),'legs_missing',[a.cut(s).Volume for a in legs],flush=True)
  f=out/(label+'.step');s.exportStep(str(f));v=Part.Shape();v.read(str(f));print(label,'step',s.cut(v).Volume,v.cut(s).Volume,flush=True)
 t=Part.makeTorus(eye,w,App.Vector(),App.Vector(0,0,1),-180,180,180);t.rotate(App.Vector(),App.Vector(1,0,-1),180);t.translate(App.Vector(0,top,0))
 e=t
 for sign in [-1,1]:
  start=App.Vector(0,top,sign*eye);end=App.Vector(0,head+.2,sign*half);v=end-start;axis=v/v.Length
  lead=Part.makeCylinder(w,v.Length+.4,start-axis*.2,axis)
  e=e.fuse(lead)
 s=e.fuse(legs[0]).fuse(legs[1]).removeSplitter()
 print('analytic eye',e.Volume,len(e.Solids),'fullpin',s.Volume,len(s.Solids),s.isValid(),'legs_missing',[a.cut(s).Volume for a in legs],flush=True)
 f=out/'analytic_eye_pin.step';s.exportStep(str(f));v=Part.Shape();v.read(str(f));print('analytic step',s.cut(v).Volume,v.cut(s).Volume,flush=True)
 s.exportBrep(str(out/'analytic_eye_pin.brep'))
finally:runtime.close()
