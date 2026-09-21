"""Bounded feed-location and passage-diameter trials against real prior parts."""
import argparse,copy,math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_input_installation_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'sensitivity_run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'sensitivity_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    from lib.cad_build import leaves
    from transmission_input_installation_parts import grease_feed
    report=read(out/'report.json');native=out/'TransmissionInputInstallationCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    controls=read(ROOT/'transmission_input_installation_controls.json')
    doc=App.openDocument(str(ROOT/'transmission_input_build/TransmissionInputCandidate.FCStd'));doc.recompute()
    prior={i['id']:i for i in leaves(doc.Root)}
    housing=prior['InputHousing_housing']['target'].Shape;spacer=prior['InputHousing_spacer']['target'].Shape
    results=[]
    for key,value in [('station',278.0),('station',282.0),('flow_radius',3.0),('flow_radius',5.0)]:
        c=copy.deepcopy(controls['grease']);c[key]=value
        shapes,d,_=grease_feed(c,housing,spacer);clashes=[]
        keys=list(shapes)
        for n,k in enumerate(keys):
            for j in keys[n+1:]:
                vol=shapes[k].common(shapes[j]).Volume
                if vol>1e-5:clashes.append(dict(a=k,b=j,volume_mm3=vol))
        u=App.Vector(0,1/math.sqrt(2),1/math.sqrt(2));base=App.Vector(c['station'],0,0)+u*50
        gauge=Part.makeCylinder(1,25,u*0+base,u)
        blockage=sum(gauge.common(shapes[k]).Volume for k in ['housing','spacer'])
        results.append(dict(parameter=key,value=value,valid_single_solids=all(s.isValid() and len(s.Solids)==1 for s in shapes.values()),
            material_pairs=15,overlaps=clashes,radial_passage_blockage_mm3=blockage,
            passed=not clashes and blockage<1e-5 and all(s.isValid() and len(s.Solids)==1 for s in shapes.values())))
        write(out/'sensitivity_progress.json',results)
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in results),trials=results,native_sha256=sha(native),report_sha256=sha(out/'report.json'),
        checker_sha256=sha(Path(__file__)),parts_sha256=sha(ROOT/'transmission_input_installation_parts.py'),controls_sha256=sha(ROOT/'transmission_input_installation_controls.json'),
        scope='Four local geometry trials, actual prior M250/M249, six affected parts and radial passage only. Nominal installed and whole-route qualification are separate.')
    write(out/'sensitivity_checks.json',result);print('PASS' if result['passed'] else 'FAIL',results,flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
