"""Estimated front brake ears and the coupled M330/M331/M332/M333/M335 linkage.

Ear definitions share the upper band's drum frame (+X forward, +Y shaft, +Z up).
The lever origin is its lower-band pin. Screw origin is its upper-band pin,
with +Z pointing toward the adjusting nut. Swivel and nut axes follow that screw.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_band_parts import sector,point
from transmission_brake_anchor_parts import strip

V=App.Vector


def cy(radius,width,center=None):
    return Part.makeCylinder(radius,width,(center or V())+V(0,-width/2,0),V(0,1,0))


def coil(height,c):
    wire=c['spring_wire_radius'];radius=c['spring_mean_radius'];pitch=(height-2*wire)/c['spring_turns']
    assert pitch>2*wire
    path=Part.Wire(Part.makeHelix(pitch,height-2*wire+pitch/2,radius).Edges)
    section=Part.Wire([Part.makeCircle(wire,V(radius,0,0),V(0,radius,pitch/(2*math.pi)))])
    shape=path.makePipeShell([section],True,True)
    shift=V(0,0,wire-pitch/4);shape.translate(shift);path.translate(shift)
    shape=shape.common(Part.makeCylinder(radius+wire+1,height))
    return shape,path,dict(installed_height_mm=height,pitch_mm=pitch,mean_radius_mm=radius,wire_radius_mm=wire,
        generated_centerline_length_mm=path.Length,ends='Planar ground ends cut from extended helix; source section/turn count estimated.')


def parts(c,anchor_report,saved_bands):
    a=anchor_report['controls'];old=anchor_report['details'];bc=old['new_band_controls'];bd=old['band_details']
    assert c['foot_stock']==a['foot_stock'],'Different front stock requires a separately qualified rivet grip definition.'
    shapes={};bands={};details={}
    eye_width=2*c['lug_y']-c['lug_stock']-2*c['eye_side_clearance']
    outer_width=2*c['lug_y']+c['lug_stock'];bore=c['pin_diameter']/2+c['pin_bore_allowance']
    # The same M336 pin spans either ear. Head inboard, one split pin outboard.
    head=-outer_width/2-c['pin_axial_clearance'];cotter=outer_width/2+c['cotter_station_overhang']
    tip=cotter+c['pin_end_beyond_cotter']
    pin=Part.makeCylinder(c['pin_diameter']/2,tip-head,V(0,head,0),V(0,1,0)).fuse(
        Part.makeCylinder(c['pin_head_radius'],c['pin_head_stock'],V(0,head-c['pin_head_stock'],0),V(0,1,0)))
    pin=pin.cut(Part.makeCylinder(c['cotter_hole_radius'],c['pin_diameter']+2,V(-c['pin_diameter']/2-1,cotter,0),V(1,0,0)))
    shapes['pin']=pin
    screw=cy(c['screw_eye_radius'],eye_width).multiFuse([
        Part.makeCylinder(c['screw_radius'],c['screw_length']-10,V(0,0,10)),
        Part.makeCylinder(c['screw_shoulder_radius'],c['screw_shoulder_stock'],V(0,0,c['screw_shoulder_distance']-c['screw_shoulder_stock']))])
    shapes['screw']=screw.cut(cy(bore,eye_width+2))
    swivel=cy(c['swivel_radius'],c['swivel_width'])
    gap=c['swivel_gap'];flat=c['swivel_flat_distance']
    # Local flats are inside the fork gap. The end journals remain circular.
    swivel=swivel.cut(Part.makeBox(100,gap,100,V(-50,-gap/2,flat)))
    swivel=swivel.cut(Part.makeBox(100,gap,100,V(-50,-gap/2,-100-flat)))
    shapes['swivel']=swivel.cut(Part.makeCylinder(c['screw_radius']+c['thread_bore_allowance'],100,V(0,0,-50)))
    nut=Part.makeCylinder(c['nut_neck_radius'],c['nut_neck_length']).fuse(
        Part.makeBox(c['nut_wing_length'],c['nut_wing_width'],c['nut_wing_stock'],V(-c['nut_wing_length']/2,-c['nut_wing_width']/2,c['nut_neck_length'])))
    z=c['nut_neck_length']+c['nut_wing_stock'];radius=c['nut_hex_radius']
    points=[V(radius*math.cos(math.radians(i*60)),radius*math.sin(math.radians(i*60)),z) for i in range(6)]
    nut=nut.fuse(Part.Face(Part.makePolygon(points+points[:1])).extrude(V(0,0,c['nut_hex_length'])))
    shapes['nut']=nut.cut(Part.makeCylinder(c['screw_radius']+c['thread_bore_allowance'],z+c['nut_hex_length']+2,V(0,0,-1)))
    swivel_center=V(c['swivel_forward_offset'],0,0);end=V(c['lever_end_x'],0,c['lever_end_z'])
    lever=cy(c['lever_eye_radius'],eye_width).multiFuse([
        cy(c['lever_head_radius'],c['swivel_width'],swivel_center),
        strip(V(),swivel_center,c['lever_web_width'],-c['swivel_width']/2,c['swivel_width']),
        strip(V(c['lever_leg_root_x'],0,c['lever_leg_root_z']),end,c['lever_leg_width'],-c['lever_leg_stock']/2,c['lever_leg_stock']),
        cy(c['lever_end_radius'],c['lever_leg_stock'],end)])
    lever=lever.cut(Part.makeBox(200,gap,150,V(c['lever_slot_start_x'],-gap/2,-75)))
    lever=lever.cut(cy(bore,eye_width+2)).cut(cy(c['swivel_radius']+c['swivel_bore_allowance'],c['swivel_width']+2,swivel_center))
    shapes['lever']=lever.cut(cy(c['lever_end_bore_radius'],c['lever_leg_stock']+2,end))
    vector=V(c['swivel_forward_offset'],0,-2*c['pin_height']);length=vector.Length
    rotation=App.Rotation(V(0,0,1),vector);spring_height=length-flat-c['screw_shoulder_distance']
    shapes['spring'],curve,spring_details=coil(spring_height,c)
    for role in ['low','track']:
        d=bd['brakes'][role];outer=old['brakes'][role]['band_outer_radius_mm'];inner=outer-bc['steel_stock'];width=old['brakes'][role]['band_width_mm']
        theta0=d['half_start_rad'];theta1=theta0+math.radians(c[role+'_foot_sweep_deg'])
        pinx=math.sqrt((outer+c['pin_radial_offset'])**2-c['pin_height']**2);center=V(pinx,0,c['pin_height'])
        band=saved_bands[role].copy();assert band.Placement.isIdentity()
        foot=sector(outer,outer+c['foot_stock'],theta0,theta1,width)
        end=point(outer+c['foot_stock']/2,math.radians(c['lug_web_theta_deg']),0)
        lugs=[]
        for y in [-c['lug_y'],c['lug_y']]:
            web=strip(center,end,c['lug_web_width'],y-c['lug_stock']/2,c['lug_stock'])
            lug=Part.makeCylinder(c['lug_radius'],c['lug_stock'],center+V(0,y-c['lug_stock']/2,0),V(0,1,0))
            lugs.extend([web,lug])
        ear=foot.multiFuse(lugs).cut(sector(.01,outer,theta0,d['half_end_rad'],width+2))
        ear=ear.cut(Part.makeCylinder(bore,width+2,center+V(0,-width/2-1,0),V(0,1,0)))
        blank=sector(inner,outer,theta0,d['half_end_rad'],width);lining_joints=[];steel_joints=[]
        for joint in d['joints']:
            pose=App.Placement(App.Matrix(*joint['frame']));angle=math.atan2(pose.Base.z,pose.Base.x)
            if angle>theta1:continue
            assert joint['segment']==1 and joint['hole'] in [1,2,3]
            old_spot=Part.makeCylinder(bc['rivet_tail_radius']+.05,10,V(0,0,bd['rivet']['grip_mm']));old_spot.Placement=pose
            band=band.fuse(blank.common(old_spot))
            drill=Part.makeCylinder(bc['rivet_shank_diameter']/2+bc['steel_hole_clearance'],old['long_copper_rivet']['grip_mm']+20,V(0,0,-5));drill.Placement=pose
            band=band.cut(drill)
            spot=Part.makeCylinder(bc['rivet_tail_radius']+.05,old['long_copper_rivet']['tail_height_mm']+5,V(0,0,old['long_copper_rivet']['grip_mm']));spot.Placement=pose
            ear=ear.cut(drill.fuse(spot));lining_joints.append(joint)
        assert len(lining_joints)==3
        offsets=[2,6,10,14] if role=='low' else [8,12,16];ys=[-15.875,15.875] if role=='low' else [-12.7,12.7]
        for i,(offset,y) in enumerate([(off,y) for off in offsets for y in ys],1):
            theta=theta0+math.radians(offset);pose=App.Placement(point(inner+a['steel_head_recess'],theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
            hole=a['steel_shank_diameter']/2+a['steel_hole_clearance'];k=math.tan(math.radians(a['steel_countersink_angle_deg']/2))
            tool=Part.makeCylinder(hole,old['steel_rivet']['grip_mm']+20,V(0,0,-5)).fuse(
                Part.makeCone(a['steel_head_radius']+5*k,hole,old['steel_rivet']['head_depth_mm']+5,V(0,0,-5)))
            tool.Placement=pose;band=band.cut(tool);ear=ear.cut(tool)
            spot=Part.makeCylinder(a['steel_tail_radius']+.05,old['steel_rivet']['tail_height_mm']+5,V(0,0,old['steel_rivet']['grip_mm']));spot.Placement=pose
            ear=ear.cut(spot);steel_joints.append(dict(index=i,angle_deg=math.degrees(theta),y_mm=y,frame=list(pose.toMatrix().A)))
        shapes[role+'_ear']=ear;bands[role]=band
        details[role]=dict(pin_x_mm=pinx,upper_pin_mm=list(center),lower_pin_mm=[pinx,0,-c['pin_height']],
            swivel_mm=[pinx+c['swivel_forward_offset'],0,-c['pin_height']],foot_start_rad=theta0,foot_end_rad=theta1,
            lining_joints=lining_joints,steel_joints=steel_joints,band_outer_radius_mm=outer,band_width_mm=width)
    for name,s in {**shapes,**bands}.items():assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
    return shapes,bands,dict(brakes=details,eye_width_mm=eye_width,outer_lug_width_mm=outer_width,
        pin_head_seat_y_mm=head,cotter_y_mm=cotter,pin_tip_y_mm=tip,screw_rotation=list(rotation.Q),
        upper_eye_to_swivel_mm=length,spring=spring_details,thread_representation='Nominal cylindrical male/female surfaces, no thread helix.',
        swivel_retention='Crossed adjusting screw constrains axial travel; precise historical end retention remains unresolved.'),{'spring_centerline':curve}
