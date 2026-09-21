"""Bevel wheels, dog clutch, nominal fasteners and the thrust-bearing stack."""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder,box,revolve,spline_envelope,outline_face
from transmission_bevel_tooth import tooth,repeated_teeth


def toothed_blanks(c,sleeve):
    shapes={};reports={}
    for key,n,m in [('wheel',c['wheel_teeth'],c['pinion_teeth']),('pinion',c['pinion_teeth'],c['wheel_teeth'])]:
        single,d=tooth(n,m,c['pitch_numerator'],c['pitch_denominator'],c['tooth_face_width'],c['pressure_angle'],c['tooth_thinning'],c['flank_samples'])
        ri,yi=d['root_radial_axial_inner_mm'];ro,yo=d['root_radial_axial_outer_mm']
        if key=='wheel':
            face=sleeve['flange_limits_y_mm'][0]
            profile=[(c['gear_bore'],c['gear_web_front']),(ri-c['web_transition_radial'],c['gear_web_front']),
                (ri,yi-c['root_embed']),(ro,yo-c['root_embed']),(ro,c['gear_rim_back']),
                (c['flange_pocket_radius'],c['gear_rim_back']),(c['flange_pocket_radius'],face),(c['gear_bore'],face)]
            blank=revolve(profile)
        else:
            blank=Part.makeCone(ri,ro,yo-yi,App.Vector(0,yi-c['root_embed'],0),App.Vector(0,1,0))
            blank=blank.fuse(cylinder(c['input_journal_radius'],yo-1,c['input_spline_start']))
            blank=blank.fuse(spline_envelope(c['input_spline_root'],c['input_spline_tip'],c['input_spline_width'],c['input_spline_count'],c['input_spline_start']-.1,c['input_thread_start']))
            blank=blank.fuse(cylinder(c['input_thread_radius'],c['input_thread_start']-.1,c['input_shaft_end']))
            hole=Part.makeCylinder(c['input_cotter_diameter']/2,c['input_thread_radius']*2+2,App.Vector(-c['input_thread_radius']-1,c['input_cotter_station'],0),App.Vector(1,0,0))
            blank=blank.cut(hole)
        phase=0 if key=='wheel' else 180/n
        shape=blank.multiFuse(repeated_teeth(single,n,phase)).removeSplitter()
        assert shape.isValid() and len(shape.Solids)==1,key
        if key=='pinion':shape.rotate(App.Vector(),App.Vector(0,0,1),-90)
        shapes[key]=shape;reports[key]=d
    return shapes,reports


def dog_sector(inner,outer,low,high,center,width):
    def p(r,a):return App.Vector(r*math.cos(math.radians(a)),low,r*math.sin(math.radians(a)))
    a,b=center-width/2,center+width/2
    edges=[Part.makeLine(p(inner,a),p(outer,a)),Part.Arc(p(outer,a),p(outer,center),p(outer,b)).toShape(),
        Part.makeLine(p(outer,b),p(inner,b)),Part.Arc(p(inner,b),p(inner,center),p(inner,a)).toShape()]
    return Part.Face(Part.Wire(edges)).extrude(App.Vector(0,high-low,0))


def formed_rivet(radius,low,high,length,height):
    extra=length-(high-low);assert extra>0
    tail_radius=math.sqrt((6*radius*radius*extra/height-height*height)/3)
    sphere_radius=(tail_radius*tail_radius+height*height)/(2*height)
    caps=[]
    for face,sign in [(low,-1),(high,1)]:
        center=face-sign*(sphere_radius-height)
        angle=math.acos((sphere_radius-height)/sphere_radius)
        axis=App.Vector(0,face,0);base=App.Vector(tail_radius,face,0);tip=App.Vector(0,face+sign*height,0)
        mid=App.Vector(sphere_radius*math.sin(angle/2),center+sign*sphere_radius*math.cos(angle/2),0)
        profile=Part.Wire([Part.makeLine(axis,base),Part.Arc(base,mid,tip).toShape(),Part.makeLine(tip,axis)])
        cap=Part.Face(profile).revolve(App.Vector(),App.Vector(0,1,0),360)
        assert cap.isValid() and len(cap.Solids)==1
        assert abs(cap.Volume-math.pi*radius*radius*extra)<1e-5
        caps.append(cap)
    shape=cylinder(radius,low,high).multiFuse(caps).removeSplitter()
    assert abs(shape.Volume-math.pi*radius*radius*((high-low)+2*extra))<1e-5
    return shape,dict(grip_mm=high-low,blank_length_mm=length,tail_upset_mm=extra,head_base_radius_mm=tail_radius,
        tail_volume_mm3=caps[1].Volume,displaced_shank_volume_mm3=math.pi*radius*radius*extra)


def support_stack(c,old_support,core,old_shaft,base_case,base_cover,sun_low,drum_low):
    """Fit printed thrust bearings; retain the global sun and brake datums."""
    lo,flange_end=old_support['flange_limits_y_mm']
    sleeve_end=sun_low-c['sleeve_sun_gap']
    retainer_end=drum_low-c['retainer_drum_gap'];bush_end=retainer_end-c['oil_retainer_stock']
    thrust_start=flange_end;thrust_end=thrust_start+c['thrust_width'];shim_end=thrust_end+c['shim_stock']
    bush_start=shim_end+c['bush_flange_stock']
    assert lo<flange_end<thrust_end<shim_end<bush_start<c['screw_station']<bush_end<retainer_end<sleeve_end
    sleeve=cylinder(c['thrust_seat_radius'],lo,shim_end).fuse(cylinder(c['sleeve_radius'],shim_end,sleeve_end))
    sleeve=sleeve.fuse(cylinder(c['sleeve_flange_radius'],lo,flange_end)).cut(cylinder(c['inner_bush_outer']+c['inner_bush_sleeve_gap'],lo-1,sleeve_end+1))
    inner=cylinder(c['inner_bush_outer'],lo,sleeve_end).cut(cylinder(c['inner_bush_bore'],lo-1,sleeve_end+1))
    screw_hole=Part.makeCylinder(c['screw_diameter']/2+c['fastener_radial_gap'],c['sleeve_radius']+1-c['screw_tip_radius']+c['fastener_bottom_gap'],
        App.Vector(c['screw_tip_radius']-c['fastener_bottom_gap'],c['screw_station'],0),App.Vector(1,0,0))
    sleeve=sleeve.cut(screw_hole);inner=inner.cut(screw_hole)
    screw=Part.makeCylinder(c['screw_diameter']/2,c['screw_length'],App.Vector(c['screw_tip_radius'],c['screw_station'],0),App.Vector(1,0,0))
    end=c['screw_tip_radius']+c['screw_length']
    screw=screw.cut(box(end-c['screw_slot_depth'],end+1,c['screw_station']-5,c['screw_station']+5,-c['screw_slot_width']/2,c['screw_slot_width']/2))
    outer=cylinder(c['outer_bush_radius'],bush_start,bush_end).fuse(cylinder(c['outer_bush_flange_radius'],shim_end,bush_start))
    outer=outer.cut(cylinder(c['sleeve_radius']+c['outer_bush_running_gap'],shim_end-1,bush_end+1))
    dowel_y=old_support['dowel_origin_mm'][1]
    dowel_hole=Part.makeCylinder(c['dowel_diameter']/2+c['fastener_radial_gap'],c['boss_radius']+1-c['dowel_start_radius']+c['fastener_bottom_gap'],
        App.Vector(c['dowel_start_radius']-c['fastener_bottom_gap'],dowel_y,0),App.Vector(1,0,0))
    outer=outer.cut(dowel_hole)
    retainer=cylinder(c['oil_retainer_radius'],bush_end,retainer_end).cut(cylinder(c['sleeve_radius']+c['oil_running_gap'],bush_end-1,retainer_end+1))
    shim=cylinder(c['thrust_outer_radius'],thrust_end,shim_end).cut(cylinder(c['thrust_bore_radius']+c['shim_bore_gap'],thrust_end-1,shim_end+1))
    shaft=old_shaft.copy();case=base_case.copy();cover=base_cover.copy()
    split=core['bevel_split_gap']/2;case_inner=core['bevel_half_width']-core['bevel_end_stock']
    # The earlier input boss was fused after hollowing the case, leaving its
    # inboard annular stock inside the intended cavity. Restore that same cavity
    # before adding the thrust-bearing seats; do not reduce the source-sized gears.
    cavity=outline_face(core['bevel_outline_segments'],core['bevel_cavity_scale']).extrude(App.Vector(0,2*case_inner,0))
    cavity.translate(App.Vector(0,-case_inner,0))
    inboard_boss_removed=cover.common(cavity).Volume
    cover=cover.cut(cavity)
    halves=[box(-500,-split,-500,500,-300,300),box(split,500,-500,500,-300,300)]
    for sign in [-1,1]:
        low,high=sorted([sign*(lo-c['journal_end_gap']),sign*(sleeve_end+c['journal_end_gap'])])
        shaft=shaft.fuse(cylinder(c['shaft_journal_radius'],low,high))
        boss=cylinder(c['thrust_boss_radius'],case_inner,bush_start).fuse(cylinder(c['boss_radius'],bush_start,retainer_end))
        bore=cylinder(c['outer_bush_radius'],case_inner-1,retainer_end+1)
        pockets=[cylinder(c['thrust_outer_radius']+c['thrust_case_gap'],case_inner-1,shim_end),
            cylinder(c['outer_bush_flange_radius'],case_inner-1,bush_start),cylinder(c['oil_retainer_radius'],bush_end,retainer_end+1)]
        hole=dowel_hole.copy()
        if sign<0:
            for s in [boss,bore,hole]+pockets:s.rotate(App.Vector(),App.Vector(1,0,0),180)
        case=case.fuse(boss.common(halves[0])).cut(bore)
        cover=cover.fuse(boss.common(halves[1])).cut(bore).cut(hole)
        for pocket in pockets:case=case.cut(pocket);cover=cover.cut(pocket)
    shapes=dict(sleeve=sleeve,inner_bush=inner,outer_bush=outer,retainer=retainer,screw=screw,shim=shim,shaft=shaft,case=case,cover=cover)
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1,name
    return shapes,dict(sleeve_limits_y_mm=[lo,sleeve_end],flange_limits_y_mm=[lo,flange_end],thrust_limits_y_mm=[thrust_start,thrust_end],
        shim_limits_y_mm=[thrust_end,shim_end],outer_bush_limits_y_mm=[bush_start,bush_end],outer_bush_flange_limits_y_mm=[shim_end,bush_start],
        retainer_limits_y_mm=[bush_end,retainer_end],journal_limits_y_mm=[lo-c['journal_end_gap'],sleeve_end+c['journal_end_gap']],
        sleeve_to_sun_gap_mm=c['sleeve_sun_gap'],retainer_to_drum_gap_mm=c['retainer_drum_gap'],
        inboard_input_boss_removed_mm3=inboard_boss_removed,
        input_boss_correction='Restore the original central cavity through inboard input-boss stock; external casting outline retained.')


def thrust_bearing(c,station):
    height=c['thrust_width'];center=station+height/2;pitch=c['ball_pitch_radius'];r=c['ball_radius']
    torus=Part.makeTorus(pitch,r+c['race_ball_gap'],App.Vector(0,center,0),App.Vector(0,1,0))
    races=[]
    for low,high in [(station,station+c['race_stock']),(station+height-c['race_stock'],station+height)]:
        race=cylinder(c['thrust_outer_radius'],low,high).cut(cylinder(c['thrust_bore_radius'],low-1,high+1)).cut(torus).removeSplitter();races.append(race)
    cage=cylinder(c['cage_outer_radius'],center-c['cage_stock']/2,center+c['cage_stock']/2).cut(cylinder(c['cage_inner_radius'],center-c['cage_stock'],center+c['cage_stock']))
    balls=[]
    for n in range(c['ball_count']):
        angle=2*math.pi*n/c['ball_count'];pos=App.Vector(pitch*math.cos(angle),center,pitch*math.sin(angle))
        balls.append(Part.makeSphere(r,pos))
        # Align pocket latitude circles with the cage's axial faces. The same
        # spherical material then survives STEP without a larger sewing tolerance.
        cage=cage.cut(Part.makeSphere(r+c['cage_ball_gap'],pos,App.Vector(0,1,0)))
    shapes=dict(rotating_race=races[0],stationary_race=races[1],cage=cage.removeSplitter())
    for n,ball in enumerate(balls):shapes['ball_'+str(n).zfill(2)]=ball
    for name,s in shapes.items():assert s.isValid() and len(s.Solids)==1,name
    return shapes,dict(printed_envelope_mm=[2*c['thrust_bore_radius'],2*c['thrust_outer_radius'],height],ball_count=c['ball_count'],
        ball_radius_mm=r,ball_pitch_radius_mm=pitch,assumed_internal_construction=True)


def gear_joints(c,wheel,sleeve,d):
    back=c['gear_web_front'];front=back-c['clutch_ring_stock'];end=d['flange_limits_y_mm'][1]
    ring=cylinder(c['clutch_ring_radius'],front,back).cut(cylinder(c['clutch_ring_bore'],front-1,back+1))
    dogs=[dog_sector(c['ring_dog_inner'],c['ring_dog_outer'],front-c['ring_dog_length'],front,
        c['ring_dog_phase']+n*90,c['dog_width']) for n in range(4)]
    ring=ring.multiFuse(dogs)
    rivets={};rivet_dimensions={};occurrences=[]
    for role,low,length,phase in [('short',back,c['short_rivet_length'],30),('long',front,c['long_rivet_length'],0)]:
        rivet,rd=formed_rivet(c['rivet_diameter']/2,low,end,length,c['rivet_head_height'])
        rivets[role]=rivet;rivet_dimensions[role]=rd
        for n in range(6):
            angle=math.radians(phase+60*n);location=App.Vector(c['rivet_circle']*math.cos(angle),0,c['rivet_circle']*math.sin(angle))
            hole=cylinder(c['rivet_diameter']/2+c['rivet_hole_gap'],front-1,end+1);hole.translate(location)
            wheel=wheel.cut(hole);sleeve=sleeve.cut(hole)
            if role=='long':ring=ring.cut(hole)
            else:
                recess=cylinder(rd['head_base_radius_mm']+c['rivet_head_access_gap'],front-1,back+.01);recess.translate(location);ring=ring.cut(recess)
            occurrences.append(dict(key='rivet_'+role,index=n,position_mm=[location.x,0,location.z]))
    hub=cylinder(c['clutch_hub_radius'],-c['clutch_hub_half_length'],c['clutch_hub_half_length'])
    clutch=hub.fuse(cylinder(c['clutch_disk_radius'],-c['clutch_disk_half_length'],c['clutch_disk_half_length']))
    groove=cylinder(c['clutch_disk_radius']+1,-c['clutch_groove_width']/2,c['clutch_groove_width']/2).cut(
        cylinder(c['clutch_groove_radius'],-c['clutch_groove_width'],c['clutch_groove_width']))
    clutch=clutch.cut(groove)
    # Four axial lugs provide either engagement when shifted; the standard
    # configuration is forward, i.e. the right/starboard bevel wheel (HB119).
    clutch=clutch.multiFuse([dog_sector(c['clutch_dog_inner'],c['clutch_dog_outer'],-c['clutch_dog_half_length'],c['clutch_dog_half_length'],n*90,c['dog_width']) for n in range(4)])
    clutch=clutch.cut(spline_envelope(c['clutch_spline_root'],c['clutch_spline_tip'],c['clutch_spline_width'],10,
        -c['clutch_hub_half_length']-1,c['clutch_hub_half_length']+1))
    result=dict(wheel=wheel.removeSplitter(),sleeve=sleeve.removeSplitter(),clutch_ring=ring.removeSplitter(),clutch=clutch.removeSplitter(),
        rivet_short=rivets['short'],rivet_long=rivets['long'])
    for name,s in result.items():assert s.isValid() and len(s.Solids)==1,name
    return result,dict(rivets=rivet_dimensions,rivet_occurrences=occurrences,clutch_ring_limits_y_mm=[front,back],
        ring_dog_limits_y_mm=[front-c['ring_dog_length'],front],standard_clutch_center_y_mm=c['forward_clutch_y'],
        standard_engagement='starboard/right bevel wheel, ahead motion per HB119',
        joint_assumption='Six short rivets join gear/sleeve. Six interleaved longer rivets include the quarter-inch clutch-ring flange; short heads have explicit access recesses.')
