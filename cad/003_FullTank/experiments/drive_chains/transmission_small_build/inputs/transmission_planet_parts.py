"""Large epicyclic gears with explicit Fellows-style stub-tooth approximation.

Tooth flanks are sampled analytic involutes interpolated by cubic B-splines;
root continuations below the base circle are radial, with unmodeled root fillets.
Pressure angle and backlash are reconstruction choices, not Mark VIII dimensions.
"""
import math
import FreeCAD as App
import Part

from transmission_core_parts import cylinder,box,spline_envelope,revolve


def polar(radius,angle):
    return App.Vector(radius*math.cos(angle),0,radius*math.sin(angle))


def inv(t):
    return t-math.atan(t)


def gear_outline(teeth,pitch_radius,root_radius,tip_radius,pressure_deg,thinning,samples):
    alpha=math.radians(pressure_deg);base=pitch_radius*math.cos(alpha)
    half=math.pi/(2*teeth)-thinning/(2*pitch_radius)
    start=max(root_radius,base);t0=math.sqrt(max(0,(start/base)**2-1));t1=math.sqrt((tip_radius/base)**2-1)
    inv_pitch=math.tan(alpha)-alpha
    h=lambda t:half+inv_pitch-inv(t)
    assert h(t1)>0 and h(t0)<math.pi/teeth
    edges=[];curves=[];errors=[]
    for n in range(teeth):
        center=2*math.pi*n/teeth
        for side in [-1,1]:
            ts=[t0+(t1-t0)*k/(samples-1) for k in range(samples)]
            if side>0:ts.reverse()
            points=[polar(base*math.sqrt(1+t*t),center+side*h(t)) for t in ts]
            root=polar(root_radius,center+side*h(t0))
            if side<0 and root_radius<start-1e-8:edges.append(Part.makeLine(root,points[0]))
            curve=Part.BSplineCurve();curve.interpolate(points)
            edges.append(curve.toShape())
            if n==0:curves.append((side,curve))
            if side<0:
                edges.append(Part.Arc(points[-1],polar(tip_radius,center),polar(tip_radius,center+h(t1))).toShape())
            else:
                if root_radius<start-1e-8:edges.append(Part.makeLine(points[-1],root))
                next_angle=center+2*math.pi/teeth-h(t0)
                edges.append(Part.Arc(root,polar(root_radius,(center+h(t0)+next_angle)/2),polar(root_radius,next_angle)).toShape())
    wire=Part.Wire(edges)
    assert wire.isClosed() and wire.isValid()
    # Independent dense samples measure approximation, rather than trusting pole count.
    for side,curve in curves:
        edge=curve.toShape()
        for k in range(201):
            t=t0+(t1-t0)*k/200
            truth=polar(base*math.sqrt(1+t*t),side*h(t))
            errors.append(edge.distToShape(Part.Vertex(truth))[0])
    return Part.Face(wire),dict(teeth=teeth,pitch_radius_mm=pitch_radius,base_radius_mm=base,
        root_radius_mm=root_radius,tip_radius_mm=tip_radius,pressure_angle_deg=pressure_deg,
        pitch_tooth_thinning_mm=thinning,flank_samples=samples,max_flank_fit_error_mm=max(errors),
        spline_degrees=sorted({curve.Degree for side,curve in curves}))


def extrude(face,low,high):
    shape=face.extrude(App.Vector(0,high-low,0));shape.translate(App.Vector(0,low,0));return shape


def planet_parts(c,core,cal,dimensions):
    # All common-axis shapes use the port axial station in the centerline frame.
    rp={key:c['teeth_'+key]*25.4/(2*c['pitch_numerator']) for key in ['sun','planet','ring']}
    add=25.4/c['pitch_denominator'];ded=1.25*add
    assert abs(rp['ring']-rp['sun']-2*rp['planet'])<1e-8
    width=(c['gear_face_picks_px'][1]-c['gear_face_picks_px'][0])*cal['mm_per_pixel']
    high=dimensions['carrier_inner_y']-c['carrier_gear_gap'];low=high-width
    faces={};tooth_reports={}
    for key in ['sun','planet','ring']:
        internal=key=='ring'
        faces[key],tooth_reports[key]=gear_outline(c['teeth_'+key],rp[key],rp[key]-add if internal else rp[key]-ded,
            rp[key]+ded if internal else rp[key]+add,c['pressure_angle'],
            -c['tooth_thinning'] if internal else c['tooth_thinning'],c['flank_samples'])
    shapes={}
    for key in ['sun','planet']:shapes[key]=extrude(faces[key],low,high)
    root=core['cross_shaft_root_radius'];tip=core['cross_shaft_tip_radius'];sw=core['cross_shaft_spline_width']
    ring_center=dimensions['shaft_half_length']-c['retainer_end_margin']-c['retainer_stock']/2
    sun_end=ring_center-c['retainer_stock']/2-c['sun_retainer_gap']
    shapes['sun']=shapes['sun'].fuse(cylinder(c['sun_hub_radius'],low,sun_end))
    shapes['sun']=shapes['sun'].cut(spline_envelope(root+c['spline_radial_gap'],tip+c['spline_radial_gap'],
                         sw+2*c['spline_side_gap'],core['splines'],low-1,sun_end+1)).removeSplitter()
    shapes['planet']=shapes['planet'].cut(cylinder(c['planet_bore_radius'],low-1,high+1)).removeSplitter()
    joint=(dimensions['brake_case_inner_y']+dimensions['plain_case_outer_y'])/2
    flange_low=joint-c['ring_flange_stock']/2;flange_high=joint+c['ring_flange_stock']/2
    ring_outer=dimensions['brake_case_lip_radius']-c['ring_radial_gap']
    blank=cylinder(ring_outer,low,high).fuse(cylinder(c['ring_flange_radius'],flange_low,flange_high))
    void=extrude(faces['ring'],low-1,high+1)
    shapes['ring']=blank.cut(void).removeSplitter()
    gasket=cylinder(c['ring_flange_radius'],0,c['gasket_stock']).cut(cylinder(ring_outer, -1,c['gasket_stock']+1))
    shapes['gasket']=gasket.removeSplitter()
    retainer=cylinder(c['retainer_outer_radius'],-c['retainer_stock']/2,c['retainer_stock']/2).cut(
        cylinder(c['retainer_inner_radius'],-c['retainer_stock'],c['retainer_stock']))
    retainer=retainer.cut(box(0,c['retainer_outer_radius']+1,-c['retainer_stock'],c['retainer_stock'],
                            -c['retainer_slot']/2,c['retainer_slot']/2)).removeSplitter()
    shapes['retainer']=retainer
    washer_low=dimensions['carrier_outer_y']+c['washer_axial_gap']
    washer_high=dimensions['output_bush_inner_y']-c['washer_axial_gap']
    assert washer_high>washer_low
    shapes['washer']=cylinder(c['washer_outer_radius'],washer_low,washer_high).cut(
        cylinder(c['washer_inner_radius'],washer_low-1,washer_high+1)).removeSplitter()
    for key,shape in shapes.items():assert shape.isValid() and len(shape.Solids)==1,key
    return shapes,dict(tooth_profiles=tooth_reports,gear_band_y_mm=[low,high],gear_width_mm=width,
        planet_center_radius_mm=rp['sun']+rp['planet'],ring_outside_radius_mm=ring_outer,
        ring_flange_y_mm=[flange_low,flange_high],gasket_y_mm=[flange_low-c['gasket_stock'],flange_high],
        retainer_center_y_mm=ring_center,sun_hub_outer_y_mm=sun_end,washer_faces_y_mm=[washer_low,washer_high],
        addendum_mm=add,dedendum_mm=ded,radial_tip_clearance_mm=ded-add,low_reduction=1+rp['ring']/rp['sun'])


def case_and_shaft_receivers(old,c,d):
    lo,hi=d['ring_flange_y_mm'];r=d['ring_outside_radius_mm'];g=c['gasket_stock']
    pocket=cylinder(c['ring_flange_radius']+c['ring_radial_gap'],lo-g,hi+g).cut(cylinder(r,lo-g-1,hi+g+1))
    brake=old['brake_case'].cut(pocket).removeSplitter()
    low,high=d['gear_band_y_mm'];seat=r+c['ring_radial_gap']
    # Larger local bore accommodates the printed ring gear, with an inferred cast shoulder.
    outer=seat+c['plain_case_wall_stock'];inner_shoulder=low-c['ring_axial_gap']
    transition=inner_shoulder-c['plain_case_transition']
    band=revolve([(seat,transition),(c['plain_case_old_outer_radius'],transition),
                  (outer,inner_shoulder),(outer,lo-g),(seat,lo-g)])
    plain=old['plain_case'].fuse(band)
    plain=plain.cut(cylinder(seat,inner_shoulder,high+1)).cut(pocket).removeSplitter()
    shaft=old['cross_shaft'].copy()
    half=c['retainer_stock']/2+c['retainer_groove_gap'];center=d['retainer_center_y_mm']
    for sign in [-1,1]:
        groove=cylinder(50,sign*center-half,sign*center+half).cut(
            cylinder(c['retainer_groove_radius'],sign*center-half-1,sign*center+half+1))
        shaft=shaft.cut(groove)
    result=dict(brake_case=brake,plain_case=plain,cross_shaft=shaft.removeSplitter())
    for key,shape in result.items():assert shape.isValid() and len(shape.Solids)==1,key
    return result
