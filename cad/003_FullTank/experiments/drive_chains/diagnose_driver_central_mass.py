"""Measure the unchanged saved bridle/STEP pair with independent OCC integrators."""
from control_rebuild_io_v2 import *
from lib.mass_properties import AdaptiveMass
from lib.kronrod_mass import KronrodMass
N=H/'driver_foot_reverse_study';out=N/'central_mass_diagnostics01';out.mkdir(exist_ok=False)
mass=AdaptiveMass(out/'gauss_runtime');gk=KronrodMass(out/'kronrod_runtime');rows=[]
for case in ['central03','central_variation03']:
    s=Saved(N/case);ex=read(s.folder/'exchange01/exchange_checks.json')
    for scope in ['Definitions','Installed']:
        row=next(q for q in ex['checks'] if q['scope']==scope and 'Bridle' in q['name'] and not q['passed'])
        native=s.definition(row['name']) if scope=='Definitions' else s.world(row['name'])
        file=s.folder/'exchange01'/('RebuiltControlAdditions'+scope+'.step');assert sha(file)==ex['step_hashes'][file.name]
        recovered=Part.Shape();recovered.read(str(file));step=recovered.Solids[row['step_solid_index']]
        for kind,q in [('native',native),('step',step)]:
            item=dict(case=case,scope=scope,kind=kind,gauss=mass.measure(q),kronrod=gk.measure(q),kernel_volume=q.Volume)
            rows.append(item);write(out/'progress.json',rows);print(case,scope,kind,item['gauss']['converged'],item['kronrod']['converged'],item['gauss']['volume_mm3'],flush=True)
write(out/'report.json',dict(worker_sha256=sha(Path(__file__)),measurements=rows,provenance={'gauss':mass.provenance,'kronrod':gk.provenance},inputs={str(N/case/'exchange01/exchange_checks.json'):sha(N/case/'exchange01/exchange_checks.json') for case in ['central03','central_variation03']}))
