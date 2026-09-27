"""Record actual saved spline nets and reproducible nonphysical backrest sections."""
import argparse
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_seat_parts_v2 import transverse_edge, back_width

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);out=s.folder/'surface_records';out.mkdir(exist_ok=False)
records={}
for name in ['Frame','Cushion','BackPadding']:
    key='Def_DriverSeat_'+name;shape=s.definition(key);faces=[]
    for i,face in enumerate(shape.Faces):
        surf=face.Surface
        if not isinstance(surf,Part.BSplineSurface):continue
        faces.append(dict(face_index=i,degree_u=surf.UDegree,degree_v=surf.VDegree,
                          knots_u=surf.getUKnots(),knots_v=surf.getVKnots(),
                          multiplicities_u=surf.getUMultiplicities(),multiplicities_v=surf.getVMultiplicities(),
                          poles=[[[v.x,v.y,v.z] for v in row] for row in surf.getPoles()],
                          weights=surf.getWeights(),parameter_range=face.ParameterRange,
                          trim_source='Authoritative boundaries are the corresponding saved BRep face; knot net alone does not describe trimming.'))
    records[key]=dict(brep_sha256=s.manifest['definitions'][key]['brep_sha256'],spline_faces=faces)
doc=App.newDocument('SeatBackSectionGuides')
origin=App.Vector(*s.report['details']['origin_world_mm']);width_delta=s.report['details']['width_mm']-480
guides=[]
for z in s.report['details']['curves']['back_section_z_mm']:
    edge=transverse_edge(z,back_width(z,width_delta),0)
    obj=doc.addObject('PartDesign::Feature','BackGuide'+str(z));obj.Shape=edge
    obj.Placement=App.Placement(origin,App.Rotation())
    metadata(obj,Physical=False,Purpose='Source-constrained estimated backrest construction curve; excluded from physical assembly and BOM.',SectionHeightMM=str(z))
    curve=edge.Curve
    guides.append(dict(name=obj.Name,z_mm=z,degree=curve.Degree,poles=[list(v) for v in curve.getPoles()],knots=curve.getKnots(),multiplicities=curve.getMultiplicities()))
doc.recompute();path=out/'SeatBackSectionGuides.FCStd';doc.saveAs(str(path));App.closeDocument(doc.Name)
write(out/'report.json',dict(native_sha256=sha(s.native),worker_sha256=sha(Path(__file__)),
    parts_sha256=sha(H/'driver_seat_parts_v2.py'),surfaces=records,guides=guides,
    nonphysical_guides_native_sha256=sha(path),nonphysical=True,geometry_modified=False,
    fitting_status='Pan endpoints are source construction picks; curved back and cushion are explicitly estimated shapes. No independent fit acceptance or camera refit.',
    constraints=s.report['details']['curves']))
print('Saved actual spline control nets and ten nonphysical section guides',flush=True)
