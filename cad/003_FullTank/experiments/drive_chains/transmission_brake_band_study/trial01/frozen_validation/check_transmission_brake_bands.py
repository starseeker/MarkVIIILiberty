"""Inspect saved brake solids, printed dimensions, contact, hierarchy and context."""
import argparse
import math
from pathlib import Path
import sys
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--standard-manifest',type=Path,required=True)
a=p.parse_args();out=a.candidate.resolve();r=read(out/'report.json');m=read(out/'isolated/manifest.json')
source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json');standard=read(a.standard_manifest)
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
assert all(sha(ROOT/f)==v for f,v in standard['native_files'].items())
rows,prior,tank=[{v['name']:v for v in d['occurrences']} for d in [m,old,standard]]
checks=[]
def ck(name,passed,**detail):
    checks.append(dict(name=name,passed=bool(passed),**detail));write(out/'check_progress.json',checks)
    print(name,bool(passed),flush=True)
def near(name,value,expected=0,tol=1e-5):ck(name,abs(value-expected)<tol,actual=value,expected=expected,tolerance=tol)
def error(a,b):return float(np.max(np.abs(np.array(a)-b)))
expected=r['expected_new_occurrences'];newdefs=set(r['new_definitions']);changed=set(r['changed_definitions'])
ck('HB segmented variant: eight half-bands, twenty-four linings and 216 rivets',len(expected)==248
   and sum(n.endswith('Band') for n in expected)==8 and sum(n.endswith('Lining') for n in expected)==24
   and sum('Rivet' in n for n in expected)==216 and rows.keys()==prior.keys()|expected.keys()
   and len(rows)==r['expected_physical_occurrences'])
frames=[]
for name,row in rows.items():
    target=expected.get(name,prior.get(name));delta=error(row['frame'],target['frame'])
    frames.append(dict(name=name,error=delta,passed=delta<1e-7 and row['definition']==target['definition'] and row['owners']==target['owners']))
ck('All prior frames and owners retained; new composed frames correct',all(v['passed'] for v in frames))
assemblies=[]
for name,before in old['assemblies'].items():
    after=m['assemblies'][name];added=newdefs if name=='Definitions' else {'TransmissionBrakeBands'} if name=='Root' else set()
    assemblies.append(dict(name=name,passed=error(before['local'],after['local'])<1e-7 and error(before['world'],after['world'])<1e-7
        and set(after['children'])==set(before['children'])|added))
ck('Prior assembly frames and children retained',all(v['passed'] for v in assemblies)
   and m['assemblies'].keys()==old['assemblies'].keys()|set(r['new_assemblies'])
   and len(m['assemblies'])==r['expected_assembly_count'])
ck('Existing definition identities retained; exactly two receivers revised',m['definitions'].keys()==old['definitions'].keys()|newdefs
   and all(v['properties']==m['definitions'][n]['properties'] for n,v in old['definitions'].items())
   and changed=={'Def_TransmissionCore_brake_case','Def_Output_drum'} and len(newdefs)==5)
for role,mark,rid in [('low_band','M344','HB:nomenclature:207:043'),('low_lining','M346','HB:nomenclature:207:044'),
    ('track_band','M349','HB:nomenclature:207:046'),('track_lining','M351','HB:nomenclature:207:047')]:
    props=m['definitions']['Def_BrakeBand_'+role]['properties']
    ck(mark+' source identity retained',props['SourcePartMark']==mark and rid in props['SourceRecords'])
import FreeCAD as App
import Part
V=App.Vector;cache={};c=r['controls']
def definition(name,scope='new'):
    key=scope,name
    if key not in cache:
        d={'new':m,'old':old,'standard':standard}[scope]['definitions'][name];f=Path(d['brep_path']);assert sha(f)==d['brep_sha256']
        s=Part.Shape();s.read(str(f));assert s.Placement.isIdentity();cache[key]=s
    return cache[key].copy()
def shape(name,scope='new'):
    row={'new':rows,'old':prior,'standard':tank}[scope][name];s=definition(row['definition'],scope)
    s.Placement=App.Placement(App.Matrix(*row['frame']));return s
def faces(s,kind):return [f for f in s.Faces if isinstance(f.Surface,kind)]
def contact(fs,gs):
    return sum(f.common(g).Area for f in fs for g in gs if f.distToShape(g)[0]<1e-6)
def coverage(fs,gs):
    # Area integration on re-trimmed cylindrical faces can vary while their
    # complete surface difference is empty. Require exact coverage topology,
    # coincident analytic supports and full axial containment instead.
    result=[]
    for f in fs:
        matched=[g for g in gs if abs(f.Surface.Radius-g.Surface.Radius)<1e-7
            and f.Surface.Axis.cross(g.Surface.Axis).Length<1e-7
            and (f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length<1e-7
            and g.BoundBox.YMin<=f.BoundBox.YMin+1e-7 and g.BoundBox.YMax>=f.BoundBox.YMax-1e-7]
        if not matched:result.append(dict(passed=False,reason='No coincident complete support'));continue
        missing=f.cut(Part.makeCompound(matched))
        result.append(dict(passed=len(missing.Faces)==0 and abs(missing.Area)<1e-5,
            uncovered_faces=len(missing.Faces),uncovered_area_mm2=missing.Area,face_area_mm2=f.Area))
    return bool(result) and all(v['passed'] for v in result),result
def cylinders(s,radius):return [f for f in faces(s,Part.Cylinder) if abs(f.Surface.Radius-radius)<1e-6]
for name in sorted(newdefs|changed):
    s=definition(name);ck(name+' valid single solid',s.isValid() and len(s.Solids)==1 and s.getTolerance(1)<=1e-4,tolerance_mm=s.getTolerance(1))
# Printed values are transcribed independently from HB97 and HB98, not taken
# from the builder's dimensions report. Estimates remain named controls.
printed={'low':dict(radius=11.75*25.4,width=3.75*25.4,length=11.875*25.4,pitch=3.5*25.4),
         'track':dict(radius=12*25.4,width=2.75*25.4,length=12.0625*25.4,pitch=3.5625*25.4)}
for role,v in printed.items():
    liner=definition('Def_BrakeBand_'+role+'_lining');band=definition('Def_BrakeBand_'+role+'_band')
    inner=cylinders(liner,v['radius']);outer=cylinders(liner,v['radius']+5/16*25.4)
    ck(role+' printed inner radius and lining thickness',len(inner)==len(outer)==1)
    near(role+' printed axial width',liner.BoundBox.YLength,v['width'])
    radial_ends=[f for f in faces(liner,Part.Plane) if abs(f.normalAt(0,0).y)<1e-6]
    angles=sorted(math.atan2(f.CenterOfMass.z,f.CenterOfMass.x) for f in radial_ends)
    ck(role+' two planar radial segment ends',len(angles)==2)
    near(role+' printed flat length retained at middle radius',(angles[-1]-angles[0])*(v['radius']+5/32*25.4),v['length'])
    holes=cylinders(liner,9/64*25.4);cones=faces(liner,Part.Cone)
    ck(role+' nine printed bores and nine countersinks',len(holes)==9 and len(cones)==9)
    ck(role+' seventy degree countersinks',all(abs(abs(f.Surface.SemiAngle)-math.radians(35))<1e-7 for f in cones))
    witnesses=[]
    for column in range(4):
        theta=(11/16*25.4+column*v['pitch'])/(v['radius']+5/32*25.4)
        ys=[-v['width']/2+5/8*25.4,v['width']/2-5/8*25.4]
        if column==0:ys.append(0)
        for y in ys:
            axis=V(math.cos(theta),0,math.sin(theta));origin=axis*(v['radius']+5/16*25.4-1)+V(0,y,0)
            matching=[f for f in holes if abs(abs(f.Surface.Axis.dot(axis))-1)<1e-7
                and (origin-f.Surface.Center).cross(axis).Length<1e-6]
            bore=Part.makeCylinder(3.1,1.5,origin-axis*.5,axis)
            witnesses.append(dict(column=column,y=y,passed=len(matching)==1 and abs(liner.common(bore).Volume)<1e-5))
    ck(role+' printed hole pitch, end margin, edge rows and clear bores',all(v['passed'] for v in witnesses),witnesses=witnesses)
    # A filled receiving hole must fail the same material witness.
    filled=liner.fuse(bore);ck(role+' filled-bore negative control rejected',filled.common(bore).Volume>1)
    near(role+' steel axial width',band.BoundBox.YLength,v['width']+2*c['steel_side_overhang'])
    ck(role+' steel radial stock',len(cylinders(band,v['radius']+5/16*25.4))>=1
       and len(cylinders(band,v['radius']+5/16*25.4+c['steel_stock']))>=1)
    name=r['lands'][role]['definition'];oldshape=definition(name,'old');newshape=definition(name)
    near(role+' all old drum material retained',oldshape.cut(newshape).Volume)
    of=max([f for f in faces(oldshape,Part.Cylinder) if abs(abs(f.Surface.Axis.y)-1)<1e-7],key=lambda f:f.Surface.Radius)
    rr=of.Surface.Radius;bb=of.BoundBox
    interior=Part.makeCylinder(rr,bb.YLength+4,V(0,bb.YMin-2,0),V(0,1,0))
    near(role+' original internal voids retained',newshape.cut(oldshape).common(interior).Volume)
    for edge,lo,hi in [('first',bb.YMin-1,bb.YMin+c['protected_end_width']),('last',bb.YMax-c['protected_end_width'],bb.YMax+1)]:
        region=Part.makeCylinder(v['radius']+2,hi-lo,V(0,lo,0),V(0,1,0))
        near(role+' '+edge+' end strip unchanged',newshape.cut(oldshape).common(region).Volume)
    land=cylinders(newshape,v['radius']);ck(role+' new analytic friction land',len(land)==1)
    near(role+' land includes axial edge margins',land[0].BoundBox.YLength,v['width']+2*c['land_axial_margin'])
rivet=definition('Def_BrakeBand_copper_rivet');head=faces(rivet,Part.Cone)[0]
depth=c['lining_stock']-c['straight_lining_stock']-c['rivet_head_recess'];small=9/64*25.4
big=small+depth*math.tan(math.radians(35))
stock_volume=math.pi*depth*(small*small+small*big+big*big)/3+math.pi*(c['rivet_shank_diameter']/2)**2*c['rivet_stock_length']
near('Upset rivet retains complete estimated stock volume',rivet.Volume,stock_volume)
contacts=[]
for name in expected:
    if not name.endswith('Lining'):continue
    one=shape(name);role='low' if 'LowSpeed' in name else 'track';v=printed[role]
    bandname=name.split('Segment')[0]+'Band';drumname=('Port' if name.startswith('Port') else 'Starboard')+('TransmissionCore_brake_case' if role=='low' else 'TransmissionOutput_drum')
    inner=cylinders(one,v['radius']);outer=cylinders(one,v['radius']+5/16*25.4)
    drum=shape(drumname);band=shape(bandname)
    inner_area=contact(inner,cylinders(drum,v['radius']));outer_area=contact(outer,cylinders(band,v['radius']+5/16*25.4))
    for label,fs,gs in [('friction',inner,cylinders(drum,v['radius'])),('steel backing',outer,cylinders(band,v['radius']+5/16*25.4))]:
        passed,evidence=coverage(fs,gs);ck(name+' full '+label+' contact',passed,coverage=evidence)
    contacts.append(dict(name=name,friction_area_mm2=sum(f.Area for f in inner),backing_area_mm2=sum(f.Area for f in outer),
        boolean_intersection_friction_area_mm2=inner_area,boolean_intersection_backing_area_mm2=outer_area))
    if name in ['PortTrackBrakeLowerSegment1Lining','StarboardTrackBrakeUpperSegment3Lining']:
        moved=one.copy();moved.translate(V(.01,0,0))
        ok,evidence=coverage(cylinders(moved,v['radius']),cylinders(drum,v['radius']))
        ck(name+' displaced-lining negative control loses full coverage',not ok,coverage=evidence)
# All nine distinct joint stations for each type. Repeated installations have
# separately checked rigid frames and full material-interference checks below.
joint_contacts=[]
for label in ['LowSpeed','Track']:
    prefix='Port'+label+'BrakeUpper';lining=shape(prefix+'Segment1Lining');band=shape(prefix+'Band')
    for i in range(1,10):
        name=prefix+'Segment1Rivet'+str(i);one=shape(name);cone=faces(one,Part.Cone)
        seated=contact(cone,faces(lining,Part.Cone));near(name+' conical head fully seated',seated,sum(f.Area for f in cone))
        tail_area=contact(faces(one,Part.Plane),faces(band,Part.Plane))
        required=math.pi*(c['rivet_tail_radius']**2-(c['rivet_shank_diameter']/2+c['steel_hole_clearance'])**2)
        near(name+' tail bears on complete spotface annulus',tail_area,required)
        moved=one.copy();direction=App.Placement(App.Matrix(*rows[name]['frame'])).Rotation.multVec(V(0,0,1));moved.translate(direction*.02)
        near(name+' lifted-head negative control loses seating',contact(faces(moved,Part.Cone),faces(lining,Part.Cone)))
        joint_contacts.append(dict(name=name,head_area_mm2=seated,tail_area_mm2=tail_area))
affected=set(r['affected_occurrences']);all_shapes={n:shape(n) for n in rows}
def bounds(s):
    b=s.copy().cleaned().BoundBox;return np.array([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
def collisions(others,label,same):
    names=sorted(others);boxes=np.array([bounds(others[n]) for n in names]);seen=set();records=[]
    for name in sorted(affected):
        one=all_shapes[name];bb=bounds(one)
        possible=np.where(np.all(boxes[:,:3]<=bb[3:]+1e-7,axis=1)&np.all(boxes[:,3:]>=bb[:3]-1e-7,axis=1))[0]
        for i in possible:
            other=names[i];pair=tuple(sorted([name,other])) if same else (name,other)
            if (same and name==other) or pair in seen:continue
            seen.add(pair);v=one.common(others[other]).Volume
            records.append(dict(first=name,second=other,common_mm3=v,passed=abs(v)<1e-5));write(out/(label+'_material_progress.json'),records)
        print(label,name,len(records),'pairs',flush=True)
    ck(label+' all nearby material pairs clear',all(v['passed'] for v in records),pair_count=len(records));return records
development=collisions(all_shapes,'development',True)
excluded=(set(rows)&set(tank))|{'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}
context={n:shape(n,'standard') for n,v in tank.items() if n not in excluded and v['representation']=='assembly'}
standard_pairs=collisions(context,'standard',False)
result=dict(local_brake_checks_passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],source_native_sha256=sha(source),
    checker_sha256=sha(Path(__file__)),checks=checks,occurrence_frames=frames,assembly_checks=assemblies,contacts=contacts,
    joint_contacts=joint_contacts,development_material_pairs=development,standard_material_pairs=standard_pairs,
    standard_manifest_sha256=sha(a.standard_manifest),standard_context_count=len(context),excluded_standard_occurrences=sorted(excluded&set(tank)),
    historical_geometry_qualified=False,installation_qualified=False,ears_and_linkage_pending=True)
write(out/'independent_checks.json',result)
print('Finished',len(checks),'checks; failures',[v['name'] for v in checks if not v['passed']],flush=True)
assert result['local_brake_checks_passed']
