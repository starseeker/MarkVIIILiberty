#!/usr/bin/env python3
"""Validate this audit against the previous delivered project ZIP.
Run after Scribus export and make_proofs.py --pilot-only.
"""
from pathlib import Path
import argparse, hashlib, importlib, io, json, sys, zipfile
import xml.etree.ElementTree as ET
import fitz
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from project_sequence import LABELS
parser=argparse.ArgumentParser();parser.add_argument('--baseline-zip',required=True)
args=parser.parse_args()
z=zipfile.ZipFile(args.baseline_zip)
prefix=next(n[:-len('SNL_G13_Pilot.sla')] for n in z.namelist() if n.endswith('/SNL_G13_Pilot.sla'))
audit=json.loads((ROOT/'audit/ambiguity_audit.json').read_text())
changes=[r['change'] for r in audit['findings'] if r['change']]
byname={c['frame']:c for c in changes}
old=ET.fromstring(z.read(prefix+'SNL_G13_Pilot.sla'))
new=ET.parse(ROOT/'SNL_G13_Pilot.sla').getroot()
def canon(n):
 # Scribus allocates ItemID anew on reopening; object names are stable identities.
 return (n.tag,sorted((k,v) for k,v in n.attrib.items() if k!='ItemID'),(n.text or '').strip(),[canon(c) for c in n])
oldpages=old.findall('.//PAGE');newpages=new.findall('.//PAGE')
assert len(newpages)==314
assert [canon(p) for p in oldpages]==[canon(p) for p in newpages], 'Page geometry changed'
a={p.get('ANNAME'):p for p in old.findall('.//PAGEOBJECT')}
b={p.get('ANNAME'):p for p in new.findall('.//PAGEOBJECT')}
assert len(a)==32632 and a.keys()==b.keys()
for name,obj in a.items():
 if name in byname:
  c=byname[name];found=0
  for t in obj.iter('ITEXT'):
   if c['old'] in t.get('CH',''):
    t.set('CH',t.get('CH').replace(c['old'],c['new']));found+=1
  assert found==1,name
 assert canon(obj)==canon(b[name]),'Native object changed unexpectedly: '+str(name)
assets=[];sources=[]
for folder,target in [('assets',assets),('sources',sources)]:
 for p in sorted((ROOT/folder).iterdir()):
  if p.is_file():
   key=prefix+p.relative_to(ROOT).as_posix()
   assert p.read_bytes()==z.read(key),str(p)
   target.append(p.name)
# Check table contents field by field against the original modules.
changed_fields=[];rowcount=0
for p in sorted((ROOT/'data').glob('*.py')):
 if p.stem not in ['parts_tables','opening_tables'] and not p.stem.startswith('tables_'):continue
 namespace={'__name__':'data.'+p.stem,'__package__':'data'}
 exec(compile(z.read(prefix+p.relative_to(ROOT).as_posix()),p.name,'exec'),namespace)
 previous=namespace['TABLES'];current=importlib.import_module('data.'+p.stem).TABLES
 assert previous.keys()==current.keys()
 for page,rows in previous.items():
  assert len(rows)==len(current[page])
  for i,(a0,b0) in enumerate(zip(rows,current[page]),1):
   rowcount+=1;assert a0.keys()==b0.keys()
   for field in a0:
    if a0[field]!=b0[field]:
     c=next(c for c in changes if c['page']==page and c['row']==i and c['field']==field)
     assert b0[field]==a0[field].replace(c['old'],c['new'])
     changed_fields.append(dict(page=page,row=i,field=field))
assert rowcount==7571 and len(changed_fields)==3
native=json.loads((ROOT/'audit/context_native_validation.json').read_text())
assert native['exported'] and native['overflow_count']==native['line_count_errors']==0
reopen=json.loads((ROOT/'reopen-validation.json').read_text())
assert reopen['page_count']==314 and len(reopen['frames'])==25682
assert not any(r['overflow'] or r['lines']!=r['expected_lines'] for r in reopen['frames'])
current=fitz.open(ROOT/'SNL_G13_Pilot.pdf');previous=fitz.open(stream=z.read(prefix+'SNL_G13_Pilot.pdf'),filetype='pdf')
assert len(current)==314 and [p.get_label() for p in current]==LABELS
assert current.get_toc()==previous.get_toc()
unchanged=[];changed=[]
for i,(p,q) in enumerate(zip(previous,current)):
 assert p.rect==q.rect
 assert all(current.extract_font(f[0])[3] for f in q.get_fonts())
 # Modest-resolution pixel comparison catches unintended rendering changes anywhere.
 same=p.get_pixmap(matrix=fitz.Matrix(1,1)).samples==q.get_pixmap(matrix=fitz.Matrix(1,1)).samples
 (unchanged if same else changed).append(LABELS[i])
assert set(changed)=={'43','66','97'},'Unexpected PDF page changes: '+repr(changed)
for c in changes:
 txt=current[LABELS.index(str(c['page']))].get_text()
 assert c['new'] in txt, c
report=fitz.open(ROOT/'Transcription_Ambiguity_Audit.pdf')
assert len(report)==4
assert all(report.extract_font(f[0])[3] for p in report for f in p.get_fonts())
result=dict(status='PASS',date='2026-09-12',electronic_pages=314,editable_text_frames=25682,
 native_objects=32632,native_geometry_preserved=True,changed_text_frames=list(byname),
 table_records_checked=rowcount,changed_data_fields=changed_fields,
 unchanged_source_images=len(sources),unchanged_figure_assets=len(assets),
 unchanged_rendered_pdf_pages=len(unchanged),changed_pdf_folios=changed,
 embedded_fonts=True,original_folio_navigation=True,audit_report_pages=4,
 review_summary=audit['summary'])
(ROOT/'audit/context_delivery_validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
