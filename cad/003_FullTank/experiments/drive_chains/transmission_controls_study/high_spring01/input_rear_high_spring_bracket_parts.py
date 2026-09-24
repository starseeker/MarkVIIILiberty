"""Estimated M4135 angle guides, with source-listed rivets and exact receiving holes."""
import FreeCAD as App
import Part
from rear_control_channel_mount_parts import formed_rivet

V = App.Vector


def parts(c, channel, channel_pose):
    b = c['bracket']
    t = b['stock']
    z = b['guide_height']
    radius = b['tab_radius']
    foot = Part.makeBox(b['foot_length'], b['foot_width'], t, V(0, -b['foot_width']/2, 0))
    upright = Part.makeBox(t, 2*radius, z, V(0, -radius, 0))
    crown = Part.makeCylinder(radius, t, V(0, 0, z), V(1, 0, 0))
    bend = b['inside_radius']
    corner = Part.makeBox(bend, 2*radius, bend, V(t, -radius, t))
    corner = corner.cut(Part.makeCylinder(bend, 2*radius + 2,
                                        V(t+bend, -radius-1, t+bend), V(0, 1, 0)))
    bracket = foot.fuse(upright).fuse(crown).fuse(corner)
    bracket = bracket.cut(Part.makeCylinder(b['guide_diameter']/2, t+bend+2,
                                           V(-1, 0, z), V(1, 0, 0)))
    local_holes = [Part.makeCylinder(c['rivet']['hole_diameter']/2, t+2,
                                    V(b['rivet_x'], y, -1)) for y in b['rivet_y']]
    bracket = bracket.cut(Part.makeCompound(local_holes)).removeSplitter()
    rivet, detail = formed_rivet(c['rivet'], t+c['channel_stock'])
    receiving = []
    axes = []
    for name, point in c['stations'].items():
        for y in b['rivet_y']:
            top = V(*point) + V(b['rivet_x'], y, 0)
            tool = Part.makeCylinder(c['rivet']['hole_diameter']/2, c['channel_stock']+2,
                                     top + V(0, 0, -c['channel_stock']-1))
            tool.Placement = channel_pose.inverse().multiply(tool.Placement)
            receiving.append(tool)
            axes.append(dict(station=name, world_mm=list(top)))
    holes = Part.makeCompound(receiving)
    modified = channel.cut(holes)
    shapes = dict(bracket=bracket, rivet=rivet, channel=modified)
    for role, shape in shapes.items():
        if not (shape.isValid() and len(shape.Solids) == 1 and shape.Solids[0].isClosed()
                and shape.Placement.isIdentity()):
            raise ValueError(('Invalid guide component', role))
    return shapes, dict(rivet=detail, channel_hole_axes=axes), holes
