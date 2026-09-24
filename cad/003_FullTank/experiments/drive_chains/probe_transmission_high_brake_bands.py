"""Save and inspect proposed source-sized strips before modifying the assembly."""
import argparse
from pathlib import Path
import sys
import math
import FreeCAD as App
import Part

H=Path(__file__).resolve().parent;STAGE=H.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(H),str(STAGE)]
from lib.evidence import read,write,sha
from transmission_high_brake_band_parts import parts,rotate_theta

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--controls',type=Path,default=H/'transmission_high_brake_study/band_controls.json')
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
parent=H/'transmission_brake_spacer_study/trial01';pr=read(parent/'report.json')
m=read(parent/'isolated/manifest.json');assert sha(parent/pr['native_file'])==m['native_sha256']
c=read(a.controls)['controls'];shapes,details=parts(c)
for name,s in shapes.items():s.exportBrep(str(out/(name+'.brep')))
rows={v['name']:v for v in m['occurrences']};cache={}
def load(row):
    d=m['definitions'][row['definition']]
    if row['definition'] not in cache:
        assert sha(d['brep_path'])==d['brep_sha256'];s=Part.Shape();s.read(d['brep_path']);cache[row['definition']]=s
    s=cache[row['definition']].copy();s.Placement=App.Placement(App.Matrix(*row['frame']));return s
actual=[];installed=[]
for hand,sign in [('Port',1),('Starboard',-1)]:
    drum=load(rows[hand+'TransmissionCore_high_drum'])
    center=drum.Placement.multVec(App.Vector(0,222.25,0))
    center.y+=sign*c['axial_outboard_shift']
    for role in ['long','short']:
        pose=App.Placement(center,rotate_theta(details['placement_angles_rad'][role]))
        for leaf in ['lining','band']:
            key=role+'_'+leaf;name=hand+'HighSpeedBrake_'+key
            s=Part.Shape();s.read(str(out/(key+'.brep')));s.Placement=pose
            installed.append((name,s))
            for other in m['occurrences']:
                neighbor=load(other)
                if not s.BoundBox.intersect(neighbor.BoundBox):continue
                common=s.common(neighbor);volume=sum(t.Volume for t in common.Solids)
                if volume>1e-6 or not common.isValid():
                    actual.append(dict(new=name,existing=other['name'],overlap_mm3=volume,intersection_valid=common.isValid()))
    print(hand,'examined',flush=True)
for i,(name,s) in enumerate(installed):
    for other,t in installed[i+1:]:
        if not s.BoundBox.intersect(t.BoundBox):continue
        common=s.common(t);volume=sum(v.Volume for v in common.Solids)
        if volume>1e-6 or not common.isValid():actual.append(dict(new=name,other_new=other,overlap_mm3=volume,intersection_valid=common.isValid()))
write(out/'probe.json',dict(native_sha256=m['native_sha256'],controls_sha256=sha(a.controls),controls=c,details=details,
    shape_hashes={k:sha(out/(k+'.brep')) for k in shapes},interferences=actual,
    passed_no_detected_interference=not actual,assembly_modified=False,
    scope='Eight proposed band/lining solids against all inherited development geometry. Does not qualify source, receiving features, contact or full installation.'))
print('Interferences:',actual,flush=True)
