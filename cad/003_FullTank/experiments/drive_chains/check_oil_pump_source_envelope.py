"""Compare actual saved cylinders with independent HB45 image intervals.

The prior oversized study is a negative control. This verifies only conditional
source envelopes/levels, not internal material, historical configuration, or fit.
"""
import argparse,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parents[1])]
import FreeCAD as App
import Part
from lib.evidence import read,write,sha

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--sources',type=Path,default=HERE/'engine_pump_layout_study/source_constraints.json')
p.add_argument('--profile-sources',type=Path)
a=p.parse_args();candidate=a.candidate.resolve();source=read(a.sources)
profile=read(a.profile_sources) if a.profile_sources else None
if profile:assert profile['source_constraints_sha256']==sha(a.sources)


def measure(folder):
    report=read(folder/'report.json');native=folder/report['native_file'];assert sha(native)==report['native_sha256']
    doc=App.openDocument(str(native))
    try:
        s=doc.Def_lower_body.Shape
        centered=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder)
                  and abs(f.Surface.Axis.z)>.999999 and abs(f.Surface.Center.x)<1e-7
                  and abs(f.Surface.Center.y)<1e-7]
        body=2*max(f.Surface.Radius for f in centered if f.BoundBox.ZMin<-30<f.BoundBox.ZMax)
        flange=2*max(f.Surface.Radius for f in centered if f.BoundBox.ZMin<-.1<f.BoundBox.ZMax)
        placement=json.loads(doc.EngineOilPump.ProposedEnginePlacementJSON)
        side=[f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Axis.y)>.999999
              and abs(f.Surface.Center.x)<1e-7]
        supply=[f for f in side if abs(f.Surface.Radius-7)<1e-7 and f.BoundBox.YMin<-body/2+1]
        returned=[f for f in side if abs(f.Surface.Radius-4.5)<1e-7 and f.BoundBox.YMax>body/2-1]
        assert supply and returned,'Actual external connection bores not found'
        supply_z={round(f.Surface.Center.z+placement['z'],7) for f in supply}
        return_z={round(f.Surface.Center.z+placement['z'],7) for f in returned}
        assert len(supply_z)==len(return_z)==1,(supply_z,return_z)
        values=dict(body=body,flange=flange,supply_z=supply_z.pop(),return_z=return_z.pop())
        checks=[]
        for key in ['body','flange']:
            low,high=source['widths'][key]['pixel_only_interval_mm']
            checks.append(dict(name=key+'_native_diameter',actual_mm=values[key],source_pick_interval_mm=[low,high],
                               passed=low<=values[key]<=high))
        for key,dimension in [('supply_z','right_connection_drop'),('return_z','left_connection_drop')]:
            target=-source['printed'][dimension]['exact_inch_conversion_mm']
            checks.append(dict(name=key+'_proposed_engine_level',actual_mm=values[key],target_mm=target,
                comparison_tolerance_mm=.1,passed=abs(values[key]-target)<=.1,
                note='Conditional connection identification and proposed metadata pose, not a physically installed pump.'))
        if profile:
            cover=doc.Def_cover.Shape
            rim=[f for f in cover.Faces if isinstance(f.Surface,Part.Cylinder)
                 and abs(f.Surface.Axis.z)>.999999 and abs(2*f.Surface.Radius-flange)<1e-7
                 and abs(f.Surface.Center.x)<1e-7 and abs(f.Surface.Center.y)<1e-7]
            assert rim,'Outer cover-rim cylinder missing'
            row=next(r for r in report['occurrences'] if r['key']=='drain_plug')
            link=doc.getObject(row['name']);drain=link.LinkedObject.Shape.copy()
            drain.Placement=doc.getObject(row['assembly']).getGlobalPlacement().multiply(link.LinkPlacement).multiply(drain.Placement)
            levels=dict(body_bottom=-(s.BoundBox.ZMin+placement['z']),
                cover_rim_bottom=-(min(f.BoundBox.ZMin for f in rim)+placement['z']),
                drain_tip=-(drain.BoundBox.ZMin+placement['z']))
            values.update(levels)
            for key,depth in levels.items():
                low,high=profile['features'][key]['pixel_only_interval_mm']
                checks.append(dict(name=key+'_depth_below_crankshaft',actual_mm=depth,
                    source_pick_interval_mm=[low,high],passed=low<=depth<=high,
                    note='Conditional local image-scaled depth, using proposed pose.'))
        return dict(native_sha256=sha(native),measured=values,checks=checks,passed=all(x['passed'] for x in checks))
    finally:App.closeDocument(doc.Name)


current=measure(candidate)
old=measure(HERE/'engine_oil_pump_mounting_study')
result=dict(candidate=current,prior_negative_control=old,
    prior_rejected=not old['passed'] and all(not r['passed'] for r in old['checks']),
    source_constraints_sha256=sha(a.sources),checker_sha256=sha(Path(__file__)),
    scope='Conditional HB45 body/flange envelopes and proposed oil-connection levels only',
    installation_qualified=False)
if profile:result['profile_sources_sha256']=sha(a.profile_sources)
result['passed']=current['passed'] and result['prior_rejected']
write(candidate/'source_envelope_checks.json',result)
print(json.dumps(result,indent=2),flush=True)
assert result['passed']
