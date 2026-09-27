"""Explicitly approximate seat forms, real bearing bores and complete hardware."""
import math
from control_rebuild_io_v2 import App, Part

V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)


def box(dx, dy, dz, p):
    return Part.makeBox(dx, dy, dz, V(*p))


def rounded_wire(x0, x1, width, radius, z):
    y0, y1 = -width / 2, width / 2
    r = radius
    points = [V(x0+r, y0, z), V(x1-r, y0, z), V(x1, y0+r, z), V(x1, y1-r, z),
              V(x1-r, y1, z), V(x0+r, y1, z), V(x0, y1-r, z), V(x0, y0+r, z)]
    centers = [V(x1-r, y0+r, z), V(x1-r, y1-r, z), V(x0+r, y1-r, z), V(x0+r, y0+r, z)]
    edges = []
    for i in range(4):
        a, b, c = points[2*i], points[2*i+1], points[(2*i+2) % 8]
        edges.append(Part.makeLine(a, b))
        mid = b + c - centers[i]*2
        mid.normalize()
        edges.append(Part.Arc(b, centers[i] + mid*r, c).toShape())
    return Part.Wire(edges)


def center_x(z):
    return -75.175 - .25*z - .001235*z*z


def back_width(z, width_delta=0):
    return 380 + width_delta + 40*z/300 + 40*math.sin(math.pi*z/300)


def transverse_edge(z, width, offset):
    # Exact quadratic Bezier: x(center)=cx, x(edges)=cx+25 mm.
    cx = center_x(z) + offset
    curve = Part.BezierCurve()
    curve.setPoles([V(cx+25, -width/2, z), V(cx-25, 0, z), V(cx+25, width/2, z)])
    return curve.toBSpline().toShape()


def back_wire(z, width, x0, x1):
    rear = transverse_edge(z, width, x0)
    front = transverse_edge(z, width, x1)
    front.reverse()
    cx = center_x(z)+25
    return Part.Wire([rear, Part.makeLine(V(cx+x0, width/2, z), V(cx+x1, width/2, z)),
                      front, Part.makeLine(V(cx+x1, -width/2, z), V(cx+x0, -width/2, z))])


def cap(base_radius, height):
    """Analytic spherical cap, base at Z0 and pole at positive Z."""
    radius = (base_radius**2 + height**2) / (2*height)
    sphere = Part.makeSphere(radius, V(0, 0, height-radius))
    return sphere.common(box(2*radius+2, 2*radius+2, height+1, [-radius-1, -radius-1, 0]))


def rivet(grip, stock=28.575, radius=4.7625):
    tail_volume = math.pi*radius*radius*(stock-grip)
    base_radius = 8.0
    lo, hi = 0., 16.
    for _ in range(80):
        h = (lo+hi)/2
        volume = math.pi*h*(3*base_radius**2+h*h)/6
        if volume < tail_volume:
            lo = h
        else:
            hi = h
    height = (lo+hi)/2
    formed = cap(base_radius, height)
    formed.Placement = App.Placement(V(0, 0, -grip), App.Rotation(X, 180))
    head = cap(base_radius, 4.0)
    q = head.fuse(Part.makeCylinder(radius, grip, V(0, 0, -grip))).fuse(formed)
    return q, dict(stock_length_mm=stock, radius_mm=radius, grip_mm=grip,
                   formed_head_height_mm=height, formed_tail_volume_mm3=tail_volume,
                   manufactured_head_volume_mm3=head.Volume)


def nail():
    # 12.7 mm under-head length includes a 2 mm point. Head unprinted.
    q = Part.makeCylinder(1., 10.7, V(0, 0, -10.7))
    q = q.fuse(Part.makeCone(0, 1., 2., V(0, 0, -12.7)))
    return q.fuse(cap(3., 1.5))


def bearing():
    flange = box(70, 30, 12.7, [-35, -15, -12.7])
    web = box(30, 30, 24, [-15, -15, -36])
    lug = Part.makeCylinder(20, 30, V(0, -15, -35.5696394686906), Y)
    q = flange.fuse(web).fuse(lug)
    q = q.cut(Part.makeCylinder(8.15, 32, V(0, -16, -35.5696394686906), Y))
    for x in [-24, 24]:
        q = q.cut(Part.makeCylinder(4.9, 15, V(x, 0, -13), Z))
    return q


def clip(stock=3.175):
    # Two 2 mm spring-strip feet embrace the pan edge. No SH291C length transfer.
    pts = [(-15, -2), (2, -2), (2, stock+2), (-15, stock+2),
           (-15, stock), (0, stock), (0, 0), (-15, 0)]
    wire = Part.makePolygon([V(-15, y, z) for y, z in pts] + [V(-15, *pts[0])])
    return Part.Face(wire).extrude(V(30, 0, 0))


def forms(width, depth):
    t = 3.175
    delta = width - 480
    pan = Part.Face(rounded_wire(-depth/2, depth/2, width, 20, 0)).extrude(V(0, 0, t))
    sections = [0, 15, 40, 80, 120, 160, 200, 240, 280, 300]
    surface = Part.makeLoft([Part.Wire([transverse_edge(z, back_width(z, delta), 0)]) for z in sections], False, False)
    back = surface.extrude(V(t, 0, 0))
    frame = pan.fuse(back)
    # Both solids use the SAME master surface, so upholstery support is exact.
    # Clip only to the chosen upholstery perimeter, not to neighboring hardware.
    front = surface.copy()
    front.translate(V(t, 0, 0))
    back_pad = front.extrude(V(24, 0, 0))
    back_pad = back_pad.common(box(500, 380+delta, 385, [-300, -(380+delta)/2, 15]))
    cushion = Part.makeLoft([
        rounded_wire(-20, depth/2-6, width-60, 18, t),
        rounded_wire(-25, depth/2-6, width-60, 18, t+20),
        rounded_wire(-10, depth/2-22, width-90, 25, t+55)], True, False)
    return frame, cushion, back_pad, dict(sheet_stock_projected_x_mm=t,
        pan_stock_mm=t, back_height_mm=300, back_section_z_mm=sections,
        transverse_curve='Quadratic Bezier; edge X=cx+25, center pole X=cx-25; degree2.',
        center_x_formula='-75.175 - 0.25*z - 0.001235*z*z',
        back_width_formula='380+(pan_width-480)+40*z/300+40*sin(pi*z/300)',
        pad_thickness_projected_x_mm=24, longitudinal_loft_ruled=False,
        common_master_surface=True,
        approximation='Formed pan/back and homogeneous upholstery volumes; hidden fabrication, material layers, stock and transverse sizes are estimated. No artificial separate wood identity.')
