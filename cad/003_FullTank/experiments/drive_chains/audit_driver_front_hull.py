"""Audit saved front-hull rake in the existing whole-tank section registration."""
import argparse
import math
import os
from pathlib import Path
from control_rebuild_io_v2 import *

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
os.environ.setdefault('MPLCONFIGDIR', str(out/'matplotlib_runtime'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

calibration_path = H.parents[1]/'data/calibrations.json'
parameter_path = H.parents[1]/'data/parameters.json'
reg = read(calibration_path)['snl_2']
values = read(parameter_path)
scales = [reg['axes'][axis]['sign'] * values[reg['axes'][axis]['span_parameter']]['value'] /
          abs(reg['axes'][axis]['pixels'][1]-reg['axes'][axis]['pixels'][0]) for axis in ['x','z']]
datum = reg['datum_pixel']
source = ROOT/reg['image']
standard_path = H/'transmission_brake_front_study/trial01/standard_context_manifest.json'
standard = read(standard_path)
assert all(sha(ROOT/f)==digest for f,digest in standard['native_files'].items())
rows = {r['name']:r for r in standard['occurrences']}


def image_point(point):
    return [datum[0]+point.x/scales[0], datum[1]+point.z/scales[1]]


def world_point(point):
    return App.Vector((point[0]-datum[0])*scales[0],0,(point[1]-datum[1])*scales[1])


def shape(name):
    row = rows[name]; entry = standard['definitions'][row['definition']]
    assert sha(entry['brep_path'])==entry['brep_sha256']
    q = Part.Shape(); q.read(entry['brep_path']); q.Placement=pose(row['frame'])
    return q


def edges(ax,q,color,width=1.,alpha=.8):
    for edge in q.Edges:
        coords = [image_point(v) for v in edge.discretize(Deflection=1.)]
        if len(coords)>1: ax.plot(*zip(*coords),color=color,linewidth=width,alpha=alpha)


nose = shape('hull_front_slope')
face = max((f for f in nose.Faces if isinstance(f.Surface,Part.Plane)),key=lambda f:f.Area)
low = min(face.Vertexes,key=lambda v:v.Point.z).Point
high = max(face.Vertexes,key=lambda v:v.Point.z).Point
# Reviewed full-figure picks, confirmed against the unretouched original scan.
# These locate the central sloping wall, not the track-frame cheek outline.
source_low, source_high = [316.,392.], [404.,240.]
sl, sh = world_point(source_low), world_point(source_high)
native_dx, source_dx = high.x-low.x, sh.x-sl.x
normal = App.Vector(-(sh.z-sl.z),0,sh.x-sl.x)
normal.normalize()
native = Saved(H/'transmission_controls_study/driver_redo01/operating_integrated01')
main = App.Vector(*native.report['details']['foundation']['shafts']['Main']['center_world_mm'])
if (main-sl).dot(normal)<0:normal=-normal
profiles = H/'transmission_controls_study/driver_redo01/handle_profiles01'
records = {}
for label in ['overall_control','pivot_reach','functional_current','functional_source']:
    report = read(profiles/label/'profile_checks02/report.json')
    records[label] = dict(profile_receipt_sha256=sha(profiles/label/'profile_checks02/report.json'),
        pole_to_source_wall_plane_mm={side:(App.Vector(*r['actual_tip_world_mm'])-sl).dot(normal)
                                      for side,r in report['records'].items()},
        note='Distance to a source-derived plane only; not a new physical hull, clearance qualification or chosen model correction.')

fig,ax=plt.subplots(figsize=(14,10),dpi=150)
ax.imshow(Image.open(source).convert('RGB'))
for name in ['hull_floor_1','hull_floor_2']:
    edges(ax,shape(name),'#737373',1.)
for name in ['upper_driver_front','upper_driver_roof','upper_port_driver_side','hull_port_roof_driver']:
    edges(ax,shape(name),'#9454ab',1.)
edges(ax,nose,'#ca3026',2.)
for name in ['PortDriverOperatingHandle','PortDriverOperatingFulcrum','DriverMainShaft','DriverSwingShaft']:
    edges(ax,native.world(name),'#155dab',1.2)
ax.plot([source_low[0],source_high[0]],[source_low[1],source_high[1]],'o--',color='#128444',linewidth=2.,label='Reviewed source wall line')
ax.set_xlim(285,650);ax.set_ylim(475,175);ax.set_aspect('equal')
ax.set_title('Front-hull audit | existing whole-tank section registration, no refit')
ax.set_xlabel('SNL Plate 2 image pixels');ax.set_ylabel('SNL Plate 2 image pixels')
fig.text(.08,.035,'Red: actual saved front plate. Green: source wall picks. Blue: current driver controls.\nPurple: saved driver enclosure/roof. Grey: saved floors. Source outline and printed enclosure datums need joint review.',fontsize=11)
fig.subplots_adjust(bottom=.13,top=.92)
fig.savefig(out/'front_hull_audit.png');plt.close(fig)

original = H/'clutch_stop_brake_sources/p277_foldout_original.jpg'
crop=[1500,1200,3800,3600]
Image.open(original).crop(crop).resize((1150,1200)).save(out/'original_front_crop.png')
deps=[calibration_path,parameter_path,source,standard_path,H.parents[1]/'lib/hull_parts.py',
      H.parents[1]/'lib/hull_geometry.py',H.parents[1]/'data/datums.json',original,
      native.folder/'qualification.json',native.folder/'report.json']
result=dict(worker_sha256=sha(Path(__file__)),geometry_modified=False,source_camera_refitted=False,
    native_sha256=sha(native.native),standard_front_definition=rows['hull_front_slope']['definition'],
    standard_front_brep_sha256=standard['definitions'][rows['hull_front_slope']['definition']]['brep_sha256'],
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in deps},
    calibration=dict(key='snl_2',mode=reg['mode'],pixel_scales_mm=scales,datum_pixel=datum,
                     limitations=reg['note'],refitted=False),
    native_face_endpoints_px=dict(lower=image_point(low),upper=image_point(high)),
    source_wall_picks_px=dict(lower=source_low,upper=source_high,uncertainty_per_pick_px=5.),
    native_upper_minus_lower_x_mm=native_dx,source_upper_minus_lower_x_mm=source_dx,
    rake_sign_contradiction=native_dx*source_dx<0,
    native_upward_rake_degrees=math.degrees(math.atan2(high.z-low.z,native_dx)),
    source_upward_rake_degrees=math.degrees(math.atan2(sh.z-sl.z,source_dx)),
    source_pole_plane_diagnostics=records,
    original_scan_crop=dict(path=str(original.relative_to(ROOT)),box=crop,resize=[1150,1200]),
    images={p.name:sha(p) for p in out.glob('*.png')},
    conclusion='The saved central front plate rises forward; the reviewed central wall in the full longitudinal section rises aft. The high-resolution original scan confirms the source rake. Current front-plate/floor/enclosure geometry must be reviewed before using its interference to shorten handles or move the driver. The upper enclosure is independently dimensioned and also offset in this unchanged conditional registration; do not replace the whole shell with an unqualified tracing.',
    next_action='Reconstruct the bow wall and its lower floor junction, reviewing the HB enclosure dimension identities and SNL2/SNL7/HB6 context together. Audit hull part identity and roof joins before integrating any correction. Then rerun complete driver profiles and retained hull/control context; leave the current checkpoint intact meanwhile.')
assert result['rake_sign_contradiction']
write(out/'report.json',result)
print('Native/source rake degrees',result['native_upward_rake_degrees'],result['source_upward_rake_degrees'],flush=True)
print('Native/source endpoints',result['native_face_endpoints_px'],result['source_wall_picks_px'],flush=True)
