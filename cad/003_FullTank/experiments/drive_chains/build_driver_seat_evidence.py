"""Extract seat sources and conditional section datums without accepting geometry."""
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys

H = Path(__file__).resolve().parent
ROOT = H.parents[3]
SNL = ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project'
HB = ROOT / 'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank'
sys.path.insert(0, str(SNL))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    dependencies = {}

    def bind(path):
        dependencies[str(path.relative_to(ROOT))] = sha(path)

    bind(Path(__file__))
    rows = []
    selections = {'opening_tables': {5: [6], 17: [24]},
                  'tables_025_044': {31: [4, 8]},
                  'tables_065_084': {66: [6]},
                  'tables_145_164': {147: [11, 12]},
                  'tables_165_184': {167: [16]},
                  'tables_205_224': {207: list(range(24, 31))}}
    for module, pages in selections.items():
        path = SNL / 'data' / (module + '.py')
        bind(path)
        tables = importlib.import_module('data.' + module).TABLES
        for page, indices in pages.items():
            bind(SNL / 'sources' / f'p{page:03d}.jpg')
            for index in indices:
                rows.append(dict(source_id=f'SNL:{page:03d}:{index:03d}',
                                 path=str(path.relative_to(ROOT)), **tables[page][index - 1]))
    write(out / 'source_rows.json', rows)
    correction = dict(source_id='SNL:207:030', field='item',
                      preserved_transcription=next(r['item'] for r in rows if r['source_id'] == 'SNL:207:030'),
                      reviewed_reading='eight — RIVET, button head, ⅜″ x 1⅛″.',
                      diameter_mm=9.525, stock_length_mm=28.575, quantity=8,
                      corroborating_source='SNL:167:016',
                      basis='Direct original p207 scan reads 3/8, not transcribed 5/8. Original p167 also lists 3/8 x1-1/8 and two per SH289E bearing; four bearings give eight rivets.',
                      source_transcription_modified=False)
    write(out / 'reviewed_erratum.json', correction)
    calibration_path = H.parents[1] / 'data/calibrations.json'
    parameters_path = H.parents[1] / 'data/parameters.json'
    bind(calibration_path); bind(parameters_path)
    calibration = read(calibration_path)['snl_2']
    parameters = read(parameters_path)
    scale = [calibration['axes'][axis]['sign'] * parameters[calibration['axes'][axis]['span_parameter']]['value'] /
             abs(calibration['axes'][axis]['pixels'][1] - calibration['axes'][axis]['pixels'][0]) for axis in ['x', 'z']]
    origin = calibration['datum_pixel']
    world = lambda p: [(p[0] - origin[0]) * scale[0], (p[1] - origin[1]) * scale[1]]
    source = ROOT / calibration['image']; bind(source)
    # Construction picks, manually read from the unchanged section. These are
    # intentionally not claimed as independent validation of later fitted curves.
    picks = {
        'pan_front': dict(pixel=[439., 339.], uncertainty_px=3.),
        'pan_rear': dict(pixel=[505., 339.], uncertainty_px=3.),
        'back_lower': dict(pixel=[480., 336.], uncertainty_px=4.),
        'back_upper': dict(pixel=[511., 288.], uncertainty_px=5.),
        'front_underseat_attachment': dict(pixel=[449., 345.], uncertainty_px=4.),
        'rear_underseat_attachment': dict(pixel=[490., 345.], uncertainty_px=4.),
        'front_lower_support_joint': dict(pixel=[442., 389.], uncertainty_px=5.),
        'rear_lower_support_joint': dict(pixel=[495., 388.], uncertainty_px=5.)}
    for value in picks.values():
        value['conditional_world_xz_mm'] = world(value['pixel'])
        value['world_uncertainty_note'] = 'Pixel pick uncertainty only; source scale, drawing distortion and configuration transfer add unquantified error.'
    old_envelope = calibration['profiles']['driver_seat']
    candidate_path = H / 'driver_layout_study/trial01/report.json'
    accepted_path = H / 'transmission_controls_study/driver_redo01/operating_integrated01/report.json'
    bind(candidate_path); bind(accepted_path)
    candidate = read(candidate_path)
    accepted = read(accepted_path)
    pan_z = world(picks['pan_front']['pixel'])[1]
    datums = dict(projection='existing conditional orthographic whole-tank section; unchanged',
                  source_camera_refitted=False, independent_validation=False,
                  construction_picks=picks, old_layout_envelope_pixel=old_envelope,
                  pan_depth_estimate_mm=abs(world(picks['pan_front']['pixel'])[0] - world(picks['pan_rear']['pixel'])[0]),
                  pan_underside_height_estimate_mm=pan_z,
                  old_envelope_top_height_mm=max(world(p)[1] for p in old_envelope),
                  pan_above_old_envelope_top_mm=pan_z - max(world(p)[1] for p in old_envelope),
                  pan_above_candidate_main_shaft_mm=pan_z - candidate['details']['main_world_mm'][2],
                  width_mm=None, adjustment_axis=None, adjustment_travel_mm=None,
                  support_joint_identity='Visual picks do not establish which catalogued bearing/clip/shaft each line represents.')
    write(out / 'section_datums.json', datums)
    for path in [HB / 'original_scans/MarkVIII009.jpg', HB / 'original_scans/MarkVIII008.jpg',
                 HB / 'original_scans/MarkVIII074.jpg', HB / 'Handbook_Project/assets/plate06.png',
                 HB / 'Handbook_Project/data/body.json', HB / 'Handbook_Project/data/body_batch08.json',
                 SNL / 'assets/p281-geometry.png']:
        bind(path)
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.work/seat-evidence-20260927/matplotlib'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image
    from matplotlib.patches import Polygon
    image = Image.open(source)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=150)
    for ax in axes:
        ax.imshow(image); ax.set_xlim(420, 565); ax.set_ylim(480, 275)
        ax.set_xlabel('Fixed source X pixels'); ax.set_ylabel('Fixed source Y pixels')
    axes[0].add_patch(Polygon(old_envelope, closed=True, fill=False, edgecolor='#b83d35', linewidth=2, label='Old nonphysical seat envelope'))
    for name, value in picks.items():
        x, y = value['pixel']; axes[0].plot(x, y, 'o', color='#246a46', markersize=4)
    axes[0].set_title('Seat outline and attachment construction picks')
    axes[0].legend(loc='lower left', fontsize=8)
    for label, point, color in [('Accepted main shaft', accepted['details']['foundation']['shafts']['Main']['center_world_mm'], '#cd7331'),
                                 ('Conditional main Z975', candidate['details']['main_world_mm'], '#315e9a'),
                                 ('Conditional swing Z995', candidate['details']['swing_world_mm'], '#52799a')]:
        x = origin[0] + point[0] / scale[0]; y = origin[1] + point[2] / scale[1]
        axes[1].plot(x, y, 'o', color=color, markersize=6, label=label)
    axes[1].plot([439, 505], [339, 339], color='#246a46', label='Provisional seat underside')
    axes[1].set_title('Seat source and current shaft hypotheses'); axes[1].legend(loc='lower left', fontsize=8)
    fig.suptitle('Seat reconstruction evidence | construction picks are not independent validation')
    fig.text(.05, .025, 'Original section suggests the seat pan above the old layout box. Width, bearing form and adjustment travel remain unmeasured.\nThe Z975 driver study is conditional context; the source does not establish its historical height.', fontsize=10)
    fig.subplots_adjust(bottom=.16, top=.9, wspace=.3)
    fig.savefig(out / 'seat_section_datums.png'); plt.close(fig)
    # Lossless analytical crops of originals, with exact crop provenance.
    crop_records = []
    for page, box in [(207, (810, 710, 1745, 900)), (167, (805, 925, 1625, 1010)), (66, (890, 448, 1910, 526))]:
        path = SNL / 'sources' / f'p{page:03d}.jpg'
        file = f'p{page:03d}_seat_rows.png'
        im = Image.open(path).rotate(-90, expand=True)
        im.crop(box).save(out / file)
        crop_records.append(dict(file=file, source=str(path.relative_to(ROOT)), source_sha256=sha(path),
                                 rotation_degrees=-90, crop_after_rotation=box, output_sha256=sha(out / file)))
    write(out / 'report.json', dict(evidence_only=True, geometry_created=False,
          source_camera_refitted=False, input_hashes=dependencies, crops=crop_records,
          images={p.name: sha(p) for p in out.glob('*.png')},
          seat_parts=dict(M791=1, SH289E=4, SH291X=2, upholstering_nail_half_inch=21, bearing_rivet=8),
          additional_support_parts=dict(M786_existing=1, M787_existing=1, M788=2,
                                        M788_half_inch_bolt_41_275_mm=8, plain_nut=8, lock_washer=8),
          separate_clip_record=dict(mark='SH291C', quantity=1, printed_length_mm=88.9,
                                    rule='Separate catalogue identity. Do not apply this length or count to SH291X without evidence.'),
          observations=['SNL2 depicts a separate pan/back and two side-profile support members; four bearings are source-counted, not geometrically identified.',
                        'HB6 is an uncalibrated perspective photograph showing curved seat back and a support frame. No width or absolute height is measured from it.',
                        'HB14 gives qualitative head-in-driver-enclosure placement. HB146 describes seat and forward controls as one assembly.',
                        'Old driver_seat is layout_only and does not enclose the visible source seat; do not use it as a mounting datum or collision solid.'],
          next_action='Build M791 frame/pan/back and bearing/support interfaces as a source-labelled static prototype. Keep transverse size and support/adjustment topology explicit approximations; preserve complete printed hardware stock. Reconcile coupled shaft/seat geometry before integration.'))
    print('Seat evidence saved; original rivet correction and separate clip identities retained. No geometry promoted.')


if __name__ == '__main__':
    main()
