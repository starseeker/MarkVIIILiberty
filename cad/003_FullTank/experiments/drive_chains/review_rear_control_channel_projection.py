"""Reuse fixed local side registration against saved geometry, with explicit residuals."""
import argparse
import math
from pathlib import Path
import sys
from PIL import Image,ImageDraw
import numpy as np

H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
from lib.source_camera import project

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output.resolve();assert not out.exists();out.mkdir(parents=True)
packet=H/'transmission_controls_study';rp=packet/'channel_local_registration01.json';reg=read(rp)
source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
base=packet/'us_nuts01';m=read(base/'isolated/manifest.json');r=read(base/'report.json');native=base/r['native_file'];assert sha(native)==m['native_sha256']
rows={v['name']:v for v in m['occurrences']}
selected=['PortTransmissionCore_high_drum','PortTransmissionOutput_drum','PortHighSpeedBrakeLeverLeft']
validate_native_bindings(dict(native_file=str(native),render_occurrences=selected,landmarks=[]),m)
shapes={};bindings=[]
for name in selected:
    row=rows[name];d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);s.Placement=App.Placement(App.Matrix(*row['frame']));shapes[name]=s
    bindings.append(dict(occurrence=name,definition_sha256=d['brep_sha256'],frame=row['frame']))
def cylinders(name,radius):return [f.Surface for f in shapes[name].Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-7]
inner=cylinders(selected[0],190.5);outer=cylinders(selected[1],304.8);pins=cylinders(selected[2],8.0875);assert inner and outer and pins
center=inner[0].Center;outer_center=outer[0].Center;pin=min(pins,key=lambda c:c.Center.z).Center
assert max(abs(center.x-reg['axis_world_mm'][0]),abs(center.z-reg['axis_world_mm'][2]),abs(center.x-outer_center.x),abs(center.z-outer_center.z))<1e-7
camera=dict(projection='orthographic',image_size_px=reg['image_size_px'],world_to_camera_rotation=[[-1,0,0],[0,0,-1],[0,-1,0]],origin_world_mm=reg['axis_world_mm'],scale_px_per_mm=reg['pixels_per_mm'],principal_px=reg['center_px'])
def uv(v):return project([list(v)],camera)[0,:2].tolist()
diagnostics=[]
world_points=dict(outer_drum_top=outer_center+App.Vector(0,0,304.8),outer_drum_bottom=outer_center-App.Vector(0,0,304.8),outer_drum_right=outer_center-App.Vector(304.8,0,0),high_speed_control_pin=pin)
for name,point in world_points.items():
    pred=uv(point);pick=reg['diagnostic_picks'][name];error=math.dist(pred,pick)
    diagnostics.append(dict(id=name,pixel_pick=pick,world_mm=list(point),projected_px=pred,residual_px=error,within_diagnostic_pick_allowance=error<=reg['pick_uncertainty_px'],use='check_only_not_fitting'))
cr=read(a.candidate/'report.json');cnative=a.candidate/cr['native_file'];assert sha(cnative)==cr['native_sha256'];doc=App.openDocument(str(cnative))
try:
    link=doc.getObject('RearControlChannelStock');s=link.LinkedObject.Shape.copy();pose=doc.Root.getGlobalPlacement().multiply(link.LinkPlacement);s.Placement=pose
finally:App.closeDocument(doc.Name)
im=Image.open(source).convert('RGB');assert list(im.size)==reg['image_size_px'];draw=ImageDraw.Draw(im)
for c,radius in [(center,190.5),(outer_center,304.8)]:
    pts=[uv(c+App.Vector(radius*math.cos(t),0,radius*math.sin(t))) for t in np.linspace(0,2*math.pi,361)]
    draw.line([tuple(p) for p in pts],fill='#187bb5',width=2)
for edge in s.Edges:
    points=edge.discretize(Deflection=.5)
    draw.line([tuple(uv(v)) for v in points],fill='#d66d16',width=2)
for q in diagnostics:
    u,v=q['pixel_pick'];x,y=q['projected_px'];draw.ellipse((u-4,v-4,u+4,v+4),outline='#c4237e',width=2)
    draw.line((u,v,x,y),fill='#c4237e',width=1);draw.line((x-3,y,x+3,y),fill='#c4237e',width=2);draw.line((x,y-3,x,y+3),fill='#c4237e',width=2)
draw.text((1150,697),'Blue: saved drum radii. Orange: channel stock. Magenta: checks.',fill='#1b1b1b')
im.save(out/'source_overlay.png')
im.crop((1140,690,1680,950)).resize((1620,780)).save(out/'rear_side_detail.png')
write(out/'assessment.json',dict(registration_sha256=sha(rp),registration_reused_without_refit=True,camera=camera,source_sha256=sha(source),native_sha256=sha(native),channel_native_sha256=sha(cnative),reviewer_script_sha256=sha(Path(__file__)),anchor_bindings=bindings,checks=diagnostics,images={n:sha(out/n) for n in ['source_overlay.png','rear_side_detail.png']},detail_pixel_transform=dict(crop_original_px=[1140,690,1680,950],display_scale=3),historical_geometry_qualified=False,camera_fitted=False,
    scope='Fixed conditional local side comparison only. Existing drum diameter provides registration scale; outside drum and control bore are checks. Channel shape was estimated using this source and is not an independent validation feature.',
    diagnostic_note='A control-pin mismatch is retained for source/lever/rod diagnosis. Do not refit the registration to make it vanish; uncertain component geometry and schematic projection remain competing causes.'))
print('Fixed local registration reused;',[(d['id'],round(d['residual_px'],3)) for d in diagnostics],flush=True)
