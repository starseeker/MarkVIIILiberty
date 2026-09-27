"""Verify complete world-curve signatures despite native topology-location bookkeeping."""
import argparse,copy
from pathlib import Path
from control_rebuild_io_v2 import App,Part,H,ROOT,Saved,read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();s=Saved(a.candidate);r=s.report
prior=read(s.folder/'diagnostics/guide_serialization01/initial_inherited_guide_checks.json')
assert prior['native_sha256']==sha(s.native) and prior['source_native_sha256']==r['source_native_sha256']
specs={v['name']:dict(source_native=r['source_native'],source_object=v['name'],inherited=True) for v in prior['checks']}
specs.update({n:dict(v,inherited=False) for n,v in r['nonphysical_guides'].items()})
def vector(v):return list(v)
def signature(shape):
    assert shape.isValid() and not shape.Faces and not shape.Solids
    edges=[]
    for e in shape.Edges:
        c=e.Curve;t=type(c).__name__;q=dict(type=t,range=[e.FirstParameter,e.LastParameter],length=e.Length,
          samples=[vector(e.valueAt(e.FirstParameter+(e.LastParameter-e.FirstParameter)*f)) for f in [0,.25,.5,.75,1]])
        if t=='BSplineCurve':q.update(poles=[vector(v) for v in c.getPoles()],weights=c.getWeights(),knots=c.getKnots(),multiplicities=c.getMultiplicities(),degree=c.Degree,periodic=c.isPeriodic())
        elif t=='BezierCurve':q.update(poles=[vector(v) for v in c.getPoles()],weights=c.getWeights(),degree=c.Degree)
        elif t=='Line':q.update(location=vector(c.Location),direction=vector(c.Direction))
        elif t=='Circle':q.update(center=vector(c.Center),axis=vector(c.Axis),radius=c.Radius)
        else:raise ValueError('Unqualified guide curve type: '+t)
        edges.append(q)
    return dict(edges=edges,vertices=[vector(v.Point) for v in shape.Vertexes],wires=len(shape.Wires),closed=shape.isClosed(),length=shape.Length)
def equal(a,b):
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return isinstance(b,(list,tuple)) and len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    if isinstance(a,(float,int)) and not isinstance(a,bool):return isinstance(b,(float,int)) and abs(a-b)<=1e-9
    return a==b
checks=[];sources={};doc=App.openDocument(str(s.native))
try:
    for source in sorted({v['source_native'] for v in specs.values()}):
        native=ROOT/source;sources[source]=sha(native);original=App.openDocument(str(native))
        try:
            for name,v in specs.items():
                if v['source_native']!=source:continue
                x,y=original.getObject(v['source_object']),doc.getObject(name);one,two=signature(x.Shape),signature(y.Shape)
                ta,tb=x.Shape.getTolerance(1),y.Shape.getTolerance(1)
                ok=equal(one,two) and tb<=max(ta,1e-7)+1e-10 and tb<=1e-4
                if not v['inherited']:
                    props={k:getattr(y,k) for k in y.PropertiesList if y.getGroupOfProperty(k)=='Reconstruction'}
                    ok=ok and props==v['properties'] and y in doc.getObject(v['group']).Group and name not in s.rows and v['source_native_sha256']==sha(native)
                # Positive equality plus translated negative on every whole guide.
                shifted=y.Shape.copy();shifted.translate(App.Vector(.01,0,0));negative=not equal(one,signature(shifted))
                checks.append(dict(name=name,passed=ok and negative,inherited=v['inherited'],source_signature=one,candidate_signature=two,tolerance_mm=[ta,tb],translated_001mm_rejected=negative))
                print(name,ok,negative,flush=True)
        finally:App.closeDocument(original.Name)
finally:App.closeDocument(doc.Name)
# A changed spline pole or clipped edge interval must also be rejected.
bs=next(v['source_signature'] for v in checks if any(e['type']=='BSplineCurve' for e in v['source_signature']['edges']));bad=copy.deepcopy(bs);next(e for e in bad['edges'] if e['type']=='BSplineCurve')['poles'][1][0]+=.01
cut=copy.deepcopy(bs);cut['edges'][0]['range'][1]-=.01
negatives=dict(spline_pole_001mm=not equal(bs,bad),trim_interval_001=not equal(bs,cut))
result=dict(passed=all(v['passed'] for v in checks) and all(negatives.values()),native_sha256=sha(s.native),source_native_sha256=r['source_native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,negative_controls=negatives,source_hashes=sources,coordinate_tolerance_mm=1e-9,scope='World-space analytic/B-spline definitions, full trim intervals, vertices, topology counts and tolerances. Extra native location records and vertex-coordinate bookkeeping do not establish a geometry change; physical solids are unchanged.')
write(s.folder/'guide_geometry_checks.json',result);print('GUIDES',len(checks),result['passed'],flush=True);assert result['passed'] and len(checks)==31
