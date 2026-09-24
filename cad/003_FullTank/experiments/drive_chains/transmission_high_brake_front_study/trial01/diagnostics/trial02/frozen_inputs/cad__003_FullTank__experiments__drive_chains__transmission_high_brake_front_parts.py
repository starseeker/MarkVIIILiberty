"""Separate inferred forward fittings and the catalogue lining-fastener set.

End fittings use common brake coordinates; revised backing definitions retain
source lining coordinates. Fasteners use +Z along the radial shank. Their head
forms, formed tails and the unseen fitting sections are explicit approximations.
"""
import math
import FreeCAD as App
import Part
from transmission_brake_band_parts import sector,point,rotate_theta,copper_rivet
from transmission_brake_anchor_parts import steel_rivet,strip
from transmission_high_brake_joint_parts import parts as rear_parts
V=App.Vector

def parts(c,parent,bands):
    bc=parent['band_controls'];jc=dict(parent['controls'],anchor_end_deg=c['rear_anchor_end_deg'])
    rear,rd=rear_parts(jc,bc);base=rd['initial_band_details'];angles=rd['placement_angles_rad']
    inner=bc['inner_radius']+bc['lining_stock'];outer=inner+bc['steel_stock'];neutral=rd['neutral_radius_mm'];width=bc['width']
    shapes={};changed={'Def_HighBrake_anchor_end':rear['anchor_end']};detail=dict(ends={},lining_joints={},copper={},rear_anchor_end_deg=c['rear_anchor_end_deg'])
    shapes['steel_rivet'],steel=steel_rivet(c,bc['steel_stock']);detail['steel_rivet']=steel
    for key,foot,length in [('lining_normal_075',0,19.05),('lining_normal_1',0,25.4),('lining_front_1',c['foot_stock'],25.4),('lining_anchor_125',jc['anchor_outer_stock'],31.75)]:
        cc=dict(lining_stock=bc['lining_stock'],steel_stock=bc['steel_stock']+foot,straight_lining_stock=bc['straight_bore_depth'],hole_diameter=bc['hole_diameter'],countersink_angle_deg=bc['countersink_included_angle_deg'],rivet_head_recess=c['lining_head_recess'],tail_spotface_depth=c['lining_tail_spotface'],rivet_stock_length=length,rivet_tail_radius=c['lining_tail_radius'],rivet_shank_diameter=c['lining_rivet_shank_diameter'])
        shapes[key],d=copper_rivet(cc);detail['copper'][key]=dict(d,source_stock_length_mm=length,added_receiver_stock_mm=foot)
    head=detail['copper']['lining_front_1'];depth=head['head_depth_mm']
    brass=Part.makeCone(head['head_radius_mm'],bc['hole_diameter']/2,depth).fuse(Part.makeCylinder(c['brass_screw_diameter']/2,c['brass_screw_length']-depth,V(0,0,depth)))
    brass=brass.cut(Part.makeBox(2*head['head_radius_mm']+2,c['brass_slot_width'],c['brass_slot_depth']+1,V(-head['head_radius_mm']-1,-c['brass_slot_width']/2,-1)))
    shapes['lining_brass']=brass
    for role,sign,z in [('long',1,c['upper_pin_z']),('short',-1,c['lower_pin_z'])]:
        sweep=base[role]['sweep_rad'];edge=angles[role]+(0 if role=='long' else sweep)
        limit=edge+sign*c['foot_length']/neutral;lo,hi=sorted([edge,limit])
        foot=sector(outer,outer+c['foot_stock'],lo,hi,width)
        pin=V(c['pin_x'],0,z);anchor=point(outer+c['foot_stock']/2,edge+sign*c['web_station']/neutral,0)
        y=(c['fork_gap']+c['lug_stock'])/2;ears=[]
        for axial in [-y,y]:
            ears.extend([strip(pin,anchor,c['web_width'],axial-c['lug_stock']/2,c['lug_stock']),Part.makeCylinder(c['lug_outer_radius'],c['lug_stock'],pin+V(0,axial-c['lug_stock']/2,0),V(0,1,0))])
        foot=foot.multiFuse(ears)
        # The tangent web may cross the curved backing. Trim the complete
        # fitting to its real receiving cylinder, leaving a continuous seat.
        foot=foot.cut(Part.makeCylinder(outer,width+4,V(0,-width/2-2,0),V(0,1,0)))
        # Clear the future lever/screw eye from the central gap, rather than
        # leaving hidden foot material through its receiving envelope.
        pocket=Part.makeCylinder(c['receiver_eye_radius']+c['receiver_radial_clearance'],c['fork_gap'],pin+V(0,-c['fork_gap']/2,0),V(0,1,0))
        bore=Part.makeCylinder(c['pin_bore_radius'],width+4,pin+V(0,-width/2-2,0),V(0,1,0))
        foot=foot.cut(pocket).cut(bore)
        band=bands[role].copy();inv=App.Placement(V(),rotate_theta(angles[role])).inverse();tools=[];steel_joints=[]
        for station,axial in zip(c['steel_stations'],c['steel_axial']):
            theta=edge+sign*station/neutral;y=sign*axial
            pose=App.Placement(point(inner+c['steel_head_recess'],theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
            hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
            tool=Part.makeCylinder(hole,steel['grip_mm']+20,V(0,0,-5)).fuse(Part.makeCone(c['steel_head_radius']+5*slope,hole,steel['head_depth_mm']+5,V(0,0,-5)))
            rotation=App.Placement(V(),App.Rotation(V(0,0,1),90));tool.Placement=pose.multiply(rotation)
            foot=foot.cut(tool);local=tool.copy();local.Placement=inv.multiply(tool.Placement);tools.append(local)
            spot=Part.makeCylinder(c['steel_tail_radius']+.05,steel['tail_height_mm']+5,V(0,0,steel['grip_mm']));spot.Placement=pose;foot=foot.cut(spot)
            steel_joints.append(dict(station_mm=station,axial_mm=y,theta_rad=theta,frame=list(pose.toMatrix().A)))
        band=band.cut(Part.makeCompound(tools));joints=[]
        for index,h in enumerate(base[role]['holes']):
            if role=='long':key='lining_front_1' if index<2 else 'lining_normal_075' if index==11 else 'lining_normal_1'
            else:key='lining_anchor_125' if index==0 else 'lining_front_1' if index==4 else 'lining_brass' if index==5 else 'lining_normal_1'
            pose=App.Placement(App.Matrix(*h['frame'])).multiply(App.Placement(V(0,0,c['lining_head_recess']),App.Rotation()))
            common=App.Placement(V(),rotate_theta(angles[role])).multiply(pose)
            drill=Part.makeCylinder(bc['steel_hole_radius'],40,V(0,0,-1));drill.Placement=common
            if key in ['lining_front_1','lining_brass']:foot=foot.cut(drill)
            if key=='lining_anchor_125':changed['Def_HighBrake_anchor_end']=changed['Def_HighBrake_anchor_end'].cut(drill)
            if key!='lining_brass':
                d=detail['copper'][key];spot=Part.makeCylinder(c['lining_tail_radius']+.05,d['tail_height_mm']+5,V(0,0,d['grip_mm']))
                if key=='lining_front_1':spot.Placement=common;foot=foot.cut(spot)
                elif key=='lining_anchor_125':spot.Placement=common;changed['Def_HighBrake_anchor_end']=changed['Def_HighBrake_anchor_end'].cut(spot)
                else:spot.Placement=pose;band=band.cut(spot)
            joints.append(dict(index=index+1,definition_role=key,local_frame=list(pose.toMatrix().A),common_frame=list(common.toMatrix().A)))
        shapes[role+'_end']=foot;changed['Def_HighBrake_'+role+'_band']=band
        detail['ends'][role]=dict(pin_center_mm=list(pin),foot_angles_rad=[lo,hi],steel_joints=steel_joints,fork_outer_width_mm=c['fork_gap']+2*c['lug_stock'],receiver_width_mm=c['receiver_width'])
        detail['lining_joints'][role]=joints
    for name,s in {**shapes,**changed}.items():assert s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(),(name,s.isValid(),len(s.Solids))
    detail['limitations']=['Forward fitting shape, fork width, pin bores and fastener head forms are estimates.','Source rivet stock-length datum remains uncertain; formed tails conserve the selected under-head stock model.','Brass screw threads represented by nominal shank and receiving bore, without helices.','M356 pins/cotters, lever members, adjustment, anchor supports and stops remain to populate.']
    return shapes,changed,detail


def relieve_case(c,case,centers,width):
    """Bounded estimated bridge relief; no bearing-seat or drum edits."""
    result=case.copy();tools=[]
    for center in centers:
        axial=width+2*c['case_axial_margin'];low=center.y-axial/2
        cylinder=Part.makeCylinder(c['case_clearance_radius'],axial,V(center.x,low,center.z),V(0,1,0))
        window=Part.makeBox(c['case_relief_x_max']-c['case_relief_x_min'],axial,2*c['case_relief_half_height'],V(c['case_relief_x_min'],low,-c['case_relief_half_height']))
        tool=cylinder.common(window);result=result.cut(tool);tools.append(tool)
    assert result.isValid() and len(result.Solids)==1 and result.Solids[0].isClosed()
    return result,dict(centers_case_mm=[list(v) for v in centers],radius_mm=c['case_clearance_radius'],axial_width_mm=width+2*c['case_axial_margin'],scope='Estimated rear bridge relief only; preserve all material outside the two bounded clearance envelopes.')
