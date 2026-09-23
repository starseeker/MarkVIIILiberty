"""Liberty water pump, local X along spindle from the common bevel apex.

Analytic machining and explicit estimated casting profiles; all parts remain
separate physical definitions. The external crankcase is not modified here.
"""
import math
import FreeCAD as App
import Part
from engine_crankshaft_parts import cyl, ring, polygon
from engine_crossmember_parts import box
from transmission_core_parts import revolve
from transmission_bevel_tooth import tooth, repeated_teeth
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin

V=App.Vector
X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)

def moved(shape,position):
    result=shape.copy();result.translate(position);return result

def clean(shape):
    assert shape.isValid() and len(shape.Solids)==1
    try:
        result=shape.copy().removeSplitter()
        if result.isValid() and len(result.Solids)==1 and result.getTolerance(1)<=shape.getTolerance(1)+1e-10:
            return result
    except Part.OCCError:
        pass
    return shape

def revolvex(profile):
    shape=revolve(profile);shape.rotate(V(),Z,-90);return shape

def flange(radius,inner,a,b,pitch,ear,count,phase,hole):
    shape=ring(radius,inner,a,b);centers=[]
    for i in range(count):
        theta=math.radians(phase+i*360/count);y,z=pitch*math.cos(theta),pitch*math.sin(theta)
        shape=shape.fuse(cyl(ear,a,b,y,z));centers.append((y,z))
    if hole>0:
        for y,z in centers:shape=shape.cut(cyl(hole,a-1,b+1,y,z))
    return shape,centers

def castle(rad,af,stock,crown,depth,pind,gap):
    nut=hex_x(af,0,stock-depth).fuse(cyl(crown,stock-depth,stock))
    nut=nut.cut(cyl(rad+gap,-1,stock+1))
    for angle in [0,60,120]:
        slot=box(stock-depth,stock+1,-crown-1,crown+1,-(pind+.25)/2,(pind+.25)/2)
        slot.rotate(V(),X,angle);nut=nut.cut(slot)
    return nut

def cotter(diameter,length,crown):
    return formed_pin(dict(cotter_center_spacing=.52*diameter,cotter_diameter=diameter,
        crown_radius=crown,cotter_head_gap=.15,cotter_exit_gap=.15,
        cotter_bend_radius=.7,cotter_bend_angle=35,cotter_length=length,
        cotter_eye_radius=1.2,cotter_eye_rise=.6,cotter_eye_join_overlap=.02))

def parts(c,lower,mount_x,progress=None):
    p={};occ=[];d={};assemblies=['EngineWaterPumpShaftAssembly','EngineWaterPumpBearing','EngineWaterPumpBodyAssembly']
    def add(key,name,pos=V(),rotation=None,parent='EngineWaterPump'):
        occ.append(dict(key=key,name='EngineWaterPump_'+name,xyz=list(pos),rotation=list((rotation or App.Rotation()).Q),assembly=parent))
    def audit(key):
        assert p[key].isValid() and len(p[key].Solids)==1,(key,p[key].isValid(),len(p[key].Solids))
        p[key]=clean(p[key])
        if progress:progress(key,p[key])

    # The horizontal gear and the inherited lower vertical gear have equal21 teeth.
    n=lower['pump_mate_teeth'];one,td=tooth(n,lower['lower_teeth'],25.4/lower['module'],
        25.4/lower['module'],lower['lower_face'],lower['pressure_angle_deg'],
        lower['tooth_thinning'],lower['flank_samples'])
    ro,yo=td['root_radial_axial_outer_mm'];ri,yi=td['root_radial_axial_inner_mm'];embed=lower['root_embed']
    blank=revolve([(0,yi-embed),(ri,yi-embed),(ro,yo-embed),(ro,yo+embed),(0,yo+embed)])
    phase=-90+180/n
    gear=blank.multiFuse(repeated_teeth(one,n,phase));gear.rotate(V(),Z,-90)
    a=c['bearing_start'];b=a+c['bearing_width'];shaft_r=(c['bearing_id']-c['shaft_fit_diametral'])/2
    shaft=gear.fuse(cyl(11,yo,a)).fuse(cyl(shaft_r,a,c['shaft_taper_start']))
    shaft=shaft.fuse(Part.makeCone(shaft_r,c['shaft_taper_tip_radius'],c['shaft_taper_end']-c['shaft_taper_start'],V(c['shaft_taper_start'],0,0),X))
    shaft=shaft.fuse(cyl(c['shaft_thread_radius'],c['shaft_taper_end'],c['shaft_end']))
    def shaft_radius(x):
        return shaft_r+(c['shaft_taper_tip_radius']-shaft_r)*(x-c['shaft_taper_start'])/(c['shaft_taper_end']-c['shaft_taper_start'])
    ka,kb=c['key_start'],c['key_start']+c['key_length']
    def key(extra=0):
        lo,hi=ka-extra,kb+extra;w=c['key_width']+2*extra
        return polygon([V(lo,shaft_radius(lo)-c['key_depth']-extra,-w/2),V(hi,shaft_radius(hi)-c['key_depth']-extra,-w/2),
            V(hi,shaft_radius(hi)-c['key_depth']+c['key_height']+extra,-w/2),V(lo,shaft_radius(lo)-c['key_depth']+c['key_height']+extra,-w/2)],V(0,0,w))
    shaft=shaft.cut(key(c['thread_gap']));p['key']=key()
    nut_x=c['impeller_hub_end'];pin_x=nut_x+c['impeller_nut_stock']-c['impeller_castle_depth']/2
    shaft=shaft.cut(Part.makeCylinder(c['impeller_cotter_diameter']/2+.08,30,V(pin_x,-15,0),Y))
    p['shaft']=shaft
    p['impeller_nut']=castle(c['shaft_thread_radius'],c['impeller_nut_af'],c['impeller_nut_stock'],c['impeller_nut_crown'],c['impeller_castle_depth'],c['impeller_cotter_diameter'],c['thread_gap'])
    p['impeller_cotter'],d['impeller_cotter']=cotter(c['impeller_cotter_diameter'],c['impeller_cotter_length'],c['impeller_nut_crown'])
    for key_,name,pos in [('shaft','GearedShaft',V()),('key','ImpellerKey',V()),('impeller_nut','ImpellerNut',V(nut_x,0,0)),('impeller_cotter','ImpellerCotter',V(pin_x,0,0))]:
        add(key_,name,pos,parent='EngineWaterPumpShaftAssembly')
    audit('shaft')

    # One catalogue bearing; explicit estimated races, rolling elements and cage.
    center=(a+b)/2;ball=c['ball_radius'];pitch=c['ball_pitch_radius']
    groove=Part.makeTorus(pitch,ball+c['race_groove_allowance'],V(center,0,0),X)
    p['bearing_inner']=ring(c['inner_race_outer'],c['bearing_id']/2,a,b).cut(groove)
    p['bearing_outer']=ring(c['bearing_od']/2,c['outer_race_inner'],a,b).cut(groove)
    cage=ring(c['cage_outer'],c['cage_inner'],center-c['cage_width']/2,center+c['cage_width']/2)
    for i in range(c['ball_count']):
        theta=2*math.pi*i/c['ball_count'];pos=V(center,pitch*math.cos(theta),pitch*math.sin(theta))
        # Keep sphere poles outside the cylindrical cage stock. Axial/tangential
        # poles gave valid native pockets but invalid STEP; radial poles preserve
        # exactly the same material and pass the strict isolated round trip.
        cage=cage.cut(Part.makeSphere(ball+c['cage_ball_gap'],pos,V(0,math.cos(theta),math.sin(theta))))
        add('bearing_ball','BearingBall'+str(i+1),pos,parent='EngineWaterPumpBearing')
    p['bearing_cage']=cage;p['bearing_ball']=Part.makeSphere(ball,V(),X)
    for k in ['bearing_inner','bearing_outer','bearing_cage']:add(k,k,parent='EngineWaterPumpBearing')

    # Conical retainer and two packing boxes with tabbed sliding glands.
    first=b+c['bearing_endplay'];pack0=first+1;pack1=pack0+c['packing_length']
    gn=c['gland_nose_length'];gf=c['gland_flange_stock'];spring0=pack1+gn+gf
    spring1=spring0+c['spring_length'];pack2=spring1+gf+gn;pack3=pack2+c['packing_length']
    packing_outer=shaft_r+c['packing_rope_diameter'];sleeve_outer=c['body_shaft_sleeve_radius']
    shell=revolvex([(0,a),(c['neck_outer'],a),(c['neck_outer'],c['neck_end']),
        (c['retainer_end_radius'],mount_x),(0,mount_x)])
    shell=shell.cut(Part.makeCone(c['neck_outer']-c['retainer_wall'],c['retainer_end_radius']-c['retainer_wall'],
        mount_x-c['neck_end']+1,V(c['neck_end'],0,0),X))
    shell=shell.fuse(cyl(sleeve_outer,first,pack1+gn))
    shell=shell.cut(cyl(c['bearing_od']/2+c['thread_gap'],a-1,first))
    shell=shell.cut(cyl(shaft_r+c['rotating_gap'],a-1,mount_x+1))
    shell=shell.cut(cyl(packing_outer+c['packing_radial_gap'],pack0,pack1+gn+1))
    flange0,mount_centers=flange(c['retainer_flange_radius'],c['retainer_end_radius']-c['retainer_wall'],mount_x,mount_x+c['retainer_flange_stock'],
        c['mount_bolt_radius'],c['mount_ear_radius'],4,c['mount_angle_deg'],c['mount_hole_radius'])
    shell=shell.fuse(flange0)
    def gland_slots(shape,lo,hi):
        for angle in range(0,360,90):
            slot=box(lo,hi,packing_outer-1,c['gland_tab_radius']+c['thread_gap'],-c['gland_tab_width']/2-c['thread_gap'],c['gland_tab_width']/2+c['thread_gap'])
            slot.rotate(V(),X,angle);shape=shape.cut(slot)
        return shape
    p['retainer']=gland_slots(shell,pack1-.1,pack1+gn+gf+1)
    gland=ring(packing_outer-c['thread_gap'],shaft_r+c['rotating_gap'],0,gn)
    gland=gland.fuse(ring(c['gland_flange_radius'],shaft_r+c['rotating_gap'],gn,gn+gf))
    for angle in range(0,360,90):
        tab=box(gn,gn+gf,packing_outer-1,c['gland_tab_radius'],-c['gland_tab_width']/2,c['gland_tab_width']/2)
        tab.rotate(V(),X,angle);gland=gland.fuse(tab)
    p['gland']=gland;p['packing']=ring(packing_outer,shaft_r,0,c['packing_length'])
    add('retainer','BearingRetainer');add('packing','FrontPacking',V(pack0,0,0));add('packing','RearPacking',V(pack2,0,0))
    add('gland','FrontGland',V(pack1,0,0));add('gland','RearGland',V(pack2,0,0),App.Rotation(Z,180))
    height=c['spring_length'];wire=c['spring_wire_radius'];radius=c['spring_mean_radius'];pitch_s=(height-2*wire)/c['spring_turns']
    helix=Part.makeHelix(pitch_s,height-2*wire+pitch_s/2,radius);path=Part.Wire(helix.Edges)
    section=Part.Wire([Part.makeCircle(wire,V(radius,0,0),V(0,radius,pitch_s/(2*math.pi)))])
    spring=path.makePipeShell([section],True,True);spring.translate(V(0,0,wire-pitch_s/4))
    spring=spring.common(Part.makeCylinder(radius+wire+1,height));spring.rotate(V(),Y,90)
    p['spring']=spring;add('spring','GlandSpring',V(spring0,0,0));audit('retainer')

    # Annular centrifugal chamber and two opposite outlets. Exact scroll growth
    # is not printed; these circular cast profiles remain reconstruction estimates.
    rear=c['body_back'];front=c['body_front'];wall=c['body_wall'];cx=c['scroll_center_x']
    outer=Part.makeTorus(c['scroll_center_radius'],c['scroll_outer_radius'],V(cx,0,0),X)
    body=outer.fuse(cyl(c['chamber_radius']+wall,rear,front))
    cavity=Part.makeTorus(c['scroll_center_radius'],c['scroll_inner_radius'],V(cx,0,0),X)
    cavity=cavity.fuse(cyl(c['chamber_radius'],rear+wall,front+1))
    for sign in [-1,1]:
        start=V(cx,sign*c['outlet_start_y'],sign*c['outlet_offset_z']);direction=Y*sign;length=c['outlet_tip_y']-c['outlet_start_y']
        outlet_rotation=App.Rotation(X,c['outlet_clock_deg'])
        start=V(cx,0,0)+outlet_rotation.multVec(start-V(cx,0,0));direction=outlet_rotation.multVec(direction)
        body=body.fuse(Part.makeCylinder(c['outlet_outer_radius'],length,start,direction))
        cavity=cavity.fuse(Part.makeCylinder(c['outlet_inner_radius'],length+1,start,direction))
        for i in range(c['hose_bead_count']):
            distance=length-c['hose_bead_width']-i*c['hose_bead_spacing']
            body=body.fuse(Part.makeCylinder(c['outlet_outer_radius']+c['hose_bead_height'],c['hose_bead_width'],start+direction*distance,direction))
    body=body.cut(cavity)
    joint=mount_x+c['retainer_flange_stock'];back0=joint+c['retainer_body_gasket']
    back_flange,_=flange(c['retainer_flange_radius'],c['retainer_end_radius']-c['retainer_wall'],back0,back0+c['body_mount_flange_stock'],c['mount_bolt_radius'],c['mount_ear_radius'],4,c['mount_angle_deg'],c['mount_hole_radius'])
    back_shell=ring(c['chamber_radius']+wall,c['chamber_radius']-wall,back0,rear+wall)
    body=body.fuse(back_flange).fuse(back_shell).fuse(cyl(sleeve_outer,spring1+gf,rear+wall))
    body=body.cut(cyl(shaft_r+c['rotating_gap'],spring1-1,rear+wall+1))
    body=body.cut(cyl(packing_outer+c['packing_radial_gap'],spring1,pack3))
    body=gland_slots(body,spring1-1,pack2+.1)
    # Clear added flange stock before adding blind cover-stud receiving bosses.
    # Those bosses must retain their walls where they project into the chamber.
    body=body.cut(cavity)
    cover_face,cover_centers=flange(c['cover_flange_radius'],c['chamber_radius'],front-wall,front,c['cover_stud_radius'],c['cover_ear_radius'],8,c['cover_stud_angle_deg'],c['cover_stud_diameter']/2+c['thread_gap'])
    body=body.fuse(cover_face)
    # Studs are threaded into blind receiving holes, not fused into the casting.
    for y,z in cover_centers:
        body=body.fuse(cyl(c['cover_ear_radius'],front-c['cover_stud_embed']-2,front,y,z))
        body=body.cut(cyl(c['cover_stud_diameter']/2+c['thread_gap'],front-c['cover_stud_embed']-.1,front+1,y,z))
    plug_x=cx;plug_z=-c['scroll_center_radius']-c['scroll_outer_radius']
    # A small flat boss provides an explicit washer seat on the drain opening.
    drain_seat=c['drain_seat_z'];boss_top=plug_z+wall+1
    assert drain_seat<boss_top
    body=body.fuse(Part.makeCylinder(c['plug_head_af']/2+2,boss_top-drain_seat,V(plug_x,0,drain_seat),Z))
    bore_top=-c['scroll_center_radius']+c['scroll_inner_radius']
    body=body.cut(Part.makeCylinder(c['plug_diameter']/2+c['thread_gap'],bore_top-drain_seat+1,V(plug_x,0,drain_seat-1),Z))
    p['body']=body;add('body','BodyCasting',parent='EngineWaterPumpBodyAssembly');audit('body')
    p['joint_gasket'],_=flange(c['retainer_flange_radius'],c['retainer_end_radius']-c['retainer_wall'],0,c['retainer_body_gasket'],c['mount_bolt_radius'],c['mount_ear_radius'],4,c['mount_angle_deg'],c['mount_hole_radius'])
    p['shim'],_=flange(c['retainer_flange_radius'],c['retainer_end_radius']+c['thread_gap'],0,c['shim_stock'],c['mount_bolt_radius'],c['mount_ear_radius'],4,c['mount_angle_deg'],c['mount_hole_radius'])
    add('joint_gasket','RetainerBodyGasket',V(joint,0,0));add('shim','RetainerAdjustmentShim',V(mount_x-c['shim_stock'],0,0))
    # Four case attachment sets. Printed thread lengths constrain the estimated
    # flange stack; smooth thread envelopes still retain both axial extents.
    face=mount_x-c['shim_stock'];seat=back0+c['body_mount_flange_stock']
    nutseat=seat+c['mount_washer_stock'];pinstation=nutseat+c['mount_nut_stock']-c['mount_castle_depth']/2
    end=c['mount_stud_length']-c['mount_stud_embed']
    assert nutseat-face>=end-c['mount_stud_outer_thread']
    assert pinstation+c['mount_cotter_diameter']/2<face+end
    stud=cyl(c['mount_stud_diameter']/2,-c['mount_stud_embed'],end)
    stud=stud.cut(Part.makeCylinder(c['mount_cotter_diameter']/2+.08,24,V(pinstation-face,-12,0),Y))
    p['mount_stud']=stud
    p['mount_washer']=ring(c['mount_washer_radius'],c['mount_stud_diameter']/2+c['thread_gap'],0,c['mount_washer_stock'])
    p['mount_nut']=castle(c['mount_stud_diameter']/2,c['mount_nut_af'],c['mount_nut_stock'],c['mount_nut_crown'],c['mount_castle_depth'],c['mount_cotter_diameter'],c['thread_gap'])
    p['mount_cotter'],d['mount_cotter']=cotter(c['mount_cotter_diameter'],c['mount_cotter_length'],c['mount_nut_crown'])
    for i,(y,z) in enumerate(mount_centers,1):
        for key_,name,dx in [('mount_stud','MountStud',face),('mount_washer','MountWasher',seat),('mount_nut','MountNut',nutseat),('mount_cotter','MountCotter',pinstation)]:
            add(key_,name+str(i),V(dx,y,z))
    d['mounting']=dict(case_face_x=face,washer_seat_x=seat,nut_seat_x=nutseat,cotter_x=pinstation,
        stud_span=[face-c['mount_stud_embed'],face+end],
        inner_thread_span=[face-c['mount_stud_embed'],face],
        outer_thread_span=[face+end-c['mount_stud_outer_thread'],face+end],
        flange_stack_mm=seat-face,fully_embedded_inner_thread_is_estimate=True)
    p['plug']=cyl(c['plug_diameter']/2,-c['plug_length'],0).fuse(hex_x(c['plug_head_af'],0,c['plug_head_stock']))
    p['plug_gasket']=ring(c['plug_head_af']/2+1,c['plug_diameter']/2+c['thread_gap'],0,c['plug_gasket_stock'])
    plug_rot=App.Rotation(Y,90)
    add('plug_gasket','DrainGasket',V(plug_x,0,drain_seat),plug_rot)
    add('plug','DrainPlug',V(plug_x,0,drain_seat-c['plug_gasket_stock']),plug_rot)

    # Tapered, keyed open impeller; the source does not establish a full back disk.
    imp=cyl(c['impeller_hub_radius'],c['impeller_hub_start'],c['impeller_hub_end'])
    start=c['impeller_disk_start'];end=start+c['impeller_disk_stock']
    if c['impeller_back_shroud']:imp=imp.fuse(cyl(c['impeller_radius'],start,end))
    for i in range(c['impeller_blade_count']):
        blade=box(start,c['impeller_blade_end'],c['impeller_hub_radius']-1,c['impeller_radius'],-c['impeller_blade_stock']/2,c['impeller_blade_stock']/2)
        blade.rotate(V(),X,i*360/c['impeller_blade_count']);imp=imp.fuse(blade)
    imp=imp.cut(cyl(shaft_r+c['rotating_gap'],c['impeller_hub_start']-1,c['shaft_taper_start']))
    imp=imp.cut(Part.makeCone(shaft_r+c['rotating_gap'],c['shaft_taper_tip_radius']+c['rotating_gap'],c['shaft_taper_end']-c['shaft_taper_start'],V(c['shaft_taper_start'],0,0),X))
    imp=imp.cut(cyl(c['shaft_thread_radius']+c['rotating_gap'],c['shaft_taper_end'],c['impeller_hub_end']+1)).cut(key(c['thread_gap']))
    p['impeller']=imp;add('impeller','Impeller')

    # Cover and integral inlet: a documented spline meridian, circular elbow,
    # and open straight hose end. Mark12081 ownership still needs corroboration.
    cf=front+c['cover_gasket_stock'];ce=cf+c['cover_flange_stock'];neck=c['inlet_neck_x']
    cover,_=flange(c['cover_flange_radius'],c['chamber_radius'],cf,ce,c['cover_stud_radius'],c['cover_ear_radius'],8,c['cover_stud_angle_deg'],c['cover_stud_diameter']/2+c['thread_gap'])
    outer_profile=[(ce,65),(ce+7,62),(ce+15,52),(ce+22,35),(neck,c['inlet_od']/2)]
    inner_profile=[(ce,c['chamber_radius']),(ce+3,57),(ce+12,48),(ce+19,31),(neck,c['inlet_od']/2-c['inlet_wall'])]
    curves=[]
    for profile in [outer_profile,inner_profile]:
        curve=Part.BSplineCurve();curve.interpolate([V(x,r,0) for x,r in profile]);curves.append(curve)
    edges=[curves[0].toShape(),Part.makeLine(V(*[outer_profile[-1][0],outer_profile[-1][1],0]),V(*[inner_profile[-1][0],inner_profile[-1][1],0])),curves[1].toShape(),Part.makeLine(V(ce,inner_profile[0][1],0),V(ce,outer_profile[0][1],0))]
    cover=cover.fuse(Part.Face(Part.Wire(edges)).revolve(V(),X,360))
    bend=c['inlet_bend_radius'];start=V(neck,0,0);mid=V(neck+bend/math.sqrt(2),0,-bend+bend/math.sqrt(2));finish=V(neck+bend,0,-bend)
    path=Part.Wire([Part.Arc(start,mid,finish).toShape()])
    tubes=[]
    for radius in [c['inlet_od']/2,c['inlet_od']/2-c['inlet_wall']]:
        section=Part.Wire([Part.makeCircle(radius,start,X)])
        tubes.append(path.makePipeShell([section],True,True).fuse(Part.makeCylinder(radius,c['inlet_stub_length'],finish,-Z)))
    for i in range(c['hose_bead_count']):
        distance=c['inlet_stub_length']-c['hose_bead_width']-i*c['hose_bead_spacing']
        tubes[0]=tubes[0].fuse(Part.makeCylinder(c['inlet_od']/2+c['hose_bead_height'],c['hose_bead_width'],finish-Z*distance,-Z))
    cover=cover.fuse(tubes[0].cut(tubes[1]))
    # Machine complete washer seats where the estimated dome meets the ears.
    for y,z in cover_centers:
        cover=cover.cut(cyl(c['cover_washer_radius']+.2,ce,ce+c['washer_seat_relief_depth'],y,z))
    p['cover']=cover;add('cover','InletCover')
    p['cover_gasket'],_=flange(c['cover_flange_radius'],c['chamber_radius'],0,c['cover_gasket_stock'],c['cover_stud_radius'],c['cover_ear_radius'],8,c['cover_stud_angle_deg'],c['cover_stud_diameter']/2+c['thread_gap'])
    add('cover_gasket','CoverGasket',V(front,0,0));audit('cover')

    # Eight source-length stud sets on the cover joint.
    ns=c['cover_gasket_stock']+c['cover_flange_stock']+c['cover_washer_stock'];ps=ns+c['cover_nut_stock']-c['cover_castle_depth']/2
    stud=cyl(c['cover_stud_diameter']/2,-c['cover_stud_embed'],c['cover_stud_length']-c['cover_stud_embed'])
    stud=stud.cut(Part.makeCylinder(c['cover_cotter_diameter']/2+.08,20,V(ps,-10,0),Y));p['cover_stud']=stud
    p['cover_washer']=ring(c['cover_washer_radius'],c['cover_stud_diameter']/2+c['thread_gap'],0,c['cover_washer_stock'])
    p['cover_nut']=castle(c['cover_stud_diameter']/2,c['cover_nut_af'],c['cover_nut_stock'],c['cover_nut_crown'],c['cover_castle_depth'],c['cover_cotter_diameter'],c['thread_gap'])
    p['cover_cotter'],d['cover_cotter']=cotter(c['cover_cotter_diameter'],c['cover_cotter_length'],c['cover_nut_crown'])
    for i,(y,z) in enumerate(cover_centers,1):
        for key_,name,dx in [('cover_stud','CoverStud',0),('cover_washer','CoverWasher',ns-c['cover_washer_stock']),('cover_nut','CoverNut',ns),('cover_cotter','CoverCotter',ps)]:
            add(key_,name+str(i),V(front+dx,y,z),parent='EngineWaterPumpBodyAssembly')
    for key_ in p:audit(key_)
    d.update(teeth=td,tooth_phase_deg=phase,gear_back_x=yo+embed,bearing_span=[a,b],shaft_radius=shaft_r,
        packing_spans=[[pack0,pack1],[pack2,pack3]],spring_span=[spring0,spring1],packing_outer_radius=packing_outer,
        mount_x=mount_x,mount_centers=mount_centers,body_joint_x=joint,cover_centers=cover_centers,
        cover_joint_x=front,cover_cotter_station=front+ps,impeller_nut_x=nut_x,impeller_cotter_station=pin_x,
        cover_outer_profile=outer_profile,cover_inner_profile=inner_profile,
        cover_curve_degrees=[curve.Degree for curve in curves],spring_pitch=pitch_s,
        historical_dimensions_qualified=False,packing_count_conflict_retained=True)
    return p,occ,assemblies,d
