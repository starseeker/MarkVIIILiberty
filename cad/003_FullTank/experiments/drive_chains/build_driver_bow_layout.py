"""Save a coupled bow/driver hypothesis with complete rods and actual mounts."""
import argparse
import copy
from pathlib import Path
from control_rebuild_io_v2 import *
from driver_layout_trial_parts import layout
from driver_folded_floor_support import support

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--main-z',type=float,default=975.)
a=p.parse_args();parent=Saved(C/'driver_redo01/operating_integrated01')
bow=H/'bow_reconstruction_study/trial02';br=read(bow/'report.json');bn=bow/br['native_file'];assert sha(bn)==br['native_sha256']
shapes,specs,props,details=layout(parent,a.main_z)
changed=['Def_DriverClutchFrontRod_M576']
props[changed[0]]=dict(props[changed[0]],ReconstructionStatus='Unprinted common M576 stock regenerated for the explicit driver height hypothesis; three physical applications share one definition.',ParameterUpdate='Regenerate build_driver_bow_layout.py with the recorded main-z setting.')
doc=App.openDocument(str(bn));bow_names=[]
for name,row in br['occurrences'].items():
    if not row['candidate']:continue
    link=doc.getObject(name);shape=link.LinkedObject.Shape.copy()
    if name in ['hull_floor_1','hull_floor_2']:
        key=parent.rows[name]['definition'];changed.append(key)
    else:key='Def_BowLayout_'+name
    shapes[key]=shape;props[key]=dict(SourceRecords=link.LinkedObject.SourceRecords,
        SourceDefinition=name,Representation='reconstruction_trial',ReconstructionStatus='Conditional inclusive-length bow reconstruction, with explicit driver mounting holes where applicable. M2014 and seam identities remain unresolved.',ParameterUpdate='Regenerate build_driver_bow_layout.py; bow_reconstruction_study/trial02 is the geometric source.')
    specs[name]=dict(definition=key,frame=row['frame'],owner='BowEnclosure' if name.startswith('upper_') else 'BowShell',role='bow_plate')
    bow_names.append(name)
App.closeDocument(doc.Name)
foundation=copy.deepcopy(parent.report['details']['foundation']);main=App.Vector(*details['main_world_mm']);rear=App.Vector(*details['swing_world_mm'])
mounts=[];supports={}
oldmounts={m['stem']:m for m in foundation['mounts']}
for side,hand in [('Port',1),('Starboard',-1)]:
    name='Driver'+side+'SupportPlate';key=parent.rows[name]['definition']
    shape,placement,mm,record=support(br,foundation['controls'],main,rear,hand)
    shapes[key]=shape;changed.append(key)
    props[key]=dict(parent.manifest['definitions'][key]['properties'],ReconstructionStatus='Estimated folded-foot support on the actual corrected two-plane floor, with full shaft bores and four mounting bores. Stock and existing hardware retained.',ParameterUpdate='Regenerate build_driver_bow_layout.py; main-z remains an unprinted reconstruction hypothesis.')
    specs[name]=dict(definition=key,frame=list(placement.toMatrix().A),owner='DriverSupports',role='support')
    supports[side]=record
    for i,m in enumerate(mm,1):
        stem='Driver'+side+'SupportMount'+str(i);old=oldmounts[stem]
        p0=App.Vector(*old['floor_contact_world_mm']);p1=App.Vector(*m['contact_world_mm'])
        normal=App.Vector(*m['normal_world']);oldnormal=App.Vector(*foundation['floor_normal'])
        rotation=App.Rotation(oldnormal,normal)
        for suffix in ['Bolt','Lock','Nut']:
            n=stem+suffix;row=parent.rows[n];k=row['definition']
            if k not in shapes:shapes[k]=parent.definition(k);props[k]=parent.manifest['definitions'][k]['properties']
            oldframe=pose(row['frame']);new=App.Placement(p1+rotation.multVec(oldframe.Base-p0),rotation.multiply(oldframe.Rotation))
            specs[n]=dict(definition=k,frame=list(new.toMatrix().A),owner='DriverSupports',role='mount_'+suffix.lower())
        floor_key=specs[m['floor']]['definition']
        shapes[floor_key]=shapes[floor_key].cut(Part.makeCylinder(6.5,30,p1+normal*10,-normal)).removeSplitter()
        mounts.append(dict(stem=stem,plate=name,**m))
# Include the actual fixed receiving eyes and the first retained flat floor.
receivers={'hull_floor_3'}
for rec in parent.report['details']['low_speed'].values():receivers.add(rec['endpoints'][0]['receiver'])
receivers.add(parent.report['details']['rods']['Front']['endpoints'][0]['receiver'])
for rec in parent.report['details']['high_controls'].values():receivers.add(rec['rods']['Front']['endpoints'][0]['receiver'])
for name in sorted(receivers):
    row=parent.rows[name];key=row['definition']
    if key not in shapes:shapes[key]=parent.definition(key);props[key]=parent.manifest['definitions'][key]['properties']
    specs[name]=dict(definition=key,frame=row['frame'],owner='RetainedReceivers',role='receiver')
details.update(supports=supports,mounts=mounts,bow_source=str(bow.relative_to(ROOT)),bow_native_sha256=sha(bn),
    bow_occurrences=bow_names,source_camera_refitted=False,
    hypothesis_note='Main height selected from a tested feasible sample, not a printed historical dimension. Relative driver state is preserved, M574 and short rods keep full printed stock. Full context/source qualification is still required.',
    missing_rear_rods_correction='M575/M578/M573 were already present; all rear/intermediate geometry is retained.')
inputs=[Path(__file__),H/'driver_layout_trial_parts.py',H/'driver_folded_floor_support.py',H/'bow_reconstruction_parts.py',
        bow/'report.json',bow/'checks01/report.json',H/'driver_layout_study/probe01/report.json',
        parent.folder/'report.json',parent.folder/'isolated/manifest.json',parent.folder/'qualification.json']
trial(a.output,parent,shapes,specs,props,details,inputs,changed_definitions=changed)
print('Saved coupled layout:',len(specs),'occurrences;',len(shapes),'definitions; main Z',a.main_z,flush=True)
