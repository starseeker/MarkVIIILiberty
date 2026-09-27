"""Verify saved station integration, preserved hierarchy/material, metadata and guides."""
import argparse, shutil, tempfile, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from control_rebuild_io_v2 import App, Part, H, ROOT, Saved, read, write, sha
from lib.camera_review import validate_native_bindings
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
s=Saved(a.candidate);r=s.report;out=s.folder;parent=Saved((ROOT/r['source_native']).parent);proto=Saved(ROOT/r['prototype']);plan=read(ROOT/r['plan'])
assert sha(ROOT/r['plan'])==r['plan_sha256'] and all(sha(ROOT/f)==h for f,h in r['input_hashes'].items())
checks=[]
def ck(name,passed,**detail):checks.append(dict(name=name,passed=bool(passed),**detail))
def close(a,b):return len(a)==len(b) and max(abs(x-y) for x,y in zip(a,b))<1e-7
m,old,pm=s.manifest,parent.manifest,proto.manifest
ck('Exact physical union and assembly counts',len(s.rows)==r['expected_physical_occurrences']==3712 and len(m['definitions'])==r['expected_definition_count']==689 and len(m['assemblies'])==r['expected_assembly_count']==456 and set(s.rows)==set(parent.rows)|set(proto.rows) and set(m['definitions'])==set(old['definitions'])|set(pm['definitions']))
ck('All inherited occurrence identities, owners and undeclared world frames preserved',all(s.rows[n]['definition']==v['definition'] and s.rows[n]['owners']==v['owners'] and close(s.rows[n]['frame'],r['expected_changed_occurrences'].get(n,v)['frame']) for n,v in parent.rows.items()))
ck('All prototype world frames and definition references retained',all(s.rows[n]['definition']==v['definition'] and close(s.rows[n]['frame'],v['frame']) for n,v in proto.rows.items()))
ck('New occurrence owners match explicit hierarchy',all(s.rows[n]['owners']==v['owners'] for n,v in r['expected_new_occurrences'].items()))
ck('Inherited assembly children and full local/world frames preserved',all(m['assemblies'][n]['children']==v['children']+r['added_children'].get(n,[]) and close(m['assemblies'][n]['local'],v['local']) and close(m['assemblies'][n]['world'],v['world']) for n,v in old['assemblies'].items()))
ck('New assembly identity and composed frames',set(m['assemblies'])==set(old['assemblies'])|set(r['new_assembly_specs']) and all(m['assemblies'][n]['children']==r['added_children'].get(n,[]) and close(m['assemblies'][n]['world'],v['frame']) for n,v in r['new_assembly_specs'].items()))
ck('Changed shared definitions have complete reviewed occurrence coverage',all(n in proto.rows for n,v in parent.rows.items() if v['definition'] in r['changed_definitions']))
material=[]
def equivalent(key,one,two,label):
    x,y=one.manifest['definitions'][key],two.manifest['definitions'][key]
    for d in [x,y]:assert sha(d['brep_path'])==d['brep_sha256']
    q=dict(definition=key,comparison=label,source_sha256=x['brep_sha256'],target_sha256=y['brep_sha256'])
    if x['brep_sha256']==y['brep_sha256']:q.update(passed=True,method='exact saved BRep bytes')
    else:
        left,right=one.definition(key),two.definition(key);diff=[left.cut(right),right.cut(left)]
        volumes=[sum(abs(v.Volume) for v in z.Solids) for z in diff];fuzzy=[len(left.cut(right,1e-4).Faces),len(right.cut(left,1e-4).Faces)]
        q.update(passed=left.isValid() and right.isValid() and len(left.Solids)==len(right.Solids)==1 and left.Solids[0].isClosed() and right.Solids[0].isClosed() and max(left.getTolerance(1),right.getTolerance(1))<=1e-4 and max(volumes)<1e-5 and not any(fuzzy),method='strict two-way material',difference_mm3=volumes,fuzzy_difference_faces=fuzzy)
    material.append(q);write(out/'material_verification_progress.json',material);return q['passed']
for key in old['definitions']:
    if key not in r['changed_definitions']:equivalent(key,parent,s,'inherited preservation')
proof={v['definition']:v for v in plan['inherited_prototype_material']}
for key in pm['definitions']:
    # Exact saved parent bytes transfer the separately verified source equivalence.
    if key in proof and key in old['definitions'] and m['definitions'][key]['brep_sha256']==old['definitions'][key]['brep_sha256']:
        q=proof[key];assert q['source_sha256']==m['definitions'][key]['brep_sha256'] and q['prototype_sha256']==pm['definitions'][key]['brep_sha256']
        material.append(dict(definition=key,comparison='reviewed prototype transfer',passed=q['passed'],method='exact saved parent bytes plus bound prototype material proof',plan_sha256=r['plan_sha256']))
    else:equivalent(key,proto,s,'reviewed prototype transfer')
ck('Complete inherited definition preservation and reviewed prototype material transfer',all(v['passed'] for v in material),comparisons=len(material),strict=sum(v['method']=='strict two-way material' for v in material))
write(out/'definition_preservation_checks.json',dict(passed=all(v['passed'] for v in material),native_sha256=sha(s.native),source_native_sha256=sha(parent.native),checker_sha256=sha(Path(__file__)),checks=material,definition_count=len(old['definitions'])-len(r['changed_definitions']),intentionally_rebuilt_definitions=r['changed_definitions']))
with tempfile.TemporaryDirectory(prefix='relocation_',dir=out) as work:
    relocated=Path(work)/s.native.name;shutil.copy2(s.native,relocated)
    validate_native_bindings(dict(native_file=str(relocated),render_occurrences=list(s.rows),landmarks=[]),m)
    doc=App.openDocument(str(relocated))
    try:
        ck('Native relocation: all physical links are internal and definitions identity-frame',all(doc.getObject(v['object']).LinkedObject.Document==doc and doc.getObject(v['object']).LinkedObject.Placement.isIdentity() for v in s.rows.values()))
        for key,expected in plan['metadata'].items():
            obj=doc.getObject(key);actual={k:getattr(obj,k) for k in obj.PropertiesList if obj.getGroupOfProperty(k)=='Reconstruction'}
            ck(key+' full reconstruction metadata restored',actual==expected)
        physicalobjects={v['object'] for v in s.rows.values()}|set(m['definitions'])|set(m['assemblies'])
        for source in sorted({v['source_native'] for v in r['nonphysical_guides'].values()}):
            original=App.openDocument(str(ROOT/source))
            try:
                for name,v in r['nonphysical_guides'].items():
                    if v['source_native']!=source:continue
                    assert sha(ROOT/source)==v['source_native_sha256']
                    x,y=original.getObject(v['source_object']),doc.getObject(name)
                    assert x and y
                    f1,f2=Path(work)/'source.brep',Path(work)/'target.brep';x.Shape.exportBrep(str(f1));y.Shape.exportBrep(str(f2))
                    props={k:getattr(y,k) for k in y.PropertiesList if y.getGroupOfProperty(k)=='Reconstruction'}
                    ck(name+' complete curve retained outside physical hierarchy',sha(f1)==sha(f2) and not y.Shape.Solids and name not in physicalobjects and y in doc.getObject(v['group']).Group and props==v['properties'])
            finally:App.closeDocument(original.Name)
    finally:App.closeDocument(doc.Name)

def xml(path):
    with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('Document.xml'))
    return ({o.get('name'):o.get('type') for o in root.findall('Objects/Object')},{(o.get('name'),p.get('name')):p for o in root.findall('ObjectData/Object') for p in o.findall('Properties/Property')})
ot,op=xml(parent.native);nt,np=xml(s.native)
ck('All inherited object types preserved',all(nt.get(n)==t for n,t in ot.items()))
def numeric_equal(a,b):
    if a.tag!=b.tag or a.attrib.keys()!=b.attrib.keys() or len(a)!=len(b):return False
    for k,v in a.attrib.items():
        if v==b.get(k):continue
        try:
            if abs(float(v)-float(b.get(k)))>1e-12:return False
        except ValueError:return False
    return all(numeric_equal(x,y) for x,y in zip(a,b))
tips={op[(k,'Tip')].find('Link').get('value') for k in r['changed_definitions']}
changes=[]
for key,before in op.items():
    after=np.get(key)
    if after is not None and ET.tostring(before)==ET.tostring(after):continue
    name,prop=key;ok=False;reason='Unexpected inherited change'
    if after is not None:
        if prop=='Group' and name in r['added_children']:
            ok=[x.get('value') for x in after.findall('LinkList/Link')]==[x.get('value') for x in before.findall('LinkList/Link')]+r['added_children'][name];reason='Declared appended children'
        elif name=='Root' and prop in ['Label','RegistrationStatus']:ok=True;reason='Checkpoint description'
        elif name in tips and prop=='Shape':
            x,y=before.find('Part'),after.find('Part');ok=before.attrib==after.attrib and x is not None and y is not None and x.get('file')==y.get('file') and all(v.tag in ['Part','ElementMap','ElementMap2'] for v in after);reason='Declared tip geometry, independently verified'
        elif name in r['expected_changed_occurrences'] and prop in ['Placement','LinkPlacement']:ok=True;reason='Independently composed reviewed world frame'
        elif name in r['changed_definitions'] and prop in plan['metadata'][name]:ok=True;reason='Full native metadata matched above to original packets'
        elif prop in ['Geometry','Placement','LinkPlacement']:ok=numeric_equal(before,after);reason='Numeric serialization within1e-12, identical XML structure'
    changes.append(dict(object=name,property=prop,passed=ok,reason=reason))
newprops={key for key in np if key[0] in ot and key not in op}
allowed={(k,prop) for k in r['changed_definitions'] for prop in plan['metadata'][k] if (k,prop) not in op}
ck('Every inherited persistent property preserved except explicit changes',all(v['passed'] for v in changes) and newprops==allowed,changed=changes,new_properties=sorted(newprops),expected_new_properties=sorted(allowed),compared=len(op))
# Reconstruct exactly the union used by the original context audit. This transfers
# collision evidence only after every candidate part and unaffected parent is bound.
standard=read(H/'transmission_brake_front_study/trial01/standard_context_manifest.json')
assert all(sha(ROOT/f)==h for f,h in standard['native_files'].items())
sm={v['name']:v for v in standard['occurrences'] if v['representation']=='assembly'}
replacement=set(s.rows)&set(sm)
context_names=set(s.rows)|{'standard:'+n for n in sm if n not in s.rows and n not in {'PortPinion_Rotor_Casting','StarboardPinion_Rotor_Casting'}}
audit=read(proto.folder/'context_audit/report.json')
ck('Full physical context union preserved without duplicate bow or floor panels',audit['passed'] and audit['no_mating_pair_exemptions'] and not audit['findings'] and audit['context_occurrences']==len(context_names) and replacement==set(r['standard_replaced_occurrences']) and len(r['new_tank_parts'])==92 and len(r['new_development_context'])==38,context_occurrences=len(context_names),transferred_pairs=len(audit['pairs']),standard_replacements=sorted(replacement))
receipts=['checks01/independent_checks.json','mount_material03/report.json','delta_checks.json','context_audit/report.json','exchange01/exchange_checks.json','reproduction_checks.json']
for f in receipts:
    q=read(proto.folder/f);ck('Transferred bound local qualification '+f,q['passed'] and q['native_sha256']==sha(proto.native))
result=dict(passed=all(v['passed'] for v in checks),native_sha256=sha(s.native),source_native_sha256=sha(parent.native),prototype_native_sha256=sha(proto.native),checker_sha256=sha(Path(__file__)),checks=checks,transferred_receipts={f:sha(proto.folder/f) for f in receipts},scope='Complete saved union, hierarchy/frames, inherited material and persistent properties, restored source metadata, nonphysical guides, and exact full-context transfer. No new whole-assembly STEP export claimed.',historical_geometry_qualified=False,installation_qualified=False)
write(out/'independent_checks.json',result)
for v in checks:
    if not v['passed']:print(v,flush=True)
print('INTEGRATION',len(checks),'checks',result['passed'],flush=True)
assert result['passed']
