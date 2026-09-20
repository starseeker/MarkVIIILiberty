from pathlib import Path
import sys,subprocess
sys.path.insert(0,'/home/cyapp/MarkVIIILiberty/cad/003_FullTank')
from lib.runtime import environment
from lib.evidence import STAGE,read,write,sha
out=STAGE/'experiments/drive_mounts/receiver_build'
if '--worker' not in sys.argv:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(out)).returncode)
import FreeCAD as App
from lib.visual_review import shaded
native=out/'CurrentDriveReceiverDiagnostic.FCStd';doc=App.openDocument(str(native))
items=[dict(id=o.Name,definition=o.Name,shape=o.Shape,target=o,system='HullStructure' if o.Name.startswith('hull_') else 'RunningGear',representation='assembly') for o in doc.Diagnostic.Group]
shaded(items,out/'current_receivers.svg',(1,1,.7),'Current rear hull and drive mount diagnostic | undrilled receivers; source mapping unresolved')
write(out/'render_provenance.json',dict(native_sha256=sha(native),script_sha256=sha(Path(__file__)),
    image_sha256=sha(out/'current_receivers.png'),note='Direct installed targets use unique mesh-cache keys; contacts in current_report.json unchanged.'))
App.closeDocument(doc.Name)
