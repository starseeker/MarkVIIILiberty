"""Display-only X section through the lower chamber and drain, before and after."""
from pathlib import Path
import hashlib,json,sys
from types import SimpleNamespace
import FreeCAD as App
import Part
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';stage=h.parents[1]
sys.path[:0]=[str(h),str(stage)]
from detail_render import shaded_detail
from lib.cad_build import COLORS
COLORS.update(PumpCasting=(.63,.69,.65),Intrusion=(.85,.35,.2))
out=Path.cwd();images={};V=App.Vector
for label,base in [('previous',h/'engine_water_pump_mounting_study'),('corrected',h/'engine_water_pump_passage_study')]:
    r=json.loads((base/'report.json').read_text());path=base/r['native_file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==r['native_sha256']
    doc=App.openDocument(str(path));body=doc.getObject(r['definitions']['body']).Shape.copy();App.closeDocument(doc.Name)
    # Identical slab and orthographic camera for a fair local silhouette comparison.
    section=body.common(Part.makeBox(.5,90,55,V(153,-45,-90)))
    rows=[dict(id=label,shape=section,target=SimpleNamespace(Shape=section),definition=label,system='PumpCasting',representation='assembly')]
    shaded_detail(rows,out/(label+'.svg'),(1,0,0),label.capitalize()+' drain section | X=153..153.5 mm; display cut only',deflection=.015)
    images[label+'.png']=hashlib.sha256((out/(label+'.png')).read_bytes()).hexdigest()
(out/'receipt.json').write_text(json.dumps(dict(images=images,display_only=True,section_box_mm=[153,153.5,-45,45,-90,-35],camera=[1,0,0]),indent=2)+'\n')
