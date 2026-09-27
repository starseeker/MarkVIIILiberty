"""Seat support footprint derived from the visible fore-edge, not shaft span."""
from control_rebuild_io_v2 import App
from driver_folded_floor_support import floor_profile
from bow_reconstruction_parts import intersection, line_offset


def support(bow, controls, main, rear, hand, front_edge):
    points, at = floor_profile(bow)
    t, outer = controls['plate_stock'], controls['nut_seat_y']
    base = App.Vector(rear.x, 0, at(rear.x)[0])
    a, b = rear.x - 70., front_edge
    bottom = [[a, at(a)[0]]] + [p for p in points if a < p[0] < b] + [[b, at(b)[0]]]
    offsets = [line_offset(p, q, t, [0, 1]) for p, q in zip(bottom, bottom[1:])]
    upper = [intersection(offsets[0], ([a, 0], [a, 1]))]
    upper += [intersection(p, q) for p, q in zip(offsets, offsets[1:])]
    upper += [intersection(offsets[-1], ([b, 0], [b, 1]))]
    mounts = []
    # Keep complete heads off the floor bend; the hole pattern is unprinted.
    front_stop = min(b - 25., bow['joint_datums']['inner']['floor_bend'][0] - 30.)
    for x in [a + 30., a + 60., front_stop - 30., front_stop]:
        z, normal = at(x)
        mounts.append(dict(contact_world_mm=[x, hand * (outer + 27.5), z],
                           normal_world=list(normal),
                           floor='hull_floor_2' if x < bow['joint_datums']['inner']['floor_seam'][0] else 'hull_floor_1'))
    return None, App.Placement(base, App.Rotation()), mounts, dict(
        floor_contact_section_world=bottom, upper_foot_section_world=upper,
        stock_mm=t, canonical_origin_world_mm=list(base),
        main_shaft_local_mm=[main.x-rear.x, 0, main.z-base.z],
        swing_shaft_local_mm=[0, 0, rear.z-base.z],
        front_edge_world_x_mm=front_edge, front_mount_pair_x_mm=[front_stop-30.,front_stop],
        mount_clearance_rule='Frontmost hole center at least30mm aft of floor bend; full head and stock retained.',
        approximation='Forward footprint extends to the visible near-vertical side-plate edge below the front stay. Source registration unchanged; stock, hole pitches and exact edge position remain estimates.')
