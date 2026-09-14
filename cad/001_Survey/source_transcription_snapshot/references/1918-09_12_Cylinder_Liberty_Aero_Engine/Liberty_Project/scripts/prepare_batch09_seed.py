"""Append only the two unprinted closing cover surfaces to the exact v08 SLA."""
from pathlib import Path
import json, copy
from xml.etree import ElementTree as ET
R = Path(__file__).resolve().parents[1]
old = json.loads((R / 'data/baseline_v08_release.json').read_text())
tree = ET.parse(R / old['sla'])
d = tree.find('DOCUMENT')
pages = d.findall('PAGE')
assert len(pages) == 160
last = pages[-1]
idx = list(d).index(last) + 1
for n in range(160, 162):
    p = copy.deepcopy(last)
    p.set('NUM', str(n))
    p.set('PAGEYPOS', str(float(last.get('PAGEYPOS')) + (n - 159) * 731))
    p.set('PAGEWIDTH', '396')
    p.set('PAGEHEIGHT', '691')
    d.insert(idx, p)
    idx += 1
assert all(ET.tostring(a) == ET.tostring(b) for a, b in zip(pages, d.findall('PAGE')[:160]))
d.set('ANZPAGES', '162')
path = R / '_batch09_seed.sla'
tree.write(path, encoding='UTF-8', xml_declaration=True)
print(path)
