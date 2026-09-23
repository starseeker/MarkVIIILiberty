"""Replay the local correction using frozen inputs and retained failing bodies."""
from pathlib import Path
import json,sys,textwrap
import FreeCAD as App
import Part
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'cad/001_Survey/mark_viii_parts.sqlite').is_file())
HERE=ROOT/'cad/003_FullTank/experiments/drive_chains'
base=HERE/'engine_water_pump_passage_study';diagnostic=base/'diagnostics/passage'
sys.path[:0]=[str(base/'inputs'),str(HERE)]
import engine_water_pump_parts as helpers
source=(base/'inputs/engine_water_pump_parts.py').read_text();results=[]
for label in ['nominal','trial']:
    r=json.loads((diagnostic/(label+'_previous_report.json')).read_text());c=r['controls'];d=r['datums']
    env=dict(vars(helpers),c=c,mount_x=d['mount_x'],shaft_r=d['shaft_radius'],packing_outer=d['packing_outer_radius'],
        sleeve_outer=c['body_shaft_sleeve_radius'],spring1=d['spring_span'][1],gf=c['gland_flange_stock'],
        pack2=d['packing_spans'][1][0],pack3=d['packing_spans'][1][1])
    start=source.index('    def gland_slots(');end=source.index("    p['retainer']=",start)
    exec(textwrap.dedent(source[start:end]),env)
    start=source.index("    rear=c['body_back']");end=source.index("    p['body']=body",start)
    exec(textwrap.dedent(source[start:end]),env);new=helpers.clean(env['body'])
    old=Part.Shape();old.read(str(diagnostic/(label+'_previous_body.brep')))
    retained=Part.Shape();retained.read(str(diagnostic/(label+'_corrected_body.brep')))
    fluid=env['cavity'].common(env['drain_stock']);removed=old.cut(new)
    details=dict(old_fluid_intrusion_mm3=abs(old.common(fluid).Volume),new_fluid_intrusion_mm3=abs(new.common(fluid).Volume),
        added_mm3=abs(new.cut(old).Volume),removed_outside_drain_fluid_mm3=0. if not removed.Solids else abs(removed.cut(fluid).Volume),
        replay_missing_mm3=abs(retained.cut(new).Volume),replay_added_mm3=abs(new.cut(retained).Volume),max_tolerance_mm=new.getTolerance(1))
    passed=(old.isValid() and retained.isValid() and new.isValid() and len(new.Solids)==1 and details['old_fluid_intrusion_mm3']>1 and
        details['max_tolerance_mm']<=1e-4 and all(details[k]<1e-5 for k in ['new_fluid_intrusion_mm3','added_mm3','removed_outside_drain_fluid_mm3','replay_missing_mm3','replay_added_mm3']))
    results.append(dict(label=label,passed=passed,**details));print(json.dumps(results[-1]),flush=True)
result=dict(passed=all(x['passed'] for x in results),cases=results)
(Path.cwd()/'replay_checks.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed']
