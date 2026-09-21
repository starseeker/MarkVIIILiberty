"""Bounded static fit study; preserve rejected phases and explicit axis offsets."""
from pathlib import Path
import math
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'static_fit'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from scipy.optimize import minimize_scalar
from lib.evidence import read,write,sha,fingerprint
from lib.visual_review import shaded
lock=fingerprint();prior=read(ROOT/'phase_build/report.json')
for relative,digest in prior['native_inputs'].items():assert sha(STAGE/relative)==digest
rotor=App.openDocument(str(ROOT/'pin_build/PinionWithPins.FCStd'))
library=App.openDocument(str(STAGE/'build/native/library/RunningGear.FCStd'))
rim=library.Def_drive_rim.Shape.copy();rim.translate(App.Vector(0,190,0))
roller=rotor.Def_Roller.Shape.copy();a=read(ROOT/'rotor_build/hypotheses.json')['values_mm']
center=App.Vector(*prior['relative_axis_mm']);unit=App.Vector(center);unit.normalize()
def bank(phase,offset):
    for n in range(9):
        t=math.radians(phase+n*40);s=roller.copy()
        s.translate(center+unit*offset+App.Vector(a['roller_circle']*math.sin(t),190,a['roller_circle']*math.cos(t)))
        yield n,s
rows=[]
def measure(phase,offset):
    pairs=[]
    for n,s in bank(phase,offset):
        if not s.BoundBox.intersect(rim.BoundBox):continue
        volume=s.common(rim).Volume
        pairs.append(dict(roller=n,overlap_mm3=volume,gap_mm=s.distToShape(rim)[0] if volume<1e-5 else 0))
    row=dict(phase_deg=float(phase),axis_offset_mm=offset,
             overlap_mm3=sum(p['overlap_mm3'] for p in pairs),
             minimum_gap_mm=min(p['gap_mm'] for p in pairs),pairs=pairs)
    rows.append(row)
    write(OUT/'measured_samples.json',dict(script_sha256=sha(__file__),samples=rows))
    return row
fit=minimize_scalar(lambda phase:measure(phase,0.)['overlap_mm3'],
                    bounds=(17.2,17.3),method='bounded',options={'xatol':.0001,'maxiter':25})
angle=round(float(fit.x),4)
selected=measure(angle,0.)
# A small explicit static clearance is allowed within the stated source-pick
# uncertainty. It is not hidden in the calibration or advertised as a gear fit.
if selected['overlap_mm3']>1e-5 or selected['minimum_gap_mm']<.1:
    for offset in [.25,.5,1.,2.]:
        trial=measure(angle,offset)
        if trial['overlap_mm3']<1e-5 and trial['minimum_gap_mm']>=.1:
            selected=trial;break
    else:
        print(rows[-5:],flush=True)
        raise ValueError('No bounded static sample clears; inspect saved assumptions')
doc=App.newDocument('StaticPinionFit');items=[]
for name,shape in [('DriveRim',rim)]+[('Roller'+str(n),s) for n,s in bank(selected['phase_deg'],selected['axis_offset_mm'])]:
    obj=doc.addObject('PartDesign::Body',name);obj.newObject('PartDesign::Feature','Native'+name).Shape=shape
    items.append(dict(id=name,definition=name,target=obj,system='RunningGear',representation='assembly'))
doc.recompute()
for item in items:item['shape']=item['target'].Shape.copy()
path=OUT/'StaticPinionFit.FCStd';doc.saveAs(str(path))
shaded(items,OUT/'axial.svg',(0,1,0),'Static pinion fit study | documented inferred placement | gearing unqualified')
write(OUT/'report.json',dict(status='candidate_static_pinion_fit',passed=True,selected=selected,samples=rows,
    nominal_relative_axis_mm=list(center),inferred_axis_offset_vector_mm=list(unit*selected['axis_offset_mm']),
    corrected_relative_axis_mm=list(center+unit*selected['axis_offset_mm']),
    source_pixel=[1614,422],pick_uncertainty_pixels=3,source_pick_and_calibration_changed=False,
    authored_fingerprint=lock,native_inputs=prior['native_inputs'],script_sha256=sha(__file__),
    native_sha256=sha(path),render_sha256=sha(OUT/'axial.png'),visual_review_status='pending',
    main_model_changed=False,complete_rotor_checked=False,continuous_engagement_qualified=False))
shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
for name in list(App.listDocuments()):App.closeDocument(name)
print('PASS candidate static sample',selected,flush=True)
