"""Validate text/assets and create eight source/reconstruction comparison sheets."""
from pathlib import Path
import json,re,collections,hashlib,unicodedata
import fitz
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
def normalized(t):return ''.join(unicodedata.normalize('NFKC',t).split())
def main():
 (ROOT/'qa').mkdir(exist_ok=True)
 r=json.loads((ROOT/'data/release.json').read_text());frames=json.loads((ROOT/'data/native_frames.json').read_text())
 p=fitz.open(ROOT/r['pdf']);assert len(p)==8
 page_ids=['cover']+list(range(27,34))
 p.set_page_labels([dict(startpage=0,prefix='Cover',style=''),dict(startpage=1,prefix='',style='D',firstpagenum=27)])
 p.set_toc([[1,'Publication context',1],[1,'Manufacture of Mark VIII Tanks at Rock Island Arsenal',2]]+[[2,'Original page '+str(27+i),i+2] for i in range(7)])
 p.save(ROOT/'qa/master_labeled.pdf',garbage=4,deflate=True);p.close();(ROOT/'qa/master_labeled.pdf').replace(ROOT/r['pdf']);p=fitz.open(ROOT/r['pdf'])
 checks=[]
 for i,page in enumerate(p):
  expected=''.join(f['text'] for f in frames if f['page']==page_ids[i]);actual=page.get_text()
  diff=collections.Counter(normalized(expected))-collections.Counter(normalized(actual));extra=collections.Counter(normalized(actual))-collections.Counter(normalized(expected))
  oob=[list(b[:4]) for b in page.get_text('blocks') if not page.rect.contains(fitz.Rect(b[:4]))]
  checks.append(dict(page=page_ids[i],missing_characters=dict(diff),extra_characters=dict(extra),out_of_bounds=oob))
 doc=etree.parse(str(ROOT/r['sla']));links=[]
 for el in doc.findall('.//PAGEOBJECT'):
  path=el.get('PFILE')
  if path:links.append(dict(path=path,relative=not Path(path).is_absolute(),exists=(ROOT/path).is_file()))
 result=dict(pages=checks,images=links,pdf_fonts_embedded=all(x[1]!='n/a' for i in range(len(p)) for x in p.get_page_fonts(i)))
 (ROOT/'data/pdf_validation.json').write_text(json.dumps(result,indent=2))
 assert all(not c['missing_characters'] and not c['extra_characters'] and not c['out_of_bounds'] for c in checks),checks
 assert len(links)==6 and all(x['relative'] and x['exists'] for x in links),links
 comp=fitz.open()
 for i in range(8):
  page=comp.new_page(width=1260,height=918)
  page.insert_text((28,24),'SOURCE SCAN'+(' - volume title page' if i==0 else ' - supplied composite' if i==2 else ''),fontsize=10,fontname='hebo')
  page.insert_text((656,24),'SCRIBUS '+('COVER ADAPTATION - article identification added' if i==0 else 'RECONSTRUCTION - original page '+str(page_ids[i])),fontsize=10,fontname='hebo')
  source=ROOT/'sources'/('MarkVIII_manufacture'+('002_composite' if i==2 else '%03d'%i)+'.jpg')
  page.insert_image(fitz.Rect(20,40,622,885),filename=str(source),keep_proportion=True)
  page.show_pdf_page(fitz.Rect(644,38,1256,902),p,i)
  page.insert_text((28,906),'Harry B. Jordan | Army Ordnance | July-August 1920 | '+r['release_id'],fontsize=7)
 comp.save(ROOT/r['comparison'],garbage=4,deflate=True)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
