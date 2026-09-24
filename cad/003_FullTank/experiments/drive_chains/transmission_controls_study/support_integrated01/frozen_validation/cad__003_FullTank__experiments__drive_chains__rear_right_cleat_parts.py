"""Explicit M4129 shared-rivet mounting hypothesis; no source-defined profile."""
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import prism_xy, formed_rivet
from transmission_brake_stop_parts import hexagon

V = App.Vector


def parts(c, floor, floor_pose):
    a, b = c['cleat'], c['bolt']
    t, z, x = a['stock'], c['channel_height'], a['head_center_x']
    head = Part.makeBox(a['head_width_x'], a['head_span_y'], t,
                        V(x-a['head_width_x']/2, -a['head_span_y']/2, z))
    neck = Part.makeBox(t-x, a['neck_width'], t, V(x, -a['neck_width']/2, z))
    upright = Part.makeBox(t, a['neck_width'], z+t, V(0, -a['neck_width']/2, 0))
    half = a['foot_width']/2
    foot = prism_xy([(0, -half), (0, half), (a['foot_reach'], half)], t)
    cleat = head.fuse(neck).fuse(upright).fuse(foot)
    for y in a['rivet_y']:
        cleat = cleat.cut(Part.makeCylinder(c['rivet']['hole_diameter']/2, t+2,
                                          V(x, y, z-1)))
    cleat = cleat.cut(Part.makeCylinder(b['hole_diameter']/2, t+2,
                                      V(a['bolt_x'], a['bolt_y'], -1)))
    cleaned = cleat.copy().removeSplitter()
    if (cleaned.isValid() and len(cleaned.Solids) == 1 and
            cleaned.getTolerance(1) <= max(1e-7, cleat.getTolerance(1))*1.01):
        cleat = cleaned
    head = hexagon(b['head_af'], b['head_height'])
    head.translate(V(0, 0, -b['head_height']))
    bolt = Part.makeCylinder(b['diameter']/2, b['underhead_length']).fuse(head)
    rivet, rd = formed_rivet(c['rivet'], c['low_bracket_stock']+t+c['channel_stock'])
    holes, axes = [], []
    for xyz in c['stations'].values():
        axis = V(*xyz)+V(a['bolt_x'], a['bolt_y'], 0)
        drill = Part.makeCylinder(b['hole_diameter']/2, c['floor_thickness']+2,
                                  axis-V(0, 0, c['floor_thickness']+1))
        drill.Placement = floor_pose.inverse().multiply(drill.Placement)
        holes.append(drill)
        axes.append(list(axis))
    shapes = dict(cleat=cleat, bolt=bolt, low_rivet=rivet,
                  floor=floor.cut(Part.makeCompound(holes)))
    for role, s in shapes.items():
        if not (s.isValid() and len(s.Solids) == 1 and s.Solids[0].isClosed()
                and s.Placement.isIdentity()):
            raise ValueError(('Invalid combined support definition', role))
    return shapes, dict(rivet=rd, floor_hole_centers_world_mm=axes)
