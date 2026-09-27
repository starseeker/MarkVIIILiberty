"""Add two low-speed selectors with complete M790 joints; correct provisional M762."""
import argparse,copy,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_low_selector_parts import selector,connecting,joint_pin
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls)
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
prior=read(ROOT/c['context_prototype']/'report.json');d=copy.deepcopy(parent.report['details']);main=V(*d['foundation']['shafts']['Main']['center_world_mm']);rear=V(*d['foundation']['shafts']['Swing']['center_world_mm']);specs={};shapes={};props={}
def reuse(key):
    if key not in shapes:shapes[key]=parent.definition(key);props[key]=parent.manifest['definitions'][key]['properties']
for name,oldspec in prior['specs'].items():
    row=parent.rows[name];reuse(row['definition']);specs[name]=dict(definition=row['definition'],frame=row['frame'],owner=row['owners'][-1],role=oldspec['role'])
def put(name,key,frame,owner,role):specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
front=main-rear+V(*c['front_relative_to_main'])+Y*c['connecting_y'];knee=V(*d['low_parts']['knee'])+Y*c['connecting_y']
key='Def_DriverLowConnecting_M762';shapes[key]=connecting(c,knee,front)
props[key]=dict(SourcePartMark='M762',SourceRecords=['SNL:119:035','HB:113'],Representation='reconstruction_trial',ReconstructionStatus='Revised straight diagonal link from real upper M790 selector joint to retained rear M761 knee. Previous bowed profile confused the foot-brake bridle. Width, stock and eyes estimated.',ParameterUpdate='Regenerate trial_driver_low_selectors.py from selector_controls01.json')
key='Def_DriverLowSelectorJointPin_M790';shapes[key]=joint_pin(c);props[key]=dict(SourcePartMark='M790',SourceRecords=['SNL:137:009','HB:113'],Representation='reconstruction_trial',ReconstructionStatus='Complete joint pin with actual cotter drilling. Diameter, head and31.75mm under-head length are estimates. Two of three source applications installed.',ParameterUpdate='Regenerate trial_driver_low_selectors.py')
keeper='Def_DriverLowSuspensionKeeper';reuse(keeper)
groups={};records={};identity=list(App.Placement().toMatrix().A)
for side,sign,mark,record in [('Port',1,'M756','SNL:117:029'),('Starboard',-1,'M757','SNL:117:030')]:
    branch=side+'DriverLowBranch';stem=side+'DriverLowSelector';groups[stem+'Joint']=dict(owner=branch,frame=identity)
    pivot=main+Y*(sign*180+c['selector_y_relative_to_low']);point=main+V(*c['front_relative_to_main'])+Y*(sign*180)
    key='Def_DriverLowSelector_'+mark;shapes[key]=selector(c,side)
    props[key]=dict(SourcePartMark=mark,SourceRecords=[record,'HB:93','HB:113'],Representation='reconstruction_trial',ReconstructionStatus='SNL handed identity selected; HB190 reverses M756/M757. Short side-opening gate and upper bell eye. Profile, section, axial position and static pose estimated; high selector and operating handle remain unfinished.',ParameterUpdate='Regenerate trial_driver_low_selectors.py')
    put(stem,key,App.Placement(pivot,App.Rotation()),branch,'selector')
    put(stem+'Pin','Def_DriverLowSelectorJointPin_M790',App.Placement(point,App.Rotation()),stem+'Joint','pin')
    # Same cotter stock as the M761 joint; the pin diameter is also19.05mm.
    put(stem+'Keeper',keeper,App.Placement(point+Y*c['pin_keeper_y'],App.Rotation(-Y,X,Z,'XYZ')),stem+'Joint','keeper')
    records[side]=dict(pivot_world_mm=list(pivot),pin_world_mm=list(point),connecting_eye_world_mm=list(point+Y*c['connecting_y']),pin_head_seat_world_mm=list(point+Y*c['pin_head_seat_y']),pin_keeper_world_mm=list(point+Y*c['pin_keeper_y']),mark=mark)
    d['low_speed'][side].pop('open_selector_connection_world_mm',None);d['low_speed'][side]['selector_connection_world_mm']=list(point+Y*c['connecting_y'])
d['low_parts']['connecting_front']=list(front);d['low_parts'].pop('connecting_arc_radius_mm',None)
d['selector_controls']=c;d['low_selectors']=records;d['scope']='Two low-speed selectors with complete M790 pins/cotters and corrected diagonal M762 links. Operating handles, high selectors, spacing, gates/stops and remaining driver controls are unfinished.'
inputs=[Path(__file__),a.controls,source,ROOT/c['context_prototype']/'report.json',parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,props,d,inputs,changed_definitions=['Def_DriverLowConnecting_M762'],assembly_groups=groups)
print('Saved low selectors and physical upper joints; verification pending.',flush=True)
