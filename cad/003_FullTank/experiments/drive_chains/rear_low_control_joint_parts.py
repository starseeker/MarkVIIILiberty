"""M569A/M568A low-speed control joint hypothesis, in pin-centered coordinates.

X is toward the rod. Y is the pin axis.
The literal 1-inch length from SNL87:002 is interpreted as throat-to-face
(threaded shank/socket length), ensuring >= 19.05mm thread engagement
while clearing receiver tips with a 22.225mm throat.
"""
import math
from pathlib import Path
import sys
import FreeCAD as App
import Part

H = Path(__file__).resolve().parent
if str(H) not in sys.path:
    sys.path.insert(0, str(H))
from transmission_input_installation_parts import formed_pin

V = App.Vector


def parts(c, nut, pin=None, cotter=None):
    radius = c['ear_radius']
    gap = c['lever_width'] + 2 * c['side_clearance']
    outer = gap + 2 * c['ear_stock']
    half = outer / 2
    if c['fork_length_datum'] == 'throat_to_rod_seat':
        face = c['throat_end'] + c['fork_length']
    elif c['fork_length_datum'] == 'overall':
        face = c['fork_length'] - radius
    elif c['fork_length_datum'] == 'pin_center_to_rod_seat':
        face = c['fork_length']
    else:
        raise ValueError(f"Unknown fork_length_datum: {c['fork_length_datum']}")
    assert face > c['throat_end']
    shoulder = min(c['ear_shoulder'], face - 0.5)

    # Analytic D-profile wire bounding both ears.
    a = V(0, -half, radius)
    b = V(shoulder, -half, radius)
    d = V(shoulder, -half, -radius)
    e = V(0, -half, -radius)
    wire = Part.Wire([
        Part.makeLine(a, b),
        Part.makeLine(b, d),
        Part.makeLine(d, e),
        Part.Arc(e, V(-radius, -half, 0), a).toShape()
    ])
    fork = Part.Face(wire).extrude(V(0, outer, 0))
    fork = fork.fuse(Part.makeCylinder(c['socket_radius'], face - c['throat_end'], V(c['throat_end'], 0, 0), V(1, 0, 0)))
    fork = fork.cut(Part.makeBox(c['throat_end'] + radius + 1, gap, 2 * radius + 2, V(-radius - 1, -gap / 2, -radius - 1)))
    bore = c['pin_diameter'] / 2 + c['pin_bore_radial_gap']
    fork = fork.cut(Part.makeCylinder(bore, outer + 2, V(0, -half - 1, 0), V(0, 1, 0)))
    thread = c['rod_diameter'] / 2 + c['thread_envelope_radial_gap']
    fork = fork.cut(Part.makeCylinder(thread, face - c['throat_end'] + 2, V(c['throat_end'] - 1, 0, 0), V(1, 0, 0)))

    station = half + c['cotter_station_beyond_fork']
    if pin is None:
        pin = Part.makeCylinder(c['pin_diameter'] / 2, c['pin_length'], V(0, -half, 0), V(0, 1, 0))
        pin = pin.fuse(Part.makeCylinder(c['pin_head_radius'], c['pin_head_stock'], V(0, -half - c['pin_head_stock'], 0), V(0, 1, 0)))
        cr = c['cotter_diameter'] / 2 + c['cotter_hole_radial_gap']
        pin = pin.cut(Part.makeCylinder(cr, c['pin_diameter'] + 2, V(-c['pin_diameter'] / 2 - 1, station, 0), V(1, 0, 0)))
    else:
        pin = pin.copy()

    _, cd = formed_pin(c)
    if cotter is None:
        cotter, _ = formed_pin(c)
        cotter.rotate(V(), V(0, 0, 1), -90)
        cotter = Part.makeCompound([cotter])
    else:
        cotter = cotter.copy()

    shapes = dict(fork=fork, pin=pin, cotter=cotter, nut=nut.copy())
    for name, s in shapes.items():
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids) == 1 and s.Solids[0].isClosed(), name
    local = dict(
        fork=App.Placement(),
        pin=App.Placement(),
        cotter=App.Placement(V(0, station, 0), App.Rotation()),
        nut=App.Placement(V(face, 0, 0), App.Rotation(V(0, 0, 1), V(1, 0, 0)))
    )
    return shapes, dict(
        fork_outer_width_mm=outer,
        fork_gap_mm=gap,
        rod_seat_x_mm=face,
        overall_fork_length_mm=face + radius,
        thread_envelope_length_mm=face - c['throat_end'],
        pin_head_seat_y_mm=-half,
        pin_tip_y_mm=-half + c['pin_length'],
        cotter_station_y_mm=station,
        cotter=cd,
        local_frames={k: list(v.toMatrix().A) for k, v in local.items()}
    )
