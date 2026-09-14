#!/usr/bin/env python3
"""Freeze the repository's reviewed transcriptions and PDF page map for the survey.
Run from any directory. Requires PyMuPDF only for PDF text/page inventory.
No network; does not alter the source documents.
"""
from pathlib import Path
import ast, hashlib, importlib, json, re, subprocess, sys
import fitz

HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
REF=REPO/'references'
OUT=HERE/'inputs'
OUT.mkdir(exist_ok=True)
dirs={
 'SNL':'1928-03-30_SNL_G13',
 'HB':'1925-03-06_Preliminary_Handbook_Mark_VIII_Tank',
 'LIB':'1918-09_12_Cylinder_Liberty_Aero_Engine',
 'GUN':'1919-08-15_Handbook_QF_Hotchkiss_2.244in_6pdr',
 'JORDAN':'1920-07_Manufacture_of_Mark_VIII_Tanks',
 'PATENT':'1921-01-25_US1366550A'}
projects={'SNL':'SNL_G13_Project','HB':'Handbook_Project','LIB':'Liberty_Project',
          'GUN':'Hotchkiss_Project','JORDAN':'Article_Project','PATENT':'US1366550A_Project'}
manifest={}
def register(p):
 p=Path(p);rel=p.relative_to(REPO).as_posix()
 manifest[rel]={'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
 return rel
def readj(p):
 register(p);return json.loads(p.read_text())
def module(sid,name):
 # Source data modules contain transcription constructors, not the Scribus build.
 base=REF/dirs[sid]/projects[sid]
 for k in list(sys.modules):
  if k=='data' or k.startswith('data.'):del sys.modules[k]
 sys.path.insert(0,str(base))
 try:m=importlib.import_module('data.'+name)
 finally:sys.path.pop(0)
 register(base/'data'/f'{name}.py');return m
def dump(name,obj):
 (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

snl=[]
for name in ['parts_tables','opening_tables']+[p.stem for p in sorted((REF/dirs['SNL']/projects['SNL']/'data').glob('tables_*.py'))]:
 m=module('SNL',name)
 for page,rows in m.TABLES.items():
  for n,row in enumerate(rows,1):
   snl.append({'source':'SNL','page':str(page),'row':n,'path':str(Path(m.__file__).relative_to(REPO)),**row})
snl.sort(key=lambda r:(int(r['page']),r['row']))
dump('snl_rows.json',snl)
n=module('SNL','notes');dump('snl_notes.json',{'notes':n.NOTES,'manufacturers':n.MANUFACTURERS})

hb=[];specs=[];figures=[]
def legend(page,rr,path):
 for i,row in enumerate(rr,1):
  if len(row)==3:callout,mark,desc=row
  else:callout,desc=row;mark=''
  hb.append({'source':'HB','page':str(page),'row':i,'record_type':'legend','callout':callout,'mark':mark,'description':desc,'quantity':'','path':path})
for name in ['front_matter','batch02_tables','batch03_tables']:
 m=module('HB',name);path=str(Path(m.__file__).relative_to(REPO))
 if name=='front_matter':
  specs.extend({'source':'HB','page':'9','feature':x.split('|')[0].strip(),'raw_value':x.split('|')[1],'path':path} for x in m.SPECS.splitlines())
  figures.extend({'source':'HB','page':p,'figure':str(n),'caption':t,'path':path,'kind':'plate_index'} for n,t,p in m.PLATES)
 for attr,page in [('GASOLINE_SPECS',29),('HULL_SPECS',35),('ENGINE_SPECS',45)]:
  for a,b in getattr(m,attr,[]):specs.append({'source':'HB','page':str(page),'feature':a,'raw_value':b,'path':path})
 for attr in ['PARTS','LEGENDS']:
  for page,cols in getattr(m,attr,{}).items():legend(page,[r for col in cols for r in col],path)
hbdata=REF/dirs['HB']/projects['HB']/'data'
for p in sorted(hbdata.glob('tables_batch*.json')):
 d=readj(p);path=str(p.relative_to(REPO))
 if 'legends' in d:
  for page,rr in d['legends'].items():legend(page,rr,path)
  for page,rr in d.get('specifications',{}).items():
   specs.extend({'source':'HB','page':page,'feature':r[0],'raw_value':r[1],'path':path} for r in rr)
 else:
  for page,pd in d.items():
   if not isinstance(pd,dict) or 'sections' not in pd:continue
   i=0
   for sec in pd['sections']:
    heading=' / '.join(x['text'] for x in sec.get('headings',[]))
    for row in sec['rows']:
     i+=1
     hb.append({'source':'HB','page':page,'row':i,'record_type':'nomenclature','mark':row.get('part',''),'description':' '.join(x['text'] for x in row.get('lines',[])),'quantity':row.get('quantity',''),'section':heading,'path':path,'raw':row})
p=hbdata/'batch05_legend.json'
if p.exists():
 d=readj(p)
 dump('hb_batch05_legend_original.json',d)
 # Data structure is retained intact; parse the page's reviewed legend rows below.
 if isinstance(d,dict):
  for page,rows in d.items():
   if isinstance(rows,list) and rows and isinstance(rows[0],(list,tuple)) and len(rows[0]) in (2,3):legend(page,rows,register(p))
 elif isinstance(d,list):legend(95,d,register(p))
dump('hb_rows.json',hb)

lib=readj(REF/dirs['LIB']/projects['LIB']/'data/transcription.json')
dump('liberty_transcription.json',lib)
libpath=str((REF/dirs['LIB']/projects['LIB']/'data/transcription.json').relative_to(REPO))
for entries in lib.get('illustration_index',{}).values():
 for f in entries:figures.append({'source':'LIB','page':f['reference'],'figure':f['number'],'caption':' '.join(f['text']),'path':libpath,'kind':'illustration_index_unemended'})
snlfront=REF/dirs['SNL']/projects['SNL']/'build_front_matter.py'
for node in ast.parse(snlfront.read_text()).body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PLATES' for t in node.targets):
  figures.extend({'source':'SNL','page':p,'figure':str(n),'caption':t,'path':register(snlfront),'kind':'plate_index'} for n,t,p in ast.literal_eval(node.value))
for pg in lib['pages']:
 page=str(pg.get('printed_page',pg.get('label','')))
 for t in pg.get('tables',[]):
  for row in t.get('rows',[]):
   specs.append({'source':'LIB','page':page,'feature':row[0],'raw_value':row[1],'path':str((REF/dirs['LIB']/projects['LIB']/'data/transcription.json').relative_to(REPO))})
dump('specifications.json',specs)

pages=[]
gunmap=readj(REF/dirs['GUN']/projects['GUN']/'data/page_inventory.json')
for p in gunmap:
 if p['label'].startswith('Plate '):figures.append({'source':'GUN','page':p['label'],'figure':p['label'].removeprefix('Plate '),'caption':p['label'],'path':str((REF/dirs['GUN']/projects['GUN']/'data/page_inventory.json').relative_to(REPO)),'kind':'plate_page_inventory'})
for n in (1,2,3):figures.append({'source':'PATENT','page':'drawing sheet '+str(1 if n==1 else 2),'figure':str(n),'caption':{1:'Fragmentary longitudinal vertical section',2:'Cross section on line 2-2 of Fig. 1',3:'Horizontal section through the sponson'}[n],'path':str((REF/dirs['PATENT']/projects['PATENT']/'data/reviewed_transcription.json').relative_to(REPO)),'kind':'patent_figure'})
dump('figure_index.json',figures)
for sid,dirname in dirs.items():
 for pdf in sorted((REF/dirname).glob('*.pdf')):
  path=register(pdf);doc=fitz.open(pdf)
  for i,pg in enumerate(doc):
   if sid=='HB':printed=str((int(re.search(r'Part_(\d)',pdf.name)[1])-1)*50+i+1)
   elif sid=='SNL':printed=str(i-1) if 2<=i<=278 else ('Plate 2 / face p. 277' if i==279 else str(i-2) if i>=280 else '')
   elif sid=='JORDAN':printed=str(i+26) if i else 'editorial cover'
   elif sid=='PATENT':printed=('drawing sheet '+str(i+1)) if i<2 else ('specification '+str(i-1))
   elif sid=='LIB':
    entry=next((p for p in lib['pages'] if p.get('leaf')==i+1),{})
    printed=str(entry.get('printed_page',entry.get('label','')))
   else:
    printed=next((x['label'] for x in gunmap if x['pdf_page']==i+1),'')
   text=pg.get_text(sort=True)
   # SNL text is a dense rotated table; structured rows are authoritative.
   if sid=='SNL' and printed.isdigit() and 2<=int(printed)<=276:
    text='\n'.join(r['item'] for r in snl if r['page']==printed)
   pages.append({'source':sid,'path':path,'pdf_page':i+1,'printed_page':printed,'text':text})
 # Preserve errata in full, including issues irrelevant to geometry.
 for p in (REF/dirname).glob('*errata.txt'):
  register(p);(OUT/(sid.lower()+'_errata.txt')).write_text(p.read_text())
dump('source_pages.json',pages)
for sid,name in [('GUN','lines.json'),('GUN','page_inventory.json'),('JORDAN','reviewed_transcription.json'),('PATENT','reviewed_transcription.json')]:
 p=REF/dirs[sid]/projects[sid]/'data'/name
 if p.exists():dump(sid.lower()+'_'+name,readj(p))
for sid in ['HB','SNL']:
 p=REF/dirs[sid]/projects[sid]/'review.json'
 if p.exists():dump(sid.lower()+'_review.json',readj(p))
dump('source_manifest.json',{'repository':'https://github.com/starseeker/MarkVIIILiberty','commit':subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip(),'files':list(manifest.values())})
print(json.dumps({'snl_rows':len(snl),'handbook_rows':len(hb),'specification_rows':len(specs),'pdf_pages':len(pages),'source_files':len(manifest)},indent=2))
