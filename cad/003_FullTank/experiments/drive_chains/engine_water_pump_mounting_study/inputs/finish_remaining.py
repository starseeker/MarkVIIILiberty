from pathlib import Path
import subprocess,sys,json,time
root=Path('/home/cyapp/MarkVIIILiberty');h=root/'cad/003_FullTank/experiments/drive_chains';w=root/'.work/engine-water-pump-mounting';b=h/'engine_water_pump_mounting_study';results=[]
commands=[
 [h/'render_engine_water_pump.py'],
 [root/'skills/freecad-reconstruction/scripts/freecad_headless.py','--workdir',w/'empty_difference_probe',w/'probe_empty_difference.py'],
 [h/'check_engine_water_pump.py','--candidate',w/'variant','--preservation'],
 [h/'check_engine_water_pump_exchange.py','--candidate',w/'variant'],
 [h/'engine_water_pump_build.py','--output',w/'fresh_nominal'],
 [w/'check_reproduction.py'],
 [root/'skills/freecad-reconstruction/scripts/freecad_headless.py','--workdir',w/'frozen_trace_replay',b/'diagnostics/mounting_revision/trace_body.py']]
for command in commands:
 print('START',*[str(x) for x in command],flush=True);start=time.time()
 r=subprocess.run([sys.executable,*map(str,command)])
 results.append(dict(command=list(map(str,command)),exit_code=r.returncode,elapsed_seconds=time.time()-start));(w/'remaining_pipeline.json').write_text(json.dumps(results,indent=2)+'\n')
 print('FINISH',command[0].name,r.returncode,flush=True)
 if r.returncode:sys.exit(r.returncode)
