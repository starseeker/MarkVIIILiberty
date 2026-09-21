"""Populate the opposed input bearings and principal M250 housing assembly."""
import argparse
from collections import Counter
import json, math
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--stage',type=Path,required=True)
p.add_argument('--output',type=Path,default=ROOT/'transmission_input_build')
p.add_argument('--worker',action='store_true')
args=p.parse_args();stage=args.stage.resolve();out=args.output.resolve();sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part,numpy as np
    from lib.cad_build import leaves,metadata,shape_signature
    from lib.worker import check_build,same_shape,placement_errors
    from transmission_input_parts import tapered_bearing,input_stack,retention,cylinder,box
    parent=ROOT/'transmission_bevel_gear_build';prior=read(parent/'report.json')
    assert prior['passed'] and prior['rendering_complete']
    native_parent=parent/'TransmissionBevelGearCandidate.FCStd'
    assert sha(native_parent)==prior['native_sha256']
    lock=fingerprint();build=check_build(stage/'build')
    names=['transmission_input_probe.py','transmission_input_parts.py','transmission_input_controls.json','transmission_input_sources.json','transmission_input_calibration.json',
        'transmission_stud_parts.py','transmission_core_parts.py','transmission_bevel_gear_build/report.json',
        'transmission_bevel_gear_build/interface_checks.json','transmission_bevel_gear_build/visual_review.json',
        'transmission_bevel_gear_build/TransmissionBevelGearCandidate.FCStd']
    hashes={n:sha(ROOT/n) for n in names}
    for n in names:
        if '/' not in n:
            dest=out/'inputs'/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    source=read(ROOT/'transmission_input_sources.json');rows={r['key']:r for r in source['physical_inventory']}
    assert all(sha(REPO/n)==h for n,h in source['source_hashes'].items())
    controls=read(ROOT/'transmission_input_controls.json');c=controls['stack'];b=controls['bearing']
    doc=App.openDocument(str(native_parent));doc.recompute();before=leaves(doc.Root);old={i['id']:i for i in before}
    signatures={i['id']:shape_signature(i['shape']) for i in before}
    changed=['CenterBevelDrive_pinion','CenterTransmissionCore_bevel_cover']
    originals={k:old[n]['target'].Shape.copy() for k,n in zip(['shaft','cover'],changed)}
    bearing,bd=tapered_bearing(b);parts,d=input_stack(c,b,originals['shaft'],originals['cover']);parts.update(retention(c))
    d['bearing']=bd
    for k,n in zip(['shaft','cover'],changed):
        old[n]['target'].Tip.Shape=parts[k]
        metadata(old[n]['target'],InputAssemblyRevision='Printed Timken envelope; pinion shoulder and extended spline; enlarged cover pilot receiver.',
            ParameterUpdate='Regenerate with transmission_input_probe.py and transmission_input_controls.json.')
    group=doc.addObject('App::Part','InputHousingAssembly');doc.TransmissionCore.addObject(group)
    metadata(group,Scope='Opposed Timken bearings, provisional single M249 spacer, MX35/M254 shims, housing, seals, coupling and shaft retention. Pump studs, lubrication, bracket and cover fasteners remain pending.',
        SurveyIds=['P_fb4ab8fe19c1d787'],InventoryQuantityRole='assembly container, not an extra physical part')
    metadata(doc.CenterBevelDrive,Scope='M247 integral pinion/shaft revised for input bearings; M257A clutch in standard ahead engagement.')
    definitions={}
    keys=['housing','coupling','spacer','spacer_shim','flange_shim','disk','felt','gland','washer','nut','cotter','gland_bolt','gland_nut','inner_race','cup','cage','roller']
    for key in keys:
        internal=key in ['inner_race','cage','roller'];row=rows['cone' if internal else key]
        shape=bearing[key] if key in bearing else parts[key]
        body=doc.addObject('PartDesign::Body','Def_TransmissionInput_'+key);doc.Definitions.addObject(body)
        body.newObject('PartDesign::Feature','ReconstructedPart').Shape=shape
        metadata(body,DefinitionId='transmission_input_'+key,OriginalMark=row['mark']+(' / inferred '+key if internal else ''),
            SurveyIds=[] if internal else [row['part_id']],SourceRecord=row['record_id'],Representation='assembly',Coverage='partial',
            ReconstructionNotes='Printed bearing envelope and source counts; tapers, rollers, casting, fits, thread envelopes and coupling pattern inferred. Cotter legs not spread.',
            ParameterUpdate='Regenerate with transmission_input_probe.py and transmission_input_controls.json.')
        if internal:metadata(body,ParentSurveyId=row['part_id'],InventoryQuantityRole='inferred commercial cone decomposition')
        if key=='cup':metadata(body,SurveyAliases=['P_6bdbb5f34d914472'])
        definitions[key]=body
    new_ids=[];expected={};key_by_id={};containers=[]
    def link(parent,name,key,placement=None):
        obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(definitions[key]);obj.LinkPlacement=placement or App.Placement()
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain',SourceRecord=definitions[key].SourceRecord)
        base=doc.TransmissionCore.Placement
        if parent!=group:base=base.multiply(doc.getObject('InputBearing'+parent.Name[-1]).Placement)
        expected[name]=base.multiply(obj.LinkPlacement).multiply(definitions[key].Shape.Placement)
        new_ids.append(name);key_by_id[name]=key
    for key in ['housing','coupling','spacer','disk','felt','gland','washer','nut','cotter']:
        link(group,'InputHousing_'+key,key)
    for key,count,start,stock in [('spacer_shim',c['spacer_shim_count'],d['spacer_limits'][1],c['spacer_shim_stock']),
        ('flange_shim',c['flange_shim_count'],c['cover_end'],c['flange_shim_stock'])]:
        for n in range(count):link(group,'InputHousing_'+key+str(n).zfill(2),key,App.Placement(App.Vector(start+n*stock,0,0),App.Rotation()))
    for n in range(4):
        angle=math.pi/4+n*math.pi/2;y=c['gland_bolt_circle']*math.cos(angle);z=c['gland_bolt_circle']*math.sin(angle)
        link(group,'InputHousing_gland_bolt'+str(n),'gland_bolt',App.Placement(App.Vector(0,y,z),App.Rotation()))
        for m in range(2):link(group,'InputHousing_gland_nut'+str(n)+'_'+str(m),'gland_nut',App.Placement(App.Vector(c['gland_end']+m*c['gland_nut_height'],y,z),App.Rotation()))
    for n,station in enumerate(d['bearing_small_end_stations']):
        bearing_group=doc.addObject('App::Part','InputBearing'+str(n));group.addObject(bearing_group)
        bearing_group.Placement=App.Placement(App.Vector(station,0,0),App.Rotation(App.Vector(0,0,1),180) if n==0 else App.Rotation())
        row=rows['bearing'];metadata(bearing_group,SurveyIds=[row['part_id']],SurveyAliases=['P_96ec390be9709327'],SourceRecord=row['record_id'],CatalogueQuantity=1,InventoryQuantityRole='commercial bearing assembly')
        containers.append(bearing_group.Name)
        cone=doc.addObject('App::Part','InputCone'+str(n));bearing_group.addObject(cone);row=rows['cone']
        metadata(cone,SurveyIds=[row['part_id']],SurveyAliases=['P_afe8298c164f36c5'],SourceRecord=row['record_id'],CatalogueQuantity=1,InventoryQuantityRole='commercial cone assembly including rollers/cage')
        containers.append(cone.Name)
        link(bearing_group,'InputBearing'+str(n)+'_cup','cup')
        for key in ['inner_race','cage']:link(cone,'InputBearing'+str(n)+'_'+key,key)
        for m in range(b['roller_count']):link(cone,'InputBearing'+str(n)+'_roller'+str(m).zfill(2),'roller',App.Placement(App.Vector(),App.Rotation(App.Vector(1,0,0),m*360/b['roller_count'])))
    doc.Definitions.Visibility=False;doc.recompute();native=out/'TransmissionInputCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root);byid={i['id']:i for i in items}
    assert len(items)==len(byid)==len(before)+len(new_ids)==1287
    for i in items:
        name=i['id'];assert i['shape'].isValid() and len(i['shape'].Solids)==1,name
        if name in expected:
            t,r=placement_errors(i['shape'].Placement,expected[name]);assert t<1e-6 and r<1e-8,(name,t,r)
        elif name not in changed:assert same_shape(signatures[name],shape_signature(i['shape'])),name
    counts=Counter(pid for n in new_ids for pid in json.loads(byid[n]['target'].SurveyIds))
    for n in containers:counts.update(json.loads(doc.getObject(n).SurveyIds))
    assert dict(counts)=={r['part_id']:r['count'] for r in source['physical_inventory']}
    print('Reopened',len(items),'valid leaves:',len(new_ids),'new; two revised. Source counts reconciled with explicit aliases/conflicts.',flush=True)
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    excluded={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting','hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in excluded and i['representation']=='assembly'];physical=items+context
    assert len({i['id'] for i in physical})==len(physical)
    boxes=np.array([[v.XMin,v.YMin,v.ZMin,v.XMax,v.YMax,v.ZMax] for v in [i['shape'].copy().cleaned().BoundBox for i in physical]])
    pairs=set();overlaps=[]
    for name in new_ids+changed:
        a=byid[name]['shape'];v=a.copy().cleaned().BoundBox;bb=np.array([v.XMin,v.YMin,v.ZMin,v.XMax,v.YMax,v.ZMax])
        near=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for index in near:
            other=physical[index];pair=tuple(sorted([name,other['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);vol=a.common(other['shape']).Volume
            if vol>1e-5:overlaps.append(dict(a=name,b=other['id'],volume_mm3=vol))
        write(out/'material_progress.json',dict(last_id=name,pairs=len(pairs),overlaps=overlaps))
    protection={}
    mask=box(c['shoulder_start']-1,500,-200,200,-200,200)
    a=originals['shaft'].cut(mask);v=parts['shaft'].cut(mask);protection['pinion_head_unchanged_mm3']=a.cut(v).Volume+v.cut(a).Volume
    mask=cylinder(c['cover_boss_radius']+1,c['cover_boss_start']-1,c['cover_end']+1)
    a=originals['cover'].cut(mask);v=parts['cover'].cut(mask);protection['cover_outside_input_boss_mm3']=a.cut(v).Volume+v.cut(a).Volume
    assert all(v<1e-5 for v in protection.values()),protection
    interfaces=[]
    def gap(a,b,want,tol=1e-5):
        v=byid[a]['shape'].distToShape(byid[b]['shape'])[0]
        interfaces.append(dict(a=a,b=b,gap_mm=v,expected_mm=want,passed=abs(v-want)<tol))
    for row in prior['interfaces']:
        if row['a'] in changed or row['b'] in changed:continue
        gap(row['a'],row['b'],row['expected_mm'])
    for n in range(2):
        prefix='InputBearing'+str(n)+'_'
        gap(prefix+'inner_race','CenterBevelDrive_pinion',0 if n==0 else .1)
        for m in range(b['roller_count']):
            for race in ['inner_race','cup']:gap(prefix+'roller'+str(m).zfill(2),prefix+race,b['race_clearance']*math.cos(math.radians(bd['roller_half_angle_degrees'])))
    for a,b,w in [('coupling','washer',0),('washer','nut',0),('disk','felt',0),('felt','gland',0),('felt','coupling',0)]:gap('InputHousing_'+a,'InputHousing_'+b,w)
    gap('InputBearing1_inner_race','InputHousing_coupling',0)
    gap('InputBearing0_cup','InputHousing_spacer',0)
    gap('InputBearing1_cup','InputHousing_spacer_shim12',0)
    gap('InputBearing1_cup','InputHousing_disk',0)
    for n in range(4):
        gap('InputHousing_gland_bolt'+str(n),'InputHousing_housing',0)
        gap('InputHousing_gland_nut'+str(n)+'_0','InputHousing_gland',0)
        gap('InputHousing_gland_nut'+str(n)+'_0','InputHousing_gland_nut'+str(n)+'_1',0)
    print('Material pairs',len(pairs),'overlaps',overlaps,flush=True)
    print('Failed interfaces',[r for r in interfaces if not r['passed']],flush=True)
    write(out/'fit_checks.json',dict(overlaps=overlaps,interfaces=interfaces,protected_material_differences_mm3=protection))
    exchange=out/'TransmissionInputParts.step';exchange_ids=new_ids+changed
    Part.makeCompound([byid[n]['shape'] for n in exchange_ids]).exportStep(str(exchange))
    imp=Part.Shape();imp.read(str(exchange));assert imp.isValid() and len(imp.Solids)==len(exchange_ids)
    unmatched=list(imp.Solids);checks=[]
    for name in exchange_ids:
        a=byid[name]['shape'].Solids[0];n=min(range(len(unmatched)),key=lambda n:(a.CenterOfMass-unmatched[n].CenterOfMass).Length);v=unmatched.pop(n)
        ta=a.getTolerance(1);tb=v.getTolerance(1);fuzzy=min(.0001,max(1e-7,ta+tb))
        missing=a.cut(v,fuzzy);extra=v.cut(a,fuzzy)
        checks.append(dict(id=name,native_max_tolerance_mm=ta,step_max_tolerance_mm=tb,comparison_fuzzy_tolerance_mm=fuzzy,
            raw_missing_mm3=a.cut(v).Volume,raw_added_mm3=v.cut(a).Volume,missing_mm3=missing.Volume,added_mm3=extra.Volume,
            passed=a.isValid() and v.isValid() and not missing.Faces and not extra.Faces and ta<=.0001 and tb<=max(1e-7,ta)*(1+1e-6)))
        write(out/'exchange_progress.json',dict(completed=len(checks),total=len(exchange_ids),failed=[r for r in checks if not r['passed']]))
    assert fingerprint()==lock and check_build(stage/'build')['native_hashes']==build['native_hashes']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    passed=not overlaps and all(r['passed'] for r in interfaces+checks)
    report=dict(complete=True,passed=passed,native_occurrences=len(items),new_occurrences=len(new_ids),new_definitions=len(definitions),
        changed_prior_occurrences=2,unchanged_prior_occurrences=len(before)-2,new_ids=new_ids,changed_ids=changed,keys_by_id=key_by_id,
        new_source_counts=dict(counts),bearing_inventory_containers=containers,material_candidate_pairs=len(pairs),overlaps=overlaps,interfaces=interfaces,
        dimensions=d,protected_material_differences_mm3=protection,shaft_axis_world_mm=prior['shaft_axis_world_mm'],input_hashes=hashes,
        authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],native_sha256=sha(native),exchange_sha256=sha(exchange),exchange_roundtrip_checks=checks,
        standard_assembly_modified=False,complete_transmission=False,historical_fit_qualified=False,rendering_complete=False,
        limitations=source['conflicts']+['MX25 cover fasteners, pump studs, lubrication and support bracket remain pending.','Cotter ends are unspread; commercial bearing internals inferred.'])
    write(out/'report.json',report);print('PASS' if passed else 'FAIL',flush=True);sys.exit(0 if passed else 1)
finally:runtime.close()
