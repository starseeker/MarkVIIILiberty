#!/usr/bin/env python3
"""Rebuild the survey SQLite database from frozen, source-linked JSON. Stdlib only.
Identifiers are conservative: drawing numbers and plate callouts are not part IDs.
"""
from pathlib import Path
import collections, hashlib, json, re, sqlite3, unicodedata
HERE=Path(__file__).resolve().parents[1];INPUT=HERE/'inputs'
def read(name):return json.loads((INPUT/name).read_text())
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True)
def norm(x):
 x=str(x).replace('–','-').replace('—','-').replace('−','-').replace('’',"'")
 return re.sub(r'\s+',' ',x).strip()
def mark(x):
 x=norm(x).upper().strip(' .,()')
 return re.sub(r'(?<=[A-Z])-(?=\d)','',x).replace(' ','')
def stable(x):return hashlib.sha256(x.encode()).hexdigest()[:16]
def clean(x):
 x=norm(x);x=re.sub(r'-(?:Continued|Contd)\.?','',x,flags=re.I)
 x=re.split(r'\(?\bFor\s',x)[0]
 x=re.sub(r'\s*\(\d[\d,]*\)\.?\)?$','',x)
 return x.rstrip(' ,.;)')
def namekey(x):
 x=clean(x).lower();x=x.replace('camshaft','cam shaft').replace('crankshaft','crank shaft').replace('louvre','louver')
 # Order-independent words reconcile "crank CASE" with "CASE, crank".
 return ' '.join(sorted(re.findall(r"[a-z0-9]+|[½¼¾⅛⅜⅝⅞″]",x)))
def quantity(x):
 s=norm(x).strip('()').replace(',','')
 return int(s) if s.isdigit() else None
ONES={'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,'eighteen':18,'nineteen':19,'twenty':20,'thirty':30,'forty':40,'fifty':50,'sixty':60,'seventy':70,'eighty':80,'ninety':90}
def numberword(x):
 n=0
 for w in x.replace('-',' ').split():
  if w in ONES:n+=ONES[w]
  elif w=='hundred':n*=100
  elif w!='and':return None
 return n
NUMWORDS='|'.join(list(ONES)+['hundred','and'])
COMP=re.compile(r'^\s*\*?\s*((?:(?:'+NUMWORDS+r')[\s-]*)+)\s+(\(?[A-Za-z0-9][A-Za-z0-9/–—−.-]*\)?|[—–-])\s+(.*)$',re.S)

dbpath=HERE/'mark_viii_parts.sqlite'
# Build in memory and publish one closed database image. This also avoids
# SQLite journal semantics on network-backed workspaces.
c=sqlite3.connect(':memory:');c.execute('PRAGMA foreign_keys=ON')
c.executescript('''
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE sources(source_id TEXT PRIMARY KEY,title TEXT,configuration TEXT,primary_role TEXT);
CREATE TABLE source_files(path TEXT PRIMARY KEY,sha256 TEXT NOT NULL,bytes INTEGER NOT NULL);
CREATE TABLE source_pages(page_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources, path TEXT REFERENCES source_files,pdf_page INTEGER,printed_page TEXT,text TEXT);
CREATE TABLE source_records(record_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,row_no INTEGER,record_type TEXT,source_path TEXT,description TEXT,raw_json TEXT NOT NULL);
CREATE TABLE parts(part_id TEXT PRIMARY KEY,canonical_name TEXT NOT NULL,kind TEXT NOT NULL,identity_basis TEXT,subsystem TEXT,readiness TEXT,readiness_basis TEXT,missing_geometry TEXT);
CREATE TABLE part_identifiers(part_id TEXT REFERENCES parts,namespace TEXT,identifier TEXT,raw_identifier TEXT,role TEXT,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,namespace,identifier,role,record_id));
CREATE INDEX identifier_lookup ON part_identifiers(namespace,identifier);
CREATE TABLE part_evidence(part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,relationship TEXT,confidence TEXT,PRIMARY KEY(part_id,record_id,relationship));
CREATE TABLE quantities(quantity_id INTEGER PRIMARY KEY,part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,quantity_raw TEXT,quantity_value REAL,scope TEXT,interpretation TEXT);
CREATE TABLE assembly_edges(edge_id INTEGER PRIMARY KEY,parent_part_id TEXT REFERENCES parts,child_part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,quantity_raw TEXT,quantity_per_parent REAL,relation TEXT,confidence TEXT,UNIQUE(parent_part_id,child_part_id,record_id,relation));
CREATE TABLE dimensions(dimension_id INTEGER PRIMARY KEY,part_id TEXT REFERENCES parts,record_id TEXT REFERENCES source_records,feature TEXT,raw_value TEXT,value_numeric REAL,unit TEXT,value_mm REAL,status TEXT,interpretation TEXT);
CREATE TABLE figures(figure_id INTEGER PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,figure TEXT,caption TEXT,kind TEXT,source_path TEXT);
CREATE TABLE part_figures(part_id TEXT REFERENCES parts,source_id TEXT REFERENCES sources,printed_page TEXT,figure TEXT,callout TEXT,record_id TEXT REFERENCES source_records);
CREATE TABLE notes(note_id TEXT PRIMARY KEY,source_id TEXT REFERENCES sources,printed_page TEXT,symbol TEXT,text TEXT);
CREATE TABLE part_notes(part_id TEXT REFERENCES parts,note_id TEXT REFERENCES notes,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,note_id,record_id));
CREATE TABLE issues(issue_id TEXT PRIMARY KEY,category TEXT,severity TEXT,title TEXT,source_id TEXT REFERENCES sources,locator TEXT,details TEXT,resolution TEXT,status TEXT);
CREATE TABLE issue_parts(issue_id TEXT REFERENCES issues,part_id TEXT REFERENCES parts,link_basis TEXT,PRIMARY KEY(issue_id,part_id));
CREATE TABLE variants(variant_id TEXT PRIMARY KEY,description TEXT);
CREATE TABLE part_variants(part_id TEXT REFERENCES parts,variant_id TEXT REFERENCES variants,status TEXT,record_id TEXT REFERENCES source_records,basis TEXT,PRIMARY KEY(part_id,variant_id,record_id,status));
CREATE TABLE research_leads(lead_id TEXT PRIMARY KEY,title TEXT,vendor TEXT,url TEXT,date_or_period TEXT,verification TEXT,priority INTEGER,benefit TEXT,limitations TEXT,checked_date TEXT);
CREATE TABLE lead_parts(lead_id TEXT REFERENCES research_leads,part_id TEXT REFERENCES parts,match_basis TEXT,PRIMARY KEY(lead_id,part_id));
CREATE TABLE part_relations(part_id TEXT REFERENCES parts,related_part_id TEXT REFERENCES parts,relation TEXT,basis TEXT,record_id TEXT REFERENCES source_records,PRIMARY KEY(part_id,related_part_id,relation,record_id));
CREATE TABLE review_queue(review_id INTEGER PRIMARY KEY,record_id TEXT REFERENCES source_records,part_id TEXT REFERENCES parts,reason TEXT,detail TEXT);
CREATE TABLE coverage(source_id TEXT REFERENCES sources,category TEXT,count INTEGER,method TEXT,limitation TEXT,PRIMARY KEY(source_id,category));
CREATE VIRTUAL TABLE records_fts USING fts5(record_id UNINDEXED,description);
CREATE VIRTUAL TABLE pages_fts USING fts5(page_id UNINDEXED,text);
''')
sources=[('SNL','Standard Nomenclature List G-13 (30 March 1928)','U.S. service; first 100 / replacement / planned future fits distinguished','parts and explicit composed-of relationships'),('HB','Preliminary Handbook of the Mark VIII Tank (1918; 1925 reprint)','preliminary International/British design, with aircraft data','vehicle arrangement, specifications, nomenclature and legends'),('LIB','The 12 Cylinder Liberty Aero Engine (September 1918)','aircraft; not automatically the tank installation','base engine form, sections, maintenance data'),('GUN','Hotchkiss 2.244-inch 6-pdr 6-cwt Mk II Gun with Tank Mounting (1919)','component manual; installation must be checked against tank','gun/mount component forms and arrangement'),('JORDAN','Harry B. Jordan, Manufacture of Mark VIII Tanks (1920), pp. 27-33','Rock Island production 1919-1920','production configuration and installation evidence'),('PATENT','Herbert W. Alden, U.S. Patent 1,366,550 (1921)','patent embodiment','sponson movement and feature relationships')]
c.executemany('INSERT INTO sources VALUES(?,?,?,?)',sources)
manifest=read('source_manifest.json')
c.executemany('INSERT INTO metadata VALUES(?,?)',[('schema_version','1.0'),('repository',manifest['repository']),('source_commit',manifest['commit']),('survey_date','2026-09-13'),('scope','Source-linked CAD survey; not a count of manufactured pieces or a released engineering BOM'),('quantity_rule','Never sum catalogue quantities, assembly contents, spare equipment and alternatives together'),('coordinate_units','Original units preserved; explicit conversions use exact 25.4 mm/in'),('build','python scripts/build_database.py')])
c.executemany('INSERT INTO source_files VALUES(:path,:sha256,:bytes)',manifest['files'])
for p in read('source_pages.json'):
 pid=p['source']+':'+Path(p['path']).name+':'+str(p['pdf_page'])
 c.execute('INSERT INTO source_pages VALUES(?,?,?,?,?,?)',(pid,p['source'],p['path'],p['pdf_page'],p['printed_page'],p['text']))
 c.execute('INSERT INTO pages_fts VALUES(?,?)',(pid,p['text']))
for v in [('PRELIMINARY_1918','1918 intended configuration described in 1925 reprint'),('ROCK_ISLAND_FIRST_100','American production first 100; dated installation evidence required'),('SERVICE_REPLACEMENT','Later service replacements, including 1922 carburetor decision'),('FUTURE_PRODUCTION','Hypothetical future production in SNL notes; not evidence of tanks built'),('AIRCRAFT_LIBERTY','1918 aircraft engine, including alternative carburetors'),('PATENT_EMBODIMENT','Alden patent drawing embodiment'),('SHIPPING_ONLY','Shipping or storage equipment'),('SPARES_TOOLS','Spare parts and tools; not installed count')]:c.execute('INSERT INTO variants VALUES(?,?)',v)

parts={};aliases=collections.defaultdict(set);records={};rid_part={};snl_primary={};fingerprints=collections.defaultdict(set)
def classify(desc,context=''):
 s=(desc+' '+context).lower()
 for key,pat in [('Armament and stowage','gun|sight|ammunition|shell|breech|cradle|recoil|periscope'),('Cooling and ventilation','radiator|cooling fan|sirocco|ventilat|water tank|fan bevel|jockey|whittle'),('Fuel and pressure','petrol|gasoline|fuel|regulating tank|air pressure|air-pressure|carburetor|carburettor'),('Electrical and instruments','generator|distribut|ignition|battery|cable|telephone|switch|lamp|tachometer|distance recorder|voltage|starter'),('Track and running gear','road track|track driv|track adjust|track roller|roller support|sprocket|chain casing|mud chute|skirting'),('Transmission clutch and controls','transmission|epicyclic|planet|clutch|brake|control|selector|cross shaft|cardan'),('Engine and lubrication','crank|cam shaft|camshaft|cylinder|piston|connecting rod|valve|engine|oil pump|water pump|silencer|muffler|gudgeon'),('Hull and fittings','hull|sponson|turret|roof|floor|door|plate|angle|beam|girder|towing|seat|batten|bracket|cover|packing piece')]:
  if re.search(pat,s):return key
 if re.search(r'\b(bolt|nut|washer|rivet|screw|pin|plug|wire|gasket)\b',s):return 'Shared hardware'
 return 'Other equipment / unassigned'
def kind(desc):
 s=desc.lower()
 if re.search(r'\b(electrolyte|compound, sealing|paint|gasoline,|oil, engine|grease,)\b',s):return 'consumable'
 if 'assembly' in s or re.search(r'\bcomplete\b',s):return 'assembly'
 if re.search(r'\b(hole|duct|orifice|recess|groove|opening)\b',s) and not re.search(r'plate|cover|tube|pipe|bracket|shaft|plug|pin|screw|valve|body|washer|angle|packing',s):return 'feature'
 return 'component'
def rec(rid,sid,page,row,typ,path,desc,raw):
 c.execute('INSERT INTO source_records VALUES(?,?,?,?,?,?,?,?)',(rid,sid,str(page),row,typ,path,desc,js(raw)))
 c.execute('INSERT INTO records_fts VALUES(?,?)',(rid,desc));records[rid]={'source':sid,'page':str(page),'desc':desc,'raw':raw}
def newpart(key,desc,basis,rid,context='',ptype=None):
 pid='P_'+stable(key)
 if pid not in parts:
  k=ptype or kind(desc);parts[pid]={'name':clean(desc) or '[unnamed source entry]','kind':k,'key':key,'basis':basis,'subsystem':classify(desc,context)}
  c.execute('INSERT INTO parts VALUES(?,?,?,?,?,?,?,?)',(pid,parts[pid]['name'],k,basis,parts[pid]['subsystem'],'D_INSUFFICIENT','No reviewed geometric sufficiency yet','Dimensions, interfaces, and shape definition require assessment'))
 c.execute('INSERT OR IGNORE INTO part_evidence VALUES(?,?,?,?)',(pid,rid,'source_identification','high' if basis.startswith('explicit') else 'provisional'))
 rid_part[rid]=pid
 return pid
def evidence(pid,rid,relationship='source_identification',confidence='high'):
 c.execute('INSERT OR IGNORE INTO part_evidence VALUES(?,?,?,?)',(pid,rid,relationship,confidence));rid_part[rid]=pid
def ident(pid,ns,raw,role,rid):
 if not raw or not str(raw).strip(' —–-'):return
 val=mark(raw);c.execute('INSERT OR IGNORE INTO part_identifiers VALUES(?,?,?,?,?,?)',(pid,ns,val,str(raw),role,rid))
 if role=='part_mark':aliases[(ns,val)].add(pid)
def ns_for(code,desc='',mfr=False):
 n=mark(code)
 if re.match(r'^(LQ|SH|M\d|MX\d)',n):return 'tank_piece_mark'
 if n.startswith('W-') or re.match(r'^W[A-Z]',n):return 'Willard'
 if re.match(r'^D\d+$',n) and re.search('distributor|generator|ignition|voltage|switch',desc,re.I):return 'Delco'
 for vendor in ['Timken','SKF','Gurney','Fafnir','Monarch','HB']:
  if n.startswith(vendor.upper()):return vendor
 if n.startswith('T-') or 'titeflex' in desc.lower():return 'Titeflex'
 if mfr:return 'manufacturer_or_signal_corps'
 return 'tank_piece_mark'
def addqty(pid,rid,raw,scope,explanation):
 if raw!='':c.execute('INSERT INTO quantities VALUES(NULL,?,?,?,?,?,?)',(pid,rid,str(raw),quantity(raw),scope,explanation))
def add_dim(pid,rid,feature,raw,value=None,unit=None,status='uninterpreted_source_dimension',meaning='Source wording retained; not an approved CAD parameter'):
 mm=value*25.4 if value is not None and unit=='in' else value if unit=='mm' else None
 c.execute('INSERT INTO dimensions VALUES(NULL,?,?,?,?,?,?,?,?,?)',(pid,rid,feature,raw,value,unit,mm,status,meaning))

snl=read('snl_rows.json');parent=None;last=None;physical=[];pending=[]
# Layout-only parsing overrides. Original source strings remain untouched.
overrides={
 'SNL:34:016':('four','Timken316-312','BEARING, roller, assembly'),
 'SNL:73:013':('three hundred and three','SH607C','radiator TUBE'),
 'SNL:77:027':('four','ND1200','BEARING, ball, radial, dia. 1.1811″, bore .3937″, face .3543″, or equal'),
 'SNL:110:029':('one','ND1200','BEARING, ball, radial, dia. 1.1811″, bore .3937″, face .3543″, or equal'),
 'SNL:112:014':('two','Timken6454-6420','BEARING, roller, assembly'),
 'SNL:158:014':('one','SKF1304','BEARING, ball, radial, dia. 2.0472″, bore .7874″, face .5906″, or equal'),
 'SNL:160:018':('one','HB303','BEARING, ball, radial, dia. 1.8504″, bore .6693″, thickness .5512″, or equal'),
 'SNL:210:017':('two','SKF1204','BEARING, ball, radial, dia. 1.8504″, bore .7874″, height .5512″, or equal'),
 'SNL:213:021':('one','HB206','BEARING, ball, radial, dia. 2.4410″, bore 1.1811″, height .6299″, or equal'),
 'SNL:251:020':('two','Fafnir1821','BEARING, ball, single thrust, dia. 6.1024″, bore 4.1339″, height 1.5748″, or equal'),
 'SNL:226:007':('twelve','Q38/21192','shell holder plunger SPRING'),
 'SNL:226:009':('sixty','B37/21191','6-pdr. shell expansion TUBE'),
 'SNL:226:010':('sixty','A37/21191','6-pdr. shell TUBE'),
 'SNL:20:014':('two','-Q512B','WIRE, lock, soft iron, W. & M. Ga. No. 18 x 5″ (4)'),
 'SNL:14:014':('approximately one half','','COMPOUND, sealing, lb.'),
 'SNL:14:015':('approximately one pint','','ELECTROLYTE, 1.255 S. G., qt.')}
for row in snl:
 rid=f"SNL:{row['page']}:{row['row']:03d}";s=row['item'];flat=norm(s)
 parse_s=re.sub(r'^\s*\((?:gd|gu)\)\s*',' ',s)
 parse_s=re.sub(r'(?<=[a-z])—',' — ',parse_s)
 m=COMP.match(parse_s)
 parsed=overrides.get(rid) or (m.groups() if m else None)
 gu=re.match(r'^\s*\(gu\)\s+(\S+)\s+(.*)$',s,re.S)
 if gu:parsed=('variable',gu[1],gu[2])
 iscomp=parsed is not None
 typ='component' if iscomp else ('composition_marker' if 'Composed of:' in s else 'catalogue_entry' if re.match(r'^[A-Z]',s) else 'continuation')
 if re.search(r'Continued|Contd\.',s) and typ=='catalogue_entry':typ='continuation_heading'
 rec(rid,'SNL',row['page'],row['row'],typ,row['path'],s,row)
 if typ=='composition_marker':parent=last;continue
 if typ=='continuation_heading':continue
 if typ=='continuation':
  if last:pending.append((last,rid,'continuation_text'))
  continue
 code='';qword='';desc=flat
 if iscomp:
  qword,code,desc=parsed;desc=clean(desc);code=code.strip('()')
  if code in ('—','–','-'):code=''
  if 'or equal' in desc:desc=desc.replace('or equal','',1).strip()
 else:
  parent=None
  desc=clean(desc)
  code=row['brit'] if re.search(r'\d',row['brit']) else row['ord'] if re.match(r'^[A-Za-z]',row['ord']) else ''
  if not code:code=row['mfr']
 if code:
  ns=ns_for(code,desc,mfr=(code==row['mfr']))
  # The same stud mark can label a bare stud and a hardware assembly.
  key='SNL:assembly:'+namekey(desc) if 'assembly' in desc.lower() else ns+':'+mark(code)
  pid=newpart(key,desc,'explicit source mark; assembly role distinguished',rid)
  ident(pid,ns,code,'part_mark',rid)
 else:
  # Unnumbered assembly references can match explicit catalogue headings by words.
  key=('SNL:assembly:' if 'assembly' in desc.lower() else 'SNL:description:')+namekey(desc)
  pid=newpart(key,desc,'description fingerprint within SNL; provisional identity',rid)
 if not iscomp:
  snl_primary[pid]=rid
  parts[pid]['name']=desc;c.execute('UPDATE parts SET canonical_name=? WHERE part_id=?',(desc,pid))
 for col in ['brit','ord','mfr','ident']:
  val=row[col]
  if not val:continue
  if col=='ident':ident(pid,'SNL_plate_callout',val,'callout',rid)
  elif col=='ord' and re.match(r'^\d',val):ident(pid,'Ordnance_drawing',val,'drawing_number_or_unresolved_numeric_reference',rid)
  else:ident(pid,ns_for(val,desc,col=='mfr'),val,'part_mark' if col in ['brit','ord'] or val==code else 'manufacturer_cross_reference',rid)
 if row['plate']:
  c.execute('INSERT INTO part_figures VALUES(?,?,?,?,?,?)',(pid,'SNL',row['page'],row['plate'],row['ident'],rid))
 addqty(pid,rid,row['qty'],'catalogue_quantity_per_unit_assembly','Column heading is quantity per unit assembly; parentheses and note (*) retained; not automatically per parent')
 if iscomp:
  v=numberword(qword);c.execute('INSERT INTO quantities VALUES(NULL,?,?,?,?,?,?)',(pid,rid,qword,v,'per_named_parent','Leading written quantity in composed-of list'))
  if parent:
   c.execute('INSERT OR IGNORE INTO assembly_edges VALUES(NULL,?,?,?,?,?,?,?)',(parent,pid,rid,qword,v,'composed_of','explicit list; parsed'))
  else:c.execute('INSERT INTO review_queue VALUES(NULL,?,?,?,?)',(rid,pid,'unattached_component','Composed-of parent not established'))
  tm=re.search(r'\((\d[\d,]*)\)\.?\)?$',flat)
  if tm:addqty(pid,rid,tm[1],'parenthetical_total','Often total for major unit under note (*); not a multiplier for leading quantity')
 else:last=pid
 physical.append((rid,pid,row,desc))
 fingerprints[namekey(desc)].add(pid)
 if re.search(r'\d.*(?:″|inches|inch|mm\b|m\. m\.|feet|foot|thread|Ga\.)',desc,re.I):add_dim(pid,rid,'dimensional_description',desc)

for pid,rid,rel in pending:evidence(pid,rid,rel,'contextual')

# Exact manufacturer / Signal Corps cross references are usable aliases, but never
# manufacture identity by stripping B/L/D prefixes from old engine drawing numbers.
for pid,ns,val,raw,role,rid in c.execute('SELECT * FROM part_identifiers').fetchall():
 if role=='manufacturer_cross_reference':aliases[(ns,val)].add(pid)

hb=read('hb_rows.json')
for r in hb:
 rid=f"HB:{r['record_type']}:{r['page']}:{r['row']:03d}"
 page=re.sub(r'(?<=\d)[a-z]$','',r['page'])
 rec(rid,'HB',page,r['row'],r['record_type'],r['path'],r['description'],r)
 code=r.get('mark','');desc=r['description'];matches=set()
 if not desc.strip() and code.isdigit():
  c.execute('INSERT INTO review_queue VALUES(NULL,?,NULL,?,?)',(rid,'unlabelled_numeric_reference','Blank legend label, numeric reference '+code+'; not enough evidence for a separate physical part'))
  continue
 if code:
  val=mark(code)
  for ns in ['tank_piece_mark','manufacturer_or_signal_corps','Delco','Willard','Titeflex']:matches.update(aliases.get((ns,val),set()))
  # A legend often names the bare component; avoid assigning it to a same-mark assembly.
  desired=[p for p in matches if (parts[p]['kind']=='assembly')==('assembly' in desc.lower())]
  if desired:matches=set(desired)
 if len(matches)==1:
  pid=next(iter(matches));evidence(pid,rid,'exact_identifier_cross_reference','high')
 elif code:
  pid=newpart('HBmark:'+mark(code)+('|assembly' if 'assembly' in desc.lower() else ''),desc,'explicit HB mark; cross-source identity unresolved',rid,r.get('section',''))
  ident(pid,'handbook_mark',code,'part_mark',rid)
  if len(matches)>1:c.execute('INSERT INTO review_queue VALUES(NULL,?,?,?,?)',(rid,pid,'multiple_identifier_matches',js(sorted(matches))))
 else:
  pid=newpart('HBunnumbered:'+r['page']+':'+str(r['row'])+':'+r['record_type'],desc,'unnumbered HB entry; retained independently',rid,r.get('section',''))
 if not desc.strip():c.execute('INSERT INTO review_queue VALUES(NULL,?,?,?,?)',(rid,pid,'missing_source_description','Identifier retained; the source row has no descriptive label'))
 addqty(pid,rid,r.get('quantity',''),'handbook_number_per_machine' if r['record_type']=='nomenclature' else 'legend','Blank, x, split and repeated quantities retained; repeated source assertions must not be summed')
 if r['record_type']=='legend':
  figures=[f for f in read('figure_index.json') if f['source']=='HB' and str(f['page'])==page]
  c.execute('INSERT INTO part_figures VALUES(?,?,?,?,?,?)',(pid,'HB',page,'; '.join(f['figure'] for f in figures),str(r.get('callout','')),rid))
 if re.search(r'\d.*(?:″|inch|mm|m\. m\.|feet|foot|thread)',desc,re.I):add_dim(pid,rid,'dimensional_description',desc)

# Notes are part-level evidence, including configuration qualifiers.
notes=read('snl_notes.json')
for page,text in notes['notes'].items():
 for block in re.split(r'\n\s*\n',text):
  m=re.match(r'\(([^)]+)\)',block)
  if not m:continue
  sym=m[1];nid='SNL_NOTE:'+sym
  c.execute('INSERT INTO notes VALUES(?,?,?,?,?)',(nid,'SNL',page,sym,block))
for rid,pid,r,desc in physical:
 syms=re.findall(r'\(([^)]+)\)',r['note'])
 syms+=re.findall(r'^\s*\((gd|gu)\)',r['item'])
 syms+= [s for s in '*%&XR' if s in r['note']]
 for s in syms:
  nid='SNL_NOTE:'+s
  if c.execute('SELECT 1 FROM notes WHERE note_id=?',(nid,)).fetchone():c.execute('INSERT OR IGNORE INTO part_notes VALUES(?,?,?)',(pid,nid,rid))
  variant={'gb':'ROCK_ISLAND_FIRST_100','gw':'ROCK_ISLAND_FIRST_100','ga':'SHIPPING_ONLY','ge':'SERVICE_REPLACEMENT','gf':'SERVICE_REPLACEMENT','gi':'SERVICE_REPLACEMENT','gj':'SERVICE_REPLACEMENT','gaa':'SERVICE_REPLACEMENT','gaj':'SERVICE_REPLACEMENT','gx':'SERVICE_REPLACEMENT'}.get(s)
  if variant:c.execute('INSERT OR IGNORE INTO part_variants VALUES(?,?,?,?,?)',(pid,variant,'qualified by note',rid,nid))

# Import all source errata; preserve their wording, rather than silently repair data.
for sid in [s[0] for s in sources]:
 f=INPUT/(sid.lower()+'_errata.txt')
 if not f.exists():continue
 text=f.read_text();blocks=re.split(r'(?m)^(?=\d+\. )',text)
 if len(blocks)==1:
  c.execute('INSERT INTO issues VALUES(?,?,?,?,?,?,?,?,?)',(sid+'_SOURCE_NOTE','inherited_source_note','low','Source wording note',sid,'See preserved errata file',text,'Original wording retained','documented_limit'))
 for b in blocks[1:]:
  number=int(re.match(r'\d+',b)[0]);b=b.split('\nBasis:')[0].strip()
  iid=f'{sid}_ERRATA_{number:02d}';first=b.split('\n')[0]
  loc=first.split(':')[0];c.execute('INSERT INTO issues VALUES(?,?,?,?,?,?,?,?,?)',(iid,'inherited_source_erratum','review',first,sid,loc,b,'No unrecorded emendation applied','open'))
  # Links require literal alphanumeric part marks, never page numbers.
  tokens={mark(t) for t in re.findall(r'\b(?:M|SH|LQ|D|B|A)[-–]?[0-9]+[A-Z]*\b',b)}
  for ns,val in list(aliases):
   if val in tokens:
    for pid in aliases[(ns,val)]:c.execute('INSERT OR IGNORE INTO issue_parts VALUES(?,?,?)',(iid,pid,'literal identifier in source erratum'))

# Source-level specification claims retain their raw units and scope.
for i,r in enumerate(read('specifications.json'),1):
 rid=f"{r['source']}:spec:{i:03d}";rec(rid,r['source'],r['page'],i,'specification',r['path'],r['feature']+': '+r['raw_value'],r)
 add_dim(None,rid,r['feature'],r['raw_value'])
for f in read('figure_index.json'):
 c.execute('INSERT INTO figures VALUES(NULL,?,?,?,?,?,?)',(f['source'],f['page'],f['figure'],f['caption'],f['kind'],f['path']))

# Hand-reviewed supplemental components, geometry anchors, issues and research leads.
curated=read('curated_survey.json') if (INPUT/'curated_survey.json').exists() else {}
curated_ids={}
for i,r in enumerate(curated.get('components',[]),1):
 rid=f"{r['source']}:survey:{i:03d}";rec(rid,r['source'],r['page'],i,'reviewed_supplement',r.get('path',''),r['name'],r)
 if r.get('same_as') in curated_ids:
  pid=curated_ids[r['same_as']];evidence(pid,rid,'spare_equipment_occurrence','reviewed')
 else:pid=newpart('survey:'+r['key'],r['name'],'reviewed source component; local survey identity',rid,r.get('subsystem',''),r.get('kind'))
 if r.get('subsystem'):parts[pid]['subsystem']=r['subsystem'];c.execute('UPDATE parts SET subsystem=? WHERE part_id=?',(r['subsystem'],pid))
 curated_ids[r['key']]=pid
 if r.get('quantity') is not None:addqty(pid,rid,str(r['quantity']),r.get('quantity_scope','documented assembly'),'Curated from specified passage; not an added catalogue total')
 if r.get('variant'):c.execute('INSERT OR IGNORE INTO part_variants VALUES(?,?,?,?,?)',(pid,r['variant'],'documented',rid,r.get('basis','')))
 if r.get('figure'):c.execute('INSERT INTO part_figures VALUES(?,?,?,?,?,?)',(pid,r['source'],str(r['page']),str(r['figure']),r.get('callout',''),rid))
 if r.get('parent') in curated_ids:
  c.execute('INSERT INTO assembly_edges VALUES(NULL,?,?,?,?,?,?,?)',(curated_ids[r['parent']],pid,rid,str(r.get('quantity','')),r.get('quantity'),'documented_arrangement','reviewed; no placement coordinates'))
 c.execute('UPDATE parts SET readiness=?,readiness_basis=?,missing_geometry=? WHERE part_id=?',(r.get('readiness','B_DOCUMENTED_FORM'),r.get('basis','Named and described in cited source; not fully dimensioned'),r.get('missing','Mating dimensions, exact profile and installation applicability'),pid))
 for code in r.get('related_marks',[]):
  for ns,val in aliases:
   if val==mark(code):
    for other in aliases[(ns,val)]:c.execute('INSERT OR IGNORE INTO part_relations VALUES(?,?,?,?,?)',(pid,other,'related_component_not_asserted_identical','Manual/source configuration must be reconciled before merging',rid))
for i,r in enumerate(curated.get('anchors',[]),1):
 rid=f"{r['source']}:anchor:{i:03d}";rec(rid,r['source'],r['page'],i,'reviewed_dimension',r.get('path',''),r['feature']+': '+r['raw'],r)
 pid=curated_ids.get(r.get('part',''))
 add_dim(pid,rid,r['feature'],r['raw'],r.get('value'),r.get('unit'),r.get('status','direct_dimension'),r.get('basis','Explicit source value; use only in stated configuration'))
for r in curated.get('issues',[]):
 c.execute('INSERT INTO issues VALUES(?,?,?,?,?,?,?,?,?)',(r['id'],r['category'],r['severity'],r['title'],r.get('source'),r['locator'],r['details'],r['resolution'],r['status']))
 for code in r.get('marks',[]):
  for ns,val in aliases:
   if val==mark(code):
    for pid in aliases[(ns,val)]:c.execute('INSERT OR IGNORE INTO issue_parts VALUES(?,?,?)',(r['id'],pid,'reviewed issue identifier'))
for r in curated.get('leads',[]):
 c.execute('INSERT INTO research_leads VALUES(?,?,?,?,?,?,?,?,?,?)',(r['id'],r['title'],r['vendor'],r['url'],r['date'],r['verification'],r['priority'],r['benefit'],r['limitations'],'2026-09-13'))
 for pid,p in parts.items():
  if any(re.search(pat,p['name'],re.I) or re.search(pat,p['key'],re.I) for pat in r.get('match',[])):
   c.execute('INSERT INTO lead_parts VALUES(?,?,?)',(r['id'],pid,'research association by documented vendor/type; not interchangeability'))

# Initial readiness is explicitly triage, not an assertion that detail geometry is solved.
for pid,p in parts.items():
 if pid in curated_ids.values():continue
 name=p['name'].lower();dims=c.execute('SELECT COUNT(*) FROM dimensions WHERE part_id=?',(pid,)).fetchone()[0]
 figs=c.execute('SELECT COUNT(*) FROM part_figures WHERE part_id=?',(pid,)).fetchone()[0]
 if p['kind']=='consumable':status='N_NON_GEOMETRIC';basis='Bulk material/consumable';missing='Represent volume only if useful to the model'
 elif p['name'] in ['BALL, steel, ¼″','BALL, steel, 1″']:
  status='A_SIMPLE_GEOMETRY';basis='Nominal spherical external geometry is fully specified by the stated diameter';missing='Finish, tolerance and installation are separate from this nominal sphere'
  rid=snl_primary.get(pid) or c.execute('SELECT record_id FROM part_evidence WHERE part_id=? LIMIT 1',(pid,)).fetchone()[0]
  add_dim(pid,rid,'sphere_diameter',p['name'],0.25 if '¼' in p['name'] else 1.0,'in','direct_dimension','Nominal sphere only; manufacturing tolerance not specified')
 elif p['kind']=='feature':status='B_DOCUMENTED_FORM';basis='Named feature, not necessarily a separate manufactured component';missing='Host part, profile, dimensions and location'
 elif re.search(r'^(?:bolt|nut|washer|rivet|screw|pin, split|wire|gasket|stud)\b',name) and dims:
  status='C_ENGINEERING_APPROXIMATION';basis='Dimensional hardware description; historical standard and head/fit details still need confirmation';missing='Period head dimensions, thread form, manufacturing details and placement'
 elif figs:
  status='B_DOCUMENTED_FORM';basis='Explicit plate/legend reference; dimensioned completeness has not been demonstrated';missing='Calibrated shape, hidden faces, mating datums and hole positions'
 elif dims:
  status='C_ENGINEERING_APPROXIMATION';basis='Some dimensions recorded, full geometric sufficiency unproven';missing='Unspecified profile, interfaces, section or mounting locations'
 else:status='D_INSUFFICIENT';basis='Identity/assembly evidence only in the normalized inventory';missing='Dimensioned drawing or calibrated views plus interface dimensions'
 blocking=c.execute("SELECT i.issue_id FROM issues i JOIN issue_parts ip USING(issue_id) WHERE ip.part_id=? AND i.category='dimension' AND i.status='open'",(pid,)).fetchall()
 if blocking:
  status='D_INSUFFICIENT';basis='Unresolved dimensional contradiction: '+', '.join(x[0] for x in blocking);missing='Resolve contradictory dimensions before using them as CAD parameters'
  c.execute("UPDATE dimensions SET status='conflicting_source_dimension',interpretation=? WHERE part_id=?",(basis,pid))
 c.execute('UPDATE parts SET readiness=?,readiness_basis=?,missing_geometry=? WHERE part_id=?',(status,basis,missing,pid))

# Duplicate names/marks remain reviewable; no fuzzy matching makes silent mergers.
for (ns,val),pids in aliases.items():
 if len(pids)>1:
  kinds={parts[p]['kind'] for p in pids}
  if len(kinds)==len(pids):continue
  for pid in sorted(pids):c.execute('INSERT INTO review_queue VALUES(NULL,NULL,?,?,?)',(pid,'identifier_collision',js({'namespace':ns,'identifier':val,'candidates':sorted(pids)})))
for sid in [s[0] for s in sources]:
 for category,table in [('pdf_pages','source_pages'),('source_records','source_records')]:
  n=c.execute(f'SELECT COUNT(*) FROM {table} WHERE source_id=?',(sid,)).fetchone()[0]
  c.execute('INSERT INTO coverage VALUES(?,?,?,?,?)',(sid,category,n,'Frozen current repository PDF/text and reviewed tables','Page presence is not a claim of exhaustive interpretation of every line/image'))
c.executescript('''
CREATE VIEW v_parts AS SELECT p.*, (SELECT group_concat(DISTINCT namespace||':'||identifier) FROM part_identifiers i WHERE i.part_id=p.part_id AND role IN ('part_mark','manufacturer_cross_reference')) AS identifiers,(SELECT count(*) FROM part_evidence e WHERE e.part_id=p.part_id) AS evidence_count FROM parts p;
CREATE VIEW v_bom_edges AS SELECT e.edge_id,e.parent_part_id,p.canonical_name AS parent,e.child_part_id,ch.canonical_name AS child,e.quantity_per_parent,e.quantity_raw,e.relation,e.confidence,r.source_id,r.printed_page,e.record_id FROM assembly_edges e JOIN parts p ON p.part_id=e.parent_part_id JOIN parts ch ON ch.part_id=e.child_part_id JOIN source_records r ON r.record_id=e.record_id;
CREATE VIEW v_geometry_queue AS SELECT part_id,canonical_name,subsystem,readiness,readiness_basis,missing_geometry FROM parts ORDER BY readiness,subsystem,canonical_name;
CREATE VIEW v_source_evidence AS SELECT e.part_id,p.canonical_name,r.record_id,r.source_id,r.printed_page,r.row_no,r.record_type,r.source_path,r.description,e.relationship,e.confidence FROM part_evidence e JOIN parts p USING(part_id) JOIN source_records r USING(record_id);
CREATE VIEW v_cross_source_parts AS SELECT p.part_id,p.canonical_name,count(DISTINCT r.source_id) AS source_count,group_concat(DISTINCT r.source_id) AS sources FROM parts p JOIN part_evidence e USING(part_id) JOIN source_records r USING(record_id) GROUP BY p.part_id HAVING count(DISTINCT r.source_id)>1;
CREATE VIEW v_reviewed_dimensions AS SELECT d.*,r.source_id,r.printed_page FROM dimensions d JOIN source_records r USING(record_id) WHERE d.status IN ('direct_dimension','derived_dimension','disputed_direct_dimension');
''')
c.commit()
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not c.execute('PRAGMA foreign_key_check').fetchall()
stats={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ['sources','source_files','source_pages','source_records','parts','part_identifiers','part_evidence','assembly_edges','quantities','dimensions','figures','part_figures','notes','issues','research_leads','review_queue','v_cross_source_parts']}
stats['readiness']={k:n for k,n in c.execute('SELECT readiness,COUNT(*) FROM parts GROUP BY readiness')}
stats['subsystems']={k:n for k,n in c.execute('SELECT subsystem,COUNT(*) FROM parts GROUP BY subsystem')}
stats['record_types']={k:n for k,n in c.execute("SELECT source_id||':'||record_type,COUNT(*) FROM source_records GROUP BY source_id,record_type")}
(HERE/'reports/build_statistics.json').write_text(json.dumps(stats,indent=2)+'\n')
(HERE/'schema.sql').write_text('\n\n'.join(row[0]+';' for row in c.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE '%_fts_%' AND name NOT LIKE 'sqlite_%' ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 ELSE 2 END,name"))+'\n')
c.execute('VACUUM')
for suffix in ['-journal','-wal','-shm']:
 Path(str(dbpath)+suffix).unlink(missing_ok=True)
dbpath.write_bytes(c.serialize());c.close()
with sqlite3.connect('file:'+str(dbpath)+'?mode=ro&immutable=1',uri=True) as check:
 assert check.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 assert not check.execute('PRAGMA foreign_key_check').fetchall()
print(json.dumps(stats,indent=2))
