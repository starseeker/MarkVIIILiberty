"""Reproduce the old obstruction and measure the proposed local body correction."""
from pathlib import Path
import hashlib,json,sys,textwrap
import FreeCAD as App
import Part
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'cad/001_Survey/mark_viii_parts.sqlite').is_file())
HERE=ROOT/'cad/003_FullTank/experiments/drive_chains';sys.path.insert(0,str(HERE))
import engine_water_pump_parts as helpers
source=(HERE/'engine_water_pump_parts.py').read_text()
out=Path.cwd();results=[]
for label,base in [('nominal',HERE/'engine_water_pump_mounting_study'),('trial',ROOT/'.work/engine-water-pump-mounting/variant')]:
    r=json.loads((base/'report.json').read_text());c=r['controls'];d=r['datums'];native=base/r['native_file']
    assert hashlib.sha256(native.read_bytes()).hexdigest()==r['native_sha256']
    env=dict(vars(helpers),c=c,mount_x=d['mount_x'],shaft_r=d['shaft_radius'],packing_outer=d['packing_outer_radius'],
        sleeve_outer=c['body_shaft_sleeve_radius'],spring1=d['spring_span'][1],gf=c['gland_flange_stock'],
        pack2=d['packing_spans'][1][0],pack3=d['packing_spans'][1][1])
    start=source.index('    def gland_slots(');end=source.index("    p['retainer']=",start)
    exec(textwrap.dedent(source[start:end]),env)
    start=source.index("    rear=c['body_back']");end=source.index("    p['body']=body",start)
    exec(textwrap.dedent(source[start:end]),env)
    new=helpers.clean(env['body']);new.exportBrep(str(out/(label+'_corrected_body.brep')))
    doc=App.openDocument(str(native));old=doc.getObject(r['definitions']['body']).Shape.copy();App.closeDocument(doc.Name)
    stock=env['drain_stock'];fluid=env['cavity'].common(stock)
    removed=old.cut(new);added=new.cut(old)
    def outside(shape,region):return 0. if not shape.Solids else abs(shape.cut(region).Volume)
    gauges=[]
    for sign in [-1,1]:
        rotation=App.Rotation(helpers.X,c['outlet_clock_deg'])
        start=App.Vector(c['scroll_center_x'],0,0)+rotation.multVec(App.Vector(0,sign*c['outlet_start_y'],sign*c['outlet_offset_z']))
        gauge=Part.makeCylinder(5,c['outlet_tip_y']-c['outlet_start_y'],start,rotation.multVec(helpers.Y*sign))
        gauges.append(dict(sign=sign,old_overlap_mm3=abs(old.common(gauge).Volume),new_overlap_mm3=abs(new.common(gauge).Volume)))
    result=dict(label=label,parent_native_sha256=r['native_sha256'],valid=new.isValid(),solids=len(new.Solids),max_tolerance_mm=new.getTolerance(1),
        old_fluid_intrusion_mm3=abs(old.common(fluid).Volume),new_fluid_intrusion_mm3=abs(new.common(fluid).Volume),
        removed_mm3=abs(removed.Volume),added_mm3=abs(added.Volume),removed_outside_drain_fluid_mm3=outside(removed,fluid),gauges=gauges)
    result['passed']=(result['valid'] and result['solids']==1 and result['max_tolerance_mm']<=1e-4 and
        result['old_fluid_intrusion_mm3']>1 and result['new_fluid_intrusion_mm3']<1e-5 and result['added_mm3']<1e-5 and
        result['removed_outside_drain_fluid_mm3']<1e-5 and all(g['new_overlap_mm3']<1e-5 for g in gauges))
    results.append(result);print(json.dumps(result),flush=True)
    (out/'probe_checks.json').write_text(json.dumps(dict(passed=all(x['passed'] for x in results),cases=results),indent=2)+'\n')
assert all(x['passed'] for x in results)
assert results[1]['gauges'][0]['old_overlap_mm3']>1e-5,'Original failed trial must remain a negative control'
