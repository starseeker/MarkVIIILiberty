"""Mount M779 on the real retained support web with two full source bolt assemblies."""
import argparse,copy,sys
from control_rebuild_io_v2 import *
from driver_reverse_quadrant_parts import quadrant,hardware
V=App.Vector;Y=V(0,1,0);Z=V(0,0,1)
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--stock-offset',type=float,default=0);a=p.parse_args();c=copy.deepcopy(read(a.controls));c['quadrant_stock_mm']+=a.stock_offset
parent=Saved(ROOT/c['parent']);seed=Saved(ROOT/c['reverse_seed']);source=ROOT/c['source_review']
assert sha(parent.native)==c['parent_native_sha256'] and sha(seed.native)==c['reverse_seed_sha256'] and sha(source)==c['source_review_sha256']
assert all(sha(ROOT/f)==v for f,v in read(source)['source_hashes'].items())
regfile=ROOT/c['side_registration'];reg=read(regfile)['side_registration'];coef=complex(*reg['complex_scale']);center=complex(*reg['main_shaft_px'])
main=V(*parent.report['details']['main_world_mm'])
def from_pixel(p):
    v=(complex(*p)-center)/(-coef);return V(v.real,0,v.imag)
holes=[from_pixel(v) for v in c['mount_construction_pixels']]
shapes={k:seed.definition(k) for k in seed.manifest['definitions']};specs={n:copy.deepcopy(seed.report['specs'][n]) for n in seed.rows};props={}
def metadata_from(src,keys):
    doc=App.openDocument(str(src.native))
    try:
        for key in keys:
            obj=doc.getObject(key);props[key]={k:getattr(obj,k) for k in obj.PropertiesList if obj.getGroupOfProperty(k)=='Reconstruction'}
    finally:App.closeDocument(doc.Name)
metadata_from(seed,shapes)
plate_name='DriverStarboardSupportPlate';pr=parent.rows[plate_name];plate_key=pr['definition'];plate=parent.definition(plate_key);metadata_from(parent,[plate_key]);f=pose(pr['frame'])
for point in holes:
    world=main+point;local=f.inverse().multVec(world);local.y=-c['support_inner_y_abs_mm']+1
    plate=plate.cut(Part.makeCylinder(c['bolt_bore_radius_mm'],c['support_stock_mm']+2,local,-Y))
shapes[plate_key]=plate.removeSplitter();props[plate_key]['ReconstructionStatus']+=' Two quadrant attachment bores added at documented estimated stations; all other material and source metadata retained.'
props[plate_key]['ParameterUpdate']='Regenerate build_driver_reverse_quadrant.py from recorded controls; no live expressions.'
specs[plate_name]=dict(definition=plate_key,frame=pr['frame'],owner='Receivers',role='receiver')
qkey='Def_DriverReverseQuadrant_M779';shapes[qkey]=quadrant(c,holes)
qcenter=c['quadrant_inner_y_mm']-c['quadrant_stock_mm']/2
spacer_length=c['support_inner_y_abs_mm']+c['quadrant_inner_y_mm']-c['quadrant_stock_mm'];assert spacer_length>0
props[qkey]=dict(SourcePartMark='M779',SourceRecords=['SNL:161:007','SNL:072:012','HB:plate94','HB:plate113','SNL:plate6'],Representation='reconstruction_trial',ReconstructionStatus='Concentric annular quadrant with two mounting ears and three estimated detents. Profile, stock, notch geometry and mounting stations inferred; linkage states and complete latch remain unqualified.',ParameterUpdate='Regenerate build_driver_reverse_quadrant.py; no live expressions.')
specs['DriverReverseQuadrant']=dict(definition=qkey,frame=list(App.Placement(main+Y*qcenter,App.Rotation()).toMatrix().A),owner='DriverReverseQuadrantMounts',role='quadrant')
keys={role:'Def_DriverReverseQuadrant'+role for role in ['Bolt','Nut','Lock','Distance']}
for role,q in hardware(c,spacer_length).items():
    key=keys[role];shapes[key]=q;props[key]=dict(SourcePartMark='M781' if role=='Distance' else '3/8in USS '+role,SourceRecords=['SNL:133:039','SNL:072:014'] if role=='Distance' else ['SNL:030:010'],Representation='reconstruction_trial',ReconstructionStatus=('Two shared distance pieces. Gap derived from actual quadrant/support faces; OD and bore estimated.' if role=='Distance' else 'Complete source3/8x2-1/4in bolt/nut/lock assembly. Under-head bolt length interpreted; nominal threads, USS exterior and compressed split washer estimated.'),ParameterUpdate='Regenerate build_driver_reverse_quadrant.py; no live expressions.')
joints=[];rot=App.Rotation(Z,-Y)
for i,point in enumerate(holes):
    stem='DriverReverseQuadrant'+['Forward','Rear'][i];world=main+point
    ys=dict(Bolt=c['quadrant_inner_y_mm'],Distance=c['quadrant_inner_y_mm']-c['quadrant_stock_mm'],Lock=-c['support_inner_y_abs_mm']-c['support_stock_mm'],Nut=-c['support_inner_y_abs_mm']-c['support_stock_mm']-c['lock_stock_mm'])
    for role,y in ys.items():
        place=App.Placement(V(world.x,y,world.z),rot);specs[stem+role]=dict(definition=keys[role],frame=list(place.toMatrix().A),owner='DriverReverseQuadrantMounts',role=role.lower())
    joints.append(dict(stem=stem,axis_world=[0,-1,0],center_xz_world_mm=[world.x,world.z],seating_y_mm=ys,spacer_length_mm=spacer_length))
details=dict(controls=c,stock_offset_mm=a.stock_offset,main_world_mm=list(main),mount_local_xz_mm=[list(p) for p in holes],joints=joints,reverse_seed=str(seed.folder.relative_to(ROOT)),reverse_seed_native_sha256=sha(seed.native),reverse_seed_details=seed.report['details'],retained_development_native=str(parent.native.relative_to(ROOT)),retained_development_native_sha256=sha(parent.native),source_camera_refitted=False,mechanism_complete=False,scope='Reverse body and short connection retained, nine quadrant/mount additions and two real support bores. Trigger, pawl and full reverse system remain unfinished.')
inputs=[Path(__file__),a.controls,source,regfile,seed.folder/'report.json',seed.folder/'isolated/manifest.json',seed.folder.parent/'reverse_short_study_receipt.json',parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json',*[ROOT/f for f in read(source)['source_hashes']]]
inputs+=sorted({Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().parent==H and str(m.__file__).endswith('.py')})
trial(a.output,parent,shapes,specs,props,details,inputs,changed_definitions=[plate_key]);print('Quadrant mounted; full source bolt stock, distance length',spacer_length,'checks pending.',flush=True)
