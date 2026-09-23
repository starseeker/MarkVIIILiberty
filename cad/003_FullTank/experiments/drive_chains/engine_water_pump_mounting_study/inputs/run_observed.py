from pathlib import Path
import json,os,signal,subprocess,sys,time,resource
root=Path('/home/cyapp/MarkVIIILiberty');w=root/'.work/engine-water-pump-mounting';start=time.time();child=None
label=sys.argv[1];command=sys.argv[2:];log=w/(label+'_process.json')
def record(**extra):
 data=dict(label=label,command=command,elapsed_seconds=time.time()-start,supervisor_pid=os.getpid(),child_pid=child.pid if child else None,**extra)
 log.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data),flush=True)
def stop(signum,frame):
 record(signal=signum,status='supervisor received signal')
 if child and child.poll() is None:child.terminate()
 raise SystemExit(128+signum)
for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,stop)
child=subprocess.Popen(command,cwd=root);record(status='started')
while True:
 try:code=child.wait(timeout=20);break
 except subprocess.TimeoutExpired:record(status='running')
record(status='finished',exit_code=code,children_peak_rss_kb=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
sys.exit(code)
