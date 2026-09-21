"""Rebuild uncertain key widths and a coherent vertical-shaft mounting offset."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=Path,required=True)
p.add_argument('--candidate',type=Path,default=ROOT/'transmission_vertical_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();stage=a.stage.resolve();out=a.candidate.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha
if not a.worker:
    with (out/'sensitivity_run.log').open('w') as log:sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--candidate',str(out),'--worker'],env=runtime.environment(out/'sensitivity_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from lib.cad_build import leaves
    from transmission_vertical_parts import vertical_parts
    report=read(out/'report.json');assert report['passed']
    parent=ROOT/'transmission_reversing_build/TransmissionReversingCandidate.FCStd'
    assert sha(parent)==report['input_hashes']['transmission_reversing_build/TransmissionReversingCandidate.FCStd']
    doc=App.openDocument(str(parent));doc.recompute();old={i['id']:i for i in leaves(doc.Root)}
    origin=doc.TransmissionCore.Placement.Base;changed=['CenterTransmissionCore_bevel_case','ReversingControl_rod']
    others={n:i['shape'].copy() for n,i in old.items() if n not in changed}
    for s in others.values():s.translate(-origin)
    base=read(ROOT/'transmission_vertical_controls.json')['controls'];rows=[]
    for change in [dict(key_width=5),dict(key_width=8),dict(shaft_xy=[-300,-179],nut_seat_x=-310)]:
        c=dict(base,**change);x,y=c['shaft_xy']
        defs,d=vertical_parts(c,*[old[n]['target'].Shape for n in changed])
        solids={k:v for k,v in defs.items() if k in ['case','rod','shaft','upper_lever','lower_lever']}
        for n,loc in enumerate(d['key_locations']):
            s=defs['key'].copy();s.rotate(App.Vector(),App.Vector(0,0,1),loc['angle']);s.translate(App.Vector(x,y,loc['z']));solids['key'+str(n)]=s
        for label,z,flip in [('Upper',c['upper_bearing_base_z'],False),('Lower',c['lower_bearing_open_z'],True)]:
            s=defs['bearing'].copy()
            if flip:s.rotate(App.Vector(),App.Vector(1,0,0),180)
            s.translate(App.Vector(x,y,z));solids[label+'_bearing']=s
        for row in d['mounts']:
            name=row['label']+'_'+row['kind'];s=defs[row['kind']].copy();s.translate(App.Vector(row['fastener_base_x'],row['y'],row['z']));solids[name]=s
            for key,oldname,xx in [('nut','PortBrakeBearing_nut0',c['nut_seat_x']),('cotter','InputInstallation_mount_cotter0',d['cotter_axis_x_mm'])]:
                s=old[oldname]['target'].Shape.copy();s.rotate(App.Vector(),App.Vector(0,0,1),180);s.translate(App.Vector(xx,row['y'],row['z']));solids[name+'_'+key]=s
        overlap=[];pairs=set();physical=dict(others,**solids)
        for one,s in solids.items():
            for two,t in physical.items():
                pair=tuple(sorted([one,two]))
                if one==two or pair in pairs or not s.BoundBox.intersect(t.BoundBox):continue
                pairs.add(pair);v=s.common(t).Volume
                if v>1e-5:overlap.append([one,two,v])
        gaps={}
        for n,lever in enumerate(['upper_lever','lower_lever']):
            for role in ['shaft',lever]:gaps['key'+str(n)+'_'+role]=solids['key'+str(n)].distToShape(solids[role])[0]
        gaps['finger_rod']=solids['upper_lever'].distToShape(solids['rod'])[0]
        valid=all(s.isValid() and len(s.Solids)==1 for s in solids.values())
        key_width=solids['key0'].BoundBox.YLength
        passed=valid and not overlap and abs(key_width-c['key_width'])<1e-7 and all(abs(v-(.15 if k=='finger_rod' else .05))<1e-5 for k,v in gaps.items())
        rows.append(dict(change=change,passed=passed,valid=valid,solid_count=len(solids),material_pairs=len(pairs),overlaps=overlap,interface_gaps_mm=gaps,key_width_mm=key_width,dimensions=d))
        write(out/'sensitivity_progress.json',dict(trials=rows));print(change,passed,overlap,flush=True)
    passed=all(r['passed'] for r in rows)
    write(out/'sensitivity_checks.json',dict(passed=passed,trials=rows,checker_sha256=sha(Path(__file__)),generator_sha256=sha(ROOT/'transmission_vertical_parts.py'),controls_sha256=sha(ROOT/'transmission_vertical_controls.json'),
        report_sha256=sha(out/'report.json'),parent_native_sha256=sha(parent),scope='21 rebuilt local solids checked against retained transmission. Shaft move preserves bearing-to-nut offset; printed stud length unchanged. No tank-context, export, motion or load qualification for variants.'))
    sys.exit(0 if passed else 1)
finally:runtime.close()
