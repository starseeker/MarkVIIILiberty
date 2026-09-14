#!/usr/bin/env python3
"""Prepare SVG copies with linked lossless tone images for Scribus 1.6 import."""
from pathlib import Path
import base64,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parent;R=ROOT/'restoration';D=R/'native';D.mkdir(exist_ok=True)
E.register_namespace('', 'http://www.w3.org/2000/svg');E.register_namespace('xlink','http://www.w3.org/1999/xlink')
M=json.loads((R/'manifest.json').read_text());doc=E.parse(ROOT/'SNL_G13_Pilot.sla').getroot()[0]
pages={int(p.get('NUM')):p for p in doc.findall('PAGE')};records={};NS='http://www.w3.org/2000/svg';XL='{http://www.w3.org/1999/xlink}href'
for n,r in M.items():
 if not (r.get('vector') or {}).get('recommended'):continue
 tree=E.parse(ROOT/r['vector']['path'])
 for i,im in enumerate(tree.findall('.//{%s}image'%NS)):
  raw=im.get(XL);assert raw.startswith('data:image/png;base64,')
  path=D/f'p{n}-tone-{i}.png';path.write_bytes(base64.b64decode(raw.split(',',1)[1]));im.set(XL,path.name)
 tree.write(D/f'p{n}-import.svg',encoding='utf-8',xml_declaration=True)
 a=next(a for a in doc.findall('PAGEOBJECT') if a.get('ANNAME')==f'p{n}-plate-artwork');p=pages[int(a.get('OwnPage'))]
 records[n]={'source_svg':r['vector']['path'],'import_svg':f'restoration/native/p{n}-import.svg','width':float(a.get('WIDTH')),'height':float(a.get('HEIGHT')),'rotation':float(a.get('ROT','0')),'page_x':float(a.get('XPOS'))-float(p.get('PAGEXPOS')),'page_y':float(a.get('YPOS'))-float(p.get('PAGEYPOS')),'own_page':int(a.get('OwnPage')),'pixel_size':r['pixel_size'],'name':a.get('ANNAME')}
(D/'placements.json').write_text(json.dumps(records,indent=2))
print('Prepared',len(records),'native vector imports')
