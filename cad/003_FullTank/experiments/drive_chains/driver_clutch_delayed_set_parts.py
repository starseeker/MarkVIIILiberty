"""Conditional M772 blade with a later outward set and unchanged end geometry.

The source fixes hand reach, not the transverse bend law. This construction
preserves the entire hub/bell below Z40 and the entire grip above Z600. Between
those stations, ruled sections retain the old X/Z silhouette and projected-Y
stock while delaying the outward set. This is an explicit profile hypothesis;
it is not asserted to match the schematic plan's nearly straight blade.
"""
from control_rebuild_io_v2 import App, Part

V=App.Vector


def delayed_set(original, maximum_setback=60.):
    stations=[(40.,0.),(100.,12.),(300.,58.),(360.,60.),(430.,55.),(520.,20.),(600.,0.)]
    profiles=[];records=[]
    for z,nominal in stations:
        delta=nominal*maximum_setback/60.
        plane=Part.makePlane(200,300,V(-100,-50,z))
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
