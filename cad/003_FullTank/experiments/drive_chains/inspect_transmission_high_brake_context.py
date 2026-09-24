"""Measure saved high-speed drums and reserve source-sized lining envelopes."""
import argparse
from pathlib import Path
import sys
import FreeCAD as App
import Part

H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();base=a.candidate.resolve()
r=read(base/'report.json');m=read(base/'isolated/manifest.json')
assert sha(base/r['native_file'])==r['native_sha256']==m['native_sha256']
rows={v['name']:v for v in m['occurrences']};cache={}
def shape(row):
    d=m['definitions'][row['definition']]
    if row['definition'] not in cache:
        assert sha(d['brep_path'])==d['brep_sha256']
        s=Part.Shape();s.read(d['brep_path']);assert s.isValid() and len(s.Solids)==1
        cache[row['definition']]=s
    s=cache[row['definition']].copy()
    s.Placement=App.Placement(App.Matrix(*row['frame']))
    return s

results=[]
for hand in ['Port','Starboard']:
    row=rows[hand+'TransmissionCore_high_drum'];world=shape(row)
    local=cache[row['definition']]
    faces=[f for f in local.Faces if isinstance(f.Surface,Part.Cylinder)
           and abs(f.Surface.Radius-190.5)<1e-6 and abs(abs(f.Surface.Axis.y)-1)<1e-7]
    assert len(faces)==1
    f=faces[0];b=f.optimalBoundingBox(False,False);center_y=(b.YMin+b.YMax)/2
    center=world.Placement.multVec(App.Vector(0,center_y,0))
    width=47.625;ri=190.5;ro=ri+6.35+4.7625
    # A full annulus is conservative: later physical bands have an opening.
    envelope=Part.makeCylinder(ro,width,center+App.Vector(0,-width/2,0),App.Vector(0,1,0)).cut(
        Part.makeCylinder(ri,width,center+App.Vector(0,-width/2,0),App.Vector(0,1,0)))
    near=[]
    for other in m['occurrences']:
        if other['name']==row['name']: continue
        s=shape(other)
        if not s.BoundBox.intersect(envelope.BoundBox):continue
        common=s.common(envelope)
        near.append(dict(name=other['name'],distance_mm=s.distToShape(envelope)[0],
            intersection_valid=common.isValid(),solid_overlap_mm3=sum(t.Volume for t in common.Solids)))
    results.append(dict(receiver=row['name'],frame=row['frame'],center_world_mm=list(center),
        source_lining_width_mm=width,source_lining_stock_mm=6.35,drum_radius_mm=f.Surface.Radius,
        drum_local_axial_faces_mm=[b.YMin,b.YMax],drum_width_mm=b.YMax-b.YMin,
        centered_lining_overhang_each_mm=(width-b.YMax+b.YMin)/2,
        friction_width_coverage_fraction=(b.YMax-b.YMin)/width,
        candidate_neighbors=near))
write(a.output,dict(native_sha256=m['native_sha256'],inspector_sha256=sha(Path(__file__)),
    standard_modified=False,geometry_added=False,drums=results,
    scope='Saved drum dimensions and conservative full-ring neighbor audit. No contact, historical shape or installation qualification.'))
print([(x['receiver'],x['drum_width_mm'],len(x['candidate_neighbors'])) for x in results])
