"""Reproducible hierarchical oil-pump development document; incomplete assembly."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import sha,write,read

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--controls',type=Path,default=HERE/'engine_oil_pump_controls.json')
parser.add_argument('--worker',action='store_true')
a=parser.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);controls=a.controls.resolve()
if not a.worker:
    with (out/'build.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--output',str(out),'--controls',str(controls),'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)

try:
    import FreeCAD as App,Part
    from engine_oil_pump_assembly import parts
    V=App.Vector;source=read(HERE/'engine_oil_pump_sources.json');control_data=read(controls);c=control_data['controls'];audits=[]
    def audit(name,s):
        row=dict(definition=name,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,max_tolerance_mm=s.getTolerance(1));audits.append(row);write(out/'build_progress.json',audits);print(name,len(s.Faces),flush=True)
        assert row['valid'] and row['solids']==1 and row['volume_mm3']>0,name
    definitions,occurrences,groups,datums=parts(c,audit)
    # HB203 and its assembly instructions establish identities; the differing
    # separating-plate transcription is retained rather than silently repaired.
    hb_rows=dict(lower_body=2,body_plug=3,lower_bush=6,lower_driving_gear=7,lower_idler_gear=8,partition=9,long_pin=10,short_pin=11,upper_idler_gear=12,upper_driving_gear=13,upper_body=14,upper_plug=15,upper_bush=16,shaft=21,relief_seat=22,relief_cage=23,relief_spring=24,relief_valve=25,lower_filter_frame=28,lower_side_screen=29,lower_end_screen=30,cover=31,drain_plug=32,drain_gasket=33,cover_gasket=34,upper_filter_frame=40,upper_side_screen=41,upper_end_screen=42,screen_nut=43,screen_lock=44,dowel=45)
    hb_rows.update(upper_body_bolt=17,cover_body_bolt=35,fastener_washer=18,fastener_nut=19,fastener_cotter=20)
    indexed={r['record_id']:r for r in source['records']}
    doc=App.newDocument('OilPumpDevelopment');root=doc.addObject('App::Part','Root');root.Label='Mark VIII oil pump — development assembly'
    pump=doc.addObject('App::Part','EngineOilPump');root.addObject(pump)
    def prop(obj,name,value,kind='App::PropertyString'):
        obj.addProperty(kind,name,'Reconstruction');setattr(obj,name,value)
    prop(pump,'CompletionStatus','Incomplete: '+ '; '.join(datums['missing']))
    prop(pump,'FrameDescription','Local engine-aligned axes; crankcase mounting face Z=0. Proposed engine placement is recorded, not qualified or applied.')
    prop(pump,'ProposedEnginePlacementJSON',json.dumps(dict(x=c['pump_axis_x'],y=0,z=c['pump_mount_z'])))
    prop(pump,'ControlsJSON',json.dumps(control_data,sort_keys=True))
    prop(pump,'DatumsJSON',json.dumps(datums,sort_keys=True))
    containers={}
    for name in groups:
        container=doc.addObject('App::Part',name);pump.addObject(container);containers[name]=container
    library=doc.addObject('App::DocumentObjectGroup','Definitions');objects={};identities={}
    for key,shape in definitions.items():
        obj=doc.addObject('PartDesign::Body','Def_'+key);library.addObject(obj);feature=obj.newObject('PartDesign::Feature','ReconstructedOilPump');feature.Shape=shape
        rid=f'HB:nomenclature:203:{hb_rows[key]:03}' if key in hb_rows else 'SNL:160:005'
        row=indexed[rid];raw=json.loads(row['raw_json']);mark=raw.get('mark','LQ65A')
        refs=[rid]
        if key=='partition':refs.append('HB:printed86:separating plate 8188')
        prop(obj,'DefinitionKey',key);prop(obj,'SourceRecords',refs,'App::PropertyStringList');prop(obj,'SourcePartMark',mark)
        prop(obj,'RepresentationNote','Analytic and spline BRep reconstruction; unprinted dimensions estimated. Inputs require scripted regeneration.')
        if 'screen' in key and key not in ['screen_nut','screen_lock']:obj.RepresentationNote=datums['strainers']['representation']
        identities[key]=dict(source_records=refs,source_part_mark=mark);objects[key]=obj
    # A Body's aggregate Shape is populated by recompute; reading it directly
    # after assigning its feature yields a null shape on this runtime.
    doc.recompute()
    shapes=[]
    for row in occurrences:
        link=doc.addObject('App::Link',row['name']);containers[row['assembly']].addObject(link);link.setLink(objects[row['key']]);link.LinkPlacement=App.Placement(V(*row['xyz']),App.Rotation(*row['rotation']))
        prop(link,'DefinitionKey',row['key']);prop(link,'PhysicalRole','Installed oil-pump constituent')
        s=objects[row['key']].Shape.copy();s.Placement=link.LinkPlacement.multiply(s.Placement);shapes.append(s)
    doc.recompute();library.Visibility=False;native=out/'OilPump.FCStd';doc.saveAs(str(native))
    Part.setStaticValue('write.surfacecurve.mode',1)
    Part.makeCompound([objects[k].Shape for k in definitions]).exportStep(str(out/'OilPumpDefinitions.step'))
    Part.makeCompound(shapes).exportStep(str(out/'OilPumpAssembly.step'))
    inputs=[Path(__file__),HERE/'engine_oil_pump_assembly.py',HERE/'engine_oil_pump_parts.py',HERE/'engine_oil_pump_services.py',HERE/'engine_oil_pump_strainers.py',HERE/'engine_oil_pump_hardware.py',HERE/'engine_water_pump_parts.py',controls,HERE/'engine_oil_pump_sources.json',HERE/'engine_crossmember_parts.py',HERE/'transmission_planet_parts.py',HERE/'transmission_stud_parts.py',HERE/'transmission_core_parts.py']
    report=dict(status='Incomplete oil-pump development assembly',complete_pump=False,complete_engine=False,complete_tank=False,native_file=native.name,native_sha256=sha(native),physical_count=len(occurrences),definition_count=len(definitions),definition_order=list(definitions),identities=identities,occurrences=occurrences,groups=groups,controls=c,datums=datums,source_assets=source['source_assets'],input_hashes={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):sha(p) for p in inputs},audits=audits)
    write(out/'report.json',report);print(json.dumps(dict(native=str(native),physical_count=len(occurrences),definitions=len(definitions))),flush=True)
finally:
    runtime.close()
