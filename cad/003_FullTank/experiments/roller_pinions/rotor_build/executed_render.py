"""Render the preserved incomplete pinion-rotor experiment from native solids."""
from pathlib import Path
import sys,subprocess,shutil
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'rotor_build';sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.visual_review import shaded
report=read(OUT/'report.json');native=OUT/'PartialPinionRotor.FCStd';assert sha(native)==report['native_sha256']
doc=App.openDocument(str(native));items=[]
for obj in doc.Rotor.Group:
 target=obj.LinkedObject;shape=target.Shape.copy();shape.Placement=obj.Placement.multiply(shape.Placement)
 items.append(dict(id=obj.Name,definition=target.Name,target=target,shape=shape,system='RunningGear',representation='assembly'))
for name,direction in [('oblique',(1,1,.6)),('axial',(0,1,0))]:
 shaded(items,OUT/(name+'.svg'),direction,'Unaccepted pinion rotor | casting and18 rollers |54 pin-assembly leaves omitted')
report['generated_rasters']={name+'.png':sha(OUT/(name+'.png')) for name in ['oblique','axial']};report['visual_review_status']='pending';write(OUT/'report.json',report)
shutil.copy2(__file__,OUT/'executed_render.py');App.closeDocument(doc.Name)
