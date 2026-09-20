"""Native track parts with explicit reconstructed forging and forming geometry."""
import math

import FreeCAD as App
import Part
import Sketcher
import _PartDesign


def feature(body, name, shape):
    previous = body.Tip
    result = body.newObject("PartDesign::Feature", name)
    result.Shape = shape
    body.Tip = result
    if previous:
        previous.Visibility = False
    body.Document.recompute()
    return result


def cylinder_y(radius, length, x=0, y=0, z=0):
    return Part.makeCylinder(radius, length, App.Vector(x,y-length/2,z), App.Vector(0,1,0))


def rounded_rectangle(x0, x1, y0, y1, radius):
    r = radius
    points = [(x0+r,y0),(x1-r,y0),(x1,y0+r),(x1,y1-r),
              (x1-r,y1),(x0+r,y1),(x0,y1-r),(x0,y0+r)]
    centers = [(x1-r,y0+r),(x1-r,y1-r),(x0+r,y1-r),(x0+r,y0+r)]
    edges = []
    for index in range(4):
        a,b = points[2*index],points[2*index+1]
        end = points[(2*index+2)%8]
        center = centers[index]
        edges.append(Part.makeLine(App.Vector(*a,0), App.Vector(*b,0)))
        va,vb = App.Vector(b[0]-center[0],b[1]-center[1],0),App.Vector(end[0]-center[0],end[1]-center[1],0)
        vm = va+vb
        vm.normalize()
        mid = App.Vector(*center,0)+vm*r
        edges.append(Part.Arc(App.Vector(*b,0),mid,App.Vector(*end,0)).toShape())
    return Part.Wire(edges)


def pressed_patch(half_x, half_y, height, thickness):
    """A clamped quartic NURBS patch: flat boundary/tangent and controlled peak."""
    surfaces = []
    for z0 in [0, thickness]:
        poles = []
        for i in range(5):
            row = []
            for j in range(5):
                # B^4_2(0.5)^2 = 0.140625, so the surface peak is exactly height.
                z = z0 + (height/0.140625 if i == j == 2 else 0)
                row.append(App.Vector(-half_x+i*half_x/2, -half_y+j*half_y/2, z))
            poles.append(row)
        surface = Part.BSplineSurface()
        surface.buildFromPolesMultsKnots(poles, [5,5], [5,5], [0,1], [0,1], False, False, 4, 4)
        surfaces.append(surface.toShape())
    sides = []
    corners = [(-half_x,-half_y),(half_x,-half_y),(half_x,half_y),(-half_x,half_y)]
    for a,b in zip(corners,corners[1:]+corners[:1]):
        points = [App.Vector(*a,0),App.Vector(*b,0),App.Vector(*b,thickness),App.Vector(*a,thickness)]
        sides.append(Part.Face(Part.makePolygon(points+points[:1])))
    surfaces[0].reverse()
    solid = Part.makeSolid(Part.makeShell(surfaces+sides))
    if solid.Volume < 0:
        solid.reverse()
    return solid


def shoe(doc, name, v):
    from .cad_build import sketch_polygon, pad
    body = doc.addObject("PartDesign::Body", name)
    p,w,t = v["pitch"],v["width"],v["thickness"]
    x0,x1 = -p/2-v["overlap"],p/2+v["overlap"]
    ramp_end = p/2-v["overlap"]-2
    ramp_start = ramp_end-v["ramp_run"]
    lower = [(x0,0),(ramp_start,0),(ramp_end,v["lift"]),(x1,v["lift"])]
    points = [(x,-z) for x,z in lower+[(x,z+t) for x,z in reversed(lower)]]
    placement = App.Placement(App.Vector(0,-w/2,0),App.Rotation(App.Vector(1,0,0),-90))
    sketch = sketch_polygon(body,"PressedLongitudinalSection",points,placement)
    base = pad(body,sketch,w).Shape
    clip = Part.Face(rounded_rectangle(x0,x1,-w/2,w/2,v["corner_radius"])).extrude(App.Vector(0,0,200))
    clip.translate(App.Vector(0,0,-80))
    base = base.common(clip)
    hx,hy = v["dome_half_length"],v["dome_half_width"]
    hole = Part.makeBox(2*hx,2*hy,200,App.Vector(-hx,-hy,-80))
    patch = pressed_patch(hx,hy,v["dome_height"],t)
    formed = base.cut(hole).fuse(patch).removeSplitter()
    f = feature(body,"PressedNURBSCenter",formed)
    f.addProperty("App::PropertyString","FormingAssumption","Reconstruction")
    f.FormingAssumption = "Quartic NURBS center pressing with flat boundary/tangent. Constant vertical sheet thickness approximates the formed normal thickness."
    cuts = []
    for x in [-v["rivet_x"],v["rivet_x"]]:
        for y in [-v["rivet_y_outer"],-v["rivet_y_inner"],v["rivet_y_inner"],v["rivet_y_outer"]]:
            cuts.append(Part.makeCylinder(v["hole_diameter"]/2,100,App.Vector(x,y,-20)))
    finished = formed.cut(Part.makeCompound(cuts)).removeSplitter()
    feature(body,"EightRivetBores",finished)
    return body


def link(doc,name,v):
    body = doc.addObject("PartDesign::Body",name)
    pitch,thickness,z,r = v["pitch"],v["web_thickness"],v["pin_height"],v["eye_radius"]
    base_z = v["shoe_thickness"]+v["foot_thickness"]
    web = Part.makeBox(pitch,thickness,z+r-base_z,App.Vector(-pitch/2,-thickness/2,base_z))
    for x in [-pitch/2,pitch/2]:
        web = web.fuse(cylinder_y(r,thickness,x=x,z=z))
    feature(body,"ForgedWebAndEyes",web.removeSplitter())
    # A modeled stepped lap gives adjacent eyes separate material at one joint.
    # Exact production crank/fillet profiles remain explicit approximations.
    clear = v["lap_clearance"]
    cuts = [Part.makeBox(2*r+4,thickness+2,2*r+4,App.Vector(-pitch/2-r-2,-clear/2,z-r-2)),
            Part.makeBox(2*r+4,thickness+2,2*r+4,App.Vector(pitch/2-r-2,-thickness-2+clear/2,z-r-2))]
    web = web.cut(Part.makeCompound(cuts))
    feet = []
    hand = v["hand"]
    y0 = -thickness/2-v["foot_width"] if hand < 0 else thickness/2-1
    for x in [-v["rivet_x"],v["rivet_x"]]:
        feet.append(Part.makeBox(v["foot_length"],v["foot_width"]+1,v["foot_thickness"],
                                App.Vector(x-v["foot_length"]/2,y0,v["shoe_thickness"])))
    web = web.multiFuse(feet).removeSplitter()
    feature(body,"LappedEndsAndRivetFeet",web)
    cuts = [cylinder_y(v["pin_hole_diameter"]/2,thickness+4,x=x,z=z) for x in [-pitch/2,pitch/2]]
    foot_y = hand*(thickness/2+v["foot_width"]/2)
    for x in [-v["rivet_x"],v["rivet_x"]]:
        cuts.append(Part.makeCylinder(v["rivet_hole_diameter"]/2,100,App.Vector(x,foot_y,-10)))
    feature(body,"PinAndRivetBores",web.cut(Part.makeCompound(cuts)).removeSplitter())
    return body


def pin(doc,name,v):
    body=doc.addObject("PartDesign::Body",name)
    shape=cylinder_y(v["diameter"]/2,v["length"])
    shape=shape.fuse(cylinder_y(v["head_diameter"]/2,v["head_length"],y=-v["length"]/2-v["head_length"]/2))
    feature(body,"PinAndHead",shape.removeSplitter())
    bore=Part.makeCylinder(v["cotter_hole_diameter"]/2,v["diameter"]+4,
                          App.Vector(0,v["cotter_y"],-v["diameter"]/2-2))
    feature(body,"CotterCrossHole",shape.cut(bore).removeSplitter())
    return body


def bushing(doc,name,v):
    from .cad_build import part
    body=doc.addObject("PartDesign::Body",name)
    shape=cylinder_y(v["outer_diameter"]/2,v["length"]).cut(cylinder_y(v["inner_diameter"]/2,v["length"]+2))
    feature(body,"WearBushing",shape.removeSplitter())
    return body


def rivet(doc,name,v):
    body=doc.addObject("PartDesign::Body",name)
    radius=v["diameter"]/2
    shank=Part.makeCylinder(radius,v["grip"],App.Vector())
    a,h=v["head_diameter"]/2,v["head_height"]
    sphere_radius=(a*a+h*h)/(2*h)
    sphere=Part.makeSphere(sphere_radius,App.Vector(0,0,v["grip"]+h-sphere_radius))
    cap=sphere.common(Part.makeBox(2*a+2,2*a+2,h+1,App.Vector(-a-1,-a-1,v["grip"])))
    tail_sphere=Part.makeSphere(sphere_radius,App.Vector(0,0,sphere_radius-h))
    tail=tail_sphere.common(Part.makeBox(2*a+2,2*a+2,h+1,App.Vector(-a-1,-a-1,-h-1)))
    shape=shank.fuse(tail).fuse(cap).removeSplitter()
    source_volume=math.pi*radius*radius*v["stock_length"]+cap.Volume
    if abs(source_volume-shape.Volume)>1e-4:
        raise ValueError("Installed track rivet does not preserve source stock volume")
    feature(body,"InstalledTwoButtonRivet",shape)
    body.addProperty("App::PropertyLength","SourceStockShankLength","Source")
    body.SourceStockShankLength=v["stock_length"]
    body.addProperty("App::PropertyString","UpsetAssumption","Reconstruction")
    body.UpsetAssumption="Two equal spherical buttons; forged foot thickness follows stock-volume conservation. Underside form is not established by the top-view source photograph."
    return body


def cotter(doc,name,v):
    body=doc.addObject("PartDesign::Body",name)
    r=v["wire_radius"]
    # Bent split-pin envelope, made from one continuous round-section path.
    points=[(-7,-22),(-1.6,-14.5),(-1.6,15),( -4,19)]
    points += [(4*math.cos(a),19+4*math.sin(a)) for a in [math.pi-i*math.pi/8 for i in range(1,9)]]
    points += [(1.6,15),(1.6,-14.5),(7,-19)]
    solids=[]
    vectors=[App.Vector(x,0,z) for x,z in points]
    for a,b in zip(vectors,vectors[1:]):
        direction=b-a
        solids.append(Part.makeCylinder(r,direction.Length,a,direction))
    solids.extend(Part.makeSphere(r,p) for p in vectors)
    feature(body,"BentSplitPin",solids[0].multiFuse(solids[1:]).removeSplitter())
    body.addProperty("App::PropertyLength","NominalSplitPinLength","Source")
    body.NominalSplitPinLength=v["nominal_length"]
    return body


BUILDERS={"track_shoe":shoe,"track_link":link,"track_pin":pin,"track_bushing":bushing,
          "track_rivet":rivet,"track_cotter":cotter}


def build(doc,name,builder,arguments):
    return BUILDERS[builder](doc,name,arguments)
