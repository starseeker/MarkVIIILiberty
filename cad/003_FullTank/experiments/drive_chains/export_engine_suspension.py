"""Refresh suspension STEP exports with explicit surface curves; native is unchanged.

The default surface-curve mode loses sufficient p-curve accuracy on the bevel
washer's elliptical rim to fail the strict mass comparison. Mode1 preserves the
native trimming curves. This is an export setting, not tolerance inflation or
healing of the saved solid. Run after engine_suspension_build.py.
"""
import argparse
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,default=HERE/'engine_suspension_build')
p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'export_refresh.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],env=runtime.environment(out/'export_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    native=out/'DrivetrainWithEngineSuspension.FCStd';r=read(out/'report.json');nh=sha(native)
    assert nh==r['native_sha256']
    doc=App.openDocument(str(native));byid={i['id']:i for i in leaves(doc.Root)}
    Part.setStaticValue('write.surfacecurve.mode',1)
    for label,shapes in [('Definitions',[doc.getObject(n).Shape for n in read(out/'definition_order.json')]),
                         ('Installation',[byid[n]['shape'] for n in r['exchange_ids']])]:
        Part.makeCompound(shapes).exportStep(str(out/('EngineSuspension'+label+'.step')))
    assert sha(native)==nh
    hashes={f.name:sha(f) for f in out.glob('*.step')}
    write(out/'export_receipt.json',dict(native_sha256=nh,exporter_sha256=sha(Path(__file__)),
        setting={'write.surfacecurve.mode':1},artifact_hashes=hashes,native_modified=False,
        explanation='Retain surface trimming curves on export. No tolerance or saved material changes. Separate strict round-trip verification is required.'))
    r['artifact_hashes']=hashes;r['export_refresh_receipt_sha256']=sha(out/'export_receipt.json');write(out/'report.json',r)
    print('Refreshed20 definition and63 installed STEP solids; saved native unchanged.',flush=True)
finally:
    runtime.close()
