"""Straight bevel tooth solids from a sampled spherical involute.

Local gear axis is +Y and the common pitch-cone apex is the origin. A string
unwinds along a great circle tangent to the base cone: its angular travel t
equals base-circle travel phi*sin(beta). Cubic splines approximate that curve;
ruled surfaces join two radial stations. Tooth end caps and root/tip chords
are reconstruction approximations, with no manufacturing or load claim.
"""
import math
import FreeCAD as App
import Part


def spherical_involute(theta,beta):
    if theta<=beta:return 0.0
    t=math.acos(max(-1,min(1,math.cos(theta)/math.cos(beta))))
    return t/math.sin(beta)-math.atan2(math.sin(t),math.sin(beta)*math.cos(t))


def tooth(teeth,mate,pitch_numerator,pitch_denominator,face_width,pressure,thinning,samples=64):
    pitch_radius=teeth*25.4/(2*pitch_numerator)
    mate_radius=mate*25.4/(2*pitch_numerator)
    distance=math.hypot(pitch_radius,mate_radius)
    delta=math.atan2(teeth,mate);beta=math.asin(math.sin(delta)*math.cos(math.radians(pressure)))
    addendum=25.4/pitch_denominator;dedendum=1.25*addendum
    root=delta-math.atan(dedendum/distance);tip=delta+math.atan(addendum/distance)
    half=math.pi/(2*teeth)-thinning/(2*pitch_radius)
    inv_pitch=spherical_involute(delta,beta)
    def point(theta,sign,radius):
        angle=sign*(half+inv_pitch-spherical_involute(theta,beta))
        return App.Vector(radius*math.sin(theta)*math.cos(angle),radius*math.cos(theta),radius*math.sin(theta)*math.sin(angle))
    assert 0<face_width<distance/3 and 0<root<tip<math.pi/2
    assert 0<half+inv_pitch-spherical_involute(tip,beta)<math.pi/teeth
    radii=[distance-face_width,distance];curves={};edges={};error=0
    angles=sorted(set([root+(tip-root)*n/(samples-1) for n in range(samples)]+([beta] if root<beta<tip else [])))
    for level,radius in enumerate(radii):
        for sign in [-1,1]:
            curve=Part.BSplineCurve();curve.interpolate([point(a,sign,radius) for a in angles])
            curves[level,sign]=curve;edges[level,sign]=curve.toShape()
            if level==1 and sign==1:
                for n in range(201):
                    error=max(error,edges[level,sign].distToShape(Part.Vertex(point(root+(tip-root)*n/200,sign,radius)))[0])
    faces=[]
    for level in [0,1]:faces.append(Part.makeRuledSurface(edges[level,-1],edges[level,1]))
    for sign in [-1,1]:faces.append(Part.makeRuledSurface(edges[0,sign],edges[1,sign]))
    for theta in [root,tip]:
        cross=[Part.makeLine(point(theta,-1,r),point(theta,1,r)) for r in radii]
        faces.append(Part.makeRuledSurface(*cross))
    shell=Part.makeShell(faces);solid=Part.makeSolid(shell)
    if solid.Volume<0:solid.reverse()
    assert solid.isValid() and len(solid.Solids)==1 and solid.Volume>0,'Invalid bevel tooth'
    report=dict(teeth=teeth,mating_teeth=mate,pitch_radius_mm=pitch_radius,pitch_cone_angle_deg=math.degrees(delta),
        cone_distance_mm=distance,face_width_mm=face_width,base_cone_angle_deg=math.degrees(beta),
        root_cone_angle_deg=math.degrees(root),tip_cone_angle_deg=math.degrees(tip),
        addendum_mm=addendum,dedendum_mm=dedendum,pressure_angle_deg=pressure,pitch_tooth_thinning_mm=thinning,
        root_radial_axial_outer_mm=[distance*math.sin(root),distance*math.cos(root)],
        root_radial_axial_inner_mm=[radii[0]*math.sin(root),radii[0]*math.cos(root)],
        spline_degrees=sorted({c.Degree for c in curves.values()}),max_flank_fit_error_mm=error,
        sample_angles_rad=angles,outer_positive_flank_poles_mm=[[v.x,v.y,v.z] for v in curves[1,1].getPoles()],
        limits='Spherical-involute flanks with chordal caps/roots/tips; root fillets and manufactured corrections absent.')
    return solid,report


def repeated_teeth(single,count,phase=0):
    result=[]
    for n in range(count):
        s=single.copy();s.rotate(App.Vector(),App.Vector(0,1,0),phase+n*360/count);result.append(s)
    return result
