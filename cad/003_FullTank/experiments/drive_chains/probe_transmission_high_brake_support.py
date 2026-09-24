"""Read-only support-context sections with the retained HB133 registration.

These sections diagnose missing receiving geometry. They neither fit a camera
nor establish the source illustration's hidden transverse depths.
"""
import argparse
import base64
from pathlib import Path
import sys
from types import SimpleNamespace

H = Path(__file__).resolve().parent
STAGE = H.parents[1]
ROOT = STAGE.parents[1]
sys.path.insert(0, str(STAGE))
from lib.evidence import read, write, sha
from lib.camera_review import validate_native_bindings
import FreeCAD as App
import Part
import fitz
from lib.visual_review import shaded
from lib.cad_build import COLORS

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
assert not out.exists(), 'Preserve prior evidence; choose a new directory.'
out.mkdir(parents=True)
packet = H/'transmission_high_brake_support_study'
parent = H/'transmission_high_brake_mechanism_study/trial01'
r = read(parent/'report.json')
m = read(parent/'isolated/manifest.json')
native = parent/r['native_file']
assert sha(native) == r['native_sha256'] == m['native_sha256']
reg = read(packet/'source_registration.json')
assert sha(ROOT/reg['reused_from']) == reg['reused_registration_sha256']
source = ROOT/reg['source_image']
assert sha(source) == reg['source_sha256']
selected = ['CenterTransmissionCore_bevel_case','PortHighSpeedBrakeAnchorEnd',
    'TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel']
selected += [o['name'] for o in m['occurrences'] if o['name'].startswith('PortHighSpeedBrake')
             and o['name'].endswith(('Lining','Band','FrontEnd'))]
validate_native_bindings(dict(native_file=str(native),render_occurrences=selected,landmarks=[]), m)
rows = {o['name']:o for o in m['occurrences']}
V = App.Vector
center = V(*r['interfaces']['PortHighSpeedBrake']['center_world_mm'])
items = {}
cache = {}
COLORS.update(SupportCase=(.52,.61,.70),SupportBand=(.68,.49,.31))
for name in selected:
    row = rows[name]
    key = row['definition']
    d = m['definitions'][key]
    if key not in cache:
        assert sha(d['brep_path']) == d['brep_sha256']
        s = Part.Shape(); s.read(d['brep_path'])
        assert s.isValid() and s.Solids
        cache[key] = SimpleNamespace(Shape=s)
    s = cache[key].Shape.copy()
    s.Placement = App.Placement(App.Matrix(*row['frame']))
    items[name] = dict(id=name,shape=s,target=cache[key],definition=key,
        system='SupportBand' if name.startswith('PortHighSpeedBrake') else 'SupportCase', representation='assembly')
case = items['CenterTransmissionCore_bevel_case']['shape']
bearing = read(H/'transmission_brake_bearing_controls.json')['controls']
stations = [('brake_midplane',center.y,'#00a1ab'),
            ('bearing_midplane',(bearing['bush_low']+bearing['bush_high'])/2,'#b02397')]
cx, cy = reg['center_px']; scale = reg['pixels_per_mm']
def pixel(v):
    return cx-(v.x-center.x)*scale, cy-(v.z-center.z)*scale
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1445" height="1850">',
    '<rect width="100%" height="100%" fill="white"/>',
    '<text x="30" y="34" font-family="sans-serif" font-size="22">Retained M263 sections | support receiving geometry still under review</text>',
    f'<image x="40" y="70" width="1365" height="1641" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
sections = []
for label,y,color in stations:
    corners = [V(center.x+x,y,center.z+z) for x,z in [(-450,-450),(450,-450),(450,450),(-450,450)]]
    plane = Part.Face(Part.makePolygon(corners+corners[:1]))
    section = case.section(plane)
    assert section.Edges, label
    section.exportBrep(str(out/(label+'.brep')))
    for edge in section.Edges:
        pts = [pixel(v) for v in edge.discretize(Deflection=.3)]
        svg.append('<polyline points="'+' '.join(f'{u+40:.3f},{v+70:.3f}' for u,v in pts)+
                   f'" fill="none" stroke="{color}" stroke-width="2.5"/>')
    sections.append(dict(name=label,station_world_y_mm=y,edge_count=len(section.Edges),
                         brep_sha256=sha(out/(label+'.brep'))))
svg += ['<text x="30" y="1745" font-family="sans-serif" font-size="18">Cyan: actual case at brake midplane. Magenta: actual case at retained bearing midplane.</text>',
    '<text x="30" y="1780" font-family="sans-serif" font-size="18">Different depths are shown separately; neither is asserted to be the drawing’s section plane.</text>',
    '<text x="30" y="1815" font-family="sans-serif" font-size="18">Inherited image center and scale; no camera refit, geometry change or historical qualification.</text></svg>']
(out/'case_sections_source.svg').write_text('\n'.join(svg))
with fitz.open(stream=(out/'case_sections_source.svg').read_bytes(),filetype='svg') as f:
    f[0].get_pixmap().save(str(out/'case_sections_source.png'))
focus = [v for k,v in items.items() if not k.startswith('TransmissionFrame_')]
context = [v for k,v in items.items() if k.startswith('TransmissionFrame_')]
shaded(focus,out/'support_context.svg',(1,-1,.4),
    'Existing high-speed brake and M263 | receiving-web and bracket depth study',context=context)
eye = items['PortHighSpeedBrakeAnchorEnd']['shape']
bores = [f.Surface for f in eye.Faces if isinstance(f.Surface,Part.Cylinder)
         and abs(f.Surface.Radius-8.0875)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-6]
assert bores
anchor = V(bores[0].Center.x,center.y,bores[0].Center.z)
assert all(abs(b.Center.x-anchor.x)<1e-6 and abs(b.Center.z-anchor.z)<1e-6 for b in bores)
measurements = []
for label,y,color in stations:
    # These are diagnostic points in source bracket-foot regions, not inferred
    # bolt axes or receiving faces. A nearest distance is not bearing contact.
    for role,pick in [('top_foot_region',[1090,210]),('bottom_foot_region',[1110,1420])]:
        q = V(center.x+(cx-pick[0])/scale,y,center.z+(cy-pick[1])/scale)
        distance,pairs,_ = case.distToShape(Part.Vertex(q))
        measurements.append(dict(region=role,source_pixel=pick,assumed_station=label,
            world_mm=list(q),case_distance_mm=distance,nearest_case_point_mm=list(pairs[0][0])))
assert sha(native) == r['native_sha256']
write(out/'report.json',dict(native_file=str(native.relative_to(ROOT)),native_sha256=sha(native),
    source_registration_sha256=sha(packet/'source_registration.json'),source_sha256=sha(source),
    input_hashes={str(f.relative_to(ROOT)):sha(f) for f in [Path(__file__),parent/'report.json',parent/'isolated/manifest.json',
        H/'transmission_brake_bearing_controls.json',STAGE/'lib/camera_review.py',STAGE/'lib/visual_review.py']},
    selected_native_bindings_verified=True,selected_occurrences=selected,sections=sections,
    anchor_pin_center_world_mm=list(anchor),anchor_pin_center_brake_mm=list(anchor-center),
    diagnostic_region_distances=measurements,
    image_hashes={n+'.png':sha(out/(n+'.png')) for n in ['case_sections_source','support_context']},
    runtime=dict(freecad=App.Version(),occ=Part.OCC_VERSION),camera_refit=False,geometry_modified=False,
    historical_geometry_qualified=False,installation_qualified=False,
    limits=['Source region picks are approximate, not bolt-center measurements.',
        'Source projection and hidden transverse depths remain uncertain.',
        'Existing M263 already has estimated geometry; the section comparison identifies receiving work, not a camera error.',
        'Nearest-point distances do not establish bearing area, material stock or safe screw engagement.']))
print('Saved read-only support context and fixed-registration sections',out,flush=True)
