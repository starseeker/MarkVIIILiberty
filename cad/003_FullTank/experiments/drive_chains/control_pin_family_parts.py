"""Local material revision of the estimated M568A family; all frames retained.

This changes the existing solids, not their source identities. The selected
diameter is an explicit common-interface estimate, not a printed dimension.
"""
import FreeCAD as App
import Part

V = App.Vector
CHANGED = ('Def_ControlJoint_pin', 'Def_ControlJoint_fork',
           'Def_HighBrakeMechanism_lever_left', 'Def_HighBrakeMechanism_lever_right')


def annulus(outer, inner, start, length):
    return Part.makeCylinder(outer, length, start, V(0, 1, 0)).cut(
        Part.makeCylinder(inner, length+2, start-V(0, 1, 0), V(0, 1, 0)))


def revise(old, diameter, radial_gap):
    """Keep head, cross-hole, fork outlines, lever curves and all other bores."""
    radius = diameter/2
    bore = radius+radial_gap
    assert 6 <= radius < 7.9375 and 0 < radial_gap < .3
    made = {k: v.copy() for k, v in old.items()}
    made[CHANGED[0]] = old[CHANGED[0]].cut(
        annulus(8.9375, radius, V(0, -17.7125, 0), 41.275))
    for low, high in [(-17.7125, -12.95), (12.95, 17.7125)]:
        made[CHANGED[1]] = made[CHANGED[1]].fuse(
            annulus(8.0875, bore, V(0, low, 0), high-low))
    for key, y in [(CHANGED[2], -12.7), (CHANGED[3], 0)]:
        made[key] = old[key].fuse(
            annulus(8.0875, bore, V(238.45, y, -293.675), 12.7))
    for key in CHANGED:
        s = made[key]
        assert s.Placement.isIdentity() and s.isValid() and len(s.Solids) == 1
        assert s.Solids[0].isClosed() and s.getTolerance(1) <= 1e-4, key
    return made
