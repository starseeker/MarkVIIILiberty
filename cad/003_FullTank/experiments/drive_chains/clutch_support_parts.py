"""Provisional physical floor attachment and connected clutch auxiliary controls."""
import math
import FreeCAD as App
import Part
from clutch_throwout_parts import cylinder, hex_nut, web_polygon
from transmission_input_installation_parts import formed_pin

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def hex_z(af, z, height):
    r = af / math.sqrt(3)
    points = [V(r*math.cos(j*math.pi/3), r*math.sin(j*math.pi/3), z) for j in range(6)]
    return Part.Face(Part.makePolygon(points+points[:1])).extrude(Z*height)


def parts(c, old_shaft, inherited, floor_top, floor_thickness):
    definitions, occurrences, mounts = {}, [], []
    def add(key, name, xyz, rotation=None, parent='ClutchSupports'):
        occurrences.append(dict(key=key, name='ClutchSupport_'+name, xyz=xyz,
                                rotation=rotation or [0, 0, 0, 1], assembly=parent))
    h = c['main_z'] - floor_top
    aux_h = h+c['aux_dz']
    width, rad = c['journal_width'], c['journal_radius']
    for side, sign, forward in [('Right', -1, 0), ('Left', 1, abs(c['aux_dx']))]:
        key = side.lower()
        xsign=-1 if side=='Left' and c['aux_dx']<0 else 1
        dy=c['aux_bracket_y']-c['bracket_y'] if forward else 0
        fh=c['foot_half_width']; rear=c['foot_rear_x']; end=c['foot_front_margin']
        xy=[(rear,-fh),(0,-fh),(forward,dy-fh),(forward+end,dy-fh),
            (forward+end,dy+fh),(forward,dy+fh),(0,fh),(rear,fh)] if forward else [(rear,-fh),(end,-fh),(end,fh),(rear,fh)]
        points=[V(xsign*x,y,0) for x,y in xy]
        base=Part.Face(Part.makePolygon(points+points[:1])).extrude(Z*c['foot_thickness'])
        journals = [(0, 0, h)] + ([(xsign*forward, dy, aux_h)] if forward else [])
        for x, y, z in journals:
            base = base.fuse(cylinder(rad, y-width/2, width, x, z))
            web=web_polygon([(x-35, 0), (x+35, 0), (x+22, z), (x-22, z)], c['web_thickness'])
            web.translate(V(0,y,0));base=base.fuse(web)
        if forward:
            wt=c['web_thickness']/2
            points=[V(0,-wt,c['foot_thickness']),V(xsign*forward,dy-wt,c['foot_thickness']),
                    V(xsign*forward,dy+wt,c['foot_thickness']),V(0,wt,c['foot_thickness'])]
            base=base.fuse(Part.Face(Part.makePolygon(points+points[:1])).extrude(Z*22))
        diameter, length = c[key+'_cap_diameter'], c[key+'_cap_length']
        holes=[]
        for x,mid_y in [(-xsign*c['bolt_x_margin'],0), (xsign*(forward+c['bolt_x_margin']),dy)]:
            for y in [mid_y-c['bolt_y'], mid_y+c['bolt_y']]:
                base=base.fuse(Part.makeCylinder(c['boss_radius'], c['boss_height'], V(x,y,0), Z))
                holes.append(Part.makeCylinder(diameter/2+c['cap_hole_clearance'],
                    length-floor_thickness+c['blind_end_gap']+1, V(x,y,-1), Z))
                center=[c['main_x']+x, sign*c['bracket_y']+y, floor_top-floor_thickness]
                n=side+'Mount%d'%(len([m for m in mounts if m['side']==side])+1)
                add(key+'_cap', n, center)
                mounts.append(dict(name='ClutchSupport_'+n, side=side, center=center,
                    diameter=diameter, length=length, head_seat_z=floor_top-floor_thickness,
                    engagement=length-floor_thickness))
        for x,y,z in journals:
            holes.append(cylinder(c['main_radius']+c['journal_clearance'], y-width/2-1, width+2, x,z))
        definitions[key+'_bracket']=base.cut(Part.makeCompound(holes)).removeSplitter()
        head_h = 8.0 if sign < 0 else 10.0
        af = 19.05 if sign < 0 else 23.8125
        definitions[key+'_cap']=Part.makeCylinder(diameter/2,length).fuse(hex_z(af,-head_h,head_h)).removeSplitter()
        add(key+'_bracket',side+'Bracket',[c['main_x'],sign*c['bracket_y'],floor_top])

    # Remove the unsupported hole without altering the rest of the inherited shaft.
    main=old_shaft.copy()
    plug=Part.makeCylinder(2.1,50,V(-25,259,0),X).common(cylinder(c['main_radius'],250,15))
    main=main.fuse(plug).removeSplitter()
    tip=c['set_screw_tip_x']; screw_r=c['set_screw_diameter']/2
    seat=Part.makeBox(40+tip, 2*(screw_r+.5), 2*(screw_r+.5),
                      V(-40,inherited['lever_y']-screw_r-.5,-screw_r-.5))
    main=main.cut(seat).removeSplitter()
    under=tip-c['set_screw_length']
    screw=Part.makeCylinder(screw_r,c['set_screw_length'],V(under,0,0),X)
    screw=screw.fuse(Part.makeBox(c['set_screw_head_height'],c['set_screw_head_width'],c['set_screw_head_width'],
        V(under-c['set_screw_head_height'],-c['set_screw_head_width']/2,-c['set_screw_head_width']/2)))
    screw=screw.cut(Part.makeCylinder(c['set_screw_cup_radius'],c['set_screw_cup_depth']+1,
        V(tip-c['set_screw_cup_depth'],0,0),X)).removeSplitter()
    definitions['cup_screw']=screw
    add('cup_screw','MainSetScrew',[c['main_x'],inherited['lever_y'],c['main_z']])

    # Source orientation: operating arm runs rearward/down toward the auxiliary
    # controls. The angle remains estimated because inherited floor height and
    # the conditional source registration disagree.
    ex,ez=c['operating_eye_x'],c['operating_eye_z'];arm_length=math.hypot(ex,ez)
    nx,nz=-ez/arm_length,ex/arm_length
    points=[(-18*nx,-18*nz),(18*nx,18*nz),(ex+10*nx,ez+10*nz),(ex-10*nx,ez-10*nz)]
    hw=inherited['lever_hub_width'];kw=inherited['key_width'];ka=inherited['key_fit_allowance']
    kz=inherited['shaft_radius']-inherited['key_depth_in_shaft']
    operating=cylinder(inherited['lever_hub_radius'],-hw/2,hw).fuse(web_polygon(points,inherited['lever_web_thickness']))
    operating=operating.fuse(cylinder(18,-inherited['lever_web_thickness']/2,inherited['lever_web_thickness'],ex,ez))
    operating=operating.cut(cylinder(inherited['shaft_bore_radius'],-hw/2-1,hw+2))
    operating=operating.cut(Part.makeBox(kw+2*ka,hw+2,kw+2*ka,V(-kw/2-ka,-hw/2-1,kz-ka)))
    operating=operating.cut(cylinder(inherited['operating_eye_bore'],-hw/2-1,hw+2,ex,ez)).removeSplitter()

    ax=c['main_x']+c['aux_dx']; az=c['main_z']+c['aux_dz']
    shaft=cylinder(c['aux_shaft_radius'],c['aux_shaft_y_min'],c['aux_shaft_y_max']-c['aux_shaft_y_min'])
    kw=inherited['key_width']; kl=inherited['key_length']; ka=inherited['key_fit_allowance']
    kz=c['aux_shaft_radius']-inherited['key_depth_in_shaft']
    taper_len=c['taper_pin_length']; big=c['taper_pin_large_diameter']/2
    small=big-taper_len/(2*c['taper_ratio'])
    pin=Part.makeCone(big,small,taper_len,V(-taper_len/2,0,c['taper_pin_z']),X)
    definitions['taper_pin']=pin
    bore=Part.makeCone(big+c['taper_bore_clearance'],small+c['taper_bore_clearance'],
                      taper_len,V(-taper_len/2,0,c['taper_pin_z']),X)
    hw=c['aux_hub_width']; eh=c['aux_eye_height']; ew=c['aux_web_width']
    lever=cylinder(c['aux_hub_radius'],-hw/2,hw)
    lever=lever.fuse(web_polygon([(-20,0),(20,0),(14,eh),(-14,eh)],ew))
    lever=lever.fuse(cylinder(c['aux_eye_radius'],-ew/2,ew,0,eh))
    lever=lever.cut(cylinder(c['aux_shaft_radius']+c['journal_clearance'],-hw/2-1,hw+2))
    lever=lever.cut(cylinder(c['fork_pin_radius']+c['fork_pin_clearance'],-ew/2-1,ew+2,0,eh))
    lever=lever.cut(Part.makeBox(kw+2*ka,hw+2,kw+2*ka,V(-kw/2-ka,-hw/2-1,kz-ka)))
    definitions['aux_lever']=lever.cut(bore).removeSplitter()
    for j,y in enumerate(c['aux_lever_ys']):
        shaft=shaft.cut(Part.makeBox(kw+2*ka,kl+2*ka,kw+2*ka,V(-kw/2-ka,y-kl/2-ka,kz-ka)))
        tool=bore.copy();tool.translate(V(0,y,0));shaft=shaft.cut(tool)
        center=[ax,y,az]
        add('aux_lever','AuxLever%d'%(j+1),center,parent='ClutchAuxiliary')
        add('existing_key','AuxKey%d'%(j+1),center,parent='ClutchAuxiliary')
        add('taper_pin','AuxTaper%d'%(j+1),center,parent='ClutchAuxiliary')
    definitions['aux_shaft']=shaft.removeSplitter()
    add('aux_shaft','AuxShaft',[ax,0,az],parent='ClutchAuxiliary')

    gap=c['fork_gap']; cheek=c['fork_cheek_thickness']; outside=gap/2+cheek
    rr=c['fork_eye_radius']; fl=c['fork_length']; socket=c['fork_socket_start']
    fork=Part.makeCylinder(c['fork_socket_radius'],fl-socket,V(socket,0,0),X)
    for sign in [-1,1]:
        start=-outside if sign<0 else gap/2
        fork=fork.fuse(cylinder(rr,start,cheek))
        fork=fork.fuse(Part.makeBox(socket+6,cheek,2*rr,V(0,start,-rr)))
    fork=fork.fuse(Part.makeBox(6,2*outside,2*rr,V(socket, -outside,-rr)))
    fork=fork.cut(cylinder(c['fork_pin_radius']+c['fork_pin_clearance'],-outside-1,2*outside+2))
    fork=fork.cut(Part.makeCylinder(c['rod_diameter']/2+.1,fl-(socket+1)+1,V(socket+1,0,0),X)).removeSplitter()
    definitions['fork']=fork
    pin=cylinder(c['fork_pin_radius'],-outside,c['fork_pin_length'])
    pin=pin.fuse(cylinder(c['fork_pin_head_radius'],-outside-c['fork_pin_head_thickness'],c['fork_pin_head_thickness']))
    pin=pin.cut(Part.makeCylinder(3.175/2+.1,22,V(-11,c['fork_pin_cotter_y'],0),X)).removeSplitter()
    definitions['fork_pin']=pin
    cotter, cotter_detail=formed_pin(dict(cotter_center_spacing=1.65,cotter_diameter=3.175,
        crown_radius=c['fork_pin_radius'],cotter_head_gap=.8,cotter_exit_gap=.8,cotter_bend_radius=2,
        cotter_bend_angle=35,cotter_length=22.225,cotter_eye_radius=3,cotter_eye_rise=2,cotter_eye_join_overlap=.03))
    cotter.rotate(V(),Z,-90)
    definitions['fork_cotter']=cotter
    nut=hex_nut(c['rod_diameter'],c['rod_nut_af'],c['rod_nut_height']);nut.rotate(V(),Z,-90)
    definitions['rod_nut']=nut
    main_eye=V(c['main_x']+c['operating_eye_x'],inherited['operating_lever_y'],c['main_z']+c['operating_eye_z'])
    aux_eye=V(ax,c['aux_lever_ys'][1],az+eh)
    rod_axis=aux_eye-main_eye
    assert abs(rod_axis.y)<1e-8 and abs(rod_axis.z)<1e-8, 'Revise rod frames for nonparallel eye heights'
    length=abs(rod_axis.x)
    main_rot=App.Rotation(Y,180) if rod_axis.x<0 else App.Rotation()
    aux_rot=App.Rotation() if rod_axis.x<0 else App.Rotation(Y,180)
    rod_start=fl-c['rod_engagement']; rod_end=length-fl+c['rod_engagement']
    assert rod_end>rod_start and length>2*(fl+c['rod_nut_height'])
    definitions['rod']=Part.makeCylinder(c['rod_diameter']/2,rod_end-rod_start,V(rod_start,0,0),X)
    add('rod','RearAuxRod',list(main_eye),list(main_rot.Q),parent='ClutchAuxiliary')
    for side,eye,rotation in [('Main',main_eye,main_rot),('Aux',aux_eye,aux_rot)]:
        for key,suffix,point in [('fork','Fork',V()),('fork_pin','ForkPin',V()),
                ('fork_cotter','ForkCotter',V(0,c['fork_pin_cotter_y'],0)),('rod_nut','RodNut',V(fl,0,0))]:
            add(key,side+suffix,list(eye+rotation.multVec(point)),list(rotation.Q),parent='ClutchAuxiliary')
    for name,shape in dict(definitions,main_shaft=main,operating_lever=operating).items():
        assert shape.isValid() and len(shape.Solids)==1,(name,len(shape.Solids))
    return definitions,occurrences,{'ClutchThrowout_Shaft':main,'ClutchThrowout_OperatingLever':operating},dict(mounts=mounts,floor_top=floor_top,floor_thickness=floor_thickness,
        main_axis=[c['main_x'],0,c['main_z']],aux_axis=[ax,0,az],rod_eyes=[list(main_eye),list(aux_eye)],
        rod_center_distance=length,cotter=cotter_detail,unsupported_main_shaft_cotter_removed=True,
        mounting_hypothesis='Underside floor screws into bracket bosses; unverified historical attachment')
