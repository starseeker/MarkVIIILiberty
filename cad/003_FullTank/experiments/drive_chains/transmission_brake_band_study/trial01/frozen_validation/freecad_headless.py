"""Launch a script against this workstation's FreeCAD snap, without starting GUI."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workdir',type=Path,default=Path.cwd())
    parser.add_argument('--freecad-root',type=Path,default=Path('/snap/freecad/current'))
    parser.add_argument('--qt-root',type=Path,default=Path('/snap/kf6-core24/current'))
    parser.add_argument('--probe',action='store_true')
    parser.add_argument('script',type=Path,nargs='?')
    parser.add_argument('script_args',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    if not args.probe and args.script is None:parser.error('Provide a script or --probe')
    work=args.workdir.resolve();work.mkdir(parents=True,exist_ok=True)
    fc=args.freecad_root.resolve();qt=args.qt_root.resolve()
    if not (fc/'usr/lib/FreeCAD.so').is_file():parser.error('FreeCAD Python library missing under --freecad-root')
    if not (qt/'usr/lib/x86_64-linux-gnu/libQt6Core.so.6').is_file():parser.error('Matching Qt library missing under --qt-root')
    env=os.environ.copy()
    env.update(LD_LIBRARY_PATH=':'.join(map(str,[fc/'usr/lib',fc/'usr/lib/x86_64-linux-gnu',qt/'usr/lib/x86_64-linux-gnu',qt/'usr/lib'])),
               PYTHONPATH=':'.join(map(str,[fc/'usr/lib',fc/'usr/lib/python3/dist-packages'])),
               PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='offscreen',QT_PLUGIN_PATH=str(qt/'usr/lib/x86_64-linux-gnu/qt6/plugins'))
    for key,name in [('FREECAD_USER_HOME','user'),('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('TMPDIR','tmp')]:
        folder=work/'runtime/freecad-skill'/name;folder.mkdir(parents=True,exist_ok=True);env[key]=str(folder)
    if args.probe:
        command=[sys.executable,'-c','import FreeCAD as A, Part, json; print(json.dumps(dict(freecad=A.Version(),occ=Part.OCC_VERSION,gui_up=bool(A.GuiUp))))']
    else:
        command=[sys.executable,str(args.script.resolve()),*args.script_args]
    return subprocess.call(command,cwd=work,env=env)


if __name__=='__main__':sys.exit(main())
