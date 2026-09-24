"""Inspect saved casing-bridge clearance; section cuts affect display only."""
import argparse,sys
from pathlib import Path
from types import SimpleNamespace
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
from lib.cad_build import COLORS
from lib.visual_review import shaded
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};center=App.Vector(*r['interfaces']['PortHighSpeedBrake']['center_world_mm'])
window=Part.makeBox(50,45.925,30,center+App.Vector(-230,-11.1125,-45))
COLORS.update(Case=(.60,.66,.72),Backing=(.38,.54,.61),Lining=(.70,.47,.25),Copper=(.76,.43,.23))
items=[]
for name,role in [('CenterTransmissionCore_bevel_case','Case'),('PortHighSpeedBrakeLongBand','Backing'),('PortHighSpeedBrakeLongLining','Lining'),('PortHighSpeedBrakeLongLiningFastener11','Copper')]:
 row=rows[name];d=m['definitions'][row['definition']];assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);s.Placement=App.Placement(App.Matrix(*row['frame']))
 cut=s.common(window);assert cut.Solids
 items.append(dict(id=name,shape=cut,target=SimpleNamespace(Shape=cut),definition=name+'_display_section',system=role,representation='assembly'))
shaded(items,out/'high_brake_case_clearance.svg',(1,-2,.5),'Rear casing bridge | display section through estimated clearance recess and source-sized lining rivet')
write(out/'case_render_receipt.json',dict(native_sha256=r['native_sha256'],renderer_sha256=sha(Path(__file__)),image_sha256=sha(out/'high_brake_case_clearance.png'),display_window_mm=[window.BoundBox.XMin,window.BoundBox.YMin,window.BoundBox.ZMin,window.BoundBox.XMax,window.BoundBox.YMax,window.BoundBox.ZMax],physical_geometry_cut=False,historical_profile_qualified=False))
