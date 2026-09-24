"""Known-camera control using real saved transmission geometry, not a historical fit."""
from pathlib import Path
import sys,json,hashlib,argparse
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
import FreeCAD as App
import Part
from lib.camera_review import render,resolve_packet
base=ROOT/'cad/003_FullTank/experiments/drive_chains/transmission_brake_stop_study/trial04'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
m=json.loads((base/'isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
selected=['TransmissionFrame_TopChannel','TransmissionFrame_BottomChannel','PortFixedBearing_inner_bracket','StarboardFixedBearing_inner_bracket']
world=[];anchors=[]
for name in selected:
 row=rows[name];d=m['definitions'][row['definition']];s=Part.Shape();s.read(d['brep_path']);b=s.BoundBox
 matrix=np.array(row['frame']).reshape(4,4)
 for xyz in [(b.XMin,b.YMin,b.ZMin),(b.XMax,b.YMin,b.ZMax),(b.XMin,b.YMax,b.ZMax),(b.XMax,b.YMax,b.ZMin)]:
  world.append(matrix[:3,:3]@xyz+matrix[:3,3]);anchors.append(dict(occurrence=name,local_mm=xyz,definition_sha256=d['brep_sha256'],evidence='Synthetic control: definition bounding-box datum, not a historical image pick'))
world=np.array(world);center=world.mean(axis=0)
direction=np.array([1.,-.65,.45]);direction/=np.linalg.norm(direction)
right=np.cross([0,0,1],direction);right/=np.linalg.norm(right)
up=np.cross(direction,right);R=np.array([right,-up,-direction])
origin=center+direction*4200
camera=dict(projection='perspective',world_to_camera_rotation=R.tolist(),origin_world_mm=origin.tolist(),focal_px=1500.,principal_px=[600.,450.],near_mm=.01,image_size_px=[1200,900])
q=(world-origin)@R.T;uv=q[:,:2]*1500/q[:,2,None]+[600,450]
white=out/'white.png';Image.new('RGB',(1200,900),'white').save(white)
packet=dict(source_image=str(white),image_size_px=[1200,900],projection='perspective',native_file=str(base/'PowertrainWithBrakeStops.FCStd'),manifest=str(base/'isolated/manifest.json'),render_occurrences=selected,landmarks=[],projection_classification='Synthetic known perspective; not historical evidence')
for i,(w,p,a) in enumerate(zip(world,uv,anchors)):
 packet['landmarks'].append(dict(id='L'+str(i),use='holdout' if i%4==3 else 'fit',world_mm=w.tolist(),pixel=p.tolist(),sigma_px=1.,anchor=a))
packet,manifest=resolve_packet(packet)
render(packet,manifest,camera,out/'known',out/'runtime')
packet['source_image']=str(out/'known/geometry.png');packet['source_sha256']=hashlib.sha256(Path(packet['source_image']).read_bytes()).hexdigest()
(out/'packet.json').write_text(json.dumps(packet,indent=2));(out/'known_camera.json').write_text(json.dumps(camera,indent=2))
print('Saved real native geometry / known camera control with 12 fit and 4 holdout anchors')
