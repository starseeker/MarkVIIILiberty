"""Isolated static rim study; does not mutate the tank's authored records."""
from pathlib import Path
import sys, subprocess, math

STAGE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
OUT=Path(__file__).resolve().parent/'build'
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)

import FreeCAD as App
import Part
import numpy as np
from types import SimpleNamespace
from lib.evidence import read,write,sha,fingerprint
from lib.model import load
from lib.cad_build import leaves,frame
from lib.wheel_geometry import values as wheel_values
from lib.visual_review import shaded

lock=fingerprint()
assert lock==read(Path(__file__).resolve().parent/'authored_input_fingerprint.json'),'Archived study inputs changed; review and explicitly rebase before regeneration'
data=load()
baseline=Path(__file__).resolve().parent/'reference_native/MarkVIII.FCStd'
assert baseline.is_file(),'The reviewed lower-support nominal experiment is required'
base=App.openDocument(str(baseline));items=leaves(base.Root)
manifest=read(baseline.parent.parent/'reference_native_manifest.json')
for relative,digest in manifest['files'].items():assert sha(baseline.parent/relative)==digest
assert all(baseline.parent.resolve() in Path(i['target'].Document.FileName).resolve().parents for i in items)
physical=[i for i in items if i['representation']=='assembly']
def bounds(shape):
    b=shape.optimalBoundingBox(False)
    return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
boxes=np.array([bounds(i['shape']) for i in physical])

v=wheel_values(data)
outer=data['values']['drive_diameter'].value/2
inner=data['values']['drive_inner_diameter'].value/2
width=50.8
# Deliberate hypotheses for comparison, not a derived or qualified gear form.
root_radius=462.5;groove_radius=25.7;lip_inner_radius=450.0
rivet_circle=430.0

def cylinder(radius,length,x=0,y=0,z=0):
    return Part.makeCylinder(radius,length,App.Vector(x,y,z),App.Vector(0,1,0))

def rim(count):
    shape=cylinder(outer,width,y=-width/2).cut(cylinder(inner,width+2,y=-width/2-1))
    # The outer axial half clears an adjacent disk; all dimensions here remain
    # inferred except the printed OD, ID and tooth width.
    shape=shape.cut(cylinder(lip_inner_radius,width/2+1,y=0))
    tools=[]
    for n in range(count):
        a=2*math.pi*n/count;radius=root_radius+groove_radius
        tools.append(cylinder(groove_radius,width+2,x=radius*math.sin(a),
                              y=-width/2-1,z=radius*math.cos(a)))
    for n in range(24):
        a=math.radians(7.5+15*n)
        tools.append(cylinder((v['wheel_rim_rivet_diameter']+v['wheel_rivet_hole_clearance'])/2,
                              width+2,x=rivet_circle*math.sin(a),y=-width/2-1,z=rivet_circle*math.cos(a)))
    shape=shape.cut(Part.makeCompound(tools)).removeSplitter()
    assert shape.isValid() and len(shape.Solids)==1
    return shape

drive=frame('port_drive',data)
def installed(shape,side,phase):
    placement=App.Placement(App.Vector(0,side*v['wheel_rim_center'],0),
                            App.Rotation(App.Vector(0,1,0),phase).multiply(
                                App.Rotation(App.Vector(1,0,0),180 if side==-1 else 0)))
    result=shape.copy();result.Placement=drive.multiply(placement)
    return result

results=[]
for count in [35,37]:
    print('START rim hypothesis',count,flush=True,file=sys.stderr)
    local=rim(count);phases=[]
    for step in range(8):
        phase=360/count*step/8;contacts=[];tested=0
        for side in [-1,1]:
            shape=installed(local,side,phase);b=bounds(shape)
            near=np.where(np.all(boxes[:,:3]<=b[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=b[:3]-1e-7,axis=1))[0]
            for index in near:
                other=physical[index];tested+=1;volume=shape.common(other['shape']).Volume
                if volume>1e-5:contacts.append(dict(side=side,other=other['id'],volume_mm3=volume))
        phases.append(dict(phase_deg=phase,candidate_pairs=tested,overlaps=contacts,
                           total_overlap_mm3=sum(x['volume_mm3'] for x in contacts)))
    best=min(phases,key=lambda r:r['total_overlap_mm3'])
    doc=App.newDocument('DriveRimStudy'+str(count));draw=[]
    disk=next(i['target'].Shape for i in items if i['definition']=='wheel_disk')
    disk_contacts=[]
    for side in [-1,1]:
        shape=installed(local,side,best['phase_deg'])
        obj=doc.addObject('PartDesign::Feature','Rim'+('Inner' if side==-1 else 'Outer'))
        obj.Shape=shape;obj.addProperty('App::PropertyInteger','ToothHypothesis');obj.ToothHypothesis=count
        obj.addProperty('App::PropertyString','Qualification');obj.Qualification='Unintegrated static experiment; profiles and engagement unqualified'
        draw.append(dict(id=obj.Name,definition=obj.Name,shape=shape,target=SimpleNamespace(Shape=shape),
                         system='RunningGear',representation='assembly'))
        target=disk.copy()
        y=side*(v['wheel_rim_center']-v['wheel_rim_width']/2+v['wheel_rim_land_stock']+v['wheel_disk_stock']/2)
        target.Placement=drive.multiply(App.Placement(App.Vector(0,y,0),App.Rotation())).multiply(disk.Placement)
        disk_contacts.append(dict(side=side,overlap_mm3=shape.common(target).Volume,
            radial_tip_margin_mm=outer-(data['values']['idler_diameter'].value/2-v['wheel_disk_edge_inset']),
            rim_rivet_circle_mm=rivet_circle,current_disk_rivet_circle_mm=data['values']['idler_diameter'].value/2-v['wheel_rim_rivet_inset']))
    doc.recompute();native=OUT/('DriveRimStudy'+str(count)+'.FCStd');doc.saveAs(str(native))
    shaded(draw,OUT/('rims_'+str(count)+'.svg'),(1,1,.6),
           'Drive rims | '+str(count)+'-tooth hypothesis | isolated unqualified study')
    result=dict(teeth=count,phases=phases,least_overlap_phase=best,current_idler_disk_checks=disk_contacts,
                native=str(native.relative_to(OUT)),native_sha256=sha(native))
    results.append(result)
    write(OUT/'report.json',dict(complete=False,baseline_native_sha256=sha(baseline),
        authored_fingerprint=lock,geometry_integrated=False,results=results))
    print('END rim hypothesis',count,'least overlap',best['total_overlap_mm3'],flush=True,file=sys.stderr)
assert fingerprint()==lock
write(OUT/'report.json',dict(complete=True,baseline_native_sha256=sha(baseline),authored_fingerprint=lock,
    geometry_integrated=False,historical_profile_qualified=False,continuous_engagement_qualified=False,
    executed_script_sha256=sha(Path(__file__)),reference_native_manifest_sha256=sha(baseline.parent.parent/'reference_native_manifest.json'),
    inferred_dimensions_mm=dict(root_radius=root_radius,groove_radius=groove_radius,
                                lip_inner_radius=lip_inner_radius,rivet_circle=rivet_circle),results=results))
for name in list(App.listDocuments()):App.closeDocument(name)
print('RIM STUDY COMPLETE',flush=True,file=sys.stderr)
