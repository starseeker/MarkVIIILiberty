"""Saved driver foundation, real mount section and fixed local source overlay."""
import argparse,base64,io
import numpy as np
from PIL import Image
from pathlib import Path
from types import SimpleNamespace
import fitz
from control_rebuild_io_v2 import *
from lib.raster import paint
from lib.camera_review import validate_native_bindings
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report;d=r['details'];c=d['controls'];out=s.folder
validate_native_bindings(dict(native_file=str(s.native),render_occurrences=list(s.rows),landmarks=[]),s.manifest)
COLORS.update(Shaft=(.36,.51,.65),Nut=(.58,.60,.48),Keeper=(.81,.63,.31),Plate=(.42,.58,.43),Bolt=(.69,.59,.38),Lock=(.65,.58,.38),Floor=(.70,.72,.70))
items=[];origin=App.Vector(*d['plate_origin_world_mm']);main=App.Vector(*d['shafts']['Main']['center_world_mm']);rear=App.Vector(*d['shafts']['Swing']['center_world_mm'])
for name,row in s.rows.items():
    q=s.world(name)
    if name.startswith('hull_floor'):
        q=q.common(Part.makeBox(main.x-rear.x+210,820,600,App.Vector(rear.x-120,-410,650)))
    items.append(dict(id=name,shape=q,target=SimpleNamespace(Shape=q),definition=name,system=r['specs'][name]['role'].title(),representation='assembly'))
shaded(items,out/'isometric.svg',(-1,-1,.9),'Driver foundation | two shafts, partial seat-support plates, eight real floor mounts')
shaded([v for v in items if v['system']!='Floor'],out/'plan.svg',(0,0,1),'Driver foundation plan | source-counted retainers and separate M782 / M783 shafts')
section=[];box=Part.makeBox(main.x-rear.x+200,65,600,App.Vector(rear.x-110,276,650))
for item in items:
    q=item['shape'].common(box)
    if q.Faces:section.append(dict(item,shape=q,target=SimpleNamespace(Shape=q),definition=item['id']+'Section'))
shaded(section,out/'mount_section.svg',(0,1,.12),'Port mount section | source-length bolts through side-plate feet and actual sloping floor')
reg=read(ROOT/c['registration']);src=ROOT/reg['source_image'];assert sha(src)==reg['source_image_sha256'];scale=reg['pixels_per_mm'];xp=reg['world_plus_x_image_unit'];yp=reg['world_plus_y_image_unit'];center=reg['image_center_px']
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="1050" viewBox="210 180 280 287">',f'<image width="1688" height="1075" href="data:image/png;base64,{base64.b64encode(src.read_bytes()).decode()}"/>']
# Rasterize actual saved surfaces in the same fixed XY registration; cylinder
# silhouette edges are absent from an edge-only projection of analytic BReps.
triangles=[];colors=[]
for name,row in s.rows.items():
    if name.startswith('hull_floor'):continue
    vertices,indices=s.definition(row['definition']).tessellate(.6)
    frame=np.array(row['frame']).reshape(4,4);v=np.array([list(p) for p in vertices])@frame[:3,:3].T+frame[:3,3]
    u=center[0]+scale*((v[:,0]-main.x)*xp[0]+v[:,1]*yp[0]);vv=center[1]+scale*((v[:,0]-main.x)*xp[1]+v[:,1]*yp[1]);cells=np.column_stack([u,vv,v[:,2]])[np.array(indices)]
    triangles.append(cells);color=[22,122,46] if r['specs'][name]['role']=='plate' else [0,103,197] if r['specs'][name]['role']=='shaft' else [195,99,0];colors.append(np.tile(color,(len(cells),1)))
pixels,depth=paint(np.concatenate(triangles),np.concatenate(colors),1688,1075,out.parent/'runtime')
rgba=np.dstack([pixels,np.where(np.isfinite(depth),65,0).astype(np.uint8)]);buffer=io.BytesIO();Image.fromarray(rgba).save(buffer,format='PNG')
svg.append(f'<image width="1688" height="1075" href="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"/>')
for item in items:
    if item['system']=='Floor':continue
    color='#167a2e' if item['system']=='Plate' else '#0067c5' if item['system']=='Shaft' else '#c36300'
    svg.append(f'<g fill="none" stroke="{color}" stroke-width="0.65" opacity=".68"><title>{item["id"]}</title>')
    for edge in item['shape'].Edges:
        points=edge.discretize(Deflection=.8)
        coords=' '.join(f'{center[0]+scale*((p.x-main.x)*xp[0]+p.y*yp[0]):.3f},{center[1]+scale*((p.x-main.x)*xp[1]+p.y*yp[1]):.3f}' for p in points)
        svg.append(f'<polyline points="{coords}"/>')
    svg.append('</g>')
for point in reg['construction_picks'].values():svg.append(f'<circle cx="{point[0]}" cy="{point[1]}" r="2.5" fill="none" stroke="#b32642" stroke-width=".6"/>')
svg+=['<rect x="210" y="180" width="280" height="27" fill="white" opacity=".94"/>','<text x="214" y="186" font-family="sans-serif" font-size="4.5">SNL6 local plan registration | construction picks, not independent validation</text>','<text x="214" y="193" font-family="sans-serif" font-size="4.5">Blue: shafts  Green: estimated plates  Orange: hardware  Red: source picks</text>','<text x="214" y="200" font-family="sans-serif" font-size="4.5">Seat attachments and controls pending; no fit across broken rods</text>','</svg>']
path=out/'source_plan.svg';path.write_text('\n'.join(svg))
with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),images={n:sha(out/n) for n in ['isometric.png','plan.png','mount_section.png','source_plan.png']},registration= c['registration'],registration_sha256=sha(ROOT/c['registration']),source_camera_refitted=False,scope='Actual saved prototype with display-only clipped floors and port section. Source plan similarity reused unchanged; construction anchors are not validation holdouts.'))
print('Rendered driver foundation and registered source plan.',flush=True)
