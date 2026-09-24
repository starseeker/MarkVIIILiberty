"""Parameter-driven M4128 stock hypothesis; mounting details are a separate stage."""
import FreeCAD as App
import Part

def channel(width, height, stock, length):
    if not (length > 0 and 0 < stock < height and 2*stock < width):
        raise ValueError('Channel must retain a web, two flanges and an open underside')
    # One connected, downward-open section, extruded transversely. No Booleans.
    x = width/2
    profile = [(-x,0),(-x,height),(x,height),(x,0),
               (x-stock,0),(x-stock,height-stock),(-x+stock,height-stock),(-x+stock,0)]
    pts = [App.Vector(px,-length/2,pz) for px,pz in profile]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,length,0))
