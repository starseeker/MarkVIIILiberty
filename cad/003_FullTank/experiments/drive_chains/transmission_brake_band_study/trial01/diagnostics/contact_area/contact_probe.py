import sys,json,math
from pathlib import Path
import FreeCAD as App
import Part
ROOT=Path('/home/cyapp/MarkVIIILiberty');out=ROOT/'cad/003_FullTank/experiments/drive_chains/transmission_brake_band_study/trial01'
m=json.loads((out/'isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
def shape(name):
 r=rows[name];s=Part.Shape();s.read(m['definitions'][r['definition']]['brep_path']);s.Placement=App.Placement(App.Matrix(*r['frame']));return s
results=[]
for name in ['PortTrackBrakeLowerSegment1Lining','StarboardTrackBrakeUpperSegment3Lining']:
 one=shape(name);two=shape(('Port' if name.startswith('Port') else 'Starboard')+'TransmissionOutput_drum')
 f=next(f for f in one.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-304.8)<1e-6)
 g=next(f for f in two.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-304.8)<1e-6)
 common=f.common(g);diff=f.cut(g);common_diff=f.cut(common);excess=common.cut(f)
 row=dict(name=name,face_area=f.Area,common_area=common.Area,difference_area=diff.Area,difference_faces=len(diff.Faces),
  common_difference_area=common_diff.Area,common_difference_faces=len(common_diff.Faces),excess_area=excess.Area,excess_faces=len(excess.Faces),
  axis_error=f.Surface.Axis.cross(g.Surface.Axis).Length,
  offset_error=(f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length)
 moved=f.copy();moved.translate(App.Vector(.01,0,0));miss=moved.cut(g)
 row['negative_uncovered_area']=miss.Area;row['negative_uncovered_faces']=len(miss.Faces)
 results.append(row);print(row,flush=True)
Path('contact_probe.json').write_text(json.dumps(results,indent=2))
