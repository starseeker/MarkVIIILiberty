import sys,json
from pathlib import Path
R=Path('/home/cyapp/MarkVIIILiberty');H=R/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write
import FreeCAD as A
import Part
p=H/'transmission_high_brake_support_study';m=read(p/'integrated01/isolated/manifest.json');rows={x['name']:x for x in m['occurrences']};center=A.Vector(*read(p/'integrated01/report.json')['interfaces']['PortHighSpeedBrake']['center_world_mm'])
row=rows['PortHighSpeedBrakeShortLiningFastener1'];s=Part.Shape();s.read(m['definitions'][row['definition']]['brep_path']);s.Placement=A.Placement(A.Matrix(*row['frame']));s.translate(-center)
b=Part.Shape();b.read(str(p/'bottom_stops01/anchor_bracket.brep'));c=b.common(s);bb=c.BoundBox
result={'intersection_mm3':c.Volume,'bounds':dict(x=[bb.XMin,bb.XMax],y=[bb.YMin,bb.YMax],z=[bb.ZMin,bb.ZMax]),'fastener_surfaces':[(type(f.Surface).__name__,getattr(f.Surface,'Radius',None),list(f.CenterOfMass)) for f in s.Faces]}
extra=Part.Shape();extra.read(str(p/'bottom_stops01/bracket_addition.brep'));result['addition_intersections']=[v.common(s).Volume for v in extra.Solids];write(p/'bottom_stops01/collision_diagnostic.json',result);print(json.dumps(result,indent=2))
