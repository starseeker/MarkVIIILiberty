"""Bound selected inferred interfaces and prove the checks detect conflicting geometry."""
import argparse
import copy
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--candidate',type=Path,default=ROOT/'transmission_core_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not args.worker:
    with (out/'sensitivity_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    from transmission_core_parts import core_parts
    report=read(out/'report.json');native=out/'TransmissionCoreCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    c=read(ROOT/'transmission_core_controls.json')['controls'];cal=read(ROOT/'transmission_output_calibration.json')
    chain={k:v['value'] for k,v in read(ROOT/'chain_candidate_controls.json')['controls'].items()}
    for name in ['transmission_core_parts.py','transmission_core_controls.json','transmission_output_calibration.json','chain_candidate_controls.json']:
        assert sha(ROOT/name)==report['input_hashes'][name]
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    origin=App.Vector(*report['shaft_axis_world_mm']);frame=report['dimensions']['bevel_frame_local_mm']
    half=report['dimensions']['cross_shaft_half_length_mm']+c['shaft_end_gap']
    def placed(shape,name):
        row=report['expected_placements'][name];p=App.Placement(App.Vector(*row['base']),App.Rotation(*row['quaternion']))
        shape=shape.copy();shape.Placement=p.multiply(shape.Placement);return shape
    def new_shapes(controls):
        return core_parts(controls,cal,chain,half,report['output_center_y_mm'],frame)[0]
    trials=[]
    # Source-trace uncertainty in M278 lip radius; low radius is a negative control.
    for pixel,allowed in [(222,True),(224,True),(225,True),(229,False)]:
        control=copy.deepcopy(c)
        for point in control['planetary_profiles_px']['brake_case']:
            if point[1]==225:point[1]=pixel
        shape=placed(new_shapes(control)['brake_case'],'PortTransmissionCore_brake_case')
        disk=byid['PortTransmissionCore_planet_disk']['shape']
        volume=shape.common(disk).Volume;gap=shape.distToShape(disk)[0]
        trials.append(dict(kind='case_lip_trace',pixel_y=pixel,expected_clear=allowed,overlap_mm3=volume,gap_mm=gap,
                           passed=(volume<1e-5 if allowed else volume>1)))
    # The hub-face trace must reserve the existing M290 ring; washer remains absent.
    for pixel,allowed in [(858,True),(860,True),(861.8,True),(865,False)]:
        control=copy.deepcopy(c)
        for point in control['planetary_profiles_px']['planet_disk']:
            if point[0]==861.8:point[0]=pixel
        shape=placed(new_shapes(control)['planet_disk'],'PortTransmissionCore_planet_disk')
        ring=byid['PortTransmissionBearing_InnerRing']['shape'];shaft=byid['PortTransmissionOutput_shaft']['shape']
        ring_hit=shape.common(ring).Volume;shaft_hit=shape.common(shaft).Volume
        trials.append(dict(kind='carrier_hub_trace',pixel_x=pixel,expected_clear=allowed,ring_overlap_mm3=ring_hit,
                           shaft_overlap_mm3=shaft_hit,ring_gap_mm=shape.distToShape(ring)[0],
                           passed=shaft_hit<1e-5 and (ring_hit<1e-5 if allowed else ring_hit>1)))
    # Actual source spline engagement prevents arbitrary relative carrier rotation.
    for hand in ['Port','Starboard']:
        disk=byid[hand+'TransmissionCore_planet_disk']['shape'].copy()
        disk.rotate(origin,App.Vector(0,1,0),18)
        volume=disk.common(byid[hand+'TransmissionOutput_shaft']['shape']).Volume
        trials.append(dict(kind='carrier_phase_negative',hand=hand,rotation_deg=18,overlap_mm3=volume,passed=volume>1))
    for dy,hand in [(1,'Port'),(-1,'Starboard')]:
        shaft=byid['CenterTransmissionCore_cross_shaft']['shape'].copy();shaft.translate(App.Vector(0,dy,0))
        volume=shaft.common(byid[hand+'TransmissionOutput_shaft']['shape']).Volume
        trials.append(dict(kind='cross_shaft_axial_negative',shift_y_mm=dy,overlap_mm3=volume,passed=volume>1))
    # Derive the specified diameter from analytic native surfaces, not a mesh box.
    diameters=[]
    for hand in ['Port','Starboard']:
        shape=byid[hand+'TransmissionCore_high_drum']['shape']
        radius=max(f.Surface.Radius for f in shape.Faces if isinstance(f.Surface,Part.Cylinder))
        diameters.append(dict(hand=hand,diameter_mm=2*radius,printed_HB126_mm=381,passed=abs(2*radius-381)<1e-7))
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in trials+diameters),trials=trials,printed_diameter_checks=diameters,
                candidate_native_sha256=sha(native),candidate_report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),
                controls_sha256=sha(ROOT/'transmission_core_controls.json'),full_parameter_envelope_qualified=False,
                scope='Local lip/hub source-trace trials, actual carrier spline phase and cross-shaft end negatives. Gear, bearing, gasket, shell-thickness and full-tank perturbations remain pending.')
    write(out/'sensitivity.json',result)
    for row in trials:print(row,flush=True)
    print('PASS' if result['passed'] else 'FAIL',flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
