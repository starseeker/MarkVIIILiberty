"""Source-sized M782 shaft and retainers; mounting remains explicitly unqualified."""
import argparse,sys
from pathlib import Path
from control_rebuild_io_v2 import *
from transmission_input_installation_parts import formed_pin
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();c=read(a.controls);parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256'];assert all(sha(ROOT/f)==v for f,v in read(source)['source_hashes'].items())
end=c['shaft_length']/2;shoulder=end-c['reduced_end_length'];seat=shoulder+c['receiver_grip'];pin_station=seat+14+c['keeper_front_offset'];r=c['reduced_end_radius'];nutkey='Def_TransmissionPin_nut';nut=parent.definition(nutkey);nb=nut.BoundBox
assert abs(nb.YLength-14)<1e-5
shaft=Part.makeCylinder(c['shaft_diameter']/2,2*shoulder,V(0,-shoulder,0),Y)
for sign in [-1,1]:shaft=shaft.fuse(Part.makeCylinder(r,c['reduced_end_length'],Y*(sign*shoulder),Y*sign))
for sign in [-1,1]:shaft=shaft.cut(Part.makeCylinder(c['keeper_hole_diameter']/2,2*r+2,V(-r-1,sign*pin_station,0),X))
shaft=shaft.removeSplitter();keeper,kd=formed_pin(c['keeper']);shapes={'Def_DriverFulcrumShaft_Redo':shaft,'Def_DriverFulcrumKeeper_Redo':keeper,nutkey:nut}
properties={'Def_DriverFulcrumShaft_Redo':dict(SourcePartMark='M782',SourceRecords=['HB:148','SNL:213:016'],Representation='reconstruction_trial',ReconstructionStatus='Printed628.65mm total length and38.0238mm journal; estimated reduced ends, receiver grip and keeper stations. No mounting acceptance.',ParameterUpdate='Regenerate trial_driver_fulcrum_shaft.py'),'Def_DriverFulcrumKeeper_Redo':dict(SourcePartMark='3/16 x 1-1/2 inch split pin',SourceRecords=['SNL:213:018'],Representation='reconstruction_trial',ReconstructionStatus='Source-sized formed keeper; installed bend and placement estimates.',ParameterUpdate='Regenerate trial_driver_fulcrum_shaft.py'),nutkey:parent.manifest['definitions'][nutkey]['properties']}
center=V(*c['center']);owner='DriverFulcrumShaftStudy';specs={};identity=list(App.Placement().toMatrix().A)
def put(name,key,f,role,rs):specs[name]=dict(definition=key,frame=list(f.toMatrix().A),owner=owner,role=role,source_records=rs)
put('DriverFulcrumShaft','Def_DriverFulcrumShaft_Redo',App.Placement(center,App.Rotation()),'shaft',['HB:148','SNL:213:016'])
for side,sign in [('Port',1),('Starboard',-1)]:
 rotation=App.Rotation() if sign==1 else App.Rotation(Z,180)
 put('DriverFulcrum'+side+'Nut',nutkey,App.Placement(center+Y*(sign*(seat-nb.YMin)),rotation),'nut',['SNL:213:017'])
 # Keeper local Y crosses the shaft in world X; tails spread in world Z.
 frame=App.Placement(center+Y*(sign*pin_station),App.Rotation(-Y,X,Z,'XYZ'))
 put('DriverFulcrum'+side+'Keeper','Def_DriverFulcrumKeeper_Redo',frame,'keeper',['SNL:213:018'])
details=dict(controls=c,shaft_half_length_mm=end,shoulder_station_mm=shoulder,nut_seat_station_mm=seat,keeper_station_mm=pin_station,existing_nut_base_y_mm=nb.YMin,keeper=kd,receiving_interface=dict(future_support_grip_mm=c['receiver_grip'],support_axis='Y',journal_radius_mm=r,positive_side_limits_mm=[shoulder,seat],negative_side_limits_mm=[-seat,-shoulder]),scope='Uninstalled five-part study; brackets, floor attachment and final shaft-end interpretation remain open. No part of the accepted full model changes.')
inputs=[Path(__file__),a.controls,source,parent.folder/'report.json',parent.folder/'isolated/manifest.json']
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,properties,details,inputs,assembly_groups={owner:dict(owner='Root',frame=identity)})
print('Saved uninstalled M782/nut/keeper study; no full-model integration.',flush=True)
