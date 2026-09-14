from pathlib import Path
import csv,json,re,statistics,difflib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
 d=json.loads((ROOT/'data/reviewed_transcription.json').read_text());norm=json.loads((ROOT/'data/normalization.json').read_text());out=[];diffs=[]
 for key,body in d['regions'].items():
  page,reg=key.split('_',1);rows=list(csv.DictReader(open(ROOT/'data/ocr'/('p'+key+'.tsv')),delimiter='\t'))
  groups={}
  for r in rows:
   if r['level']=='5' and r['text'].strip():groups.setdefault((r['block_num'],r['par_num'],r['line_num']),[]).append(r)
  expected=[t for t in body.splitlines() if t];raw=[]
  box=norm[page]['regions'][reg]['box']
  for words in groups.values():
   text=' '.join(w['text'] for w in words);xs=[int(w['left']) for w in words];xe=[int(w['left'])+int(w['width']) for w in words]
   bottoms=[int(w['top'])+int(w['height']) for w in words if not re.search('[gypqj,;]',w['text'])]
   y=statistics.median(bottoms or [int(w['top'])+int(w['height']) for w in words])-1
   raw.append(dict(ocr=text,x=box[0]+min(xs),right=box[0]+max(xe),y=box[1]+y))
  assert len(raw)==len(expected),(key,len(raw),len(expected))
  # The OCR-derived positions are layout references only; all text below is reviewed.
  for r,t in zip(raw,expected):
   if r['ocr']!=t:diffs.append(dict(region=key,ocr=r['ocr'],reviewed=t))
   r['text']=t
  left=float(np.percentile([r['x'] for r in raw],10));right=float(np.percentile([r['right'] for r in raw],90));width=right-left
  # Replace scan bow with straight, consistently spaced native baselines.
  steps=np.diff([r['y'] for r in raw]);leading=float(np.median(steps))
  starts=[0]+[i+1 for i,v in enumerate(steps) if v>leading*1.40 or v<leading*.62]+[len(raw)]
  for i,j in zip(starts,starts[1:]):
   if j-i>=3:
    ys=np.array([r['y'] for r in raw[i:j]]);slope=float(np.polyfit(np.arange(j-i),ys,1)[0]);intercept=float(np.median(ys-np.arange(j-i)*slope))
    for k,r in enumerate(raw[i:j]):r['y']=intercept+k*slope
  for i,r in enumerate(raw):
   heading=r['text'] in d['headings'];indent=0 if r['x']-left<25 else min(48,r['x']-left)
   align=4 if (r['right']-left)>width*.93 else 0
   if heading:indent=0;align=1
   # Source subassembly and electrical lists are ragged, with hanging indents.
   if page=='29' and reg=='L' and 12<=i<=25:indent=35;align=0
   if page=='29' and reg=='R' and 13<=i<=17:indent=45 if i!=15 else 0;align=0
   if page=='33' and reg=='R' and i<5:indent=35;align=0
   if page=='33' and reg=='L' and i==14:indent=35;align=0
   r.update(page=int(page),region=reg,index=i,frame_x=left+indent,frame_width=right-left-indent,heading=heading,align=align)
   if page=='27' and reg=='Ltop':
    r['frame_x']=100 if i<3 else 0;r['frame_width']=890 if i<3 else 990;r['align']=4 if i<3 else 0
   out.append(r)
 (ROOT/'data/layout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(ROOT/'data/ocr_corrections.json').write_text(json.dumps(diffs,ensure_ascii=False,indent=2))
 print('Layout lines:',len(out),'OCR differences:',len(diffs))
if __name__=='__main__':main()
