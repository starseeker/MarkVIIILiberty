import sys,subprocess,json,math
from pathlib import Path
repo=Path(__file__).resolve().parents[2];stage=repo/'cad/003_FullTank';sys.path.insert(0,str(stage));from lib import runtime
out=Path(__file__).resolve().parent
if '--worker' not in sys.argv:
    with (out/'spring_envelope_probe.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out),stdout=f,stderr=subprocess.STDOUT).returncode)
import FreeCAD as App,Part
from lib.evidence import write
s=Part.Shape();s.read(str(out/'spring_native.brep'));s.translate(App.Vector(-1825.2303627827532,0,-849.2335104357661))
x,y=-181.46496913580248,-135
v=[p for e in s.Edges for p in e.discretize(Number=1000)]
result=dict(volume=s.Volume,radial_sample=[min(math.hypot(p.x-x,p.y-y) for p in v),max(math.hypot(p.x-x,p.y-y) for p in v)],z_sample=[min(p.z for p in v),max(p.z for p in v)],placement=str(s.Placement))
print(result,flush=True);result['cuts']=[]
for extra in [.001,.0001,.00001]:
    print('cut',extra,flush=True);cy=Part.makeCylinder(17.4625/2+extra,30,App.Vector(x,y,185))
    result['cuts'].append(dict(extra=extra,missing=s.cut(cy).Volume));print(result['cuts'][-1],flush=True)
pts=[App.Vector(x,y0,z) for y0,z in [(-155,180),(-115,180),(-115,220),(-155,220),(-155,180)]]
section=s.section(Part.Face(Part.makePolygon(pts)))
result['section']=dict(edges=len(section.Edges),wires=len(section.Wires))
result['groups']=[dict(edges=len(es),closed=Part.Wire(es).isClosed()) for es in Part.sortEdges(section.Edges)]
write(out/'spring_envelope_probe.json',result);print(json.dumps(result),flush=True)
