"""Converged centerline quadrature and independent constant-section tube moments."""
import math
import numpy as np


def wire_reference(path, radius):
    estimates=[]
    for order in [96,192]:
        nodes,weights=np.polynomial.legendre.leggauss(order)
        length=0.;moment=np.zeros(3)
        for edge in path.Edges:
            lo,hi=edge.FirstParameter,edge.LastParameter
            knots=[lo]+([k for k in edge.Curve.getKnots() if lo<k<hi]
                         if hasattr(edge.Curve,'getKnots') else [])+[hi]
            for a,b in zip(knots,knots[1:]):
                for x,w in zip(nodes,weights):
                    t=float((a+b)/2+(b-a)/2*x)
                    dl=float(w)*(b-a)/2*edge.derivative1At(t).Length
                    length+=dl;moment+=np.array(tuple(edge.valueAt(t)))*dl
        first,last=path.Edges[0],path.Edges[-1]
        tangent_change=np.array(tuple(last.tangentAt(last.LastParameter)-first.tangentAt(first.FirstParameter)))
        # A curved circular tube's volume element is (1 - curvature*y) dA ds.
        # Its first moment includes -I * integral(dT/ds ds), I/A=radius^2/4.
        centroid=(moment-radius**2/4*tangent_change)/length
        estimates.append(dict(length_mm=length,volume_mm3=math.pi*radius**2*length,
                              centroid_mm=centroid.tolist(),order=order))
    a,b=estimates
    return dict(converged=abs(a['length_mm']-b['length_mm'])<1e-8 and
                math.dist(a['centroid_mm'],b['centroid_mm'])<1e-7,
                estimates=estimates,**b,
                method='Independent knot-span Gauss centerline integral; exact constant circular tube moment formula.')
