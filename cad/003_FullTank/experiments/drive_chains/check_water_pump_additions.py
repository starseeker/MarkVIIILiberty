"""Independent saved-solid witnesses for HB191 connections and SNL drain wire."""
import math
import FreeCAD as App
import Part
import numpy as np
from scipy.spatial import cKDTree

V=App.Vector;X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)

def check_additions(doc,report,part,ck):
    c,d=report['controls'],report['datums'];body,cover=part('BodyCasting'),part('InletCover')
    # Printed stock dimensions, independent of the generator's control values.
    tube_length=1.875*25.4;wall=.065*25.4
    for label,shape,outer,starts,directions in [
        ('outlet',body,1.375*25.4/2,
         [V(c['scroll_center_x'],0,0)+App.Rotation(X,c['outlet_clock_deg']).multVec(V(0,sign*(c['outlet_start_y']+c['outlet_cast_length']),sign*c['outlet_offset_z'])) for sign in [-1,1]],
         [App.Rotation(X,c['outlet_clock_deg']).multVec(Y*sign) for sign in [-1,1]]),
        ('inlet',cover,25.4,[V(c['inlet_neck_x']+c['inlet_bend_radius'],0,-c['inlet_bend_radius'])],[-Z])]:
        radii=[f.Surface.Radius for f in shape.Faces if isinstance(f.Surface,Part.Cylinder)]
        ck(label+' has printed hose-end OD and 0.065 inch wall',all(any(abs(actual-required)<1e-6 for actual in radii) for required in [outer,outer-wall]))
        for index,(start,axis) in enumerate(zip(starts,directions),1):
            inside=Part.makeCylinder(outer-wall-.001,tube_length-.002,start+axis*.001,axis)
            e1=X if abs(axis.x)<.9 else Y;e2=axis.cross(e1);mid=outer-wall/2
            witness=[shape.isInside(start+axis*station+(e1*math.cos(t)+e2*math.sin(t))*mid,1e-7,False)
                     for station in [.2,10.,25.,tube_length-.2] for t in [i*math.pi/16 for i in range(32)]]
            ck(label+' full 1-7/8 inch stock remains open '+str(index),abs(shape.common(inside).Volume)<1e-5)
            ck(label+' printed tube wall throughout stock '+str(index),all(witness),dict(samples=len(witness),failed=sum(not a for a in witness)))
    identities=[doc.getObject(report['definitions'][k]).IntegralConnectionIdentity for k in ['body','cover']]
    ck('HB191 connection identities belong to their two castings', '12075' in identities[0] and '12081' in identities[1])
    wire=part('DrainLockWire');plug=part('DrainPlug');wd=d['drain_lock']
    reference=doc.getObject(report['wire_centerline_object']);path=reference.Shape.Wires[0]
    ck('wire reference is hidden nonphysical construction geometry',reference in doc.Definitions.Group and not reference.Visibility
        and 'Nonphysical' in reference.QuantityRole and not any(row['key']=='wire_centerline' for row in report['occurrences']))
    ck('one LQ167A wire retains all ten inches of stock',sum(row['key']=='lock_wire' for row in report['occurrences'])==1 and abs(path.Length-254.)<1e-5,path.Length)
    stock_r=.0475*25.4/2;radii=[];unsupported=[]
    for f in wire.Faces:
        s=f.Surface
        if isinstance(s,Part.Cylinder):radii.append(s.Radius)
        elif isinstance(s,Part.Toroid):radii.append(s.MinorRadius)
        elif not isinstance(s,Part.Plane):unsupported.append(type(s).__name__)
    ck('every round wire surface retains No18 diameter',not unsupported and len(radii)>0 and all(abs(a-stock_r)<1e-6 for a in radii),dict(round_faces=len(radii),unsupported=unsupported))
    expected=math.pi*stock_r**2*254.;error=abs(wire.Volume-expected)
    ck('wire solid contains the source stock volume',error<wire.Area*wire.getTolerance(1),dict(actual_mm3=wire.Volume,expected_mm3=expected,error_mm3=error))
    # Check actual saved centreline, including the doubled strands. Sampling is
    # a conservative distance witness with a 0.1mm allowance for its spacing.
    pts=np.array([list(p) for p in path.discretize(Distance=.1)])
    chords=np.linalg.norm(np.diff(pts,axis=0),axis=1);stations=np.concatenate(([0.],np.cumsum(chords)))
    nearby=[float(np.linalg.norm(pts[i]-pts[j])) for i,j in cKDTree(pts).query_pairs(2.) if abs(stations[i]-stations[j])>4.]
    nearest=min(nearby)
    ck('nonadjacent wire strands remain separated',max(chords)<=.10001 and nearest>2*stock_r+.1,dict(samples=len(pts),maximum_chord_mm=float(max(chords)),minimum_nonlocal_center_distance_mm=nearest,sampling_margin_mm=.1))
    bend=min(e.Curve.Radius for e in path.Edges if isinstance(e.Curve,Part.Circle))
    ck('formed wire has no local folded tube',bend>2*stock_r,dict(minimum_bend_radius_mm=bend,wire_radius_mm=stock_r))
    center_checks=[wire.isInside(e.valueAt((e.FirstParameter+e.LastParameter)/2),1e-7,False) for e in path.Edges]
    ck('physical wire follows every saved centerline segment',all(center_checks),dict(segments=len(center_checks)))
    hole=V(*wd['plug_hole_center']);bore=Part.makeCylinder(stock_r+.01,30,hole-Y*15,Y)
    support=[plug.isInside(hole+V(1.35*math.cos(t),0,1.35*math.sin(t)),1e-7,False) for t in [i*math.pi/16 for i in range(32)]]
    ck('plug cross-hole passes the wire and retains surrounding head stock',abs(plug.common(bore).Volume)<1e-5 and all(support))
    anchor=part('CoverStud'+str(c['lock_wire_anchor_index']));nut=part('CoverNut'+str(c['lock_wire_anchor_index']))
    ck('wire loop clears the cover stud and nut',wire.distToShape(anchor)[0]>1e-5 and wire.distToShape(nut)[0]>1e-5)
    # Preserve the intended smooth reference alongside the analytic-arc fit.
    tail=V(*wd['tail_base']);axis=V(*wd['tail_axis']);rotation=App.Rotation(Z,axis);turns=c['lock_wire_tail_turns'];n=math.ceil(turns*8);end=2*math.pi*turns;fit=[]
    for phase in [0.,math.pi]:
        for i in range(n):
            for f in [.25,.5,.75]:
                t=(i+f)*end/n
                point=tail+rotation.multVec(V(wd['coil_radius_mm']*math.cos(t+phase),wd['coil_radius_mm']*math.sin(t+phase),wd['height']*t/end))
                fit.append(Part.Vertex(point).distToShape(path)[0])
    curve=Part.BezierCurve();curve.setPoles([V(*p) for p in wd['bridge_poles']])
    for i in range(32):
        for f in [.25,.5,.75]:fit.append(Part.Vertex(curve.value((i+f)/32)).distToShape(path)[0])
    ck('retained helix and Bezier reference fit within 0.001 mm at held-out samples',max(fit)<.001,dict(samples=len(fit),maximum_distance_mm=max(fit),scope='Held-out fit samples; physical route is estimated, not source-dimensioned'))
    wire.check(True)
    ck('wire passes detailed kernel Boolean geometry check',True)
