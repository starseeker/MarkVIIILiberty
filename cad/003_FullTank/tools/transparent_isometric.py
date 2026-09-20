"""Render the saved assembly with a translucent armor shell, without resaving CAD.

Use after a standard build: python3 cad/003_FullTank/tools/transparent_isometric.py
The closest armor surface is one display layer. This CAD inspection treatment
keeps overlapping armor from accumulating opacity and obscuring the interior.
"""
import argparse
import base64
import io
from pathlib import Path
import subprocess
import sys

import numpy as np

STAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE))
from lib import runtime
from lib.evidence import sha, write, fingerprint
from lib.raster import paint


def composite(opaque, opaque_depth, shell, shell_depth, opacity):
    if not 0 <= opacity <= 1:
        raise ValueError('Armor opacity must be between zero and one')
    result = opaque.copy()
    front = np.isfinite(shell_depth) & (shell_depth > opaque_depth)
    result[front] = np.rint((1 - opacity) * opaque[front] + opacity * shell[front]).astype(np.uint8)
    return result


def render(items, out, opacity):
    import FreeCAD as App
    import fitz
    from PIL import Image
    from lib.cad_build import COLORS

    direction = App.Vector(1, 1, .6); direction.normalize()
    right = App.Vector(0, 0, 1).cross(direction); right.normalize()
    up = direction.cross(right); up.normalize()
    camera = np.array([[right.x, -up.x, direction.x], [right.y, -up.y, direction.y], [right.z, -up.z, direction.z]])
    omitted = {'track_pin', 'track_bushing', 'track_cotter', 'track_rivet'}
    context = {'central_hull', 'track_frame', 'track_path'}
    selected = [i for i in items if i['definition'] not in omitted]
    bounds = App.BoundBox()
    for item in selected:
        bounds.add(item['shape'].BoundBox)
    deflection = max(.6, bounds.DiagonalLength / 2500)
    batches = {False: [], True: []}; edges = {False: [], True: []}
    coords = []; cache = {}; translucent = []
    for item in selected:
        if item['definition'] in context or not item['shape'].Faces:
            for edge in item['shape'].Edges:
                coords.extend((v.dot(right), -v.dot(up)) for v in edge.discretize(Deflection=2.0))
            continue
        shell = item['system'] in {'HullStructure', 'Sponsons'} and item['representation'] == 'assembly'
        if shell:
            translucent.append(item['id'])
        target = item['target'].Shape
        key = item['definition']
        if key not in cache:
            vertices, indices = target.tessellate(deflection)
            local = np.array([[v.x, v.y, v.z] for v in vertices])
            indices = np.array(indices, dtype=np.int32)
            cells = local[indices]
            normals = np.cross(cells[:, 1] - cells[:, 0], cells[:, 2] - cells[:, 0])
            lengths = np.linalg.norm(normals, axis=1)
            valid = lengths > 1e-12
            lines = [np.array([[v.x, v.y, v.z] for v in e.discretize(Deflection=deflection)])
                     for e in target.Edges] if item['representation'] == 'assembly' else []
            cache[key] = local, indices[valid], normals[valid] / lengths[valid, None], lines
        local, indices, normals, lines = cache[key]
        transform = item['shape'].Placement.multiply(target.Placement.inverse())
        m = transform.toMatrix()
        rotation = np.array([[m.A11,m.A12,m.A13],[m.A21,m.A22,m.A23],[m.A31,m.A32,m.A33]])
        translation = np.array([m.A14, m.A24, m.A34])
        projected = (local @ rotation.T + translation) @ camera
        expected = transform.multVec(App.Vector(*local[0]))
        assert np.linalg.norm(local[0] @ rotation.T + translation - [expected.x, expected.y, expected.z]) < 1e-7
        color = COLORS[item['system']]
        if item['representation'] == 'assembly' and key.startswith('track_'):
            color = (.43,.47,.42) if key == 'track_shoe' else (.64,.66,.61)
        light = .58 + .37 * np.abs(normals @ (rotation.T @ np.array([.3,-.5,.8])))
        rgb = np.clip(light[:, None] * np.array(color)[None, :] * 255, 0, 255).astype(np.uint8)
        batches[shell].append((projected[indices], rgb))
        coords.extend([(projected[:,0].min(), projected[:,1].min()), (projected[:,0].max(), projected[:,1].max())])
        edges[shell].extend((line @ rotation.T + translation) @ camera for line in lines)
    width, height = 1600, 900
    xmin, ymin = np.min(coords, axis=0); xmax, ymax = np.max(coords, axis=0)
    scale = min((width-100)/max(xmax-xmin,1), (height-150)/max(ymax-ymin,1))
    def screen(points):
        result = points.copy()
        result[...,0] = (width-(xmax-xmin)*scale)/2 + (result[...,0]-xmin)*scale
        result[...,1] = 100 + (result[...,1]-ymin)*scale
        return result
    layers = {}
    for shell in (False, True):
        cells = screen(np.concatenate([b[0] for b in batches[shell]]))
        colors = np.concatenate([b[1] for b in batches[shell]])
        pixels, depth = paint(cells, colors, width, height, out/'runtime')
        for line in edges[shell]:
            line = screen(line)
            for a,b in zip(line, line[1:]):
                steps = max(2, int(np.max(np.abs(b[:2]-a[:2])))+2)
                sampled = a + (b-a)*np.linspace(0,1,steps)[:,None]
                xx,yy = np.rint(sampled[:,:2]).astype(int).T
                valid = (xx>=0)&(xx<width)&(yy>=0)&(yy<height)
                xx,yy,z = xx[valid],yy[valid],sampled[valid,2]
                seen = z >= depth[yy,xx]-1.5/scale
                pixels[yy[seen],xx[seen]] = (48,54,47)
        layers[shell] = pixels, depth
    pixels = composite(*layers[False], *layers[True], opacity)
    bitmap = io.BytesIO(); Image.fromarray(pixels).save(bitmap, format='PNG')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900">'
           f'<image width="1600" height="900" href="data:image/png;base64,{base64.b64encode(bitmap.getvalue()).decode()}"/>'
           '<text x="40" y="36" font-family="sans-serif" font-size="24">Mark VIII | transparent hull inspection</text>'
           f'<text x="40" y="65" font-family="sans-serif" font-size="16">Armor {opacity:.0%} opacity · interior layout envelopes remain provisional</text></svg>')
    path = out/'previews/isometric_transparent.svg'; path.write_text(svg)
    with fitz.open(stream=svg.encode(), filetype='svg') as doc:
        doc[0].get_pixmap().save(str(path.with_suffix('.png')))
    return dict(armor_opacity=opacity, method='nearest armor display layer composited against opaque depth buffer',
                translucent_occurrences=translucent, opaque_interior_and_running_gear=True,
                omitted_small_track_hardware=sorted(omitted), camera_direction=[1,1,.6],
                projected_extents=[float(v) for v in [xmin,xmax,ymin,ymax]],
                canvas=[width,height], native_geometry_changed=False,
                output_sha256={str(p.relative_to(out)):sha(p) for p in [path,path.with_suffix('.png')]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=STAGE/'build')
    parser.add_argument('--opacity', type=float, default=.18)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args(); out = args.output.resolve()
    if not 0 <= args.opacity <= 1:
        parser.error('opacity must be between zero and one')
    if not args.worker:
        folder = out/'runtime/transparent_isometric'; folder.mkdir(parents=True, exist_ok=True)
        with (folder/'run.log').open('w') as log:
            return subprocess.run([sys.executable,__file__,'--worker','--output',str(out),'--opacity',str(args.opacity)],
                                  env=runtime.environment(out), stdout=log, stderr=subprocess.STDOUT).returncode
    try:
        App, Gui = runtime.start_gui()
        from lib.worker import check_build
        from lib.cad_build import leaves
        report = check_build(out)
        doc = App.openDocument(str(out/'native/MarkVIII.FCStd')); doc.recompute()
        result = render(leaves(doc.Root), out, args.opacity)
        assert check_build(out)['native_hashes'] == report['native_hashes']
        result.update(authored_fingerprint=fingerprint(), native_hashes=report['native_hashes'],
                      renderer_sha256=sha(Path(__file__)), passed=True)
        write(out/'reports/transparent_isometric.json', result)
        print('PASS: transparent isometric saved; all native hashes unchanged.', flush=True)
        return 0
    finally:
        runtime.close()


if __name__ == '__main__':
    sys.exit(main())
