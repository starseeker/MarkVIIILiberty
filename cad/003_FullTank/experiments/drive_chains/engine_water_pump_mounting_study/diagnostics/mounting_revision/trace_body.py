from pathlib import Path
import sys,json,ast,textwrap,os
os.environ.setdefault('MARKVIII_RESOLVED_FREECAD',str(Path('/snap/freecad/current').resolve()))
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'cad/001_Survey/mark_viii_parts.sqlite').is_file());h=ROOT/'cad/003_FullTank/experiments/drive_chains';sys.path[:0]=[str(h),str(h.parents[1])]
import FreeCAD as App
import Part
from deep_drain_parts import *
r=json.loads((h/'engine_water_pump_study/report.json').read_text());c=json.loads(Path(__file__).with_name('deep_drain_controls.json').read_text())['controls'];d=r['datums'];mount_x=d['mount_x'];shaft_r=d['shaft_radius'];packing_outer=d['packing_outer_radius'];sleeve_outer=c['body_shaft_sleeve_radius'];spring1=d['spring_span'][1];gf=c['gland_flange_stock'];pack2,pack3=d['packing_spans'][1]
out=Path.cwd();records=[];last=0.;counter=0

def record(label,s):
 global last,counter
 counter+=1;tol=s.getTolerance(1);entry=dict(stage=counter,label=label,valid=s.isValid(),solids=len(s.Solids),max_tolerance_mm=tol)
 if tol>max(last,1e-5)*1.01:
  filename='stage_%02d.brep'%counter;s.exportBrep(str(out/filename));entry['shape']=filename
 records.append(entry);(out/'stages.json').write_text(json.dumps(records,indent=2)+'\n');last=tol
 print(entry,flush=True)

source=Path(__file__).with_name('deep_drain_parts.py').read_text()
start=source.index('    def gland_slots(');end=source.index("    p['retainer']=",start)
exec(compile(textwrap.dedent(source[start:end]),'<gland_slots>','exec'))
start=source.index("    rear=c['body_back']");end=source.index("    p['body']=body",start)
block=textwrap.dedent(source[start:end]);tree=ast.parse(block)
class Trace(ast.NodeTransformer):
 def visit_Assign(self,node):
  if any(isinstance(t,ast.Name) and t.id=='body' for t in node.targets):
   label=ast.get_source_segment(block,node)
   return [node,ast.Expr(value=ast.Call(func=ast.Name(id='record',ctx=ast.Load()),args=[ast.Constant(value=label),ast.Name(id='body',ctx=ast.Load())],keywords=[]))]
  return node
exec(compile(ast.fix_missing_locations(Trace().visit(tree)),'<body_stages>','exec'))
record('raw_final',body);body.exportBrep(str(out/'raw_final.brep'));selected=clean(body);record('selected_cleanup',selected);selected.exportBrep(str(out/'selected.brep'))
edges=[]
for i,e in enumerate(selected.Edges):
 t=e.getTolerance(1)
 if t>1e-5:
  box_=e.BoundBox;edges.append(dict(index=i,tolerance=t,bounds=[getattr(box_,k) for k in ['XMin','XMax','YMin','YMax','ZMin','ZMax']]))
(out/'high_tolerance_edges.json').write_text(json.dumps(edges,indent=2)+'\n')
