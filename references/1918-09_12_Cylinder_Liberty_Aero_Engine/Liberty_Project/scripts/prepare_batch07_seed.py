"""Append blank page definitions to the exact released native baseline.
Scribus 1.6's scripter cannot change one page's dimensions. This deterministic
XML step adds only new PAGE elements, including the wider page-123 foldout.
All original page definitions, objects and styles are left intact. The builder
opens, authors, saves and reopens the resulting seed in native Scribus.
"""
from pathlib import Path
import json,copy
from xml.etree import ElementTree as etree
R=Path(__file__).resolve().parents[1]
old=json.loads((R/'data/baseline_v06_release.json').read_text())
tree=etree.parse(str(R/old['sla']));d=tree.find('DOCUMENT');pages=d.findall('PAGE');assert len(pages)==120
last=pages[-1];idx=list(d).index(last)+1
for n in range(120,140):
 p=copy.deepcopy(last);p.set('NUM',str(n));p.set('PAGEYPOS',str(float(last.get('PAGEYPOS'))+(n-119)*731));p.set('PAGEWIDTH','612' if n==125 else '396');d.insert(idx,p);idx+=1
assert all(etree.tostring(a)==etree.tostring(b) for a,b in zip(pages,d.findall('PAGE')[:120]))
d.set('ANZPAGES','140')
# Keep beside the source document so relative artwork references remain valid.
path=R/'_batch07_seed.sla';tree.write(str(path),encoding='UTF-8',xml_declaration=True)
print(path)
