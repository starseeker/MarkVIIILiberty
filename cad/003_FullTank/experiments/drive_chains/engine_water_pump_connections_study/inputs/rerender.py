from pathlib import Path
import json,shutil,subprocess,sys,time
root=Path('/home/cyapp/MarkVIIILiberty');w=root/'.work/engine-water-pump-lock';h=root/'cad/003_FullTank/experiments/drive_chains';b=h/'engine_water_pump_connections_study';before=w/'before_display_cleanup';before.mkdir(exist_ok=True)
p=w/'qualification_pipeline.json';d=json.loads(p.read_text());assert len(d)==9 and all(x['exit_code']==0 for x in d)
for source in [p,b/'source_review/render_receipt.json',b/'source_review/drain_lock.png']:shutil.copy2(source,before/source.name)
start=time.time();result=subprocess.run([sys.executable,*d[-1]['command']],cwd=root)
d[-1].update(exit_code=result.returncode,elapsed_seconds=time.time()-start,display_revision='Hide detached cover slivers created by detail crop; no native geometry change',superseded_render_receipt=str(before/'render_receipt.json'))
p.write_text(json.dumps(d,indent=2)+'\n');sys.exit(result.returncode)
