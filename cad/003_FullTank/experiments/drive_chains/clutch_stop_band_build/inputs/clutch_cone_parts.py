"""Analytic pressed cone, drilled support and separate retained spring sets.

X forward in the existing transmission frame. Small repeated hardware uses local
Z; springs and cups use local X. All receiving holes are real material removals.
"""
import math
import FreeCAD as App
import Part
from air_pressure_pump_parts import xc,cyl,box,moved
from front_clutch_parts import spring as spring_shape


def revolved(points):
    v=[App.Vector(x,r,0) for x,r in points]
    return Part.Face(Part.makePolygon(v+v[:1])).revolve(App.Vector(),App.Vector(1,0,0),360)


def ztool(points):
    """Single revolved cutter profile; no coincident shaft/head Boolean union."""
    v=[App.Vector(rad,0,z) for rad,z in points]
    return Part.Face(Part.makePolygon(v+v[:1])).revolve(App.Vector(),App.Vector(0,0,1),360)


def cap(radius,height,z=0):
    sr=(radius*radius+height*height)/(2*height)
    sphere=Part.makeSphere(sr,App.Vector(0,0,z+height-sr))
    return sphere.common(cyl(radius+.01,z,z+height))


def geometry(c,pc,tc):
    q=math.sqrt(.5);rl=c['large_diameter']/2;rs=c['small_diameter']/2
    sa=(rl-rs)/c['face_slant'];ca=math.sqrt(1-sa*sa)
    offset=c['lining_stock']+c['steel_stock']/2;b=c['bend_radius']
    rb=rs-offset*ca-b*(q+ca);xb=rb+c['web_x_intercept']
    center=(xb-b*q,rb+b*q)
    small=(center[0]+b*sa+offset*sa,rs)
    large=(small[0]-c['face_slant']*ca,rl)
    stopfront=pc['thrust_front']-tc['race_floor_depth']+tc['ball_diameter']+tc['stop_plate_stock']
    tail=stopfront+c['plunger_head_height']-c['plunger_length']
    ringfront=tail+c['ring_stock'];cupseat=c['cup_front']-c['cup_end_stock']
    return dict(sin_alpha=sa,cos_alpha=ca,half_angle_deg=math.degrees(math.asin(sa)),
                bend_center=list(center),web_tangent=[xb,rb],small_face=list(small),large_face=list(large),
                stop_front=stopfront,plunger_tail=tail,ring_front=ringfront,spring_front=cupseat,
                spring_length=cupseat-ringfront,cup_support_seat=c['cup_front']-c['cup_flange_stock'])


def build(c,pc,tc):
    d=geometry(c,pc,tc);q=math.sqrt(.5);sa=d['sin_alpha'];ca=d['cos_alpha'];b=c['bend_radius'];t=c['steel_stock']/2
    V=lambda p:App.Vector(*p,0)
    center=V(d['bend_center']);bend=V(d['web_tangent'])
    normal=App.Vector(q,-q,0);rimnormal=App.Vector(sa,ca,0)
    inner=App.Vector(c['web_inner_radius']+c['web_x_intercept'],c['web_inner_radius'],0)
    small=V(d['small_face']);large=V(d['large_face'])
    end=large-rimnormal*(c['lining_stock']+t)
    theta0=-math.pi/4;theta1=math.atan2(ca,sa)
    def arc(radius,reverse=False):
        pts=[center+App.Vector(math.cos(a),math.sin(a),0)*radius for a in [theta0,(theta0+theta1)/2,theta1]]
        if reverse:pts.reverse()
        return Part.Arc(*pts).toShape()
    a=inner+normal*t;bb=bend+normal*t
    cc=center+rimnormal*(b+t);dd=end+rimnormal*t
    ee=end-rimnormal*t;ff=center+rimnormal*(b-t);gg=bend-normal*t;hh=inner-normal*t
    edges=[Part.makeLine(a,bb),arc(b+t),Part.makeLine(cc,dd),Part.makeLine(dd,ee),
           Part.makeLine(ee,ff),arc(b-t,True),Part.makeLine(gg,hh),Part.makeLine(hh,a)]
    cone=Part.Face(Part.Wire(edges)).revolve(App.Vector(),App.Vector(1,0,0),360)
    lining=revolved([tuple(small)[:2],tuple(large)[:2],tuple(large-rimnormal*c['lining_stock'])[:2],tuple(small-rimnormal*c['lining_stock'])[:2]])
    # Retain the parent's inner running/key region, rebuilding only its outer form.
    intercept=c['web_x_intercept']-t*math.sqrt(2);width=c['support_joint_stock']*math.sqrt(2)
    ri=c['web_inner_radius'];ro=c['support_outer_radius'];seat=d['cup_support_seat']
    support=revolved([(pc['support_rear'],pc['collar_body_radius']+pc['support_running_gap']),
        (pc['support_front'],pc['collar_body_radius']+pc['support_running_gap']),
        (pc['support_front'],pc['support_radius']),(seat,pc['support_radius']),
        (seat,126),(ri+intercept,ri-1),(ri+intercept,ri),(ro+intercept,ro),
        (ro+intercept-width,ro),(ri+intercept-width,ri),
        (ri+intercept-width,pc['support_radius']),(pc['support_rear'],pc['support_radius'])])
    for n in range(pc['key_count']):
        tool=box(pc['support_rear']-1,pc['support_front']+1,0,
                 pc['key_bed_radius']+pc['key_radial_height']+pc['key_roof_gap'],
                 -pc['key_width']/2-pc['key_side_gap'],pc['key_width']/2+pc['key_side_gap'])
        tool.rotate(App.Vector(),App.Vector(1,0,0),360*n/pc['key_count']);support=support.cut(tool)
    parts={};occ=[];tools_cone=[];tools_lining=[];tools_support=[];joints=[]
    def add(name,key,point=(0,0,0),rot=None,parent='Cone'):
        rot=rot or App.Rotation()
        occ.append(dict(name='ClutchCone_'+name,key=key,xyz=list(point),rotation=list(rot.Q),parent=parent))
    def along(shape,point,direction):return moved(shape,point,App.Rotation(App.Vector(0,0,1),direction))
    # Button rivets through the actual inclined cone/support joint. Local z=0 is
    # the estimated shallow rear head seat, not an uncut nominal surface.
    grip=c['steel_stock']+c['support_joint_stock']-2*c['spotface_depth'];sr=c['support_rivet_diameter']/2
    rivet=cyl(sr,0,grip).fuse(cap(6.5,4,grip))
    tail=cap(6.5,3.2);tail.rotate(App.Vector(),App.Vector(1,0,0),180)
    rivet=rivet.fuse(tail).removeSplitter();parts['support_rivet']=rivet
    for n in range(tc['plunger_count']):
        angle=math.radians(tc['plunger_phase_deg']+n*360/tc['plunger_count'])
        radial=App.Vector(0,math.cos(angle),math.sin(angle));N=App.Vector(q,0,0)-radial*q
        r=c['support_rivet_radius'];p=App.Vector(r+c['web_x_intercept'],0,0)+radial*r
        base=p-N*(t+c['support_joint_stock']-c['spotface_depth'])
        rot=App.Rotation(App.Vector(0,0,1),N)
        add(f'SupportRivet{n+1}','support_rivet',base,rot)
        hr=6.5+c['head_seat_radial_gap'];dr=sr+c['rivet_radial_gap']
        tool=along(ztool([(0,-5),(hr,-5),(hr,0),(dr,0),(dr,grip),(hr,grip),(hr,grip+6),(0,grip+6)]),base,N)
        tools_cone.append(tool);tools_support.append(tool)
        joints.append(dict(kind='support',name=occ[-1]['name'],base=list(base),normal=list(N),grip=grip))
    # Two staggered rows give the printed total43. Their layout remains inferred.
    lr=c['lining_rivet_diameter']/2;total=c['steel_stock']+c['lining_stock']-c['spotface_depth']
    headtop=total-c['lining_head_recess'];headstart=headtop-c['lining_head_depth']
    rivet=cyl(lr,0,headstart).fuse(Part.makeCone(lr,c['lining_head_radius'],c['lining_head_depth'],App.Vector(0,0,headstart)))
    tail=cap(3.6,2.2);tail.rotate(App.Vector(),App.Vector(1,0,0),180)
    parts['lining_rivet']=rivet.fuse(tail).removeSplitter()
    number=0
    for row,(count,fraction) in enumerate(zip(c['lining_rivet_rows'],c['lining_rivet_slant_fractions'])):
        surface=small+(large-small)*fraction
        for n in range(count):
            number+=1;angle=2*math.pi*(n+row*.5)/count
            radial=App.Vector(0,math.cos(angle),math.sin(angle));N=App.Vector(sa,0,0)+radial*ca
            p=App.Vector(surface.x,0,0)+radial*surface.y
            base=p-N*(c['steel_stock']+c['lining_stock']-c['spotface_depth'])
            rot=App.Rotation(App.Vector(0,0,1),N);add(f'LiningRivet{number:02}','lining_rivet',base,rot)
            dr=lr+c['rivet_radial_gap'];tr=3.6+c['head_seat_radial_gap'];hr=c['lining_head_radius']+c['rivet_radial_gap']
            drill=ztool([(0,-4),(tr,-4),(tr,0),(dr,0),(dr,total+2),(0,total+2)])
            counter=ztool([(0,-4),(dr,-4),(dr,headstart),(hr,headtop),(hr,total+2),(0,total+2)])
            tools_cone.append(along(drill,base,N));tools_lining.append(along(counter,base,N))
            joints.append(dict(kind='lining',name=occ[-1]['name'],base=list(base),normal=list(N),head_top=headtop,surface=total))
    # One independent rear ring; smooth mating threaded envelopes at plunger tails.
    pitch=tc['plunger_pitch_radius'];pr=c['plunger_diameter']/2
    ring=xc(tc['stop_outer_radius'],d['plunger_tail'],d['ring_front']).cut(
         xc(pc['support_radius']+c['ring_bore_gap'],d['plunger_tail']-1,d['ring_front']+1))
    cup=xc(c['cup_outer_radius'],c['cup_rear'],c['cup_front'])
    cup=cup.fuse(xc(c['cup_flange_radius'],seat,c['cup_front']))
    cup=cup.cut(xc(c['cup_inner_radius'],c['cup_rear']-1,d['spring_front']))
    cup=cup.cut(xc(pr+c['cup_plunger_gap'],c['cup_rear']-1,c['cup_front']+1)).removeSplitter()
    # Shift definition to its own rear datum for reuse at six sites.
    cup.translate(App.Vector(-c['cup_rear'],0,0));parts['cup']=cup
    plunger=xc(pr,0,c['plunger_length']-c['plunger_head_height'])
    plunger=plunger.fuse(xc(c['plunger_head_radius'],c['plunger_length']-c['plunger_head_height'],c['plunger_length'])).removeSplitter()
    parts['plunger']=plunger
    sc=dict(spring_turns=c['spring_turns'],spring_end_turns=1,spring_wire_radius=c['spring_wire_radius'],
            spring_inside_radius=c['spring_outer_diameter']/2-2*c['spring_wire_radius'],
            spring_rear_seat=0,spring_length=d['spring_length'],spring_transition_turns=.5,
            spring_end_pitch=c['spring_end_pitch'],spring_end_grind_fraction=.65,spring_samples_per_turn=32)
    parts['spring'],spine,sd=spring_shape(sc);d['spring']=sd
    for n in range(tc['plunger_count']):
        angle=math.radians(tc['plunger_phase_deg']+n*360/tc['plunger_count']);y=pitch*math.cos(angle);z=pitch*math.sin(angle)
        ring=ring.cut(xc(pr,d['plunger_tail']-1,d['ring_front']+1,y,z))
        tools_support.append(xc(c['cup_outer_radius']+c['cup_support_gap'],pc['support_rear']-1,c['cup_front']+1,y,z))
        add(f'Plunger{n+1}','plunger',[d['plunger_tail'],y,z],parent='Springs')
        add(f'Cup{n+1}','cup',[c['cup_rear'],y,z],parent='Springs')
        add(f'Spring{n+1}','spring',[d['ring_front'],y,z],parent='Springs')
    # Approximate Q52A plug position with real lubrication passage and tapered seat.
    ang=math.radians(c['plug_angle_deg']);N=App.Vector(0,math.cos(ang),math.sin(ang))
    plug=Part.makeCone(c['plug_tip_radius'],c['plug_root_radius'],c['plug_length'])
    w=c['plug_head_width'];plug=plug.fuse(box(-w/2,w/2,-w/2,w/2,c['plug_length'],c['plug_length']+c['plug_head_height'])).removeSplitter()
    parts['plug']=plug;base=App.Vector(c['plug_x'],0,0)+N*(c['plug_seat_radius']-c['plug_length'])
    plug_tool=Part.makeCone(c['plug_tip_radius'],c['plug_root_radius'],c['plug_length']).fuse(
        cyl(c['plug_passage_radius'],-12,c['plug_length'])).fuse(cyl(7,c['plug_length'],c['plug_length']+12)).removeSplitter()
    tools_support.append(along(plug_tool,base,N))
    add('Plug','plug',base,App.Rotation(App.Vector(0,0,1),N))
    for name,shape in [('cone blank',cone),('lining blank',lining),('support blank',support)]:
        assert shape.isValid() and len(shape.Solids)==1,name
    blanks=dict(cone=cone.copy(),lining=lining.copy(),support=support.copy())
    parts.update(cone=cone.cut(Part.makeCompound(tools_cone)).removeSplitter(),
                 lining=lining.cut(Part.makeCompound(tools_lining)).removeSplitter(),ring=ring.removeSplitter())
    support=support.cut(Part.makeCompound(tools_support)).removeSplitter()
    for name in ['cone','lining','ring']:add(name,name,parent='Springs' if name=='ring' else 'Cone')
    for name,s in dict(parts,support=support).items():
        assert s.isValid() and len(s.Solids)==1,(name,s.isValid(),len(s.Solids))
    assert len(occ)==71
    d['rivet_joints']=joints;d['spring_controls']=sc;d['plug_base']=list(base);d['plug_axis']=list(N)
    return parts,occ,support,spine,d,blanks
