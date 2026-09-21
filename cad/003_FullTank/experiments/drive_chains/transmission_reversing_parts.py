"""M301 fork, M302 rod and M307–M309 detent in the standard forward setting.

The fork outline is a fitted cubic B-spline/arc reconstruction. Dimensions are
explicit hypotheses except the catalogue spring envelope and split-pin size.
"""
import math
import FreeCAD as App
import Part
from transmission_core_parts import cylinder
from transmission_stud_parts import hex_x
from transmission_input_installation_parts import formed_pin


def tube_y(radius,lo,hi,x=0,z=0):
    return Part.makeCylinder(radius,hi-lo,App.Vector(x,lo,z),App.Vector(0,1,0))


def zc(radius,lo,hi,x,y):
    return Part.makeCylinder(radius,hi-lo,App.Vector(x,y,lo))


def band(inner,outer,half_width,angle):
    def v(r,a):return App.Vector(r*math.cos(math.radians(a)),-half_width,r*math.sin(math.radians(a)))
    edges=[Part.Arc(v(outer,angle),v(outer,180),v(outer,360-angle)).toShape(),
        Part.makeLine(v(outer,360-angle),v(inner,360-angle)),
        Part.Arc(v(inner,360-angle),v(inner,180),v(inner,angle)).toShape(),
        Part.makeLine(v(inner,angle),v(outer,angle))]
    return Part.Face(Part.Wire(edges)).extrude(App.Vector(0,2*half_width,0))


def reversing_parts(c,old_case,old_clutch,old_ring):
    x,z=c['rod_axis_xz'];fy=c['forward_y'];lo=fy-c['fork_hub_length']/2;hi=fy+c['fork_hub_length']/2
    # Finish the groove AFTER the dogs. The parent lugs bridge its outer edge.
    groove=tube_y(c['groove_tool_radius'],-c['groove_width']/2,c['groove_width']/2).cut(tube_y(c['groove_radius'],-10,10))
    clutch=old_clutch.cut(groove).removeSplitter()
    # The paired ring dogs must end before the fork's swept annulus. Shorten
    # their inferred free tips symmetrically, retaining the driving flank band.
    ring=old_ring.cut(tube_y(c['groove_tool_radius'],0,c['ring_dog_tip_y'])).removeSplitter()
    fork=band(c['groove_radius']+c['fork_radial_gap'],c['fork_outer_radius'],c['fork_width']/2,c['fork_open_half_angle'])
    # Two cubic curves interpolate the visible arm edges in the X/Z plane.
    # The end faces and hub remain analytic; no polygonal mesh substitution.
    y=-c['fork_width']/2
    a=c['arm_upper_xz']+[[x,z+19]]
    b=[[x-18,z-13]]+c['arm_lower_xz']
    curves=[]
    for pts in [a,b]:
        curve=Part.BSplineCurve();curve.interpolate([App.Vector(px,y,pz) for px,pz in pts]);curves.append(curve.toShape())
    wire=Part.Wire([curves[0],Part.makeLine(curves[0].Vertexes[-1].Point,curves[1].Vertexes[0].Point),curves[1],
        Part.makeLine(curves[1].Vertexes[-1].Point,curves[0].Vertexes[0].Point)])
    arm=Part.Face(wire).extrude(App.Vector(0,c['fork_width'],0))
    thick=Part.Face(wire).extrude(App.Vector(0,c['arm_width'],0));thick.translate(App.Vector(0,-(c['arm_width']-c['fork_width'])/2,0))
    thick=thick.cut(tube_y(c['arm_root_clear_radius'],-30,30))
    fork=fork.fuse(arm).fuse(thick).cut(tube_y(c['groove_radius']+c['fork_radial_gap'],-30,30))
    fork.translate(App.Vector(0,fy,0))
    hub=tube_y(c['hub_radius'],lo,hi,x,z)
    fork=fork.fuse(hub).cut(tube_y(c['rod_tip_radius']+c['bore_gap'],lo-1,hi+1,x,z))
    tip=hi+c['nut_height']+c['tip_projection'];pin_y=hi+c['nut_height']-c['nut_slot_depth']/2
    rod=tube_y(c['rod_radius'],c['rod_start_y'],lo,x,z).fuse(tube_y(c['rod_tip_radius'],lo,tip,x,z))
    cross=Part.makeCylinder(c['cotter_diameter']/2+c['cotter_hole_gap'],40,App.Vector(x-20,pin_y,z),App.Vector(1,0,0))
    rod=rod.cut(cross)
    rod=rod.cut(zc(c['lever_pin_hole_radius'],z-25,z+25,x,c['lever_pin_y']))
    # Three detent pockets correspond to ahead, neutral and reverse. Only the
    # ahead assembly is built here; the other service poses are not qualified.
    nose_center=z+c['rod_radius']-c['detent_depth']+c['nose_radius']
    for dy in [0,-c['shift_step'],-2*c['shift_step']]:
        rod=rod.cut(Part.makeSphere(c['nose_radius']+c['detent_gap'],App.Vector(x,c['detent_y']+dy,nose_center+c['detent_gap'])))
    pin,detail=formed_pin(dict(cotter_diameter=c['cotter_diameter'],cotter_center_spacing=c['cotter_diameter']/3,
        cotter_length=c['cotter_length'],crown_radius=c['nut_crown_radius'],cotter_head_gap=1,cotter_exit_gap=1.5,
        cotter_bend_radius=4,cotter_bend_angle=90,cotter_eye_radius=3.5,cotter_eye_rise=2,cotter_eye_join_overlap=.35))
    pin.rotate(App.Vector(),App.Vector(0,0,1),90);pin.translate(App.Vector(x,pin_y,z))
    cy=c['detent_y'];seat=c['spring_seat_z'];top=seat+c['spring_installed_height'];guide=c['plunger_shoulder_z']
    plunger=Part.makeSphere(c['nose_radius'],App.Vector(x,cy,nose_center)).fuse(zc(c['nose_radius'],nose_center,guide,x,cy)).fuse(zc(c['plunger_radius'],guide,seat,x,cy))
    wire_r=c['spring_wire_diameter']/2;mean=(c['spring_od']-c['spring_wire_diameter'])/2
    rise=c['spring_installed_height']-2*wire_r;pitch=rise/c['spring_turns']
    helix=Part.makeHelix(pitch,rise+pitch/2,mean);path=Part.Wire(helix.Edges)
    start=App.Vector(mean,0,0);tangent=App.Vector(0,mean,pitch/(2*math.pi))
    section=Part.Wire([Part.makeCircle(wire_r,start,tangent)])
    spring=path.makePipeShell([section],True,True);spring.translate(App.Vector(x,cy,seat+wire_r-pitch/4))
    # Square-ground ends define the installed envelope without invented end caps.
    spring=spring.common(zc(c['spring_od'],seat,top,x,cy))
    cap=zc(c['cap_thread_radius'],c['cap_bottom_z'],c['cap_seat_z'],x,cy)
    head=hex_x(c['cap_af'],0,c['cap_height']);head.rotate(App.Vector(),App.Vector(0,1,0),-90);head.translate(App.Vector(x,cy,c['cap_seat_z']))
    cap=cap.fuse(head).cut(zc(c['spring_bore_radius'],c['cap_bottom_z']-1,top,x,cy))
    boss=tube_y(c['rod_boss_radius'],c['rod_boss_y'][0],c['rod_boss_y'][1],x,z)
    tower=zc(c['detent_boss_radius'],z,c['cap_seat_z'],x,cy)
    case=old_case.fuse(boss).fuse(tower)
    bore=tube_y(c['rod_radius']+c['bore_gap'],c['rod_start_y']-1,lo,x,z)
    detent=zc(c['nose_radius']+c['bore_gap'],z,guide,x,cy).fuse(zc(c['spring_bore_radius'],guide,c['cap_seat_z']+1,x,cy))
    detent=detent.fuse(zc(c['cap_thread_radius']+c['bore_gap'],c['cap_bottom_z'],c['cap_seat_z']+1,x,cy))
    case=case.cut(bore.fuse(detent))
    case=case.cut(tube_y(c['hub_relief_radius'],lo-c['hub_relief_axial_gap'],tip+c['hub_relief_axial_gap'],x,z))
    case=case.cut(zc(c['cap_spotface_radius'],c['cap_seat_z'],c['cap_seat_z']+25,x,cy))
    shapes=dict(fork=fork,rod=rod,cotter=pin,plunger=plunger,spring=spring,cap=cap,case=case,clutch=clutch,clutch_ring=ring)
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for key,s in shapes.items():assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
    return shapes,dict(fork_hub_limits_y_mm=[lo,hi],nut_seat_y_mm=hi,cotter_axis_y_mm=pin_y,rod_tip_y_mm=tip,
        detent_centers_y_mm=[cy,cy-c['shift_step'],cy-2*c['shift_step']],nose_center_z_mm=nose_center,
        spring_seats_z_mm=[seat,top],spring_pitch_mm=pitch,cotter=detail,
        removed_clutch_mm3=old_clutch.cut(clutch).Volume,removed_ring_mm3=old_ring.cut(ring).Volume,
        added_case_mm3=case.cut(old_case).Volume,removed_case_mm3=old_case.cut(case).Volume)
