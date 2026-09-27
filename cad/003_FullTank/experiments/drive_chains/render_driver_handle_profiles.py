"""Compare saved handle hypotheses under unchanged source and hull projections."""
import argparse
import os
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.camera_review import validate_native_bindings

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--study', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
study, out = a.study.resolve(), a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
os.environ.setdefault('MPLCONFIGDIR', str(out / 'matplotlib_runtime'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

labels = ['overall_control', 'pivot_reach', 'functional_current', 'functional_source']
titles = ['Accepted overall extent (replay)', '37 in: second pivot to grip',
          '37 in: main shaft radius, current return', '37 in: main shaft radius, source direction']
candidates = [Saved(study / label) for label in labels]
parent = Saved((ROOT / candidates[0].report['parent_native']).parent)
render = read(parent.folder / 'render_receipt.json')
reg = read(ROOT / render['registration'])
assert sha(ROOT / render['registration']) == render['registration_sha256']
main = App.Vector(*parent.report['details']['foundation']['shafts']['Main']['center_world_mm'])
coef = complex(*render['side_registration']['complex_scale'])
plan = Image.open(ROOT / reg['source_image']).convert('RGB')
side = Image.open(ROOT / render['side_source']).crop((0,0,590,650)).transpose(Image.Transpose.ROTATE_90).convert('RGB')
anchors = reg['construction_picks']
pa, pb = [complex(*anchors[k]) for k in ['main_shaft_starboard_tip_px', 'main_shaft_port_tip_px']]
span = reg['printed_main_shaft_length_mm']
standard = read(H / 'transmission_brake_front_study/trial01/standard_context_manifest.json')
row = next(v for v in standard['occurrences'] if v['name'] == 'hull_front_slope')
entry = standard['definitions'][row['definition']]
assert sha(entry['brep_path']) == entry['brep_sha256']
nose = Part.Shape(); nose.read(entry['brep_path']); nose.Placement = pose(row['frame'])
records = {}


def coordinates(points, view):
    result = []
    for point in points:
        delta = point-main
        if view == 'side':
            p = complex(315,322)-coef*complex(delta.x,delta.z)
        elif view == 'plan':
            p = (pa+pb)/2+complex(delta.y,delta.x)*(pb-pa)/span
        else:
            p = complex(point.x, point.z)
        result.append((p.real, p.imag))
    return list(zip(*result))


def edges(ax, shape, view, color, alpha=1., width=.8):
    for edge in shape.Edges:
        points = edge.discretize(Deflection=.7)
        if len(points) > 1:
            ax.plot(*coordinates(points,view),color=color,alpha=alpha,linewidth=width)


for view in ['side', 'plan', 'hull']:
    fig, axes = plt.subplots(2,2,figsize=(14,11),dpi=140)
    for ax, label, title, s in zip(axes.flat, labels, titles, candidates):
        check = read(s.folder/'profile_checks02/report.json')
        context = read(s.folder/'context_audit/report.json')
        assert check['passed'] and check['native_sha256'] == context['native_sha256'] == sha(s.native)
        names = ['PortDriverOperatingHandle','PortDriverOperatingFulcrum','PortDriverLowSelector','PortDriverHighSelector','DriverMainShaft']
        if view == 'plan':
            names += ['StarboardDriverOperatingHandle','StarboardDriverOperatingFulcrum','StarboardDriverLowSelector','StarboardDriverHighSelector']
        validate_native_bindings(dict(native_file=str(s.native),render_occurrences=names,landmarks=[]),s.manifest)
        if view in ['side','plan']:
            ax.imshow(side if view == 'side' else plan, alpha=.75)
        for name in names:
            if name.endswith('OperatingHandle'):
                edges(ax,parent.world(name),view,'#228341',.6,.8)
                edges(ax,s.world(name),view,'#145aad',.9,1.)
            else:
                edges(ax,s.world(name),view,'#665877',.6,.65)
        record = check['records']['Port']
        if view == 'side':
            ax.set_xlim(0,405); ax.set_ylim(400,0)
        elif view == 'plan':
            ax.set_xlim(30,380); ax.set_ylim(475,185)
        else:
            # Section is a display copy. Physical candidate and hull are untouched.
            section = nose.common(Part.makeBox(2000,2,1800,App.Vector(7200,64,800)))
            edges(ax,section,view,'#b53624',.9,1.3)
            common = s.world('PortDriverOperatingHandle').common(nose)
            if common.Faces:
                edges(ax,common,view,'#e22b1c',1.,2.)
            ax.set_xlim(8350,7420); ax.set_ylim(1100,2150)
        ax.set_aspect('equal')
        ax.set_title(title,fontsize=11)
        verdict = ('context clear' if context['passed'] else 'REJECT: hull interference')
        ax.text(.02,.02,f'{verdict}\nPlan {record["plan_residual_px"]:.2f} px; side {record["side_residual_px"]:.2f} px',
                transform=ax.transAxes,fontsize=9,bbox=dict(facecolor='white',alpha=.92,edgecolor='none'))
        ax.tick_params(labelsize=8)
        records[label] = dict(native_sha256=sha(s.native),profile_receipt_sha256=sha(s.folder/'profile_checks02/report.json'),
                             context_receipt_sha256=sha(s.folder/'context_audit/report.json'))
    fig.suptitle('Complete handle hypotheses | fixed cameras and unchanged lower interfaces',fontsize=14)
    fig.text(.04,.015,'Green: accepted profile. Blue: saved alternative. Red: actual hull section/intersection.\nNo source pose, motion or alternative length datum is qualified. Source-direction case uses the grip pick as a construction constraint.',fontsize=10)
    fig.tight_layout(rect=(0,.065,1,.955))
    fig.savefig(out/(view+'_comparison.png'))
    plt.close(fig)
write(out/'render_receipt.json',dict(renderer_sha256=sha(Path(__file__)),candidates=records,
    registration_sha256=sha(ROOT/render['registration']),source_camera_refitted=False,
    images={p.name:sha(p) for p in out.glob('*.png')},geometry_modified=False,
    scope='Actual saved complete handle alternatives and retained neighbors. Fixed plan/side registrations. Physical hull section is a display copy only; rejected intersections are shown.'))
print('Rendered three comparisons for four saved hypotheses.',flush=True)
