"""Analytic trimmed curved-face controls for the independent mass integrator."""
import argparse,math
from pathlib import Path
from control_rebuild_io_v2 import *
from control_rebuild_surface_mass_v6 import TrimmedSurfaceMassV6
V=App.Vector;Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(exist_ok=False,parents=True)
mass=TrimmedSurfaceMassV6(out/'runtime');checks=[];fixtures=[]
fixtures.append(('box',Part.makeBox(10,20,30),6000,V(5,10,15)))
fixtures.append(('annular_tube',Part.makeCylinder(5,20).cut(Part.makeCylinder(2,22,V(0,0,-1))),math.pi*21*20,V(0,0,10)))
for hollow in [False,True]:
    cylinder=Part.makeCylinder(5,20,V(0,0,-10))
    if hollow:cylinder=cylinder.cut(Part.makeCylinder(2,22,V(0,0,-11)))
    alpha=.35;level=.7;normal=V(-alpha,0,1);normal.normalize()
    cutter=Part.makeBox(100,100,100,V(-50,-50,0));cutter.Placement=App.Placement(V(0,0,level),App.Rotation(Z,normal))
    shape=cylinder.cut(cutter)
    area=math.pi*(25-(4 if hollow else 0));ex2=(25+(4 if hollow else 0))/4;height=10+level
    center=V(alpha*ex2/height,0,(alpha**2*ex2+level**2-100)/(2*height))
    fixtures.append(('oblique_'+('annulus' if hollow else 'cylinder'),shape,area*height,center))
for level in [0.,1.]:
    radius=5.;height=radius-level
    cap=Part.makeSphere(radius).common(Part.makeBox(20,20,20,V(-10,-10,level)))
    volume=math.pi*height**2*(radius-height/3);moment=math.pi*(radius**2-level**2)**2/4
    fixtures.append(('spherical_cap_'+str(level),cap,volume,V(0,0,moment/volume)))
    rotation=App.Rotation(V(1,2,3),37);rotated=cap.copy();rotated.Placement=App.Placement(V(),rotation)
    fixtures.append(('oblique_spherical_cap_'+str(level),rotated,volume,rotation.multVec(V(0,0,moment/volume))))
# Two polynomial spans with a genuine interior knot. The extrusion retains
# SurfaceOfExtrusion rather than converting that face into a BSplineSurface.
# x=5*t: z=2+2*t^2; x=5+5*t: z=4+4*t-5*t^2, both t in [0,1].
# Exact area=35, first moments about Z and X:2375/12 and397/6.
curve=Part.BSplineCurve()
curve.buildFromPolesMultsKnots([V(0,0,2),V(2.5,0,2),V(5,0,4),V(7.5,0,6),V(10,0,3)], [3,2,3], [0.,1.,2.], False, 2)
wire=Part.Wire([Part.makeLine(V(0,0,0),V(10,0,0)),Part.makeLine(V(10,0,0),V(10,0,3)),curve.toShape().reversed(),Part.makeLine(V(0,0,2),V(0,0,0))])
solid=Part.Face(wire).extrude(V(0,7,0))
fixtures.append(('two_span_spline_extrusion',solid,245.,V(475/84,3.5,397/210)))
for name,shape,volume,center in fixtures:
    assert shape.isValid() and len(shape.Solids)==1
    for nurbs in [False,True]:
        for moved in [False,True]:
            test=shape.toNurbs() if nurbs else shape.copy()
            frame=App.Placement(V(7491.553815,-291,1517.637951),App.Rotation(V(2,-1,3),43)) if moved else App.Placement()
            test.Placement=frame.multiply(test.Placement);expected=frame.multVec(center)
            q=mass.measure(test);dv=abs(q['volume_mm3']-volume);dc=math.dist(q['centroid_mm'],list(expected))
            check=dict(name=name,nurbs=nurbs,moved=moved,passed=q['converged'] and dv<1e-5 and dc<1e-6,volume_error_mm3=dv,centroid_error_mm=dc,measurement=q)
            checks.append(check);write(out/'progress.json',checks);print(name,nurbs,moved,check['passed'],dv,dc,flush=True)
for n,test in [('inverted',Part.makeBox(1,2,3)),('open',Part.makePlane(10,10)),('compound',Part.makeCompound([Part.makeBox(1,2,3),Part.makeBox(1,2,3,V(5,0,0))]))]:
    if n=='inverted':test.reverse()
    try:rejected=not mass.measure(test)['converged']
    except (AssertionError,ValueError):rejected=True
    checks.append(dict(name=n+' rejected',passed=rejected))
result=dict(passed=all(v['passed'] for v in checks),checks=checks,provenance=mass.provenance,checker_sha256=sha(Path(__file__)),scope='Two-span polynomial spline extrusion with exact moments, plus analytic solid/annular cylinders below inclined planes, spherical caps and oblique caps, NURBS conversion and rigid frames; invalid input negatives. Quadrature convergence thresholds unchanged; actual trimmed pcurves and surface knot crossings integrated.')
write(out/'qualification.json',result);assert result['passed'];print('PASSED',len(checks),'controls',flush=True)
