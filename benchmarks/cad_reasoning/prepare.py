"""Freeze the entire candidate input; never include reference solutions."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def schema(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)

STRING = {'type': 'string'}
BOOL = {'type': 'boolean'}
POINT = {'type': 'array', 'items': {'type': 'number'}, 'minItems': 2, 'maxItems': 2}
COMMON = '''This is an isolated empirical benchmark, not an instruction to continue the tank project.
All necessary inputs are in this prompt and any attached image. Do not use any tools,
read files, search the web, delegate, or inspect project history. Return only the JSON
object required by the supplied output schema. Give a concise explanation, not a
reasoning transcript. Your output will be assessed outside this session. State
uncertainty honestly. Do not assume an unknown dimension from apparent drawing scale.
'''

CONSTRUCTION = {
    'x0': 842.95, 'shoulder': 853.15, 'sleeve_length': 68.2498,
    'bearing_end': 994.95, 'outer_radius': 76.0,
    'rear_bore': 57.3, 'front_bore': 50.8254,
    'relief_radius': 69.0, 'relief_start': 893.15, 'relief_end': 969.95,
    'sleeve_radius': 57.15, 'sleeve_bore': 44.8437,
    'groove_root': 50.525, 'groove_width': 5.0, 'groove_count': 24,
}
REPAIR = {
    'joint_face': 834.95, 'lip_end': 841.3, 'front': 1002.95,
    'bore_step': 842.95, 'rear_bore': 52.65,
    'main_bore': 76.0, 'body_radius': 88.0, 'lip_radius': 114.3,
}

def main():
    fixtures = HERE / 'fixtures'
    fixtures.mkdir(exist_ok=True)
    source = ROOT / 'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p293-geometry.png'
    shutil.copyfile(source, fixtures / 'plate21.png')
    parent = ROOT / 'cad/003_FullTank/experiments/drive_chains/clutch_stack_build/inputs/parent_collar.brep'
    shutil.copyfile(parent, fixtures / 'parent_collar.brep')
    cases = {
        'source': {
            'prompt': COMMON + '''Read the attached full SNL G-13 Plate 21 (1447 by 1055 pixels).
Catalogue transcriptions, not geometrical interpretations:
SNL p67 row20: COLLAR, clutch spring thrust; mark SH998B; Plate21 ident28; quantity1.
SNL p165 row1: RING, clutch snap; mark SH861E; Plate21 ident30; quantity1.

Trace both callout leaders to their component endpoints. Identify the mark of the
large annular piece that closes the LEFT end of the long central bearing in this
image. Decide whether callout30 is a separate ring and whether it sits externally
on the collar or internally in the large bearing bore. Give approximate leader
endpoint coordinates in the FULL original image (origin top left; x right, y down).
Do not give the coordinates of the printed number. Decide whether these inputs
establish an exact ring diameter or justify claiming historical dimensional fit.
The fields are: callout_28_mark, callout_30_mark, bearing_end_mark,
separate_components, ring_location (external/internal/uncertain), endpoint_28,
endpoint_30, exact_ring_diameter_mm (null if not established), historical_fit_proven,
and explanation. Keep explanation under 180 words.
''',
            'schema': schema(dict(callout_28_mark=STRING, callout_30_mark=STRING,
                bearing_end_mark=STRING, separate_components=BOOL,
                ring_location={'type': 'string', 'enum': ['external', 'internal', 'uncertain']},
                endpoint_28=POINT, endpoint_30=POINT,
                exact_ring_diameter_mm={'type': ['number', 'null']},
                historical_fit_proven=BOOL, explanation=STRING)),
            'images': ['plate21.png'],
        },
        'construction': {
            'prompt': COMMON + '''Implement a pure FreeCAD Python function build(p, frame) returning
{'bearing': TopoShape, 'sleeve': TopoShape}. The globals App (FreeCAD), Part and math
are supplied. No imports, file IO, documents, printing or GUI operations. Return
the function and helpers as a python_code string, plus a short explanation.
Use parameters by key; the grader changes dimensions and installation frames.
Millimetres, LOCAL X along the shaft; radius is measured in local Y/Z.

Bearing: outer cylinder of radius outer_radius, from shoulder to bearing_end.
The bore has radius rear_bore from shoulder to relief_start, radius relief_radius
from relief_start to relief_end, and radius front_bore from relief_end to bearing_end.
Sleeve: barrel radius sleeve_radius from x0 to x0+sleeve_length, plus an integral
rear flange of radius outer_radius from x0 to shoulder. Its bore is a circle of
radius sleeve_bore UNION groove_count straight radial rectangular grooves.
Each groove extends from radius zero to groove_root in its radial direction and
has total tangential width groove_width; rotate evenly around local X, starting
along +Y (angle zero). Extrude this entire bore/groove void through the full sleeve.
This defines rectangular-ended grooves, not an involute spline or radial circular
arcs. Keep the bearing and sleeve as separate one-solid, valid shapes. They nest
axially: the sleeve barrel enters the bearing rear bore; do not lay them end to end.
No fillets or other details are requested.

Apply the supplied App.Placement frame to each finished LOCAL shape exactly once.
Return shapes in world coordinates. Example frame: translation (112,-37,84),
rotation 27 degrees about axis (1,2,3); other frames will also be checked.
Nominal p:
''' + json.dumps(CONSTRUCTION, indent=2),
            'schema': schema(dict(python_code=STRING, explanation=STRING)),
            'images': [],
        },
        'repair': {
            'prompt': COMMON + '''A collar generator passes nominal-size checks but fails a smaller-size
trial. Diagnose the cause and return a corrected pure FreeCAD function
rebuild(parent, p) returning one valid collar TopoShape. The globals App, Part and
math are supplied. No imports, file IO, documents, printing or GUI operations.
Return python_code and explanation. Do not modify the input parent shape.

All shapes use local X as the axis, mm. The supplied legacy parent has a mounting
lip at X834.95..841.30 with outer radius114.3 and SIX actual screw clearance holes;
body radius77 from841.30 onward; and an old FRONT rim of radius88 starting995.0
and ending1002.95. Its old front bore radius is59.65. The rear bore radius52.65
continues to842.95. Preserve every bit of the mounting lip and its six holes.

Required new collar: the same mounting lip, a body whose outer radius is
p['body_radius'] everywhere from p['lip_end'] to p['front'], a rear bore radius
p['rear_bore'] from p['joint_face'] to p['bore_step'], and a main bore radius
p['main_bore'] from p['bore_step'] to p['front']. No other forward rim is requested.
Do not change receiving components, tolerances or the six lip holes to obtain a pass.
Only body_radius and main_bore vary in the trial, by the same delta; parent stays
fixed. A separate thrust lip has inner radius body_radius+0.15 over X991.95..1002.95.
At nominal body_radius88 it clears; at body_radius87 a positive overlap appears.

Faulty implementation:
def xc(r, a, b):
    return Part.makeCylinder(r, b-a, App.Vector(a,0,0), App.Vector(1,0,0))
def rebuild(parent, p):
    s = parent.fuse(xc(p['body_radius'], p['lip_end'], p['front']))
    s = s.cut(xc(p['rear_bore'], p['joint_face']-1, p['bore_step']))
    return s.cut(xc(p['main_bore'], p['bore_step'], p['front']+1)).removeSplitter()

Nominal p:
''' + json.dumps(REPAIR, indent=2),
            'schema': schema(dict(python_code=STRING, explanation=STRING)),
            'images': [],
        },
    }
    for name, case in cases.items():
        folder = fixtures / name
        folder.mkdir(exist_ok=True)
        (folder / 'prompt.txt').write_text(case['prompt'])
        (folder / 'schema.json').write_text(json.dumps(case['schema'], indent=2) + '\n')
    (fixtures / 'parameters.json').write_text(json.dumps(dict(construction=CONSTRUCTION, repair=REPAIR), indent=2) + '\n')
    manifest = dict(protocol='README.md', model='gpt-6-astra', efforts=['medium','high','xhigh'],
        repetitions=3, cases={k:{'images':v['images']} for k,v in cases.items()},
        fixture_hashes={str(p.relative_to(HERE)):sha(p) for p in sorted(fixtures.rglob('*')) if p.is_file()},
        source_files={str(source.relative_to(ROOT)):sha(source), str(parent.relative_to(ROOT)):sha(parent)})
    (HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Prepared frozen inputs for three cases; no model calls.')

if __name__ == '__main__':
    main()
