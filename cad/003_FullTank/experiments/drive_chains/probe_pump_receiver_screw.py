"""Locate receiver/screw overlap and independently check moved drive vs water."""
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
import FreeCAD as App
import Part
from lib.cad_build import leaves
from lib.evidence import read,write,sha

out=HERE/'engine_pump_receiver_study/trial01/screw_diagnostic';out.mkdir(exist_ok=True)
source=HERE/'engine_pump_layout_study/lower_drive_trial'
dr=read(source/'report.json');wp=HERE/'engine_water_pump_connections_study';wr=read(wp/'report.json')
paths=[source/'DrivetrainWithLowerDriveStudy.FCStd',wp/wr['native_file']]
shapes={};roles={}
for key,path,r in zip(['drive','water'],paths,[dr,wr]):
    assert sha(path)==r['native_sha256'];doc=App.openDocument(str(path));inverse=doc.TankLibertyEngine.getGlobalPlacement().inverse()
    try:
        for row in leaves(doc.Root):
            if not row['id'].startswith('EngineLowerDrive_' if key=='drive' else 'EngineWaterPump_'):continue
            s=row['shape'].copy();s.Placement=inverse.multiply(s.Placement)
            if key=='water':s.translate(App.Vector(0,0,-dr['controls']['pump_axis_drop']-wr['pump_axis_z']))
            shapes[row['id']]=s;roles[row['id']]=key
    finally:App.closeDocument(doc.Name)
pairs=[]
for name,s in shapes.items():
    if roles[name]!='drive':continue
    for other,t in shapes.items():
        if roles[other]!='water' or not s.BoundBox.intersect(t.BoundBox):continue
        volume=abs(s.common(t).Volume);pairs.append(dict(a=name,b=other,overlap_mm3=volume,passed=volume<1e-5))
        write(out/'progress.json',pairs)
case_path=out.parent/'PumpReceiver.FCStd';doc=App.openDocument(str(case_path));case=doc.Def_EngineCase_lower.Shape.copy();App.closeDocument(doc.Name)
screw=shapes['EngineLowerDrive_HousingRetainingScrew'];common=case.common(screw)
def bounds(s):
    b=s.BoundBox;return dict(x=[b.XMin,b.XMax],y=[b.YMin,b.YMax],z=[b.ZMin,b.ZMax])
for name,s in [('case',case),('screw',screw),('overlap',common)]:s.exportBrep(str(out/(name+'.brep')))
result=dict(input_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths+[case_path]},probe_sha256=sha(Path(__file__)),
    drive_water_pairs=pairs,collisions=[row for row in pairs if not row['passed']],
    screw_bounds_mm=bounds(screw),overlap_bounds_mm=bounds(common),overlap_mm3=common.Volume,
    source_screw=dr['controls'],drive_mid_z=dr['datums']['mid_z'],source_head_seat_x=dr['main_apex']+dr['datums']['retaining_screw_span'][1])
write(out/'result.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['source_screw','drive_water_pairs','input_hashes']},indent=2))
