"""Render actual saved combined rear support family and compare them through the unchanged local source registration."""
import argparse
from pathlib import Path
import sys
from types import SimpleNamespace
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
import FreeCAD as App
import Part
from lib.evidence import read,write,sha
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
from lib.source_camera import project

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==m['native_sha256']==r['native_sha256']
r['parent_native']=r['source_native'];r['parent_native_sha256']=r['source_native_sha256']
parent=ROOT/r['parent_native'];old=read(parent.parent/'isolated/manifest.json');assert sha(parent)==old['native_sha256']==r['parent_native_sha256']
prototype=read(ROOT/r['prototype']/'report.json')
r['specs']=prototype['specs']
rows={v['name']:v for v in m['occurrences'] if v['name'] in r['specs']};prior={v['name']:v for v in old['occurrences']}
context_names=[n for n in prior if n.startswith(('RearChannelLeftCleat', 'ClutchSupport_')) or any(v.endswith('ControlFulcrum') for v in prior[n].get('owners', []))]
validate_native_bindings(dict(native_file=str(native),render_occurrences=list(rows),landmarks=[]),m)
validate_native_bindings(dict(native_file=str(parent),render_occurrences=context_names,landmarks=[]),old)
COLORS.update(Channel=(.69,.48,.28),Bracket=(.57,.59,.47),Lever=(.39,.54,.61),Hardware=(.73,.67,.50),Cleat=(.44,.53,.56),Context=(.46,.53,.54),Floor=(.48,.54,.52))
cache={};shapes={};items=[];floor=[]
def item(name,row,manifest,system):
    d=manifest['definitions'][row['definition']];key=d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path'])==key;s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[key]=s
    s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));shapes[name]=s
    return dict(id=name,shape=s,target=SimpleNamespace(Shape=cache[key]),definition=key,system=system,representation='assembly')
for name,row in rows.items():
    role=r['specs'][name]['role'];system='Channel' if role=='channel' else 'Floor' if role=='floor' else 'Cleat' if role=='cleat' else 'Bracket' if role.endswith('bracket') else 'Hardware'
    (floor if role=='floor' else items).append(item(name,row,m,system))
for name in context_names:
    v=item(name,prior[name],old,'Floor' if name=='hull_floor_7' else 'Context')
    (floor if name=='hull_floor_7' else items).append(v)
shaded(items,out/'support_family_isometric.svg',(-1,-1,.8),'Rear controls | installed M4135 / M4136 / M4129 support family',context=floor)
shaded([v for v in items if v['id'].startswith(('PortLowSpring','PortRightChannelCleat'))],out/'support_family_detail.svg',(1,-1,.65),'Estimated M4129 cleat under M4136 | four source rivets shared across both sides')
regpath=H/'transmission_controls_study/channel_local_registration01.json';reg=read(regpath);source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
camera=dict(projection='orthographic',image_size_px=reg['image_size_px'],world_to_camera_rotation=[[-1,0,0],[0,0,-1],[0,-1,0]],origin_world_mm=reg['axis_world_mm'],scale_px_per_mm=reg['pixels_per_mm'],principal_px=reg['center_px'])
im=Image.open(source).convert('RGB');draw=ImageDraw.Draw(im)
for name in rows:
    if name!='RearControlChannelStock' and not name.startswith('Port'):continue
    role=r['specs'][name]['role'];color='#d26e19' if role=='channel' else '#1d7ea3' if role.startswith('lever') else '#74794d'
    for edge in shapes[name].Edges:
        pts=edge.discretize(Deflection=.35);uv=project([[v.x,v.y,v.z] for v in pts],camera)[:,:2]
        if len(uv)>1:draw.line([tuple(v) for v in uv],fill=color,width=1)
draw.text((1130,690),'Fixed side registration; estimated support family. No plan calibration.',fill='#111111')
im.save(out/'source_overlay.png');im.crop((1130,685,1680,970)).resize((1650,855)).save(out/'source_detail.png')
write(out/'render_receipt.json',dict(native_sha256=sha(native),manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),parent_native_sha256=sha(parent),source_registration_sha256=sha(regpath),camera=camera,source_camera_refitted=False,images={n:sha(out/n) for n in ['support_family_isometric.png','support_family_detail.png','source_overlay.png','source_detail.png']},scope='22 affected saved occurrences from the full3246-part development native, plus retained mounts/fulcrums/clutch support; floor is translucent context. Source side projection diagnoses the conditional layout; no historical perspective or plan fit.',historical_geometry_qualified=False))
print('Rendered spring supports and fixed-registration source overlay.',flush=True)
