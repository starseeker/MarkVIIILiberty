"""Construct a source-bound driver support hypothesis; acceptance is separate."""
import argparse,sys,math
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_control_mount_parts import parts
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls)
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
registration=read(ROOT/c['registration']);probe=read(ROOT/c['floor_probe'])
floorpoint=V(*probe['floors']['hull_floor_1']['planes'][2]['point']);normal=V(*probe['floors']['hull_floor_1']['planes'][2]['normal']);slope=-normal.x/normal.z
def floor_z(x):return floorpoint.z+slope*(x-floorpoint.x)
# Keep the source M574 stock constraint explicit while its actual front rocker
# is still pending. This target is NOT counted as an installed rod or receiver.
receiver=V(*read(ROOT/c['receiver_report'])['details']['receiving_interfaces']['PortLowIntermediateRocker']['front_pin_world_mm'])
pinspan=49.5*25.4+2*(44.45-19.05)
frontx=receiver.x+math.sqrt(pinspan**2-(c['future_low_pin_z']-receiver.z)**2)
rear=V(frontx-c['future_low_pin_relative_to_swing'][0],0,c['future_low_pin_z']-c['future_low_pin_relative_to_swing'][2])
separation=registration['shaft_separation_mm'];main=V(rear.x+separation,0,c['main_shaft_z']);origin=V(rear.x,0,floor_z(rear.x))
shapes,kd=parts(c,separation,rear.z-origin.z,main.z-origin.z,normal,slope)
specs={};properties={};identity=list(App.Placement().toMatrix().A)
groups={'DriverControlFoundation':dict(owner='Root',frame=identity)}
for child in ['DriverMainFulcrum','DriverRearSwing','DriverSupportPlates','DriverFloorContext']:
    groups[child]=dict(owner='DriverControlFoundation',frame=identity)
marks={'MainShaft':('M782',['HB:148','SNL:213:016']),'SwingShaft':('M783',['SNL:213:011']),
       'MainKeeper':('3/16 x 1-1/2 inch split pin',['SNL:213:018']),
       'SwingKeeper':('3/16 x 2 inch split pin',['SNL:213:013','SNL:141:012']),
       'PortSupportPlate':('M786',['SNL:147:011','SNL:31:004']),
       'StarboardSupportPlate':('M787',['SNL:147:012','SNL:31:004']),
       'SupportBolt':('1/2 x 1-1/4 inch hexagon bolt',['SNL:31:004'])}
for kind,(mark,rs) in marks.items():
    properties['Def_Driver'+kind+'_MountStudy']=dict(SourcePartMark=mark,SourceRecords=rs,Representation='reconstruction_trial',ReconstructionStatus='Partial driver support-interface hypothesis; source stock retained where printed. Plate outline, seat attachments, shaft spacing/heights and floor mount interpretation remain estimates. See mount_source_review03.json.',ParameterUpdate='Regenerate trial_driver_control_mounts_v3.py using saved controls.')
def reuse(key):
    shapes[key]=parent.definition(key);properties[key]=parent.manifest['definitions'][key]['properties']
def put(name,key,point,rotation,owner,role,rs=None):
    specs[name]=dict(definition=key,frame=list(App.Placement(point,rotation).toMatrix().A),owner=owner,role=role)
    if rs:specs[name]['source_records']=rs
for key in ['Def_TransmissionPin_nut','Def_TransmissionSmallSupport_nut','Def_EngineSuspension_half_nut','Def_EngineSuspension_half_lock']:reuse(key)
shafts={}
for kind,center,nutkey,height,offset in [('Main',main,'Def_TransmissionPin_nut',14,16.5),('Swing',rear,'Def_TransmissionSmallSupport_nut',13,10)]:
    owner='DriverMainFulcrum' if kind=='Main' else 'DriverRearSwing';base=shapes[nutkey].BoundBox.YMin if kind=='Main' else shapes[nutkey].BoundBox.YMax
    put('Driver'+kind+'Shaft','Def_Driver'+kind+'Shaft_MountStudy',center,App.Rotation(),owner,'shaft')
    for side,sign in [('Port',1),('Starboard',-1)]:
        rot=(App.Rotation() if sign==1 else App.Rotation(Z,180)) if kind=='Main' else (App.Rotation(X,180) if sign==1 else App.Rotation())
        nut_origin=center+Y*(sign*(c['nut_seat_y']-base if kind=='Main' else c['nut_seat_y']+base))
        put('Driver'+kind+side+'Nut',nutkey,nut_origin,rot,owner,'nut',['SNL:213:017' if kind=='Main' else 'SNL:213:012'])
        # Both eyes/tails spread in the plane normal to the shaft. The swing
        # keeper crosses the real radial castle slot without hitting its base.
        rot=App.Rotation(-Y,X,Z,'XYZ')
        put('Driver'+kind+side+'Keeper','Def_Driver'+kind+'Keeper_MountStudy',center+Y*(sign*(c['nut_seat_y']+offset)),rot,owner,'keeper')
    shafts[kind]=dict(center_world_mm=list(center),nut_seat_station_mm=c['nut_seat_y'],keeper_station_mm=c['nut_seat_y']+offset,nut_height_mm=height,original_nut_seat_y_mm=base,shoulder_station_mm=c['nut_seat_y']-c['plate_stock'])
floors={}
for name,f in probe['floors'].items():
    assert sha(ROOT/f['brep'])==f['sha256'];q=Part.Shape();q.read(str(ROOT/f['brep']));floors[name]=q
mounts=[]
for side,sign in [('Port',1),('Starboard',-1)]:
    name='Driver'+side+'SupportPlate';put(name,'Def_Driver'+side+'SupportPlate_MountStudy',origin,App.Rotation(),'DriverSupportPlates','plate')
    for i,x in enumerate([rear.x-40,rear.x-10,main.x-80,main.x-50],1):
        y=sign*(c['nut_seat_y']+27.5);base=V(x,y,floor_z(x));head=base+normal*c['plate_stock'];lock=base-normal*6;nut=lock-normal*3.175
        floorname='hull_floor_2' if x<7262.528034682733 else 'hull_floor_1'
        floors[floorname]=floors[floorname].cut(Part.makeCylinder(6.5,8,base+normal,-normal))
        stem='Driver'+side+'SupportMount'+str(i)
        for role,key,point in [('Bolt','Def_DriverSupportBolt_MountStudy',head),('Lock','Def_EngineSuspension_half_lock',lock),('Nut','Def_EngineSuspension_half_nut',nut)]:
            put(stem+role,key,point,App.Rotation(Z,-normal),'DriverSupportPlates',role.lower(),['SNL:31:004'])
        mounts.append(dict(stem=stem,plate=name,floor=floorname,floor_contact_world_mm=list(base),head_seat_world_mm=list(head),lock_seat_world_mm=list(lock),nut_seat_world_mm=list(nut),axis_world=list(-normal)))
for name,q in floors.items():
    key='Def_DriverContext_'+name;shapes[key]=q.removeSplitter();properties[key]=dict(SourcePartMark=name,SourceRecords=['Existing standard hull geometry','SNL:31:004'],Representation='reconstruction_trial',ReconstructionStatus='Original standard floor retained except four declared driver support bolt bores.',ParameterUpdate='Regenerate trial_driver_control_mounts_v3.py')
    put(name,key,V(),App.Rotation(),'DriverFloorContext','floor')
details=dict(controls=c,shafts=shafts,keeper=kd,mounts=mounts,floor_normal=list(normal),plate_origin_world_mm=list(origin),shaft_separation_mm=separation,future_low_pin_world_mm=[frontx,receiver.y,c['future_low_pin_z']],future_low_pin_status='Unmodeled provisional target; no front rod or rocker counted.',scope='Partial seat-support plates, two shaft interfaces and real floor attachment; seat mount extensions, lever fulcrums, controls and front rods remain pending.')
inputs=[Path(__file__),a.controls,source,ROOT/c['registration'],ROOT/c['floor_probe'],ROOT/c['receiver_report'],parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs += [ROOT/f['brep'] for f in probe['floors'].values()]
inputs += sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,properties,details,inputs,assembly_groups=groups)
print('Saved 38-part driver foundation hypothesis; independent validation required.',flush=True)
