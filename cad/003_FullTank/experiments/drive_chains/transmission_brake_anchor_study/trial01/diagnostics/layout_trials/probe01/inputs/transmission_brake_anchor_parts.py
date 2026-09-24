"""Estimated rear brake-band brackets, riveted feet and retained anchor pins.

Bracket coordinates are the upper band's drum coordinates. MX49's lug lies at
negative Y; MX47's lies at positive Y. Rigid X half-turns supply lower halves.
Round eyes, pins and holes are analytic; hidden joint sections remain estimates.
"""
import copy,math
import FreeCAD as App
import Part
from transmission_brake_band_parts import parts as band_parts,sector,point,copper_rivet
from transmission_frame_joint_parts import cap
V=App.Vector


def shank_tail(radius,length,grip,tail_radius):
    volume=math.pi*radius**2*(length-grip);lo,hi=0.,tail_radius
    assert 0<volume<2*math.pi*tail_radius**3/3
    for _ in range(80):
        h=(lo+hi)/2
        if math.pi*h*(3*tail_radius**2+h*h)/6<volume:lo=h
        else:hi=h
    return (lo+hi)/2,volume


def steel_rivet(c,band_stock):
    rad=c['steel_shank_diameter']/2;hole=rad+c['steel_hole_clearance']
    depth=(c['steel_head_radius']-hole)/math.tan(math.radians(c['steel_countersink_angle_deg']/2))
    grip=band_stock+c['foot_stock']-c['steel_tail_spotface']-c['steel_head_recess']
    h,volume=shank_tail(rad,c['steel_stock_length'],grip-depth,c['steel_tail_radius'])
    shape=Part.makeCone(c['steel_head_radius'],hole,depth).multiFuse([
        Part.makeCylinder(rad,grip-depth,V(0,0,depth)),cap(c['steel_tail_radius'],h).translated(V(0,0,grip))])
    return shape,dict(grip_mm=grip,head_depth_mm=depth,tail_height_mm=h,tail_volume_mm3=volume)


def button_rivet(c,role):
    rad=c['retainer_rivet_diameter']/2;spacer=c['spring_spacer_stock'] if role=='low' else 0.
    grip=c['lug_stock']+spacer+c['spring_stock'];length=c['retainer_rivet_'+role+'_stock'];headrad=2.25*rad
    h,volume=shank_tail(rad,length,grip,headrad)
    head=cap(headrad,.6*c['retainer_rivet_diameter']);head.rotate(V(),V(1,0,0),90)
    tail=cap(headrad,h);tail.rotate(V(),V(1,0,0),-90);tail.translate(V(0,grip,0))
    return head.multiFuse([Part.makeCylinder(rad,grip,V(),V(0,1,0)),tail]),dict(grip_mm=grip,stock_length_mm=length,tail_height_mm=h,tail_volume_mm3=volume)


def strip(a,b,width,y0,stock):
    delta=b-a;normal=V(-delta.z,0,delta.x);normal.normalize()
    ps=[a-normal*width/2,a+normal*width/2,b+normal*width/2,b-normal*width/2]
    ps=[p+V(0,y0,0) for p in ps]
    return Part.Face(Part.makePolygon(ps+ps[:1])).extrude(V(0,stock,0))


def spring(c):
    # Open fork at the free end engages an annular pin groove. This retention
    # form is estimated; the source identifies the spring but not its section.
    width=c['spring_width'];stock=c['spring_stock'];stud=V(5,0,c['spring_stud_z'])
    shape=strip(V(),stud,width,0,stock).multiFuse([
        Part.makeCylinder(16,stock,V(),V(0,1,0)),Part.makeCylinder(width/2,stock,stud,V(0,1,0))])
    slot=Part.makeCylinder(9.15,stock+2,V(0,-1,0),V(0,1,0)).fuse(Part.makeBox(18.3,stock+2,30,V(-9.15,-1,-30)))
    hole=Part.makeCylinder(c['retainer_rivet_diameter']/2+c['spring_hole_clearance'],stock+2,stud+V(0,-1,0),V(0,1,0))
    return shape.cut(slot.fuse(hole))


def parts(c,band_controls,link_report):
    bc=copy.deepcopy(band_controls);bc['rear_split_half_gap_deg']=c['rear_split_half_gap_deg']
    shapes,bd,curves=band_parts(bc);new={};changed={};details={}
    lc=copy.deepcopy(bc);lc['steel_stock']+=c['foot_stock'];lc['rivet_stock_length']=c['lining_long_stock']
    new['long_copper_rivet'],long_detail=copper_rivet(lc)
    new['steel_rivet'],steel_detail=steel_rivet(c,bc['steel_stock'])
    new['spring']=spring(c)
    new['spacer']=Part.makeCylinder(c['spring_spacer_od']/2,c['spring_spacer_stock'],V(),V(0,1,0)).cut(
        Part.makeCylinder(c['spring_spacer_id']/2,c['spring_spacer_stock']+2,V(0,-1,0),V(0,1,0)))
    anchor=link_report['dimensions']['lower_anchor_radius_mm'];link=link_report['controls']
    for role in ['low','track']:
        d=bd['brakes'][role];width=bc[role]['width']+2*bc['steel_side_overhang'];band=shapes[role+'_band'];inner=d['outer_radius_mm'];outer=inner+bc['steel_stock']
        theta0=math.radians(c['foot_start_deg']);theta1=d['half_end_rad'];assert theta0<theta1
        blank=sector(inner,outer,d['half_start_rad'],theta1,width)
        foot=sector(outer,outer+c['foot_stock'],theta0,theta1,width)
        lugy=(-1 if role=='low' else 1)*width/4;center=V(-anchor,0,0)
        end=point(outer+c['foot_stock']/2,math.radians(c['lug_web_theta_deg']),0)
        web=strip(center,end,c['lug_web_width'],lugy-c['lug_stock']/2,c['lug_stock'])
        ear=Part.makeCylinder(c['lug_radius'],c['lug_stock'],center+V(0,lugy-c['lug_stock']/2,0),V(0,1,0))
        body=foot.multiFuse([web,ear])
        # The gap admits the complete round lug. In the band sector, the web
        # starts at the backing outer face rather than penetrating its lining.
        body=body.cut(sector(.01,outer,.0001,theta1,width+2))
        bore=Part.makeCylinder(link['lower_pin_diameter']/2+c['lug_bore_allowance'],width+4,center+V(0,-width/2-2,0),V(0,1,0))
        stud=center+V(5,0,c['spring_stud_z'])
        spring_hole=Part.makeCylinder(c['retainer_rivet_diameter']/2+c['spring_hole_clearance'],width+4,stud+V(0,-width/2-2,0),V(0,1,0))
        body=body.cut(bore.fuse(spring_hole))
        lining_joints=[];steel_joints=[]
        for joint in d['joints']:
            pose=App.Placement(App.Matrix(*joint['frame']));angle=math.atan2(pose.Base.z,pose.Base.x)
            if angle<theta0:continue
            assert joint['segment']==3 and joint['hole'] in [8,9]
            # Fill the former shallow upset-head spotface inside the band,
            # then retain the through bore for the extended shank.
            old_spot=Part.makeCylinder(bc['rivet_tail_radius']+.05,10,V(0,0,bd['rivet']['grip_mm']));old_spot.Placement=pose
            band=band.fuse(blank.common(old_spot))
            drill=Part.makeCylinder(bc['rivet_shank_diameter']/2+bc['steel_hole_clearance'],long_detail['grip_mm']+20,V(0,0,-5));drill.Placement=pose
            band=band.cut(drill)
            spot=Part.makeCylinder(bc['rivet_tail_radius']+.05,long_detail['tail_height_mm']+5,V(0,0,long_detail['grip_mm']));spot.Placement=pose
            body=body.cut(drill.fuse(spot));lining_joints.append(joint)
        assert len(lining_joints)==2
        locations=([(angle,y) for angle in [162,166,170,174] for y in [-12.7,12.7]] if role=='low' else
                   [(angle,y) for angle in [163,169] for y in [-25.4,0,25.4]]+[(174,0)])
        for index,(deg,y) in enumerate(locations,1):
            angle=math.radians(deg);direction=point(1,angle,0)
            pose=App.Placement(point(inner+c['steel_head_recess'],angle,y),App.Rotation(V(0,0,1),direction))
            hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];k=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
            tool=Part.makeCylinder(hole,steel_detail['grip_mm']+20,V(0,0,-5)).fuse(
                Part.makeCone(c['steel_head_radius']+5*k,hole,steel_detail['head_depth_mm']+5,V(0,0,-5)))
            tool.Placement=pose;band=band.cut(tool);body=body.cut(tool)
            spot=Part.makeCylinder(c['steel_tail_radius']+.05,steel_detail['tail_height_mm']+5,V(0,0,steel_detail['grip_mm']));spot.Placement=pose
            body=body.cut(spot);steel_joints.append(dict(index=index,angle_deg=deg,y_mm=y,frame=list(pose.toMatrix().A)))
        # Pin definition runs from the inboard link toward the outboard spring;
        # the opposite vehicle side uses a rigid half-turn about X.
        head=-width/2-c['link_axial_allowance']-link['link_band_side_clearance']-link['lower_stock']
        spacer=c['spring_spacer_stock'] if role=='low' else 0.
        spring_inner=width/4+c['lug_stock']/2+spacer
        groove_start=spring_inner-.15;groove_end=spring_inner+c['spring_stock']+.15;tip=groove_end+c['pin_tail_extension']
        pin=Part.makeCylinder(link['lower_pin_diameter']/2,tip-head,V(0,head,0),V(0,1,0)).fuse(
            Part.makeCylinder(c['pin_head_radius'],c['pin_head_stock'],V(0,head-c['pin_head_stock'],0),V(0,1,0)))
        ring=Part.makeCylinder(link['lower_pin_diameter']/2+1,groove_end-groove_start,V(0,groove_start,0),V(0,1,0)).cut(
            Part.makeCylinder(9,groove_end-groove_start+2,V(0,groove_start-1,0),V(0,1,0)))
        pin=pin.cut(ring)
        new[role+'_bracket']=body;new[role+'_pin']=pin;new[role+'_retainer_rivet'],retainer=button_rivet(c,role)
        changed[role+'_band']=band
        outward=-1 if role=='low' else 1
        spring_y=lugy+outward*(c['lug_stock']/2+spacer)-(c['spring_stock'] if outward<0 else 0)
        details[role]=dict(band_width_mm=width,band_outer_radius_mm=outer,foot_start_rad=theta0,foot_end_rad=theta1,lug_y_mm=lugy,
            anchor_radius_mm=anchor,lining_joints=lining_joints,steel_joints=steel_joints,retainer=retainer,
            retainer_stud_xz_mm=[stud.x,stud.z],spring_y_mm=spring_y,outward_sign=outward,
            spring_spacer_mm=spacer,pin_head_seat_y_mm=head,pin_groove_y_mm=[groove_start,groove_end],pin_tip_y_mm=tip)
    for name,s in {**new,**changed}.items():assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
    return new,changed,dict(brakes=details,band_details=bd,steel_rivet=steel_detail,long_copper_rivet=long_detail,new_band_controls=bc)
