"""Small compiled software rasterizer, cached by its complete source hash."""
import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import numpy as np


def paint(vertices, colors, width, height, runtime):
    vertices = np.ascontiguousarray(vertices,dtype=np.float64)
    colors = np.ascontiguousarray(colors,dtype=np.uint8)
    if vertices.shape != (len(colors),3,3) or colors.shape != (len(colors),3):
        raise ValueError("Invalid raster triangle/color arrays")
    if not np.isfinite(vertices).all() or (vertices.size and np.max(np.abs(vertices))>1e6) or not (0 < width <= 8192 and 0 < height <= 8192):
        raise ValueError("Invalid raster coordinates or dimensions")
    source = Path(__file__).with_suffix(".c")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:20]
    folder = Path(runtime)/"raster"
    folder.mkdir(parents=True,exist_ok=True)
    library = folder/(digest+".so")
    if not library.exists():
        temporary = library.with_suffix("."+str(os.getpid())+".tmp.so")
        subprocess.run(["cc","-O3","-fPIC","-shared",str(source),"-o",str(temporary),"-lm"],check=True,capture_output=True)
        temporary.replace(library)
    lib = ctypes.CDLL(str(library))
    doubles = np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
    bytes_ = np.ctypeslib.ndpointer(dtype=np.uint8,flags="C_CONTIGUOUS")
    lib.rasterize.argtypes = [ctypes.c_int,ctypes.c_int,ctypes.c_size_t,doubles,bytes_,bytes_,doubles]
    lib.rasterize.restype = None
    pixels = np.full((height,width,3),(246,244,237),dtype=np.uint8)
    depth = np.full((height,width),-np.inf,dtype=np.float64)
    lib.rasterize(width,height,len(colors),vertices,colors,pixels,depth)
    return pixels,depth
