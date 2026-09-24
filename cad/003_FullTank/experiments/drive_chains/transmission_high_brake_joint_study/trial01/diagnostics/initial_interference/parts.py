"""Riveted M361 end and six-screw coupling; unprinted profiles remain estimates.

Band/lining definitions retain their first lining station as angle zero. Anchor
end and fastener placements use common brake coordinates: X forward, Y port,
Z up. Analytic annular sectors provide the rear tails and stepped bearing lands.
"""
import math
import FreeCAD as App
import Part
from transmission_high_brake_band_parts import parts as initial_parts
from transmission_brake_band_parts import sector,point,rotate_theta
from transmission_brake_anchor_parts import steel_rivet,strip
from transmission_brake_stop_parts import hexagon

V=App.Vector

def parts(c,bc):
    shapes,base=initial_parts(bc)
    neutral=bc['inner_radius']+bc['lining_stock']/2
    ri=bc['inner_radius']+bc['lining_stock'];ro=ri+bc['steel_stock'];width=bc['width']
    tail=c['rear_tail_length']/neutral
    short=math.radians(c['short_lining_start_deg'])
    long_end=short-2*tail-c['rear_steel_gap']/neutral
    long=long_end-base['long']['sweep_rad']
    long_tail_end=long_end+tail
    angles=dict(long=long,short=short)
    for role in ['long','short']:
        s=shapes[role+'_band'];sweep=base[role]['sweep_rad']
        extension=sector(ri,ro,sweep-1/neutral,sweep+tail,width) if role=='long' else sector(ri,ro,-tail,1/neutral,width)
        s=s.fuse(extension)
        # The estimated reinforced terminal belongs to the same manufactured
        # long band. Its form is unresolved; it supplies the receiving thread
        # engagement required by the six catalogue coupling screws.
        if role=='long':s=s.fuse(sector(ro-.1,ro+c['long_end_pad_stock'],sweep,sweep+tail,width))
        shapes[role+'_band']=s
    anchor_start=long_end-math.radians(c['anchor_start_margin_deg'])
    anchor_end=math.radians(c['anchor_end_deg'])
    outer=ro+c['anchor_outer_stock']
    assert ro+c['long_end_pad_stock']<outer and anchor_start<long_end<long_tail_end<short<anchor_end
    anchor=sector(ro,outer,anchor_start,anchor_end,width)
    relief=sector(ro-.1,ro+c['long_end_pad_stock'],long_end,long_tail_end,width+2)
    anchor=anchor.cut(relief)
    lug_theta=math.radians(c['anchor_lug_angle_deg'])
    lug_center=point(c['anchor_lug_radius'],lug_theta,0)
    lug=Part.makeCylinder(c['anchor_eye_outer_radius'],c['anchor_eye_width'],lug_center+V(0,-c['anchor_eye_width']/2,0),V(0,1,0))
    web=strip(point((ro+outer)/2,lug_theta,0),lug_center,c['anchor_web_width'],-c['anchor_eye_width']/2,c['anchor_eye_width'])
    anchor=anchor.multiFuse([lug,web])
    eye=Part.makeCylinder(c['anchor_eye_bore_radius'],width+4,lug_center+V(0,-width/2-2,0),V(0,1,0))
    anchor=anchor.cut(eye)

    rc=dict(c,foot_stock=c['anchor_outer_stock'])
    rivet,rd=steel_rivet(rc,bc['steel_stock'])
    shapes['anchor_rivet']=rivet
    screw_length=c['anchor_outer_stock']-c['coupling_head_spotface']
    assert screw_length>c['long_end_pad_stock']>0
    screw=Part.makeCylinder(c['coupling_screw_diameter']/2,screw_length,V(0,0,-screw_length)).fuse(
        hexagon(c['coupling_head_af'],c['coupling_head_stock']))
    shapes['coupling_screw']=screw
    rivets=[];screws=[]
    for column,along in enumerate(c['attachment_columns_mm']):
        for row,y in enumerate(c['attachment_rows_mm']):
            # Six rivets bind the short tail to M361; six screws join its
            # opposite stepped land to the reinforced long tail.
            theta=short-tail+along/neutral
            pose=App.Placement(point(ri+c['steel_head_recess'],theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
            hole=c['steel_shank_diameter']/2+c['steel_hole_clearance']
            slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2))
            tool=Part.makeCylinder(hole,rd['grip_mm']+20,V(0,0,-5)).fuse(
                Part.makeCone(c['steel_head_radius']+5*slope,hole,rd['head_depth_mm']+5,V(0,0,-5)))
            tool.Placement=pose
            anchor=anchor.cut(tool)
            local=tool.copy();local.Placement=App.Placement(V(),rotate_theta(short)).inverse().multiply(pose)
            shapes['short_band']=shapes['short_band'].cut(local)
            spot=Part.makeCylinder(c['steel_tail_radius']+.05,rd['tail_height_mm']+5,V(0,0,rd['grip_mm']));spot.Placement=pose
            anchor=anchor.cut(spot)
            rivets.append(dict(column=column,row=row,theta_rad=theta,along_mm=along,axial_mm=y,frame=list(pose.toMatrix().A)))

            theta=long_end+along/neutral
            pose=App.Placement(point(outer-c['coupling_head_spotface'],theta,y),App.Rotation(V(0,0,1),point(1,theta,0)))
            tool=Part.makeCylinder(c['coupling_hole_radius'],screw_length+2,V(0,0,-screw_length))
            tool.Placement=pose;anchor=anchor.cut(tool)
            local=tool.copy();local.Placement=App.Placement(V(),rotate_theta(long)).inverse().multiply(pose)
            shapes['long_band']=shapes['long_band'].cut(local)
            spotrad=c['coupling_head_af']/math.sqrt(3)+.1
            spot=Part.makeCylinder(spotrad,c['coupling_head_stock']+3);spot.Placement=pose;anchor=anchor.cut(spot)
            screws.append(dict(column=column,row=row,theta_rad=theta,along_mm=along,axial_mm=y,frame=list(pose.toMatrix().A)))
    shapes['anchor_end']=anchor
    for name,s in shapes.items():
        assert s.isValid() and len(s.Solids)==1 and s.Solids[0].isClosed(),(name,s.isValid(),len(s.Solids))
    details=dict(initial_band_details=base,placement_angles_rad=angles,neutral_radius_mm=neutral,
        long_lining_end_rad=long_end,long_steel_end_rad=long_tail_end,short_steel_start_rad=short-tail,
        anchor_start_rad=anchor_start,anchor_end_rad=anchor_end,anchor_outer_radius_mm=outer,
        anchor_pin_center_mm=list(lug_center),anchor_eye_bore_radius_mm=c['anchor_eye_bore_radius'],
        rivets=rivets,screws=screws,rivet=rd,screw_length_mm=screw_length,
        screw_thread_engagement_envelope_mm=c['long_end_pad_stock'],
        limitations=['Unprinted terminal reinforcement and stepped anchor profile estimated.',
            'Screw threads represented by nominal major-diameter solids and receiving clearance bores, not helices.',
            'Source countersunk stock-length datum retains earlier uncertainty.',
            'Free-end formed eyes and fasteners, external anchor bracket/pin, adjustment and stops pending.'])
    return shapes,details
