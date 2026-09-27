"""Adaptive OCCT mass integration; leaves supplied CAD geometry unchanged.

FreeCAD's default mass properties can be inaccurate for heavily trimmed curved
faces. This adapter uses the same snap's headers/libraries and records convergence
at two integration precisions. It does not replace shape validity or material
comparison. Call only with independently checked closed single-solid geometry.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


class AdaptiveMass:
    def __init__(self,work,freecad_root=Path('/snap/freecad/current')):
        self.work=Path(work).resolve();self.work.mkdir(parents=True,exist_ok=True)
        self.root=Path(freecad_root).resolve();source=Path(__file__).with_name('occt_mass_properties.cpp')
        self.environment=os.environ.copy()
        self.environment['LD_LIBRARY_PATH']=':'.join([str(self.root/'usr/lib'),str(self.root/'usr/lib/x86_64-linux-gnu'),self.environment.get('LD_LIBRARY_PATH','')])
        self.binary=self.work/'occt_mass_properties'
        command=['g++','-std=c++17','-O2','-I'+str(self.root/'usr/include/opencascade'),str(source),
            '-L'+str(self.root/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKMath','-lTKernel','-o',str(self.binary)]
        subprocess.run(command,env=self.environment,check=True,capture_output=True,text=True)
        self.provenance=dict(adapter_sha256=digest(Path(__file__)),source_sha256=digest(source),binary_sha256=digest(self.binary),
            runtime_root=str(self.root),compile_command=command,
            header_sha256=digest(self.root/'usr/include/opencascade/BRepGProp.hxx'),
            library_sha256=digest(self.root/'usr/lib/libTKTopAlgo.so'))
        self.cache={}

    def measure(self,shape):
        import Part
        assert shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed()
        with tempfile.TemporaryDirectory(dir=self.work) as name:
            path=Path(name)/'shape.brep';shape.exportBrep(str(path));key=digest(path)
            if key in self.cache:return self.cache[key]
            result=json.loads(subprocess.check_output([str(self.binary),str(path)],env=self.environment,text=True))
        assert result['occ']==Part.OCC_VERSION
        coarse,fine=result['results'];volume_delta=abs(coarse['volume']-fine['volume'])
        centroid_delta=math.dist(coarse['centroid'],fine['centroid'])
        finite=all(math.isfinite(x) for v in result['results'] for x in [v['volume'],v['reported_error'],*v['centroid']])
        converged=finite and fine['volume']>0 and all(0<=v['reported_error']<=v['requested_error'] for v in result['results'])
        converged=converged and volume_delta<1e-5 and centroid_delta<1e-6
        result.update(brep_sha256=key,volume_convergence_mm3=volume_delta,centroid_convergence_mm=centroid_delta,
            converged=converged,volume_mm3=fine['volume'],centroid_mm=fine['centroid'],method='BRepGProp::VolumeProperties adaptive Gauss')
        self.cache[key]=result;return result
