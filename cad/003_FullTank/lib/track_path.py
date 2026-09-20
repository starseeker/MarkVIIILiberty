"""Closed constant-chord track layout, with explicit source-shape residuals."""
import json
import math
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from scipy.spatial import ConvexHull


def solve(data):
    from .model import point
    values = data["values"]
    names = ["shoe_pitch","track_units_per_side","track_pin_height","track_rivet_head_height",
             "track_rivet_head_diameter","track_rivet_x","vehicle_length","vehicle_height","track_path_rounding_radius",
             "track_upper_clearance_lift","track_upper_clearance_center_x","track_upper_clearance_sigma"]
    signature = (tuple(values[k].value for k in names),json.dumps(data["calibrations"]["snl_2"],sort_keys=True))
    cached = data.get("_track_path_cache")
    if cached and cached[0] == signature:
        return cached[1]
    pitch = values["shoe_pitch"].value
    count = int(values["track_units_per_side"].value)
    pin_height = values["track_pin_height"].value
    tail_height = values["track_rivet_head_height"].value
    outer = np.array([point(data,"snl_2",p) for p in data["calibrations"]["snl_2"]["profiles"]["track"]])
    # Round the convex source envelope through inward half-plane offsets and
    # a circular sweep. Unlike an interpolating spline through sparse corners,
    # this cannot introduce tight spurious kinks at the idler nose.
    outer = outer[ConvexHull(outer).vertices]
    rounding = values["track_path_rounding_radius"].value
    offset = rounding+pin_height+tail_height
    inner = outer.copy()
    for a,b in zip(outer,np.roll(outer,-1,axis=0)):
        tangent = (b-a)/np.linalg.norm(b-a)
        normal = np.array([-tangent[1],tangent[0]])
        clipped = []
        for c,d in zip(inner,np.roll(inner,-1,axis=0)):
            fc,fd = np.dot(normal,c-a)-offset,np.dot(normal,d-a)-offset
            if fc >= -1e-8:
                clipped.append(c)
            if (fc>0) != (fd>0):
                clipped.append(c+(d-c)*fc/(fc-fd))
        inner = np.array(clipped)
        if len(inner)<3:
            raise ValueError("Track-envelope offset has collapsed")
    points = []
    for index,b in enumerate(inner):
        incoming = b-inner[index-1]
        incoming /= np.linalg.norm(incoming)
        following = inner[(index+1)%len(inner)]
        outgoing = following-b
        outgoing /= np.linalg.norm(outgoing)
        n0,n1 = np.array([incoming[1],-incoming[0]]),np.array([outgoing[1],-outgoing[0]])
        a0 = math.atan2(n0[1],n0[0])
        sweep = (math.atan2(n1[1],n1[0])-a0)%(2*math.pi)
        for angle in np.linspace(a0,a0+sweep,max(2,math.ceil(sweep*rounding/35)),endpoint=False):
            points.append(b+rounding*np.array([math.cos(angle),math.sin(angle)]))
        start,end = b+rounding*n1,following+rounding*n1
        for fraction in np.linspace(0,1,max(2,math.ceil(np.linalg.norm(end-start)/35)),endpoint=False):
            points.append(start+fraction*(end-start))
    shifted = np.array(points)
    lengths = np.linalg.norm(np.roll(shifted,-1,axis=0)-shifted,axis=1)
    knots = np.r_[0,np.cumsum(lengths)]
    knots /= knots[-1]
    curve = CubicSpline(knots,np.vstack([shifted,shifted[0]]),bc_type="periodic")
    # Start near the center of the straight lower run.
    phase = float(knots[np.argmin((shifted[:,1]-min(shifted[:,1]))*100+abs(shifted[:,0]-4000))])
    center = np.mean(outer,axis=0)
    clearance_lift=values["track_upper_clearance_lift"].value
    clearance_center=values["track_upper_clearance_center_x"].value
    clearance_sigma=values["track_upper_clearance_sigma"].value
    def corrected(t):
        p=np.array(curve(np.asarray(t)%1),copy=True)
        # Activate smoothly only on the upper run; the lower contact segment
        # remains unchanged before global chord closure/ground registration.
        upper=np.clip((p[...,1]-800)/700,0,1)
        upper=upper*upper*(3-2*upper)
        p[...,1] += clearance_lift*np.exp(-.5*((p[...,0]-clearance_center)/clearance_sigma)**2)*upper
        return p
    def location(t,scale):
        return center+scale*(corrected(t)-center)
    def march(scale):
        ts = [phase]
        for _ in range(count):
            t0 = ts[-1]
            start = location(t0,scale)
            def residual(t):
                return np.linalg.norm(location(t,scale)-start)-pitch
            hi = t0+1/count
            while residual(hi) < 0:
                hi += 0.25/count
                if hi-t0 > 0.1:
                    raise ValueError("Track curve cannot advance by one printed pitch")
            ts.append(brentq(residual,t0,hi,xtol=1e-14))
        return np.array(ts)
    scale = brentq(lambda s:march(s)[-1]-phase-1,0.9,1.15,xtol=1e-12)
    parameters = march(scale)[:-1]
    pins = location(parameters,scale)
    delta = np.roll(pins,-1,axis=0)-pins
    unit_tangents = delta/pitch
    unit_normals = np.column_stack((-unit_tangents[:,1],unit_tangents[:,0]))
    origins = (pins+np.roll(pins,-1,axis=0))/2-pin_height*unit_normals
    # Exact underside spherical-button contact near the lower run.
    a = values["track_rivet_head_diameter"].value/2
    radius = (a*a+tail_height*tail_height)/(2*tail_height)
    lower = origins[:,1]-abs(values["track_rivet_x"].value*unit_tangents[:,1])+(radius-tail_height)*unit_normals[:,1]-radius
    bottom = (unit_normals[:,1]>0.9)
    lift = -float(min(lower[bottom]))
    pins[:,1] += lift
    origins[:,1] += lift
    angles = np.arctan2(unit_tangents[:,1],unit_tangents[:,0])
    bends = (np.roll(angles,-1)-angles+math.pi)%(2*math.pi)-math.pi
    reference = curve(parameters%1)
    residuals = np.linalg.norm(pins-reference,axis=1)
    result = {"pins":pins.tolist(),"origins":origins.tolist(),"angles_deg":np.degrees(angles).tolist(),
              "joint_bends_deg":np.degrees(bends).tolist(),"pitch_mm":pitch,"units":count,
              "upper_clearance_correction":{"peak_before_scale_mm":clearance_lift,"center_x_mm":clearance_center,"sigma_mm":clearance_sigma,
                                            "basis":"Bounded correction following physical hull/track interference, not a refit of image calibration."},
              "source_curve_scale":float(scale),"source_rounding_radius_mm":rounding,"ground_translation_mm":lift,
              "pin_path_residual_rms_mm":float(np.sqrt(np.mean(residuals**2))),
              "pin_path_residual_max_mm":float(max(residuals)),
              "max_pitch_error_mm":float(max(abs(np.linalg.norm(delta,axis=1)-pitch))),
              "min_bend_deg":float(min(np.degrees(bends))),"max_bend_deg":float(max(np.degrees(bends))),
              "closed":True,"wheel_contact_qualified":False,
              "interpretation":"Printed count and pitch govern closure. A documented smooth upper-run clearance correction precedes the recorded uniform closure scale; source image calibration is unchanged. Residuals still compare pins with the uncorrected rounded/inset source construction. Wheel engagement and support-contact residuals remain open."}
    data["_track_path_cache"] = (signature,result)
    return result
