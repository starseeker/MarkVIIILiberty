#!/usr/bin/env python3
"""Compare every preexisting Scribus page object and named style with checkpoint 12."""
from pathlib import Path
import json,hashlib
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parent
oldpath=R/'Handbook_Checkpoint_001-240_v12.sla';newpath=R/'Handbook_Master.sla'
a=E.parse(oldpath);b=E.parse(newpath);aa=a.findall('.//PAGEOBJECT');bb=b.findall('.//PAGEOBJECT')[:len(aa)]
errors=[];ids=0;unused=[]
for i,(x,y) in enumerate(zip(aa,bb)):
 dx=dict(x.attrib);dy=dict(y.attrib)
 if dx.pop('ItemID',None)!=dy.pop('ItemID',None):ids+=1
 if dx.get('PTYPE')=='5' and 'SHADE' in dx and 'SHADE' not in dy:unused.append(dict(object_index=i,attribute='SHADE',old=dx.pop('SHADE')))
 if dx!=dy:errors.append(dict(object_index=i,attribute_changes={k:[dx.get(k),dy.get(k)] for k in dx.keys()|dy.keys() if dx.get(k)!=dy.get(k)}))
 if [E.tostring(z) for z in x]!=[E.tostring(z) for z in y]:errors.append(dict(object_index=i,problem='Child content changed'))
styles=[]
for tag,key in [('STYLE','NAME'),('CHARSTYLE','CNAME')]:
 old={x.get(key):x for x in a.findall('.//'+tag)};new={x.get(key):x for x in b.findall('.//'+tag)}
 for name,x in old.items():
  y=new.get(name)
  if y is None:errors.append(dict(style=name,problem='Missing'));continue
  changes={k:[x.get(k),y.get(k)] for k in x.attrib.keys()|y.attrib.keys() if x.get(k)!=y.get(k)}
  if changes:styles.append(dict(tag=tag,name=name,changes=changes))
result=dict(baseline=oldpath.name,baseline_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest(),master_sha256=hashlib.sha256(newpath.read_bytes()).hexdigest(),previous_pages=240,compared_page_objects=len(aa),page_object_content_geometry_style_assignments_preserved=not errors,regenerated_item_ids=ids,removed_unused_line_attributes=unused,earlier_style_serialization_changes=styles,errors=errors)
(R/'data/preservation_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
