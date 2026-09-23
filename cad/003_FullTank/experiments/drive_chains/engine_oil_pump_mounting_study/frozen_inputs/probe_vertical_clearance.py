"""Test why a rigid upward pump shift alone cannot resolve the floor fit."""
from pathlib import Path
import sys
ROOT=Path('/home/cyapp/MarkVIIILiberty')
BASE=ROOT/'cad/003_FullTank/experiments/drive_chains'
sys.path[:0]=[str(BASE),str(BASE.parents[1])]
import FreeCAD as App
import Part
from lib.cad_build import leaves
from lib.evidence import read,write,sha

out=BASE/'engine_oil_pump_mounting_study/diagnostics/current_context'
r=read(BASE/'engine_oil_pump_mounting_study/report.json')
pr=read(BASE/'engine_water_pump_connections_study/report.json')
native=BASE/'engine_oil_pump_mounting_study'/r['native_file']
parent=BASE/'engine_water_pump_connections_study'/pr['native_file']
assert sha(native)==r['native_sha256'] and sha(parent)==pr['native_sha256']
doc=App.openDocument(str(parent));pd=App.openDocument(str(native))
try:
    inverse=doc.TankLibertyEngine.getGlobalPlacement().inverse()
    rows={x['id']:x for x in leaves(doc.Root)}
    def neighbor(name):
        s=rows[name]['shape'].copy();s.Placement=inverse.multiply(s.Placement);return s
    floor=neighbor('hull_floor_5')
    pump={}
    for row in r['occurrences']:
        link=pd.getObject(row['name']);s=link.LinkedObject.Shape.copy()
        s.Placement=App.Placement(App.Vector(r['controls']['pump_axis_x'],0,r['controls']['pump_mount_z']),App.Rotation()).multiply(pd.getObject(row['assembly']).getGlobalPlacement()).multiply(link.LinkPlacement).multiply(s.Placement)
        pump[row['name']]=s
    original_low=min(s.BoundBox.ZMin for s in pump.values())
    required_shift=floor.BoundBox.ZMax-original_low
    clearance=1.
    shift=required_shift+clearance
    selected=['EngineOilPump_UpperBody','EngineOilPump_UpperFilterFrame','EngineOilPump_DrivingShaft']
    # Use the occurrence carrying the actual shaft definition, not a guessed name.
    selected[-1]=next(x['name'] for x in r['occurrences'] if x['key']=='shaft')
    pairs=[]
    for name in selected:
        s=pump[name].copy();s.translate(App.Vector(0,0,shift))
        for target in ['EngineWaterPump_GearedShaft','EngineWaterPump_BearingRetainer','EngineLowerDrive_IntegralDriver']:
            t=neighbor(target)
            overlap=abs(s.common(t).Volume) if s.BoundBox.intersect(t.BoundBox) else 0.
            pairs.append(dict(pump=name,neighbor=target,overlap_mm3=overlap,clear=overlap<1e-5))
            write(out/'vertical_clearance_progress.json',pairs)
            print(name,target,overlap,flush=True)
    result=dict(status='Rigid-shift diagnostic, not a selected installation',
        native_sha256=sha(native),parent_native_sha256=sha(parent),checker_sha256=sha(Path(__file__)),
        floor_engine_z=[floor.BoundBox.ZMin,floor.BoundBox.ZMax],lowest_pump_engine_z=original_low,
        minimum_upward_shift_for_floor_mm=required_shift,trial_clearance_mm=clearance,trial_shift_mm=shift,
        trial_mount_z=r['controls']['pump_mount_z']+shift,pairs=pairs,
        rigid_shift_alone_rejected=any(not x['clear'] for x in pairs),
        floor_clear_by_full_envelope=(original_low+shift>floor.BoundBox.ZMax),
        source_documents_unchanged=sha(native)==r['native_sha256'] and sha(parent)==pr['native_sha256'])
    write(out/'vertical_clearance.json',result)
    print(result,flush=True)
finally:
    App.closeDocument(pd.Name);App.closeDocument(doc.Name)
