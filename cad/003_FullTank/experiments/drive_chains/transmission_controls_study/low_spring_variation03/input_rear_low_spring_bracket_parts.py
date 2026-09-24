"""Estimated U-shaped M4136 spring anchors with source-counted mounting rivets."""
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import formed_rivet

V = App.Vector


def parts(c, channel, channel_pose):
    b = c['bracket']
    width, half, t = b['width_x'], b['outer_span_y']/2, b['stock']
    height, radius = b['height'], b['inside_bend_radius']
    bracket = Part.makeBox(width, 2*half, t, V(-width/2, -half, 0))
    for side in [-1, 1]:
        y = -half if side < 0 else half-t
        leg = Part.makeBox(width, t, height-width/2, V(-width/2, y, 0))
        crown = Part.makeCylinder(width/2, t, V(0, y, height-width/2), V(0, 1, 0))
        bracket = bracket.fuse(leg).fuse(crown)
        # Concave bend material, tangent to the base and upright inner faces.
        low_y = -half+t if side < 0 else half-t-radius
        corner = Part.makeBox(width, radius, radius, V(-width/2, low_y, t))
        center_y = low_y+radius if side < 0 else low_y
        corner = corner.cut(Part.makeCylinder(radius, width+2,
                            V(-width/2-1, center_y, t+radius), V(1, 0, 0)))
        bracket = bracket.fuse(corner)
        bracket = bracket.cut(Part.makeCylinder(b['anchor_hole_diameter']/2, t+2,
                              V(0, y-1, b['anchor_height']), V(0, 1, 0)))
    for y in b['rivet_y']:
        bracket = bracket.cut(Part.makeCylinder(c['rivet']['hole_diameter']/2,
                              t+2, V(0, y, -1)))
    # Preserve the original if optional same-domain cleanup fails or inflates tolerance.
    cleaned = bracket.copy().removeSplitter()
    if (cleaned.isValid() and len(cleaned.Solids) == 1 and
            cleaned.getTolerance(1) <= max(1e-7, bracket.getTolerance(1))*1.01):
        bracket = cleaned
    rivet, rd = formed_rivet(c['rivet'], t+c['channel_stock'])
    tools, axes = [], []
    for side, xyz in c['stations'].items():
        for y in b['rivet_y']:
            center = V(*xyz)+V(0, y, 0)
            tool = Part.makeCylinder(c['rivet']['hole_diameter']/2,
                                    c['channel_stock']+2,
                                    center-V(0, 0, c['channel_stock']+1))
            tool.Placement = channel_pose.inverse().multiply(tool.Placement)
            tools.append(tool)
            axes.append(dict(station=side, world_mm=list(center)))
    holes = Part.makeCompound(tools)
    shapes = dict(bracket=bracket, rivet=rivet, channel=channel.cut(holes))
    for role, shape in shapes.items():
        if not (shape.isValid() and len(shape.Solids) == 1 and
                shape.Solids[0].isClosed() and shape.Placement.isIdentity()):
            raise ValueError(('Invalid M4136 trial shape', role))
    return shapes, dict(rivet=rd, receiving_hole_axes=axes), holes
