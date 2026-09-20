"""Audit installed source identities in a saved standalone casing fixture.

This reads native link ownership, not geometry. The separately bound native
probe report supplies geometry evidence; source quantity conflicts stay open.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(folder):
    native=folder/'CasingSupportCandidate.FCStd'
    report_path=folder/'report.json';report=json.loads(report_path.read_text())
    assert report['passed'] and report['rendering_complete'] and report['native_sha256']==sha(native)
    with zipfile.ZipFile(native) as archive:document=ET.fromstring(archive.read('Document.xml'))
    objects={o.attrib['name']:o for o in document.find('ObjectData')}
    installed=[]
    def string(obj,key):
        value=obj.find('./Properties/Property[@name="'+key+'"]/String')
        return value.attrib['value'] if value is not None else ''
    def walk(name,stack=()):
        if name in stack:raise ValueError('Cyclic native ownership '+name)
        obj=objects[name];link=obj.find('./Properties/Property[@name="LinkedObject"]/XLink')
        if link is not None:
            assert not link.attrib['file'], 'External links need a different audit'
            target=objects[link.attrib['name']]
            if string(target,'DefinitionId'):
                installed.append(dict(occurrence=string(obj,'OccurrenceId'),definition=string(target,'DefinitionId'),
                                      survey_ids=json.loads(string(target,'SurveyIds'))))
                return
            walk(link.attrib['name'],stack+(name,));return
        for child in obj.findall('./Properties/Property[@name="Group"]/LinkList/Link'):
            walk(child.attrib['value'],stack+(name,))
    walk('Root')
    assert len(installed)==report['fixture_occurrences']
    assert len({i['occurrence'] for i in installed})==len(installed)
    parts=json.loads((ROOT/'casing_source_rows.json').read_text())['parts']
    counts=Counter(pid for i in installed for pid in i['survey_ids'])
    marks={mark:dict(part_id=part['part_id'],expected=part['expected_vehicle_count'],observed=counts[part['part_id']])
           for mark,part in parts.items()}
    assert all(r['expected']==r['observed'] for r in marks.values())
    records={'short_case_rivets':'SNL:167:009','long_case_rivets':'SNL:167:010',
             'beading_countersunk_rivets':'SNL:191:001','wall_rivets':'SNL:170:002',
             'cap_bolts':'SNL:31:002','assumed_support_bolts':'SNL:31:007',
             'plain_nuts':'SNL:128:001','lock_washers':'SNL:270:003'}
    hardware={}
    with sqlite3.connect((REPO/'cad/001_Survey/mark_viii_parts.sqlite').as_uri()+'?mode=ro&immutable=1',uri=True) as connection:
        for key,record in records.items():
            ids=[r[0] for r in connection.execute('select distinct part_id from part_evidence where record_id=?',(record,))]
            assert len(ids)==1
            hardware[key]=dict(type_record=record,part_id=ids[0],observed=counts[ids[0]])
    assert {k:v['observed'] for k,v in hardware.items()}==dict(short_case_rivets=58,long_case_rivets=72,
        beading_countersunk_rivets=40,wall_rivets=22,cap_bolts=14,assumed_support_bolts=8,plain_nuts=22,lock_washers=22)
    casing=[i for i in installed if 'Casing' in i['occurrence']]
    assert len(casing)==300 and sum(v['observed'] for v in marks.values())==42
    return dict(passed=True,native_sha256=sha(native),geometry_report_sha256=sha(report_path),
        source_parts_sha256=sha(ROOT/'casing_source_rows.json'),audit_script_sha256=sha(Path(__file__)),
        fixture_occurrences=len(installed),selected_casing_occurrences=len(casing),named_component_occurrences=42,
        named_source_marks=marks,hardware_counts=hardware,installed_casing_occurrences=casing,
        quantity_conflicts=['Long casing rivets:72 selected joint-level vehicle total versus60 nested total.',
            'Short casing rivets:58 selected nested vehicle total versus62 global catalogue total.',
            'Countersunk beading rivets:40 selected nested vehicle total versus20 remaining in global row.',
            'Support hull bolt type and eight-set allocation are assumptions; the type row names other equipment.',
            'HB M1586 cap beading and HB quantity scopes differ from the selected SNL interpretation.'],
        source_inventory_reconciled=False,full_casing_bom_populated=False,historical_fit_qualified=False,
        standard_model_modified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder',type=Path,nargs='?',default=ROOT/'casing_support_build')
    args=parser.parse_args();result=audit(args.folder.resolve())
    (args.folder/'inventory_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Native casing inventory:300 occurrences,42 named components across12marks; selected quantities pass; source conflicts remain')
