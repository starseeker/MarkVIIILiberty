"""Independently inspect saved shaft material, bearing interfaces and tank context."""
import argparse,math
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1];ROOT=STAGE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE/'engine_crankshaft_build')
p.add_argument('--worker',action='store_true');p.add_argument('--local-only',action='store_true');a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    args=[sys.executable,__file__,'--candidate',str(out),'--worker']+(['--local-only'] if a.local_only else [])
    with (out/'interface_check.log').open('w') as log:sys.exit(subprocess.run(args,env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves,shape_signature
    from lib.worker import same_shape,placement_errors,check_build
    V=App.Vector;X=V(1,0,0);Z=V(0,0,1)
    native=out/'DrivetrainWithEngineCrankshaft.FCStd';r=read(out/'report.json');assert sha(native)==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items};c=r['controls'];cc=r['case_controls'];d=r['datums'];checks=[]
    shaft=doc.Def_EngineCrank_shaft.Shape;upper=doc.Def_EngineCase_upper.Shape;lower=doc.Def_EngineCase_lower.Shape;origin=doc.TankLibertyEngine.Placement.Base
    def ck(name,result,detail=None):
        checks.append(dict(name=name,passed=bool(result),detail=detail))
        if not result:print('FAIL',name,detail,flush=True)
    def near(name,value,expected=0,tol=1e-6):ck(name,abs(value-expected)<tol,dict(actual=value,expected=expected,tolerance=tol))
    def inside(name,s,p,expected=True):ck(name,s.isInside(V(*p),1e-7,False)==expected,dict(point=p,expected_material=expected))
    def local(name):
        s=byid[name]['shape'].copy();s.translate(-origin);return s
    ck('1992 unique physical occurrences',len(items)==len(byid)==1992 and all(i['representation']!='layout' for i in items))
    ck('81 new physical constituents',len(r['new_ids'])==81)
    ck('28 main bearing constituents',len(leaves(doc.EngineMainBearings))==28)
    ck('one thrust catalogue item with45 constituents',doc.EngineThrustBearing.OriginalMark=='LQ273A' and len(leaves(doc.EngineThrustBearing))==45)
    ck('engine subassemblies own all new leaves',all(doc.getObject(n) in doc.TankLibertyEngine.Group for n in ['EngineRotatingAssembly','EngineMainBearings','EngineThrustBearing']))
    ck('affected shapes are valid single solids',all(byid[n]['shape'].isValid() and len(byid[n]['shape'].Solids)==1 for n in r['exchange_ids']))
    ck('definitions hidden',not doc.Definitions.Visibility)
    for name,expected in [('journal_diameter',66.675),('stroke',177.8),('main_bearing_long_length',115.),('main_bearing_short_length',49.),('key_screw_length',19.05),('output_cotter_length',76.2)]:near('source '+name,c[name],expected)
    ck('diametral clearance within handbook interval',.0025*25.4<=c['bearing_diametral_clearance']<=.00325*25.4)
    ck('journal endplay distinct from thrust endplay',.0575*25.4<=c['journal_endplay']<=.0775*25.4)
    first=cc['nose_to_first_row'];rows=[first+i*165.1 for i in range(7)];short=49;long=115
    seats=[(first+short/2-long,first+short/2)]+[(x-short/2,x+short/2) for x in rows[1:]]
    jr=33.3375;inner=jr+c['bearing_diametral_clearance']/2;outer=cc['crankshaft_diameter']/2+cc['main_bearing_shell_stock']
    for i,(a,b) in enumerate(seats):
        length=b-a;label='long' if i==0 else 'short'
        for sign,word in [(1,'upper'),(-1,'lower')]:
            name='EngineCrank_Main%d_%s'%(i+1,word);shell=local(name);bb=shell.optimalBoundingBox(False)
            near(name+' axial source length',bb.XLength,length,1e-5);near(name+' seat start',bb.XMin,a,1e-5)
            near(name+' running clearance',shaft.distToShape(shell)[0],c['bearing_diametral_clearance']/2,1e-5)
            near(name+' seated outer shell',shell.distToShape(upper if sign>0 else lower)[0])
            expected={'long_lower':'LQ238A','long_upper':'LQ239A','short_lower':'LQ240A','short_upper':'LQ241A'}[label+'_'+word]
            ck(name+' catalogue identity',byid[name]['target'].OriginalMark==expected)
            # Uninterrupted running land, casing saddle and oil-feed voids.
            x=a+length*.12
            inside(name+' inner running land',shell,[x,0,sign*(inner+.3)])
            inside(name+' retained saddle',upper if sign>0 else lower,[x,0,sign*(outer+2)])
            for fx in ([a+length*.25,a+length*.75] if i==0 else [(a+b)/2]):
                witness=Part.makeCylinder(c['bearing_oil_feed_radius']-.1,outer+1,V(fx,0,0),Z*sign)
                near(name+' oil entry '+str(fx),shell.common(witness).Volume,0,1e-5)
            dowel=local(name+'_Dowel');ck(name+' dowel identity',byid[name+'_Dowel']['target'].OriginalMark=='LQ194A')
            near(name+' dowel length',dowel.optimalBoundingBox(False).ZLength,c['dowel_length'],1e-5)
            near(name+' dowel recessed from shaft',dowel.distToShape(shaft)[0],c['dowel_radial_start']-jr,1e-5)
        # A hollow journal, with real material around its bore and source radius.
        x=(a+b)/2
        inside('main%d cavity'%i,shaft,[x,0,0],False)
        inside('main%d journal land'%i,shaft,[x,jr-.2,0])
        inside('main%d outer diameter void'%i,shaft,[x,jr+.01,0],False)
    for i,offset in enumerate([0,-120,120,120,-120,0]):
        phase=math.radians(c['static_phase_deg']+offset);pin=V(0,88.9*math.sin(phase),88.9*math.cos(phase));x=first+(i+.5)*165.1
        inside('crank%d hollow pin'%i,shaft,[x,pin.y,pin.z],False)
        normal=V(0,math.cos(phase),-math.sin(phase));point=V(x,pin.y,pin.z)+normal*(c['crankpin_diameter']/2-.3)
        inside('crank%d source stroke and plane material'%i,shaft,list(point))
        inside('crank%d no fictitious axial bar'%i,shaft,[x,0,0],False)
        faces=[f for f in shaft.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-c['crankpin_diameter']/2)<1e-6 and abs(f.Surface.Center.y-pin.y)<1e-6 and abs(f.Surface.Center.z-pin.z)<1e-6 and f.BoundBox.XMin<x<f.BoundBox.XMax]
        ck('crank%d analytic pin axis on source station'%i,bool(faces))
    for i,passage in enumerate(d['oil_passages']):
        # Independently intersect the reopened material with a narrow witness.
        start=V(*passage['start']);end=V(*passage['end']);axis=end-start
        near('shaft oil passage%d open'%i,shaft.common(Part.makeCylinder(1,axis.Length,start,axis)).Volume,0,1e-5)
    for x in [first-cc['nose_second_web_spacing']]+rows:
        for sign in [-1,1]:
            tool=Part.makeCylinder(6.35,120,V(x,sign*50.8,-60))
            near('case bearing-stud receiver '+str((x,sign)),upper.common(tool).Volume+lower.common(tool).Volume,0,1e-5)
    for i in range(6):
        x=first+(i+.5)*165.1
        for sign in [-1,1]:
            axis=V(0,sign*math.sin(math.radians(22.5)),math.cos(math.radians(22.5)))
            center=V(x,0,0)+axis*(cc['deck_center_height']*math.cos(math.radians(22.5)))
            near('preserved cylinder receiver '+str((i,sign)),upper.common(Part.makeCylinder(63.5,30,center-axis*20,axis)).Volume,0,1e-5)
    inside('old gear floor removed',upper,[rows[-1]+60,100,cc['gear_chamber_floor']-4],False)
    inside('raised gear floor has material',upper,[rows[-1]+60,100,c['gear_floor_height']-4])
    inside('space below raised gear floor',upper,[rows[-1]+60,100,c['gear_floor_height']-cc['case_wall']-2],False)
    for x,y,rad in [(rows[-1]+78,0,34),(rows[-1]+25,55,9)]:
        near('gear floor opening '+str((x,y)),upper.common(Part.makeCylinder(rad-.5,c['gear_floor_height']+2,V(x,y,-1))).Volume,0,1e-5)
    # Check the assembled thrust, including each separate ball's location/radius.
    thrust=leaves(doc.EngineThrustBearing);ballnames=[n for n in r['new_ids'] if 'Ball' in n]
    ck('two rows of20 individual balls',len(ballnames)==40)
    for n in ballnames:
        s=local(n);center=s.Solids[0].CenterOfMass
        near(n+' spherical volume',s.Volume,4*math.pi*c['thrust_ball_radius']**3/3,1e-5)
        near(n+' pitch radius',math.hypot(center.y,center.z),c['thrust_ball_pitch_radius'])
        near(n+' row station',abs(center.x-c['thrust_center']),c['thrust_ball_row_offset'])
    for side in ['Left','Right']:
        race=local('EngineCrank_Thrust'+side+'Race');sleeve=local('EngineCrank_Thrust'+side+'Sleeve')
        near(side+' outer race against sleeve back',race.distToShape(sleeve)[0])
        near(side+' sleeve seated axially in casing',min(sleeve.distToShape(upper)[0],sleeve.distToShape(lower)[0]))
        ck(side+' race has analytic rolling groove',any(isinstance(f.Surface,Part.Toroid) for f in race.Faces))
    center=local('EngineCrank_ThrustCenter');nut=local('EngineCrank_ThrustNut')
    near('central race against shaft shoulder',shaft.distToShape(center)[0])
    near('thrust nut against central race',nut.distToShape(center)[0])
    fly=byid['ClutchDrum_flywheel']['shape'];worldshaft=byid['EngineCrank_Forging']['shape']
    near('shaft taper seated in existing flywheel',worldshaft.distToShape(fly)[0])
    near('output nut seats against flywheel',byid['EngineCrank_OutputNut']['shape'].distToShape(fly)[0])
    near('key seats in shaft',byid['EngineCrank_FlywheelKey']['shape'].distToShape(worldshaft)[0])
    near('cotter source developed leg length',d['output_cotter']['total_leg_centerline_mm'],76.2)
    # All old physical material outside the two revised cases stays unchanged.
    print('Checking parent preservation.',flush=True)
    parent=App.openDocument(str(HERE/'engine_case_build/DrivetrainWithEngineCase.FCStd'));old={i['id']:i for i in leaves(parent.Root)};failed=[]
    for n,i in old.items():
        if n in r['changed_ids']:continue
        t,angle=placement_errors(i['shape'].Placement,byid[n]['shape'].Placement)
        if not(same_shape(shape_signature(i['shape']),shape_signature(byid[n]['shape'])) and t<1e-6 and angle<1e-8):failed.append(n)
    ck('1909 unaffected parent occurrences preserved',len(old)-2==1909 and not failed,failed)
    write(out/'independent_checks.json',dict(passed=all(x['passed'] for x in checks),checks=checks,native_sha256=sha(native),checker_sha256=sha(Path(__file__)),scope='Static crankshaft/bearing development, source applicability conditional; plugs/gear/rods remain pending'))
    candidates=dict(byid);affected=set(r['exchange_ids']);pairs=[];seen=set()
    if not a.local_only:
        standard=check_build(STAGE/'build');tank=App.openDocument(standard['build']['top_document'])
        for item in leaves(tank.Root):
            if item['representation']!='layout' and item['id'] not in byid:candidates['Standard_'+item['id']]=item
    boxes={n:item['shape'].BoundBox for n,item in candidates.items()}
    def overlaps(a,b):return all(getattr(a,k+'Min')<=getattr(b,k+'Max')+1e-7 and getattr(b,k+'Min')<=getattr(a,k+'Max')+1e-7 for k in ['X','Y','Z'])
    for n in sorted(affected):
        for other in sorted(candidates):
            pair=tuple(sorted([n,other]))
            if n==other or pair in seen or not overlaps(boxes[n],boxes[other]):continue
            seen.add(pair);volume=abs(byid[n]['shape'].common(candidates[other]['shape']).Volume)
            pairs.append(dict(a=n,b=other,overlap_mm3=volume,passed=volume<1e-5))
            if len(pairs)%20==0:
                write(out/'material_progress.json',dict(checked=len(pairs),failed=[x for x in pairs if not x['passed']]))
                print('Material pairs',len(pairs),flush=True)
    failures=[x for x in pairs if not x['passed']]
    write(out/'material_checks.json',dict(passed=not failures,native_sha256=sha(native),pairs=pairs,overlaps=failures,standard_context_checked=not a.local_only))
    print(len(checks),'independent;',len(pairs),'material pairs;',len(failures),'overlaps.',flush=True)
    assert all(x['passed'] for x in checks) and not failures
finally:
    runtime.close()
