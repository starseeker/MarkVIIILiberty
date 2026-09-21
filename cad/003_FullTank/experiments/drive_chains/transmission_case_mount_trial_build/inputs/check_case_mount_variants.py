"""Local MX5 source-length and channel-taper sensitivity, without promotion."""
import argparse,subprocess,sys
from pathlib import Path
REPO=next(p for p in Path(__file__).resolve().parents if (p/'cad/003_FullTank').is_dir());STAGE=REPO/'cad/003_FullTank';ROOT=STAGE/'experiments/drive_chains';STUDY=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');a=p.parse_args()
sys.path[:0]=[str(STAGE),str(ROOT)]
from lib import runtime
from lib.evidence import read,write,sha
out=ROOT/'transmission_case_mount_trial_build/variants';out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from transmission_case_mount_parts import case_mount_parts
    from lib.cad_build import leaves
    parent=ROOT/'transmission_vertical_build/TransmissionVerticalCandidate.FCStd'
    parent_report=read(ROOT/'transmission_vertical_build/report.json');assert sha(parent)==parent_report['native_sha256']
    doc=App.openDocument(str(parent));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    case=old['CenterTransmissionCore_bevel_case']['target'].Shape
    nut=old['PortFixedBearing_inner_Stud01_Nut']['target'].Shape
    channels={k:old['TransmissionFrame_'+label+'Channel']['target'].Shape for k,label in [('top','Top'),('bottom','Bottom')]}
    base=read(ROOT/'transmission_case_mount_controls.json')['controls']
    pc={k:v['value'] for k,v in read(ROOT/'transmission_stud_controls.json')['controls'].items()};pc['cotter_eye_join_overlap']=.1
    rows=[]
    for change in [dict(stud_length=139.7),dict(flange_root_stock=10),dict(flange_root_stock=14)]:
        c=dict(base,**change);defs,revised,parts,d=case_mount_parts(c,case,channels,nut,pc)
        valid=all(s.isValid() and len(s.Solids)==1 for s in parts.values());pairs=set();overlaps=[]
        for n,s in parts.items():
            for m,t in parts.items():
                pair=tuple(sorted([n,m]))
                if n==m or pair in pairs or not s.BoundBox.intersect(t.BoundBox):continue
                pairs.add(pair);v=s.common(t).Volume
                if v>1e-5:overlaps.append([n,m,v])
        gaps=[]
        for mount in d['mounts']:
            n=mount['name'];channel=parts[mount['channel']+'_channel']
            for k,other,want in [('stud',parts['case'],.15),('stud',channel,.15),('washer',channel,0),('washer',parts[n+'_nut'],0),('stud',parts[n+'_cotter'],.15)]:
                value=parts[n+'_'+k].distToShape(other)[0];gaps.append(dict(name=n+'_'+k,value=value,expected=want,passed=abs(value-want)<1e-5))
        length=defs['stud'].BoundBox.XLength
        passed=valid and not overlaps and abs(length-c['stud_length'])<1e-7 and all(x['passed'] for x in gaps)
        rows.append(dict(change=change,passed=passed,valid=valid,occurrences=len(parts),material_pairs=len(pairs),overlaps=overlaps,
            gaps=gaps,measured_stud_length_mm=length,dimensions=d))
        write(out/'progress.json',dict(trials=rows));print(change,passed,flush=True)
    write(out/'report.json',dict(passed=all(r['passed'] for r in rows),trials=rows,
        generator_sha256=sha(ROOT/'transmission_case_mount_parts.py'),controls_sha256=sha(ROOT/'transmission_case_mount_controls.json'),
        checker_sha256=sha(Path(__file__)),parent_native_sha256=sha(parent),scope='19 rebuilt local solids and interface distances. Nominal trial has complete standard/transmission context checks; these variants have no external context or STEP qualification.'))
    sys.exit(0 if all(r['passed'] for r in rows) else 1)
finally:runtime.close()
