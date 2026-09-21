"""Coupled spring size trials and a competing diameter-reading interference test."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];REPO=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'front_clutch_build')
p.add_argument('--worker',action='store_true');a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(parents=True,exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part,numpy as np
    from lib.cad_build import leaves
    from lib.worker import check_build
    from front_clutch_parts import build,spring
    report=read(base/'report.json');native=base/'TransmissionWithFrontClutch.FCStd';nh=sha(native);assert nh==report['native_sha256']
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    oldshaft=Part.Shape();oldshaft.read(str(base/'inputs/parent_shaft.brep'))
    oldbox=Part.Shape();oldbox.read(str(base/'inputs/parent_box.brep'))
    standard=check_build(STAGE/'build');td=App.openDocument(standard['build']['top_document']);td.recompute()
    context=[i for i in leaves(td.Root) if i['representation']=='assembly'];scenarios=[]
    for delta in [-1,1]:
        c=dict(report['controls']);c['spring_length']+=delta*8;c['spring_wire_radius']+=delta*.3;c['spring_end_pitch']=2*c['spring_wire_radius']+.05
        parts,occ,revised,d,spine=build(c,report['drive_controls'],oldshaft,oldbox)
        doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
        for key,s in parts.items():doc.getObject('Def_FrontClutch_'+key).Tip.Shape=s
        byid['ClutchDrive_shaft']['target'].Tip.Shape=revised['shaft'];byid['ClutchDrive_box']['target'].Tip.Shape=revised['box']
        doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items};physical=items+context
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in physical]])
        pairs=[];seen=set()
        for n in report['affected_ids']:
            s=byid[n]['shape'];assert s.isValid() and len(s.Solids)==1,n
            b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=physical[idx];pair=tuple(sorted([n,other['id']]))
                if n==other['id'] or pair in seen:continue
                seen.add(pair);v=s.common(other['shape']).Volume;pairs.append(dict(a=n,b=other['id'],intersection_mm3=v))
        contacts=[]
        for an,bn in [('FrontClutch_Spring','FrontClutch_UpperFlange'),('FrontClutch_Spring','FrontClutch_LowerFlange'),('FrontClutch_Spring','FrontClutch_Coupling'),('FrontClutch_UpperFlange','ClutchDrive_shaft'),('FrontClutch_LowerFlange','ClutchDrive_shaft')]:
            distance=byid[an]['shape'].distToShape(byid[bn]['shape'])[0]
            contacts.append(dict(a=an,b=bn,gap_mm=distance,passed=distance<1e-5))
        overlaps=[r for r in pairs if r['intersection_mm3']>1e-5]
        row=dict(spring_length=c['spring_length'],wire_diameter=2*c['spring_wire_radius'],free_pitch=d['spring']['free_pitch'],
            coupling_front=d['coupling_front'],material_pairs=len(pairs),overlaps=overlaps,contacts=contacts,
            passed=not overlaps and all(x['passed'] for x in contacts))
        scenarios.append(row);write(out/('shorter.json' if delta<0 else 'longer.json'),dict(**row,pairs=pairs))
        write(out/'progress.json',dict(completed=len(scenarios),scenarios=scenarios));print('Scenario',delta,row['passed'],overlaps,flush=True)
        App.closeDocument(doc.Name)
    # Actual alternate geometry, holding the assumed wire gauge constant. An
    # interference does not disprove every possible mean-diameter interpretation.
    alt=dict(report['controls']);alt['spring_inside_radius']-=alt['spring_wire_radius']
    alt_spring,_,_=spring(alt)
    doc=App.openDocument(str(native));doc.recompute();byid={i['id']:i for i in leaves(doc.Root)}
    coupling=byid['FrontClutch_Coupling']['target'].Shape
    intersection=alt_spring.common(coupling);overlap=intersection.Volume
    alternate=dict(reading='5-3/8in as mean diameter with unchanged1/2in inferred wire',
        intersection_mm3=overlap,intersection_valid=intersection.isValid(),
        expected_interference_detected=overlap>1 and intersection.isValid(),
        scope='Conditional negative geometry test only; thinner wire or different historical dimensions could change the outcome.')
    write(out/'mean_diameter_reading.json',alternate)
    assert sha(native)==nh
    for path,h in report['input_hashes'].items():assert sha(REPO/path)==h,path
    result=dict(passed=all(x['passed'] for x in scenarios) and alternate['expected_interference_detected'],scenarios=scenarios,
        alternate_reading=alternate,native_sha256=nh,checker_sha256=sha(Path(__file__)),
        parts_sha256=sha(HERE/'front_clutch_parts.py'),standard_native_hashes=standard['native_hashes'],
        scope='Two sampled length/wire-gauge scenarios with coupled front seat; full transmission and standard physical context. No spring-rate or exhaustive uncertainty qualification.')
    write(out/'report.json',result);print('All scenarios and conditional negative reading',result['passed'],flush=True)
    sys.exit(0 if result['passed'] else 1)
finally:runtime.close()
