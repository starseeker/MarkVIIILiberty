"""Restricted independent quadrature; retains AdaptiveMass convergence predicates.

Only rectangular curved parametric patches and analytic/affine planar trimmed faces are
supported. Nonrectangular curved trims use a nested U antiderivative and oriented pcurve boundary integral.
Use after the retained Gauss/GK spring failures, with analytic control receipts.
"""
import os
import subprocess
from pathlib import Path
from lib.mass_properties import AdaptiveMass,digest


class TrimmedSurfaceMassV5(AdaptiveMass):
    def __init__(self,work,freecad_root=Path('/snap/freecad/current')):
        self.work=Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True)
        self.root=Path(freecad_root).resolve();source=Path(__file__).with_suffix('.cpp')
        self.environment=os.environ.copy()
        self.environment['LD_LIBRARY_PATH']=':'.join([str(self.root/'usr/lib'),str(self.root/'usr/lib/x86_64-linux-gnu'),self.environment.get('LD_LIBRARY_PATH','')])
        self.binary=self.work/'tube_surface_mass'
        command=['g++','-std=c++17','-O2','-I'+str(self.root/'usr/include/opencascade'),str(source),
                 '-L'+str(self.root/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKG2d','-lTKGeomAlgo','-lTKGeomBase','-lTKMath','-lTKernel','-o',str(self.binary)]
        subprocess.run(command,env=self.environment,check=True,capture_output=True,text=True)
        self.provenance=dict(adapter_sha256=digest(Path(__file__)),source_sha256=digest(source),
            convergence_adapter_sha256=digest(Path(__file__).parents[2]/'lib/mass_properties.py'),
            binary_sha256=digest(self.binary),runtime_root=str(self.root),compile_command=command,
            algorithm='Independent divergence integration; rectangular UV domains or exact pcurve-boundary Green integrals with numerical U antiderivative; planar Green boundary integrals; knot-span Gauss 16/32/64.',
            acceptance='Original reported-error, absolute volume and centroid convergence predicates unchanged.')
        self.cache={}

    def measure(self,shape):
        result=super().measure(shape)
        result['method']='Restricted tube surface quadrature; independent divergence theorem integration'
        return result
