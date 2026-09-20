"""Both handed pinion units against both complete unchanged driving wheels."""
from pathlib import Path
import math
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent;STAGE=ROOT.parents[1];OUT=ROOT/'installation_build'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
from lib.evidence import read,write,sha,fingerprint
from lib.model import load,datum_values
from lib.cad_build import frame
from lib.visual_review import shaded

lock=fingerprint();data=load();fit=read(ROOT/'static_fit/report.json')
mount_report=read(ROOT/'mounted_build/report.json')
assert fit['passed'] and mount_report['passed']
mount_path=ROOT/'mounted_build/MountedPinionStudy.FCStd'
library_path=STAGE/'build/native/library/RunningGear.FCStd'
assert sha(mount_path)==mount_report['native_sha256']
assert sha(library_path)==fit['native_inputs']['build/native/library/RunningGear.FCStd']
inputs={str(p.relative_to(STAGE)):sha(p) for p in [mount_path,library_path,ROOT/'static_fit/report.json']}
source=App.openDocument(str(mount_path));library=App.openDocument(str(library_path))
doc=App.newDocument('PairedPinionDriveStudy');defs={};items=[]
def definition(key,target):
    if key in defs:return defs[key]
    obj=doc.addObject('PartDesign::Body','Def_'+key)
    obj.newObject('PartDesign::Feature','Native'+key).Shape=target.Shape.copy()
    if 'SurveyId' in target.PropertiesList:
        obj.addProperty('App::PropertyString','SurveyId','Evidence');obj.SurveyId=target.SurveyId
    doc.recompute();obj.Visibility=False;defs[key]=obj;return obj
def add(name,target,placement,parent,family,hand):
    obj=doc.addObject('App::Link',name);obj.setLink(target);obj.Placement=placement;parent.addObject(obj)
    shape=target.Shape.copy();shape.Placement=placement.multiply(shape.Placement)
    items.append(dict(id=name,definition=target.Name,target=target,shape=shape,
                      system='RunningGear',representation='assembly',family=family,hand=hand))
links=[o for o in source.Objects if o.TypeId=='App::Link'];assert len(links)==98
rotating_roles={'Casting','Roller','Pin','Cotter','Plug'}
for label,sign in [('Port',1),('Starboard',-1)]:
    parent=doc.addObject('App::Part',label+'DriveAndPinion')
    old=doc.addObject('App::Part',label+'Drive');parent.addObject(old)
    new=doc.addObject('App::Part',label+'Pinion');parent.addObject(new)
    for spec in data['occurrences']:
        if not spec['id'].startswith(label+'Drive_') or not spec['definition']:continue
        target=definition('Drive_'+spec['definition'],library.getObject('Def_'+spec['definition']))
        add(spec['id'],target,frame(spec['frame'],data),old,'drive',label)
    origin=datum_values(label.lower()+'_drive',data)['translation']
    delta=fit['corrected_relative_axis_mm']
    axis=App.Vector(origin[0]+delta[0],origin[1],origin[2]+delta[2])
    handed=App.Rotation(App.Vector(0,0,1),0 if sign==1 else 180)
    base=App.Placement(axis,handed)
    # The starboard hand frame reverses X/Y. Reverse the local phase so both
    # nine-roller banks retain the same installed XZ relation to the wheel.
    phase=App.Placement(App.Vector(),App.Rotation(App.Vector(0,1,0),sign*fit['selected']['phase_deg']))
    for link in links:
        role=link.LinkedObject.Name.removeprefix('Def_')
        target=definition('Pinion_'+role,link.LinkedObject)
        placement=base.multiply(phase if role in rotating_roles else App.Placement()).multiply(link.Placement)
        add(label+'Pinion_'+link.Name,target,placement,new,'pinion',label)
doc.recompute()
counts={label:{family:sum(i['hand']==label and i['family']==family for i in items)
               for family in ['drive','pinion']} for label in ['Port','Starboard']}
assert all(v=={'drive':149,'pinion':98} for v in counts.values()),counts
overlaps=[];pairs=[];ring_gaps=[]
for label in ['Port','Starboard']:
    old=[i for i in items if i['hand']==label and i['family']=='drive']
    new=[i for i in items if i['hand']==label and i['family']=='pinion']
    for first in new:
        for second in old:
            if not first['shape'].BoundBox.intersect(second['shape'].BoundBox):continue
            volume=first['shape'].common(second['shape']).Volume
            row=dict(a=first['id'],b=second['id'],overlap_mm3=volume)
            pairs.append(row)
            if volume>1e-5:overlaps.append(row)
    # Explicitly check all 18 rollers against both actual installed ring solids,
    # independently of the earlier one-bank sample and its bounding-box filter.
    rings=[i for i in old if i['definition']=='Def_Drive_drive_rim'];assert len(rings)==2
    rollers=[i for i in new if i['definition']=='Def_Pinion_Roller'];assert len(rollers)==18
    for ring in rings:
        distances=[dict(roller=r['id'],gap_mm=r['shape'].distToShape(ring['shape'])[0]) for r in rollers]
        nearest=min(distances,key=lambda row:row['gap_mm'])
        ring_gaps.append(dict(ring=ring['id'],nearest=nearest,all_roller_gaps=distances))
        assert abs(nearest['gap_mm']-fit['selected']['minimum_gap_mm'])<1e-5,(label,nearest)
    print('Measured',label,'complete driving wheel and pinion',flush=True)
path=OUT/'PairedPinionDriveStudy.FCStd';doc.saveAs(str(path))
port=[i for i in items if i['hand']=='Port']
for name,direction in [('oblique',(1,1,.6)),('axial',(0,1,0)),('section_plan',(0,0,1))]:
    shaded(port,OUT/(name+'.svg'),direction,'Pinion and complete driving wheel | static fit study | motion unqualified')
write(OUT/'report.json',dict(status='experimental_paired_pinion_drive_installation',passed=not overlaps,
    counts=counts,physical_occurrences=len(items),candidate_pairs=len(pairs),overlaps=overlaps,
    roller_ring_checks=ring_gaps,static_fit=fit['selected'],
    native_sha256=sha(path),native_inputs=inputs,script_sha256=sha(__file__),authored_fingerprint=lock,
    render_sha256={n+'.png':sha(OUT/(n+'.png')) for n in ['oblique','axial','section_plan']},
    visual_review_status='pending',main_model_changed=False,complete_wheels_checked=True,
    complete_tank_checked=False,hull_receiver_revision_at_corrected_axis_checked=False,
    continuous_engagement_qualified=False,formed_cotter_retention_qualified=False))
shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
for name in list(App.listDocuments()):App.closeDocument(name)
assert not overlaps,overlaps
print('PASS paired complete drive/pinion study;',len(pairs),'cross-family material pairs',flush=True)
