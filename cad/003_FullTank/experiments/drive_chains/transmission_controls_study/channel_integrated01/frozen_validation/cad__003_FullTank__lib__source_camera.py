"""Source-camera estimation with immutable fit inputs and separate holdout checks.

Coordinates are millimetres and original decoded-image pixels (x right, y down).
Perspective camera coordinates use +Z forward. A fit never changes CAD geometry.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import numpy as np
import scipy
from PIL import Image
from scipy.linalg import rq
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def arrays(observations):
    world = np.asarray([v['world_mm'] for v in observations], dtype=float)
    pixel = np.asarray([v['pixel'] for v in observations], dtype=float)
    sigma = np.asarray([v.get('sigma_px', 3.) for v in observations], dtype=float)
    if world.shape != (len(observations), 3) or pixel.shape != (len(observations), 2):
        raise ValueError('Expected world3D and image2D landmark coordinates')
    if not np.isfinite(world).all() or not np.isfinite(pixel).all() or not np.isfinite(sigma).all() or np.any(sigma <= 0):
        raise ValueError('Landmarks and positive pixel uncertainties must be finite')
    return world, pixel, sigma


def camera_points(world, camera):
    world = np.asarray(world, dtype=float)
    if camera['projection'] == 'oblique_affine':
        matrix = np.asarray(camera['matrix'])
        uv = world @ matrix[:, :3].T + matrix[:, 3]
        direction = np.cross(matrix[0, :3], matrix[1, :3])
        direction /= np.linalg.norm(direction)
        return np.column_stack([uv, world @ direction])
    return (world-np.asarray(camera['origin_world_mm'])) @ np.asarray(camera['world_to_camera_rotation']).T


def project_camera(points, camera):
    q = np.asarray(points, dtype=float)
    if camera['projection'] == 'perspective':
        if np.any(q[:, 2] <= camera.get('near_mm', .01)):
            raise ValueError('Camera has landmarks/geometry behind or across its near plane')
        uv = q[:, :2] * (camera['focal_px']/q[:, 2, None]) + camera['principal_px']
        depth = 1/q[:, 2]
    elif camera['projection'] == 'orthographic':
        uv = q[:, :2]*camera['scale_px_per_mm'] + camera['principal_px']
        depth = -q[:, 2]
    elif camera['projection'] == 'oblique_affine':
        uv, depth = q[:, :2], -q[:, 2]
    else:
        raise ValueError('Unsupported projection')
    return np.column_stack([uv, depth])


def project(world, camera):
    return project_camera(camera_points(world, camera), camera)


def perspective_initial(world, pixel):
    # Normalized DLT is initialization only; the final fit constrains a proper
    # rotation and square pixels. Scan anisotropy is not hidden in focal ratios.
    center = world.mean(axis=0)
    scale = np.sqrt(3)/np.sqrt(np.mean(np.sum((world-center)**2, axis=1)))
    wp = (world-center)*scale
    pc = pixel.mean(axis=0)
    ps = np.sqrt(2)/np.sqrt(np.mean(np.sum((pixel-pc)**2, axis=1)))
    pp = (pixel-pc)*ps
    A = []
    for point, (u, v) in zip(wp, pp):
        X = np.r_[point, 1.]
        A.extend([np.r_[X, np.zeros(4), -u*X], np.r_[np.zeros(4), X, -v*X]])
    _, singular, vt = np.linalg.svd(A)
    if singular[-2] < singular[0]*1e-8:
        raise ValueError('Perspective landmark system is degenerate')
    T3 = np.eye(4); T3[:3, :3] *= scale; T3[:3, 3] = -center*scale
    T2 = np.array([[ps, 0, -pc[0]*ps], [0, ps, -pc[1]*ps], [0, 0, 1.]])
    P = np.linalg.solve(T2, vt[-1].reshape(3, 4)) @ T3
    if np.linalg.det(P[:, :3]) < 0: P = -P
    K, R = rq(P[:, :3])
    signs = np.diag(np.where(np.diag(K) < 0, -1., 1.))
    K, R = K @ signs, signs @ R
    K /= K[2, 2]
    origin = -np.linalg.solve(P[:, :3], P[:, 3])
    focal = (K[0, 0]+K[1, 1])/2
    if focal <= 0 or np.linalg.det(R) < .999:
        raise ValueError('DLT did not yield a physical starting camera')
    return R, origin, focal, K[:2, 2]


def fit(packet):
    observations = [v for v in packet['landmarks'] if v['use'] == 'fit']
    world, pixel, sigma = arrays(observations)
    projection = packet['projection']
    if len(observations) < 8:
        raise ValueError('Use at least 8 distributed fitting landmarks plus independent holdouts')
    singular = np.linalg.svd(world-world.mean(axis=0), compute_uv=False)
    if singular[-1] < singular[0]*1e-3:
        raise ValueError('Landmarks are planar or nearly planar; camera depth is not sufficiently constrained')
    if projection == 'oblique_affine':
        X = np.column_stack([world, np.ones(len(world))])
        matrix = np.linalg.lstsq(X/sigma[:, None], pixel/sigma[:, None], rcond=None)[0].T
        if np.linalg.norm(np.cross(matrix[0, :3], matrix[1, :3])) < 1e-12:
            raise ValueError('Degenerate oblique projection')
        return dict(projection=projection, matrix=matrix.tolist(),
                    image_size_px=packet['image_size_px'], fit_method='weighted affine least squares',
                    physical_perspective_camera=False)
    center = world.mean(axis=0)
    span = np.linalg.norm(np.ptp(world, axis=0))
    width, height = packet['image_size_px']
    if projection == 'perspective':
        R, origin, focal, principal = perspective_initial(world, pixel)
        x0 = np.r_[Rotation.from_matrix(R).as_rotvec(), (origin-center)/span, np.log(focal), principal/np.array([width, height])]
        def decode(x):
            return dict(projection=projection, world_to_camera_rotation=Rotation.from_rotvec(x[:3]).as_matrix().tolist(),
                origin_world_mm=(center+span*x[3:6]).tolist(), focal_px=float(np.exp(x[6])),
                principal_px=(x[7:9]*[width, height]).tolist(), near_mm=.01,
                image_size_px=packet['image_size_px'])
        lower = np.r_[[-np.inf]*6, np.log(max(width, height)*.1), [-1., -1.]]
        upper = np.r_[[np.inf]*6, np.log(max(width, height)*100.), [2., 2.]]
        if np.any(x0 <= lower) or np.any(x0 >= upper):
            raise ValueError('Starting camera outside broad optical/crop bounds; review landmarks/projection')
    elif projection == 'orthographic':
        X = np.column_stack([world-center, np.ones(len(world))])
        affine = np.linalg.lstsq(X, pixel, rcond=None)[0].T
        u, _, vt = np.linalg.svd(affine[:, :3], full_matrices=False)
        rows = u @ vt
        R = np.vstack([rows, np.cross(rows[0], rows[1])])
        scale = np.linalg.norm(affine[:, :3], axis=1).mean()
        x0 = np.r_[Rotation.from_matrix(R).as_rotvec(), np.log(scale), affine[:, 3]]
        def decode(x):
            return dict(projection=projection, world_to_camera_rotation=Rotation.from_rotvec(x[:3]).as_matrix().tolist(),
                origin_world_mm=center.tolist(), scale_px_per_mm=float(np.exp(x[3])),
                principal_px=x[4:6].tolist(), image_size_px=packet['image_size_px'])
        lower, upper = -np.inf, np.inf
    else:
        raise ValueError('Choose perspective, orthographic or oblique_affine explicitly')
    def residual(x):
        camera = decode(x)
        q = camera_points(world, camera)
        if projection == 'perspective':
            # Keep optimization finite at the invalid side of the focal plane;
            # the final solution must pass strict positive-depth checks.
            z = np.maximum(q[:, 2], .01)
            uv = q[:, :2]*(camera['focal_px']/z[:, None])+camera['principal_px']
        else:
            uv = project_camera(q, camera)[:, :2]
        return ((uv-pixel)/sigma[:, None]).ravel()
    solution = least_squares(residual, x0, bounds=(lower, upper), loss='soft_l1',
                             x_scale='jac', max_nfev=3000, ftol=1e-12, xtol=1e-12, gtol=1e-12)
    camera = decode(solution.x)
    project(world, camera)
    if not solution.success:
        raise ValueError('Camera optimizer did not converge: '+solution.message)
    jsv = np.linalg.svd(solution.jac, compute_uv=False)
    camera.update(fit_method='constrained robust least squares; no CAD changes',
                  function_evaluations=solution.nfev, jacobian_condition=float(jsv[0]/max(jsv[-1], 1e-30)),
                  parameter_at_bound=bool(np.any(solution.active_mask)),
                  physical_perspective_camera=projection == 'perspective')
    return camera


def assess(camera, observations):
    result = {}
    for use in ('fit', 'holdout'):
        subset = [v for v in observations if v['use'] == use]
        if not subset:
            result[use] = dict(count=0, status='missing'); continue
        world, pixel, sigma = arrays(subset)
        predicted = project(world, camera)[:, :2]
        errors = np.linalg.norm(predicted-pixel, axis=1)
        result[use] = dict(count=len(subset), rms_px=float(np.sqrt(np.mean(errors**2))),
            max_px=float(errors.max()), normalized_max=float((errors/sigma).max()),
            residuals=[dict(id=row['id'], predicted_px=uv.tolist(), error_px=float(error),
                            uncertainty_px=float(s)) for row, uv, error, s in zip(subset, predicted, errors, sigma)])
    result['review_required'] = True
    result['holdout_consistent_with_pick_uncertainty'] = result['holdout']['count'] >= 3 and result['holdout']['normalized_max'] <= 3
    result['fit_consistent_with_pick_uncertainty'] = result['fit']['count'] >= 8 and result['fit']['normalized_max'] <= 3
    # A diagnostic threshold, not an uncertainty interval or accuracy guarantee.
    result['weak_numerical_constraint'] = camera.get('jacobian_condition', 0) > 1e6 or camera.get('parameter_at_bound', False)
    return result


def cached_fit(packet, cache):
    """New holdouts/new non-anchor geometry reassess a fixed camera, not refit it."""
    ids = [v['id'] for v in packet['landmarks']]
    if len(set(ids)) != len(ids) or any(v['use'] not in ('fit', 'holdout') for v in packet['landmarks']):
        raise ValueError('Unique landmark IDs and explicit fit/holdout roles required')
    source = Path(packet['source_image'])
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != packet['source_sha256']:
        raise ValueError('Source image changed; reverify pixel picks before refitting')
    with Image.open(source) as source_bitmap:
        if list(source_bitmap.size) != packet['image_size_px']:
            raise ValueError('Pixel picks must use the original decoded image dimensions')
    arrays(packet['landmarks'])
    identity = dict(source_sha256=source_hash, image_size_px=packet['image_size_px'], projection=packet['projection'],
        fit_landmarks=[{k: v[k] for k in ('id', 'world_mm', 'pixel', 'sigma_px')} for v in packet['landmarks'] if v['use'] == 'fit'],
        camera_assumptions=packet.get('camera_assumptions', {}),
        fitter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        numpy_version=np.__version__, scipy_version=scipy.__version__)
    key = digest(identity)
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True)
    path = cache/(key+'.json')
    reused = path.exists()
    started = time.perf_counter()
    previous = packet.get('previous_fit_key')
    if previous and previous != key:
        if len(previous) != 64 or any(c not in '0123456789abcdef' for c in previous):
            raise ValueError('Invalid previous camera key')
        old = json.loads((cache/(previous+'.json')).read_text())
        if digest(old['identity']) != previous or digest(old['camera']) != old['camera_sha256']:
            raise ValueError('Previous camera record changed')
        if not packet.get('refit_review', {}).get('reason') or not packet['refit_review'].get('reviewer'):
            raise ValueError('Changed fit inputs require a recorded refit reason and reviewer')
    if reused:
        record = json.loads(path.read_text())
        if record['identity'] != identity or digest(record['camera']) != record['camera_sha256']:
            raise ValueError('Cached camera record changed')
        camera = record['camera']
    else:
        camera = fit(packet)
        record = dict(identity=identity, camera=camera, camera_sha256=digest(camera),
                      fit_seconds=time.perf_counter()-started)
        # Atomic, exclusive publication: interrupted writes cannot become fits.
        fd, temporary = tempfile.mkstemp(prefix='.fit-', dir=cache)
        try:
            with os.fdopen(fd, 'w') as stream: json.dump(record, stream, indent=2, allow_nan=False)
            try: os.link(temporary, path)
            except FileExistsError:
                concurrent = json.loads(path.read_text())
                if concurrent['identity'] != identity or concurrent['camera_sha256'] != digest(camera):
                    raise ValueError('Concurrent fit differs; review before reuse')
        finally:
            Path(temporary).unlink()
    assessment = assess(camera, packet['landmarks'])
    issues = []
    if not assessment['holdout_consistent_with_pick_uncertainty']: issues.append('holdout_missing_or_conflicting')
    if not assessment['fit_consistent_with_pick_uncertainty']: issues.append('fitting_residuals_exceed_uncertainty')
    if assessment['weak_numerical_constraint']: issues.append('weak_or_bound_limited_camera')
    return dict(fit_key=key, reused=reused, camera=camera, assessment=assessment,
                fit_record=str(path), geometry_context=packet.get('geometry_context'),
                previous_fit_key=packet.get('previous_fit_key'), refit_review=packet.get('refit_review'),
                camera_sha256=digest(camera), original_fit_seconds=record['fit_seconds'],
                current_evaluation_seconds=time.perf_counter()-started, issues=issues,
                policy='Holdout contradictions require review; never auto-refit by silently turning validation points into fitting points.',
                status='camera_review_required' if not issues else 'evidence_review_needed')
