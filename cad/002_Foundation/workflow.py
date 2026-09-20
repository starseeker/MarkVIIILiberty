"""Worker process launched with the installed FreeCAD runtime."""
import copy
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

from evidence import HERE, REPO, SURVEY, arithmetic, database, fingerprint, load_data, read, sha, source_check, write


def cad():
    import FreeCAD as App
    import Part
    import Sketcher
    import _PartDesign
    import AssemblyApp
    if App.Version()[:3]!=['1','1','1']:
        raise ValueError('FreeCAD version changed from tested 1.1.1. Requalify the runtime before updating this gate.')
    return App,Part


def gui():
    App,_=cad()
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('SaveThumbnail',False)
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    import FreeCADGui as Gui
    Gui.showMainWindow()
    Gui.getMainWindow().hide()
    return Gui


def capability(out):
    App,Part=cad()
    import Sketcher
    import Import
    from geometry import annulus
    d=App.newDocument('CapabilityCheck')
    b=d.addObject('PartDesign::Body','Cylinder')
    pad=annulus(b,'Pad',5,0,0,20);pad.Length=25;d.recompute()
    assert pad.Shape.isValid() and abs(pad.Shape.Volume-math.pi*25*25)<1e-7
    assert d.PadProfile.FullyConstrained
    cut=pad.Shape.cut(Part.makeCylinder(2,25,App.Vector(),App.Vector(0,1,0)))
    nurbs=cut.toNurbs();assert nurbs.isValid() and len(nurbs.Solids)==1
    surface=Part.BSplineSurface()
    surface.interpolate([[App.Vector(i*10,j*10,i*j) for j in range(4)] for i in range(4)])
    assert surface.toShape().isValid()
    root=d.addObject('Assembly::AssemblyObject','Assembly');sub=d.addObject('App::Part','Subassembly');root.addObject(sub)
    for i in range(2):
        link=d.addObject('App::Link','Instance'+str(i));link.setLink(b);sub.addObject(link)
        link.LinkPlacement.Base=App.Vector(30*i,0,0)
    d.recompute()
    folder=out/'capability';folder.mkdir(parents=True,exist_ok=True)
    d.saveAs(str(folder/'probe.FCStd'));Import.export([root],str(folder/'probe.step'))
    App.closeDocument(d.Name);d=App.openDocument(str(folder/'probe.FCStd'));d.recompute()
    assert d.Instance1.LinkedObject==d.Cylinder and len(d.Subassembly.Group)==2
    s=Part.Shape();s.read(str(folder/'probe.step'))
    assert s.isValid() and len(s.Solids)==2 and abs(s.Volume-2*math.pi*25*25)<1e-5
    App.closeDocument(d.Name)
    return {'passed':True,'native_features':True,'constrained_sketch':True,'parameter_recompute':True,
            'nurbs_solid_and_surface':True,'assembly_links':True,'fcstd_and_step_roundtrip':True,
            'FreeCAD':App.Version(),'OpenCASCADE':Part.OCC_VERSION,
            'runtime':os.environ.get('MARKVIII_RESOLVED_FREECAD')}


def check(data,out):
    import fitz
    import numpy
    import scipy
    import PIL
    result=source_check(data)
    result.update({'PyMuPDF':fitz.VersionBind,'NumPy':numpy.__version__,'SciPy':scipy.__version__,'Pillow':PIL.__version__})
    result['capability']=capability(out)
    write(out/'reports/environment.json',result)
    return result


def signature(doc):
    from geometry import leaves
    result={}
    for name,s,obj in leaves(doc):
        b=s.optimalBoundingBox(False)
        result[name]={'solids':len(s.Solids),'volume_mm3':s.Volume,
                      'bounds_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                      'survey_id':obj.SurveyId,'part_file':Path(obj.LinkedObject.Document.FileName).name}
    return result


def close_all():
    App,_=cad()
    for name in list(App.listDocuments()):App.closeDocument(name)


def open_pilot(out):
    App,_=cad()
    path=out/'native/MarkVIII_Pilot.FCStd'
    if not path.is_file():raise ValueError('Build is missing. Run manage.py build first.')
    close_all();doc=App.openDocument(str(path));doc.recompute()
    if not hasattr(doc,'Root'):raise ValueError('Native pilot root is missing.')
    return doc


def check_build_inputs(out,directory):
    manifest=read(out/'reports/build.json')
    if manifest['data_hashes']!=fingerprint(directory):
        raise ValueError('Model inputs changed since build. Run build before validate/export.')
    if manifest['code_hashes']!={p.name:sha(p) for p in sorted(HERE.glob('*.py'))}:
        raise ValueError('Model code changed since build. Run build before validate/export.')


def build(data,out,directory):
    import calibration
    import geometry
    check(data,out)
    calibration.run(data,out)
    gui()
    App,_=cad()
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetInt('CountBackupFiles',0)
    App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('SaveThumbnail',False)
    doc=geometry.build(data,out)
    sig=signature(doc)
    write(out/'reports/build.json',{'configuration':data['model']['configuration'],
          'data_hashes':fingerprint(directory),'code_hashes':{p.name:sha(p) for p in sorted(HERE.glob('*.py'))},
          'physical_occurrences':len(sig),'geometry':sig,'FreeCAD':App.Version()})
    return doc


def export(data,out,directory):
    import Import
    import geometry
    from preview import render,exact_projection
    App,Part=cad()
    check_build_inputs(out,directory)
    doc=open_pilot(out)
    folder=out/'exports';folder.mkdir(parents=True,exist_ok=True)
    physical=geometry.leaves(doc)
    # Native root also includes reference shapes: export a separate physical-only hierarchy.
    edoc=App.newDocument('PhysicalExport')
    export_root=edoc.addObject('App::Part','PhysicalPilot')
    groups={'Root':export_root}
    shapes={name:shape for name,shape,obj in physical}
    for item in data['model']['occurrences']:
        if item['part']:
            o=edoc.addObject('PartDesign::Feature',item['id']);o.Shape=shapes[item['id']]
        else:o=edoc.addObject('App::Part',item['id'])
        groups[item['parent']].addObject(o);groups[item['id']]=o
    edoc.recompute()
    Import.export([export_root],str(folder/'MarkVIII_PhysicalPilot.step'))
    checks={}
    allshape=Part.makeCompound([s for n,s,o in physical])
    for key in data['model']['parts']:
        linked=next(o.LinkedObject for n,s,o in physical if o.LinkedObject.Name==key)
        Import.export([linked],str(folder/(key+'.step')))
        restored=Part.Shape();restored.read(str(folder/(key+'.step')))
        checks[key]=compare_shape(linked.Shape,restored)
    restored=Part.Shape();restored.read(str(folder/'MarkVIII_PhysicalPilot.step'))
    checks['assembly']=compare_shape(allshape,restored)
    if not all(checks.values()):raise ValueError('STEP round-trip mismatch: '+str(checks))
    # Verify hierarchy survives STEP import (constraints/history are not promised in STEP).
    stepdoc=App.newDocument('ImportedSTEP');Import.insert(str(folder/'MarkVIII_PhysicalPilot.step'),stepdoc.Name)
    groups_imported=[o.Label for o in stepdoc.Objects if o.TypeId=='App::Part']
    checks['step_hierarchy']=len(groups_imported)>=3
    if not checks['step_hierarchy']:
        raise ValueError('STEP import lost the physical assembly hierarchy.')
    write(out/'reports/export.json',{'roundtrip':checks,'step_groups':groups_imported,
          'computational_tolerances':{'relative_volume':1e-6,'bounds_mm':1e-5},'reference_objects_exported':0})
    App.closeDocument(stepdoc.Name);App.closeDocument(edoc.Name)
    items=[(n,s,False) for n,s,o in physical]
    references=[(o.Name,o.Shape,True) for o in doc.ReferenceGeometry.Group]
    previews=out/'previews';previews.mkdir(exist_ok=True)
    for name,direction in [('isometric',(1,-1,0.65)),('side',(0,-1,0)),('front',(1,0,0)),('top',(0,0,1))]:
        render(items+references,previews/(name+'.svg'),direction,'Mark VIII | Rock Island production pilot')
    detail=[(n,s,False) for n,s,o in physical if n.startswith('Port')]
    render(detail,previews/'running_gear.svg',(1,-1,0.8),'Track shoe segment and rotating roller unit')
    joint=[(n,s,False) for n,s,o in physical if n in ['SupportAngle','SupportPlate','JointFastener1','JointFastener2']]
    render(joint,previews/'support_joint.svg',(1,1,0.7),'Support No.1 | provisional local joint coupon')
    exact_projection(Part.makeCompound([s for n,s,r in detail]),previews/'running_gear_exact.svg',(1,-1,0.8))
    exact_projection(Part.makeCompound([s for n,s,r in joint]),previews/'support_joint_exact.svg',(1,1,0.7))
    write_delivery(data,out)
    return checks


def compare_shape(a,b):
    if b.isNull() or not b.isValid() or len(a.Solids)!=len(b.Solids):return False
    if abs(a.Volume-b.Volume)>max(1e-5,abs(a.Volume)*1e-6):return False
    ab,bb=a.optimalBoundingBox(False),b.optimalBoundingBox(False)
    return all(abs(getattr(ab,k)-getattr(bb,k))<=1e-5
               for k in ['XMin','YMin','ZMin','XMax','YMax','ZMax'])


def write_delivery(data,out):
    rows=['# Mark VIII — foundation and pilot', '',
          'Open `native/MarkVIII_Pilot.FCStd`. Keep all native files together when relocating.',
          'Scripts and authored records are authoritative. Transfer GUI experiments back before rebuilding.', '',
          '![Pilot](previews/isometric.png)', '',
          '## Physical pilot', '',data['model']['physical_scope'],'',
          'STEP exports include physical pilot parts only. Blue-grey reference envelopes and track guides are excluded.', '',
          '![Running gear](previews/running_gear.png)', '',
          '![Joint](previews/support_joint.png)', '',
          '## Evidence and limitations','',
          'Handbook dimensions are provisionally transferred to the Rock Island production baseline.',
          'Photographic Plates 1, 3, 4, 10 remain visual-only. See [calibration checks](calibration/README.md).','']
    for key,item in data['issues'].items():rows.append(f'- **{key}:** {item["summary"]}')
    rows+=['','## Parameters','','| Parameter | CAD mm | Status | Bounds mm | Evidence |','|---|---:|---|---|---|']
    for k,p in data['parameters'].items():rows.append(f'| {k} | {data["values"][k]:.4f} | {p["status"]} | {p["bounds_mm"]} | {", ".join(p["evidence"])} |')
    (out/'README.md').write_text('\n'.join(rows)+'\n')
    paths=[]
    for folder in ['native','exports','previews','reports','calibration']:
        paths.extend(p for p in (out/folder).rglob('*') if p.is_file())
    write(out/'delivery_manifest.json',{'configuration':data['model']['configuration'],
          'files':{str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)},
          'note':'Generated artifacts, not a manufacturing release. Native paths are relative; keep native directory intact.'})


def original_survey_checks(out):
    folder=out/'verification/survey'
    for rel in ['mark_viii_parts.sqlite','inputs/snl_rows.json','inputs/hb_rows.json','scripts/validate_database.py']:
        dst=folder/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SURVEY/rel,dst)
    (folder/'reports').mkdir(exist_ok=True)
    p=subprocess.run([sys.executable,str(folder/'scripts/validate_database.py')],capture_output=True,text=True)
    if p.returncode:raise ValueError('Original survey validation failed: '+p.stdout+p.stderr)
    report=read(folder/'reports/validation.json')
    assert report['all_passed'] and len(report['checks'])==27
    return {'passed':True,'checks':27}


def validate(data,out,directory):
    import geometry
    App,Part=cad()
    check_build_inputs(out,directory)
    report={'survey':original_survey_checks(out)}
    doc=open_pilot(out);baseline=signature(doc)
    physical=geometry.leaves(doc)
    assert len(physical)==32, f'Unexpected pilot leaf count {len(physical)}'
    report['valid_solids']=all(s.isValid() and s.Volume>0 and len(s.Solids)==1 for n,s,o in physical)
    report['source_ids_and_links']=all(o.SurveyId==data['model']['parts'][next(x['part'] for x in data['model']['occurrences'] if x['id']==n)]['survey_id'] or
                                     (o.SurveyId=='' and o.LinkedObject.SurveyId=='') for n,s,o in physical)
    for n,s,o in physical:
        assert not o.ReferenceOnly and o.LinkedObject is not None
    # Contact and overlap classification operates on actual placed solids.
    overlaps=[];contacts=[]
    for i,(n,a,o) in enumerate(physical):
        for m,b,other in physical[i+1:]:
            if a.BoundBox.intersect(b.BoundBox):
                volume=a.common(b).Volume
                if volume>1e-4:overlaps.append({'a':n,'b':m,'volume_mm3':volume})
            if a.distToShape(b)[0]<1e-5:contacts.append([n,m])
    report['interference']={'unintended_overlaps':overlaps,'contacts':contacts}
    assert not overlaps,'Unintended pilot interference: '+str(overlaps)
    # Relocation must resolve every linked source from the copied directory.
    relocation=out/'verification/relocated';relocation.mkdir(parents=True,exist_ok=True)
    shutil.copytree(out/'native',relocation/'native',dirs_exist_ok=True)
    relocated=open_pilot(relocation)
    assert signatures_equal(baseline,signature(relocated))
    for n,s,o in geometry.leaves(relocated):
        assert Path(o.LinkedObject.Document.FileName).parent==relocation/'native','Link did not relocate: '+n
    report['relocated_native_links']=True
    close_all()
    # Equivalent rebuild in a separate directory; compare geometry rather than ZIP timestamps.
    gui();rebuild=out/'verification/rebuild'
    rebuilt=geometry.build(data,rebuild)
    assert signatures_equal(baseline,signature(rebuilt))
    report['reproducible_geometry']=True
    # Real parameter-change rebuild checks all repeated occurrences and the joint plate.
    changed=copy.deepcopy(data)
    changed['values']['plate_thickness']+=1
    changed['values']['shoe_pitch']+=0.5
    amended=geometry.build(changed,out/'verification/changed');after=signature(amended)
    shoe_names=[n for n in baseline if 'Shoe' in n and n.endswith('Plate')]
    assert len(shoe_names)==6
    for n in shoe_names:
        old=baseline[n]['bounds_mm'];new=after[n]['bounds_mm']
        assert abs((new[3]-new[0])-(old[3]-old[0])-0.5)<1e-5
    assert after['SupportPlate']['volume_mm3']>baseline['SupportPlate']['volume_mm3']
    report['parameter_rebuild_all_instances']=True
    # Check a native expression update propagates through external links without regeneration.
    shoe=amended.PortShoe1Plate.LinkedObject
    before=amended.PortShoe1Plate.Shape.BoundBox.YLength
    shoe.Document.Parameters.shoe_width=float(shoe.Document.Parameters.shoe_width)+1
    shoe.Document.recompute();amended.recompute()
    assert abs(amended.PortShoe1Plate.Shape.BoundBox.YLength-before-1)<1e-5
    assert abs(amended.StarboardShoe3Plate.Shape.BoundBox.YLength-before-1)<1e-5
    report['native_expression_update']=True
    close_all()
    # Negative cases exercise real readers, not a second implementation of validation.
    neg=out/'verification/negative_data';shutil.copytree(directory,neg,dirs_exist_ok=True)
    p=read(neg/'parameters.json');p['shoe_pitch']['blocked']=True;write(neg/'parameters.json',p)
    try:load_data(neg)
    except ValueError as e:assert 'conflict' in str(e)
    else:raise AssertionError('Blocked parameter accepted')
    missing=copy.deepcopy(data);missing['sources']['required']['references/DOES_NOT_EXIST']='0'*64
    try:source_check(missing)
    except ValueError as e:assert 'Missing source' in str(e)
    else:raise AssertionError('Missing source accepted')
    report['negative_source_and_conflict_checks']=True
    # A missing dependency is detected from the delivery manifest before opening FreeCAD.
    missing_folder=out/'verification/missing_link';shutil.copytree(out/'native',missing_folder,dirs_exist_ok=True)
    (missing_folder/'shoe.FCStd').unlink()
    assert missing_native(missing_folder,data)==['shoe.FCStd']
    report['missing_link_diagnostic']=True
    source_check(data)
    report['frozen_sources_unchanged']=True
    report['all_passed']=report['valid_solids'] and report['source_ids_and_links']
    assert report['all_passed']
    export(data,out,directory)
    write(out/'reports/validation.json',report)
    write_delivery(data,out)
    return report


def missing_native(folder,data):
    return [k+'.FCStd' for k in data['model']['parts'] if not (folder/(k+'.FCStd')).is_file()]


def signatures_equal(a,b):
    if a.keys()!=b.keys():return False
    for key in a:
        if a[key]['solids']!=b[key]['solids'] or a[key]['part_file']!=b[key]['part_file']:return False
        if not math.isclose(a[key]['volume_mm3'],b[key]['volume_mm3'],rel_tol=1e-9,abs_tol=1e-5):return False
        if any(abs(x-y)>1e-5 for x,y in zip(a[key]['bounds_mm'],b[key]['bounds_mm'])):return False
    return True


def main():
    command,out,directory=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3])
    try:
        data=load_data(directory);source_check(data)
        obsolete = {'build': ['reports/build.json', 'reports/validation.json', 'reports/export.json', 'delivery_manifest.json'],
                    'validate': ['reports/validation.json', 'delivery_manifest.json'],
                    'export': ['reports/export.json', 'delivery_manifest.json']}
        for name in obsolete.get(command, []):
            (out/name).unlink(missing_ok=True)
        if command=='check':result=check(data,out)
        elif command=='calibrate':
            import calibration
            result=calibration.run(data,out)
        elif command=='build':
            doc=build(data,out,directory);result={'native_file':doc.FileName,'physical_occurrences':len(signature(doc))}
        else:
            missing=missing_native(out/'native',data)
            if missing:raise ValueError('Missing linked native documents: '+', '.join(missing)+'. Run build.')
            result=validate(data,out,directory) if command=='validate' else export(data,out,directory)
        print(json.dumps({'command':command,'success':True,'output':str(out),'result':result},indent=2))
        return 0
    except Exception as e:
        print(f'{command} failed: {e}',file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        # Tear down Qt views while Python callbacks are still alive. Leaving hidden
        # Inventor views to process-exit destruction can crash the packaged GUI.
        if 'FreeCAD' in sys.modules:
            App=sys.modules['FreeCAD']
            for name in list(App.listDocuments()):
                App.closeDocument(name)
            if App.GuiUp:
                import FreeCADGui as Gui
                from PySide6 import QtCore, QtWidgets
                QtWidgets.QApplication.processEvents()
                Gui.getMainWindow().deleteLater()
                QtCore.QCoreApplication.sendPostedEvents(None,QtCore.QEvent.DeferredDelete)


if __name__=='__main__':sys.exit(main())
