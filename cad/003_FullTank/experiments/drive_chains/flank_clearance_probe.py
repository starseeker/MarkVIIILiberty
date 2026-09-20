"""Check a repeated tangent-flank hypothesis against all 50 chain roller envelopes."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'flank_clearance_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import fingerprint,read,write,sha
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),
            '--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from lib.model import load
    from lib.pinion_geometry import values,station
    from lib.pinion_parts import casting
    from lib.track_parts import cylinder_y
    from lib.visual_review import shaded
    from sprocket_geometry import open_flanks
    data=load();lock=fingerprint();a=dict(values(data),chain_relief_radius=25.65)
    route=read(ROOT/'installed_pitch_route_report.json');center=station(data,1)
    placement=App.Placement(App.Vector(*center),App.Rotation(App.Vector(0,1,0),a['static_phase']))
    base=casting(a)
    roller=cylinder_y(25.4,39.6875).cut(cylinder_y(1.231*25.4/2,41.6875))
    cases=[]
    for angle in [15,20,25]:
        doc=App.newDocument('TangentFlanks%d'%angle)
        gear=doc.addObject('Part::Feature','PinionCasting')
        gear.Shape=open_flanks(base,int(a['teeth']),a['chain_pitch_radius'],a['sprocket_radius'],
                               a['tooth_width'],a['chain_relief_radius'],angle)
        gear.Placement=placement
        for n,(x,z) in enumerate(route['vertices_world_xz_mm']):
            obj=doc.addObject('Part::Feature','DiagnosticRoller%02d'%n);obj.Shape=roller
            obj.Placement=App.Placement(App.Vector(x,center[1],z),App.Rotation())
        doc.recompute();native=out/('flanks_%d.FCStd'%angle);doc.saveAs(str(native));App.closeDocument(doc.Name)
        doc=App.openDocument(str(native));doc.recompute();gear=doc.getObject('PinionCasting')
        overlaps=[];gaps=[];items=[]
        for obj in doc.Objects:
            shape=obj.Shape
            if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid reopened solid '+obj.Name)
            items.append(dict(id=obj.Name,definition=obj.Name,shape=shape,target=obj,system='RunningGear',representation='assembly'))
            if obj.Name=='PinionCasting':continue
            volume=gear.Shape.common(shape).Volume
            if volume>1e-5:overlaps.append(dict(roller=obj.Name,volume_mm3=volume))
            gaps.append(dict(roller=obj.Name,gap_mm=gear.Shape.distToShape(shape)[0]))
        shaded(items,out/('flanks_%d.svg'%angle),(0,1,0),
               'Diagnostic chain fit | repeated tangent flanks %d degrees; historical profile unresolved'%angle)
        cases.append(dict(flank_degrees=angle,overlaps=overlaps,clearances=gaps,
                          shape_volume_mm3=gear.Shape.Volume,native_sha256=sha(native)))
        App.closeDocument(doc.Name)
    assert fingerprint()==lock
    write(out/'report.json',dict(complete=True,authored_fingerprint=lock,cases=cases,
          seat_radius_mm=25.65,roller_radius_mm=25.4,source_diameter_and_count_retained=True,
          input_hashes={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'sprocket_geometry.py',ROOT/'installed_pitch_route_report.json']},
          promoted=False,full_chain_interfaces_qualified=False,historical_profile_qualified=False,
          interpretation='Circular root seats and tangent straight flanks; identical repeated geometry, not per-roller clearance cuts. Static installed route only.'))
    print([(case['flank_degrees'],len(case['overlaps'])) for case in cases],flush=True)
finally:
    runtime.close()
