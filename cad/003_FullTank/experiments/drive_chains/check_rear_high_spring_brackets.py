"""Check saved guide passages, rivet retention, receiving holes and local material."""
import argparse
from collections import Counter
import itertools
import math
from pathlib import Path
import shutil
import sys
import tempfile
H = Path(__file__).resolve().parent
ROOT = H.parents[3]
sys.path.insert(0, str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings
V = App.Vector
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate', type=Path, required=True)
a = p.parse_args()
out = a.candidate.resolve()
assert not (out/'independent_checks.json').exists()
r = read(out/'report.json')
m = read(out/'isolated/manifest.json')
native = out/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
source = ROOT/r['parent_native']
old = read(source.parent/'isolated/manifest.json')
assert sha(source) == r['parent_native_sha256'] == old['native_sha256']
c = r['controls']
assert c['mount_face'] == 'rear_flange'
b, ri = c['bracket'], c['rivet']
rows = {v['name']: v for v in m['occurrences']}
checks = []


def ck(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))


def volume(shape):
    return sum(abs(s.Volume) for s in shape.Solids)


with tempfile.TemporaryDirectory(prefix='relocated_high_spring_', dir=out) as temp:
    copied = Path(temp)/native.name
    shutil.copy2(native, copied)
    validate_native_bindings(dict(native_file=str(copied), render_occurrences=list(rows), landmarks=[]), m)
    doc = App.openDocument(str(copied))
    try:
        ck('Seven saved links remain local after relocation', len(rows) == 7 and all(
            doc.getObject(v['object']).LinkedObject.Document == doc and
            doc.getObject(v['object']).LinkedObject.Placement.isIdentity() for v in rows.values()))
        for name in c['stations']:
            group = doc.getObject(name+'HighSpringSupport')
            ck(name+' owns one guide and two rivets', len(group.Group) == 3 and
               all(v.TypeId == 'App::Link' for v in group.Group))
        ck('Bracket and rivet source records persist',
           doc.getObject('Def_HighSpringGuide_bracket').SourcePartMark == 'M4135' and
           'SNL:169:011' in doc.getObject('Def_HighSpringGuide_rivet').SourceRecords)
    finally:
        App.closeDocument(doc.Name)
counts = Counter(v['definition'].removeprefix('Def_HighSpringGuide_') for v in rows.values())
ck('Two guides and four rivets share three definitions',
   counts == dict(channel=1, bracket=2, rivet=4) and len(m['definitions']) == 3)
cache = {}


def world(name, manifest=m):
    row = next(v for v in manifest['occurrences'] if v['name'] == name)
    d = manifest['definitions'][row['definition']]
    digest = d['brep_sha256']
    if digest not in cache:
        assert sha(d['brep_path']) == digest
        s = Part.Shape()
        s.read(d['brep_path'])
        assert s.Placement.isIdentity()
        cache[digest] = s
    s = cache[digest].copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    return s


shapes = {name: world(name) for name in rows}
for role in ['channel', 'bracket', 'rivet']:
    name = next(name for name in rows if r['specs'][name]['role'] == role)
    s = shapes[name]
    ck(role+' is one valid closed solid with bounded tolerance',
       s.isValid() and len(s.Solids) == 1 and s.Solids[0].isClosed() and
       s.getTolerance(1) <= 1e-4, tolerance_mm=s.getTolerance(1))
channel = shapes['RearControlChannelStock']
original = world('RearControlChannelStock', old)
holes = []
for point in c['stations'].values():
    for y in b['rivet_y']:
        center = V(*point)+V(b['stock']-1, y, b['rivet_height'])
        holes.append(Part.makeCylinder(ri['hole_diameter']/2, c['channel_stock']+2, center, V(1, 0, 0)))
expected = original.common(Part.makeCompound(holes))
removed = original.cut(channel)
ck('Channel loses exactly four receiving passages and gains no material',
   volume(channel.cut(original)) < 1e-5 and volume(removed.cut(expected)) < 1e-5 and
   volume(expected.cut(removed)) < 1e-5, removed_mm3=volume(removed))
expected_volume = 4*math.pi*(ri['hole_diameter']/2)**2*c['channel_stock']
ck('Four complete channel bores retain their specified diameter',
   abs(volume(removed)-expected_volume) < 1e-5, expected_mm3=expected_volume)


def faces(shape, x):
    return [f for f in shape.Faces if isinstance(f.Surface, Part.Plane) and
            abs(abs(f.normalAt(0, 0).x)-1) < 1e-7 and abs(f.CenterOfMass.x-x) < 1e-6]


def bearing(one, two, x):
    return sum(f.common(g).Area for f in faces(one, x) for g in faces(two, x))


for name, point in c['stations'].items():
    base = V(*point)
    bracket = shapes[name+'HighSpringBracket']
    center = base+V(0, 0, b['guide_height'])
    cylinders = [f for f in bracket.Faces if isinstance(f.Surface, Part.Cylinder) and
                 abs(f.Surface.Radius-b['guide_diameter']/2) < 1e-7 and
                 abs(abs(f.Surface.Axis.x)-1) < 1e-7 and
                 math.hypot(f.Surface.Center.y-center.y, f.Surface.Center.z-center.z) < 1e-6]
    ck(name+' guide bore is an actual full-length cylindrical face',
       len(cylinders) == 1 and abs(cylinders[0].BoundBox.XLength-b['stock']) < 1e-6)
    witness = Part.makeCylinder(19.05/2, b['stock']+2, center-V(1, 0, 0), V(1, 0, 0))
    ck(name+' nominal three-quarter-inch rod envelope passes guide',
       volume(witness.common(bracket)) < 1e-5,
       nominal_radial_gap_mm=(b['guide_diameter']-19.05)/2,
       scope='Guide passage only; complete M575 route, spring and thread fit remain open.')
    ck(name+' bracket has the recorded plate stock',
       abs(bracket.BoundBox.XLength-b['stock']) < 1e-6)
    ck(name+' rear-flange seating exists',
       bearing(bracket, channel, base.x+b['stock']) > 500,
       bearing_area_mm2=bearing(bracket, channel, base.x+b['stock']))
    for i, y in enumerate(b['rivet_y'], 1):
        rivet = shapes[name+'HighSpringRivet'+str(i)]
        axis = base+V(0, y, b['rivet_height'])
        factory_area = math.pi*((ri['diameter']/2*ri['factory_ratio'])**2-(ri['hole_diameter']/2)**2)
        tail_area = math.pi*((ri['diameter']/2*ri['upset_ratio'])**2-(ri['hole_diameter']/2)**2)
        fa = bearing(rivet, bracket, base.x)
        ta = bearing(rivet, channel, base.x+b['stock']+c['channel_stock'])
        ck(name+' rivet'+str(i)+' retains both complete head annuli',
           abs(fa-factory_area) < 1e-5 and abs(ta-tail_area) < 1e-5,
           factory_bearing_mm2=fa, tail_bearing_mm2=ta)
        shank = Part.makeCylinder(ri['diameter']/2, b['stock']+c['channel_stock'], axis, V(1, 0, 0))
        ck(name+' rivet'+str(i)+' shank clears both holes',
           volume(shank.common(bracket)) < 1e-5 and volume(shank.common(channel)) < 1e-5)
        pad_center = axis+V(b['stock'], 0, 0)
        pad = Part.Face(Part.Wire([Part.makeCircle(12.7, pad_center, V(1, 0, 0))]))
        bore = Part.Face(Part.Wire([Part.makeCircle(ri['hole_diameter']/2, pad_center, V(1, 0, 0))]))
        pad = pad.cut(bore)
        contact = Part.makeCompound([f.common(g) for f in faces(bracket, pad_center.x)
                                     for g in faces(channel, pad_center.x)])
        unsupported = pad.cut(contact)
        ck(name+' rivet'+str(i)+' mounting annulus fully supported', not unsupported.Faces,
           unsupported_mm2=unsupported.Area)
rivet = shapes['StarboardHighSpringRivet1']
radius = ri['diameter']/2
head_radius = radius*ri['factory_ratio']
head_height = ri['diameter']*ri['factory_height_ratio']
stock_volume = math.pi*radius**2*19.05 + math.pi*head_height*(3*head_radius**2+head_height**2)/6
ck('Rivet retains source three-quarter-inch stock and factory head',
   abs(rivet.Volume-stock_volume) < 1e-5 and ri['stock_length'] == 19.05,
   actual_mm3=rivet.Volume, expected_mm3=stock_volume)
pairs = []
for first, second in itertools.combinations(rows, 2):
    common = shapes[first].common(shapes[second])
    occupied = volume(common)
    pairs.append(dict(first=first, second=second, common_mm3=occupied,
                      passed=(common.isNull() or common.isValid()) and occupied < 1e-5))
ck('All local material pairs clear', all(v['passed'] for v in pairs))
result = dict(passed=all(v['passed'] for v in checks), checks=checks, material_pairs=pairs,
              native_sha256=sha(native), parent_native_sha256=sha(source),
              manifest_sha256=sha(out/'isolated/manifest.json'), checker_sha256=sha(Path(__file__)),
              scope='Saved rear-flange guide pair, source rivets and receiving channel; complete rod and spring routes not qualified.',
              historical_geometry_qualified=False, installation_qualified=False)
write(out/'independent_checks.json', result)
print(len(checks), 'saved-guide checks;', len(pairs), 'local pairs;', result['passed'], flush=True)
if not result['passed']:
    print([v for v in checks if not v['passed']], flush=True)
assert result['passed']
