"""High selectors, complete source-length M789A rods and shared M576 long connections."""
import argparse,copy,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_high_control_parts import selector
V=App.Vector;X=V(1,0,0);Y=V(0,1,0)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls)
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
prior=read(ROOT/c['context_prototype']/'report.json');d=copy.deepcopy(parent.report['details']);main=V(*d['foundation']['shafts']['Main']['center_world_mm']);specs={};shapes={};props={}
def reuse(key):
    if key not in shapes:shapes[key]=parent.definition(key);props[key]=parent.manifest['definitions'][key]['properties']
def carry(name,role='receiver'):
    row=parent.rows[name];reuse(row['definition']);specs[name]=dict(definition=row['definition'],frame=row['frame'],owner=row['owners'][-1],role=role)
for name,spec in prior['specs'].items():carry(name,spec['role'])
def put(name,key,frame,owner,role,records=None):
    specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
    if records:specs[name]['source_records']=records
key='Def_DriverFrontShortRod_M789A';shapes[key]=Part.makeCylinder(c['rod_radius'],c['short_stock_mm'],V(),X);props[key]=dict(SourcePartMark='M789A',SourceRecords=['SNL:194:028'],Representation='reconstruction_trial',ReconstructionStatus='Complete printed10-5/8in rod stock; two high-control occurrences. Third reverse application remains required. Fork insertion and nominal thread envelopes estimated.',ParameterUpdate='Regenerate trial_driver_high_controls.py from high_controls01.json')
long_key='Def_DriverClutchFrontRod_M576';reuse(long_key)
identity=list(App.Placement().toMatrix().A);groups={'DriverHighControls':dict(owner='DriverControlFoundation',frame=identity)};records={};template=pose(parent.rows['PortTrackBrakeJointFork']['frame'])
for side,sign,mark,rowid in [('Port',1,'M759','SNL:117:025'),('Starboard',-1,'M758','SNL:117:026')]:
    stem=side+'DriverHigh';group=stem+'Branch';groups[group]=dict(owner='DriverHighControls',frame=identity);pivot=main+Y*(sign*125);bell=pivot+V(*c['bell_relative_to_main']);key='Def_DriverHighSelector_'+mark;shapes[key]=selector(c,side)
    props[key]=dict(SourcePartMark=mark,SourceRecords=[rowid,'HB:93','HB:113'],Representation='reconstruction_trial',ReconstructionStatus='Short outward-opening high selector jaw; stock/profile/pose estimated. Lower eye closes complete source-length M789A; fixed source comparison retains13.53px discrepancy. Operating-handle engagement unfinished.',ParameterUpdate='Regenerate trial_driver_high_controls.py')
    put(stem+'Selector',key,App.Placement(pivot,App.Rotation()),group,'selector')
    swing=d['swings'][side+'High'];short=V(*swing['front_pin_world_mm']);long=V(*swing['rear_pin_world_mm']);rocker=side+'HighIntermediateRocker';carry(rocker);intermediate=pose(parent.rows[rocker]['frame']).multVec(V(0,0,66.675))
    data=dict(pivot_world_mm=list(pivot),bell_pin_world_mm=list(bell),mark=mark,rods={})
    for kind,startpin,endpin,receivers,key,stock in [('Short',short,bell,(swing['occurrence'],stem+'Selector'),'Def_DriverFrontShortRod_M789A',c['short_stock_mm']),('Front',intermediate,long,(rocker,swing['occurrence']),long_key,d['rods']['Front']['stock_length_mm'])]:
        direction=endpin-startpin;distance=direction.Length;direction.normalize();assert abs(distance-stock-2*c['pin_to_stock_offset_mm'])<1e-7;start=startpin+direction*c['pin_to_stock_offset_mm'];name=stem+kind+'Rod';put(name,key,App.Placement(start,App.Rotation(X,direction)),group,'rod')
        endpoints=[]
        for end,point,axis,receiver in [('Rear',startpin,direction,receivers[0]),('Forward',endpin,-direction,receivers[1])]:
            joint=stem+kind+end+'Joint';frame=App.Placement(point,App.Rotation(axis,Y,axis.cross(Y),'XYZ'));groups[joint]=dict(owner=group,frame=list(frame.toMatrix().A))
            for role in ['Fork','Pin','Cotter','Nut']:
                row=parent.rows['PortTrackBrakeJoint'+role];reuse(row['definition']);put(joint+role,row['definition'],frame.multiply(template.inverse().multiply(pose(row['frame']))),joint,role.lower(),['SNL:129:002'] if role=='Nut' else None)
            endpoints.append(dict(stem=joint,pin_world_mm=list(point),rod_axis_world=list(axis),receiver=receiver))
        data['rods'][kind]=dict(occurrence=name,definition=key,stock_length_mm=stock,pin_span_mm=distance,stock_start_world_mm=list(start),axis_world=list(direction),endpoints=endpoints)
    records[side]=data
d['high_selector_controls']=c;d['high_controls']=records;d['scope']='Two high selectors, two complete printed M789A rods and two shared M576 front rods, with eight complete clevis joints. All inherited shapes and frames preserved. Actual source high-eye discrepancy remains open; operator mechanisms remain unfinished.'
inputs=[Path(__file__),a.controls,source,ROOT/c['layout'],ROOT/c['context_prototype']/'report.json',parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,props,d,inputs,assembly_groups=groups)
print('Saved complete high-selector short and long connections; verification pending.',flush=True)
