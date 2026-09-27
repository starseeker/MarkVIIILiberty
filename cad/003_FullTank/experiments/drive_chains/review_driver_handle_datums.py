"""Bound grip comparison errors without changing accepted geometry or cameras.

Run with system Python. Measurements come from the qualified saved-native render
receipt. The plan uncertainty calculation is exact for independently bounded
endpoint disks; it is not a camera fit or a statistical confidence interval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
F = H / 'transmission_controls_study/driver_redo01'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(a, b, x, y, span):
    # Complex image coordinates: multiplication by i rotates the shaft vector
    # toward world +X. World +Y is along the shaft, as in the retained camera.
    return (a + b) / 2 + complex(y, x) * (b - a) / span


def uncertainty_record(a, b, x, y, span, source, endpoint_radius, tip_radius):
    w = complex(y, x) / span
    ca, cb = .5 - w, .5 + w
    nominal = project(a, b, x, y, span)
    radius = endpoint_radius * (abs(ca) + abs(cb))
    residual = abs(source - nominal)
    # Each conformal coefficient maps a disk to a disk. Their Minkowski sum
    # is exactly a disk of radius R, including with unequal coefficient phases.
    # Construct endpoint shifts that attain its boundary toward the source.
    direction = (source - nominal) / residual
    da = endpoint_radius * direction * ca.conjugate() / abs(ca)
    db = endpoint_radius * direction * cb.conjugate() / abs(cb)
    shifted = project(a + da, b + db, x, y, span)
    assert abs(shifted - nominal - radius * direction) < 1e-9
    assert abs(abs(da) - endpoint_radius) < 1e-9
    assert abs(abs(db) - endpoint_radius) < 1e-9
    return dict(
        nominal_saved_tip_px=[nominal.real, nominal.imag],
        source_tip_px=[source.real, source.imag],
        nominal_residual_px=residual,
        endpoint_uncertainty_radius_px=endpoint_radius,
        source_tip_uncertainty_radius_px=tip_radius,
        maximum_projected_tip_shift_px=radius,
        minimum_possible_residual_px=max(0., residual - radius - tip_radius),
        attainability_control_passed=True,
        extreme_endpoint_shifts_px=[[da.real, da.imag], [db.real, db.imag]],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.exists(), 'Preserve prior evidence; choose a fresh output directory.'
    candidate = F / 'operating_integrated01'
    report = read(candidate / 'report.json')
    render = read(candidate / 'render_receipt.json')
    qualification = read(candidate / 'qualification.json')
    native = candidate / report['native_file']
    assert sha(native) == report['native_sha256'] == render['native_sha256']
    assert qualification['native_sha256'] == sha(native)
    assert qualification['local_static_checks_passed']
    reg_path = F / 'mount_registration01.json'
    picks_path = F / 'operating_landmarks01.json'
    reg, picks = read(reg_path), read(picks_path)
    assert sha(reg_path) == render['registration_sha256']
    assert sha(picks_path) == render['operating_landmarks_sha256']
    anchors = reg['construction_picks']
    a = complex(*anchors['main_shaft_starboard_tip_px'])
    b = complex(*anchors['main_shaft_port_tip_px'])
    span = reg['printed_main_shaft_length_mm']
    center = report['details']['foundation']['shafts']['Main']['center_world_mm']
    uncertainty = reg['pick_uncertainty_px']
    results = {}
    for side, actual in render['operating_handle_comparison'].items():
        x = actual['actual_tip_world_mm'][0] - center[0]
        y = actual['actual_tip_world_mm'][1] - center[1]
        source = complex(*picks['plan_cap_picks_px'][side])
        r = uncertainty_record(a, b, x, y, span, source,
                               uncertainty, picks['pick_uncertainty_px'])
        assert abs(complex(*r['nominal_saved_tip_px']) -
                   complex(*actual['plan_tip_px'])) < 1e-9
        # If the original 5 px allowance meant +/-5 in EACH coordinate, its
        # square lies inside a radius sqrt(2)*5 disk. This is a conservative
        # outer bound for that alternative interpretation, not an exact square.
        r['coordinate_square_outer_bound'] = uncertainty_record(
            a, b, x, y, span, source, uncertainty * math.sqrt(2),
            picks['pick_uncertainty_px'] * math.sqrt(2))
        assert r['coordinate_square_outer_bound']['minimum_possible_residual_px'] > 0
        results[side] = r

    # Independent controls for the closed form: shaft endpoints must project
    # directly to their respective picks, and the centre to their midpoint.
    assert abs(project(a, b, 0, -span / 2, span) - a) < 1e-10
    assert abs(project(a, b, 0, span / 2, span) - b) < 1e-10
    assert abs(project(a, b, 0, 0, span) - (a + b) / 2) < 1e-10
    assert abs(project(a + 3 + 4j, b + 3 + 4j, 123, 45, span) -
               project(a, b, 123, 45, span) - (3 + 4j)) < 1e-10

    sources = [
        candidate / 'report.json', candidate / 'render_receipt.json',
        candidate / 'qualification.json', candidate / 'source_comparison_diagnosis.json',
        reg_path, picks_path, F / 'handbook_text01.json',
        ROOT / 'cad/001_Survey/inputs/figure_index.json',
        ROOT / 'cad/001_Survey/inputs/snl_rows.json',
        ROOT / reg['source_image'],
        ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/proofs/checkpoint08/source-145-148.jpg',
        ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/proofs/checkpoint08/source-149-152.jpg',
    ]
    assets = ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'
    sources += [assets / f'plate{plate}.png' for plate in ['06', '92', '93', '113']]
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    diagnosis = read(candidate / 'source_comparison_diagnosis.json')
    result = dict(
        native_sha256=sha(native), worker_sha256=sha(Path(__file__)),
        source_hashes=source_hashes, geometry_modified=False,
        source_camera_refitted=False, source_length_datum_resolved=False,
        nominal_plan_comparison_reproduced=True,
        uncertainty_model='Independent endpoint and grip-pick disks of radius 5 px; also an outer bound enclosing +/-5 px coordinate squares. Printed shaft span and current saved geometry fixed. Bounds are conditional, not statistical.',
        equation='p = (a+b)/2 + ((Y+iX)/S)*(b-a); R = e*(abs(1/2-w)+abs(1/2+w)), w=(Y+iX)/S. Residual lower bound=max(0,abs(source-p)-R-tip_allowance).',
        controls_passed=['Native binding', 'Retained projection reproduced',
                         'Shaft endpoints and midpoint', 'Rigid image translation',
                         'Uncertainty extrema attained by explicit endpoint shifts'],
        plan=results,
        nominal_side_diagnosis=diagnosis['records'],
        conclusions=[
            'Main-shaft endpoint uncertainty cannot remove either plan grip discrepancy under the retained orthographic similarity assumptions. A side-scale change alone cannot settle the two-view contradiction.',
            'The original HB148 wording does not identify endpoints for the 37-inch speed lever. HB149 explicitly says over all for the pedal and from the fulcrum centre for the clutch; HB150 specifies the hand side of the reverse fulcrum. Those neighbouring conventions make the speed-lever datum ambiguous, not resolved.',
            'The nominal 940.88 mm side main-shaft-to-cap radius suggests a functional length interpretation, but it is not a new dimension. HB113 and SNL6 repeat substantially the same control layout and are not independent engineering measurements.',
            'HB93 is a qualitative pictorial view of lateral selection. HB6 is a perspective interior photograph. Neither has a qualified metric camera here, and neither justifies stretching the handle or moving the complete driver station.',
            'Keep the mechanically checked model and failed source comparisons. Test alternative complete-stock length/profile interpretations with the fixed comparisons and front-hull constraints before fixing upper fittings. Any change to anchor identity or camera model needs separate source evidence.'
        ],
    )
    out.mkdir(parents=True)
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    draw(out, ROOT / reg['source_image'], anchors, results)
    receipt = dict(report_sha256=sha(out / 'report.json'),
                   images={'plan_uncertainty.png': sha(out / 'plan_uncertainty.png')},
                   scope='Diagnostic overlay only. Current projection unchanged; dashed disks show a hypothetical bound, not an adopted camera fit.')
    (out / 'render_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({side: {'disk_min_px': v['minimum_possible_residual_px'],
                             'square_outer_min_px': v['coordinate_square_outer_bound']['minimum_possible_residual_px']}
                      for side, v in results.items()}, indent=2))


def draw(out, image, anchors, results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from PIL import Image
    fig, ax = plt.subplots(figsize=(12, 9), dpi=150)
    ax.imshow(Image.open(image))
    for label, p in anchors.items():
        if 'main_shaft' in label:
            ax.add_patch(Circle(p, 5, fill=False, color='#08834d', linewidth=2))
    for side, r in results.items():
        p, q = r['nominal_saved_tip_px'], r['source_tip_px']
        ax.plot([p[0], q[0]], [p[1], q[1]], color='#bd3b26', linewidth=1.5)
        ax.add_patch(Circle(p, r['maximum_projected_tip_shift_px'], fill=False,
                            color='#2469ba', linewidth=2, linestyle='--'))
        ax.add_patch(Circle(q, 5, fill=False, color='#bd3b26', linewidth=2))
        ax.plot(*p, 'o', color='#2469ba')
        ax.text(145, 207 if side == 'Starboard' else 470,
                f'{side}: at least {r["minimum_possible_residual_px"]:.1f} px remains',
                fontsize=11, bbox=dict(facecolor='white', alpha=.9, edgecolor='none'))
    ax.set_xlim(20, 450)
    ax.set_ylim(495, 185)
    ax.set_title('Fixed plan comparison: endpoint uncertainty does not explain the grip discrepancy')
    ax.set_xlabel('Original SNL6 image pixels; no refit')
    ax.set_ylabel('Original SNL6 image pixels')
    fig.text(.08, .03, 'Green: shaft anchor allowances. Red: source grip picks. Blue: saved grips and exact projected uncertainty disks.\nAll allowances are 5 px disks. This is a conditional geometric bound, not a historical accuracy claim.', fontsize=10)
    fig.subplots_adjust(bottom=.12, top=.94)
    fig.savefig(out / 'plan_uncertainty.png')
    plt.close(fig)


if __name__ == '__main__':
    main()
