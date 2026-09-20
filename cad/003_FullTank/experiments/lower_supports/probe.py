"""Native lower-support installation experiment; delivered model remains read-only.

Run with system python3. Outputs go to this experiment's build directory by
default, or --out PATH. Source identities/counts are known; station allocation,
contours, stock, tapped attachment and fastener head envelopes are hypotheses.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
sys.path.insert(0, str(STAGE))

RUNS = [
    ('01', list(range(0, 2)), 'M2078', 'M2078', 1),
    ('02', list(range(2, 4)), 'M2079', 'M2079', 1),
    ('03', list(range(4, 6)), 'M2080', 'M2080', 1),
    ('04', list(range(6, 12)), 'M2081B', 'M2081A', 4),
    ('05', list(range(12, 16)), 'M2082B', 'M2082A', 4),
    ('06', list(range(16, 18)), 'M2083B', 'M2083A', 3),
    ('07', list(range(18, 23)), 'M2084B', 'M2084A', 3),
    ('08', list(range(23, 29)), 'M2085', 'M2085', 2),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--out', type=Path, default=HERE / 'build')
    args = parser.parse_args()
    from lib.runtime import environment, start_gui, close
    if not args.worker:
        return subprocess.run([sys.executable, __file__, '--worker', '--out', str(args.out)],
                              env=environment(args.out)).returncode
    App, _ = start_gui()
    try:
        worker(App, args.out)
    finally:
        close()
    return 0


def worker(App, out):
    import Part
    import Sketcher
    import numpy as np
    from lib.model import load
    from lib.evidence import database, fingerprint, sha, write, read
    from lib.roller_geometry import stations, values
    from lib.roller_validation import bearing_face
    from lib.cad_build import frame, pad
    from lib.track_parts import feature
    from lib.visual_review import shaded

    out.mkdir(parents=True, exist_ok=True)
    data = load()
    baseline = read(STAGE / 'build/reports/build.json')
    if baseline['fingerprint'] != fingerprint():
        raise ValueError('Authored inputs differ from the native baseline; rebuild before probing')
    v = values(data)
    st = stations(data)
    V = App.Vector
    doc = App.newDocument('LowerSupportInstallationExperiment')
    root = doc.addObject('App::Part', 'SupportExperiment')
    root.addProperty('App::PropertyString', 'Status')
    root.Status = 'Unqualified experiment; not part of the delivered tank'
    items = []
    libraries = {}
    for system in ['RunningGear', 'HullStructure']:
        libraries[system] = App.openDocument(str(STAGE / 'build/native/library' / (system + '.FCStd')))
    print('BASELINE OPENED', flush=True)
    frame_cache = {}
    for spec in data['occurrences']:
        key = spec['definition']
        if not key:
            continue
        definition = data['definitions'][key]
        system = definition['subsystem']
        if system not in libraries or definition['representation'] != 'assembly':
            continue
        target = libraries[system].getObject('Def_' + key)
        shape = target.Shape.copy()
        shape.Placement = frame(spec['frame'], data, frame_cache).multiply(shape.Placement)
        items.append(dict(spec, shape=shape, target=target, representation='assembly', system=system))
    rotations = {}
    for _, indices, _, _, _ in RUNS[:3]:
        a, b = [st[k] for k in indices]
        angle = math.degrees(math.atan2(a['z'] - b['z'], a['x'] - b['x']))
        for index in indices:
            rotations[index] = angle
        for hand in ['Port', 'Starboard']:
            center_y = (1 if hand == 'Port' else -1) * data['values']['track_centers'].value / 2
            for index in indices:
                center = V(st[index]['x'], center_y, st[index]['z'])
                turn = App.Placement(center, App.Rotation(V(0, 1, 0), -angle)).multiply(
                    App.Placement(-center, App.Rotation()))
                for item in items:
                    if item['id'].startswith(f'{hand}Rollers_Unit{index:03d}_'):
                        item['shape'].Placement = turn.multiply(item['shape'].Placement)

    # Read identity and quantity independently from the frozen catalogue rows.
    source = {}
    with database() as connection:
        records = connection.execute("SELECT record_id,raw_json FROM source_records WHERE source_id='SNL' AND printed_page IN ('4','5')")
        for record, raw in records:
            row = json.loads(raw)
            mark = row.get('brit', '')
            if mark not in {x for r in RUNS for x in r[2:4]} | {'M2175', 'M2176'}:
                continue
            identities = [r[0] for r in connection.execute('SELECT part_id FROM part_evidence WHERE record_id=?', (record,))]
            if len(identities) != 1:
                raise ValueError('Ambiguous support identity: ' + mark)
            source[mark] = dict(record=record, survey_id=identities[0], quantity=int(row['qty']))

    t = v['roller_support_thickness']
    width = v['roller_support_width']
    toe = v['roller_pin_flat_height']
    top = v['roller_clamp_seat']
    shell_offset = v['hull_frame_clear'] / 2 + data['values']['hull_skirt_thickness'].value
    clamp_y = v['hull_frame_clear'] / 2 + v['hull_side_thickness'] + v['roller_ubolt_diameter'] / 2 + v['roller_clamp_gap'] - shell_offset
    leg = v['roller_pin_diameter'] / 2 + v['roller_ubolt_clearance'] + v['roller_ubolt_diameter'] / 2

    def spline_segment(a, b):
        curve = Part.BSplineCurve()
        d = (b[0] - a[0]) / 3
        curve.buildFromPolesMultsKnots([V(*p, 0) for p in [a, (a[0]+d, a[1]), (b[0]-d, b[1]), b]],
                                      [4, 4], [0., 1.], False, 3)
        return curve

    def path_curves(points, ends, offset):
        # Flat 120 mm seats preserve full pin/washer faces. Cubic bridges between
        # them are an explicit formed-contour hypothesis, not a traced contour.
        result = []
        start = (ends[0], points[0][1] + offset)
        def line(a, b):
            if math.dist(a, b) > 1e-7:
                result.append(Part.LineSegment(V(*a, 0), V(*b, 0)))
        for index, (x, z) in enumerate(points):
            left = (max(ends[0], x - 60), z + offset)
            right = (min(ends[1], x + 60), z + offset)
            if index:
                if abs(start[1] - left[1]) < 1e-8:
                    line(start, left)
                else:
                    result.append(spline_segment(start, left))
            else:
                line(start, left)
            line(left, right)
            start = right
        line(start, (ends[1], points[-1][1] + offset))
        return result

    def band_wire(points, ends, low, high):
        lower = [c.toShape() for c in path_curves(points, ends, low)]
        upper = [c.toShape() for c in path_curves(points, ends, high)]
        edges = lower + [Part.makeLine(V(ends[1], points[-1][1]+low, 0), V(ends[1], points[-1][1]+high, 0))]
        edges += [edge.reversed() for edge in reversed(upper)]
        edges.append(Part.makeLine(V(ends[0], points[0][1]+high, 0), V(ends[0], points[0][1]+low, 0)))
        return Part.Wire(edges)

    supports = []
    bolts = []
    metadata = []
    bolt_body = doc.addObject('PartDesign::Body', 'AttachmentBoltDefinition')
    r = 22.225 / math.sqrt(3)
    hex_points = [V(r*math.cos(i*math.pi/3), 0, r*math.sin(i*math.pi/3)) for i in range(6)]
    bolt_shape = Part.Face(Part.makePolygon(hex_points + hex_points[:1])).extrude(V(0, 8.73125, 0))
    bolt_shape = bolt_shape.fuse(Part.makeCylinder(6.35, 22.225, V(), V(0, -1, 0))).removeSplitter()
    feature(bolt_body, 'PlainHeadAndShank', bolt_shape)
    bolt_body.Visibility = False
    hull_tools = []
    for hand, center_sign in [('Port', 1), ('Starboard', -1)]:
        for end_sign in [-1, 1]:
            outside = end_sign == center_sign
            bank = root.newObject('App::Part', hand + ('Outer' if outside else 'Inner'))
            for number, original_indices, mark_b, mark_a, bolt_count in RUNS:
                # Shared A/B marks exchange inner/outer diagonally. Local shapes
                # are mirrored construction variants, with rigid placements.
                specs = [(number, original_indices, mark_b if end_sign == 1 else mark_a, bolt_count, None)]
                if number == '05' and not outside:
                    short_ends = (st[12]['x'] - 168.275/2, st[12]['x'] + 168.275/2)
                    long_ends = (short_ends[0] - 4 - 822.325, short_ends[0] - 4)
                    specs = [('05a', [12], 'M2176', 1, short_ends),
                             ('05b', [13, 14, 15], 'M2175', 3, long_ends)]
                for run, indices, mark, nbolts, exact_ends in specs:
                    angle = rotations.get(indices[0], 0)
                    cx = sum(st[k]['x'] for k in indices) / len(indices)
                    cz = sum(st[k]['z'] for k in indices) / len(indices)
                    rot = App.Rotation(V(0, 1, 0), -angle)
                    inv = rot.inverted()
                    points = sorted((inv.multVec(V(st[k]['x']-cx, 0, st[k]['z']-cz)).x,
                                     inv.multVec(V(st[k]['x']-cx, 0, st[k]['z']-cz)).z) for k in indices)
                    ends = (points[0][0]-60, points[-1][0]+60) if exact_ends is None else tuple(x-cx for x in exact_ends)
                    name = bank.Name + '_Run' + run
                    body = doc.addObject('PartDesign::Body', name + 'Definition')
                    body.addProperty('App::PropertyString', 'SurveyIdentity')
                    body.SurveyIdentity = source[mark]['survey_id']
                    body.addProperty('App::PropertyString', 'SourceMark')
                    body.SourceMark = mark
                    body.addProperty('App::PropertyString', 'Hypothesis')
                    body.Hypothesis = 'Run allocation, contour, stock, tapped attachment and hole pattern are inferred.'
                    # A native section sketch retains the cubic support contour.
                    sketch = body.newObject('Sketcher::SketchObject', 'WebContour')
                    # XY sketch maps to global local XZ, extrusion toward end_sign Y.
                    transform = App.Placement(V(), App.Rotation(V(1, 0, 0), 90))
                    sketch.Placement = transform
                    wire = band_wire(points, ends, toe, top)
                    for edge in wire.Edges:
                        curve = edge.Curve
                        if isinstance(curve, Part.Line):
                            curve = Part.LineSegment(edge.Vertexes[0].Point, edge.Vertexes[-1].Point)
                        j = sketch.addGeometry(curve, False)
                        sketch.addConstraint(Sketcher.Constraint('Block', j))
                    extrusion = pad(body, sketch, t)
                    # Keep planes analytic: transformGeometry(reflection) turns
                    # them into BSpline surfaces and defeats plane-only seat checks.
                    extrusion.Reversed = end_sign == 1
                    doc.recompute()
                    web = extrusion.Shape
                    flange = Part.Face(band_wire(points, ends, top-t, top))
                    flange.Placement = transform
                    shape = web.fuse(flange.extrude(V(0, end_sign*width, 0))).removeSplitter()
                    # Exact native bores follow the unchanged clamp centers.
                    for x, z in points:
                        for direction in [-1, 1]:
                            shape = shape.cut(Part.makeCylinder(v['roller_fastener_bore']/2, top+2,
                                V(x+direction*leg, end_sign*clamp_y, z-1)))
                    # Fit the inferred holes between clamp/pin exclusion zones.
                    # Dynamic programming minimizes movement from equal spacing
                    # while maintaining edge distance and distinct bolt positions.
                    wanted = np.array([ends[0] + (ends[1]-ends[0])*(i+.5)/nbolts for i in range(nbolts)])
                    trial_x = np.linspace(ends[0]+16, ends[1]-16, int(ends[1]-ends[0])+1)
                    trial_x = trial_x[np.min(np.abs(trial_x[:,None]-np.array([p[0] for p in points])[None,:]),axis=1)>=60]
                    costs=(trial_x-wanted[0])**2
                    back=[]
                    for k in range(1,nbolts):
                        best=np.minimum.accumulate(costs)
                        best_index=np.zeros(len(costs),dtype=int)
                        for q in range(1,len(costs)):
                            best_index[q]=q if costs[q]<costs[best_index[q-1]] else best_index[q-1]
                        previous=np.searchsorted(trial_x,trial_x-30,side='right')-1
                        cost=np.full(len(trial_x),np.inf)
                        valid=previous>=0
                        cost[valid]=(trial_x[valid]-wanted[k])**2+best[previous[valid]]
                        index=np.full(len(trial_x),-1,dtype=int)
                        index[valid]=best_index[previous[valid]]
                        back.append(index)
                        costs=cost
                    if not len(costs) or not np.isfinite(costs.min()):
                        raise ValueError('No candidate bolt spacing: '+name)
                    chosen=[int(np.argmin(costs))]
                    for step in reversed(back):
                        chosen.append(int(step[chosen[-1]]))
                    bx=[float(trial_x[q]) for q in reversed(chosen)]
                    def path_z(x):
                        if x <= points[0][0]+60:
                            return points[0][1]
                        for (x0,z0),(x1,z1) in zip(points,points[1:]):
                            if x <= x1-60:
                                q=(x-(x0+60))/(x1-x0-120)
                                return z0+(z1-z0)*(3*q*q-2*q*q*q)
                            if x <= x1+60:
                                return z1
                        return points[-1][1]
                    attach = [(x, path_z(x)+(toe+top-t)/2) for x in bx]
                    for x,z in attach:
                        shape = shape.cut(Part.makeCylinder(6.55, width+2, V(x, -end_sign, z), V(0,end_sign,0)))
                    feature(body, 'FlangeAndOwnedHoles', shape.removeSplitter())
                    if not body.Shape.isValid() or len(body.Shape.Solids) != 1:
                        raise ValueError('Invalid single-solid support: '+name)
                    body.Visibility = False
                    install = App.Placement(V(cx, center_sign*data['values']['track_centers'].value/2+end_sign*shell_offset, cz), rot)
                    link = bank.newObject('App::Link', name)
                    link.setLink(body)
                    link.Placement = install
                    world = body.Shape.copy()
                    world.Placement = install.multiply(world.Placement)
                    item = dict(id=name, definition='lower_support_'+name, shape=world,
                                target=body, representation='assembly', system='RunningGear')
                    supports.append(item)
                    metadata.append(dict(id=name, mark=mark, source=source[mark], hand=hand,
                        end_sign=end_sign, stations=indices, angle_deg=angle,
                        local_ends_mm=ends, projected_length_mm=ends[1]-ends[0],
                        points=points, attachment_bolts=nbolts, attachment_points_xz=attach))
                    for i,(x,z) in enumerate(attach):
                        bolt_name=name+f'_Bolt{i:02d}'
                        rotation = rot.multiply(App.Rotation(V(1,0,0), 0 if end_sign==1 else 180))
                        position=install.multVec(V(x,end_sign*t,z))
                        placement=App.Placement(position,rotation)
                        link=bank.newObject('App::Link',bolt_name)
                        link.setLink(bolt_body)
                        link.Placement=placement
                        shape=bolt_shape.copy()
                        shape.Placement=placement
                        bolts.append(dict(id=bolt_name,definition='lower_support_attachment_bolt',
                            shape=shape,target=bolt_body,representation='assembly',system='RunningGear'))
                        # A plain cylinder models the tapped-hole envelope only.
                        axis=rot.multVec(V(0,-end_sign,0))
                        hull_tools.append(Part.makeCylinder(6.35,22.225+2,position-axis,axis))
                    print('SUPPORT',name,mark,flush=True)
    observed=Counter(m['mark'] for m in metadata)
    if observed != Counter({mark:s['quantity'] for mark,s in source.items()}):
        raise ValueError('Support source counts differ: '+str(observed))
    if len(bolts)!=76:
        raise ValueError('Attachment bolt allocation does not total 76')
    print('BUILT',len(supports),'supports;',len(bolts),'bolts',flush=True)
    # Only experiment copies of hull shapes receive matching attachment holes.
    for item in items:
        if item['system']!='HullStructure':
            continue
        shape=item['shape']
        for cutter in hull_tools:
            if shape.optimalBoundingBox(False).intersect(cutter.optimalBoundingBox(False)):
                shape=shape.cut(cutter)
        item['shape']=shape

    candidates=items+supports+bolts
    def bounds(item):
        b=item['shape'].optimalBoundingBox(False)
        return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
    boxes=np.array([bounds(i) for i in candidates])
    by_id={i['id']:i for i in candidates}
    modified=[i for i in items if any(i['id'].startswith(f'{h}Rollers_Unit{k:03d}_')
              for h in ['Port','Starboard'] for k in range(6))]
    selected=supports+bolts+modified
    selected_ids={i['id'] for i in selected}
    overlaps=[]
    tested=0
    for a in selected:
        bb=np.array(bounds(a))
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for j in near:
            b=candidates[j]
            if a['id']==b['id'] or (b['id'] in selected_ids and b['id']<a['id']):
                continue
            tested+=1
            vol=a['shape'].common(b['shape']).Volume
            if vol>1e-5:
                overlaps.append(dict(a=a['id'],b=b['id'],volume_mm3=vol))
    print('COLLISIONS',tested,'candidate pairs;',len(overlaps),'overlaps',flush=True)
    contacts=[]
    hull_contacts=[]
    bolt_contacts=[]
    for support,meta in zip(supports,metadata):
        for k in meta['stations']:
            prefix=f"{meta['hand']}Rollers_Unit{k:03d}"
            end='B' if meta['end_sign']==1 else 'A'
            for suffix in ['_PinAssembly_Pin']+[f'_Clamp{end}_Washer{leg}' for leg in ['A','B']]:
                target=by_id[prefix+suffix]
                gap,area=bearing_face(support['shape'],target['shape'])
                contacts.append(dict(support=support['id'],mate=target['id'],gap_mm=gap,area_mm2=area))
        near=[i for i in items if i['system']=='HullStructure' and
              support['shape'].optimalBoundingBox(False).intersect(i['shape'].optimalBoundingBox(False))]
        seats=[]
        for item in near:
            gap,area=bearing_face(support['shape'],item['shape'])
            if area>1e-6:
                seats.append(dict(hull=item['id'],gap_mm=gap,area_mm2=area))
        hull_contacts.append(dict(support=support['id'],seats=seats))
        for bolt in bolts:
            if bolt['id'].startswith(support['id']+'_Bolt'):
                gap,area=bearing_face(support['shape'],bolt['shape'])
                bolt_contacts.append(dict(support=support['id'],bolt=bolt['id'],gap_mm=gap,area_mm2=area))
    # Store the complete modified lower banks and affected hull in this standalone
    # experiment document. They are baked copies, deliberately not delivery links.
    context=root.newObject('App::Part','ExperimentContext')
    for item in items:
        if item['id'].startswith(('PortRollers_','StarboardRollers_')) or item['system']=='HullStructure':
            obj=context.newObject('PartDesign::Feature','Context_'+item['id'])
            obj.Shape=item['shape']
            obj.Label=item['id']
    doc.recompute()
    native=out/'LowerSupportExperiment.FCStd'
    doc.saveAs(str(native))
    port=[i for i in candidates if (i['id'].startswith('PortRollers_') and not i['id'].startswith('PortRollers_Unit029_')) or i['id'].startswith('PortOuter') or i['id'].startswith('PortInner')]
    shaded(port,out/'port_support_bank.svg',(0,1,.35),'EXPERIMENT | 17 lower supports, 38 attachment bolts | inferred contours and joints')
    front=[i for i in port if i['id'].startswith(tuple(f'PortRollers_Unit{k:03d}_' for k in range(6))) or any('_Run'+n in i['id'] for n in ['01','02','03'])]
    shaded(front,out/'front_support_detail.svg',(1,1,.6),'EXPERIMENT | inclined front supports and complete rotated roller stacks')
    rear=[i for i in port if i['id'].startswith(tuple(f'PortRollers_Unit{k:03d}_' for k in range(23,29))) or '_Run08' in i['id']]
    shaded(rear,out/'rear_support_detail.svg',(1,1,.6),'EXPERIMENT | rear run allocation and formed contour remain unverified')
    report=dict(status='native_experiment_not_promoted',authored_fingerprint=fingerprint(),
        experiment_script_sha256=sha(Path(__file__)),
        baseline_libraries={k:sha(STAGE/'build/native/library'/(k+'.FCStd')) for k in libraries},
        source_quantities=dict(observed),support_occurrences=len(supports),attachment_bolts=len(bolts),
        modified_roller_components=len(modified),candidate_pairs=tested,overlaps=overlaps,
        bearing_contacts=contacts,missing_bearing_contacts=[x for x in contacts if x['gap_mm']>1e-6 or x['area_mm2']<1],
        hull_contacts=hull_contacts,bolt_contacts=bolt_contacts,
        missing_bolt_contacts=[x for x in bolt_contacts if x['gap_mm']>1e-6 or x['area_mm2']<1],
        runs=metadata,native_file_sha256=sha(native),
        limitations=['Source run-to-station allocation is a hypothesis, especially the two rear outline rollers.',
                     'M2176 carries Lower12; M2175 carries Lower13-15 with printed lengths fixed and 4 mm separation. Allocation is inferred.',
                     'Runs 4 and 8 use horizontal pin seats joined by cubic curves; this is not a historical contour qualification.',
                     'Angle wall is at the 10 mm skirt outer face; upper cross-section sizes are transferred and root radius omitted.',
                     'Attachment bolt heads and tapped hull joints are inferred; handbook detachable plate topology is unresolved.',
                     'Baked context copies and mirrored construction variants are for interface review only.',
                     'No STEP, relocation or delivery qualification is claimed.'])
    write(out/'report.json',report)
    print('EXPERIMENT SAVED',native,'missing bearing contacts',len(report['missing_bearing_contacts']),flush=True)


if __name__=='__main__':
    raise SystemExit(main())
