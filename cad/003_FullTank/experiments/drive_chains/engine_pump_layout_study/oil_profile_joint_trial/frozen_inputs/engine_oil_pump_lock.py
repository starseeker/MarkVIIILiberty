"""HB87 relief-cage lock wire: source attachment, estimated formed route.

One continuous No18 wire passes once through each transverse hole. Its source
8-inch stock length determines the doubled tail; the route is not a source
measurement or a mechanical preload simulation.
"""
import math
import FreeCAD as App
import Part
from engine_water_pump_lock import rounded,reversed_edges,fitted_helix,round_stock
V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)


def route(c,d):
    radius=c['relief_lock_wire_diameter']/2
    coil=radius+c['relief_lock_pair_gap']/2
    turns=c['relief_lock_tail_turns'];joint=d['fastener_joints']['upper']
    bx,by=joint['centers'][c['upper_wire_locked_bolt']-1]
    bz=joint['head_bearing_z']-joint['cotter_station_from_head_mm']
    cage=V(c['relief_x']+c['relief_lock_cage_hole_x'],c['relief_y'],d['relief_cage_span'][0]+c['relief_cage_floor_stock']/2)
    base=V(bx+6,by+9,cage.z-9)
    rotation=App.Rotation(Z,V(-1,0,0))
    def centerline(height):
        h1=fitted_helix(height,turns,coil);h1.Placement=App.Placement(base,rotation)
        h2=fitted_helix(height,turns,coil);h2.rotate(V(),Z,180);h2.Placement=App.Placement(base,rotation).multiply(h2.Placement)
        e1,e2=h1.Edges[0],h2.Edges[0]
        b1,b2=e1.valueAt(e1.FirstParameter),e2.valueAt(e2.FirstParameter)
        t1,t2=e1.tangentAt(e1.FirstParameter),e2.tangentAt(e2.FirstParameter)
        points=[b1,b1-t1*6,V(bx,by-7,-36),
                V(bx,by-7,bz),V(bx,by+7,bz),V(bx,by+7,-36),
                cage-Y*16,cage+Y*16,V(bx+11,cage.y+16,cage.z-6),
                b2-t2*6,b2]
        main=rounded(points,c['relief_lock_bend_radius'])
        path=Part.Wire(reversed_edges(h1.Edges)+main+list(h2.Edges))
        return path,dict(height_mm=height,pitch_mm=height/turns,route_points=[list(v) for v in points])
    low,high=2.,70.;a,_=centerline(low);b,_=centerline(high)
    length=c['relief_lock_stock_length']
    assert a.Length<length<b.Length,(a.Length,length,b.Length)
    for _ in range(35):
        mid=(low+high)/2;path,details=centerline(mid)
        if path.Length<length:low=mid
        else:high=mid
    path,details=centerline((low+high)/2)
    details.update(centerline_length_mm=path.Length,stock_length_mm=length,
        wire_diameter_mm=2*radius,offcut_length_mm=0.,coil_radius_mm=coil,
        bolt_hole_center=[bx,by,bz],cage_hole_center=list(cage),tail_base=list(base),
        source_attachment='HB87(f): cage to the upper-body bolt left without cotter',
        route_is_estimated=True,mechanical_preload_simulated=False)
    return path,details


def extend(c,p,occ,groups,d):
    path,details=route(c,d)
    p['relief_lock_wire']=round_stock(path,c['relief_lock_wire_diameter']/2)
    center=V(*details['cage_hole_center'])-V(c['relief_x'],c['relief_y'],0)
    drill=Part.makeCylinder(c['relief_lock_hole_radius'],40,center-Y*20,Y)
    p['relief_cage']=p['relief_cage'].cut(drill)
    # LIB34 and HB87 require underside access to the body-bolt nuts and lock.
    # These wells preserve the bearing planes and the lower-strainer rim seat.
    lower=c['lower_filter_top']-1
    upper=d['fastener_joints']['upper']['nut_bearing_z']+c['washer_stock']
    for x,y in d['upper_bolt_centers']:
        tool=Part.makeCylinder(c['upper_nut_access_radius'],upper-lower,V(x,y,lower),Z)
        p['lower_body']=p['lower_body'].cut(tool)
    occ.append(dict(key='relief_lock_wire',name='EngineOilPump_ReliefLockWire',
        xyz=[0,0,0],rotation=list(App.Rotation().Q),assembly='EngineOilPumpRelief'))
    d['relief_lock']=details
    d['missing']=['Two remaining source lock wires and mounting gasket/fasteners',
        'Case receiving revision and standard-context qualification',
        'External connection configuration reconciliation']
