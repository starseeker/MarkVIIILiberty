"""Test one common disk/land hypothesis in isolated idler and drive fixtures."""
from pathlib import Path
import sys,subprocess,math
ROOT=Path(__file__).resolve().parent
STAGE=ROOT.parents[1]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
REFINED='--refined' in sys.argv
OUT=ROOT/('common_fit_refined_build' if REFINED else 'common_fit_build')
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker',*sys.argv[1:]],env=environment(OUT)).returncode)

import FreeCAD as App
import Part
import numpy as np
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import leaves
from lib.wheel_geometry import values,rivets
from lib.wheel_parts import build as wheel_part
from lib.roller_validation import bearing_face
from lib.visual_review import shaded

lock=fingerprint()
assert lock==read(ROOT/'authored_input_fingerprint.json'),'Archived study inputs changed; review and explicitly rebase before regeneration'
data=load();v=values(data)
# These values are an unintegrated hypothesis, not edits to accepted parameters.
changed=dict(v,wheel_disk_edge_inset=v['idler_diameter']/2-449.0,
             wheel_rim_depth=v['idler_diameter']/2-415.925,
             wheel_rim_rivet_inset=v['idler_diameter']/2-430.0)
if REFINED:
    changed.update(wheel_web_outer_radius=404.0,wheel_flange_outer_radius=410.0,wheel_short_pitch=25.0)
reference=ROOT/'reference_native';manifest=read(ROOT/'reference_native_manifest.json')
for path,digest in manifest['files'].items():assert sha(reference/path)==digest
base=App.openDocument(str(reference/'MarkVIII.FCStd'));existing=leaves(base.Root)
old={i['definition']:i['target'] for i in existing if i['definition'].startswith('wheel_')}
rim_document=App.openDocument(str(ROOT/'build/DriveRimStudy35.FCStd'))
drive_rim=rim_document.getObject('RimOuter').Shape.copy();drive_rim.Placement=App.Placement()
assert abs(drive_rim.optimalBoundingBox(False).YLength-50.8)<1e-6

doc=App.newDocument('CommonWheelInterfaceStudy')
library=doc.addObject('App::Part','Library')
root=doc.addObject('App::Part','Fixtures')
definitions={}
for key in ['rim','disk','boss','bush','diaphragm_x','diaphragm_y','rivet_short','rivet_long','rivet_rim']:
    if key in {'rim','disk'} or REFINED and key in {'diaphragm_x','diaphragm_y'}:
        obj=wheel_part(doc,'Candidate_'+key,{**changed,'role':key})
    else:
        obj=doc.addObject('PartDesign::Feature','Shared_'+key)
        obj.Shape=old['wheel_'+key].Shape.copy()
    library.addObject(obj)
    obj.addProperty('App::PropertyString','SourceDefinition');obj.SourceDefinition='wheel_'+key
    obj.addProperty('App::PropertyStringList','SurveyIdentities')
    obj.SurveyIdentities=data['definitions']['wheel_'+key]['survey_ids']
    assert obj.Shape.isValid() and len(obj.Shape.Solids)==1
    definitions[key]=obj
obj=doc.addObject('PartDesign::Feature','DriveRimHypothesis');obj.Shape=drive_rim;library.addObject(obj)
obj.addProperty('App::PropertyString','SourceRecord');obj.SourceRecord='SNL:164:027'
definitions['drive_rim']=obj

items=[];source_roles={}
for kind,offset in [('idler',0),('drive',2500)]:
    group=doc.addObject('App::Part',kind.title()+'Fixture');root.addObject(group)
    group.Placement.Base=App.Vector(offset,0,0)
    roles=[]
    def add(role,name,translation=(0,0,0),rotation=(0,0,0)):
        target=definitions[role];link=doc.addObject('App::Link',kind+'_'+name)
        link.setLink(target);group.addObject(link)
        link.Placement=App.Placement(App.Vector(*translation),App.Rotation(*rotation))
        shape=target.Shape.copy();shape.Placement=group.Placement.multiply(link.Placement).multiply(target.Shape.Placement)
        items.append(dict(id=link.Name,definition=role,shape=shape,target=target,
                          system='RunningGear',representation='assembly',fixture=kind))
        roles.append(role)
    face=changed['wheel_rim_center']-changed['wheel_rim_width']/2+changed['wheel_rim_land_stock']
    for side in [-1,1]:
        suffix='A' if side==-1 else 'B';rotation=(0,0,180) if side==-1 else (0,0,0)
        add('rim' if kind=='idler' else 'drive_rim','Rim'+suffix,(0,side*changed['wheel_rim_center'],0),rotation)
        add('disk','Disk'+suffix,(0,side*(face+changed['wheel_disk_stock']/2),0))
        add('bush','Bush'+suffix,(0,side*(changed['wheel_boss_length']-changed['wheel_bush_length'])/2,0),rotation)
    add('boss','Boss')
    for n in range(6):add('diaphragm_y' if n==5 else 'diaphragm_x','Diaphragm'+str(n),rotation=(0,n*60,0))
    for rivet in rivets(changed):add('rivet_'+rivet['role'],'Rivet_'+rivet['id'].replace('-','m'),rivet['translation'],rivet['rotation_deg'])
    source_roles[kind]={role:roles.count(role) for role in sorted(set(roles))}
    assert len(roles)==121
doc.recompute()

def bounds(shape):
    b=shape.optimalBoundingBox(False)
    return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
checks=[]
for kind in ['idler','drive']:
    print('CHECK',kind,flush=True,file=sys.stderr)
    group=[i for i in items if i['fixture']==kind];boxes=np.array([bounds(i['shape']) for i in group])
    tested=0;overlaps=[]
    for index,a in enumerate(group):
        b=boxes[index]
        near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
        for other in near:
            if other<=index:continue
            tested+=1;volume=a['shape'].common(group[other]['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=a['id'],b=group[other]['id'],volume_mm3=volume))
    by_id={i['id']:i for i in group};seats=[]
    for suffix in ['A','B']:
        a=by_id[kind+'_Rim'+suffix]['shape'];b=by_id[kind+'_Disk'+suffix]['shape']
        gap,area=bearing_face(a,b);seats.append(dict(side=suffix,gap_mm=gap,area_mm2=area))
        assert gap<1e-6 and area>1
    checks.append(dict(fixture=kind,components=len(group),source_roles=source_roles[kind],
                       candidate_pairs=tested,overlaps=overlaps,rim_disk_bearing_faces=seats))
    shaded(group,OUT/(kind+'.svg'),(1,1,.6),kind.title()+' common-interface hypothesis | isolated fixture, not an installed release')
native=OUT/'CommonWheelInterfaceStudy.FCStd';doc.saveAs(str(native))
assert fingerprint()==lock
write(OUT/'report.json',dict(complete=True,integrated=False,fixture_checks=checks,native_sha256=sha(native),
    authored_fingerprint=lock,executed_script_sha256=sha(Path(__file__)),
    variant='shortened_flange' if REFINED else 'initial_disk_land_only',
    parameter_hypotheses={k:value for k,value in changed.items() if value!=v[k]},
    shared_hypothesis_mm=dict(disk_radius=449,rim_land_inner_radius=415.925,rim_rivet_circle_radius=430),
    historical_profile_qualified=False,whole_vehicle_fit_qualified=False,
    limitations=['No shaft, bearing supports or roller-pinion installation in these fixtures.',
                 'Trial disk/rim dimensions have not been accepted into the authored parameter registry.',
                 'Rivet heads can overhang the annular land locally; structural adequacy is not established.',
                 'Source tooth-count conflict and exact casting/formed profiles remain unresolved.']))
for name in list(App.listDocuments()):App.closeDocument(name)
print('COMMON INTERFACE STUDY COMPLETE',flush=True,file=sys.stderr)
