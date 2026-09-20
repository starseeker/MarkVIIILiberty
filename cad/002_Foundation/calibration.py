"""Conditional metric calibration and explicit nonmetric photographic references."""
import html
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

from evidence import REPO, write


def metric(entry, values):
    axes = {}
    for axis, specification in entry['axes'].items():
        a, b = specification['pixels']
        if a == b:
            raise ValueError('Coincident calibration control points')
        axes[axis] = specification['sign'] * values[specification['span_parameter']] / abs(b - a)
    return axes


def point(entry, values, pixel):
    scales = metric(entry, values)
    return [(pixel[0] - entry['datum_pixel'][0]) * scales['x'],
            (pixel[1] - entry['datum_pixel'][1]) * scales['z']]


def run(data, out):
    folder = Path(out) / 'calibration'
    folder.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, entry in data['calibrations'].items():
        with Image.open(REPO / entry['image']) as src:
            image = src.convert('RGB')
        crop = entry['crop']
        if crop[2] > image.width or crop[3] > image.height:
            raise ValueError(f'{name}: crop exceeds image dimensions {image.size}')
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        record = {'mode': entry['mode'], 'note': entry['note'], 'image_dimensions': list(image.size),
                  'crop': crop, 'original': entry['original'], 'image': entry['image'],
                  'prior_transform_document': entry['prior_transform_document'], 'checks': []}
        if entry['mode'] == 'conditional_metric':
            axes = metric(entry, data['values'])
            record['mm_per_pixel'] = axes
            record['datum_pixel'] = entry['datum_pixel']
            record['affine_pixel_to_xz'] = [[axes['x'], 0, -axes['x'] * entry['datum_pixel'][0]],
                                          [0, axes['z'], -axes['z'] * entry['datum_pixel'][1]]]
            for axis, spec in entry['axes'].items():
                for value in spec['pixels']:
                    ends = [(value, 0), (value, image.height)] if axis == 'x' else [(0, value), (image.width, value)]
                    draw.line(ends, fill='#bb233a', width=2)
            for item in entry['checks']:
                measured = abs(item['pixels'][1] - item['pixels'][0]) * abs(axes[item['axis']])
                target = data['values'][item['parameter']]
                uncertainty = 2 * entry['point_uncertainty_px'] * abs(axes[item['axis']])
                result = dict(item, measured_mm=measured, reference_mm=target,
                              residual_mm=measured - target, picking_uncertainty_mm=uncertainty,
                              within_picking_uncertainty=abs(measured - target) <= uncertainty)
                record['checks'].append(result)
            for label, points in entry.get('profiles', {}).items():
                draw.line([tuple(p) for p in points + [points[0]]], fill='#006aab', width=3)
            for label, pixel in entry.get('axes_pixels', {}).items():
                x, y = pixel
                draw.ellipse((x-5, y-5, x+5, y+5), outline='#007a54', width=3)
                draw.text((x+8, y), label, fill='#007a54')
            # Transform retained as a metric SVG viewport embedding unchanged source pixels.
            import base64
            raw = (REPO / entry['image']).read_bytes()
            mm_w, mm_h = image.width * abs(axes['x']), image.height * abs(axes['z'])
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                   f'width="{mm_w}mm" height="{mm_h}mm" viewBox="0 0 {image.width} {image.height}" '
                   'preserveAspectRatio="none">'
                   f'<title>{html.escape(name)}: conditional scale, not a manufacturing drawing</title>'
                   f'<image width="{image.width}" height="{image.height}" xlink:href="data:image/png;base64,'
                   + base64.b64encode(raw).decode() + '"/></svg>')
            (folder / (name + '_metric.svg')).write_text(svg)
        else:
            record['metric_transform'] = None
            record['limitation'] = 'Perspective photograph: deliberately not assigned mm/pixel.'
        image.crop(crop).save(folder / (name + '_reference.png'))
        overlay.crop(crop).save(folder / (name + '_overlay.png'))
        report[name] = record
    write(folder / 'calibration_report.json', report)
    lines = ['# Calibration and visual references', '',
             'Red lines: fitting spans. Blue: authored blockout profiles. Green: wheel axes.',
             'Scaling is conditional on handbook-to-production applicability; no new historical precision is claimed.', '']
    for name, record in report.items():
        lines += [f'## {name}: {record["mode"]}', '', record['note'], '',
                  f'![{name}]({name}_overlay.png)', '']
        for c in record['checks']:
            lines.append(f'- {c["label"]}: residual {c["residual_mm"]:.2f} mm; '
                         f'point-picking allowance ±{c["picking_uncertainty_mm"]:.2f} mm. '
                         + ('Within picking allowance.' if c['within_picking_uncertainty'] else
                            'Disagreement retained; use printed dimensions for the part.'))
        lines.append('')
    (folder / 'README.md').write_text('\n'.join(lines))
    return report
