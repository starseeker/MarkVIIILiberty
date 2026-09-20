"""Isolated HB130 chain-roller envelopes versus the provisional pinion casting.

These diagnostic annuli are not inventory-counted installed chain components.
The candidate changes only the relief radius, without changing authored inputs.
"""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'roller_clearance_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import fingerprint,read,write,sha
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),
            '--output',str(out),'--worker'],env=runtime.environment(out),
            stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    from lib.model import load
    from lib.pinion_geometry import values,station
    from lib.pinion_parts import casting
    from lib.track_parts import cylinder_y
    from lib.visual_review import shaded
    lock=fingerprint();data=load();controls=values(data)
    route=read(ROOT/'installed_pitch_route_report.json')
    center=station(data,1)
    assert abs(center[0]-route['roller_pinion_axis_xz_mm'][0])<1e-7
    assert abs(center[2]-route['roller_pinion_axis_xz_mm'][1])<1e-7
    placement=App.Placement(App.Vector(*center),App.Rotation(App.Vector(0,1,0),controls['static_phase']))
    # HB130 gives the roller OD. HB132 gives the pin-bore control. Axial length
    # deliberately covers only the inner-bar gap for this tooth-fit diagnostic.
    roller=cylinder_y(25.4,39.6875).cut(cylinder_y(1.231*25.4/2,41.6875))
    results=[]
    for name,radius in [('current',controls['chain_relief_radius']),('candidate',25.65)]:
        a=dict(controls,chain_relief_radius=radius)
        doc=App.newDocument('ChainRelief_'+name)
        gear=doc.addObject('PartDesign::Body','PinionCasting')
        feature=gear.newObject('PartDesign::Feature','ReconstructedCasting')
        feature.Shape=casting(a).removeSplitter();gear.Placement=placement
        for n,(x,z) in enumerate(route['vertices_world_xz_mm']):
            obj=doc.addObject('Part::Feature','DiagnosticRoller%02d'%n)
            obj.Shape=roller;obj.Placement=App.Placement(App.Vector(x,center[1],z),App.Rotation())
            obj.addProperty('App::PropertyString','Scope','Evidence')
            obj.Scope='Diagnostic roller envelope only; chain inventory and installed interfaces unresolved'
        doc.recompute();native=out/(name+'.FCStd');doc.saveAs(str(native));App.closeDocument(doc.Name)
        doc=App.openDocument(str(native));doc.recompute();gear=doc.getObject('PinionCasting')
        overlaps=[];gaps=[];items=[]
        for obj in [gear]+[o for o in doc.Objects if o.Name.startswith('DiagnosticRoller')]:
            shape=obj.Shape
            if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid saved solid: '+obj.Name)
            items.append(dict(id=obj.Name,definition=obj.Name,shape=shape,target=obj,
                              system='RunningGear',representation='assembly'))
            if obj==gear:continue
            volume=gear.Shape.common(shape).Volume
            if volume>1e-5:overlaps.append(dict(roller=obj.Name,volume_mm3=volume))
            gaps.append(dict(roller=obj.Name,gap_mm=gear.Shape.distToShape(shape)[0]))
        shaded(items,out/(name+'_elevation.svg'),(0,1,0),
               'Diagnostic chain roller envelopes | '+name+' relief %.3f mm'%radius)
        results.append(dict(case=name,relief_radius_mm=radius,roller_radius_mm=25.4,
                            overlaps=overlaps,clearances=gaps,native_sha256=sha(native)))
        App.closeDocument(doc.Name)
    assert fingerprint()==lock
    write(out/'report.json',dict(complete=True,authored_fingerprint=lock,cases=results,
          route_report_sha256=sha(ROOT/'installed_pitch_route_report.json'),script_sha256=sha(__file__),
          source='HB130 original scan, first roller diameter in chain outline: two inches',
          axial_length_scope='39.6875 mm inner-bar gap only; bushing ends, bars, pins and cotters excluded',
          model_inputs_changed=False,inventory_reconciled=False,full_chain_interfaces_qualified=False))
    print([(r['case'],len(r['overlaps'])) for r in results],flush=True)
finally:
    runtime.close()
