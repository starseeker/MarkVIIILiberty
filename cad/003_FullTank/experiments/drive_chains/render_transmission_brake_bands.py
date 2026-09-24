"""Review actual saved brake geometry and dimensioned handbook lining figures."""
import argparse
import base64
import math
from pathlib import Path
import sys
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
import FreeCAD as App
import Part
import fitz
from lib.cad_build import COLORS
from lib.visual_review import shaded
COLORS.update(Band=(.40,.47,.53),Lining=(.62,.46,.29),Copper=(.86,.49,.26),Drum=(.48,.55,.63),Frame=(.62,.56,.45))
rows={v['name']:v for v in m['occurrences']};cache={}
def definition(key):
    if key not in cache:
        d=m['definitions'][key];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));cache[key]=s
    return cache[key]
def item(name):
    row=rows[name];key=row['definition'];target=SimpleNamespace(Shape=definition(key));s=target.Shape.copy()
    s.Placement=App.Placement(App.Matrix(*row['frame']))
    role='Copper' if 'Rivet' in name and 'Brake' in name else 'Lining' if name.endswith('Lining') else 'Band' if name.endswith('Band') else 'Drum' if name in r['affected_occurrences'] else 'Frame'
    return dict(id=name,shape=s,target=target,definition=key,system=role,representation='assembly')
selected=[item(n) for n in r['affected_occurrences']]
frame=[item(n) for n,v in rows.items() if 'TransmissionMountingFrame' in v['owners']]
detail=[v for v in selected if v['id'].startswith('PortLowSpeedBrake')]
views=[('isometric',selected,frame,(1,-.8,.55),'Transmission brakes | HB segmented linings and copper rivets; ears and linkage pending'),
       ('band_detail',detail,[],(1,-1,.6),'Low-speed brake | six M346 lining segments, two M344 steel half-bands, 54 rivets')]
for name,solid,context,direction,title in views:
    shaded(solid,out/(name+'.svg'),direction,title,context=context);print('Rendered',name,flush=True)
# Side and flattened hole-layout comparisons use the saved analytic surfaces.
# The flat view is a dimensional diagram, not another physical manufactured part.
for role,plate in [('low',97),('track',98)]:
    s=definition('Def_BrakeBand_'+role+'_lining');cyl=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder)]
    radial=[f for f in cyl if abs(abs(f.Surface.Axis.y)-1)<1e-7];ri=min(f.Surface.Radius for f in radial);ro=max(f.Surface.Radius for f in radial)
    ends=[f for f in s.Faces if isinstance(f.Surface,Part.Plane) and abs(f.normalAt(0,0).y)<1e-6]
    angles=sorted(math.atan2(f.CenterOfMass.z,f.CenterOfMass.x) for f in ends);sweep=angles[1]-angles[0]
    neutral=(ri+ro)/2;length=sweep*neutral;width=s.BoundBox.YLength
    source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets'/('plate'+str(plate)+'.png')
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1640" height="1200">','<rect width="100%" height="100%" fill="white"/>',
        f'<text x="30" y="34" font-family="sans-serif" font-size="23">HB Plate {plate} | original figure and saved-native lining section / flattened bore centers</text>',
        f'<image x="20" y="60" width="980" height="720" preserveAspectRatio="xMidYMin meet" href="data:image/png;base64,{base64.b64encode(source.read_bytes()).decode()}"/>']
    def line(points,color='#ac582b'):
        path=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
        svg.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="1.5"/>')
    ss=s.copy();ss.rotate(App.Vector(),App.Vector(0,1,0),-math.degrees(math.pi/2-sweep/2))
    scale=1.75
    for edge in ss.Edges:line([(1295+v.x*scale,300-v.z*scale+ri*scale) for v in edge.discretize(Number=45)])
    svg.append(f'<text x="1030" y="130" font-family="sans-serif" font-size="19">Inner radius {ri:.3f} mm; stock {ro-ri:.4f} mm</text>')
    x0,y0=1020,490;scale=1.85
    svg.append(f'<rect x="{x0}" y="{y0}" width="{length*scale}" height="{width*scale}" fill="#f6eee3" stroke="#5d473a"/>')
    holes=[]
    for face in cyl:
        if abs(abs(face.Surface.Axis.y)-1)<1e-7:continue
        axis=face.Surface.Axis
        if axis.x<0:axis=-axis
        theta=math.atan2(axis.z,axis.x);station=theta*neutral;axial=face.Surface.Center.y
        holes.append(dict(station_mm=station,axial_mm=axial,radius_mm=face.Surface.Radius))
        x=x0+station*scale;y=y0+(axial+width/2)*scale
        svg.append(f'<circle cx="{x}" cy="{y}" r="{face.Surface.Radius*scale}" fill="white" stroke="#5d473a" stroke-width="2"/>')
    for i,text in enumerate([f'Flat middle-radius length {length:.3f} mm; width {width:.3f} mm',
        f'{len(holes)} bores, diameter {2*holes[0]["radius_mm"]:.5f} mm',
        'Curved section above includes all native edges, including rear holes.',
        'Flattened bore centers below are derived from saved cylinder axes.',
        'Drawing views shown side by side; no pixel registration is claimed.',
        'Radius arrow and remaining straight stock are interpreted from HB.',
        'Track countersink angle and later copper-rivet stock are estimates.']):
        svg.append(f'<text x="40" y="{850+i*38}" font-family="sans-serif" font-size="22">{text}</text>')
    svg.append('</svg>');name=role+'_source_comparison';path=out/(name+'.svg');path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(out/(name+'.png')))
    write(out/(role+'_source_measurements.json'),dict(native_sha256=r['native_sha256'],inner_radius_mm=ri,stock_mm=ro-ri,
        flat_length_mm=length,width_mm=width,holes=holes,source_sha256=sha(source),pixel_registration_claimed=False))
    print('Rendered',name,flush=True)
names=['isometric','band_detail','low_source_comparison','track_source_comparison']
write(out/'render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),
    images={name+'.png':sha(out/(name+'.png')) for name in names},
    views={name:dict(direction=direction,solid_ids=[v['id'] for v in solid],context_ids=[v['id'] for v in context]) for name,solid,context,direction,title in views},
    historical_geometry_qualified=False,installation_qualified=False))
