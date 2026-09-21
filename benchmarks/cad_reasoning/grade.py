"""Fixed independent source witnesses and FreeCAD material/interface checks."""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'cad/003_FullTank'))
from lib import runtime

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class Checks:
    def __init__(self): self.rows = []
    def add(self, name, ok, detail=None):
        self.rows.append(dict(name=name, passed=bool(ok), detail=detail))
    def result(self):
        return dict(passed=bool(self.rows) and all(r['passed'] for r in self.rows),
                    passed_checks=sum(r['passed'] for r in self.rows), total_checks=len(self.rows), checks=self.rows)

def source(answer):
    c = Checks()
    for name,expected in [('callout_28_mark','SH998B'),('callout_30_mark','SH861E'),
                          ('bearing_end_mark','SH998B'),('separate_components',True),
                          ('ring_location','external'),('exact_ring_diameter_mm',None),
                          ('historical_fit_proven',False)]:
        c.add(name, name in answer and answer[name] == expected, answer.get(name))
    for name,center in [('endpoint_28',(383,674)),('endpoint_30',(427,718))]:
        point = answer.get(name,[])
        distance = math.dist(point,center) if len(point)==2 else 1e9
        c.add(name, distance <= 35, dict(point=point, distance_pixels=distance, allowed_pixels=35))
    return c.result()

def compile_candidate(code, entry, App, Part):
    tree = ast.parse(code)
    banned = (ast.Import,ast.ImportFrom,ast.With,ast.AsyncWith,ast.ClassDef,ast.Global,ast.Nonlocal)
    for node in ast.walk(tree):
        if isinstance(node,banned): raise ValueError('Disallowed candidate syntax: '+type(node).__name__)
        if isinstance(node,ast.Attribute) and node.attr.startswith('__'): raise ValueError('Dunder access prohibited')
        if isinstance(node,ast.Name) and node.id.startswith('__'): raise ValueError('Dunder name prohibited')
    for node in tree.body:
        if not isinstance(node,(ast.FunctionDef,ast.Assign,ast.AnnAssign,ast.Expr)):
            raise ValueError('Unexpected top-level statement')
    # Functions can construct CAD only; host controls file IO and saved artifacts.
    builtins = {k:v for k,v in vars(__import__('builtins')).items() if k in
        ['range','len','min','max','abs','sum','float','int','bool','enumerate','zip','list','dict','tuple','set',
         'round','sorted','isinstance','ValueError','RuntimeError','Exception']}
    namespace = {'__builtins__':builtins,'App':App,'Part':Part,'math':math}
    exec(compile(tree,'<candidate>','exec'),namespace)
    return namespace[entry]

def construction(answer, out, save=True):
    import FreeCAD as App
    import Part
    c = Checks()
    p0 = json.loads((HERE/'fixtures/parameters.json').read_text())['construction']
    fn = compile_candidate(answer['python_code'],'build',App,Part)
    for scenario,delta,translation,axis,angle in [
        ('nominal',0,(112,-37,84),(1,2,3),27),
        ('smaller',-.7,(-52,190,-16),(2,-1,1),-63),
        ('larger',.9,(700,-330,121),(0,1,0),91)]:
        p = dict(p0)
        for k in ['outer_radius','rear_bore','front_bore','relief_radius','sleeve_radius','sleeve_bore','groove_root']:
            p[k] += delta
        for k in ['x0','shoulder','bearing_end','relief_start','relief_end']: p[k] += delta*3
        p['sleeve_length'] += delta*2
        frame = App.Placement(App.Vector(*translation),App.Rotation(App.Vector(*axis),angle))
        shapes = fn(dict(p),frame)
        c.add(scenario+'/separate definitions',set(shapes)=={'bearing','sleeve'})
        for k,s in shapes.items():
            c.add(scenario+'/'+k+'/one valid solid',s.isValid() and len(s.Solids)==1)
        bearing,sleeve = shapes['bearing'],shapes['sleeve']
        c.add(scenario+'/no material overlap',abs(bearing.common(sleeve).Volume)<1e-5)
        # Analytic material witnesses in local coordinates, transformed independently.
        count=0; errors=[]
        for x,radius in [((p['shoulder']+p['relief_start'])/2,p['rear_bore']),
                         ((p['relief_start']+p['relief_end'])/2,p['relief_radius']),
                         ((p['relief_end']+p['bearing_end'])/2,p['front_bore'])]:
            for r,inside in [(radius-.05,False),(radius+.05,True),(p['outer_radius']-.05,True),(p['outer_radius']+.05,False)]:
                for angle2 in [0,43,97,181,278]:
                    t=math.radians(angle2); point=frame.multVec(App.Vector(x,r*math.cos(t),r*math.sin(t)))
                    count+=1
                    if bearing.isInside(point,1e-6,False)!=inside:errors.append([x,r,angle2,inside])
        c.add(scenario+'/stepped bearing and world transform',not errors,dict(witnesses=count,errors=errors[:12]))
        xs=[(p['x0']+p['shoulder'])/2,p['shoulder']+.5,p['x0']+p['sleeve_length']-.5]
        errors=[];count=0
        for x in xs:
            outer=p['outer_radius'] if x<p['shoulder'] else p['sleeve_radius']
            for k in range(p['groove_count']):
                theta=2*math.pi*k/p['groove_count']
                # Within rectangular groove, beyond its square end, beside each
                # tangential wall, and inside the circular bore / outside OD.
                radial=(p['sleeve_bore']+p['groove_root'])/2
                for u,v,inside in [(radial,0,False),(p['groove_root']+.08,0,True),
                    (radial,p['groove_width']/2-.08,False),(radial,p['groove_width']/2+.08,True),
                    (p['sleeve_bore']-.08,0,False),(outer+.08,0,False)]:
                    y=u*math.cos(theta)-v*math.sin(theta);z=u*math.sin(theta)+v*math.cos(theta)
                    point=frame.multVec(App.Vector(x,y,z));count+=1
                    if sleeve.isInside(point,1e-6,False)!=inside:errors.append([x,k,u,v,inside])
        c.add(scenario+'/24 grooves and lands',not errors,dict(witnesses=count,errors=errors[:12]))
        for name,s,low,high,r in [('bearing',bearing,p['shoulder'],p['bearing_end'],p['outer_radius']),
                                ('sleeve',sleeve,p['x0'],p['x0']+p['sleeve_length'],p['outer_radius'])]:
            local=s.copy();local.transformShape(frame.inverse().toMatrix())
            bb=local.BoundBox
            errors2=[abs(bb.XMin-low),abs(bb.XMax-high),abs(bb.YMin+r),abs(bb.YMax-r),abs(bb.ZMin+r),abs(bb.ZMax-r)]
            c.add(scenario+'/'+name+'/extents',max(errors2)<1e-5,errors2)
        # At the overlapping rear band there is .15 mm radial clearance.
        x=(p['shoulder']+min(p['relief_start'],p['x0']+p['sleeve_length']))/2
        gap_point=frame.multVec(App.Vector(x,(p['rear_bore']+p['sleeve_radius'])/2,0))
        c.add(scenario+'/nested radial clearance',not bearing.isInside(gap_point,1e-6,False) and not sleeve.isInside(gap_point,1e-6,False))
        if save: save_exchange(shapes,out/scenario,c,scenario,App,Part)
    return c.result()

def repair(answer,out,save=True):
    import FreeCAD as App
    import Part
    c=Checks()
    p0=json.loads((HERE/'fixtures/parameters.json').read_text())['repair']
    fn=compile_candidate(answer['python_code'],'rebuild',App,Part)
    def cyl(r,a,b):return Part.makeCylinder(r,b-a,App.Vector(a,0,0),App.Vector(1,0,0))
    for delta in [-2,-1,0,1,2]:
        name=f'delta_{delta:+d}';p=dict(p0);p['body_radius']+=delta;p['main_bore']+=delta
        parent=Part.Shape();parent.read(str(HERE/'fixtures/parent_collar.brep'))
        before=parent.copy();s=fn(parent,dict(p))
        c.add(name+'/valid single solid',s.isValid() and len(s.Solids)==1)
        c.add(name+'/parent unchanged',abs(before.cut(parent).Volume)+abs(parent.cut(before).Volume)<1e-6)
        mask=cyl(p['lip_radius']+1,p['joint_face']-1,p['lip_end'])
        old=before.common(mask);new=s.common(mask)
        difference=abs(old.cut(new).Volume)+abs(new.cut(old).Volume)
        c.add(name+'/entire rear lip preserved',difference<1e-5,difference)
        # Analytic body envelope checks both added and absent material.
        body=cyl(p['body_radius'],p['lip_end'],p['front'])
        body=body.cut(cyl(p['rear_bore'],p['lip_end']-1,p['bore_step']))
        body=body.cut(cyl(p['main_bore'],p['bore_step'],p['front']+1))
        actual=s.common(cyl(p['lip_radius']+1,p['lip_end'],p['front']))
        extra=abs(actual.cut(body).Volume);missing=abs(body.cut(actual).Volume)
        c.add(name+'/requested body only',extra<1e-5 and missing<1e-5,dict(extra=extra,missing=missing))
        lip=cyl(p['body_radius']+8,991.95,p['front']).cut(cyl(p['body_radius']+.15,990.95,p['front']+1))
        overlap=abs(s.common(lip).Volume)
        c.add(name+'/thrust lip clearance',overlap<1e-5,overlap)
        for k in range(6):
            t=math.radians(k*60);r=100;x=(p['joint_face']+p['lip_end'])/2
            c.add(name+f'/hole{k}',not s.isInside(App.Vector(x,r*math.cos(t),r*math.sin(t)),1e-6,False))
        if save:save_exchange({'collar':s},out/name,c,name,App,Part)
    return c.result()

def save_exchange(shapes,out,c,prefix,App,Part):
    out.mkdir(parents=True,exist_ok=True)
    doc=App.newDocument('Benchmark')
    try:
        objs=[]
        for name,s in shapes.items():
            obj=doc.addObject('PartDesign::Feature',name);obj.Shape=s;objs.append(obj)
            path=out/(name+'.step');s.exportStep(str(path))
            loaded=Part.Shape();loaded.read(str(path))
            scale=max(abs(s.Volume),1)
            relative=abs(loaded.Volume-s.Volume)/scale
            centroid=(loaded.Solids[0].CenterOfMass-s.Solids[0].CenterOfMass).Length
            c.add(prefix+'/'+name+'/STEP round trip',loaded.isValid() and len(loaded.Solids)==1 and relative<1e-6 and centroid<1e-5,
                  dict(relative_volume=relative,centroid_mm=centroid))
        doc.recompute();doc.saveAs(str(out/'candidate.FCStd'))
    finally:App.closeDocument(doc.Name)

def evaluate(case,answer,out,save=True):
    try:
        result={'source':source,'construction':lambda a:construction(a,out,save),'repair':lambda a:repair(a,out,save)}[case](answer)
    except Exception as e:
        result=dict(passed=False,passed_checks=0,total_checks=1,checks=[dict(name='execution',passed=False,detail=str(e))],traceback=traceback.format_exc())
    result['grader_sha256']=sha(Path(__file__))
    return result

def self_test(out):
    import reference
    tests={}
    for case,code in [('construction',reference.CONSTRUCTION),('repair',reference.REPAIR)]:
        tests[case+'_reference']=evaluate(case,{'python_code':code},out/case,True)
        assert tests[case+'_reference']['passed'],tests[case+'_reference']
    mutants=[('repair_legacy','repair',reference.LEGACY_REPAIR),
             ('construction_no_frame','construction',reference.CONSTRUCTION.replace('frame.multiply(shape.Placement)','shape.Placement')),
             ('construction_missing_groove','construction',reference.CONSTRUCTION.replace("range(p['groove_count'])","range(p['groove_count']-1)"))]
    for name,case,code in mutants:
        tests[name]=evaluate(case,{'python_code':code},out/name,False)
        assert not tests[name]['passed'],name
    good=dict(callout_28_mark='SH998B',callout_30_mark='SH861E',bearing_end_mark='SH998B',separate_components=True,
              ring_location='external',endpoint_28=[383,674],endpoint_30=[427,718],exact_ring_diameter_mm=None,historical_fit_proven=False)
    tests['source_reference']=source(good);assert tests['source_reference']['passed']
    wrong=dict(good,ring_location='internal',bearing_end_mark='SH861E',exact_ring_diameter_mm=152,historical_fit_proven=True)
    tests['source_bad_mapping']=source(wrong);assert not tests['source_bad_mapping']['passed']
    (out/'self_test.json').write_text(json.dumps(dict(passed=True,tests=tests,grader_sha256=sha(Path(__file__))),indent=2)+'\n')
    print('PASS: references pass and four deliberately faulty answers fail.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--worker',action='store_true')
    p.add_argument('--case',choices=['source','construction','repair']);p.add_argument('--answer',type=Path);p.add_argument('--output',type=Path)
    args=p.parse_args();out=args.output or HERE/'results/self_test';out.mkdir(parents=True,exist_ok=True)
    if not args.worker:
        with (out/'grader.log').open('w') as log:
            return subprocess.run([sys.executable,__file__,*sys.argv[1:],'--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode
    if args.self_test:self_test(out)
    else:
        result=evaluate(args.case,json.loads(args.answer.read_text()),out)
        result['answer_sha256']=sha(args.answer)
        (out/'grade.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='checks' and k!='traceback'}))
    return 0

if __name__=='__main__':sys.exit(main())
