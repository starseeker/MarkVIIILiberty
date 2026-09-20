"""Build/reopen a complete isolated fifty-pitch chain hypothesis and its sprockets."""
import argparse
from collections import Counter
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=Path,required=True)
parser.add_argument('--output',type=Path,default=ROOT/'chain_candidate_build')
parser.add_argument('--worker',action='store_true')
args=parser.parse_args();stage=args.stage.resolve();out=args.output.resolve()
sys.path.insert(0,str(stage))
from lib import runtime
from lib.evidence import fingerprint,read,write,sha
if not args.worker:
    out.mkdir(parents=True,exist_ok=True)
    with (out/'run.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--stage',str(stage),'--output',str(out),
            '--worker'],env=runtime.environment(out),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui()
    from lib.model import load
    from lib.cad_build import metadata,leaves
    from lib.pinion_geometry import values,station
    from lib.pinion_parts import casting
    from lib.visual_review import shaded
    from chain_parts import parts
    from sprocket_geometry import open_flanks
    data=load();lock=fingerprint();controls=read(ROOT/'chain_candidate_controls.json')
    a={key:record['value'] for key,record in controls['controls'].items()}
    route=read(ROOT/'installed_pitch_route_report.json');big=values(data)
    center=station(data,1);points=route['vertices_world_xz_mm'];count=int(a['pitch_count'])
    assert count==50 and len(points)==count
    shapes=parts(a,big)
    shapes['roller_pinion']=open_flanks(casting(dict(big,chain_relief_radius=a['seat_radius'])),
        int(big['teeth']),big['chain_pitch_radius'],big['sprocket_radius'],big['tooth_width'],
        a['seat_radius'],a['flank_angle'])
    sources=dict(inner_bar=['P_d19f35ff3a948e5e'],outer_bar=['P_091e568ad342a1e0'],
                 bush=['P_108191214e2f2d25'],pin=['P_552691f5ff4ccb7b'],cotter=['P_d890a06c05938c09'],
                 transmission_pinion=['P_37432287284f7f15'],
                 roller_pinion=data['definitions']['pinion_casting']['survey_ids'])
    doc=App.newDocument('DriveChainCandidate')
    library=doc.addObject('App::Part','Definitions');defs={}
    root=doc.addObject('App::Part','Root');root.Label='Drive chain — isolated 50-pitch hypothesis'
    metadata(root,PhysicalRelease=False,QuantityConflict=controls['quantity_interpretation'])
    for name,shape in shapes.items():
        body=doc.addObject('PartDesign::Body','Def_'+name);library.addObject(body)
        feature=body.newObject('PartDesign::Feature','ReconstructedSolid');feature.Shape=shape
        metadata(body,DefinitionId=name,Representation='assembly',Coverage='partial',
                 SurveyIds=sources[name],ReconstructionNotes='Isolated chain study; see chain_candidate_controls.json')
        defs[name]=body
    def group(name,parent,translation=(0,0,0),angle=0):
        obj=doc.addObject('App::Part',name);parent.addObject(obj)
        obj.Placement=App.Placement(App.Vector(*translation),App.Rotation(App.Vector(0,1,0),angle))
        return obj
    def link(name,key,parent,translation=(0,0,0),angle=0):
        obj=doc.addObject('App::Link',name);parent.addObject(obj);obj.setLink(defs[key])
        obj.LinkPlacement=App.Placement(App.Vector(*translation),App.Rotation(App.Vector(0,1,0),angle))
        metadata(obj,OccurrenceId=name,Subsystem='Drivetrain')
        return obj
    chain=group('Chain',root);links=group('BarPairs',chain);joints=group('PinJoints',chain)
    for n,(x,z) in enumerate(points):
        nxt=points[(n+1)%count];previous=points[(n-1)%count]
        distance=math.dist((x,z),nxt)
        if abs(distance-a['pitch'])>1e-7:raise ValueError('Route is not source pitch')
        angle=-math.degrees(math.atan2(nxt[1]-z,nxt[0]-x))
        unit=group('Link%02d'%n,links,(x,center[1],z),angle)
        kind='inner' if n%2==0 else 'outer'
        y=a['inside_gap']/2+a['inner_stock']/2 if kind=='inner' else a['outside_gap']/2+a['outer_stock']/2
        for hand,sign in [('Inboard',-1),('Outboard',1)]:
            link('Link%02d_%s'%(n,hand),kind+'_bar',unit,(0,sign*y,0))
        normal=-math.degrees(math.atan2(nxt[1]-previous[1],nxt[0]-previous[0]))+180
        joint=group('Joint%02d'%n,joints,(x,center[1],z),normal)
        link('Joint%02d_Bush'%n,'bush',joint)
        link('Joint%02d_Pin'%n,'pin',joint)
        link('Joint%02d_Cotter'%n,'cotter',joint,(0,a['cotter_center_y'],0))
    gears=group('Sprockets',root)
    link('RollerPinion','roller_pinion',gears,center,big['static_phase'])
    small=route['candidate_transmission_axis_xz_mm']
    link('TransmissionPinion','transmission_pinion',gears,(small[0],center[1],small[1]),
         route['small_pinion_candidate_phase_deg'])
    library.Visibility=False
    doc.recompute();native=out/'DriveChainCandidate.FCStd';doc.saveAs(str(native));App.closeDocument(doc.Name)
    doc=App.openDocument(str(native));doc.recompute();items=leaves(doc.Root)
    counts=Counter(i['definition'] for i in items)
    expected=dict(inner_bar=50,outer_bar=50,bush=50,pin=50,cotter=50,roller_pinion=1,transmission_pinion=1)
    if counts!=expected:raise ValueError('Reopened chain composition differs from the declared hypothesis')
    for item in items:
        shape=item['shape']
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid native leaf '+item['id'])
    overlaps=[];tested=0
    for i,left in enumerate(items):
        for right in items[i+1:]:
            if not left['shape'].BoundBox.intersect(right['shape'].BoundBox):continue
            tested+=1;volume=left['shape'].common(right['shape']).Volume
            if volume>1e-5:overlaps.append(dict(a=left['id'],b=right['id'],volume_mm3=volume))
    index={i['id']:i for i in items};joint_checks=[]
    for n in range(count):
        bush=index['Joint%02d_Bush'%n]['shape'];pin=index['Joint%02d_Pin'%n]['shape']
        gap=bush.distToShape(pin)[0];expected_gap=(a['pin_hole_diameter']-a['pin_diameter'])/2
        if abs(gap-expected_gap)>1e-6:raise ValueError('Reopened bush/pin radial clearance differs at joint '+str(n))
        joint_checks.append(dict(joint=n,radial_gap_mm=gap))
    for name,direction in [('elevation',(0,1,0)),('oblique',(1,1,.5)),('plan',(0,0,1))]:
        shaded(items,out/(name+'.svg'),direction,'50-pitch chain hypothesis | source quantity conflict retained')
    link_detail=[i for i in items if i['id'].startswith(('Link00_','Link01_','Joint00_','Joint01_','Joint02_'))]
    shaded(link_detail,out/'link_detail.svg',(1,1,.5),'Chain joint detail | separate bars, bushings, pins and unsplayed cotters')
    report=dict(complete=True,passed=not overlaps,counts=dict(counts),physical_occurrences=len(items),
        contact_candidates=tested,overlaps=overlaps,joint_checks=joint_checks,
        native_sha256=sha(native),authored_fingerprint=lock,
        candidate_inputs={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'chain_parts.py',
            ROOT/'sprocket_geometry.py',ROOT/'chain_candidate_controls.json',ROOT/'installed_pitch_route_report.json']},
        quantity_interpretation=controls['quantity_interpretation'],source_bom_reconciled=False,
        full_installed_tank_interfaces_qualified=False,formed_retention_qualified=False,
        lubrication_qualified=False,continuous_engagement_qualified=False,historical_fit_qualified=False,
        visual_review_status='pending')
    assert fingerprint()==lock
    write(out/'report.json',report)
    print('Chain fixture:',dict(counts),'candidates',tested,'overlaps',len(overlaps),flush=True)
    sys.exit(0 if report['passed'] else 1)
finally:
    runtime.close()
