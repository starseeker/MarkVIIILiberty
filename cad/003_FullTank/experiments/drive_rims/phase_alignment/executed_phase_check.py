from pathlib import Path
import sys,subprocess
sys.path.insert(0,'/home/cyapp/MarkVIIILiberty/cad/003_FullTank')
from lib.runtime import environment
out=Path('/tmp/drive-phase-check')
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(out)).returncode)
import FreeCAD as App
from lib.model import load
from lib.cad_build import leaves,frame
from lib.wheel_validation import paired_rim_alignment
from lib.evidence import write,fingerprint
from lib.visual_review import shaded
x=load();doc=App.openDocument('/tmp/drive-wheel-staggered-before-phase/native/MarkVIII.FCStd')
items=leaves(doc.Root);selected=[i for i in items if i['id'].startswith(('PortDrive_','StarboardDrive_'))]
try:paired_rim_alignment(x,selected)
except ValueError as e:
 assert 'staggered' in str(e);old_error=str(e)
else:raise AssertionError('Old staggered rings accepted')
for i in selected:
 if i['definition']=='drive_rim':i['shape'].Placement=frame(i['id'],x).multiply(i['target'].Shape.Placement)
aligned=paired_rim_alignment(x,selected)
shaded([i for i in selected if i['id'].startswith('PortDrive_')],out/'aligned.svg',(1,1,.6),'Paired drive rims | corrected axial reversal preserves tooth phase')
first=next(i for i in selected if i['definition']=='drive_rim')
center=frame('port_drive',x).Base
transform=App.Placement(center,App.Rotation(App.Vector(0,1,0),1)).multiply(App.Placement(-center,App.Rotation()))
first['shape'].Placement=transform.multiply(first['shape'].Placement)
try:paired_rim_alignment(x,selected)
except ValueError as e:
 assert 'staggered' in str(e);negative_error=str(e)
else:raise AssertionError('One-degree phase error accepted')
write(out/'report.json',dict(passed=True,old_stagger_rejected=old_error,aligned=aligned,one_degree_error_rejected=negative_error,authored_fingerprint=fingerprint()))
App.closeDocument(doc.Name)
print('Native paired-rim alignment and negative phase checks passed',flush=True)
