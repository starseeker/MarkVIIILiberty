"""Independently check the saved seat-side material, fasteners and interfaces."""
import argparse
import math
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
s = Saved(a.candidate); parent = Saved((ROOT/s.report['parent_native']).parent)
d = s.report['details']; out = s.folder/'checks03'; out.mkdir(exist_ok=False)
validate_native_bindings(dict(native_file=str(s.native), render_occurrences=list(s.rows), landmarks=[]), s.manifest)
assert all(sha(ROOT/f) == h for f, h in s.report['input_hashes'].items())
V = App.Vector; X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
origin = V(*d['origin_world_mm']); checks = []


def check(name, value, **detail):
    checks.append(dict(name=name, passed=bool(value), **detail))
    if not value: print('FAILED', name, detail, flush=True)


def volume(q):
    return sum(abs(v.Volume) for v in q.Solids)


def planes(q, p, n):
    return [f for f in q.Faces if isinstance(f.Surface, Part.Plane) and
            f.normalAt(0, 0).cross(n).Length < 1e-7 and abs((f.CenterOfMass-p).dot(n)) < 1e-6]


def contact(q, other, p, n):
    return sum(f.common(g).Area for f in planes(q, p, n) for g in planes(other, p, n))


def bores(q, p, n, r):
    return [f for f in q.Faces if isinstance(f.Surface, Part.Cylinder) and
            abs(f.Surface.Radius-r) < 1e-7 and f.Surface.Axis.cross(n).Length < 1e-7 and
            (f.Surface.Center-p).cross(n).Length < 1e-6]


check('Exactly38 seat-side additions', len(s.report['new_occurrences']) == 38 and len(s.rows) == 227)
check('Seven new definitions; all inherited definitions unchanged', len(s.report['new_definitions']) == 7 and not s.report['changed_definitions'])
for key, row in s.manifest['definitions'].items():
    q = s.definition(key)
    check(key+' valid closed canonical solid', q.isValid() and q.Placement.isIdentity() and
          len(q.Solids) == 1 and q.Solids[0].isClosed() and q.getTolerance(1) <= 1e-4)
    if key in parent.manifest['definitions']:
        other = parent.definition(key)
        check(key+' complete inherited material', volume(q.cut(other)) < 1e-5 and volume(other.cut(q)) < 1e-5)
for name, row in parent.rows.items():
    check(name+' inherited frame and definition', s.rows[name]['frame'] == row['frame'] and s.rows[name]['definition'] == row['definition'])
frame = s.world('DriverSeatFrame')
cushion = s.world('DriverSeatCushion')
backpad = s.world('DriverSeatBackPadding')
check('Physical pan underside at source-derived construction datum', bool(planes(frame, origin, Z)))
check('Pan has3.175mm flat stock', bool(planes(frame, origin+Z*3.175, Z)))
check('Frame contains curved spline faces', any(isinstance(f.Surface, Part.BSplineSurface) for f in frame.Faces))
check('Back padding contains curved spline faces', any(isinstance(f.Surface, Part.BSplineSurface) for f in backpad.Faces))
seat_area = contact(frame, cushion, origin+Z*3.175, Z)
check('Cushion actually supported by pan', seat_area > 50000, contact_area_mm2=seat_area)
back_area = sum(f.common(g).Area for f in frame.Faces if isinstance(f.Surface, Part.BSplineSurface)
                for g in backpad.Faces if isinstance(g.Surface, Part.BSplineSurface))
check('Back padding has actual curved support contact', back_area > 80000, contact_area_mm2=back_area)
check('No overlapping upholstery or frame material', volume(frame.common(cushion)) < 1e-5 and
      volume(frame.common(backpad)) < 1e-5 and volume(cushion.common(backpad)) < 1e-5)
mounts = []
for row in d['bearing_records']:
    bearing = s.world(row['name']); pos = origin+V(*row['local_origin_mm'])
    area = contact(frame, bearing, pos, Z)
    check(row['name']+' actual flange contact', area > 1500, contact_area_mm2=area)
    pin = V(*row['receiving_center_world_mm'])
    check(row['name']+' open coaxial receiving bore', bool(bores(bearing, pin, Y, 8.15)))
    for rivet in row['rivets']:
        pp = origin+V(*rivet['local_underhead_mm']); riv = s.world(rivet['name'])
        check(rivet['name']+' receiving holes through pan and flange', bool(bores(frame, pp, Z, 4.9)) and bool(bores(bearing, pp, Z, 4.9)))
        head_area = contact(riv, frame, pp, Z)
        tail_area = contact(riv, bearing, pp-Z*15.875, Z)
        check(rivet['name']+' both heads seated', head_area > 100 and tail_area > 100,
              manufactured_head_contact_mm2=head_area, formed_head_contact_mm2=tail_area)
        check(rivet['name']+' full3/8-inch grip shank', bool(bores(riv, pp, Z, 4.7625)))
    mounts.append(dict(name=row['name'], actual_contact_mm2=area, receiving_center_world_mm=list(pin)))
q = s.definition('Def_DriverSeat_BearingRivet')
expected_head = math.pi*4*(3*8**2+4**2)/6
stock_volume = math.pi*4.7625**2*28.575
check('Rivet retains full reviewed stock through upset', abs(volume(q)-expected_head-stock_volume) < 1e-5,
      source_stock_volume_mm3=stock_volume, saved_volume_excluding_manufactured_head_mm3=volume(q)-expected_head)
q = s.definition('Def_DriverSeat_UpholsteryNail')
check('Complete half-inch nail includes point', abs(q.BoundBox.ZMin+12.7) < 1e-7 and abs(q.BoundBox.ZMax-1.5) < 1e-7)
check('Twenty-one physical upholstery nails', len(d['nails']) == 21)
for row in d['nails']:
    host = cushion if row['part'] == 'Cushion' else backpad
    nail = s.world(row['name']); p0 = origin+V(*row['point']); axis = V(*row['axis'])
    area = contact(nail, host, p0, axis)
    check(row['name']+' real tack head seating', area > 20, contact_area_mm2=area)
    check(row['name']+' full receiving shank clearance', bool(bores(host, p0, axis, 1.1)))
for side in ['Port', 'Starboard']:
    q = s.world('DriverSeat'+side+'Clip')
    area = contact(q, frame, origin, Z)+contact(q, frame, origin+Z*3.175, Z)
    check(side+' clip embraces both pan faces', area > 850, contact_area_mm2=area)
check('Installation limits remain explicit', not d['support_installation_complete'] and not s.report['geometry_integrated'] and not s.report['historical_geometry_qualified'])
result = dict(passed=all(v['passed'] for v in checks), checks=checks, mounts=mounts,
              native_sha256=sha(s.native), parent_native_sha256=sha(parent.native), checker_sha256=sha(Path(__file__)),
              geometry_integrated=False, support_installation_complete=False,
              scope='Saved seat-side forms, four open bearing receivers, two clips, eight stock-conserving rivets and21 complete nails. Source width, fabrication and support/adjustment topology remain estimated; full installation is not qualified.')
write(out/'independent_checks.json', result)
print('Seat material/interface checks', len(checks), 'passed', result['passed'], flush=True)
assert result['passed']
