"""Fit/reassess an image packet; optionally render through the headless launcher."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'cad/003_FullTank'))
from lib.source_camera import cached_fit
from lib.camera_review import resolve_packet,render,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('packet',type=Path);p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--render',action='store_true')
    a=p.parse_args();packet=json.loads(a.packet.read_text())
    # Paths in review packets are relative to the repository, never a temp cwd.
    for key in ['source_image','native_file','manifest']:
        if key in packet: packet[key]=str((ROOT/packet[key]).resolve())
    manifest=None
    if 'manifest' in packet: packet,manifest=resolve_packet(packet)
    if a.output.exists(): raise ValueError('Preserve old assessments; choose a fresh output directory')
    a.output.mkdir(parents=True)
    result=cached_fit(packet,a.cache)
    if a.render:
        if manifest is None: raise ValueError('Rendering requires a native-bound manifest')
        result['render']=render(packet,manifest,result['camera'],a.output,a.output/'runtime')
    result['packet_sha256']=sha(a.packet)
    result['historical_geometry_qualified']=False
    result['projection_classification']=packet.get('projection_classification','unreviewed')
    (a.output/'assessment.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    packet['previous_fit_key']=result['fit_key'];packet.pop('refit_review',None)
    (a.output/'next_packet.json').write_text(json.dumps(packet,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['fit_key','reused','status','issues','original_fit_seconds','current_evaluation_seconds']},indent=2))


if __name__=='__main__': main()
