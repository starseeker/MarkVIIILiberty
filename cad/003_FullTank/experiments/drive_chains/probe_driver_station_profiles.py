"""Save and test complete handles at a conditional source station.

This is a bounded bow/seat clearance experiment. It deliberately does not assert
rod closure, supporting structure, whole-tank fit, STEP acceptance or installation.
"""
import argparse
import itertools
import os
from pathlib import Path
from control_rebuild_io_v2 import *

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
F=C/'driver_redo01';review=H/'driver_station_review/visibility01/report.json'
e=read(review);parent=Saved(F/'operating_integrated01')
seat=Saved(H/'driver_seat_support_study/trial01')
seat_names=read(H/'driver_seat_study/trial06/report.json')['new_occurrences']
bow_names=read(H/'driver_layout_study/trial01/report.json')['details']['bow_occurrences']
old=App.Vector(*parent.report['details']['foundation']['shafts']['Main']['center_world_mm'])
new=App.Vector(*e['shaft_pair']['main_construction_world_mm']);delta=new-old
records=parent.report['details']
rods=[records['rods']['Front']]
for side in ['Port','Starboard']:
    rods += [records['low_speed'][side],records['high_controls'][side]['rods']['Front']]
omit_rods={'DriverClutchFrontRod','PortDriverLowRod','StarboardDriverLowRod',
           'PortDriverHighFrontRod','StarboardDriverHighFrontRod'}
for rod in rods:
    for endpoint in rod['endpoints']:
        omit_rods.update(endpoint['stem']+v for v in ['Fork','Pin','Cotter','Nut'])
unit=[n for n,r in parent.rows.items() if 'DriverControlFoundation' in r['owners']
      and 'DriverSupportPlates' not in r['owners'] and 'DriverFloorContext' not in r['owners']
      and n not in omit_rods]
assert len(unit)==72 and len(seat_names)==38 and len(bow_names)==40
cases={};worlds={}
for label in ['overall_control','pivot_reach','functional_current','functional_source']:
    profile=Saved(F/'handle_profiles01'/label)
    proof=read(profile.folder/'profile_checks02/report.json')
    assert proof['passed'] and proof['native_sha256']==sha(profile.native)
    shapes={};specs={};props={}
    for name in unit+seat_names+bow_names:
        moving=name in unit
        src=profile if name.endswith('DriverOperatingHandle') else parent if moving else seat
        row=src.rows[name];key=row['definition']
        if key not in shapes:
            shapes[key]=src.definition(key);props[key]=src.manifest['definitions'][key]['properties']
        place=pose(row['frame'])
        if moving:place.Base+=delta
        specs[name]=dict(definition=key,frame=list(place.toMatrix().A),
            owner='DriverMechanism' if moving else 'SeatContext' if name in seat_names else 'BowContext',
            role='mechanism' if moving else 'fixed_context')
    scope='150-part clearance experiment only:72 driver parts translated rigidly,38 fixed seat parts,40 fixed bow plates. Long front rods, support plates/stays/angles, their floor attachments and full retained tank context are absent; installation is not qualified.'
    details=dict(scope=scope,hypothesis=label,driver_translation_from_accepted_mm=list(delta),
        main_world_mm=list(new),unit_occurrences=unit,seat_occurrences=seat_names,bow_occurrences=bow_names,
        source_camera_refitted=False,full_stock_closure=e['full_stock_closure'],
        profile_source=str(profile.folder.relative_to(ROOT)),profile_native_sha256=sha(profile.native))
    case=out/label
    native=trial(case,parent,shapes,specs,props,details,
        [Path(__file__),H/'control_rebuild_io_v2.py',review,profile.folder/'report.json',
         profile.folder/'profile_checks02/report.json',seat.folder/'report.json',
         seat.folder/'isolated/manifest.json',H/'driver_seat_study/trial06/report.json',
         H/'driver_layout_study/trial01/report.json'],
        changed_definitions=[specs[n]['definition'] for n in unit if n.endswith('DriverOperatingHandle')])
    # Read actual saved solids and transforms, not the construction shape dict.
    doc=App.openDocument(str(native));world={};valid=[]
    assert all(o.Placement.isIdentity() for o in doc.Objects if o.TypeId=='App::Part')
    for name in specs:
        link=doc.getObject(name);q=link.LinkedObject.Shape.copy();q.Placement=link.LinkPlacement
        valid.append(dict(name=name,passed=q.isValid() and len(q.Solids)==1 and q.Solids[0].isClosed()))
        assert valid[-1]['passed'],name
        world[name]=q
    App.closeDocument(doc.Name)
    pairs=[]
    for first,second in itertools.combinations(world,2):
        if first not in unit and second not in unit:continue
        q,t=world[first],world[second]
        if not q.BoundBox.intersect(t.BoundBox):continue
        common=q.common(t);vol=sum(abs(v.Volume) for v in common.Solids)
        pairs.append(dict(first=first,second=second,volume_mm3=vol,
            passed=vol<1e-5 and (common.isNull() or common.isValid())))
    findings=[r for r in pairs if not r['passed']]
    handle_results={}
    for side in ['Port','Starboard']:
        name=side+'DriverOperatingHandle';q=world[name]
        handle_results[side]=dict(bow_distance_mm=q.distToShape(world['hull_front_slope'])[0],
            seat_distance_mm=min(q.distToShape(world[n])[0] for n in ['DriverSeatFrame','DriverSeatCushion','DriverSeatBackPadding']),
            actual_cap_world_mm=list(App.Vector(*proof['records'][side]['actual_tip_world_mm'])+delta),
            inherited_local_plan_residual_px=proof['records'][side]['plan_residual_px'],
            inherited_local_side_residual_px=proof['records'][side]['side_residual_px'])
    result=dict(native_sha256=sha(native),worker_sha256=sha(Path(__file__)),scope=scope,
        valid_saved_solids=valid,pairs=pairs,findings=findings,no_mating_exemptions=True,
        local_clearance_passed=not findings,installation_qualified=False,geometry_integrated=False,
        source_camera_refitted=False,handles=handle_results)
    write(case/'clearance_report.json',result);cases[label]=result;worlds[label]=world
    print(label,len(pairs),'pairs',len(findings),'findings',[(r['first'],r['second'],round(r['volume_mm3'],3)) for r in findings],flush=True)

os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.work/driver-station-probe-20260927/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
cal=read(H.parents[1]/'data/calibrations.json')['snl_2'];params=read(H.parents[1]/'data/parameters.json')
scale=[cal['axes'][v]['sign']*params[cal['axes'][v]['span_parameter']]['value']/abs(cal['axes'][v]['pixels'][1]-cal['axes'][v]['pixels'][0]) for v in ['x','z']]
source=ROOT/cal['image'];im=Image.open(source).convert('RGB')
pixel=lambda q:[cal['datum_pixel'][0]+q.x/scale[0],cal['datum_pixel'][1]+q.z/scale[1]]
fig,axes=plt.subplots(2,2,figsize=(14,11),dpi=150)
for ax,(label,world) in zip(axes.flat,worlds.items()):
    ax.imshow(im)
    for name in ['hull_front_slope','DriverMainShaft','DriverSwingShaft','PortDriverOperatingHandle',
                 'PortDriverOperatingFulcrum','PortDriverLowSelector','PortDriverHighSelector','DriverSeatFrame']:
        color='#387b43' if name=='hull_front_slope' else '#916342' if name=='DriverSeatFrame' else '#2455a3'
        for edge in world[name].Edges:
            points=[pixel(q) for q in edge.discretize(Deflection=1.)]
            if len(points)>1:ax.plot(*zip(*points),color=color,linewidth=.65,alpha=.8)
    ax.set_xlim(315,560);ax.set_ylim(480,260);ax.set_aspect('equal')
    r=cases[label];h=r['handles']['Port']
    ax.set_title(label.replace('_',' '))
    ax.text(.02,.02,f'{len(r["findings"])} local intersections; bow gap {h["bow_distance_mm"]:.2f} mm\nLocal drawing residuals unchanged: plan {h["inherited_local_plan_residual_px"]:.2f}, side {h["inherited_local_side_residual_px"]:.2f} px',
        transform=ax.transAxes,fontsize=8,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'))
fig.suptitle('Conditional aft driver station | complete saved profiles, unchanged SNL2 calibration')
fig.text(.04,.015,'Blue: actual saved mechanism; brown: fixed seat frame; green: corrected bow.\nLong rods and supporting structure are omitted from this feasibility probe. Full-stock closure requires a coupled intermediate-station revision. No installation acceptance.',fontsize=9)
fig.tight_layout(rect=(0,.07,1,.95));fig.savefig(out/'source_comparison.png');plt.close(fig)
write(out/'probe_receipt.json',dict(worker_sha256=sha(Path(__file__)),review_sha256=sha(review),
    source_sha256=sha(source),calibration_sha256=sha(H.parents[1]/'data/calibrations.json'),
    parameter_sha256=sha(H.parents[1]/'data/parameters.json'),
    cases={n:dict(native_sha256=r['native_sha256'],report_sha256=sha(out/n/'report.json'),
        clearance_report_sha256=sha(out/n/'clearance_report.json')) for n,r in cases.items()},
    image_sha256=sha(out/'source_comparison.png'),source_camera_refitted=False,installation_qualified=False))
print('Four bounded saved-native station/profile probes finished.',flush=True)
