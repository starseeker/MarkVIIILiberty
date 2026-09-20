"""Repeated circular seats with tangent straight flanks, an explicit approximation.

The handbook supplies pitch, tooth counts and roller diameter, but not the tooth
flank construction. This generator does not claim a standard or historical form.
"""
import math
import FreeCAD as App
import Part


def flank_tools(teeth,pitch_radius,tip_radius,width,seat_radius,flank_degrees):
    if not 0 < flank_degrees < 45:raise ValueError('Flank angle outside candidate range')
    angle=math.radians(flank_degrees)
    x=seat_radius*math.cos(angle)
    z=pitch_radius-seat_radius*math.sin(angle)
    top=tip_radius+5
    outer=x+(top-z)*math.tan(angle)
    points=[App.Vector(-x,-width/2-1,z),App.Vector(x,-width/2-1,z),
            App.Vector(outer,-width/2-1,top),App.Vector(-outer,-width/2-1,top)]
    wedge=Part.Face(Part.makePolygon(points+points[:1])).extrude(App.Vector(0,width+2,0))
    result=[]
    for n in range(teeth):
        tool=wedge.copy();tool.rotate(App.Vector(),App.Vector(0,1,0),n*360/teeth)
        result.append(tool)
    return Part.makeCompound(result)


def open_flanks(shape,teeth,pitch_radius,tip_radius,width,seat_radius,flank_degrees):
    result=shape.cut(flank_tools(teeth,pitch_radius,tip_radius,width,seat_radius,flank_degrees)).removeSplitter()
    if not result.isValid() or len(result.Solids)!=1:
        raise ValueError('Flank construction disconnected or invalidated the sprocket')
    return result
