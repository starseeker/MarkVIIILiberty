"""Source-reach reverse lever; unprinted blade set and bell angle inferred."""
import math
from control_rebuild_io_v2 import App,Part
from driver_control_linkage_parts_v3 import clutch_lever
V=App.Vector

def delayed_set(original, maximum_setback=60.):
    stations=[(40.,0.),(100.,12.),(300.,58.),(360.,60.),(430.,55.),(520.,20.),(600.,0.)]
    profiles=[];records=[]
    for z,nominal in stations:
        delta=nominal*maximum_setback/60.
        plane=Part.makePlane(200,400,V(-100,-200,z))
        cut=original.section(plane)
        points=[]
        for vertex in cut.Vertexes:
            q=vertex.Point
            if not any((q-p).Length<1e-6 for p in points):points.append(q)
        assert len(points)==4,(z,len(points))
        # Each section has two points on each thickness face. Explicit winding
        # prevents topology bookkeeping from twisting a later loft section.
        points.sort(key=lambda q:(round(q.y,6),q.x))
        lower=sorted(points[:2],key=lambda q:q.x)
        upper=sorted(points[2:],key=lambda q:q.x,reverse=True)
        pp=[q-V(0,delta,0) for q in lower+upper]
        profiles.append(Part.makePolygon(pp+[pp[0]]))
        records.append(dict(z_mm=z,setback_y_mm=delta,original_points=[list(q) for q in lower+upper],points=[list(q) for q in pp]))
    blade=Part.makeLoft(profiles,True,True)
    lower=original.common(Part.makeBox(400,400,1040,V(-200,-200,-1000)))
    upper=original.common(Part.makeBox(400,400,1000,V(-200,-200,600)))
    result=lower.fuse(blade).fuse(upper)
    result=result.removeSplitter()
    assert result.isValid() and len(result.Solids)==1 and result.Solids[0].isClosed()
    return result,dict(section_records=records,maximum_setback_mm=maximum_setback,
        unchanged_below_z_mm=40.,unchanged_above_z_mm=600.,
        section_law='Ruled segments; original X/Z section vertices and projected-Y stock preserved. Transverse section translation only.',
        limit='Estimated delayed outward set differs from the schematic plan blade; full source comparison and mechanical checks required. No independent historical profile validation.')

def lever(c,bell_world_relative):
    # The common lever helper supplies complete analytic journal/grip/eye stock.
    # Choose the bell angle from the exact shared short-rod closure, independently
    # of the estimated upper hand inclination.
    hand=c['hand_elevation_degrees'];rotation=App.Rotation(V(0,1,0),90-hand)
    bell=rotation.inverted().multVec(bell_world_relative)
    included=90-math.degrees(math.atan2(bell.z,bell.x))
    controls=dict(lever_stock=c['blade_stock_mm'],lever_boss_width=c['hub_width_mm'],
        lever_included_angle_degrees=included,clutch_bell_radius=c['bell_radius_mm'],
        clutch_hand_length=c['hand_reach_mm'],lever_hand_outward_offset=-c['outward_set_mm'],
        lever_bore_diameter=38.3238)
    q,p=clutch_lever(controls);assert (p-bell).Length<1e-7
    q,profile=delayed_set(q,-c['delayed_set_mm'])
    return q,rotation,dict(canonical_bell_mm=list(bell),included_angle_degrees=included,
        source_hand_reach_mm=c['hand_reach_mm'],source_bell_radius_mm=c['bell_radius_mm'],
        blade_profile=profile,helper_controls=controls,
        interpretation='Hub-center-to-grip-extreme hand reach and hub-to-eye bell radius. These datums and unprinted blade sections, grip, outward set and included angle are interpretations, not recovered manufacturing dimensions.')
