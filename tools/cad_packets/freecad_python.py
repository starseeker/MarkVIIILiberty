"""Run a script with installed FreeCAD, keeping its settings inside the workspace."""
import os
from pathlib import Path
import sys


def main():
    base = Path('/snap/freecad/current').resolve()
    qt = Path('/snap/kf6-core24/current').resolve()
    if not (base / 'usr/lib/FreeCAD.so').is_file():
        raise RuntimeError('Installed FreeCAD Python library is missing')
    env = os.environ.copy()
    env.update(LD_LIBRARY_PATH=':'.join(str(p) for p in [base / 'usr/lib', base / 'usr/lib/x86_64-linux-gnu',
                   qt / 'usr/lib/x86_64-linux-gnu', qt / 'usr/lib']),
               PYTHONPATH=':'.join(str(p) for p in [base / 'usr/lib', base / 'usr/lib/python3/dist-packages']),
               QT_QPA_PLATFORM='offscreen', QT_PLUGIN_PATH=str(qt / 'usr/lib/x86_64-linux-gnu/qt6/plugins'),
               PYTHONDONTWRITEBYTECODE='1')
    for key, name in [('FREECAD_USER_HOME', 'user'), ('XDG_CONFIG_HOME', 'config'),
                      ('XDG_CACHE_HOME', 'cache'), ('XDG_DATA_HOME', 'data'), ('TMPDIR', 'tmp')]:
        folder = Path.cwd() / 'runtime' / name
        folder.mkdir(parents=True, exist_ok=True)
        env[key] = str(folder)
    os.execve(sys.executable, [sys.executable, *sys.argv[1:]], env)


if __name__ == '__main__':
    main()
