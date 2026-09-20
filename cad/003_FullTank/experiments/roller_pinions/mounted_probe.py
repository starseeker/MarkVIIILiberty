"""One source-counted pinion with shaft/supports and experimental hull receivers."""
from pathlib import Path
from collections import Counter
import math
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
STAGE=ROOT.parents[1]
OUT=ROOT/'mounted_build'
sys.path.insert(0,str(STAGE))
from lib.runtime import environment
if '--worker' not in sys.argv:
    sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=environment(OUT)).returncode)
import FreeCAD as App
import Part
from lib.evidence import read,write,sha,fingerprint,database
from lib.model import load,point,datum_values
from lib.drive_mount_geometry import values,bearing_points,backing_points
from lib.drive_mount_parts import annulus,drill
from lib.idler_parts import block
from lib.track_parts import cylinder_y
from lib.wheel_parts import button_rivet
from lib.roller_parts import revolution,lines
from lib.roller_validation import bearing_face
from lib.visual_review import shaded

lock=fingerprint();data=load();a=values(data)
source_rows={r['record_id']:r for r in read(ROOT/'source_rows.json')['rows']}
rotor_path=ROOT/'pin_build/PinionWithPins.FCStd'
interface_path=ROOT/'interface_build/PinionInterfaceStudy.FCStd'
library_path=STAGE/'build/native/library/RunningGear.FCStd'
hull_path=STAGE/'build/native/library/HullStructure.FCStd'
inputs={str(p.relative_to(STAGE)):sha(p) for p in [rotor_path,interface_path,library_path,hull_path]}
assert sha(rotor_path)==read(ROOT/'pin_build/report.json')['native_sha256']
assert sha(interface_path)==read(ROOT/'interface_build/report.json')['native_sha256']
rotor=App.openDocument(str(rotor_path));interface=App.openDocument(str(interface_path))
library=App.openDocument(str(library_path));hull=App.openDocument(str(hull_path))
doc=App.newDocument('MountedPinionStudy')
root=doc.addObject('App::Part','PinionUnit');root.Label='98-leaf provisional pinion unit; historical fit unqualified'
rotating=doc.addObject('App::Part','RotatingAssembly');root.addObject(rotating)
shaft_group=doc.addObject('App::Part','ShaftAssembly');root.addObject(shaft_group)
mounts=doc.addObject('App::Part','MountsAndBushes');root.addObject(mounts)
for obj,rid in [(rotating,'SNL:144:002'),(shaft_group,'SNL:215:009')]:
    obj.addProperty('App::PropertyString','SourceRecord','Evidence');obj.SourceRecord=rid

p=dict(shaft_length=25.25*25.4,shaft_diameter=4.434*25.4,
       oil_bore_diameter=26.8,oil_radial_diameter=4.,bush_center=143.4,
       plug_shank_diameter=26.4,plug_insertion=12.7,plug_head_af=19.05,plug_head_stock=9.525,
       journal_diameter=a['journal_diameter'],journal_shoulder=a['shoulder'],
       bearing_running_gap=a['journal_running_gap'],rear_panel_seam_pixel_x=1642.,keyway_end_overrun=.1)
p['shaft_end']=p['shaft_length']/2;p['inner_face']=p['shaft_end']
p['inner_flange_stock']=p['inner_face']-a['outside']
write(OUT/'hypotheses.json',dict(status='unaccepted_mount_and_receiver_fixture',values_mm=p,
    printed=['shaft_length','shaft_diameter'],
    note='Common source-defined parts retain their native geometry. The printed 4.434-inch shaft diameter controls the central bush journals; reduced end journals and shoulders follow the inferred common M1407 interfaces. M1546 casting, oil drilling, 3/4-inch nominal pipe-thread envelope, plug head and counterbore are inferred. Inner plug is cut flush as HB132 specifies. The keyway is open through the shaft end to avoid a 0.0625 mm inferred lip. The wing/end panel seam is independent of the unchanged fuel-compartment backplate and provisionally moved from source pixel1630 to1642. No motion, seal, thread or retention strength is qualified.'))
definitions={};items={};contexts=[]
def definition(name,shape,rid,variant=''):
    shape=shape.removeSplitter();assert shape.isValid() and len(shape.Solids)==1,name
    obj=doc.addObject('PartDesign::Body','Def_'+name)
    obj.newObject('PartDesign::Feature','Reconstructed'+name).Shape=shape
    for k,v in [('SurveyId',source_rows[rid]['part_ids'][0]),('SourceRecord',rid),
                ('Coverage','partial'),('InstalledVariant',variant)]:
        obj.addProperty('App::PropertyString',k,'Evidence');setattr(obj,k,v)
    doc.recompute();obj.Visibility=False;definitions[name]=obj;return obj
def occurrence(name,target,pose=None,parent=mounts):
    pose=pose or App.Placement();obj=doc.addObject('App::Link',name);obj.setLink(target)
    obj.Placement=pose;parent.addObject(obj)
    s=target.Shape.copy();s.Placement=pose.multiply(s.Placement)
    items[name]=dict(id=name,definition=target.Name,target=target,shape=s,
                     system='RunningGear',representation='assembly')
    return obj
for role,rid in [('Casting','SNL:144:004'),('Roller','SNL:144:006'),
                 ('Pin','SNL:143:009'),('Cotter','SNL:143:010'),('Plug','SNL:143:011')]:
    shape=interface.CounterboredCasting.Shape if role=='Casting' else rotor.getObject('Def_'+role).Shape
    definition(role,shape.copy(),rid,'Inferred end counterbores' if role=='Casting' else '')
pin_groups={}
for obj in rotor.Objects:
    if obj.TypeId!='App::Link':continue
    role=obj.LinkedObject.Name.removeprefix('Def_');parent=rotating
    if role in {'Pin','Cotter','Plug'}:
        suffix=obj.Name.removeprefix(role)
        if suffix not in pin_groups:
            group=doc.addObject('App::Part','PinAssembly'+suffix);rotating.addObject(group)
            group.addProperty('App::PropertyString','SourceRecord','Evidence');group.SourceRecord='SNL:143:007'
            pin_groups[suffix]=group
        parent=pin_groups[suffix]
    occurrence(obj.Name,definitions[role],obj.Placement,parent)

# Printed central diameter and inferred reduced end journals for the common
# bearing. The rejected full-diameter ends could not enter M1407.
R=p['shaft_diameter']/2;j=p['journal_diameter']/2;s=p['journal_shoulder'];end=p['shaft_end']
shape=cylinder_y(R,2*s).fuse(cylinder_y(j,p['shaft_length']))
shape=shape.cut(cylinder_y(p['oil_bore_diameter']/2,p['shaft_length']+2))
shape=shape.cut(block(-a['key_width']/2,a['key_width']/2,a['key_start'],
                      p['shaft_end']+p['keyway_end_overrun'],a['key_bottom'],p['shaft_diameter']/2+1))
for sign in [-1,1]:
    shape=shape.cut(Part.makeCylinder(p['oil_radial_diameter']/2,p['shaft_diameter']/2+1,
                                     App.Vector(0,sign*p['bush_center'],0),App.Vector(0,0,1)))
definition('Shaft',shape,'SNL:215:011')
plug=cylinder_y(p['plug_shank_diameter']/2,p['plug_insertion'],y=-p['plug_insertion']/2)
definition('FlushShaftPlug',plug,'SNL:215:013','Inner head cut flush after installation per HB132')
plug=plug.fuse(Part.makeBox(p['plug_head_af'],p['plug_head_stock'],p['plug_head_af'],
                           App.Vector(-p['plug_head_af']/2,0,-p['plug_head_af']/2)))
definition('OuterShaftPlug',plug,'SNL:215:013','Outer supplied head retained for oil filling')
shape=annulus(a['barrel_radius'],p['journal_diameter']/2+p['bearing_running_gap'],a['shoulder'],p['inner_face'])
shape=shape.fuse(annulus(a['flange_radius'],p['journal_diameter']/2+p['bearing_running_gap'],a['outside'],p['inner_face']))
shape=drill(shape,bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])
definition('InnerBearing',shape,'SNL:18:007','Distinct M1546; inferred flange ends at flush shaft end')
rivet=button_rivet(doc,'TemporaryInnerRivet',.75*25.4,2.5*25.4,p['inner_face']-a['shell'])
definition('InnerRivet',rivet.Shape.copy(),'SNL:189:008','Inferred upset for pinion inner joint')
for child in list(rivet.Group):doc.removeObject(child.Name)
doc.removeObject(rivet.Name)
for role,key,rid in [('Key','drive_key','SNL:215:012'),('Bush','wheel_bush','SNL:43:011'),
                     ('OuterBearing','drive_outer_bearing','SNL:18:008'),
                     ('BackingPlate','drive_backing_plate','SNL:152:021'),
                     ('BearingScrew','drive_bearing_screw','SNL:201:008'),
                     ('BackingRivet','drive_backing_rivet','SNL:170:004')]:
    definition(role,library.getObject('Def_'+key).Shape.copy(),rid)
flip=App.Rotation(App.Vector(0,0,1),180)
pose=lambda xyz=(0,0,0),rotation=None:App.Placement(App.Vector(*xyz),rotation or App.Rotation())
occurrence('FixedShaft',definitions['Shaft'],parent=shaft_group)
occurrence('ShaftKey',definitions['Key'],parent=shaft_group)
occurrence('ShaftOuterPlug',definitions['OuterShaftPlug'],pose((0,p['shaft_end'],0)),shaft_group)
occurrence('ShaftInnerPlug',definitions['FlushShaftPlug'],pose((0,-p['shaft_end'],0),flip),shaft_group)
occurrence('OuterBearing',definitions['OuterBearing'])
occurrence('InnerBearing',definitions['InnerBearing'],pose(rotation=flip))
occurrence('BackingPlate',definitions['BackingPlate'])
for n,sign in enumerate([-1,1]):occurrence('Bush'+str(n),definitions['Bush'],pose((0,sign*p['bush_center'],0)))
for n,(x,z) in enumerate(bearing_points(a)):
    occurrence('OuterScrew'+str(n),definitions['BearingScrew'],pose((x,a['face'],z)))
    occurrence('InnerRivet'+str(n),definitions['InnerRivet'],pose((x,-(p['inner_face']+a['shell'])/2,z)))
for n,(x,z) in enumerate(backing_points(a)):
    occurrence('BackingRivet'+str(n),definitions['BackingRivet'],pose((x,(a['outside']+a['shell']-a['backing_stock'])/2,z),flip))
assert len(items)==98,len(items)

# Transfer stock across the inferred wing/end seam without adding/removing
# material. Keep the two source identities, all old bores and the outer outline.
sx,sz=point(data,'snl_2',[1614,422]);axis=App.Vector(sx,datum_values('port_drive',data)['translation'][1],sz)
new_seam=point(data,'snl_2',[p['rear_panel_seam_pixel_x'],422])[0]-sx
seams=[];receiver_checks=[]
for side,wing,end in [(-1,'hull_port_inner_rear_end','hull_port_inner_fuel_side'),
                       (1,'hull_port_rear_wing','hull_port_rear_end')]:
    first=hull.getObject('Def_'+wing).Shape.copy();second=hull.getObject('Def_'+end).Shape.copy()
    first.translate(-axis);second.translate(-axis);original=first.fuse(second).removeSplitter()
    front=original.common(block(new_seam,10000,-10000,10000,-10000,10000)).removeSplitter()
    rear=original.common(block(-10000,new_seam,-10000,10000,-10000,10000)).removeSplitter()
    reconstructed=front.fuse(rear).removeSplitter()
    difference=original.cut(reconstructed).Volume+reconstructed.cut(original).Volume
    assert difference<1e-5 and front.common(rear).Volume<1e-5
    holes=[cylinder_y(a['barrel_radius'],1000)]
    specs=[('bearing',bearing_points(a),a['bearing_screw_diameter']+a['fastener_hole_clearance'])]
    if side==1:specs.append(('backing',backing_points(a),a['backing_rivet_diameter']+a['fastener_hole_clearance']))
    for kind,points,diameter in specs:
        for n,(x,z) in enumerate(points):
            witness=cylinder_y(diameter/2,a['hull_side_thickness'],x=x,y=side*(a['shell']+a['hull_side_thickness']/2),z=z)
            ratio=witness.common(front).Volume/witness.Volume
            assert abs(ratio-1)<1e-6,(side,kind,n,ratio)
            receiver_checks.append(dict(side=side,kind=kind,index=n,stock_fraction=ratio))
            holes.append(cylinder_y(diameter/2,1000,x=x,z=z))
    front=front.cut(Part.makeCompound(holes)).removeSplitter()
    for key,shape in [(wing,front),(end,rear)]:
        assert shape.isValid() and len(shape.Solids)==1,key
        obj=doc.addObject('PartDesign::Body','Receiver_'+key)
        obj.newObject('PartDesign::Feature','ExperimentalReceiver').Shape=shape
        obj.addProperty('App::PropertyString','StudyRole','Evidence');obj.StudyRole='Receiving-hull context; outside 98-leaf pinion subtotal'
        contexts.append(dict(id=key,definition=key,target=obj,system='HullStructure',representation='inspection'))
    seams.append(dict(side=side,panel_pair=[wing,end],new_local_x_mm=new_seam,union_symmetric_difference_mm3=difference))
doc.recompute()
for item in contexts:item['shape']=item['target'].Shape.copy()
all_items=list(items.values())+contexts
overlaps=[];pairs=0
for i,first in enumerate(all_items):
    for second in all_items[i+1:]:
        if not first['shape'].BoundBox.intersect(second['shape'].BoundBox):continue
        volume=first['shape'].common(second['shape']).Volume;pairs+=1
        if volume>1e-5:overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
seats=[]
for first,second in [('OuterBearing','hull_port_rear_wing'),('BackingPlate','hull_port_rear_wing'),
                      ('InnerBearing','hull_port_inner_rear_end')]:
    b=next(i for i in contexts if i['id']==second);gap,area=bearing_face(items[first]['shape'],b['shape'])
    assert gap<1e-5 and area>1,(first,gap,area);seats.append(dict(a=first,b=second,gap_mm=gap,area_mm2=area))
for name in ['OuterBearing','InnerBearing']:
    gap,area=bearing_face(items['FixedShaft']['shape'],items[name]['shape'])
    assert gap<1e-5 and area>1,(name,gap,area)
    seats.append(dict(a='FixedShaft',b=name,gap_mm=gap,area_mm2=area))
gaps=[]
for n in [0,1]:
    gap=items['Bush'+str(n)]['shape'].distToShape(items['FixedShaft']['shape'])[0]
    assert abs(gap-(data['values']['wheel_bush_id'].value-p['shaft_diameter'])/2)<1e-5
    gaps.append(gap)
counts=Counter(i['target'].SurveyId for i in items.values())
assert counts[source_rows['SNL:215:013']['part_ids'][0]]==2
assert len([o for o in shaft_group.Group if o.TypeId=='App::Link'])==4
assert len(pin_groups)==18
path=OUT/'MountedPinionStudy.FCStd';doc.saveAs(str(path))
shaded(list(items.values()),OUT/'oblique.svg',(1,1,.6),'Pinion with shaft and mounts | 98 source-counted leaves | experimental fit')
shaded(all_items,OUT/'receivers.svg',(0,-1,0),'Pinion receiver study | inferred panel seam and owned attachment holes')
write(OUT/'report.json',dict(status='unaccepted_mounted_pinion_fixture',passed=not overlaps,
    physical_occurrences=98,source_identity_counts=dict(counts),source_shaft_leaves=4,rotor_leaves=73,
    hull_context_solids=4,candidate_pairs=pairs,overlaps=overlaps,
    receiver_stock_checks=receiver_checks,seam_transfers=seams,bearing_seats=seats,shaft_bush_radial_gaps_mm=gaps,
    native_sha256=sha(path),native_inputs=inputs,authored_fingerprint=lock,script_sha256=sha(__file__),
    render_sha256={n+'.png':sha(OUT/(n+'.png')) for n in ['oblique','receivers']},visual_review_status='pending',
    main_model_changed=False,gear_engagement_qualified=False,formed_cotter_retention_qualified=False,
    historical_fit_qualified=False,source_bom_total_reconciled=False))
shutil.copy2(__file__,OUT/'executed_probe.py');assert fingerprint()==lock
for relative,digest in inputs.items():assert sha(STAGE/relative)==digest
for name in list(App.listDocuments()):App.closeDocument(name)
assert not overlaps,overlaps
print('PASS 98-leaf pinion fixture, four receiving panels,',pairs,'candidate material pairs',flush=True)
