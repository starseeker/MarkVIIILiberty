"""Saved low selectors and corrected diagonal links, with fixed local source registration."""
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
COLORS.update(Shaft=(.36,.51,.65),Nut=(.66,.57,.39),Keeper=(.81,.63,.31),Plate=(.42,.58,.43),Bolt=(.69,.59,.38),Lock=(.65,.58,.38),Floor=(.70,.72,.70),Swing_Link=(.45,.55,.70),Lever=(.27,.46,.65),Rod=(.72,.54,.25),Fork=(.57,.62,.67),Pin=(.66,.57,.39),Cotter=(.81,.63,.31),Receiver=(.50,.55,.60),Low_Link=(.58,.49,.66),Selector=(.31,.55,.72),Washer=(.66,.57,.39))
V=App.Vector;main=V(*d['foundation']['shafts']['Main']['center_world_mm']);rear=V(*d['foundation']['shafts']['Swing']['center_world_mm'])
def item(name,q,role):return dict(id=name,shape=q,target=SimpleNamespace(Shape=q),definition=name,system=role.title(),representation='assembly')
items=[]
for name in s.rows:
    if name.startswith('hull_floor'):continue
    items.append(item(name,s.world(name),r['specs'][name]['role']))
shaded(items,out/'isometric.svg',(-1,-1,.8),'Driver controls | low selectors, upper pin joints and diagonal M762 links | floors omitted')
detail=[]
for v in items:
    q=v['shape'].common(Part.makeBox(1400,1200,2000,V(rear.x-100,-600,500)))
    if q.Faces:detail.append(item(v['id']+'Detail',q,v['system']))
shaded(detail,out/'driver_detail.svg',(-1,-1,.7),'Driver detail | low selector jaws and complete upper joints | operating handles and high selectors unfinished')
box=Part.makeBox(1900,65,1500,V(5800,153,500));section=[]
for name in s.rows:
    if not (name.startswith(('hull_floor','PortDriverLow')) or name in ['DriverMainShaft','DriverSwingShaft','PortLowIntermediateRocker']):continue
    q=s.world(name).common(box)
    if q.Faces:section.append(item(name+'Section',q,r['specs'][name]['role']))
shaded(section,out/'low_section.svg',(0,1,0),'Low-speed section | diagonal M762 joins upper M790 to rear M761 | complete rods and actual sloping floor')
reg=read(ROOT/d['foundation']['controls']['registration']);src=ROOT/reg['source_image'];assert sha(src)==reg['source_image_sha256'];scale=reg['pixels_per_mm'];xp=reg['world_plus_x_image_unit'];yp=reg['world_plus_y_image_unit'];center=reg['image_center_px']
plan=Image.open(src)
side_source=ROOT/'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate113.png'
side=Image.open(side_source).crop((0,0,590,650)).transpose(Image.Transpose.ROTATE_90)
coef=complex(179,-10)/complex(reg['shaft_separation_mm'],-20)
afit,bfit=coef.real,coef.imag

def project(v,view):
    if view=='plan':
        return np.column_stack([center[0]+scale*((v[:,0]-main.x)*xp[0]+v[:,1]*yp[0]),center[1]+scale*((v[:,0]-main.x)*xp[1]+v[:,1]*yp[1]),v[:,2]])
    x,z=-(v[:,0]-main.x),-(v[:,2]-main.z)
    return np.column_stack([315+afit*x-bfit*z,322+bfit*x+afit*z,v[:,1]])

def encode(img):
    buf=io.BytesIO();img.save(buf,format='PNG');return base64.b64encode(buf.getvalue()).decode()
for view,background,box,title in [('plan',plan,'60 195 520 300','SNL6 fixed local plan | registration reused; source-informed static hand pose'),('side',side,'0 0 650 530','HB113 local side | two shaft anchors; link profile inferred, not a holdout')]:
    width,height=background.size;triangles=[];colors=[];lines=[]
    for name,row in s.rows.items():
        if name.startswith('hull_floor'):continue
        if view=='side' and not (name.startswith(('DriverMain','DriverSwing','DriverClutch','PortDriverLow')) or name=='PortClutchDriverSwingLink'):continue
        role=r['specs'][name]['role'];color=[24,112,203] if role in ['lever','shaft','selector'] else [182,73,13] if role in ['swing_link','rod'] else [19,121,67] if role=='plate' else [110,80,130]
        vertices,indices=s.definition(row['definition']).tessellate(.7);frame=np.array(row['frame']).reshape(4,4);v=np.array([list(p) for p in vertices])@frame[:3,:3].T+frame[:3,3];cells=project(v,view)[np.array(indices)];triangles.append(cells);colors.append(np.tile(color,(len(cells),1)))
        for edge in s.world(name).Edges:
            points=np.array([list(p) for p in edge.discretize(Deflection=1.)]);coords=' '.join(f'{x:.3f},{y:.3f}' for x,y,z in project(points,view));lines.append(f'<polyline points="{coords}" fill="none" stroke="rgb({color[0]},{color[1]},{color[2]})" stroke-width=".65" opacity=".55"/>')
    pixels,depth=paint(np.concatenate(triangles),np.concatenate(colors),width,height,out.parent/'runtime')
    layer=Image.fromarray(np.dstack([pixels,np.where(np.isfinite(depth),55,0).astype(np.uint8)]))
    bx,by,bw,bh=[float(v) for v in box.split()]
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="{round(1300*bh/bw)}" viewBox="{box}">',f'<image width="{width}" height="{height}" href="data:image/png;base64,{encode(background)}"/>',f'<image width="{width}" height="{height}" href="data:image/png;base64,{encode(layer)}"/>',*lines,f'<rect x="{bx}" y="{by}" width="{bw}" height="20" fill="white" opacity=".94"/>',f'<text x="{bx+5}" y="{by+13}" font-family="sans-serif" font-size="8">{title}</text>','</svg>']
    path=out/('source_'+view+'.svg');path.write_text('\n'.join(svg))
    with fitz.open(stream=path.read_bytes(),filetype='svg') as doc:doc[0].get_pixmap().save(str(path.with_suffix('.png')))
# Quantify the source-informed handle construction pick from the saved cap,
# not a builder dimension echoed back or a newly fitted camera.
local=s.definition('Def_DriverClutchLever_M772');cap=[f.Surface for f in local.Faces if isinstance(f.Surface,Part.Sphere)][0]
end=cap.Center*(1+cap.Radius/cap.Center.Length);tip=pose(s.rows['DriverClutchOperatingLever']['frame']).multVec(end)
tip_px=project(np.array([list(tip)]),'plan')[0,:2];source_tip=np.array([122.,462.])
standard=read(H/'transmission_brake_front_study/trial01/standard_context_manifest.json');nose_row=next(v for v in standard['occurrences'] if v['name']=='hull_front_slope');entry=standard['definitions'][nose_row['definition']];assert sha(entry['brep_path'])==entry['brep_sha256'];nose=Part.Shape();nose.read(entry['brep_path']);nose.Placement=pose(nose_row['frame']);nose_gap=s.world('DriverClutchOperatingLever').distToShape(nose)[0]
images=['isometric.png','driver_detail.png','low_section.png','source_plan.png','source_side.png']
write(out/'render_receipt.json',dict(native_sha256=sha(s.native),manifest_sha256=sha(out/'isolated/manifest.json'),renderer_sha256=sha(Path(__file__)),images={n:sha(out/n) for n in images},registration=d['foundation']['controls']['registration'],registration_sha256=sha(ROOT/d['foundation']['controls']['registration']),side_source=str(side_source.relative_to(ROOT)),side_source_sha256=sha(side_source),side_registration=dict(crop=[0,0,590,650],rotation='90degrees counterclockwise',main_shaft_px=[315,322],swing_shaft_px=[494,312],complex_scale=[afit,bfit],independent_validation=False),source_camera_refitted=False,hand_plan_construction_comparison=dict(source_tip_px=list(source_tip),saved_tip_px=list(tip_px),residual_px=float(np.linalg.norm(tip_px-source_tip)),independent_validation=False),hand_to_nose_minimum_distance_mm=nose_gap,scope='Actual saved solids with low selectors and corrected diagonal M762. Selector form and axial stack are estimates; high selectors and operating handles remain unbuilt. HB93 is used qualitatively, without an underconstrained metric camera fit.  floors omitted only in isometric/detail and clipped only in section. Fixed plan registration reused. Local HB113 shaft-anchored side comparison records construction picks, not independent validation. No matching source pose claimed.'))
print('Rendered low selectors, actual upper joints and fixed source comparisons.',flush=True)
