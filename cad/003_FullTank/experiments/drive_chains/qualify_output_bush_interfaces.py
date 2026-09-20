"""Recheck the retained sprocket/drum interfaces after machining output shafts."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=ROOT/'transmission_bush_build'
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint

if not args.worker:
    with (out/'interface_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--worker'],
                               env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    from transmission_output_parts import cylinder
    report=read(out/'report.json');native=out/'TransmissionBushCandidate.FCStd'
    assert report['passed'] and report['rendering_complete'] and report['native_sha256']==sha(native)
    assert report['authored_fingerprint']==fingerprint()
    original_path=ROOT/'casing_front_build/CasingFrontCandidate.FCStd'
    assert sha(original_path)==report['input_hashes']['casing_front_build/CasingFrontCandidate.FCStd']
    original=App.openDocument(str(original_path));original.recompute()
    old=next(i['target'].Shape.copy() for i in leaves(original.Root) if i['id']=='PortTransmissionOutput_shaft')
    App.closeDocument(original.Name)
    doc=App.openDocument(str(native));doc.recompute();items={i['id']:i for i in leaves(doc.Root)}
    records=[]
    for hand in ['Port','Starboard']:
        shaft=items[hand+'TransmissionOutput_shaft']
        pose=shaft['shape'].Placement.multiply(shaft['target'].Shape.Placement.inverse())
        twist=shaft['target'].Shape.copy();twist.rotate(App.Vector(),App.Vector(0,1,0),2)
        twist.Placement=pose.multiply(twist.Placement)
        for role,name in [('sprocket',hand+'Chain_TransmissionPinion'),('drum',hand+'TransmissionOutput_drum')]:
            other=items[name]['shape']
            local=other.copy();local.Placement=pose.inverse().multiply(local.Placement)
            b=local.BoundBox;slab=Part.makeBox(1000,b.YLength,1000,App.Vector(-500,b.YMin,-500))
            a=old.common(slab);new=shaft['target'].Shape.common(slab)
            difference=a.cut(new).Volume+new.cut(a).Volume
            gap=shaft['shape'].distToShape(other)[0];capture=twist.common(other).Volume
            negative=cylinder(49.8,b.YMin,b.YMax);negative.Placement=pose.multiply(negative.Placement)
            negative_overlap=negative.common(other).Volume
            overlap=shaft['shape'].common(other).Volume
            records.append(dict(hand=hand,receiver=role,unchanged_axial_region_difference_mm3=difference,
                                minimum_gap_mm=gap,overlap_mm3=overlap,twist_capture_mm3=capture,
                                unsplined_negative_mm3=negative_overlap,
                                passed=difference<1e-5 and overlap<1e-5 and gap>0 and capture>1 and negative_overlap<1e-5))
    assert sha(native)==report['native_sha256'] and fingerprint()==report['authored_fingerprint']
    result=dict(passed=all(r['passed'] for r in records),interfaces=records,native_sha256=sha(native),
                parent_report_sha256=sha(out/'report.json'),script_sha256=sha(Path(__file__)),
                historical_fit_qualified=False,full_axial_stack_qualified=False)
    write(out/'retained_interface_checks.json',result)
    print('PASS: four retained spline fits and unchanged rotor engagement regions.' if result['passed'] else 'FAIL: retained interface check',flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:
    runtime.close()
