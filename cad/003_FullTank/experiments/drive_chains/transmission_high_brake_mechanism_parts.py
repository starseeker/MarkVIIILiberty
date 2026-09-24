"""Paired M355 members, retained M356 pins and the high-speed adjustment unit.

Lever members use common brake coordinates. Pins are centred on +Y. Screw,
washers, spring and nut use local +Z along the adjusting screw. Source stock is
separated from the estimated profiles and manufactured details in controls.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_front_parts import coil
from transmission_brake_anchor_parts import shank_tail
from transmission_frame_joint_parts import cap
from transmission_input_installation_parts import formed_pin
V=App.Vector

def cy(radius,width,center=None):
    return Part.makeCylinder(radius,width,(center or V())+V(0,-width/2,0),V(0,1,0))

def parts(c,front):
    f=front['controls'];upper=V(f['pin_x'],0,f['upper_pin_z']);lower=V(f['pin_x'],0,f['lower_pin_z'])
    width=c['lever_width'];assert width<=f['receiver_width'] and c['pin_diameter']/2+c['pin_bore_clearance']<=f['pin_bore_radius']+1e-8
    outer=f['fork_gap']+2*f['lug_stock']
    # The curved foot is wider than the fork cheeks and partly enters the head
    # envelope. Retain both fitting shapes and size the unprinted pin to their
    # full width, rather than sizing the grip from the ears alone.
    envelope=max(outer,front['band_controls']['width'])
    head=-envelope/2-c['pin_axial_clearance'];cotter=envelope/2+c['cotter_station_overhang'];tip=cotter+c['pin_end_beyond_cotter']
    pin=Part.makeCylinder(c['pin_diameter']/2,tip-head,V(0,head,0),V(0,1,0)).fuse(Part.makeCylinder(c['pin_head_radius'],c['pin_head_stock'],V(0,head-c['pin_head_stock'],0),V(0,1,0)))
    pin=pin.cut(Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_clearance'],c['pin_diameter']+2,V(-c['pin_diameter']/2-1,cotter,0),V(1,0,0)))
    split,split_detail=formed_pin(c);split.rotate(V(),V(0,0,1),-90)
    # Preserve the rotated analytic child under an identity definition frame.
    # Assigning an occurrence pose directly to the rotated shape loses its turn.
    split=Part.makeCompound([split])
    shapes=dict(pin=pin,cotter=split)
    # Source-sized button rivet: retain under-head shank stock in the grip and
    # formed tail. The cap forms and length datum remain named assumptions.
    tail_h,tail_volume=shank_tail(c['rivet_diameter']/2,c['rivet_stock_length'],width,c['rivet_tail_radius'])
    button=cap(c['rivet_head_radius'],c['rivet_head_height']);button.rotate(V(),V(1,0,0),90);button.translate(V(0,-width/2,0))
    tail=cap(c['rivet_tail_radius'],tail_h);tail.rotate(V(),V(1,0,0),-90);tail.translate(V(0,width/2,0))
    shapes['rivet']=cy(c['rivet_diameter']/2,width).multiFuse([button,tail])

    rotation=App.Rotation(V(0,1,0),c['screw_axis_angle_deg']);screw_frame=App.Placement(lower,rotation)
    washer_b=c['screw_shoulder_distance'];spring_base=washer_b+c['washer_stock'];washer_a=spring_base+c['spring_installed_height'];seat=washer_a+c['washer_stock']
    assert seat<c['lever_upper_seat_distance']<c['screw_length']
    bore=c['pin_diameter']/2+c['pin_bore_clearance'];guide_end=spring_base+c['screw_guide_above_lower_washer']
    screw=cy(c['screw_eye_radius'],width).multiFuse([
        Part.makeCylinder(c['screw_guide_radius'],guide_end-10,V(0,0,10)),
        Part.makeCylinder(c['screw_radius'],c['screw_length']-10,V(0,0,10)),
        Part.makeCylinder(c['screw_shoulder_radius'],c['screw_shoulder_stock'],V(0,0,washer_b-c['screw_shoulder_stock']))])
    shapes['screw']=screw.cut(cy(bore,width+2))
    for role in ['a','b']:
        shapes['washer_'+role]=Part.makeCylinder(c['washer_outer_radius'],c['washer_stock']).cut(Part.makeCylinder(c['washer_'+role+'_bore_diameter']/2,c['washer_stock']+2,V(0,0,-1)))
    shapes['spring'],spring_curve,spring_detail=coil(c['spring_installed_height'],c)
    nut=Part.makeCylinder(c['nut_neck_radius'],c['nut_neck_length']).fuse(Part.makeBox(c['nut_wing_length'],c['nut_wing_width'],c['nut_wing_stock'],V(-c['nut_wing_length']/2,-c['nut_wing_width']/2,c['nut_neck_length'])))
    z=c['nut_neck_length']+c['nut_wing_stock'];radius=c['nut_hex_af']/math.sqrt(3)
    points=[V(radius*math.cos(math.radians(60*i)),radius*math.sin(math.radians(60*i)),z) for i in range(6)]
    nut=nut.fuse(Part.Face(Part.makePolygon(points+points[:1])).extrude(V(0,0,c['nut_hex_stock'])))
    shapes['nut']=nut.cut(Part.makeCylinder(c['screw_radius']+c['thread_bore_clearance'],z+c['nut_hex_stock']+2,V(0,0,-1)))

    # Retain genuine B-spline boundary curves for the estimated curved elbow.
    # The handle is straight; both eyes and the lower rounded end are analytic.
    curves={};edges=[]
    for role in ['outer','inner']:
        curve=Part.BSplineCurve();curve.interpolate([V(x,-width/2,z) for x,z in c['lever_'+role+'_curve_xz']]);curves[role]=curve
    start=curves['outer'].toShape().Vertexes[0].Point;outer_end=curves['outer'].toShape().Vertexes[-1].Point
    inner_start=curves['inner'].toShape().Vertexes[0].Point;finish=curves['inner'].toShape().Vertexes[-1].Point
    end=V(*c['lever_end_center']);end.y=-width/2;direction=end-V((outer_end.x+inner_start.x)/2,-width/2,(outer_end.z+inner_start.z)/2);direction.normalize()
    normal=V(-direction.z,0,direction.x);rad=c['lever_end_radius'];one=end+normal*rad;two=end-normal*rad
    edges=[curves['outer'].toShape(),Part.makeLine(outer_end,one),Part.Arc(one,end+direction*rad,two).toShape(),Part.makeLine(two,inner_start),curves['inner'].toShape(),Part.Arc(finish,V(upper.x-c['lever_eye_radius'],-width/2,upper.z),start).toShape()]
    lever=Part.Face(Part.Wire(edges)).extrude(V(0,width,0))
    # Continue the two flat member sections through a rectangular screw saddle.
    # HB133 shows the seat in profile but does not establish a circular barrel.
    # The full-width saddle is a named hidden-section estimate. A circular trial
    # also produced poorly resolved intersections with the curved profile.
    boss=Part.makeBox(2*c['lever_seat_half_width'],width,c['lever_upper_seat_distance']-seat,V(-c['lever_seat_half_width'],-width/2,seat));boss.Placement=screw_frame;lever=lever.fuse(boss)
    # Flatten the integral split bosses against the two separate receiving parts.
    for rad,z,height in [(c['washer_outer_radius']+1,-5,seat+5),(c['nut_wing_length']/2+2,c['lever_upper_seat_distance'],100)]:
        tool=Part.makeCylinder(rad,height,V(0,0,z));tool.Placement=screw_frame;lever=lever.cut(tool)
    channel=Part.makeCylinder(c['lever_screw_bore_radius'],c['screw_length']+20,V(0,0,-10));channel.Placement=screw_frame
    lever=lever.cut(channel).cut(cy(bore,width+2,upper)).cut(cy(c['lever_end_bore_radius'],width+2,V(*c['lever_end_center'])))
    for x,z in c['lever_rivet_centers_xz']:lever=lever.cut(cy(c['rivet_diameter']/2+c['rivet_hole_clearance'],width+2,V(x,0,z)))
    box=lever.BoundBox
    for role,y in [('left',-width/2),('right',0)]:
        shapes['lever_'+role]=lever.common(Part.makeBox(box.XLength+2,width/2,box.ZLength+2,V(box.XMin-1,y,box.ZMin-1)))
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed() and s.Placement.isIdentity() and s.getTolerance(1)<=1e-4,(name,s.isValid(),len(s.Solids),s.Placement,s.getTolerance(1))
    detail=dict(upper_pin_mm=list(upper),lower_pin_mm=list(lower),pin_head_seat_y_mm=head,pin_tip_y_mm=tip,cotter_station_y_mm=cotter,fork_outer_width_mm=outer,pin_joint_envelope_width_mm=envelope,
        screw_frame=list(screw_frame.toMatrix().A),washer_b_distance_mm=washer_b,spring_base_distance_mm=spring_base,washer_a_distance_mm=washer_a,lever_lower_seat_distance_mm=seat,lever_upper_seat_distance_mm=c['lever_upper_seat_distance'],screw_guide_end_mm=guide_end,
        cotter=split_detail,spring=spring_detail,rivet=dict(grip_mm=width,tail_height_mm=tail_h,tail_volume_mm3=tail_volume),
        lever_curves={k:dict(degree=v.Degree,poles_mm=[list(p) for p in v.getPoles()],knots=v.getKnots(),multiplicities=v.getMultiplicities()) for k,v in curves.items()},
        limits=['Paired lever member section and full-width rectangular integral screw saddle are inferred; B-spline curves approximate the illustrated silhouette.', 'Free-end pin and cotter stock, spring dimensions, nut form and screw shoulders are estimates.', 'Washer bore dimensions and joining-rivet stock are printed; washer outside diameters and thickness are estimates.', 'Thread interfaces use nominal cylindrical envelopes, without helices.', 'Static arrangement only; anchor supports, stops, control rods and complete service paths remain pending.'])
    return shapes,detail,{'spring_centerline':spring_curve,'lever_profile':Part.Wire(edges)}
