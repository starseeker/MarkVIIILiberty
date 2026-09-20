"""Check gallery wall stock and reject a low drilling that misses the reservoir."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_oil_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.candidate.resolve()
sys.path[:0]=[str(stage),str(ROOT)]
from lib import runtime
from lib.evidence import read,write,sha
if not args.worker:
    with (out/'gallery_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    from transmission_oil_parts import fittings,cap_lubrication
    from transmission_stud_parts import cylinder_x
    from transmission_output_parts import cylinder as cylinder_y
    r=read(out/'report.json');assert r['passed'] and r['rendering_complete']
    native=out/'TransmissionOilCandidate.FCStd';assert sha(native)==r['native_sha256']
    for n,h in r['input_hashes'].items():assert sha(ROOT/n)==h,n
    for n,h in r['tank_native_hashes'].items():assert sha(stage/'build'/n)==h,n
    doc=App.openDocument(str(ROOT/'transmission_stud_clearance_build/TransmissionStudCandidate.FCStd'));doc.recompute()
    before={i['id']:i for i in leaves(doc.Root)}
    saved=App.openDocument(str(native));saved.recompute();after={i['id']:i for i in leaves(saved.Root)}
    c={k:v['value'] for k,v in read(ROOT/'transmission_oil_controls.json')['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    dims=read(ROOT/'transmission_support_clearance_build/report.json')['dimensions']
    _,_,ft=fittings(c)
    trials=[]
    settings=[('nominal',-18,2.5,True),('higher_gallery',-10,2.5,True),('lower_gallery',-22,2.5,True),
              ('smaller_bore',-18,2,True),('larger_bore',-18,3,True),('below_reservoir_negative',-28,2.5,False)]
    for role in ['inner','outer']:
        prefix='PortFixedBearing_'+role+'_';oldcap=before[prefix+'cap']['target'].Shape;lining=before[prefix+'lining_front']['target'].Shape
        for name,z,radius,expected_pass in settings:
            controls=dict(c,gallery_z=z,gallery_radius=radius)
            shapes,d,t=cap_lubrication(oldcap,lining,dims[role],support,controls)
            start=d['gallery_running_exit_x_mm']-1;end=dims[role]['cup_back_x_mm']+support['cup_stock']
            stock=cylinder_x(radius+1,start,end,0,z).cut(cylinder_x(radius,start-1,end+1,0,z))
            stock=stock.cut(cylinder_y(dims[role]['bore_radius_mm'],-100,100))
            missing=stock.cut(shapes['cap'].fuse(shapes['lining_front'])).Volume
            witness=ft['witness'].copy();witness.translate(App.Vector(*d['inlet_origin_mm']))
            network=witness.fuse(shapes['wool']).fuse(t['passage_witness']).removeSplitter()
            connected=len(network.Solids)==1
            clear=network.common(shapes['cap'].fuse(shapes['lining_front'])).Volume
            passed=connected and missing<1e-5 and clear<1e-5
            difference={}
            if name=='nominal':
                for key in ['cap','lining_front']:
                    actual=after[prefix+key]['target'].Shape;rebuilt=shapes[key]
                    difference[key]=actual.cut(rebuilt).Volume+rebuilt.cut(actual).Volume
                assert max(difference.values())<1e-3
            trials.append(dict(role=role,trial=name,gallery_z_mm=z,gallery_radius_mm=radius,
                connected_network=connected,missing_one_mm_gallery_wall_mm3=missing,blocked_path_mm3=clear,
                nominal_native_material_difference_mm3=difference,local_geometry_pass=passed,expected_pass=expected_pass,
                expected_outcome_pass=passed==expected_pass))
            print(role,name,'connected',connected,'wallmissing',missing,'clear',clear,'pass',passed,flush=True)
    result=dict(analysis_completed=True,passed=all(t['expected_outcome_pass'] for t in trials),
                native_sha256=sha(native),candidate_report_sha256=sha(out/'report.json'),script_sha256=sha(Path(__file__)),
                trials=trials,wall_requirement_mm=1,scope='Local cap/lining gallery and reservoir connection; dimensional trials are diagnostic bounds, not measured historical tolerances.',
                full_parameter_envelope_qualified=False,historical_oil_route_qualified=False,oil_performance_qualified=False)
    write(out/'gallery_checks.json',result)
    (out/'inputs/check_transmission_oil_gallery.py').write_bytes(Path(__file__).read_bytes())
    assert sha(native)==r['native_sha256']
    for n,h in r['tank_native_hashes'].items():assert sha(stage/'build'/n)==h,n
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
