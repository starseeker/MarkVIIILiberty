"""Report the actual headless numerical stack; no CAD or model inference."""
import json
import platform
import subprocess
import sys
import FreeCAD as App
import Part
import numpy
import scipy
import PIL
import fitz

print(json.dumps(dict(freecad=App.Version(), occ=Part.OCC_VERSION,
    python=sys.version, platform=platform.platform(), numpy=numpy.__version__,
    scipy=scipy.__version__, pillow=PIL.__version__, pymupdf=fitz.VersionBind,
    compiler=subprocess.check_output(['cc', '--version'], text=True).splitlines()[0],
    gui_up=bool(App.GuiUp))))
