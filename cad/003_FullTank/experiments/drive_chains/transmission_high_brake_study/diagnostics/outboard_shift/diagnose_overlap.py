import json,math
from pathlib import Path
import FreeCAD as App
import Part
R=Path('/home/cyapp/MarkVIIILiberty');h=R/'cad/003_FullTank/experiments/drive_chains'
m=json.loads((h/'transmission_brake_spacer_study/trial01/isolated/manifest.json').read_text());rows={v['name']:v for v in m['occurrences']}
def load(name):
 r=rows[name];s=Part.Shape();s.read(m['definitions'][r['definition']]['brep_path']);s.Placement=App.Placement(App.Matrix(*r['frame']));return s
case=load('CenterTransmissionCore_bevel_case');drum=load('PortTransmissionCore_high_drum')
report=json.loads((R/'.work/high-brake/band_probe02/probe.json').read_text());angle=report['details']['placement_angles_rad']['long']
band=Part.Shape();band.read(str(R/'.work/high-brake/band_probe02/long_band.brep'))
results=[]
for shift in [0,.75,2,5,10]:
 center=drum.Placement.multVec(App.Vector(0,222.25,0));center.y+=shift
 s=band.copy();s.Placement=App.Placement(center,App.Rotation(App.Vector(0,1,0),-math.degrees(angle)))
 common=s.common(case);b=common.optimalBoundingBox(False,False)
 results.append(dict(shift=shift,center=list(center),volume=common.Volume,common_bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]))
 if shift==0:common.exportBrep(str(R/'.work/high-brake/initial_case_overlap.brep'))
print(json.dumps(results,indent=2));(R/'.work/high-brake/overlap_diagnosis.json').write_text(json.dumps(results,indent=2)+'\n')
