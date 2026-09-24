"""Render saved channel attachments and reuse the existing local side registration."""
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
r=read(out/'report.json');m=read(out/'isolated/manifest.json');native=out/r['native_file'];assert sha(native)==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};validate_native_bindings(dict(native_file=str(native),render_occurrences=list(rows),landmarks=[]),m)
cache={};shapes={};items=[];floor=[]
COLORS.update(Channel=(.69,.48,.28),Cleat=(.44,.53,.56),Bolt=(.69,.70,.69),Rivet=(.75,.64,.44),Floor=(.48,.54,.52))
for name,row in rows.items():
    d=m['definitions'][row['definition']];key=d['brep_sha256']
    if key not in cache:
        assert sha(d['brep_path'])==key;s=Part.Shape();s.read(d['brep_path']);assert s.Placement.isIdentity();cache[key]=s
    s=cache[key].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));shapes[name]=s
    role=r['specs'][name]['role'];system='Channel' if role=='channel' else 'Cleat' if role=='cleat' else 'Floor' if role=='floor' else 'Rivet' if role=='rivet' else 'Bolt'
    item=dict(id=name,shape=s,target=SimpleNamespace(Shape=cache[key]),definition=key,system=system,representation='assembly')
    (floor if role=='floor' else items).append(item)
shaded(items,out/'channel_mount_isometric.svg',(-1,-1,.65),'Rear control channel | four riveted M4130 cleats and floor bolt sets',context=floor)
# A labeled display-only section exposes both heads and the under-floor nut.
chosen='RearChannelLeftCleat4';q=App.Placement(App.Matrix(*rows[chosen]['frame'])).Base
box=Part.makeBox(240,210,150,App.Vector(q.x-120,q.y-105,q.z-60));context=[]
for name in ['RearControlChannelStock','hull_floor_7']:
    cut=Part.makeCompound([shapes[name].common(box)]);assert cut.Placement.isIdentity()
    context.append(dict(id=name+'_display_section',shape=cut,target=SimpleNamespace(Shape=cut),definition=name+'_unique_display_section',system='Channel' if name=='RearControlChannelStock' else 'Floor',representation='assembly'))
shaded([v for v in items if v['id'].startswith(chosen)],out/'cleat_mount_detail.svg',(-1,-1,.5),'M4130 mount | complete bolt/rivet retention; channel and floor shown in section',context=context)
rp=H/'transmission_controls_study/channel_local_registration01.json';reg=read(rp);source=ROOT/reg['source_image'];assert sha(source)==reg['source_sha256']
camera=dict(projection='orthographic',image_size_px=reg['image_size_px'],world_to_camera_rotation=[[-1,0,0],[0,0,-1],[0,-1,0]],origin_world_mm=reg['axis_world_mm'],scale_px_per_mm=reg['pixels_per_mm'],principal_px=reg['center_px'])
im=Image.open(source).convert('RGB');draw=ImageDraw.Draw(im)
for name,s in shapes.items():
    if name!='RearControlChannelStock' and not name.startswith(chosen):continue
    color='#d26e19' if name=='RearControlChannelStock' else '#1d7ea3'
    for edge in s.Edges:
        pts=edge.discretize(Deflection=.35);uv=project([[v.x,v.y,v.z] for v in pts],camera)[:,:2]
        if len(uv)>1:draw.line([tuple(v) for v in uv],fill=color,width=1)
draw.text((1145,697),'Fixed registration: orange channel, blue representative mounting.',fill='#111111')
im.save(out/'source_overlay.png');im.crop((1140,690,1680,970)).resize((1620,840)).save(out/'source_detail.png')
write(out/'render_receipt.json',dict(native_sha256=sha(native),manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),images={n:sha(out/n) for n in ['channel_mount_isometric.png','cleat_mount_detail.png','source_overlay.png','source_detail.png']},source_registration_sha256=sha(rp),camera=camera,source_camera_refitted=False,display_cut_only=True,historical_geometry_qualified=False,scope='Saved30-occurrence mounting prototype. Local source overlay reuses side registration; HB104 remains an uncalibrated qualitative topology reference.'))
print('Rendered saved mounting assembly, detail and unchanged local source registration.',flush=True)
