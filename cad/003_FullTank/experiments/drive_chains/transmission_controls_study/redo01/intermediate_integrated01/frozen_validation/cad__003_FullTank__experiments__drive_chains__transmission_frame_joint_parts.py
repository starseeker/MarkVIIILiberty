"""Estimated formed gussets and volume-preserving upset frame rivets.

Local rivet +Z runs from the factory head seat into the grip. The source rivet
length is unformed stock, not the installed distance between head extremities.
"""
import math
import FreeCAD as App
import Part

from transmission_support_parts import box


def cap(a, height):
    sphere_radius=(a*a+height*height)/(2*height)
    sphere=Part.makeSphere(sphere_radius,App.Vector(0,0,height-sphere_radius))
    return sphere.common(box(-a-1,a+1,-a-1,a+1,0,height+1))


def rivet(diameter, stock_length, grip, head_ratio=1.75):
    radius=diameter/2;head_radius=radius*head_ratio
    assert stock_length>grip>0
    stock_volume=math.pi*radius*radius*(stock_length-grip)
    low,high=0,2*head_radius
    for _ in range(80):
        height=(low+high)/2
        volume=math.pi*height*(3*head_radius*head_radius+height*height)/6
        if volume<stock_volume:low=height
        else:high=height
    tail_height=(low+high)/2
    assert tail_height<head_radius, 'Stock requires an excessive upset head.'
    head=cap(head_radius,.7*diameter)
    head.rotate(App.Vector(),App.Vector(1,0,0),180)
    tail=cap(head_radius,tail_height);tail.translate(App.Vector(0,0,grip))
    shape=Part.makeCylinder(radius,grip).multiFuse([head,tail])
    assert shape.isValid() and len(shape.Solids)==1
    return shape,dict(diameter_mm=diameter,stock_length_mm=stock_length,grip_mm=grip,
        head_radius_mm=head_radius,factory_head_height_mm=.7*diameter,
        upset_height_mm=tail_height,upset_stock_volume_mm3=stock_volume)


def formed_gusset(original, side_sign, controls):
    rear=-controls['channel_depth']+controls['channel_stock']
    t=controls['gusset_stock'];width=controls['gusset_width']
    y0,y1=sorted([0,-side_sign*width])
    # Fold a return behind the upright's broad flange. Its horizontal leg
    # retains the prior triangular footprint and channel bearing interface.
    flange=box(rear-t,rear,y0,y1,-controls['return_height'],0)
    result=original.fuse(flange)
    assert result.isValid() and len(result.Solids)==1
    return result
