"""Rebuild frame-reaching cast webs and replay later material features."""
import FreeCAD as App
import Part
from transmission_core_parts import outline_face, cylinder
from transmission_frame_parts import xz_plate
from transmission_support_parts import box


def bevel_case(c, frame):
    outer = outline_face(c['bevel_outline_segments'])
    inner = outline_face(c['bevel_outline_segments'], c['bevel_cavity_scale'])
    width, stock = c['bevel_half_width'], c['bevel_end_stock']
    blank = outer.extrude(App.Vector(0, 2 * width, 0))
    blank.translate(App.Vector(0, -width, 0))
    cavity = inner.extrude(App.Vector(0, 2 * (width - stock), 0))
    cavity.translate(App.Vector(0, -width + stock, 0))
    back = blank.cut(cavity).common(box(-500, -c['bevel_split_gap'] / 2,
                                      -width - 1, width + 1, -500, 500))
    back = back.cut(cylinder(c['bevel_sleeve_bore_radius'], -width - 1, width + 1))
    rear, top, bottom, height = [frame[k] for k in ['rear', 'top', 'bottom', 'height']]
    outline = [(rear, bottom - height), (rear + c['bevel_foot_depth'], bottom - height),
               (-c['bevel_web_front_reach'], -c['bevel_web_inner_z']),
               (-c['bevel_web_front_reach'], c['bevel_web_inner_z']),
               (rear + c['bevel_foot_depth'], top + height), (rear, top + height)]
    webs = [xz_plate(outline, width - c['bevel_web_stock'], width),
            xz_plate(outline, -width, -width + c['bevel_web_stock'])]
    return back.multiFuse(webs), outline


def replay_features(original_base, revised_base, detailed):
    """Retain all later bosses and pockets from the saved detailed casting.

    The original base is the saved, pre-detail casting. Feature deltas are actual
    material, not guessed hole locations. Their independent preservation and
    complete neighbor fit still require checking on the saved result.
    """
    added = detailed.cut(original_base)
    removed = original_base.cut(detailed)
    result = revised_base.copy()
    if added.Solids:
        result = result.fuse(added)
    if removed.Solids:
        result = result.cut(removed)
    assert result.isValid() and len(result.Solids) == 1
    return result, dict(later_added_mm3=added.Volume, later_removed_mm3=removed.Volume)
