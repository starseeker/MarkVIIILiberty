"""Build the intermediate receiver gang from source-length-constrained datums."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,pose,trial,read,sha
from control_rebuild_intermediate_parts import parts
V=App.Vector;X=V(1,0,0);Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();c=read(a.controls);parent=Saved(ROOT/c['parent'])
assert sha(parent.native)==c['parent_native_sha256']
source=ROOT/c['source_review'];assert sha(source)==c['source_review_sha256']
assert all(sha(ROOT/f)==h for f,h in read(source)['source_hashes'].items())
shapes,details=parts(c);specs={};properties={};groups={};mounts=[];receivers={}
identities={
 'Def_ControlIntermediateShaft_Redo':('M638',['SNL:211:029']),
 'Def_IntermediateMountBracket_Redo':('M639',['SNL:37:007']),
 'Def_M3019SupportStrip_Redo':('M3019',['SNL:225:024']),
 'Def_IntermediateMountCapScrew_Redo':('1/2 x 2 inch cap screw',['SNL:200:015']),
 'Def_IntermediateShaftKeeper_Redo':('3/16 x 2 inch split pin',['SNL:141:012']),
 'Def_IntermediateContext_hull_floor_3':('M1936 floor plate context',['development:standard:hull_floor_3'])}
for key,(mark,records) in identities.items():
    properties[key]=dict(SourcePartMark=mark,SourceRecords=records,DefinitionKey=key,
        Representation='reconstruction_trial',ReconstructionStatus='Estimated static geometry; see intermediate_source_review01.json.',
        ParameterUpdate='Regenerate with trial_control_rebuild_intermediate.py and '+str(a.controls.relative_to(ROOT)))
key=c['rocker_definition'];shapes[key]=parent.definition(key)
properties[key]=parent.manifest['definitions'][key]['properties']
theta=math.radians(c['rocker_clock_deg']);arm=V(-math.sin(theta),0,-math.cos(theta))
rotation=App.Rotation(Y.cross(arm),Y,arm,'XYZ')
low_z=c['shaft_height']+arm.z*c['rocker_inner_radius']
pin_distance=c['front_low_rod_length']+2*(c['fork_face_distance']-c['rod_insertion'])
dx=math.sqrt(pin_distance**2-(c['front_low_pin'][2]-low_z)**2)
station=c['front_low_pin'][0]-dx-arm.x*c['rocker_inner_radius']
shaft_origin=V(station,0,c['shaft_height']);base=V(station,0,c['floor_top'])
def group(name,owner,frame):groups[name]=dict(owner=owner,frame=list(frame.toMatrix().A))
def put(name,key,frame,owner,role):specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner=owner,role=role)
group('IntermediateControls','Root',App.Placement(base,App.Rotation()))
group('IntermediateFloorContext','Root',App.Placement())
put('IntermediateControlShaft','Def_ControlIntermediateShaft_Redo',App.Placement(shaft_origin,App.Rotation()),'IntermediateControls','shaft')
for name,y in c['rocker_lanes']:
    origin=V(station,y,c['shaft_height']);frame=App.Placement(origin,rotation)
    owner=name+'IntermediateControl';group(owner,'IntermediateControls',frame)
    put(name+'IntermediateRocker',c['rocker_definition'],frame,owner,'rocker')
    receivers[name]=dict(pivot_world_mm=list(origin),pin_axis_world=[0,1,0],
        front_pin_world_mm=list(frame.multVec(V(0,0,c['rocker_inner_radius']))),
        rear_pin_world_mm=list(frame.multVec(V(0,0,c['rocker_outer_radius']))))
for label,sign in [('Rear',-1),('Front',1)]:
    pos=base+X*(sign*c['mount_pitch_x']/2)
    put(label+'IntermediateSupportStrip','Def_M3019SupportStrip_Redo',App.Placement(pos,App.Rotation()),'IntermediateControls','strip')
for label,sign in [('Starboard',-1),('Port',1)]:
    pos=shaft_origin+Y*(sign*c['keeper_station_y'])
    frame=App.Placement(pos,App.Rotation(V(1,1,1),120))
    put(label+'IntermediateShaftKeeper','Def_IntermediateShaftKeeper_Redo',frame,'IntermediateControls','keeper')
floor_source=ROOT/c['floor_source'];assert sha(floor_source)==c['floor_source_sha256']
floor=Part.Shape();floor.read(str(floor_source));drills=[]
for number,y in enumerate(c['bracket_stations_y'],1):
    owner='IntermediateShaftMount'+str(number)
    foot=base+V(0,y,c['strip_thickness']);group(owner,'IntermediateControls',App.Placement(foot,App.Rotation()))
    put(owner+'Bracket','Def_IntermediateMountBracket_Redo',App.Placement(foot,App.Rotation()),owner,'bracket')
    for label,sign in [('Rear',-1),('Front',1)]:
        pos=base+V(sign*c['mount_pitch_x']/2,y,-c['floor_stock'])
        put(owner+label+'CapScrew','Def_IntermediateMountCapScrew_Redo',App.Placement(pos,App.Rotation()),owner,'screw')
        drills.append(Part.makeCylinder(c['mount_clearance']/2,c['floor_stock']+2,pos-Z))
        mounts.append(dict(name=owner+label+'CapScrew',bracket=owner+'Bracket',strip=label+'IntermediateSupportStrip',underhead_world_mm=list(pos)))
shapes['Def_IntermediateContext_hull_floor_3']=floor.cut(Part.makeCompound(drills))
assert 'hull_floor_3' not in parent.rows
put('hull_floor_3','Def_IntermediateContext_hull_floor_3',App.Placement(),'IntermediateFloorContext','floor')
details.update(controls=c,shaft_origin_world_mm=list(shaft_origin),low_front_pin_distance_mm=pin_distance,
    receiving_interfaces=receivers,mounts=mounts,external_context_replacements=['hull_floor_3'])
trial(a.output,parent,shapes,specs,properties,details,
    [Path(__file__),H/'control_rebuild_intermediate_parts.py',H/'control_rebuild_io_v2.py',
     H/'rear_control_channel_mount_parts.py',H/'transmission_frame_joint_parts.py',H/'transmission_input_installation_parts.py',
     a.controls,source,floor_source,parent.folder/'qualification.json',parent.folder/'isolated/manifest.json'],
    assembly_groups=groups)
print('Saved',len(specs),'unqualified intermediate support occurrences; shaft X',station,flush=True)
