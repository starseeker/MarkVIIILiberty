#!/usr/bin/env python3
"""Verify comparison PDF completeness, embedded fonts and page/bookmark count."""
from pathlib import Path
import hashlib,json
import fitz
R=Path(__file__).resolve().parent
state=json.loads((R/'PROJECT_STATUS.json').read_text());p=R/state['comparison_pdf'];doc=fitz.open(p)
errors=[]
if len(doc)!=12 or len(doc.get_toc())!=12:errors.append('Expected 12 pages and bookmarks')
if not p.read_bytes().rstrip().endswith(b'%%EOF'):errors.append('Incomplete PDF')
fonts=[]
for xref in sorted({f[0]for page in doc for f in page.get_fonts()}):
 name,ext,typ,data=doc.extract_font(xref);fonts.append(dict(name=name,embedded_bytes=len(data)))
 if not data:errors.append('Unembedded '+name)
result=dict(pdf=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=len(doc),bookmarks=len(doc.get_toc()),fonts=fonts,source_page_range=[241,251],source_crop_policy='Nominal halves: left x=0..1750; right x=1750..3509; y=0..2550',errors=errors)
(R/'data/comparison_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if errors:raise SystemExit(1)
