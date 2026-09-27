"""Build the source-counted seat-side assembly; support installation stays open."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_seat_parts_v2 import forms, bearing, clip, rivet, nail, back_width, center_x

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--width', type=float, default=480.)
a = p.parse_args()
parent = Saved(H/'driver_layout_study/trial01')
evidence = H/'driver_seat_study/evidence01'
receipt = read(H/'driver_seat_study/evidence_receipt.json')
assert all(sha(ROOT/f) == h for f, h in receipt['dependencies'].items())
d = read(evidence/'section_datums.json')
depth = d['pan_depth_estimate_mm']
origin = App.Vector(sum(d['construction_picks'][n]['conditional_world_xz_mm'][0] for n in ['pan_front', 'pan_rear'])/2,
                    0, d['pan_underside_height_estimate_mm'])
shapes = {k: parent.definition(k) for k in parent.manifest['definitions']}
props = {k: v['properties'] for k, v in parent.manifest['definitions'].items()}
specs = {n: dict(definition=r['definition'], frame=r['frame'], owner='DriverBowContext', role='receiver') for n, r in parent.rows.items()}


def add_definition(name, shape, marks, note):
    key = 'Def_DriverSeat_'+name
    shapes[key] = shape
    props[key] = dict(SourceRecords=marks, Representation='reconstruction_trial',
                     ReconstructionStatus=note,
                     ParameterUpdate='Regenerate build_driver_seat.py with recorded width; source evidence and section curves are external inputs.')
    return key


def add(name, key, point, rotation=None, owner='DriverSeat', role='seat'):
    placement = App.Placement(origin+point, rotation or App.Rotation())
    specs[name] = dict(definition=key, frame=list(placement.toMatrix().A), owner=owner, role=role)


V = App.Vector
X, Y, Z = V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)
frame, cushion, backpad, curves = forms(a.width, depth)
t = 3.175
bearing_key = add_definition('Bearing_SH289E', bearing(), ['SNL:017:024', 'SNL:207:027'],
    'Source-counted bearing. Flange, journal form,8.15mm bore and all unprinted stock estimated. Bearing axes are real receiving geometry; mating support members remain unbuilt.')
rivet_shape, rivet_detail = rivet(t+12.7)
rivet_key = add_definition('BearingRivet', rivet_shape, ['SNL:207:030', 'SNL:167:016'],
    'Reviewed original3/8x1-1/8in stock.15.875mm grip with volume-conserving upset tail;8mm-radius button heads are estimated.')
bearing_records = []
for station, source in [('Front', 'front_underseat_attachment'), ('Rear', 'rear_underseat_attachment')]:
    x = d['construction_picks'][source]['conditional_world_xz_mm'][0]-origin.x
    for side, hand in [('Port', 1), ('Starboard', -1)]:
        point = V(x, hand*(a.width/2-20), 0)
        name = 'DriverSeat'+side+station+'Bearing'
        add(name, bearing_key, point, owner='DriverSeatBearings')
        pins = []
        for i, offset in enumerate([-24, 24], 1):
            pp = point+V(offset, 0, t)
            frame = frame.cut(Part.makeCylinder(4.9, t+2, pp-V(0, 0, t+1)))
            n = name+'Rivet'+str(i)
            add(n, rivet_key, pp, owner='DriverSeatBearings', role='rivet')
            pins.append(dict(name=n, local_underhead_mm=list(pp)))
        bearing_records.append(dict(name=name, local_origin_mm=list(point), rivets=pins,
                                    receiving_axis='Y', receiving_radius_mm=8.15,
                                    receiving_center_world_mm=list(origin+point+V(0, 0, -35.5696394686906))))
clip_key = add_definition('Clip_SH291X', clip(), ['SNL:207:028'],
    'Two estimated spring clips embracing pan edges;2mm stock, sharp bends and30mm longitudinal length. Not SH291C; no adjustment-lock or motion qualification.')
for side, hand in [('Port', 1), ('Starboard', -1)]:
    add('DriverSeat'+side+'Clip', clip_key, V(25, hand*a.width/2, 0),
        App.Rotation(Z, 0 if hand==1 else 180), owner='DriverSeatClips', role='clip')
nail_key = add_definition('UpholsteryNail', nail(), ['SNL:207:029'],
    'Complete half-inch under-head stock including2mm point.2mm shank diameter and6mm button head are estimated; locations and upholstery substrate are unprinted.')
nails = []
for x, y in [(depth/2-42, yy) for yy in [-140, 0, 140]] + [(xx, hand*(a.width/2-60)) for hand in [-1, 1] for xx in [15, 70, 125]]:
    nails.append(dict(part='Cushion', point=[x, y, t+54], axis=[0, 0, 1]))
for z in [40, 80, 120, 160, 200, 240]:
    width = back_width(z, a.width-480)
    for hand in [-1, 1]:
        y = hand*((380+a.width-480)/2)
        x = center_x(z)+25*(2*y/width)**2+t+12
        # The unprinted back-tack pattern is placed on the planar edge seam,
        # retaining the curved padding and all21 complete nail stocks.
        nails.append(dict(part='BackPadding', point=[x, y, z], axis=[0, hand, 0]))
for i, rec in enumerate(nails, 1):
    point, axis = V(*rec['point']), V(*rec['axis'])
    # Cushion counterbores provide recessed head seats. Back-edge tacks seat on
    # existing planar perimeter faces; that outward tool removes only air.
    tool = Part.makeCylinder(3.3, 150, point, axis).fuse(Part.makeCylinder(1.1, 12.7, point-axis*12.7, axis))
    if rec['part']=='Cushion':
        cushion = cushion.cut(tool)
    else:
        backpad = backpad.cut(tool)
    name = 'DriverSeatUpholsteryNail'+str(i).zfill(2)
    add(name, nail_key, point, App.Rotation(Z, axis), owner='DriverSeatUpholstery', role='nail')
    rec['name'] = name
for name, shape, note in [('Frame', frame, 'One estimated fabricated M791 formed pan/back frame.'),
                           ('Cushion', cushion, 'Homogeneous seat upholstery volume; hidden material layers and tack recesses estimated.'),
                           ('BackPadding', backpad, 'Homogeneous back upholstery volume following the same spline support; tack recesses estimated.')]:
    key = add_definition(name, shape, ['SNL:207:026', 'HB:plate06', 'SNL:plate02'], note)
    add('DriverSeat'+name, key, V(), owner='DriverSeatM791', role='form')
details = dict(width_mm=a.width, pan_depth_mm=depth, origin_world_mm=list(origin), curves=curves,
               bearing_records=bearing_records, rivet=rivet_detail, nails=nails,
               source_camera_refitted=False, M791_catalogue_count=1, M791_modeled_constituents=3,
               support_installation_complete=False,
               required_later='M786/M787 complete seat connections, two M788 angles and their hardware; resolve SH291C application and shaft/seat historical position.',
               source_limit='Section pan datum is a construction estimate. Width, fabrication, bearing/clip profiles and hidden adjustment topology remain approximations. Full operating adjustment is not modeled.',
               retained_development_native=parent.report['parent_native'],
               retained_development_native_sha256=parent.report['parent_native_sha256'])
inputs = [Path(__file__), H/'driver_seat_parts_v2.py', H/'driver_seat_study/evidence_receipt.json',
          evidence/'report.json', evidence/'section_datums.json', evidence/'reviewed_erratum.json',
          parent.folder/'report.json', parent.folder/'isolated/manifest.json', H/'driver_layout_study/study_receipt.json']
trial(a.output, parent, shapes, specs, props, details, inputs)
print('Seat-side prototype:', len(specs)-len(parent.rows), 'additions;', len(specs), 'total occurrences;', len(shapes), 'definitions', flush=True)
