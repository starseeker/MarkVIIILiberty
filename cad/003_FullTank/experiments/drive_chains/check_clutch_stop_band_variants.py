"""Exercise coupled band-stock, release-gap and eye-size estimates in saved context."""
import argparse
import copy
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_stop_band_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();base=a.candidate.resolve();out=base/'variants';out.mkdir(exist_ok=True)
if not a.worker:
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(base),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part,numpy as np
    from lib.cad_build import leaves,shape_signature
    from lib.worker import same_shape
    from clutch_stop_brake_parts import band_parts
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    nominal=read(base/'report.json');native=base/'TransmissionWithClutchStopBand.FCStd'
    assert sha(native)==nominal['native_sha256']
    trials=[]
    for label,changes in [('thin_close',dict(steel_stock=2.75,released_gap=.35,eye_inside_radius=6.0)),
                          ('thick_open',dict(steel_stock=3.5,released_gap=.65,eye_inside_radius=7.0))]:
        folder=out/label;folder.mkdir(exist_ok=True);(folder/'inputs').mkdir(exist_ok=True)
        c=dict(nominal['controls'],**changes);doc=App.openDocument(str(native))
        before={i['id']:shape_signature(i['shape']) for i in leaves(doc.Root)}
        parts,occ,d,curves,blanks=band_parts(c)
        for key,shape in parts.items():doc.getObject('Def_ClutchStopBand_'+key).Tip.Shape=shape
        for row in occ:doc.getObject(row['name']).LinkPlacement=App.Placement(App.Vector(*row['xyz']),App.Rotation(*row['rotation']))
        for name,shape in curves.items():shape.exportBrep(str(folder/'inputs'/(name+'.brep')))
        doc.recompute();saved=folder/native.name;doc.saveAs(str(saved));App.closeDocument(doc.Name)
        doc=App.openDocument(str(saved));items=leaves(doc.Root);byid={i['id']:i for i in items}
        assert len(byid)==1681
        for name,i in byid.items():
            assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
            if name not in nominal['new_ids']:assert same_shape(before[name],shape_signature(i['shape'])),name
        boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].copy().cleaned().BoundBox for i in items]])
        pairs=[];seen=set()
        for name in nominal['new_ids']:
            s=byid[name]['shape'];b=s.copy().cleaned().BoundBox;bb=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
            near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
            for idx in near:
                other=items[idx];key=tuple(sorted([name,other['id']]))
                if name==other['id'] or key in seen:continue
                seen.add(key);pairs.append(dict(a=name,b=other['id'],intersection_mm3=s.common(other['shape']).Volume))
        overlaps=[v for v in pairs if abs(v['intersection_mm3'])>1e-5]
        report=copy.deepcopy(nominal)
        report.update(status='parameter_trial_not_qualified',native_sha256=sha(saved),controls=c,datums=d,occurrences=occ,
            variant_parent_native_sha256=sha(native),variant_changes=changes,
            artifact_hashes={},material_pairs=len(pairs),material_passed=not overlaps,overlaps=overlaps,
            material_scope='19 changed band pieces against nominal candidate neighbors; standard-tank variation check still pending')
        report['standard_context_checked']=False
        write(folder/'report.json',report);write(folder/'material_checks.json',dict(passed=not overlaps,native_sha256=sha(saved),pairs=pairs))
        App.closeDocument(doc.Name)
        with (folder/'interface_check.log').open('w') as log:
            check=subprocess.run([sys.executable,str(HERE/'check_clutch_stop_band.py'),'--candidate',str(folder),'--worker'],
                env=runtime.environment(folder/'check_runtime'),stdout=log,stderr=subprocess.STDOUT)
        trial=dict(name=label,changes=changes,native_sha256=sha(saved),checks_exit_code=check.returncode,
            independent_checks_sha256=sha(folder/'independent_checks.json') if (folder/'independent_checks.json').exists() else None,
            material_pairs=len(pairs),overlaps=overlaps,passed=not overlaps and check.returncode==0)
        trials.append(trial);print(label,trial,flush=True)
        write(out/'progress.json',dict(trials=trials))
    write(out/'checks.json',dict(passed=all(v['passed'] for v in trials),nominal_native_sha256=sha(native),
        checker_sha256=sha(Path(__file__)),trials=trials,complete_brake=False))
    assert all(v['passed'] for v in trials)
finally:
    runtime.close()
