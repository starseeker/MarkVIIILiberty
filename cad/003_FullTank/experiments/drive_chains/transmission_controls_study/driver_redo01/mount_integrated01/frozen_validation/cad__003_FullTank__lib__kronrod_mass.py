"""Explicit Gauss–Kronrod alternative after diagnosed Gauss integration failure.

Reuse AdaptiveMass's unchanged convergence predicates. This does not alter shapes,
relax measurement limits, or make an unconverged result acceptable.
"""
import os
from pathlib import Path
import subprocess
from .mass_properties import AdaptiveMass,digest


class KronrodMass(AdaptiveMass):
    def __init__(self,work,freecad_root=Path('/snap/freecad/current')):
        self.work=Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True)
        self.root=Path(freecad_root).resolve();source=Path(__file__).with_name('occt_kronrod_mass.cpp')
        self.environment=os.environ.copy()
        self.environment['LD_LIBRARY_PATH']=':'.join([str(self.root/'usr/lib'),str(self.root/'usr/lib/x86_64-linux-gnu'),self.environment.get('LD_LIBRARY_PATH','')])
        self.binary=self.work/'occt_kronrod_mass'
        command=['g++','-std=c++17','-O2','-I'+str(self.root/'usr/include/opencascade'),str(source),
            '-L'+str(self.root/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKMath','-lTKernel','-o',str(self.binary)]
        subprocess.run(command,env=self.environment,check=True,capture_output=True,text=True)
        self.provenance=dict(adapter_sha256=digest(Path(__file__)),convergence_adapter_sha256=digest(Path(__file__).with_name('mass_properties.py')),
            source_sha256=digest(source),binary_sha256=digest(self.binary),runtime_root=str(self.root),compile_command=command,
            header_sha256=digest(self.root/'usr/include/opencascade/BRepGProp.hxx'),library_sha256=digest(self.root/'usr/lib/libTKTopAlgo.so'),
            algorithm='BRepGProp::VolumePropertiesGK; OnlyClosed, IsUseSpan and CGFlag enabled; inertia and shared-face skipping disabled')
        self.cache={}

    def measure(self,shape):
        result=super().measure(shape)
        result['method']='BRepGProp::VolumePropertiesGK adaptive Gauss-Kronrod with knot spans'
        return result
