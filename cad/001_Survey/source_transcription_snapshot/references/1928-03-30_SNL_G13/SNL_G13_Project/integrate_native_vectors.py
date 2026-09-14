#!/usr/bin/env python3
"""Replace seven artwork frames with tested SVG groups; preserve all other objects."""
from pathlib import Path
import json,copy,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent;D=ROOT/'restoration/native';path=ROOT/'SNL_G13_Pilot.sla'
placements=json.loads((D/'placements.json').read_text());tree=E.parse(path);doc=tree.getroot()[0]
used={int(a.get('ItemID')) for a in doc.iter('PAGEOBJECT') if a.get('ItemID')};next_id=1000000
colors={c.get('NAME'):c for c in doc.findall('COLOR')};changes=[]
for n,r in placements.items():
 old=next(a for a in doc.findall('PAGEOBJECT') if a.get('ANNAME')==r['name'])
 if old.get('PTYPE')=='12':continue
 imp=E.parse(D/f'p{n}-native.sla').getroot()[0];group=copy.deepcopy(imp.find('PAGEOBJECT'))
 for c in imp.findall('COLOR'):
  if not c.get('NAME','').startswith('FromSVG'):continue
  name=c.get('NAME')
  if name in colors:assert c.attrib==colors[name].attrib
  else:
   clone=copy.deepcopy(c);doc.insert(list(doc).index(doc.find('PAGE')),clone);colors[name]=clone
 for key in ['WIDTH','HEIGHT','ROT']:
  assert abs(float(old.get(key,'0'))-float(group.get(key,'0')))<.02,(n,key)
 dx=float(old.get('XPOS'))-float(group.get('XPOS'));dy=float(old.get('YPOS'))-float(group.get('YPOS'))
 count=0
 for a in group.iter('PAGEOBJECT'):
  for k,shift in [('XPOS',dx),('YPOS',dy)]:
   if k in a.attrib:a.set(k,format(float(a.get(k))+shift,'.15g'))
  a.set('OwnPage',old.get('OwnPage'));a.set('LAYER',old.get('LAYER','0'))
  while next_id in used:next_id+=1
  a.set('ItemID',str(next_id));used.add(next_id);next_id+=1;count+=1
  if a.get('PFILE'):a.set('PFILE',str((D/a.get('PFILE')).resolve().relative_to(ROOT)))
 group.set('ANNAME',r['name'])
 for k in ['XPOS','YPOS','WIDTH','HEIGHT','ROT']:
  if k in old.attrib:group.set(k,old.get(k))
  else:group.attrib.pop(k,None)
 index=list(doc).index(old);doc.remove(old);doc.insert(index,group)
 changes.append({'folio':n,'object':r['name'],'old_frame_id':old.get('ItemID'),'new_group_id':group.get('ItemID'),'native_object_count':count})
path.write_bytes(E.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True))
(D/'integration.json').write_text(json.dumps(changes,indent=2));print('Inserted',len(changes),'native SVG groups; all other objects retained.')
