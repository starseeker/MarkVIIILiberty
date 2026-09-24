"""Locate missing water-shim backing; compare the previously qualified case."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
import FreeCAD as App
import Part
from lib.cad_build import leaves
from lib.evidence import read,write,sha

out=HERE/'engine_pump_receiver_study/trial02/shim_diagnostic';out.mkdir(exist_ok=True)
wp=HERE/'engine_water_pump_connections_study';wr=read(wp/'report.json')
parent=App.openDocument(str(wp/wr['native_file']));inverse=parent.TankLibertyEngine.getGlobalPlacement().inverse()
items={r['id']:r for r in leaves(parent.Root)}
shim=items['EngineWaterPump_RetainerAdjustmentShim']['shape'].copy();shim.Placement=inverse.multiply(shim.Placement)
old=items['EngineCase_lower']['shape'].copy();old.Placement=inverse.multiply(old.Placement)
App.closeDocument(parent.Name)
def bounds(s):
    b=s.BoundBox;return [b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax]
checks=[]
for key,path,dz in [('previous',None,0),('trial01',out.parents[1]/'trial01/PumpReceiver.FCStd',12.55),('trial02',out.parent/'PumpReceiver.FCStd',12.55)]:
    s=shim.copy();s.translate(App.Vector(0,0,dz));land=s.copy();land.translate(App.Vector(-s.BoundBox.XLength-.05,0,0))
    if path:
        doc=App.openDocument(str(path));case=doc.Def_EngineCase_lower.Shape.copy();App.closeDocument(doc.Name)
    else:case=old.copy()
    missing=land.cut(case)
    solids=[dict(volume_mm3=b.Volume,bounds_mm=bounds(b),center_mm=list(b.CenterOfMass)) for b in missing.Solids]
    missing.exportBrep(str(out/(key+'_missing.brep')))
    checks.append(dict(candidate=key,shim_bounds_mm=bounds(s),missing_mm3=missing.Volume,solids=solids))
write(out/'result.json',dict(checks=checks,probe_sha256=sha(Path(__file__))))
for row in checks:print(row,flush=True)
