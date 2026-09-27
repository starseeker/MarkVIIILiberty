"""Build an isolated, source-labelled bow/enclosure hypothesis; never promote it."""
import argparse
import copy
import json
from pathlib import Path
from control_rebuild_io_v2 import *
from lib.model import load, geometry_arguments, point
from lib.parameters import resolve
from lib.cad_build import frame
from lib import upper_parts, hull_parts
from bow_reconstruction_parts import bow_parts

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--controls', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
packet = read(a.controls)
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
data = load()
standard_path = ROOT/packet['standard_manifest']
standard = read(standard_path)
assert all(sha(ROOT/f)==digest for f,digest in standard['native_files'].items())
standard_rows = {r['name']:r for r in standard['occurrences']}
parent = Saved(ROOT/packet['development_parent'])
overall = data['parameters']['upper_length']['value']
driver = data['parameters']['driver_length']['value']
body = overall-driver
ratio = body/overall
data['parameters']['upper_length']['value'] = body
data['parameters']['upper_length']['bounds'] = [body, body]
station_changes = {}
for key, entry in data['parameters'].items():
    if key.startswith('upper_') and key.endswith('_station'):
        assert entry['basis']=='bounded_approximation', key
        station_changes[key] = dict(original_mm=entry['value'], candidate_mm=entry['value']*ratio)
        entry['value'] *= ratio
        entry['bounds'] = [n*ratio for n in entry['bounds']]
data['values'] = resolve(data['parameters'])
v = {k:e.value for k,e in data['values'].items()}
upper = frame('upper_base',data)
driver_base = frame('upper_driver_base',data)
narrow = v['track_centers']/2-v['hull_frame_clear']/2-v['hull_side_thickness']
wide = v['track_centers']/2+v['hull_frame_clear']/2
sections = {k:point(data,'snl_2',px) for k,px in packet['floor_source_picks_px'].items()}
sections['floor_end'] = [point(data,'snl_2',[680,0])[0],v['hull_ground_clearance']]
sections['bow_upper'] = [driver_base.Base.x+driver,upper.Base.z]
stocks = dict(narrow_half_width=narrow,wide_half_width=wide,
              floor_thickness=v['hull_floor_thickness'],wall_thickness=v['hull_side_thickness'],
              roof_thickness=v['hull_roof_thickness'],driver_inner_half_width=v['driver_width']/2-v['driver_wall'],
              main_front_x=driver_base.Base.x)
custom, joint = bow_parts(stocks, sections)
roles = {'inner_front_upper','inner_front_sponson','roof_front','roof_driver','roof_aft_upper','roof_track_rear','front_slope'}
selected = {k:d for k,d in data['definitions'].items() if d['builder'].startswith('upper_') or
            (d['builder']=='hull_plate' and (d['arguments']['role'] in roles or
             (d['arguments']['role']=='floor' and d['arguments']['index'] in [1,2])))}
occurrences = {r['id']:r for r in data['occurrences'] if r['definition'] in selected}
assert len(occurrences)==len(selected)
doc = App.newDocument('BowEnclosureHypothesis')
root = doc.addObject('App::Part','BowEnclosurePrototype')
library = doc.addObject('App::Part','Definitions')
groups = {}
definitions = {}; rows = {}; world = {}


def install(name, shape, placement, group_name, definition, evidence, notes, candidate=True):
    assert shape.isValid() and len(shape.Solids)==1 and shape.Solids[0].isClosed(), name
    assert shape.Placement.isIdentity(), name
    key = ('Candidate_' if candidate else 'Context_')+name
    body = doc.addObject('PartDesign::Body',key);library.addObject(body)
    body.newObject('PartDesign::Feature','ReconstructedStock').Shape=shape
    metadata(body,DefinitionId=definition,SourceRecords=evidence,ReconstructionNotes=notes,
             Coverage='partial_hypothesis' if candidate else 'retained_context',
             ParameterUpdate='Regenerate with build_bow_reconstruction.py and controls01.json; no live expressions.',
             GeometryQualified=False)
    if group_name not in groups:
        group=doc.addObject('App::Part',group_name);root.addObject(group);groups[group_name]=group
    link=doc.addObject('App::Link',name);groups[group_name].addObject(link);link.setLink(body)
    link.LinkPlacement=placement
    metadata(link,OccurrenceId=name,HistoricalGeometryQualified=False)
    definitions[key]=dict(source_definition=definition,shape_volume_mm3=shape.Volume)
    rows[name]=dict(definition=key,frame=list(placement.toMatrix().A),group=group_name,candidate=candidate)
    q=shape.copy();q.Placement=placement;world[name]=q


for name, occ in occurrences.items():
    definition = selected[occ['definition']]
    args = geometry_arguments(definition,data)
    role = args.get('role')
    if role=='front_slope':
        shape = custom['front_slope']
    elif role=='floor':
        shape = custom['floor_'+str(args['index'])]
    elif role=='roof_driver':
        shape = custom['roof_driver'][args['hand']]
    elif definition['builder'].startswith('upper_'):
        kind=definition['builder'].removeprefix('upper_')
        shape = upper_parts.prism(*upper_parts.stock(kind,args))
        for tool in upper_parts.cuts(kind,args):shape=shape.cut(tool)
        shape=shape.removeSplitter()
    else:
        # Reuse the original shell builder, including actual running-gear reliefs.
        temp=App.newDocument('PlateWork')
        body_obj=hull_parts.build(temp,'TemporaryPlate',args)
        shape=body_obj.Shape.copy();App.closeDocument(temp.Name)
    install(name,shape,frame(occ['frame'],data),
            'UpperEnclosure' if definition['builder'].startswith('upper_') else 'FrontAndRoofShell',
            occ['definition'],definition['evidence'],definition['notes']+'; '+packet['status'])
    print('built',name,flush=True)

for name in packet['standard_native_context']:
    r=standard_rows[name]; entry=standard['definitions'][r['definition']]
    assert sha(entry['brep_path'])==entry['brep_sha256']
    shape=Part.Shape();shape.read(entry['brep_path'])
    install(name,shape,pose(r['frame']),'RetainedStandardContext',r['definition'],[],
            'Unchanged saved standard context; source accuracy is not asserted.',False)
for name in packet['development_native_context']:
    r=parent.rows[name]
    install(name,parent.definition(r['definition']),pose(r['frame']),'RetainedDriverControls',
            r['definition'],[],'Unchanged qualified development material and placement.',False)
library.Visibility=False;doc.recompute()
native=out/'BowEnclosureHypothesis.FCStd';doc.saveAs(str(native))
# Export only proposed physical replacement plates, in their world placements.
exchange=App.newDocument('BowExchange')
objects=[]
for name,row in rows.items():
    if row['candidate']:
        obj=exchange.addObject('PartDesign::Feature',name);obj.Shape=world[name];objects.append(obj)
exchange.recompute();Part.export(objects,str(out/'BowEnclosureHypothesis.step'))
App.closeDocument(exchange.Name);App.closeDocument(doc.Name)
inputs = [a.controls,Path(__file__),H/'bow_reconstruction_parts.py',standard_path,
          parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json']
inputs += [H.parents[1]/'data'/f for f in ['parameters.json','calibrations.json','datums.json','definitions.json','occurrences.json','roller_stations.json','lower_support_runs.json']]
inputs += list((H.parents[1]/'lib').glob('*.py'))
inputs += [ROOT/f for f in packet['source_files']]
report = dict(native_file=native.name,native_sha256=sha(native),step_sha256=sha(out/'BowEnclosureHypothesis.step'),
              input_hashes={str(f.resolve().relative_to(ROOT)):sha(f) for f in inputs},
              standard_native_files=standard['native_files'],development_native=str(parent.native.relative_to(ROOT)),
              development_native_sha256=sha(parent.native),definitions=definitions,occurrences=rows,
              candidate_occurrence_count=sum(r['candidate'] for r in rows.values()),
              length_hypothesis=dict(printed_overall_mm=overall,printed_driver_mm=driver,main_body_mm=body,
                                     inclusive=True,main_center_unchanged=True,station_changes=station_changes),
              stocks=stocks,joint_datums=joint,source_camera_refitted=False,
              geometry_integrated=False,historical_geometry_qualified=False,installation_qualified=False,
              open_limits=packet['open_limits'])
write(out/'report.json',report)
print('Saved',report['candidate_occurrence_count'],'replacement occurrences;',len(rows),'total prototype occurrences',flush=True)
