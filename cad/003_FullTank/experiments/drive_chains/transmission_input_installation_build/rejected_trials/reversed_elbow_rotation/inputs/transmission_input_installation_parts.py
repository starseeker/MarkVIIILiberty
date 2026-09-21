"""MX25 cover joint and a bored grease feed; nominal thread envelopes only.

Local X is the existing input-shaft axis. The grease feed lies in a plane
normal to X, at 45 degrees above port, and the elbow brings the cup upright.
Location, cup form and internal passages are reconstruction assumptions.
"""
import math
import FreeCAD as App
import Part
from transmission_input_parts import cylinder, box
from transmission_stud_parts import hex_x, split_pin


def axial(radius, start, direction, length):
    return Part.makeCylinder(radius, length, start, direction)


def mounting(c, originals):
    radius=c['stud_diameter']/2
    nut=hex_x(c['nut_af'],0,c['nut_height']-c['slot_depth']).fuse(
        cylinder(c['crown_radius'],c['nut_height']-c['slot_depth'],c['nut_height']))
    nut=nut.cut(cylinder(radius+c['nut_bore_gap'],-1,c['nut_height']+1))
    for angle in [0,60,120]:
        tool=box(c['nut_height']-c['slot_depth'],c['nut_height']+1,-20,20,
                 -(c['cotter_diameter']+c['slot_gap'])/2,(c['cotter_diameter']+c['slot_gap'])/2)
        tool.rotate(App.Vector(),App.Vector(1,0,0),angle);nut=nut.cut(tool)
    cotter,detail=split_pin(c)
    end=c['stud_start']+c['stud_length'];pin=c['nut_seat']+c['nut_height']-c['slot_depth']/2
    stud=cylinder(radius,c['stud_start'],end)
    stud=stud.cut(axial(c['cotter_diameter']/2+c['cotter_hole_gap'],App.Vector(pin,-radius-1,0),App.Vector(0,1,0),2*radius+2))
    shapes=dict(mount_stud=stud,mount_nut=nut,mount_cotter=cotter)
    tools=[];shim_tools=[];axes=[]
    for n in range(c['count']):
        angle=math.pi/2+n*2*math.pi/c['count']
        y,z=c['bolt_circle']*math.cos(angle),c['bolt_circle']*math.sin(angle);axes.append([y,z])
        cut=cylinder(radius+c['receiver_gap'],c['stud_start']-c['blind_gap'],c['nut_seat']+1)
        cut.translate(App.Vector(0,y,z));tools.append(cut)
        cut=cylinder(radius+c['receiver_gap'],-1,1);cut.translate(App.Vector(0,y,z));shim_tools.append(cut)
    for key in ['cover','housing','flange_shim']:
        shapes[key]=originals[key].cut(Part.makeCompound(shim_tools if key=='flange_shim' else tools))
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for k,s in shapes.items():assert s.isValid() and len(s.Solids)==1,k
    return shapes,dict(stud_end_mm=end,US_thread_limits_mm=[c['stud_start'],c['stud_start']+c['US_thread_length']],
        SAE_thread_limits_mm=[end-c['SAE_thread_length'],end],cotter_station_mm=pin,axes_yz_mm=axes,cotter=detail)


def elbow_path(c):
    angle=math.radians(c['angle']);r=c['bend_radius'];straight=c['center_to_face']-r*math.tan(angle/2)
    p0=App.Vector();a=App.Vector(0,0,straight)
    curve=lambda t:App.Vector(0,r*(1-math.cos(t)),straight+r*math.sin(t))
    b=curve(angle);direction=App.Vector(0,math.sin(angle),math.cos(angle));end=b+direction*straight
    path=Part.Wire([Part.makeLine(p0,a),Part.Arc(a,curve(angle/2),b).toShape(),Part.makeLine(b,end)])
    return path,end,direction


def grease_feed(c, housing, spacer):
    # Construction in local Z; rotate the inlet toward port by 45 degrees.
    path,end,direction=elbow_path(c)
    def sweep(radius):
        return path.makePipeShell([Part.Wire([Part.makeCircle(radius,App.Vector(),App.Vector(0,0,1))])],True,False)
    body=sweep(c['elbow_radius'])
    body=body.fuse(axial(c['bead_radius'],App.Vector(),App.Vector(0,0,1),c['bead_stock']))
    body=body.fuse(axial(c['bead_radius'],end-direction*c['bead_stock'],direction,c['bead_stock']))
    bore=sweep(c['pipe_bore']/2)
    socket=c['pipe_od']/2+c['socket_gap'];depth=c['socket_depth']
    bore=bore.fuse(axial(socket,App.Vector(0,0,-1),App.Vector(0,0,1),depth+1))
    bore=bore.fuse(axial(socket,end-direction*depth,direction,depth+1))
    elbow=body.cut(bore).removeSplitter()
    port=App.Vector(c['station'],0,0);inlet=App.Vector(0,math.sin(math.radians(c['inlet_angle'])),math.cos(math.radians(c['inlet_angle'])))
    bottom=port+inlet*c['nipple_start_radius'];top=bottom+inlet*c['nipple_length']
    mount=top-inlet*c['socket_depth']
    orient=App.Rotation(App.Vector(1,0,0),-c['inlet_angle'])
    placement=App.Placement(mount,orient)
    elbow.Placement=placement.multiply(elbow.Placement)
    cup_face=placement.multVec(end);cup_axis=orient.multVec(direction)
    assert (cup_axis-App.Vector(0,0,1)).Length<1e-8
    nipple=axial(c['pipe_od']/2,bottom,inlet,c['nipple_length']).cut(axial(c['pipe_bore']/2,bottom-inlet,inlet,c['nipple_length']+2))
    # The cup is one catalogue item, decomposed into an inferred hollow body
    # and screw cap. No assertion that these are original No.4 dimensions.
    stem=cup_face-cup_axis*depth
    cup=axial(c['pipe_od']/2,stem,cup_axis,depth+1)
    cup=cup.fuse(axial(c['cup_radius'],cup_face,cup_axis,c['cup_height']))
    cup=cup.cut(axial(c['flow_radius'],stem-cup_axis,cup_axis,depth+c['cup_floor']+2))
    cup=cup.cut(axial(c['cup_bore'],cup_face+cup_axis*c['cup_floor'],cup_axis,c['cup_height']))
    cap_bottom=cup_face+cup_axis*c['cap_bottom']
    cap=axial(c['cap_radius'],cap_bottom,cup_axis,c['cap_top']-c['cap_bottom'])
    cap=cap.cut(axial(c['cup_radius']+c['socket_gap'],cap_bottom-cup_axis,cup_axis,
                      c['cap_top']-c['cap_bottom']-c['cap_stock']+1))
    # Housing receiver stops at the nipple end. A smaller coaxial feed then
    # pierces the spacer into the open annular cavity between opposed cones.
    receiver=axial(socket,port+inlet*c['nipple_start_radius'],inlet,30)
    passage=axial(c['flow_radius'],port+inlet*c['passage_start_radius'],inlet,
                   c['nipple_start_radius']-c['passage_start_radius']+.1)
    revised=housing.cut(receiver).cut(passage)
    revised_spacer=spacer.cut(passage)
    shapes=dict(housing=revised,spacer=revised_spacer,nipple=nipple,elbow=elbow,cup_body=cup,cup_cap=cap)
    shapes={k:s.removeSplitter() for k,s in shapes.items()}
    for k,s in shapes.items():assert s.isValid() and len(s.Solids)==1,k
    # This witness is for visualization only. Independent validation builds
    # its own path through reopened native faces.
    witness=sweep(1);witness.Placement=placement
    return shapes,dict(port_origin_mm=list(port),inlet_direction=list(inlet),nipple_bottom_mm=list(bottom),nipple_top_mm=list(top),
        elbow_origin_mm=list(mount),elbow_local_end_mm=list(end),cup_face_mm=list(cup_face),cup_axis=list(cup_axis),
        elbow_centerline_length_mm=path.Length),dict(elbow_path_witness=witness)
