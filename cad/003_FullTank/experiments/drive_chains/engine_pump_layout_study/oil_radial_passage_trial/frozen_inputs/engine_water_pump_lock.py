"""Source-length soft-iron drain lock wire; the formed route is an estimate.

One continuous round wire passes through a transverse plug-head hole, returns
around a neighboring cover stud, and terminates in a doubled helical tail.
The printed stock length sets the tail height, not a trimmed-away offcut.
"""
import math
import FreeCAD as App
import Part

V=App.Vector
X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)

def unit(vector):return vector/vector.Length

def rounded(points,radius):
    """Tangent lines/circular bends through a spatial polyline."""
    edges=[];last=points[0]
    for before,corner,after in zip(points,points[1:],points[2:]):
        u,v=unit(corner-before),unit(after-corner)
        angle=math.acos(max(-1.,min(1.,u.dot(v))))
        if angle<1e-8:continue
        distance=radius*math.tan(angle/2)
        assert distance<min((corner-before).Length,(after-corner).Length)*.45,(distance,points)
        a,b=corner-u*distance,corner+v*distance
        center=corner+unit(v-u)*(radius/math.cos(angle/2))
        mid=center+unit(unit(a-center)+unit(b-center))*radius
        if (a-last).Length>1e-8:edges.append(Part.makeLine(last,a))
        edges.append(Part.Arc(a,mid,b).toShape());last=b
    if (last-points[-1]).Length>1e-8:edges.append(Part.makeLine(last,points[-1]))
    return edges

def reversed_edges(edges):
    result=[]
    for edge in reversed(edges):
        item=edge.copy();item.reverse();result.append(item)
    return result

def tangent_arc(point,tangent,end):
    chord=end-point;normal=chord-tangent*chord.dot(tangent)
    if normal.Length<1e-10:return Part.makeLine(point,end)
    center=point+normal*(chord.dot(chord)/(2*normal.dot(normal)))
    mid=center+unit(unit(point-center)+unit(end-center))*(point-center).Length
    return Part.Arc(point,mid,end).toShape()

def biarc(point,tangent,end,end_tangent):
    """Two tangent circular arcs matching the endpoint positions and tangents."""
    chord=end-point;dot=chord.dot(tangent+end_tangent)
    length=chord.dot(chord)/(dot+math.sqrt(dot*dot+2*(1-tangent.dot(end_tangent))*chord.dot(chord)))
    middle=(point+end+(tangent-end_tangent)*length)/2
    one=tangent_arc(point,tangent,middle);two=tangent_arc(end,-end_tangent,middle)
    two.reverse();return [one,two]

def fitted_curve(value,tangent,start,end,spans):
    edges=[]
    for i in range(spans):
        a=start+(end-start)*i/spans;b=start+(end-start)*(i+1)/spans
        edges+=biarc(value(a),unit(tangent(a)),value(b),unit(tangent(b)))
    return Part.Wire(edges)

def fitted_helix(height,turns,radius):
    # The formed route is estimated. Eight biarc spans per turn approximate its
    # ideal helical reference; final held-out residuals are retained below.
    end=2*math.pi*turns
    return fitted_curve(lambda t:V(radius*math.cos(t),radius*math.sin(t),height*t/end),
                        lambda t:V(-radius*math.sin(t),radius*math.cos(t),height/end),0,end,int(math.ceil(turns*8)))

def round_stock(path,radius):
    """Exact cylinders and torus segments, with checked tangent end interfaces."""
    solids=[]
    for edge in path.Edges:
        curve=edge.Curve;start=edge.valueAt(edge.FirstParameter);end=edge.valueAt(edge.LastParameter)
        if isinstance(curve,Part.Line):
            delta=end-start;solid=Part.makeCylinder(radius,delta.Length,start,unit(delta))
        else:
            assert isinstance(curve,Part.Circle)
            u=unit(start-curve.Center);v=curve.Axis.cross(u)
            solid=Part.makeTorus(curve.Radius,radius,V(),Z,-180,180,math.degrees(edge.LastParameter-edge.FirstParameter))
            solid.Placement=App.Placement(curve.Center,App.Rotation(u,v,curve.Axis,'ZXY'))
        solids.append(solid)
    result=solids[0].multiFuse(solids[1:])
    assert result.isValid() and len(result.Solids)==1
    result.check(True)
    return result

def route(c,cover_centers):
    radius=c['lock_wire_diameter']/2;coil_radius=radius+c['lock_wire_pair_gap']/2
    turns=c['lock_wire_tail_turns'];front=c['body_front']
    nut_end=front+c['cover_gasket_stock']+c['cover_flange_stock']+c['cover_washer_stock']+c['cover_nut_stock']
    ay,az=cover_centers[c['lock_wire_anchor_index']-1]
    anchor=V(nut_end+radius+c['lock_wire_anchor_face_gap'],ay,az)
    plug_center=V(c['scroll_center_x'],0,c['drain_seat_z']-c['plug_gasket_stock']-c['plug_head_stock']/2)
    hole_center=plug_center+X*c['lock_wire_hole_offset_x']
    lead=c['lock_wire_hole_lead'];a=hole_center-Y*lead;b=hole_center+Y*lead
    towards_plug=unit(V(0,plug_center.y-ay,plug_center.z-az));side=X.cross(towards_plug)
    half_gap=math.radians(c['lock_wire_anchor_gap_deg']/2)
    circle_radius=c['lock_wire_anchor_radius']
    start_radius=towards_plug*math.cos(half_gap)+side*math.sin(half_gap)
    end_radius=towards_plug*math.cos(half_gap)-side*math.sin(half_gap)
    start,end=anchor+start_radius*circle_radius,anchor+end_radius*circle_radius
    start_tangent,end_tangent=X.cross(start_radius),X.cross(end_radius)
    midpoint=anchor-towards_plug*circle_radius
    anchor_arc=Part.Arc(start,midpoint,end).toShape()
    tail_base=anchor+towards_plug*c['lock_wire_joint_radius']
    tail_axis=-Y
    tail_rotation=App.Rotation(Z,tail_axis)
    base1,base2=tail_base+X*coil_radius,tail_base-X*coil_radius
    points_a=[a,V(plug_center.x+29,-lead,plug_center.z),
              start-start_tangent*c['lock_wire_anchor_lead'],start]
    # A and B are outside the head. Round their turns before the connecting bore
    # segment so the single centerline is tangent through both exits.
    def centerline(height):
        pitch=height/turns
        h1=fitted_helix(height,turns,coil_radius)
        h1.Placement=App.Placement(tail_base,tail_rotation)
        h2=fitted_helix(height,turns,coil_radius)
        h2.rotate(V(),Z,180);h2.Placement=App.Placement(tail_base,tail_rotation).multiply(h2.Placement)
        e1,e2,last=h1.Edges[0],h2.Edges[0],h2.Edges[-1]
        tangent1=e1.tangentAt(e1.FirstParameter);tangent2=e2.tangentAt(e2.FirstParameter)
        # A cubic transition preserves the loop and helix endpoint tangents.
        bridge=Part.BezierCurve();length=c['lock_wire_bridge_handle']
        bridge.setPoles([end,end+end_tangent*length,base2-tangent2*length,base2])
        fitted_bridge=fitted_curve(bridge.value,lambda t:bridge.tangent(t)[0],0,1,32)
        points_b=[b,V(plug_center.x+24,lead,plug_center.z),
                  V(anchor.x-3.5,5,plug_center.z),base1-tangent1*10,base1]
        # The bore is the middle of a single polyline, not two overlapping legs.
        main=rounded(list(reversed(points_a))+points_b,c['lock_wire_bend_radius'])
        # main runs from anchor start down through A/B to helix1 base.
        path=Part.Wire(reversed_edges(h2.Edges)+reversed_edges(fitted_bridge.Edges)+reversed_edges([anchor_arc])+main+list(h1.Edges))
        return path,dict(height=height,pitch=pitch,points_a=[list(p) for p in points_a],points_b=[list(p) for p in points_b],
                         bridge_poles=[list(p) for p in bridge.getPoles()],
                         start_point=list(last.valueAt(last.LastParameter)),start_tangent=list(-last.tangentAt(last.LastParameter)))
    low,high=2.,c['lock_wire_stock_length']/2
    lower,_=centerline(low);upper,_=centerline(high)
    assert lower.Length<c['lock_wire_stock_length']<upper.Length,(lower.Length,upper.Length)
    for _ in range(35):
        mid=(low+high)/2;path,details=centerline(mid)
        if path.Length<c['lock_wire_stock_length']:low=mid
        else:high=mid
    path,details=centerline((low+high)/2)
    details.update(centerline_length_mm=path.Length,stock_length_mm=c['lock_wire_stock_length'],wire_diameter_mm=c['lock_wire_diameter'],
        offcut_length_mm=0.,anchor_index=c['lock_wire_anchor_index'],anchor_center=list(anchor),anchor_radius_mm=circle_radius,
        plug_hole_center=list(hole_center),plug_center=list(plug_center),tail_base=list(tail_base),coil_radius_mm=coil_radius,
        tail_axis=list(tail_axis),helix_biarc_spans_per_turn=8,bridge_biarc_spans=32,
        construction='Tangent circular-arc fit to estimated helix/Bezier route; fused analytic round stock',
        route_is_estimated=True,anchor_attachment_is_estimated=True,mechanical_preload_simulated=False)
    return path,details

def drain_lock(c,cover_centers):
    path,details=route(c,cover_centers)
    wire=round_stock(path,c['lock_wire_diameter']/2)
    # Plug definition local X points outward; local Z maps to pump local X.
    drill=Part.makeCylinder(c['lock_wire_hole_radius'],40,V(c['plug_head_stock']/2,-20,c['lock_wire_hole_offset_x']),Y)
    return wire,drill,path,details
