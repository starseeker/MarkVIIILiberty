"""Review section landmark identity and full-stock closure; no camera fitting."""
import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
F = H / 'transmission_controls_study/driver_redo01'
SNL = ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project'
HB = ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    out = p.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    dependencies = {}

    def bind(path):
        dependencies[str(path.relative_to(ROOT))] = sha(path)
        return path

    bind(Path(__file__))
    sys.path.insert(0, str(SNL))
    rows = []
    for module, page, index in [('tables_025_044', 35, 32), ('tables_105_124', 118, 12),
                                ('tables_185_204', 194, 26), ('tables_205_224', 207, 24),
                                ('tables_245_264', 263, 6)]:
        bind(SNL / 'data' / (module + '.py'))
        bind(SNL / 'sources' / f'p{page:03d}.jpg')
        row = importlib.import_module('data.' + module).TABLES[page][index - 1]
        rows.append(dict(source_id=f'SNL:{page:03d}:{index:03d}', **row))
    write(out / 'catalogue_rows.json', rows)
    cal = read(bind(H.parents[1] / 'data/calibrations.json'))['snl_2']
    params = read(bind(H.parents[1] / 'data/parameters.json'))
    scale = [cal['axes'][a]['sign'] * params[cal['axes'][a]['span_parameter']]['value'] /
             abs(cal['axes'][a]['pixels'][1] - cal['axes'][a]['pixels'][0]) for a in ['x', 'z']]
    datum = cal['datum_pixel']
    world = lambda xy: [(xy[i] - datum[i]) * scale[i] for i in range(2)]
    pixel = lambda xz: [datum[i] + xz[i] / scale[i] for i in range(2)]
    picks = {
        'possible_main_shaft_end': dict(pixel=[477., 428.], uncertainty_px=5.,
            identity='Conditional: forward exposed round/hexagonal feature in side plate; no direct piece-mark leader.'),
        'possible_swing_shaft_end': dict(pixel=[545., 425.], uncertainty_px=5.,
            identity='Conditional: aft exposed round/hexagonal feature; paired spacing and relative height are consistent with the two shafts.'),
        'forward_lever_emergence': dict(pixel=[443., 399.], uncertainty_px=5.,
            identity='Visible control/plate-edge region. Occluded continuation does not establish the main shaft center.'),
        'tool_box_56_leader_tip': dict(pixel=[511., 380.], uncertainty_px=5.,
            identity='Leader ends at the horizontal box region behind the seat; the printed number lies lower inside a different outline.')}
    for row in picks.values():
        row['conditional_world_xz_mm'] = world(row['pixel'])
        assert max(abs(a-b) for a,b in zip(pixel(world(row['pixel'])), row['pixel'])) < 1e-9
    layout = read(bind(H / 'driver_layout_study/trial01/report.json'))
    old = read(bind(F / 'operating_integrated01/report.json'))
    reg = read(bind(F / 'mount_registration01.json'))
    for path in [H / 'driver_layout_study/source_review.json',
                 H / 'driver_layout_study/trial01/visual02/visual_review.json',
                 H / 'driver_seat_support_study/source_visibility01/source_review.json',
                 F / 'handle_datum_review01/report.json',
                 F / 'handle_profiles01/comparison02/visual_review.json',
                 ROOT / 'cad/001_Survey/inputs/figure_index.json']:
        bind(path)
    target = picks['possible_main_shaft_end']['conditional_world_xz_mm']
    target_main = [target[0], 0., target[1]]
    old_main = old['details']['foundation']['shafts']['Main']['center_world_mm']
    old_swing = old['details']['foundation']['shafts']['Swing']['center_world_mm']
    unit_delta = [target_main[i] - old_main[i] for i in range(3)]
    target_swing = [old_swing[i] + unit_delta[i] for i in range(3)]
    predicted_swing = pixel([target_swing[0], target_swing[2]])
    observed_swing = picks['possible_swing_shaft_end']['pixel']
    shaft_record = dict(main_construction_world_mm=target_main,
        swing_prediction_world_mm=target_swing, swing_prediction_pixel=predicted_swing,
        swing_residual_px=math.dist(predicted_swing, observed_swing),
        inherited_separation_mm=reg['shaft_separation_mm'],
        observed_section_separation_mm=target[0]-world(observed_swing)[0],
        observed_section_height_difference_mm=world(observed_swing)[1]-target[1],
        main_pick_used_for_construction=True, swing_pick_used_for_construction=False,
        independent_validation=False,
        limit='Paired-feature identity hypothesis. Small spacing residual supports consistency, not proven shaft identity or absolute accuracy.')
    # Reuse the actual retained fork-to-pin offsets and the complete printed rod.
    # Solve the rear receiver X; do not shorten M574 to reach a selected station.
    closure = {}
    for side in ['Port', 'Starboard']:
        ends = old['details']['low_speed'][side]['endpoints']
        fixed = ends[0]['pin_world_mm']
        driver = [ends[1]['pin_world_mm'][i] + unit_delta[i] for i in range(3)]
        span = 1257.3 + 2 * 25.4
        dx = math.sqrt(span**2 - (driver[1]-fixed[1])**2 - (driver[2]-fixed[2])**2)
        needed = [driver[0]-dx, fixed[1], fixed[2]]
        closure[side] = dict(printed_core_mm=1257.3, estimated_end_offsets_mm=[25.4,25.4],
            required_pin_span_mm=span, actual_fixed_receiver_mm=fixed,
            hypothetical_driver_pin_mm=driver, fixed_receiver_pin_distance_mm=math.dist(driver,fixed),
            core_shortfall_if_fixed_mm=span-math.dist(driver,fixed),
            required_receiver_world_mm=needed, required_receiver_x_shift_mm=needed[0]-fixed[0],
            solved_span_error_mm=abs(math.dist(driver,needed)-span))
        assert closure[side]['solved_span_error_mm'] < 1e-7
    source = bind(ROOT / cal['image'])
    for name in ['plate02.png', 'plate06.png', 'plate113.png']:
        bind(HB / 'assets' / name)
    bind(SNL / 'assets/p280-geometry.png')
    bind(SNL / 'assets/p281-geometry.png')
    bind(SNL / 'sources/p277_foldout.jpg')
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.work/driver-visibility-20260927/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    im = Image.open(source).convert('RGB')
    fig, axes = plt.subplots(1,2,figsize=(14,7),dpi=150)
    for ax in axes:
        ax.imshow(im); ax.set_xlim(355,575); ax.set_ylim(485,275); ax.set_aspect('equal')
        ax.set_xlabel('Unchanged SNL2 X pixels'); ax.set_ylabel('Unchanged SNL2 Y pixels')
    axes[0].set_title('Leader endpoints and occluding side-plate region')
    for name, label, xytext, color in [
        ('tool_box_56_leader_tip', '56: horizontal tool-box region', (360,285), '#674597'),
        ('forward_lever_emergence', 'Lever emergence: shaft identity unproven', (355,465), '#ad6537')]:
        xy=picks[name]['pixel']; axes[0].plot(*xy,'o',color=color)
        axes[0].annotate(label,xy,xytext=xytext,fontsize=8,color=color,arrowprops=dict(arrowstyle='->',color=color))
    for name, row in picks.items():
        if name.startswith('possible_'):
            axes[0].plot(*row['pixel'],'o',mfc='none',mec='#166b46',ms=11)
    axes[0].text(361,477,'Green rings: possible shaft ends, not labelled proof',fontsize=8,color='#166b46')
    axes[1].set_title('Test the two-feature hypothesis before moving geometry')
    for key in ['main_world_mm','swing_world_mm']:
        q=layout['details'][key]; axes[1].plot(*pixel([q[0],q[2]]),'o',color='#2458a8')
    for name in ['possible_main_shaft_end','possible_swing_shaft_end']:
        xy=picks[name]['pixel'];axes[1].errorbar(*xy,xerr=5,yerr=5,fmt='o',color='#166b46',ms=4)
    axes[1].plot(*predicted_swing,'+',color='#c63e35',ms=10)
    axes[1].text(360,473,'Blue: saved Z975 trial; green: tentative source pair\nRed +: inherited shaft spacing from the main pick',fontsize=8)
    fig.suptitle('Driver station identity review | fixed calibration, no camera refit')
    fig.text(.04,.015,'Five-pixel bars express pick ambiguity only. Projection, drawing accuracy and feature identity add unquantified uncertainty.',fontsize=9)
    fig.tight_layout(rect=(0,.055,1,.94)); fig.savefig(out/'landmark_review.png');plt.close(fig)
    hb2=Image.open(HB/'assets/plate02.png').rotate(-90,expand=True)
    hb2.crop((200,200,680,550)).save(out/'hb2_driver_detail.png')
    report=dict(input_hashes=dependencies,source_camera_refitted=False,geometry_modified=False,
        landmarks=picks,shaft_pair=shaft_record,full_stock_closure=closure,
        delta_from_Z975_trial_mm=[target_main[i]-layout['details']['main_world_mm'][i] for i in range(3)],
        crop=dict(source=str((HB/'assets/plate02.png').relative_to(ROOT)),rotation_degrees=-90,
                  crop_after_rotation=[200,200,680,550],resampling=False),
        findings=[
            'Catalogue callout56 identifies the left6-pdr tool box. Its leader ends above the sloping side-plate outline; the number position does not identify that whole outline as the box.',
            'HB2 shows the control blades disappearing behind a near side plate and two exposed fastener ends in that plate. HB2/SNL2 may share a drawing lineage and are not independent metric corroboration.',
            'The earlier statement that the main shaft is below the depicted joint lacked a named source feature. It cannot be retained as a positively identified shaft-height failure. This does not establish the current station as correct.',
            'The forward lever/edge region is not safely a main-shaft center. The two exposed side-plate ends offer a more coherent, still conditional shaft-pair hypothesis.',
            'The paired ends suggest a primarily aft station change, not a 185mm shaft rise. Complete M574 stock then conflicts with the currently fixed intermediate receivers; its calculated required receiver change must propagate through the real rods and mounting geometry.',
            'HB6 is an uncalibrated perspective photograph. It confirms overlapping controls and a central seat qualitatively; no metric camera fit or absolute shaft coordinate is claimed.',
            'SNL6/HB113 remain schematic local control drawings with broken long rods. Their existing grip discrepancies survive any rigid translation of the whole driver unit; they must be tested separately from absolute station.',
            'SNL7 armor view adds no positive driver shaft-end identity. Callouts47/49 remain without positive catalogue correspondence in the reviewed table search.'
        ],
        next_action='Test the four complete saved handle profiles at this tentative station against the corrected bow and unchanged seat. Preserve full M574 stock and explicitly solve the coupled intermediate/driver mounting revision before integration.',
        images={p.name:sha(p) for p in out.glob('*.png')})
    write(out/'report.json',report)
    print(json.dumps(dict(shaft_pair=shaft_record,delta=report['delta_from_Z975_trial_mm'],closure=closure),indent=2))


if __name__ == '__main__':
    main()
