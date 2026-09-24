from pathlib import Path
import json
import FreeCAD as App
import Part
H=Path('/home/cyapp/MarkVIIILiberty/cad/003_FullTank/experiments/drive_chains');m=json.loads((H/'transmission_brake_anchor_study/trial01/isolated/manifest.json').read_text())
def load(n):
 s=Part.Shape();s.read(m['definitions'][n]['brep_path']);return s
rows=[]
for role,radius in [('low',312.7375),('track',319.0875)]:
 f=load('Def_BrakeAnchor_'+role+'_bracket');g=load('Def_BrakeBand_'+role+'_band')
 fs=[s for s in f.Faces if isinstance(s.Surface,Part.Cylinder) and abs(s.Surface.Radius-radius)<1e-7];gs=[s for s in g.Faces if isinstance(s.Surface,Part.Cylinder) and abs(s.Surface.Radius-radius)<1e-7]
 for i,one in enumerate(fs):
  matching=[s for s in gs if one.Surface.Axis.cross(s.Surface.Axis).Length<1e-7 and (one.Surface.Center-s.Surface.Center).cross(s.Surface.Axis).Length<1e-7]
  restricted=[s for s in matching if s.BoundBox.YMin<=one.BoundBox.YMin+1e-7 and s.BoundBox.YMax>=one.BoundBox.YMax-1e-7]
  a=one.cut(Part.makeCompound(restricted));b=one.cut(Part.makeCompound(matching));b.exportBrep(str(Path(role+'_uncovered.brep')))
  row=dict(role=role,face=i,foot_faces=len(fs),support_faces=len(gs),restricted_faces=len(restricted),matched_faces=len(matching),restricted_uncovered=[len(a.Faces),a.Area],all_uncovered=[len(b.Faces),b.Area],support_extents=[[s.BoundBox.YMin,s.BoundBox.YMax] for s in gs]);rows.append(row);print(row,flush=True)
Path('report.json').write_text(json.dumps(rows,indent=2)+'\n')
