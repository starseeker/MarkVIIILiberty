"""Explicit-accuracy OCC mass integration; never changes BRep tolerances."""
import json,os,subprocess
from pathlib import Path


def calculator(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).with_suffix('.cpp')
    installed=Path(os.environ['MARKVIII_RESOLVED_FREECAD'])
    executable=folder/'case_joint_mass'
    subprocess.run(['g++','-std=c++17','-O2',str(source),'-I'+str(installed/'usr/include/opencascade'),
        '-L'+str(installed/'usr/lib'),'-lTKTopAlgo','-lTKBRep','-lTKG3d','-lTKMath','-lTKernel','-o',str(executable)],check=True,capture_output=True)
    def evaluate(shape,label):
        path=folder/(label+'.brep');shape.exportBrep(str(path))
        return json.loads(subprocess.check_output([str(executable),str(path)],text=True))
    return evaluate
