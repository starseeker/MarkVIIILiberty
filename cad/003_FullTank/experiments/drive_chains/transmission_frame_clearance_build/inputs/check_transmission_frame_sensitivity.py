"""Read saved frame geometry and expose sensitivity of its inferred interfaces."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'transmission_frame_clearance_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha

if not args.worker:
    with (out/'sensitivity_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    App,Gui=runtime.start_gui()
    from lib.cad_build import leaves
    from lib.model import load,point
    from transmission_frame_parts import frame_parts,revised_bracket

    r=read(out/'report.json');assert r['complete'] and r['rendering_complete'] and r['passed']
    native=out/'TransmissionFrameCandidate.FCStd';assert sha(native)==r['native_sha256']
    for name,digest in r['input_hashes'].items():assert sha(ROOT/name)==digest
    prior_path=ROOT/'transmission_support_clearance_build/TransmissionSupportCandidate.FCStd'
    doc=App.openDocument(str(native));doc.recompute();items={i['id']:i for i in leaves(doc.Root)}
    olddoc=App.openDocument(str(prior_path));olddoc.recompute();old={i['id']:i for i in leaves(olddoc.Root)}
    main=App.openDocument(str(stage/'build/native/MarkVIII.FCStd'));main.recompute();context={i['id']:i for i in leaves(main.Root)}
    record=read(ROOT/'transmission_frame_controls.json');c={k:v['value'] for k,v in record['controls'].items()}
    support={k:v['value'] for k,v in read(ROOT/'transmission_support_controls.json')['controls'].items()}
    old_report=read(ROOT/'transmission_support_clearance_build/report.json')
    source=old['PortFixedBearing_outer_bracket'];pose=source['shape'].Placement.multiply(source['target'].Shape.Placement.inverse())
    rebuilt,detail=revised_bracket(source['target'].Shape,'outer',c,support,old_report['dimensions'],pose.Base)
    target=items['PortFixedBearing_outer_bracket']['target'].Shape
    nominal_difference=rebuilt.cut(target).Volume+target.cut(rebuilt).Volume
    assert nominal_difference<1e-5
    def installed(shape,placement):
        copied=shape.copy();copied.Placement=placement.multiply(copied.Placement);return copied
    case=items['PortCasing_Body']['shape'];rivet=items['PortCasingWall_WallRivet05']['shape']
    variants=[]
    for key,value,expected_clear in [('rear_stem_round_radius',18,False),('rear_stem_round_radius',22,True),
                                     ('rear_stem_end_inset',0,False)]:
        altered=dict(c);altered[key]=value
        shape,_=revised_bracket(source['target'].Shape,'outer',altered,support,old_report['dimensions'],pose.Base)
        world=installed(shape,pose);volumes=[world.common(other).Volume for other in [case,rivet]]
        clear=all(v<1e-5 for v in volumes)
        variants.append(dict(parameter=key,value=value,unit='mm',case_overlap_mm3=volumes[0],rivet_overlap_mm3=volumes[1],
                             minimum_gap_mm=min(world.distToShape(other)[0] for other in [case,rivet]),
                             geometric_clearance_pass=clear,expected_clearance_pass=expected_clear,
                             expected_outcome_observed=clear==expected_clear))
    frame_variants=[]
    raw_bottom=point(load(),'snl_2',record['calibration']['bottom_channel_web_raw_pick_px'])[1]
    inner=items['PortFixedBearing_inner_bracket']
    inner_y=inner['shape'].Placement.multiply(inner['target'].Shape.Placement.inverse()).Base.y
    for key,value,member,receiver in [('channel_depth',160,'TopChannel','PortCasingWall_WallRivet10'),
                                     ('bottom_web_z',raw_bottom,'BottomChannel','hull_floor_8')]:
        altered=dict(c);altered[key]=value
        shapes,placements,_=frame_parts(altered,inner_y,pose.Base.y)
        shape_key,placement=placements[member];world=installed(shapes[shape_key],placement)
        other=(items if receiver in items else context)[receiver]['shape']
        volume=world.common(other).Volume
        frame_variants.append(dict(parameter=key,value=value,unit='mm',member=member,receiver=receiver,
                                   overlap_mm3=volume,expected_rejection_observed=volume>1e-5))
    interfaces=[]
    for hand in ['Port','Starboard']:
        for role in ['inner','outer']:
            prefix=hand+'FixedBearing_'+role+'_';sleeve=items[hand+'TransmissionBearing_'+role.title()+'Bush']['shape']
            gaps=[items[prefix+'lining_'+side]['shape'].distToShape(sleeve)[0] for side in ['back','front']]
            split=items[prefix+'bracket']['shape'].distToShape(items[prefix+'cap']['shape'])[0]
            lid=items[prefix+'lid']['shape'].distToShape(items[prefix+'cap']['shape'])[0]
            passed=all(abs(v-support['running_gap'])<1e-5 for v in gaps) and abs(split-2*support['split_gap'])<1e-5 and abs(lid-support['lid_gap'])<1e-5
            interfaces.append(dict(hand=hand,role=role,lining_gaps_mm=gaps,cap_split_mm=split,lid_gap_mm=lid,passed=passed))
    passed=(all(v['expected_outcome_observed'] for v in variants)
            and all(v['expected_rejection_observed'] for v in frame_variants)
            and all(v['passed'] for v in interfaces))
    result=dict(analysis_completed=True,expected_outcomes_passed=passed,native_sha256=sha(native),
                nominal_outer_bracket_rebuild_difference_mm3=nominal_difference,
                bearing_interfaces=interfaces,stem_variants=variants,frame_negative_witnesses=frame_variants,
                script_sha256=sha(Path(__file__)),nominal_report_sha256=sha(out/'report.json'),
                historical_fit_qualified=False,parameter_envelope_qualified=False,
                conclusion='Nominal static fit is narrow: nearby unmeasured stem radii/endpoints can collide. These witnesses expose sensitivity; they do not qualify the uncertainty range.')
    write(out/'sensitivity_checks.json',result)
    (out/'inputs/check_transmission_frame_sensitivity.py').write_bytes(Path(__file__).read_bytes())
    assert sha(native)==r['native_sha256']
    print('Frame sensitivity audit expected outcomes:',passed,flush=True)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
