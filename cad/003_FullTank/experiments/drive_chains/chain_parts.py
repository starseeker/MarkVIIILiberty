"""Source-controlled chain solids for the isolated fifty-pitch hypothesis."""
import math
import FreeCAD as App
import Part
from lib.track_parts import cylinder_y
from lib.pinion_parts import cotter
from sprocket_geometry import open_flanks


def bar(a,stock):
    p=a['pitch'];r=a['bar_end_radius']
    shape=cylinder_y(r,stock).fuse(cylinder_y(r,stock,x=p))
    shape=shape.fuse(Part.makeBox(p,stock,2*r,App.Vector(0,-stock/2,-r)))
    holes=[cylinder_y(a['pin_hole_diameter']/2,stock+2,x=x) for x in [0,p]]
    return shape.cut(Part.makeCompound(holes)).removeSplitter()


def parts(a,big):
    outside=a['outside_gap']/2+a['outer_stock']
    head_start=-outside-a['pin_head_stock'];end=head_start+a['maximum_width']
    pin=cylinder_y(a['pin_diameter']/2,end+outside,y=(end-outside)/2)
    pin=pin.fuse(cylinder_y(a['pin_head_radius'],a['pin_head_stock'],y=-outside-a['pin_head_stock']/2))
    pin=pin.cut(Part.makeCylinder((a['cotter_diameter']+a['cotter_hole_clearance'])/2,
               a['pin_diameter']+2,App.Vector(0,a['cotter_center_y'],-a['pin_diameter']/2-1),App.Vector(0,0,1)))
    length=a['inside_gap']-2*a['roller_end_gap']
    bush=cylinder_y(a['roller_diameter']/2,length).cut(cylinder_y(a['pin_hole_diameter']/2,length+2))
    c=dict(cotter_wire_radius=(a['cotter_diameter']-a['cotter_center_spacing'])/2,
           cotter_center_spacing=a['cotter_center_spacing'],pin_diameter=a['pin_diameter'],
           cotter_head_gap=a['cotter_head_gap'],cotter_nominal_length=a['cotter_length'],
           cotter_eye_radius=a['cotter_eye_radius'],cotter_eye_rise=a['cotter_eye_rise'])
    split=cotter(c)
    pitch_radius=a['pitch']/(2*math.sin(math.pi/a['small_teeth']))
    # Transfer only the big sprocket's addendum; the smaller tip diameter is
    # not dimensioned in the supplied controls and remains an approximation.
    radius=pitch_radius+big['sprocket_radius']-big['chain_pitch_radius']
    gear=cylinder_y(radius,a['small_tooth_width'])
    holes=[]
    for n in range(int(a['small_teeth'])):
        t=2*math.pi*n/a['small_teeth']
        holes.append(cylinder_y(a['seat_radius'],a['small_tooth_width']+2,
                               x=pitch_radius*math.sin(t),z=pitch_radius*math.cos(t)))
    gear=gear.cut(Part.makeCompound(holes))
    gear=open_flanks(gear,int(a['small_teeth']),pitch_radius,radius,a['small_tooth_width'],a['seat_radius'],a['flank_angle'])
    gear=gear.fuse(cylinder_y(a['small_hub_radius'],a['small_overall_width']))
    cuts=[cylinder_y(a['small_bore_radius'],a['small_overall_width']+2)]
    for n in range(int(a['splines'])):
        cut=Part.makeBox(a['spline_width'],a['small_overall_width']+2,a['spline_depth']+2,
                        App.Vector(-a['spline_width']/2,-a['small_overall_width']/2-1,a['small_bore_radius']-2))
        cut.rotate(App.Vector(),App.Vector(0,1,0),360*n/a['splines']);cuts.append(cut)
    gear=gear.cut(Part.makeCompound(cuts))
    result=dict(inner_bar=bar(a,a['inner_stock']),outer_bar=bar(a,a['outer_stock']),
                bush=bush,pin=pin,cotter=split,transmission_pinion=gear)
    for name,shape in result.items():
        result[name]=shape.removeSplitter()
        if not result[name].isValid() or len(result[name].Solids)!=1:
            raise ValueError('Invalid or disconnected chain part: '+name)
    return result
