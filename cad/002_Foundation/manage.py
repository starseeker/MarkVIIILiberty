#!/usr/bin/env python3
"""Reproducible Mark VIII foundation. Run --help; no third-party workbench required."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'calibrate', 'build', 'validate', 'export'])
    parser.add_argument('--output', type=Path, default=HERE / 'build', help='Generated output directory')
    parser.add_argument('--data', type=Path, default=HERE / 'data', help='Authored modeling records')
    args = parser.parse_args()
    out = args.output.resolve()
    repo = HERE.parents[1]
    # Never turn an input directory into a generated-output directory.
    protected = [repo / 'references', repo / 'cad/001_Survey', args.data.resolve()]
    if out == repo or out == HERE or any(out == p or p in out.parents or out in p.parents for p in protected):
        parser.error('Output must be a separate build directory, outside the source inputs.')
    runtime = Path(os.environ.get('MARKVIII_FREECAD_ROOT', '/snap/freecad/current')).resolve()
    qt = Path(os.environ.get('MARKVIII_QT_ROOT', '/snap/kf6-core24/current')).resolve()
    if not (runtime / 'usr/lib/FreeCAD.so').is_file():
        parser.error('FreeCAD libraries missing; set MARKVIII_FREECAD_ROOT to the installation root.')
    if not (qt / 'usr/lib/x86_64-linux-gnu/libQt6Core.so.6').exists():
        parser.error('Qt runtime missing; set MARKVIII_QT_ROOT to the matching packaged Qt root.')
    env = os.environ.copy()
    libdirs = [runtime / 'usr/lib', runtime / 'usr/lib/x86_64-linux-gnu',
               qt / 'usr/lib/x86_64-linux-gnu', qt / 'usr/lib']
    env['LD_LIBRARY_PATH'] = ':'.join(map(str, libdirs))
    env['PYTHONPATH'] = ':'.join(map(str, [runtime / 'usr/lib', runtime / 'usr/lib/python3/dist-packages']))
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['QT_QPA_PLATFORM'] = 'offscreen'
    env['QT_PLUGIN_PATH'] = str(qt / 'usr/lib/x86_64-linux-gnu/qt6/plugins')
    for key, name in [('FREECAD_USER_HOME', 'user'), ('XDG_CACHE_HOME', 'cache'),
                      ('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data')]:
        directory = out / 'runtime' / name
        directory.mkdir(parents=True, exist_ok=True)
        env[key] = str(directory)
    env['MARKVIII_RESOLVED_FREECAD'] = str(runtime)
    proc = subprocess.run([sys.executable, str(HERE / 'workflow.py'), args.command,
                           str(out), str(args.data.resolve())], env=env)
    return proc.returncode


if __name__ == '__main__':
    sys.exit(main())
