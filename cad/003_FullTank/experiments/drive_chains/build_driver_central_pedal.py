"""Save a connected central pedal, bridle, journals and complete pin hardware."""
import argparse,copy,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_central_pedal_parts import pedal,bridle,suspension,spacer
from driver_operating_handle_parts_v2 import hardware
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--stock-offset',type=float,default=0);a=p.parse_args()
c=copy.deepcopy(read(a.controls));c['bridle_stock_mm']+=a.stock_offset
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
review=ROOT/c['source_review'];assert sha(review)==c['source_review_sha256']
assert all(sha(ROOT/f)==h for f,h in read(review)['source_hashes'].items())
main=App.Vector(*parent.report['details']['main_world_mm']);swing=App.Vector(*parent.report['details']['swing_world_mm'])
rear_world=swing+App.Vector(*c['bridle_rear_relative_swing_mm']);rear=rear_world-main;front=main+App.Vector(*c['pedal_output_relative_main_mm'])
shapes={};props={};specs={};guides={}
def add(key,shape,mark,records,status):
    shapes[key]=shape;props[key]=dict(SourcePartMark=mark,SourceRecords=records,Representation='reconstruction_trial',ReconstructionStatus=status+' Central-connection hypothesis; complete foot-brake mechanism remains unresolved.',ParameterUpdate='Regenerate '+Path(__file__).name+' using recorded controls; no live expressions.')
def put(name,key,frame,role):specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner='DriverCentralPedalHypothesis',role=role)
def translated(point):return App.Placement(point,App.Rotation())
q,pd=pedal(c);key='Def_DriverBrakePedal_M764A';add(key,q,'M764A',['SNL:071:009','HB:149','SNL:plate06'],'HB35-1/4in overall and8x5in pad transferred provisionally to laterM764A. Overall datum along the unrotated long-arm axis is an interpretation. Pose, I-section stock, rounded pad and forked bell arm inferred.');put('DriverBrakePedal',key,translated(main),'pedal')
q,paths,bd=bridle(c,rear);key='Def_DriverBrakeBridle_M765';add(key,q,'M765',['SNL:042:025','SNL:071:024','HB:plate113','SNL:plate06'],'U-shaped branches, central tongue and two rear ears. Spline profile, stock, transverse span and joint assignments are inferred.');put('DriverBrakeBridle',key,translated(main),'bridle')
for name,path in paths.items():path.Placement=translated(main);guides['Bridle'+name]=path
link,sleeve=suspension(c)
for name,key,q,mark,records,role in [('DriverBrakeSuspension','Def_DriverBrakeSuspension_M770',link,'M770',['SNL:119:028','SNL:071:028'],'suspension'),('DriverBrakeSuspensionSleeve','Def_DriverBrakeSuspensionSleeve_M795',sleeve,'M795',['SNL:217:027','SNL:071:029'],'sleeve')]:
    add(key,q,mark,records,'Rear-shaft sleeve and two-journal suspension; sleeve location, oil holes and complete stock inferred.');put(name,key,translated(swing),role)
key='Def_DriverBrakeDistance_M766';add(key,spacer(c),'M766',['SNL:071:026'],'Clamped rear distance tube between bridle ears; suspension lower journal rotates around it. Stack assignment, stock and bores inferred.');put('DriverBrakeDistance',key,translated(rear_world),'spacer')
hc=copy.deepcopy(read(ROOT/c['hardware_controls']));assert sha(ROOT/c['hardware_controls'])==c['hardware_controls_sha256']
hc.update(fulcrum_stock_mm=2*bd['rear_outside_y_mm'],pivot_side_gap_mm=0,handle_stock_mm=0,bolt_length_mm=c['bridle_bolt_length_mm'])
hc['cotter']['cotter_length']=38.1
parts,hd=hardware(hc)
for role,mark,records in [('bolt','M767',['SNL:023:024']),('cotter','3/16x1-1/2in cotter',['SNL:023:026'])]:
    key='Def_DriverBrakeBridle'+role.title();add(key,parts[role],mark,records,'Complete7/8in nominal bolt and full38.1mm cotter. Bolt length/head, cross-hole datum and cotter formed state inferred; source cotter stock retained.')
orient=App.Rotation(App.Vector(0,0,1),App.Vector(0,-1,0));seat=rear_world+App.Vector(0,bd['rear_outside_y_mm'],0)
put('DriverBrakeBridleBolt','Def_DriverBrakeBridleBolt',App.Placement(seat,orient),'bolt')
put('DriverBrakeBridleCotter','Def_DriverBrakeBridleCotter',App.Placement(seat+App.Vector(0,-hd['cotter_axis_mm'],0),orient),'cotter')
# Preserve source metadata for actual reused definitions and unchanged shafts.
doc=App.openDocument(str(parent.native))
def reuse(key):
    shapes[key]=parent.definition(key);obj=doc.getObject(key);props[key]={k:getattr(obj,k) for k in obj.PropertiesList if obj.getGroupOfProperty(k)=='Reconstruction'}
try:
    key='Def_DriverOperatingNut';reuse(key);put('DriverBrakeBridleNut',key,App.Placement(seat+App.Vector(0,-hd['nut_seat_mm'],0),orient),'nut')
    # Translate the complete existing M790/keeper pair, preserving its geometry
    # and relative pin orientation. Head seat follows the actual new fork face.
    oldpin='PortDriverLowSelectorPin';oldkeeper='PortDriverLowSelectorKeeper'
    old=pose(parent.rows[oldpin]['frame']);oldseat=old.multVec(App.Vector(0,1.55,0));newseat=front+App.Vector(0,pd['fork_head_seat_y_mm'],0);shift=newseat-oldseat
    for name,oldname,role in [('DriverBrakePedalJointPin',oldpin,'pin'),('DriverBrakePedalJointCotter',oldkeeper,'cotter')]:
        row=parent.rows[oldname];reuse(row['definition']);frame=pose(row['frame']);frame.Base+=shift;put(name,row['definition'],frame,role)
    for name in ['DriverMainShaft','DriverSwingShaft']:
        row=parent.rows[name];reuse(row['definition']);specs[name]=dict(definition=row['definition'],frame=row['frame'],owner='Receivers',role='receiver')
finally:App.closeDocument(doc.Name)
details=dict(controls=c,stock_offset_mm=a.stock_offset,main_world_mm=list(main),swing_world_mm=list(swing),front_joint_world_mm=list(front),rear_joint_world_mm=list(rear_world),pedal=pd,bridle=bd,rear_hardware=hd,rear_hardware_controls=hc,retained_development_native=str(parent.native.relative_to(ROOT)),retained_development_native_sha256=sha(parent.native),scope='Ten complete central pedal-group occurrences connected by two shafts, front pin and rear bolt/spacer journals; brake-output linkage remains unresolved.',source_camera_refitted=False,mechanism_complete=False)
inputs=[Path(__file__),a.controls,review,ROOT/c['hardware_controls'],parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json',*[ROOT/f for f in read(review)['source_hashes']]]
inputs+=sorted({Path(m.__file__).resolve() for m in sys.modules.values() if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,props,details,inputs,curves=guides)
print('Saved ten central pedal-group parts and two unchanged shafts; checks pending.',flush=True)
