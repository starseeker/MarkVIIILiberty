from pathlib import Path
import sys,subprocess,copy
STAGE=Path('/tmp/drive-mount-integration-repo/cad/003_FullTank');OUT=STAGE/'plug_envelope_check'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.model import load
from lib.evidence import write,sha,fingerprint
from lib.drive_mount_geometry import values,child_datum
from lib.drive_mount_parts import build
from lib.roller_parts import build as roller_build
from lib.drive_mount_validation import plug_envelope
from lib.parameters import resolve
results=[];data=load()
for trial,delta in [('nominal',0),('shaft_length',2)]:
 changed=copy.deepcopy(data);changed['parameters']['drive_mount_shaft_length']['value']+=delta
 changed['values']=resolve(changed['parameters']);a=values(changed)
 doc=App.newDocument('Plug_'+trial)
 shaft=build(doc,'Shaft',{**a,'role':'shaft'}).Shape
 plug=roller_build(doc,'Plug',{**{k:v.value for k,v in changed['values'].items()},'role':'plug'}).Shape
 for hand in ['Port','Starboard']:
  frame=App.Placement(App.Vector(10,20,30),App.Rotation(0 if hand=='Port' else 180,0,0))
  d=child_datum({'parent':hand+'Drive_Unit000_ShaftAssembly','drive_mount_child':'oil_plug'},changed)
  p=plug.copy();p.Placement=frame.multiply(App.Placement(App.Vector(*d['translation']),App.Rotation(*d['rotation_deg'])))
  s=shaft.copy();s.Placement=frame.multiply(s.Placement)
  report=plug_envelope(s,p,frame,a)
  shifted=p.copy();shifted.translate(frame.Rotation.multVec(App.Vector(0,.2,0)))
  try:plug_envelope(s,shifted,frame,a)
  except ValueError as e:report['displaced_plug_rejected']=str(e)
  else:raise AssertionError('Displaced plug wrongly accepted')
  results.append(dict(trial=trial,hand=hand,**report))
 App.closeDocument(doc.Name)
write(OUT/'report.json',dict(passed=True,cases=results,authored_fingerprint=fingerprint(),script_sha256=sha(__file__)))
print('PASS four native insertion checks and four displaced-plug rejections')
