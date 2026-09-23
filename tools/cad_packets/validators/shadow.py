"""Independent checks consume CAD data only; never import a candidate builder."""
import argparse
import json
import math
from pathlib import Path
import traceback


class Checks:
    def __init__(self): self.rows=[]
    def add(self,name,ok,detail=None): self.rows.append(dict(name=name,passed=bool(ok),detail=detail))
    def result(self):return dict(passed=bool(self.rows) and all(r['passed'] for r in self.rows),checks=self.rows,
                                 passed_checks=sum(r['passed'] for r in self.rows),total_checks=len(self.rows))


def placement(f,A):
    return A.Placement(A.Vector(*f['translation']),A.Rotation(A.Vector(*f['axis']),f['angle_degrees']))


def same_frame(a,b):
    # Rotation.Angle has a 2pi representation ambiguity; compare three transformed axes.
    return max(abs(x-y) for x,y in zip(a.toMatrix().A,b.toMatrix().A))<1e-7


def world_shape(link):
    s=link.LinkedObject.Shape.copy()
    s.Placement=global_frame(link).multiply(s.Placement)
    return s


def global_frame(link):
    return link.getParentGeoFeatureGroup().getGlobalPlacement().multiply(link.Placement)


def exchange(path,shapes,c,label):
    import Part
    loaded=Part.Shape();loaded.read(str(path))
    expected=Part.makeCompound(shapes)
    c.add(label+'/STEP solid count',loaded.isValid() and len(loaded.Solids)==len(shapes))
    c.add(label+'/STEP volume',abs(loaded.Volume-expected.Volume)<max(1,expected.Volume)*1e-7)
    missing=sum(abs(s.cut(loaded).Volume) for s in shapes)
    extra=abs(loaded.cut(expected).Volume)
    c.add(label+'/STEP installed material',missing<1e-3 and extra<1e-3,dict(missing_mm3=missing,extra_mm3=extra))


def stack(inputs,artifacts,c):
    import FreeCAD as A
    specs=json.loads((inputs/'stack_spec.json').read_text())
    for label,p in specs.items():
        doc=A.openDocument(str(artifacts/(label+'.FCStd')))
        try:
            doc.recompute()
            physical=[o for o in doc.Objects if o.TypeId in ('App::Part','App::Link','PartDesign::Feature','Part::Feature')]
            c.add(label+'/definition, container and occurrence count',len(physical)==10,len(physical))
            assembly,station,defs=[doc.getObject(n) for n in ['Assembly','Station','Definitions']]
            c.add(label+'/nested parts',all(o.TypeId=='App::Part' for o in [assembly,station,defs])
                  and station in assembly.Group and set(o.Name for o in defs.Group)=={'Pin','Tube','Bush'})
            c.add(label+'/parent frames',same_frame(assembly.Placement,placement(p['assembly_frame'],A))
                  and same_frame(station.Placement,placement(p['station_frame'],A)))
            rows=[('Pin',p['pin_radius'],p['pin_bore_radius'],p['pin_length']),
                  ('Tube',p['tube_outer_radius'],p['tube_inner_radius'],p['tube_length']),
                  ('Bush',p['bush_outer_radius'],p['bush_inner_radius'],p['bush_length'])]
            for name,ro,ri,length in rows:
                obj=doc.getObject(name);s=obj.Shape
                c.add(label+'/'+name+'/one solid',s.isValid() and len(s.Solids)==1)
                c.add(label+'/'+name+'/identity definition',same_frame(obj.Placement,A.Placement()))
                bb=s.BoundBox
                c.add(label+'/'+name+'/extents',max(abs(x-y) for x,y in zip(
                    [bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax],[0,length,-ro,ro,-ro,ro]))<1e-6)
                expected=math.pi*(ro*ro-ri*ri)*length
                c.add(label+'/'+name+'/analytic volume',abs(s.Volume-expected)<expected*1e-8)
                witnesses=[]
                for x in [length*.1,length*.5,length*.9]:
                    for radius,inside in [(ri-.02,False),(ri+.02,True),(ro-.02,True),(ro+.02,False)]:
                        for angle in [0,37,103,211,300]:
                            t=math.radians(angle)
                            witnesses.append(s.isInside(A.Vector(x,radius*math.cos(t),radius*math.sin(t)),1e-7,False)==inside)
                c.add(label+'/'+name+'/material witnesses',all(witnesses),len(witnesses))
            positions={'PinInstance':('Pin',-p['pin_length']/2), 'TubeInstance':('Tube',-p['tube_length']/2),
                       'BushLeft':('Bush',-p['tube_length']/2), 'BushRight':('Bush',p['tube_length']/2-p['bush_length'])}
            c.add(label+'/four occurrences',set(o.Name for o in station.Group)==set(positions))
            shapes=[]
            for name,(target,x) in positions.items():
                obj=doc.getObject(name)
                c.add(label+'/'+name+'/definition link',obj.TypeId=='App::Link' and obj.LinkedObject.Name==target)
                local=A.Placement(A.Vector(x,0,0),A.Rotation())
                expected=placement(p['assembly_frame'],A).multiply(placement(p['station_frame'],A)).multiply(local)
                c.add(label+'/'+name+'/local and composed frame',same_frame(obj.Placement,local)
                      and same_frame(global_frame(obj),expected))
                c.add(label+'/'+name+'/unit scale',abs(obj.Scale-1)<1e-10 and tuple(obj.ScaleVector)==(1,1,1))
                shapes.append(world_shape(obj))
            overlaps=[abs(s.common(t).Volume) for i,s in enumerate(shapes) for t in shapes[i+1:]]
            c.add(label+'/no installed interference',max(overlaps)<1e-5,overlaps)
            exchange(artifacts/(label+'.step'),shapes,c,label)
        finally:A.closeDocument(doc.Name)


def mount(inputs,artifacts,c):
    import FreeCAD as A
    p=json.loads((inputs/'mount_spec.json').read_text())
    original=A.openDocument(str(inputs/'broken_mount.FCStd'))
    doc=A.openDocument(str(artifacts/'fixed.FCStd'))
    try:
        doc.recompute()
        c.add('all object identities/types preserved',[(o.Name,o.TypeId) for o in doc.Objects]==[(o.Name,o.TypeId) for o in original.Objects])
        for old in original.Objects:
            obj=doc.getObject(old.Name)
            if old.TypeId=='App::Part':
                c.add(old.Name+'/parent membership',set(o.Name for o in old.Group)==set(o.Name for o in obj.Group))
            if hasattr(old,'LinkedObject'):
                c.add(old.Name+'/shared definition',obj.LinkedObject.Name==old.LinkedObject.Name)
            if old.Name not in {'BoltLeft1','BoltRight2'} and hasattr(old,'Placement'):
                c.add(old.Name+'/unaffected frame preserved',same_frame(old.Placement,obj.Placement))
        for name in ['Plate','Bolt']:
            before,after=original.getObject(name).Shape,doc.getObject(name).Shape
            difference=abs(before.cut(after).Volume)+abs(after.cut(before).Volume)
            c.add(name+'/qualified definition preserved',difference<1e-6 and after.isValid() and len(after.Solids)==1,difference)
        shapes=[]
        for side in ['Left','Right']:
            group=doc.getObject(side)
            c.add(side+'/parent frame',same_frame(group.Placement,placement(p['side_frames'][side],A)))
            plate=doc.getObject('Plate'+side);plate_shape=world_shape(plate);shapes.append(plate_shape)
            for i,(x,y) in enumerate(p['holes']):
                name=f'Bolt{side}{i}';obj=doc.getObject(name)
                local=A.Placement(A.Vector(x,y,0),A.Rotation())
                expected=placement(p['rig_frame'],A).multiply(placement(p['side_frames'][side],A)).multiply(local)
                c.add(name+'/local and global frames',same_frame(obj.Placement,local) and same_frame(global_frame(obj),expected))
                c.add(name+'/unit scale',abs(obj.Scale-1)<1e-10 and tuple(obj.ScaleVector)==(1,1,1))
                s=world_shape(obj);shapes.append(s)
                c.add(name+'/hole clearance',abs(s.common(plate_shape).Volume)<1e-6)
        diagnosis=json.loads((artifacts/'diagnosis.json').read_text())
        c.add('diagnosed both damaged occurrences',set(diagnosis['changed_objects'])=={'BoltLeft1','BoltRight2'})
        c.add('nonempty diagnosis',len(diagnosis.get('cause',''))>=30)
        exchange(artifacts/'fixed.step',shapes,c,'mount')
    finally:A.closeDocument(doc.Name);A.closeDocument(original.Name)


def spring(inputs,artifacts,c):
    p=json.loads((artifacts/'assessment.json').read_text())
    values=dict(printed_spring_od_in=3.937,assumed_wire_diameter_in=1.0,printed_tube_od_in=3.812,
                literal_spring_id_mm=49.1998,tube_od_mm=96.8248,literal_radial_clearance_mm=-23.8125,
                alternative_spring_id_mm=99.9998,alternative_spring_od_mm=150.7998,alternative_radial_clearance_mm=1.5875)
    for k,v in values.items():c.add(k,isinstance(p.get(k),(float,int)) and not isinstance(p.get(k),bool) and abs(p[k]-v)<1e-4,p.get(k))
    for k,v in dict(spring_mark='M1336',tube_mark='M1333',decision_status='needs_source_review',
                    memo_supported=False,historical_dimensions_proven=False).items():
        c.add(k,p.get(k)==v,p.get(k))
    c.add('literal wording retained','outside' in p.get('source_wording','').lower())
    c.add('missing evidence stated',len(p.get('missing_evidence',''))>=30)


def evaluate(case,inputs,artifacts):
    c=Checks()
    try:
        {'stack':stack,'mount':mount,'spring':spring}[case](inputs,artifacts,c)
    except Exception:
        c.add('validator execution',False,traceback.format_exc())
    return c.result()


def main():
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--artifacts',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();packet=json.loads(a.packet.read_text())
    result=evaluate(packet['id'],a.inputs,a.artifacts/'deliverables')
    import FreeCAD as A
    import Part
    result['runtime']=dict(freecad=A.Version(),occ=Part.OCC_VERSION)
    a.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}))


if __name__=='__main__':main()
