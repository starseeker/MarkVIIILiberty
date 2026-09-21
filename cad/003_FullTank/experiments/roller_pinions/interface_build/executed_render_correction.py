"""Render the saved study bodies using their actual post-recompute shapes."""
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(ROOT/'render_runtime')).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha
from lib.visual_review import shaded
for folder,filename,view,direction in [
    ('interface_build','PinionInterfaceStudy.FCStd','section_context',(1,1,.4)),
    ('phase_build','PinionPhaseStudy.FCStd','axial',(0,1,0)),
]:
    out=ROOT/folder
    report=read(out/'report.json')
    path=out/filename
    assert sha(path)==report['native_sha256']
    rejected=out/'rejected_render_adapter'
    rejected.mkdir(exist_ok=True)
    for name in [view+'.png',view+'.svg','report.json']:
        if not (rejected/name).exists():
            shutil.copy2(out/name,rejected/name)
    doc=App.openDocument(str(path))
    doc.recompute()
    items=[]
    for obj in doc.Objects:
        if obj.TypeId!='PartDesign::Body':continue
        # Assigning a placed shape to a feature can bake its transform into
        # that feature. Use the reopened body's actual shape on BOTH sides
        # of the renderer adapter; mixing the earlier shape duplicates it.
        shape=obj.Shape.copy()
        items.append(dict(id=obj.Name,definition=obj.Name,target=obj,shape=shape,
                          system='RunningGear',representation='assembly'))
    shaded(items,out/(view+'.svg'),direction,
           'Pinion interface study | reopened native solids | installed fit unqualified')
    report['render_sha256']=sha(out/(view+'.png'))
    report['visual_review_status']='pending_corrected_native_render'
    report.pop('visual_review',None)
    report['render_correction']={
        'script_sha256':sha(__file__),
        'native_unchanged':True,
        'reason':'Original experimental adapter mixed pre-assignment placed shapes with post-recompute bodies, duplicating placement in the raster. Numerical native geometry checks were unaffected.',
        'rejected_artifacts':'rejected_render_adapter',
    }
    write(out/'report.json',report)
    App.closeDocument(doc.Name)
    shutil.copy2(__file__,out/'executed_render_correction.py')
print('PASS rendered reopened native study bodies without duplicate placement')
