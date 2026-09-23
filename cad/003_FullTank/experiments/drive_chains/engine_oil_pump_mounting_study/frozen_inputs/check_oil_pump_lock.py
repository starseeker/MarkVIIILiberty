"""Saved-material, stock-length and attachment witnesses for the HB87 lock."""
import math
import FreeCAD as App
import Part
import numpy as np
from scipy.spatial import cKDTree
V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)


def check_lock(doc,r,defs,shapes,passages,check):
    c,d=r['controls'],r['datums'];wd=d['relief_lock'];wire=shapes['EngineOilPump_ReliefLockWire']
    reference=doc.getObject('ReliefLockCenterline');path=reference.Shape.Wires[0]
    check('lock_reference_is_nonphysical',reference in doc.Definitions.Group and not reference.Visibility
          and 'Nonphysical' in reference.QuantityRole and len(path.Vertexes)>0)
    check('HB203_177_and_SNL160_wire_identity',doc.Def_relief_lock_wire.SourcePartMark=='177'
          and 'SNL:160:014' in doc.Def_relief_lock_wire.SourceRecords)
    check('one_relief_wire_retains_source_eight_inches',sum(x['key']=='relief_lock_wire' for x in r['occurrences'])==1
          and abs(path.Length-8*25.4)<1e-5,centerline_length_mm=path.Length)
    radius=.0475*25.4/2;radii=[];unsupported=[]
    for face in wire.Faces:
        surface=face.Surface
        if isinstance(surface,Part.Cylinder):radii.append(surface.Radius)
        elif isinstance(surface,Part.Toroid):radii.append(surface.MinorRadius)
        elif not isinstance(surface,Part.Plane):unsupported.append(type(surface).__name__)
    check('lock_round_stock_is_No18',bool(radii) and not unsupported and all(abs(x-radius)<1e-6 for x in radii),round_faces=len(radii),unsupported=unsupported)
    expected=math.pi*radius**2*8*25.4;error=abs(wire.Volume-expected)
    check('lock_stock_volume_is_preserved',error<wire.Area*wire.getTolerance(1),actual_mm3=wire.Volume,expected_mm3=expected,error_mm3=error)
    points=np.array([list(p) for p in path.discretize(Distance=.1)])
    chords=np.linalg.norm(np.diff(points,axis=0),axis=1);stations=np.concatenate(([0.],np.cumsum(chords)))
    nearby=[float(np.linalg.norm(points[i]-points[j])) for i,j in cKDTree(points).query_pairs(2.) if abs(stations[i]-stations[j])>4.]
    minimum=min(nearby);bend=min(e.Curve.Radius for e in path.Edges if isinstance(e.Curve,Part.Circle))
    check('lock_nonadjacent_strands_clear',max(chords)<=.10001 and minimum>2*radius+.1,
          samples=len(points),maximum_chord_mm=float(max(chords)),minimum_nonlocal_distance_mm=minimum,sampling_margin_mm=.1)
    check('lock_local_bends_do_not_fold',bend>2*radius,minimum_bend_radius_mm=bend)
    check('lock_material_follows_saved_centerline',all(wire.isInside(e.valueAt((e.FirstParameter+e.LastParameter)/2),1e-7,False) for e in path.Edges),segments=len(path.Edges))
    bolt='EngineOilPump_UpperJoint'+str(c['upper_wire_locked_bolt'])+'Bolt'
    for name,shape,point,span in [('cage',shapes['EngineOilPump_ReliefCage'],wd['cage_hole_center'],25.),('bolt',shapes[bolt],wd['bolt_hole_center'],8.)]:
        center=V(*point);gauge=Part.makeCylinder(radius+.01,span,center-Y*span/2,Y)
        overlap=abs(shape.common(gauge).Volume)
        centers=[center+Y*t for t in [-span*.3,0,span*.3]]
        check('lock_passes_'+name+'_hole',overlap<1e-5 and all(wire.isInside(p,1e-7,False) for p in centers),bore_material_mm3=overlap)
        support=[shape.isInside(center+V(1.1*math.cos(t),0,1.1*math.sin(t)),1e-7,False) for t in [i*math.pi/16 for i in range(32)]]
        check('lock_'+name+'_hole_retains_surrounding_stock',all(support),samples=len(support))
    # Check the entire access wells against every oil passage, not only the wire.
    bottom=c['lower_filter_top']-1;top=d['fastener_joints']['upper']['nut_bearing_z']+c['washer_stock']
    for index,(x,y) in enumerate(d['upper_bolt_centers'],1):
        tool=Part.makeCylinder(c['upper_nut_access_radius']-.001,top-bottom-.001,V(x,y,bottom),Z)
        overlap=abs(tool.common(defs['lower_body']).Volume)
        check('upper_nut_access_'+str(index),overlap<1e-5,material_mm3=overlap)
        distances={name:tool.distToShape(s)[0] for name,s in passages.items()}
        check('upper_nut_access_preserves_passage_web_'+str(index),min(distances.values())>=2.,minimum_web_mm=min(distances.values()),distances_mm=distances,required_estimated_web_mm=2.)
    outer=c['filter_outer_radius'];z=c['lower_filter_top']
    rim=Part.makeCylinder(outer,1,V(0,0,z)).cut(Part.makeCylinder(outer-c['filter_rim_width'],3,V(0,0,z-1)))
    missing=abs(rim.cut(defs['lower_body']).Volume)
    check('lock_access_retains_lower_filter_rim_seat',missing<1e-5,missing_mm3=missing)
    rotation=App.Rotation(Z,V(-1,0,0));turns=c['relief_lock_tail_turns'];end=2*math.pi*turns;fit=[]
    for phase in [0.,math.pi]:
        for i in range(math.ceil(turns*8)):
            for fraction in [.25,.5,.75]:
                t=(i+fraction)*end/math.ceil(turns*8)
                point=V(*wd['tail_base'])+rotation.multVec(V(wd['coil_radius_mm']*math.cos(t+phase),wd['coil_radius_mm']*math.sin(t+phase),wd['height_mm']*t/end))
                fit.append(Part.Vertex(point).distToShape(path)[0])
    check('lock_helix_fit_at_held_out_samples',max(fit)<.001,samples=len(fit),maximum_residual_mm=max(fit),reference_is_estimated=True)
    wire.check(True)
    check('lock_detailed_kernel_check',True)
