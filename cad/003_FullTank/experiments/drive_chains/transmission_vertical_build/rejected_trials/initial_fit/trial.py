import sys,json,subprocess
from pathlib import Path
repo=Path(__file__).resolve().parents[2];stage=repo/'cad/003_FullTank';root=stage/'experiments/drive_chains'
sys.path[:0]=[str(stage),str(root)];from lib import runtime
out=Path(__file__).resolve().parent
if '--worker' not in sys.argv:
    with (out/'trial.log').open('w') as f:sys.exit(subprocess.run([sys.executable,__file__,'--worker'],env=runtime.environment(out),stdout=f,stderr=subprocess.STDOUT).returncode)
try:
    App,Gui=runtime.start_gui();import Part
    from types import SimpleNamespace
    from lib.cad_build import leaves,COLORS
    from lib.evidence import read,write
    from lib.visual_review import shaded
    from transmission_vertical_parts import vertical_parts
    doc=App.openDocument(str(root/'transmission_reversing_build/TransmissionReversingCandidate.FCStd'));doc.recompute()
    old={i['id']:i for i in leaves(doc.Root)};c=read(root/'transmission_vertical_controls.json')['controls']
    shapes,d=vertical_parts(c,*[old[n]['target'].Shape for n in ['CenterTransmissionCore_bevel_case','ReversingControl_rod']])
    instances={k:v for k,v in shapes.items() if k in ['case','rod','shaft','upper_lever','lower_lever']};x,y=c['shaft_xy']
    for n,loc in enumerate(d['key_locations']):
        s=shapes['key'].copy();s.rotate(App.Vector(),App.Vector(0,0,1),loc['angle']);s.translate(App.Vector(x,y,loc['z']));instances['key'+str(n)]=s
    for label,z,flip in [('Upper',c['upper_bearing_base_z'],False),('Lower',c['lower_bearing_open_z'],True)]:
        s=shapes['bearing'].copy()
        if flip:s.rotate(App.Vector(),App.Vector(1,0,0),180)
        s.translate(App.Vector(x,y,z));instances[label+'_bearing']=s
    for row in d['mounts']:
        name=row['label']+'_'+row['kind'];s=shapes[row['kind']].copy();s.translate(App.Vector(row['fastener_base_x'],row['y'],row['z']));instances[name]=s
        for role,oldname,xx in [('nut','PortBrakeBearing_nut0',c['nut_seat_x']),('cotter','InputInstallation_mount_cotter0',d['cotter_axis_x_mm'])]:
            s=old[oldname]['target'].Shape.copy();s.rotate(App.Vector(),App.Vector(0,0,1),180);s.translate(App.Vector(xx,row['y'],row['z']));instances[name+'_'+role]=s
    origin=doc.TransmissionCore.Placement.Base
    others={n:i['shape'].copy() for n,i in old.items() if n not in ['CenterTransmissionCore_bevel_case','ReversingControl_rod']}
    for s in others.values():s.translate(-origin)
    parts=dict(others,**instances);pairs=set();overlaps=[]
    for name,s in instances.items():
        for other,t in parts.items():
            pair=tuple(sorted([name,other]))
            if name==other or pair in pairs or not s.BoundBox.intersect(t.BoundBox):continue
            pairs.add(pair);v=s.common(t).Volume
            if v>1e-5:overlaps.append(dict(a=name,b=other,volume=v));print(overlaps[-1],flush=True)
        print(name,'done',flush=True)
    write(out/'trial.json',dict(dimensions=d,pairs=len(pairs),overlaps=overlaps,volumes={k:s.Volume for k,s in instances.items()}))
    for k,s in instances.items():s.exportBrep(str(out/(k+'.brep')))
    COLORS.update(Control=(.72,.48,.24),Support=(.45,.56,.48),Hardware=(.6,.63,.67))
    items=[dict(id=k,shape=s,target=SimpleNamespace(Shape=s),definition=k,system='Support' if 'bearing' in k else 'Control',representation='assembly') for k,s in instances.items() if k!='case']
    shaded(items,out/'trial.svg',(-1,-1,1),'Vertical reversing controls | fitted bearings, keyed levers and distinct bolt/stud sets')
    write(out/'trial_done.json',dict(passed=not overlaps));print('done',flush=True)
finally:runtime.close()
