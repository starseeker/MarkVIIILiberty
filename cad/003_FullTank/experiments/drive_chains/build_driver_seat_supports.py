"""Connect the seat through four stays and separate floor angles, with full stock."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_seat_support_parts import supports, stay, bolt, upper_hardware

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--lower-z-offset', type=float, default=0.)
a = p.parse_args()
parent = Saved(H/'driver_seat_study/trial06')
layout_folder = H/'driver_layout_study/trial01'
layout = read(layout_folder/'report.json')
accepted = H/'transmission_controls_study/driver_redo01/operating_integrated01'
controls = read(accepted/'report.json')['details']['foundation']['controls']
packet = H/'driver_seat_support_study'
receipt = read(packet/'evidence_receipt.json')
assert all(sha(ROOT/f) == h for f, h in receipt['dependencies'].items())
constraint = read(packet/'evidence01/interface_constraints.json')
shapes = {k: parent.definition(k) for k in parent.manifest['definitions']}
props = {k: dict(v['properties']) for k, v in parent.manifest['definitions'].items()}
specs = {n: dict(definition=r['definition'], frame=r['frame'], owner='SeatDriverBowContext', role='receiver') for n, r in parent.rows.items()}
V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
t, outer = controls['plate_stock'], controls['nut_seat_y']
inside = outer-t
changed, relocated, joints, side_records, stay_records = [], [], [], {}, []


def define(name, shape, sources, note, mark=''):
    key = 'Def_SeatSupport_'+name
    shapes[key] = shape
    props[key] = dict(SourceRecords=sources, SourcePartMark=mark,
        Representation='reconstruction_trial', ReconstructionStatus=note,
        ParameterUpdate='Regenerate build_driver_seat_supports.py with recorded lower-z-offset; no live expressions.')
    return key


def install(name, key, placement, owner, sources=None):
    specs[name] = dict(definition=key, frame=list(placement.toMatrix().A), owner=owner, role='seat_support')
    if sources:
        specs[name]['source_records'] = sources


half_nut = 'Def_EngineSuspension_half_nut'
half_lock = 'Def_EngineSuspension_half_lock'
half_lock_stock = shapes[half_lock].BoundBox.ZLength
half_nut_stock = shapes[half_nut].BoundBox.ZLength
assert abs(shapes[half_lock].BoundBox.ZMin) < 1e-7 and abs(shapes[half_nut].BoundBox.ZMin) < 1e-7
lower_bolt = define('LowerStayBolt', bolt(12.7, 34.925, 19.05, 8.), ['SNL:031:005'],
    'Full printed half-inch x1-3/8 underhead stock; head form estimated.', '1/2 x 1-3/8 inch hexagon bolt')
angle_bolt = define('AngleFloorBolt', bolt(12.7, 41.275, 19.05, 8.), ['SNL:031:008'],
    'Full printed half-inch x1-5/8 underhead stock; head form estimated.', '1/2 x 1-5/8 inch hexagon bolt')
upper_bolt_shape, upper_nut_shape, upper_lock_shape = upper_hardware()
upper_bolt = define('UpperStayBolt', upper_bolt_shape, ['SNL:033:009'],
    'Full printed3/4x2-3/8in stock; underhead datum and31.75mm AF/12.3825mm head height estimated. Printed A/B application conflicts with B/D stay list.', '3/4 x 2-3/8 inch hexagon bolt')
upper_nut = define('UpperStayNut', upper_nut_shape, ['SNL:033:009'],
    'Plain nut:19.05mm stock,31.75mm AF and19.3mm nominal thread envelope estimated.', '3/4 inch plain nut')
upper_lock = define('UpperStayLock', upper_lock_shape, ['SNL:033:009'],
    'Compressed split annulus,3.175mm stock and34.925mm OD estimated.', '3/4 inch lock washer')


def stack(stem, keys, point, axis, grip, lock_stock, hosts, source, length, diameter, owner):
    rotation = App.Rotation(Z, axis)
    for suffix, key, offset in [('Bolt', keys[0], 0.), ('Lock', keys[1], grip), ('Nut', keys[2], grip+lock_stock)]:
        name = stem+suffix
        install(name, key, App.Placement(point+axis*offset, rotation), owner, [source])
        if name in parent.rows:
            relocated.append(name)
    joints.append(dict(stem=stem, point_world_mm=list(point), axis_world=list(axis), grip_mm=grip,
        lock_stock_mm=lock_stock, hosts=hosts, source_id=source,
        bolt_length_mm=length, bolt_diameter_mm=diameter,
        bolt_protrusion_mm=length-grip-lock_stock-shapes[keys[2]].BoundBox.ZLength))


# Enlarge only the through bore; preserve flange, rivet holes and all external material.
bearing_key = 'Def_DriverSeat_Bearing_SH289E'
shapes[bearing_key] = shapes[bearing_key].cut(Part.makeCylinder(9.65, 32, V(0,-16,-35.5696394686906),Y)).removeSplitter()
changed.append(bearing_key)
props[bearing_key] = dict(props[bearing_key], SourceRecords=['SNL:017:024','SNL:207:027','SNL:033:009'],
    ReconstructionStatus='Printed19.05mm upper bolt replaces earlier unconstrained bore estimate;19.3mm receiving bore gives estimated0.125mm radial clearance. All other bearing material retained.',
    ParameterUpdate='Regenerate build_driver_seat_supports.py; clearance is an estimated construction allowance.')
lower_centers = {}
for station in ['Front','Rear']:
    x,z = constraint['conditional_stay_endpoints'][station.lower()]['lower']['conditional_world_xz_mm']
    lower_centers[station] = V(x,0,z+a.lower_z_offset)

for side, hand in [('Port',1),('Starboard',-1)]:
    name = 'Driver'+side+'SupportPlate'
    key = parent.rows[name]['definition']
    record = layout['details']['supports'][side]
    web, angle, base = supports(record, controls, lower_centers, hand)
    angle_name = 'DriverSeat'+side+'SupportAngle'
    angle_key = define(side+'Angle_M788', angle, ['SNL:005:006','SNL:031:008'],
        'Separate6.35mm floor angle with55mm vertical leaf; two-plane longitudinal bend, outline and bolt allocation estimated.', 'M788')
    mounts = [v for v in layout['details']['mounts'] if v['plate']==name]
    upper = record['upper_foot_section_world']

    def height(x):
        for p0,p1 in zip(upper,upper[1:]):
            if p0[0]-1e-7 <= x <= p1[0]+1e-7:
                return p0[1]+(p1[1]-p0[1])*(x-p0[0])/(p1[0]-p0[0])
        raise ValueError('Plate bolt outside angle')

    # Four existing M786/M787 bolts move to the vertical plate-to-angle joint.
    # Four new longer M788 bolts use the actual previously qualified floor seats.
    for index, mount in enumerate(mounts,1):
        point = V(*mount['contact_world_mm']); normal = V(*mount['normal_world'])
        tool = Part.makeCylinder(6.5, t+2, point-base-normal, normal)
        shapes[angle_key] = shapes[angle_key].cut(tool).removeSplitter()
        oldstem = mount['stem']
        newstem = 'DriverSeat'+side+'AngleFloor'+str(index)
        for suffix,k in [('Bolt',angle_bolt),('Lock',half_lock),('Nut',half_nut)]:
            install(newstem+suffix,k,pose(parent.rows[oldstem+suffix]['frame']), 'SeatFloorAngles',['SNL:031:008'])
        seat = pose(parent.rows[oldstem+'Bolt']['frame']).Base
        lock_seat = pose(parent.rows[oldstem+'Lock']['frame']).Base
        grip = (lock_seat-seat).dot(-normal)
        joints.append(dict(stem=newstem,point_world_mm=list(seat),axis_world=list(-normal),grip_mm=grip,
            lock_stock_mm=half_lock_stock, hosts=[angle_name,mount['floor']],source_id='SNL:031:008',
            bolt_length_mm=41.275,bolt_diameter_mm=12.7,
            bolt_protrusion_mm=41.275-grip-half_lock_stock-half_nut_stock))
        point = V(point.x,hand*inside,height(point.x)+28)
        tool = Part.makeCylinder(6.5,2*t+2,point-base-Y*hand,Y*hand)
        web = web.cut(tool).removeSplitter()
        shapes[angle_key] = shapes[angle_key].cut(tool).removeSplitter()
        stack(oldstem,('Def_DriverSupportBolt_MountStudy',half_lock,half_nut),point,Y*hand,2*t,
            half_lock_stock,[name,angle_name],'SNL:031:004',31.75,12.7,'SeatSupportPlateFasteners')
    shapes[key] = web
    changed.append(key)
    props[key] = dict(props[key], ReconstructionStatus='Plain6.35mm support side plate with actual shaft bores, extended to conditional stay joints. Old estimated bent foot assigned to separate M788 angle; four source31.75mm bolts now join vertical plate and angle. Outline and allocation remain hypotheses.',
        ParameterUpdate='Regenerate build_driver_seat_supports.py with recorded lower-z-offset.')
    install(name,key,App.Placement(base,App.Rotation()),'SeatSupportPlates')
    install(angle_name,angle_key,App.Placement(base,App.Rotation()),'SeatFloorAngles')
    side_records[side] = dict(plate=name,angle=angle_name,plate_stock_mm=t,angle_stock_mm=t,
        base_world_mm=list(base),plate_inner_y_mm=hand*inside,plate_outer_y_mm=hand*outer,
        original_floor_mounts=mounts,original_floor_profile=record)

for station, mark in [('Front','SH289B'),('Rear','SH289D')]:
    upper_record = next(v for v in parent.report['details']['bearing_records'] if v['name']=='DriverSeatPort'+station+'Bearing')
    upper_axis = V(*upper_record['receiving_center_world_mm'])
    lower_axis = lower_centers[station]
    # Opposite sides reuse the same axially symmetric end profiles via rigid
    # rotation around the stay's projected longitudinal axis, not a scaled link.
    dx,dz = upper_axis.x-lower_axis.x,upper_axis.z-lower_axis.z
    distance = math.hypot(dx,dz)
    lower_y, upper_y = inside-t, upper_axis.y+15
    key = define(station+'Stay_'+mark,stay(V(),V(0,upper_y-lower_y,distance),t),
        ['SNL:222:007' if station=='Front' else 'SNL:222:008','SNL:031:005','SNL:033:009'],
        'Dogleg stay:6.35mm projected Y web stock,28mm center web width,18/20mm end-pad radii; section-derived length and transverse dogleg estimated. Full lower/upper bores13.0/19.3mm.', mark)
    longitudinal = App.Rotation(Y,math.degrees(math.atan2(dx,dz)))
    for side,hand in [('Port',1),('Starboard',-1)]:
        name = 'DriverSeat'+side+station+'Stay'
        bearing_name = 'DriverSeat'+side+station+'Bearing'
        plate_name = 'Driver'+side+'SupportPlate'
        point = V(lower_axis.x,hand*lower_y,lower_axis.z)
        rotation = longitudinal.multiply(App.Rotation(Z,0 if hand==1 else 180))
        placement = App.Placement(point,rotation)
        install(name,key,placement,'Seat'+station+'Stays')
        upper_point = V(upper_axis.x,hand*upper_y,upper_axis.z)
        assert (placement.multVec(V(0,upper_y-lower_y,distance))-upper_point).Length<1e-7
        stack(name+'Lower',(lower_bolt,half_lock,half_nut),point,Y*hand,2*t,half_lock_stock,
            [name,plate_name],'SNL:031:005',34.925,12.7,'Seat'+station+'Stays')
        headseat = V(upper_axis.x,hand*(upper_axis.y-15),upper_axis.z)
        stack(name+'Upper',(upper_bolt,upper_lock,upper_nut),headseat,Y*hand,30+t,3.175,
            [bearing_name,name],'SNL:033:009',60.325,19.05,'Seat'+station+'Stays')
        stay_records.append(dict(name=name,mark=mark,lower_receiver=plate_name,upper_receiver=bearing_name,
            lower_center_world_mm=list(point),upper_center_world_mm=list(upper_point),
            projected_length_mm=distance,actual_center_distance_mm=(upper_point-point).Length,
            side=side,stock_projected_y_mm=t))

details = dict(lower_z_offset_mm=a.lower_z_offset,supports=side_records,stays=stay_records,joints=joints,
    relocated_existing_hardware=relocated,source_camera_refitted=False,
    geometry_connection_built=True,installation_qualified=False,
    seat_parent_native_sha256=sha(parent.native),
    retained_development_native=parent.report['details']['retained_development_native'],
    retained_development_native_sha256=parent.report['details']['retained_development_native_sha256'],
    unchanged_source_seat_origin_world_mm=parent.report['details']['origin_world_mm'],
    scope='Four full stays,24 upper/lower fastener pieces,two separate floor angles and24 floor fastener pieces.24 previous plate fasteners relocated to real plate-angle joints. Bore, side plate and angle ownership revisions explicit.',
    limits=['A/B upper bolt versus B/D stay identities unresolved.','M788 angle allocation, sharp two-plane bend, stay doglegs, stock and support outlines estimated.','Conditional lower-joint picks and shaft/seat historical position remain unresolved.','Static assembly only; adjusting/locking mechanism and SH291C application not qualified.','No source camera refit or full tank integration.'])
inputs = [Path(__file__),H/'driver_seat_support_parts.py',H/'bow_reconstruction_parts.py',H/'engine_suspension_parts.py',
    packet/'evidence_receipt.json',packet/'evidence01/interface_constraints.json',parent.folder/'report.json',
    parent.folder/'isolated/manifest.json',H/'driver_seat_study/study_receipt.json',layout_folder/'report.json',accepted/'report.json']
trial(a.output,parent,shapes,specs,props,details,inputs,changed_definitions=changed)
print('Seat support prototype:',len(specs)-len(parent.rows),'additions;',len(specs),'total occurrences;',len(shapes),'definitions',flush=True)
