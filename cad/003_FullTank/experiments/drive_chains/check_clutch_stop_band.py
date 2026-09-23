"""Inspect saved stop-band material, source dimensions, rivet passages and stock."""
import argparse
import math
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;STAGE=HERE.parents[1]
sys.path[:0]=[str(HERE),str(STAGE)]
from lib import runtime
from lib.evidence import read,write,sha
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=HERE/'clutch_stop_band_build');p.add_argument('--worker',action='store_true')
a=p.parse_args();out=a.candidate.resolve()
if not a.worker:
    with (out/'interface_check.log').open('w') as log:
        sys.exit(subprocess.run([sys.executable,__file__,'--candidate',str(out),'--worker'],
            env=runtime.environment(out/'check_runtime'),stdout=log,stderr=subprocess.STDOUT).returncode)
try:
    import FreeCAD as App,Part
    from lib.cad_build import leaves
    native=out/'TransmissionWithClutchStopBand.FCStd';r=read(out/'report.json');nh=sha(native);assert nh==r['native_sha256']
    doc=App.openDocument(str(native));items=leaves(doc.Root);byid={i['id']:i for i in items}
    origin=doc.TransmissionCore.Placement.Base;c=r['controls'];d=r['datums'];checks=[]
    shapes={}
    for name in r['new_ids']+['ClutchDrive_drum','ClutchDrive_belt']:
        s=byid[name]['shape'].copy();s.translate(-origin);shapes[name]=s
    def ck(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    def near(name,actual,expected,tol=1e-6):ck(name,abs(actual-expected)<tol,dict(actual=actual,expected=expected,tolerance=tol))
    def at(shape,p):return shape.isInside(p,1e-7,False)
    def point(x,radius,angle):return App.Vector(x,radius*math.cos(angle),radius*math.sin(angle))
    band=shapes['ClutchStopBand_band'];lining=shapes['ClutchStopBand_lining'];drum=shapes['ClutchDrive_drum']
    ck('1681 distinct physical occurrences',len(items)==len(byid)==1681)
    ck('19 new pieces; anchor and six anchor rivets remain required',len(r['new_ids'])==19 and not d['anchor_present'] and not r['complete_brake'])
    ck('17 rivets use two shared definitions',len({byid[n]['target'].Name for n in r['new_ids'] if 'Rivet' in n})==2)
    ck('band pieces belong to one Drivetrain assembly',all(byid[n]['object'].getParentGeoFeatureGroup()==doc.ClutchStopBandAssembly and byid[n]['object'].Subsystem=='Drivetrain' for n in r['new_ids']))
    ck('saved new shapes valid single solids',all(shapes[n].isValid() and len(shapes[n].Solids)==1 for n in r['new_ids']))
    near('printed lining width',lining.BoundBox.XLength,2*25.4)
    near('strip width matches lining',band.BoundBox.XLength,2*25.4)
    # The actual axial boundary circles retain the full wrap despite head pockets.
    circles=[e for e in lining.Edges if type(e.Curve).__name__=='Circle' and e.Length>500]
    inner=min(e.Curve.Radius for e in circles);outer=max(e.Curve.Radius for e in circles)
    near('printed lining stock',outer-inner,3/16*25.4)
    wrap=min(e.Length/e.Curve.Radius for e in circles)
    near('source cut length from actual lining boundary arcs',(inner+outer)/2*wrap,27.75*25.4)
    near('actual drum to lining clearance',lining.distToShape(drum)[0],c['released_gap'])
    near('no lining/drum overlap',lining.common(drum).Volume,0,1e-5)
    near('no steel/lining overlap',band.common(lining).Volume,0,1e-5)
    ck('lining lies wholly over smooth drum land',lining.BoundBox.XMin>524.25 and lining.BoundBox.XMax<589.)
    for angle in [0,.73,1.57,2.43,3.2]:
        x=c['band_center_x']+5
        ck('printed drum radius material/void '+str(angle),at(drum,point(x,9.25*25.4/2-.02,angle)) and not at(drum,point(x,9.25*25.4/2+.02,angle)))
        ck('lining and steel contact with stock on opposite sides '+str(angle),at(lining,point(x,outer-.05,angle)) and not at(lining,point(x,outer+.05,angle)) and at(band,point(x,outer+.05,angle)))
    opening=math.radians(c['opening_clock_deg'])
    ck('lining has actual opening',not at(lining,point(c['band_center_x'],(inner+outer)/2,opening)))
    # Test the material-free pin bore in both rolled ears, beyond the main band.
    eye=App.Vector(*d['eye_axis_point'])
    for offset in [-20,20]:
        axis=App.Vector(c['band_center_x']+offset,eye.y,eye.z)
        near('rolled ear pin bore '+str(offset),band.common(Part.makeCylinder(c['eye_inside_radius']-.02,1,axis-App.Vector(.5,0,0),App.Vector(1,0,0))).Volume,0,1e-5)
        n=App.Vector(0,math.cos(d['arc_end_rad']),math.sin(d['arc_end_rad']))
        ck('rolled ear outside bore is real material '+str(offset),at(band,axis+n*(c['eye_inside_radius']+c['steel_stock']/2)))
    center_relief=Part.makeCylinder(d['eye_slot_radius']-.02,c['eye_slot_width']-.04,
        eye-App.Vector(c['eye_slot_width']/2-.02,0,0),App.Vector(1,0,0))
    near('central eyebolt relief is open',band.common(center_relief).Volume,0,1e-5)
    # Actual native heads and shanks must occupy receiving voids without cutting
    # through the friction face with unrecessed metal.
    for j in d['rivet_joints']:
        name=j['name'];riv=shapes[name];base=App.Vector(*j['base']);n=App.Vector(*j['radial'])
        p0=base+n*(j['grip']/2)
        ck(name+'/solid shank in real band/lining hole',at(riv,p0) and not at(band,p0) and not at(lining,p0))
        near(name+'/no steel interference',riv.common(band).Volume,0,1e-5)
        near(name+'/no lining interference',riv.common(lining).Volume,0,1e-5)
        near(name+'/no drum interference',riv.common(drum).Volume,0,1e-5)
        radius=c['lining_rivet_diameter']/2 if j['kind']=='lining' else c['fold_rivet_diameter']/2
        # Probe radial shank thickness in local X, which is perpendicular to every rivet.
        ck(name+'/printed shank diameter',at(riv,p0+App.Vector(radius-.01,0,0)) and not at(riv,p0+App.Vector(radius+.01,0,0)))
    # Installed tail volumes are compared to source-sized blanks, independently
    # of the builder's tail-height calculation and against the saved definitions.
    for kind,diameter,length in [('lining',3/16*25.4,.5*25.4),('fold',.25*25.4,.75*25.4)]:
        solid=doc.getObject('Def_ClutchStopBand_'+kind+'_rivet').Shape
        rr=diameter/2
        if kind=='lining':
            head_r=c['lining_rivet_head_radius'];h=head_r-rr
            expected=math.pi*h*(head_r*head_r+head_r*rr+rr*rr)/3+math.pi*rr*rr*(length-h)
        else:
            a=c['fold_rivet_head_radius'];h=c['fold_rivet_head_height']
            expected=math.pi*h*(3*a*a+h*h)/6+math.pi*rr*rr*length
        near(kind+'/installed rivet conserves source blank volume',solid.Volume,expected,1e-5)
    neutral=Part.Shape();neutral.read(str(out/'inputs/lining_neutral.brep'))
    near('retained neutral curve source length',neutral.Length,27.75*25.4)
    ck('return spline fit held-out residual below0.001mm',d['return_profile_max_residual_mm']<.001,d['return_profile_max_residual_mm'])
    # Belt closure uses the actual relocated pump center and the selected pitch
    # convention. The54in catalogue length convention remains explicitly inferred.
    rd=r['receiving_drive'];rp=rd['belt']['pump_pitch_radius'];rr=rd['belt']['drive_pitch_radius']
    distance=doc.AirPressurePump.Placement.Base.z
    alpha=math.asin((rr-rp)/distance)
    length=2*math.sqrt(distance*distance-(rr-rp)**2)+math.pi*(rr+rp)+2*(rr-rp)*alpha
    near('same54in belt closes at saved pump center',length,54*25.4)
    result=dict(passed=all(x['passed'] for x in checks),native_sha256=nh,checker_sha256=sha(Path(__file__)),checks=checks,
        scope='Band,lining,rivets and receiving drive; anchor/linkage, full installation and historical form NOT qualified')
    write(out/'independent_checks.json',result)
    print('Independent checks',len(checks),'failed',[x for x in checks if not x['passed']],flush=True)
    assert result['passed']
finally:
    runtime.close()
