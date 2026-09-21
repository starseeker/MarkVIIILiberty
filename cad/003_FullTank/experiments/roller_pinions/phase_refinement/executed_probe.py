"""Refine the smallest-overlap native phase interval without moving either axis."""
from pathlib import Path
import math
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
STAGE=ROOT.parents[1]
OUT=ROOT/'phase_refinement'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha,fingerprint
from lib.visual_review import shaded
lock=fingerprint()
prior=read(ROOT/'phase_build/report.json')
for relative,digest in prior['native_inputs'].items():assert sha(STAGE/relative)==digest
rotor=App.openDocument(str(ROOT/'pin_build/PinionWithPins.FCStd'))
library=App.openDocument(str(STAGE/'build/native/library/RunningGear.FCStd'))
rim=library.Def_drive_rim.Shape.copy();rim.translate(App.Vector(0,190,0))
roller=rotor.Def_Roller.Shape.copy()
a=read(ROOT/'rotor_build/hypotheses.json')['values_mm']
center=App.Vector(*prior['relative_axis_mm'])
def bank(phase,radial_offset=0.):
    axis=center+center.normalize()*radial_offset if radial_offset else center
    for n in range(9):
        t=math.radians(phase+n*40);s=roller.copy()
        s.translate(axis+App.Vector(a['roller_circle']*math.sin(t),190,a['roller_circle']*math.cos(t)))
        yield n,s
rows=[]
for phase in [16.9+n*.025 for n in range(33)]:
    pairs=[]
    for n,s in bank(phase):
        if not s.BoundBox.intersect(rim.BoundBox):continue
        volume=s.common(rim).Volume
        pairs.append(dict(roller=n,overlap_mm3=volume,gap_mm=s.distToShape(rim)[0] if volume<1e-5 else 0))
    rows.append(dict(phase_deg=phase,overlap_mm3=sum(p['overlap_mm3'] for p in pairs),
                     minimum_gap_mm=min(p['gap_mm'] for p in pairs),pairs=pairs))
    if len(rows)%10==0:print('Refined',len(rows),'phases',flush=True)
clear=[r for r in rows if r['overlap_mm3']<1e-5]
selected=max(clear,key=lambda r:r['minimum_gap_mm']) if clear else min(rows,key=lambda r:r['overlap_mm3'])
doc=App.newDocument('RefinedPinionPhase')
items=[]
for name,shape in [('DriveRim',rim)]+[('Roller'+str(n),s) for n,s in bank(selected['phase_deg'])]:
    obj=doc.addObject('PartDesign::Body',name);obj.newObject('PartDesign::Feature','Native'+name).Shape=shape
    items.append(dict(id=name,definition=name,target=obj,system='RunningGear',representation='assembly'))
doc.recompute()
for item in items:item['shape']=item['target'].Shape.copy()
path=OUT/'RefinedPinionPhase.FCStd';doc.saveAs(str(path))
shaded(items,OUT/'axial.svg',(0,1,0),'Refined static pinion angle | axes unchanged | continuous engagement unqualified')
write(OUT/'report.json',dict(status='unaccepted_refined_static_phase',checks_completed=True,
    selected=selected,samples=rows,nonintersecting_samples=len(clear),axes_changed=False,
    authored_fingerprint=lock,native_inputs=prior['native_inputs'],script_sha256=sha(__file__),
    native_sha256=sha(path),render_sha256=sha(OUT/'axial.png'),visual_review_status='pending',
    continuous_engagement_qualified=False,complete_rotor_checked=False))
shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
for name in list(App.listDocuments()):App.closeDocument(name)
print('PASS refined screen;',len(clear),'clear samples;',selected,flush=True)
