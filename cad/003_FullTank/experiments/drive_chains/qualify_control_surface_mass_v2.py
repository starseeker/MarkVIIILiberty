"""Analytic, swept-wire, rigid-frame and unsupported-trim controls for local quadrature."""
import argparse,math,subprocess
from pathlib import Path
from control_rebuild_io import App,Part,H,ROOT,write,sha
from control_rebuild_surface_mass_v2 import TubeSurfaceMassV2
from control_rebuild_wire_measure import wire_reference
from lib.mass_properties import AdaptiveMass

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
mass=TubeSurfaceMassV2(out/'runtime');checks=[];V=App.Vector

fixtures=[('box',Part.makeBox(10,20,30),6000,[5,10,15],1e-5),
          ('cylinder',Part.makeCylinder(2,30),math.pi*4*30,[0,0,15],1e-5),
          ('torus',Part.makeTorus(9,1),2*math.pi**2*9,[0,0,0],1e-5),
          ('sphere',Part.makeSphere(5),4*math.pi*125/3,[0,0,0],1e-5)]
annulus=Part.makeCylinder(4,8).cut(Part.makeCylinder(2,10,V(0,0,-1)))
fixtures.append(('planar_holed_caps',annulus,math.pi*12*8,[0,0,4],1e-5))
# A rectangular plate with an off-center circular hole exercises planar first moments.
plate=Part.makeBox(30,20,5).cut(Part.makeCylinder(2,7,V(7,6,-1)))
removed=math.pi*4*5;vol=3000-removed
center=[(3000*x-removed*y)/vol for x,y in zip([15,10,2.5],[7,6,2.5])]
fixtures.append(('offset_planar_hole',plate,vol,center,1e-5))
radius=1.3;mean=8.225;height=100.;turns=30
path=Part.Wire(Part.makeHelix(height/turns,height,mean).Edges)
profile=Part.Wire([Part.makeCircle(radius,V(mean,0,0),V(0,mean,height/turns/(2*math.pi)))])
coil=path.makePipeShell([profile],True,True)
expected=math.pi*radius**2*math.hypot(2*math.pi*mean*turns,height)
fixtures.append(('analytic_helix',coil,expected,[0,0,height/2],1e-3))
curve=Part.BezierCurve();curve.setPoles([V(0,0,0),V(20,0,0),V(20,30,0),V(40,30,0)])
path=Part.Wire([curve.toShape()]);ref=wire_reference(path,radius)
assert ref['converged']
profile=Part.Wire([Part.makeCircle(radius,V(),V(1,0,0))])
pipe=path.makePipeShell([profile],True,True)
# This retained inflected Frenet sweep loses nominal tube stock despite valid
# topology. Independent Gaussian integration agrees with surface integration;
# retain it as a stock-loss negative, not a nominal uniform-tube control.
baseline=AdaptiveMass(out/'gauss_control_runtime').measure(pipe)
assert baseline['converged']
fixtures.append(('retained_inflected_sweep',pipe,baseline['volume_mm3'],baseline['centroid_mm'],1e-5))
checks.append(dict(name='inflected_sweep_stock_loss_detected',
    passed=abs(mass.measure(pipe)['volume_mm3']-ref['volume_mm3'])>1,
    independent_centerline_reference=ref,independent_gauss_measurement=baseline))

for name,shape,volume,center,stock_tol in fixtures:
    shape.exportBrep(str(out/(name+'.brep')))
    for mode in ['identity','located','baked']:
        moved=mode!='identity'
        f=App.Placement(V(126,43,-57),App.Rotation(V(1,2,3),43)) if moved else App.Placement()
        s=shape.transformGeometry(f.toMatrix()) if mode=='baked' else shape.copy()
        if mode!='baked':s.Placement=f
        m=mass.measure(s)
        dv=abs(m['volume_mm3']-volume);dc=math.dist(m['centroid_mm'],list(f.multVec(V(*center))))
        check=dict(name=name,mode=mode,passed=m['converged'] and dv<stock_tol and dc<1e-5,
                   measurement=m,volume_error_mm3=dv,centroid_error_mm=dc,stock_tolerance_mm3=stock_tol)
        checks.append(check);print(name,mode,check['passed'],dv,dc,flush=True)
        write(out/'progress.json',checks)
unsupported=Part.makeSphere(5).cut(Part.makeCylinder(1,20,V(2,0,-10)))
assert unsupported.isValid() and len(unsupported.Solids)==1
unsupported.exportBrep(str(out/'unsupported_curved_trim.brep'))
try:
    mass.measure(unsupported);rejected=False
except subprocess.CalledProcessError:rejected=True
checks.append(dict(name='nonrectangular_curved_trim_rejected',passed=rejected))
try:
    mass.measure(unsupported.transformGeometry(App.Placement(V(126,43,-57),App.Rotation(V(1,2,3),43)).toMatrix()));rejected=False
except subprocess.CalledProcessError:rejected=True
checks.append(dict(name='baked_nonrectangular_curved_trim_rejected',passed=rejected))
inverted=Part.makeBox(10,20,30);inverted.reverse()
checks.append(dict(name='negative_oriented_mass_rejected',passed=not mass.measure(inverted)['converged']))
result=dict(passed=all(c['passed'] for c in checks),checks=checks,provenance=mass.provenance,
            checker_sha256=sha(Path(__file__)),wire_reference_sha256=sha(H/'control_rebuild_wire_measure.py'),
            method_scope='Closed single solids; rectangular UV domains on curved surfaces, general planar boundaries. Refuses unsupported curved trims.',
            warning='Surface quadrature is a restricted measurement alternative, not general CAD validation. Separate topology, material and interface checks remain required.')
write(out/'qualification.json',result);assert result['passed']
