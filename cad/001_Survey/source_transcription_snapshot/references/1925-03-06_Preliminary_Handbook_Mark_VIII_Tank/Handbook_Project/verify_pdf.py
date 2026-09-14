#!/usr/bin/env python3
"""Verify the saved 251-page checkpoint outside Scribus; optionally compare the older PDF."""
from pathlib import Path
import argparse,hashlib,json,re,unicodedata
import xml.etree.ElementTree as ET
import fitz
ROOT=Path(__file__).resolve().parent

def normalized(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--previous-pdf',type=Path);args=ap.parse_args()
 state=json.loads((ROOT/'PROJECT_STATUS.json').read_text());pdfpath=ROOT/state['master_pdf'];doc=fitz.open(pdfpath)
 errors=[];text=[p.get_text() for p in doc];bounds=[]
 if len(doc)!=251:errors.append('Expected 251 PDF pages')
 if not pdfpath.read_bytes().rstrip().endswith(b'%%EOF'):errors.append('Missing PDF EOF')
 for n,p in enumerate(doc,1):
  if tuple(p.rect)!= (0.0,0.0,396.0,612.0):errors.append(f'Page {n}: wrong media box')
  if '\ufffd' in text[n-1] or '\x00' in text[n-1]:errors.append(f'Page {n}: invalid extracted character')
  for block in p.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     box=fitz.Rect(span['bbox'])
     if not p.rect.contains(box):bounds.append(dict(page=n,text=span['text'],bbox=list(box)))
 errors.extend(f'Out of bounds text: {row}' for row in bounds)
 expected=json.loads((ROOT/'data/native_validation.json').read_text())['frames'];missing=[]
 for row in expected:
  if normalized(row.get('pdf_text',row['text'])) not in normalized(text[row['page']-1]):missing.append(dict(page=row['page'],name=row['name'],text=row['text']))
 # Keep missing-sequence diagnostics explicit; do not equate PDF reading order with native loss.
 if missing:errors.append(f'{len(missing)} text sequences not found in PDF extraction')
 fonts=[];xrefs={font[0] for p in doc for font in p.get_fonts()}
 for xref in sorted(xrefs):
  name,ext,typ,data=doc.extract_font(xref);fonts.append(dict(name=name,format=ext,type=typ,embedded_bytes=len(data)))
  if not data:errors.append('Unembedded font '+name)
 tree=ET.parse(ROOT/'Handbook_Master.sla');images=tree.findall('.//PAGEOBJECT[@PTYPE="2"]');links=[]
 for obj in images:
  path=obj.get('PFILE','');q=ROOT/path;links.append(path)
  if Path(path).is_absolute() or not q.exists():errors.append('Invalid portable image link '+path)
 assets=json.loads((ROOT/'data/assets.json').read_text());asseterrors=[]
 for asset in assets:
  p=ROOT/'assets'/f'{asset["name"]}.png'
  if sha(p)!=asset['sha256']:asseterrors.append(asset['name'])
 if asseterrors:errors.append('Asset hash mismatch '+repr(asseterrors))
 if len(assets)!=146 or len(images)!=146:errors.append('Expected 146 linked artwork assets')
 preservation=None
 if args.previous_pdf:
  import numpy as np
  previous=fitz.open(args.previous_pdf);rows=[]
  for i in range(240):
   a=previous[i].get_pixmap(matrix=fitz.Matrix(2,2));b=doc[i].get_pixmap(matrix=fitz.Matrix(2,2))
   aa=np.frombuffer(a.samples,dtype=np.uint8);bb=np.frombuffer(b.samples,dtype=np.uint8)
   rows.append(dict(page=i+1,identical=bool(np.array_equal(aa,bb)),changed_channel_samples=int(np.sum(aa!=bb))))
  preservation=dict(dpi=144,pages=rows)
  if any(not r['identical'] for r in rows):errors.append('Earlier rendered pages differ')
 result=dict(pdf=pdfpath.name,sha256=sha(pdfpath),pages=len(doc),page_size_points=[396,612],checked_text_sequences=len(expected),missing_text_sequences=missing,out_of_bounds_text=bounds,fonts=fonts,linked_assets=len(links),asset_hash_errors=asseterrors,earlier_pdf_comparison=preservation,errors=errors)
 (ROOT/'data/pdf_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='earlier_pdf_comparison'},ensure_ascii=False,indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
