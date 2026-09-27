"""Save the identifiable bowed M769 profile as an unintegrated local prototype."""
import argparse,copy
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_foot_link_parts import make
p=argparse.ArgumentParser();p.add_argument('--controls',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--stock-offset',type=float,default=0);a=p.parse_args()
c=read(a.controls);c=copy.deepcopy(c);c['web_stock_mm']+=a.stock_offset
parent=Saved(ROOT/c['parent']);assert sha(parent.native)==c['parent_native_sha256'];assert read(parent.folder/'qualification.json')['local_static_checks_passed']
assert all(sha(ROOT/f)==h for f,h in c['source_hashes'].items())
shape,curves,details=make(c);key='Def_DriverFootLink_M769';main=App.Vector(*parent.report['details']['main_world_mm']);center=complex(*c['side_main_px']);scale=complex(*c['side_complex_scale']);delta=-(complex(*c['front_eyes_px'][0])-center)/scale
origin=main+App.Vector(delta.real,0,delta.imag)
props={key:dict(SourcePartMark='M769',SourceRecords=['SNL:071:027','SNL:119:027','HB:plate113','SNL:plate06'],Representation='reconstruction_trial',WebStockMM=str(c['web_stock_mm']),ReconstructionStatus='Source-profile hypothesis: two triangular-head eyes and bowed lower web. Rear nominal19.05mm rod socket, recorded web stock and transverse70mm lanes are inferred. M771/bridle topology, SH946F opposite end and complete M576 closure are unresolved; not integrated.',ParameterUpdate=f'Regenerate {Path(__file__).name} from the recorded source pixels and stock offset; no live expressions.')}
specs={};guides={}
for side,sign in [('Port',1),('Starboard',-1)]:
    frame=App.Placement(origin+App.Vector(0,sign*c['lane_mm'],0),App.Rotation())
    name=side+'DriverFootLink';specs[name]=dict(definition=key,frame=list(frame.toMatrix().A),owner='DriverFootProfileHypothesis',role='foot_link')
    for kind,e in curves.items():g=e.copy();g.Placement=frame;guides[name+kind]=g
# Existing interfaces remain exact saved parent shapes; they are not new inventory.
receivers=['DriverMainShaft','DriverSwingShaft','PortDriverOperatingFulcrum','StarboardDriverOperatingFulcrum','PortFootIntermediateRocker','StarboardFootIntermediateRocker']
shapes={key:shape};doc=App.openDocument(str(parent.native))
try:
 for name in receivers:
    row=parent.rows[name];k=row['definition'];shapes[k]=parent.definition(k)
    obj=doc.getObject(k);props[k]={v:getattr(obj,v) for v in obj.PropertiesList if obj.getGroupOfProperty(v)=='Reconstruction'}
    specs[name]=dict(definition=k,frame=row['frame'],owner='Receivers',role='receiver')
finally:App.closeDocument(doc.Name)
details.update(controls=c,stock_offset_mm=a.stock_offset,origin_world_mm=list(origin),retained_development_native=str(parent.native.relative_to(ROOT)),retained_development_native_sha256=sha(parent.native),source_camera_refitted=False,scope='Two identical M769 complete-solid profile hypotheses plus exact retained receiver context; not a complete foot mechanism.',open_interfaces=['M771 joint graph, upper anchors and interpretation of the two visible front eyes require topology reconciliation.','Socket-to-M576 stock/SH946F route not closed.','M765/M770/M795 central four-bar and pedal mounting remain unresolved.'])
trial(a.output,parent,shapes,specs,props,details,[Path(__file__),a.controls,H/'driver_foot_link_parts.py',H/'control_rebuild_io_v2.py',parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json',*[ROOT/f for f in c['source_hashes']]],curves=guides)
print('Saved two M769 profile hypotheses and six exact receiver occurrences; not integrated.',flush=True)
