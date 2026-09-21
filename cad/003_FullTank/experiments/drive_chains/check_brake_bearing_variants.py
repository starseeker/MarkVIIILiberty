"""Local sensitivity of the reconstructed saddle/bush and conflicting stud length."""
import argparse,copy
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_brake_bearing_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'sensitivity_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'sensitivity_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from transmission_brake_bearing_parts import brake_bearing_parts
    report=read(out/'report.json');native=out/'TransmissionBrakeBearingCandidate.FCStd'
    assert report['passed'] and sha(native)==report['native_sha256']
    doc=App.openDocument(str(ROOT/'transmission_input_installation_build/TransmissionInputInstallationCandidate.FCStd'));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    controls=read(ROOT/'transmission_brake_bearing_controls.json')['controls'];results=[]
    originals=[old[n]['target'].Shape for n in ['CenterTransmissionCore_bevel_case','PortTransmissionCore_high_drum','PortTransmissionCore_plain_case','InputInstallation_mount_nut0']]
    for key,value in [('running_gap',.1),('running_gap',.25),('bush_radius',85.5),('stud_length',39.6875)]:
        c=copy.deepcopy(controls);c[key]=value;parts,d=brake_bearing_parts(c,*originals)
        pieces={k:s for k,s in parts.items() if k in ['case','drum','cap','bush']};pieces['plain_case']=originals[2]
        pieces['dowel']=old['PortTransmissionBearing_InnerDowel']['target'].Shape.copy();pieces['dowel'].translate(App.Vector(*d['dowel_origin_mm']))
        for n,(y,z) in enumerate(d['stud_axes_yz_mm']):
            for k,x in [('stud',0),('nut',c['nut_seat']),('cotter',d['cotter_axis_mm'])]:
                s=parts[k].copy() if k!='cotter' else old['InputInstallation_mount_cotter0']['target'].Shape.copy();s.translate(App.Vector(x,y,z));pieces[k+str(n)]=s
        overlaps=[];pairs=0
        for i,(k,s) in enumerate(pieces.items()):
            for name,t in list(pieces.items())[i+1:]:
                pairs+=1;volume=s.common(t).Volume
                if volume>1e-5:overlaps.append(dict(a=k,b=name,volume_mm3=volume))
        us=d['US_thread_limits_mm'];sae=d['SAE_thread_limits_mm'];thread_fit=us[1]<=-c['split_gap']+1e-8 and sae[0]<=c['nut_seat'] and c['nut_seat']+c['nut_height']<=sae[1]
        gap=pieces['bush'].distToShape(pieces['drum'])[0]
        valid=all(s.isValid() and len(s.Solids)==1 for s in pieces.values())
        results.append(dict(parameter=key,value=value,material_pairs=pairs,overlaps=overlaps,valid_single_solids=valid,thread_intervals_fit=thread_fit,journal_gap_mm=gap,
            passed=valid and thread_fit and not overlaps and abs(gap-c['running_gap'])<1e-5))
        write(out/'sensitivity_progress.json',results)
    assert sha(native)==report['native_sha256']
    result=dict(passed=all(r['passed'] for r in results),trials=results,native_sha256=sha(native),report_sha256=sha(out/'report.json'),checker_sha256=sha(Path(__file__)),parts_sha256=sha(ROOT/'transmission_brake_bearing_parts.py'),controls_sha256=sha(ROOT/'transmission_brake_bearing_controls.json'),scope='Four local12-solid trials, port joint and whole M263 casting; not full tank or geartrain parameter requalification. Both printed stud lengths fit this inferred joint, so fit does not settle the source conflict.')
    write(out/'sensitivity_checks.json',result);print('PASS' if result['passed'] else 'FAIL',results,flush=True);sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
