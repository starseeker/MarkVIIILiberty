"""Verify the saved merged pump hierarchy with memory-bounded native workers."""
import argparse
import ast
from pathlib import Path
import subprocess
import sys
import numpy as np

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True);p.add_argument('--render',action='store_true')
a=p.parse_args();out=a.candidate.resolve();area=out/'isolated';area.mkdir(exist_ok=True)
worker=HERE/'pump_integration_worker.py';r=read(out/'report.json');native=out/r['native_file']
assert sha(native)==r['native_sha256']
def run(args,work):
    work.mkdir(parents=True,exist_ok=True)
    with (work/'run.log').open('w') as log:
        subprocess.run([sys.executable,*map(str,args)],env=runtime.environment(work),
            stdout=log,stderr=subprocess.STDOUT,check=True)
def extract(key,path,digest):
    assert sha(path)==digest
    dest=area/key/'manifest.json'
    if not dest.exists() or read(dest)['native_sha256']!=digest or read(dest)['extractor_sha256']!=sha(worker):
        run([worker,'extract','--input',path,'--output',dest],dest.parent)
    result=read(dest);assert result['native_sha256']==digest and result['extractor_sha256']==sha(worker)
    assert len(result['occurrences'])==len({row['name'] for row in result['occurrences']})
    print('saved hierarchy extracted',key,len(result['occurrences']),flush=True)
    return result
reports={}
for key,ref in r['parent_reports'].items():
    path=ROOT/ref['path'];assert sha(path)==ref['sha256'];reports[key]=read(path)
models={'candidate':extract('candidate',native,r['native_sha256'])}
for key,ref in r['parent_natives'].items():models[key]=extract(key,ROOT/ref['path'],ref['sha256'])
receiver_report=ROOT/r['receiver_report'];rr=read(receiver_report)
models['receiver']=extract('receiver',receiver_report.parent/rr['native_file'],r['receiver_native_sha256'])
current=models['candidate'];items={row['name']:row for row in current['occurrences']}
checks=[];rows=[];pairs={};reused=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));print(name,bool(passed),flush=True)
    write(out/'check_progress.json',dict(checks=checks,occurrences=rows))
def mat(v):return np.array(v,dtype=float).reshape(4,4)
def frame_error(one,two):
    points=np.array([[0,0,0,1],[13,0,0,1],[0,17,5,1]],dtype=float).T
    return float(np.linalg.norm(((one-two)@points)[:3],axis=0).max())
def translation(x,y,z):
    m=np.eye(4);m[:3,3]=[x,y,z];return m
engine=mat(current['assemblies']['TankLibertyEngine']['world'])
water_z=-reports['drive']['controls']['pump_axis_drop']
ck('2393 unique physical occurrences',len(items)==2393)
ck('water axis follows independently bound lower-drive dimension',
   abs(current['assemblies']['EngineWaterPump']['local'][11]-water_z)<1e-7,expected_engine_z_mm=water_z)
ck('inherited engine registration preserved',frame_error(engine,mat(models['water']['assemblies']['TankLibertyEngine']['world']))<1e-7)

# Reuse only completed exact-shape pairs from the interrupted checker, after
# verifying that the acceptance expression is syntactically identical.
previous=out/'diagnostics/process247';cache={}
def predicate(path):
    terms=[ast.dump(n.value,include_attributes=False) for n in ast.walk(ast.parse(path.read_text()))
           if isinstance(n,ast.keyword) and n.arg=='passed']
    return next(s for s in terms if "id='one'" in s and 'isValid' in s)
if previous.exists():
    receipt=read(previous/'termination.json')
    for name in ['check_engine_pumps_integration.py','material_equivalence_progress.json']:
        assert sha(previous/name)==receipt['files'][name]
    assert predicate(previous/'check_engine_pumps_integration.py')==predicate(worker)
    cache={(v['source_sha256'],v['candidate_sha256']):v for v in read(previous/'material_equivalence_progress.json') if v['passed']}

def compare(name,key,old,expected,scope):
    now=items[name];source=models[key]['definitions'][old['definition']];target=current['definitions'][now['definition']]
    pair=(source['brep_sha256'],target['brep_sha256']);same=pair[0]==pair[1];passed=same
    if not same:
        if pair not in pairs:
            if pair in cache:
                result=cache[pair];reused.append(dict(source_sha256=pair[0],candidate_sha256=pair[1]))
            else:
                work=area/'material'/(pair[0]+'_'+pair[1]);work.mkdir(parents=True,exist_ok=True)
                request=dict(source_path=source['brep_path'],candidate_path=target['brep_path'],
                    source_sha256=pair[0],candidate_sha256=pair[1],definition=now['definition'])
                write(work/'request.json',request)
                if not (work/'result.json').exists():
                    run([worker,'material','--input',work/'request.json','--output',work/'result.json'],work)
                result=read(work/'result.json')
                assert (result['source_sha256'],result['candidate_sha256'])==pair
                assert result['worker_sha256']==sha(worker)
            pairs[pair]=result;write(out/'material_equivalence_progress.json',list(pairs.values()))
            print('material equivalence',now['definition'],result['passed'],flush=True)
        passed=pairs[pair]['passed']
    err=frame_error(mat(now['frame']),expected)
    rows.append(dict(name=name,scope=scope,exact_definition_brep=same,frame_error_mm=err,
        material_equivalent=passed,passed=bool(passed and err<1e-7)))

source_items={key:{row['name']:row for row in models[key]['occurrences']} for key in ['water','drive','oil','receiver']}
preserved={name for name in source_items['water'] if name!='EngineCase_lower' and
           not name.startswith(('EngineWaterPump_','EngineLowerDrive_'))}
ck('unchanged parent coverage derived from source native',preserved==set(r['preserved_parent_ids']) and len(preserved)==2152)
for name in sorted(preserved):
    old=source_items['water'][name];compare(name,'water',old,mat(old['frame']),'unchanged_parent')
for key,prefix in [('water','EngineWaterPump_'),('drive','EngineLowerDrive_')]:
    inverse=np.linalg.inv(mat(models[key]['assemblies']['TankLibertyEngine']['world']))
    delta=translation(0,0,water_z-models[key]['assemblies']['EngineWaterPump']['local'][11]) if key=='water' else np.eye(4)
    for name,old in source_items[key].items():
        if name.startswith(prefix):compare(name,key,old,engine@delta@inverse@mat(old['frame']),key)
pose=models['oil']['assemblies']['EngineOilPump']['proposed_engine_pose'];basis=engine@translation(pose['x'],pose['y'],pose['z'])
for name,old in source_items['oil'].items():
    compare(name,'oil',old,basis@mat(old['frame']),'oil')
    now=items[name];sd=models['oil']['definitions'][old['definition']];td=current['definitions'][now['definition']]
    assert sd['properties']==td['properties'],name
    assert now['definition']==r['definitions'][sd['properties']['DefinitionKey']],name
    assert now['owners'][-1]==old['owners'][-1],name
old=source_items['receiver']['EngineCase_lower'];compare('EngineCase_lower','receiver',old,engine@mat(old['frame']),'receiver')
ck('all saved definitions and composed frames match sources',len(rows)==len({v['name'] for v in rows})==2393 and all(v['passed'] for v in rows),
   counts={k:sum(v['scope']==k for v in rows) for k in ['unchanged_parent','water','drive','oil','receiver']},failures=[v for v in rows if not v['passed']])
ck('pump parentage and identities preserved',all(name in current['assemblies']['TankLibertyEngine']['children']
   for name in ['EngineOilPump','EngineWaterPump']) and len(r['definitions'])==40)
local_path=receiver_report.parent/'independent_checks.json';local=read(local_path)
ck('local mechanical evidence bound to exact receiver',local['local_mechanical_passed'] and
   local['native_sha256']==rr['native_sha256'] and sha(local_path)==r['input_hashes'][str(local_path.relative_to(ROOT))])
ck('frame negative control rejects 1mm water-axis displacement',frame_error(engine,engine@translation(0,0,1))>1e-7)
write(out/'independent_checks.json',dict(passed=all(v['passed'] for v in checks),native_sha256=sha(native),
    checker_sha256=sha(Path(__file__)),worker_sha256=sha(worker),checks=checks,occurrences=rows,
    material_equivalence=list(pairs.values()),reused_completed_material_pairs=reused,physical_occurrences=len(items),
    manifests={key:sha(area/key/'manifest.json') for key in models},
    local_mechanical_reuse=dict(receiver_checks=len(local['checks']),case_pairs=len(local['material_pairs']),
        cross_component_pairs=len(local['cross_component_pairs']),basis='Exact BReps or strict bidirectional material equivalence, plus every composed frame verified'),
    standard_assembly_modified=False,installation_qualified=False,hydraulic_circuit_qualified=False,
    inherited_floor_envelope_gap_mm=local['inherited_floor_envelope_gap_mm']))
assert all(v['passed'] for v in checks)
if a.render:run([HERE/'render_engine_pumps_integration.py','--candidate',out],out/'render_runtime')
