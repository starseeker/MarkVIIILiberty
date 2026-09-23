"""Sequential saved-artifact qualification with durable command receipts."""
from pathlib import Path
import json,subprocess,sys,time
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains'
w=root/'.work/engine-water-pump-passage';b=h/'engine_water_pump_passage_study'
commands=[
    [h/'engine_water_pump_build.py','--output',b],
    [h/'check_engine_water_pump.py','--candidate',b,'--preservation','--standard-context'],
    [h/'check_engine_water_pump_exchange.py','--candidate',b],
    [h/'engine_water_pump_build.py','--output',w/'variant','--controls',w/'variant_controls.json'],
    [h/'check_engine_water_pump.py','--candidate',w/'variant','--preservation','--standard-context'],
    [h/'check_engine_water_pump_exchange.py','--candidate',w/'variant'],
    [h/'engine_water_pump_build.py','--output',w/'fresh_nominal'],
    [w/'check_reproduction.py'],
    [h/'render_engine_water_pump.py','--candidate',b],
]
results=[]
for command in commands:
    print('START',*map(str,command),flush=True);start=time.time()
    result=subprocess.run([sys.executable,*map(str,command)],cwd=root)
    results.append(dict(command=list(map(str,command)),exit_code=result.returncode,elapsed_seconds=time.time()-start))
    (w/'qualification_pipeline.json').write_text(json.dumps(results,indent=2)+'\n')
    print('FINISH',command[0].name,result.returncode,flush=True)
    if result.returncode:sys.exit(result.returncode)
