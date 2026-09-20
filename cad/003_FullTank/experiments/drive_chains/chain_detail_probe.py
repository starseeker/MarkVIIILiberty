"""Qualify inferred oil passages and formed split-pin retention in both chains."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'chain_detail_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import read,write,sha,fingerprint,REPO
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),'--worker'],
            env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    import Part
    import numpy as np
    from types import SimpleNamespace
    from lib.cad_build import leaves,metadata
    from lib.worker import check_build
    from lib.visual_review import shaded
    from chain_detail_parts import oil_tools,formed_cotter
    lock=fingerprint();build=check_build(stage/'build')
    names=['chain_detail_probe.py','chain_detail_parts.py','chain_detail_controls.json','chain_detail_sources.json',
           'chain_candidate_controls.json','installed_pitch_route_report.json',
           'casing_support_build/report.json','casing_support_build/CasingSupportCandidate.FCStd']
    paths=[ROOT/n for n in names];hashes={n:sha(p) for n,p in zip(names,paths)}
    for n,p in zip(names,paths):
        if '/' not in n:
            target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
    for n,h in read(ROOT/'chain_detail_sources.json')['source_hashes'].items():assert sha(REPO/n)==h
    a={k:v['value'] for k,v in read(ROOT/'chain_candidate_controls.json')['controls'].items()}
    detail={k:v['value'] for k,v in read(ROOT/'chain_detail_controls.json')['controls'].items()}
    route=read(ROOT/'installed_pitch_route_report.json');prior=read(paths[-2])
    assert prior['passed'] and prior['rendering_complete'] and prior['native_sha256']==sha(paths[-1])
    assert prior['authored_fingerprint']==lock and prior['tank_native_hashes']==build['native_hashes']
    tank=App.openDocument(build['build']['top_document']);tank.recompute()
    replaced={'hull_engine_back','PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting',
              'hull_port_inner_rear_end','hull_port_rear_wing','hull_starboard_inner_rear_end','hull_starboard_rear_wing'}
    context=[i for i in leaves(tank.Root) if i['id'] not in replaced]
    doc=App.openDocument(str(paths[-1]));doc.recompute();before=leaves(doc.Root)
    old_shapes={key:next(i['target'].Shape.copy() for i in before if i['definition']==key) for key in ['inner_bar','outer_bar','cotter']}
    shape,formed=formed_cotter(old_shapes['cotter'],a,detail)
    next(i['target'] for i in before if i['definition']=='cotter').Tip.Shape=shape
    removal=[];tools=oil_tools(a,detail)
    for key in ['inner_bar','outer_bar']:
        target=next(i['target'] for i in before if i['definition']==key);old=old_shapes[key]
        updated=old.cut(Part.makeCompound(tools)).removeSplitter()
        added=updated.cut(old).Volume;removed=old.Volume-updated.Volume
        assert added<1e-5 and removed>0
        removal.append(dict(definition=key,added_material_mm3=added,removed_material_mm3=removed))
        target.Tip.Shape=updated
        metadata(target,ReconstructionNotes='Link-edge oil passage inferred from HB24/134; see chain_detail_controls.json')
    metadata(doc.Root,Scope='Isolated chain/casing candidate with formed cotter tails and link oil passages; source conflicts retained')
    doc.Definitions.Visibility=False;doc.recompute();native=out/'ChainDetailCandidate.FCStd';doc.saveAs(str(native))
    App.closeDocument(doc.Name);doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    assert len(items)==809
    for i in items:
        if not i['shape'].isValid() or len(i['shape'].Solids)!=1:raise ValueError('Invalid chain detail leaf '+i['id'])
    cotters=[i for i in items if i['definition']=='cotter'];bars=[i for i in items if i['definition'] in {'inner_bar','outer_bar'}]
    assert len(cotters)==100 and len(bars)==200
    byid={i['id']:i for i in items};physical=[i for i in context if i['representation']=='assembly']+items
    boxes=np.array([[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax] for b in [i['shape'].BoundBox for i in physical]])
    pairs=set();overlaps=[]
    # Bars only lose material. Cotter forming can introduce new intersections.
    for first in cotters:
        b=first['shape'].BoundBox;box=np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
        near=np.where(np.all(boxes[:,:3]<=box[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=box[:3]-1e-7,axis=1))[0]
        for n in near:
            second=physical[n];pair=tuple(sorted([first['id'],second['id']]))
            if pair[0]==pair[1] or pair in pairs:continue
            pairs.add(pair);volume=first['shape'].common(second['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=first['id'],b=second['id'],volume_mm3=volume))
    def transform(i):return i['shape'].Placement.multiply(i['target'].Shape.Placement.inverse())
    def placed(shape,pose):
        result=shape.copy();result.Placement=pose.multiply(result.Placement);return result
    captures=[];pin_retention=[]
    for i in cotters:
        stem=i['id'].removesuffix('Cotter');pin_item=byid[stem+'Pin'];pin=pin_item['shape']
        pose=transform(i);axis=pose.Rotation.multVec(App.Vector(0,0,1))
        shifted=i['shape'].copy();shifted.translate(axis*detail['cotter_pull_witness'])
        backward=i['shape'].copy();backward.translate(-axis*detail['cotter_pull_witness'])
        straight=placed(old_shapes['cotter'],pose);straight.translate(axis*detail['cotter_pull_witness'])
        tail_stop=shifted.common(pin).Volume;eye_stop=backward.common(pin).Volume;negative=straight.common(pin).Volume
        captures.append(dict(cotter=i['id'],tail_capture_volume_mm3=tail_stop,eye_capture_volume_mm3=eye_stop,
            unformed_negative_control_volume_mm3=negative,passed=tail_stop>1e-3 and eye_stop>1e-3 and negative<1e-5))
        hand=i['id'].split('Chain_')[0];n=int(i['id'].split('Joint')[1][:2]);outer=n if n%2 else (n-1)%50
        bar_ids=[hand+'Chain_Link%02d_'%outer+face for face in ['Inboard','Outboard']]
        axis_y=transform(pin_item).Rotation.multVec(App.Vector(0,1,0))
        volumes=[]
        for direction,receiver in [(1,bar_ids[0]),(-1,bar_ids[1])]:
            assembly=Part.makeCompound([pin,i['shape']]);assembly.translate(axis_y*(direction*detail['pin_pull_witness']))
            volumes.append(assembly.common(byid[receiver]['shape']).Volume)
        pin_retention.append(dict(pin=pin_item['id'],head_capture_volume_mm3=volumes[0],cotter_capture_volume_mm3=volumes[1],passed=min(volumes)>1e-3))
    gap=(a['pin_hole_diameter']-a['pin_diameter'])/2;r=a['pin_diameter']/2
    oil_checks=[];orientations=[];negative_oil=[]
    big,small=[np.array(route[k]) for k in ['roller_pinion_axis_xz_mm','candidate_transmission_axis_xz_mm']]
    vector=small-big
    for key in old_shapes:
        if key=='cotter':continue
        for tool in tools:
            volume=old_shapes[key].common(tool).Volume
            negative_oil.append(dict(definition=key,blocked_without_drilling_mm3=volume,passed=volume>1e-3))
    for i in bars:
        pose=transform(i);hand=i['id'].split('Chain_')[0];n=int(i['id'].split('Link')[1][:2])
        stock=a['inner_stock'] if i['definition']=='inner_bar' else a['outer_stock']
        mid=pose.multVec(App.Vector(a['pitch']/2,0,0));xz=np.array([mid.x,mid.z])
        closest=big+np.clip(np.dot(xz-big,vector)/np.dot(vector,vector),0,1)*vector
        normal=pose.Rotation.multVec(App.Vector(0,0,-1));outward=np.dot(xz-closest,[normal.x,normal.z])
        upper=big[0]<mid.x<small[0] and mid.z>big[1]+(mid.x-big[0])*vector[1]/vector[0]
        orientations.append(dict(bar=i['id'],outward_normal_dot_mm=float(outward),upper_run=bool(upper),
                                 hole_direction_world=[normal.x,normal.y,normal.z],passed=outward>0 and (not upper or normal.z>0)))
        for end,x in enumerate([0,a['pitch']]):
            # Stop inside the annular journal clearance, before the pin surface.
            length=a['bar_end_radius']+1-r-gap/2
            witness=Part.makeCylinder(detail['oil_hole_diameter']/2,length,App.Vector(x,0,-a['bar_end_radius']-1),App.Vector(0,0,1))
            margin=detail['oil_witness_margin']
            annulus=Part.makeCylinder(a['pin_hole_diameter']/2-margin,stock,App.Vector(x,-stock/2,0),App.Vector(0,1,0))
            annulus=annulus.cut(Part.makeCylinder(r+margin,stock+2,App.Vector(x,-stock/2-1,0),App.Vector(0,1,0)))
            connection=witness.common(annulus).Volume
            world=placed(witness,pose);pin=byid[hand+'Chain_Joint%02d_Pin'%((n+end)%50)]['shape']
            obstruction=i['shape'].common(world).Volume+pin.common(world).Volume
            oil_checks.append(dict(bar=i['id'],end=end,obstructing_material_mm3=obstruction,
                journal_connection_volume_mm3=connection,passed=obstruction<1e-5 and connection>1e-4))
    assert len(oil_checks)==400 and len(captures)==len(pin_retention)==100
    assert fingerprint()==lock;check_build(stage/'build')
    passed=not overlaps and all(r['passed'] for r in captures+pin_retention+oil_checks+orientations+negative_oil)
    report=dict(complete=True,passed=passed,fixture_occurrences=len(items),changed_cotters=100,drilled_bars=200,
        material_candidate_pairs=len(pairs),overlaps=overlaps,formed_cotter=formed,bar_material_removal=removal,
        cotter_capture_checks=captures,pin_retention_checks=pin_retention,oil_path_checks=oil_checks,
        oil_orientation_checks=orientations,undrilled_negative_controls=negative_oil,input_sha256=hashes,
        native_sha256=sha(native),authored_fingerprint=lock,tank_native_hashes=build['native_hashes'],
        standard_assembly_modified=False,source_inventory_reconciled=False,historical_fit_qualified=False,
        static_retention_geometry_qualified=passed,lubrication_performance_qualified=False,
        visual_review_status='pending',rendering_complete=False)
    write(out/'report.json',report)
    print('Chain details:',len(cotters),'formed cotters;',len(oil_checks),'oil paths;',len(overlaps),'overlaps; passed=',passed,flush=True)
    detail_items=[i for i in items if i['id'].startswith(('PortChain_Joint00_','PortChain_Link49_','PortChain_Link00_'))]
    shaded(detail_items,out/'chain_joint_detail.svg',(1,1,.85),'Chain joint | formed split-pin tails and inferred link-edge oil passages')
    datum=transform(byid['PortChain_Joint00_Pin']);cut=[]
    slab=Part.makeBox(1.5,160,90,App.Vector(-.75,-80,-40))
    for i in detail_items:
        shape=i['shape'].copy();shape.Placement=datum.inverse().multiply(shape.Placement)
        shape=shape.common(slab)
        if not shape.isNull():cut.append(dict(i,shape=shape,target=SimpleNamespace(Shape=shape),definition=i['id']+'_section'))
    shaded(cut,out/'chain_oil_section.svg',(1,0,.1),'Native pin-joint section | link-edge passages open into pin clearance')
    chain=[i for i in items if i['id'].startswith('PortChain_')]
    shaded(chain,out/'chain_oiling_elevation.svg',(0,1,0),'Installed chain | oil openings follow the outward edge; upper run faces upward')
    assert all(sha(p)==hashes[n] for n,p in zip(names,paths))
    report['rendering_complete']=True;write(out/'report.json',report)
    sys.exit(0 if passed else 1)
finally:
    runtime.close()
