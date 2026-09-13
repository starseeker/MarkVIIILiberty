#!/usr/bin/env python3
"""Cumulative checkpoint: open the preserved pages 1–20 SLA and append pages 21–40.
Execute inside Scribus 1.6.x. Overwrites Handbook_Rebuilt_001-040_v2.sla/pdf; save manual edits first.
"""
from pathlib import Path
import json,sys,os,traceback,hashlib
import scribus as s
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import layout_helpers as b
b.STYLE_PREFIX='Batch02 Style '
from data.batch02_tables import GASOLINE_SPECS,HULL_SPECS,PARTS

def body(n):
 for r in BODY.get(str(n),[]):
  y=17+r['baseline']*.225;t=r['text']
  if r['heading']:b.center(t,y,r.get('size',6.5),r.get('font','Roman'));continue
  indent=r['indent'];b.txt(t,50+indent,y,296-indent,9.7,align=4 if r['justify'] else 0,scale=92.5)

def art(a):
 x=198+(a['crop'][0]-a['content_center_px'])*.225;y=17+a['crop'][1]*.225
 name=s.createImage(x,y,a['output_size'][0]*.225,a['output_size'][1]*.225,f'p{a["page"]:03}-{a["name"]}')
 s.loadImage(str(ROOT/'assets'/f'{a["name"]}.png'),name);s.setScaleImageToFrame(True,True,name);s.setTextFlowMode(name,0)

def specs(rows,y,step,size,x=43,valuex=278):
 for label,value in rows:
  width=valuex-x-9;natural=b.advance(label,size,'Roman');scale=min(100,(width-1.2)/natural*100)
  b.txt(label,x,y,width,size,scale=scale)
  start=x+natural*scale/100+2;end=valuex-6
  if start+1<end:b.rule(start,y-1.8,end-start,.25,True)
  b.txt(value,valuex,y,355-valuex,size);y+=step

def parts(n):
 if n not in PARTS:return
 columns=PARTS[n]
 y0={29:504,30:422,31:513,33:424,39:386}[n]
 # Source lettering is small; maintain separate editable number/part/name cells.
 size={29:5.6,30:5.6,31:5.8,33:5.9,39:5.5}[n];step=5.8
 for col,rows in enumerate(columns):
  x=50+col*153;partx=x+11;namex=x+42;right=x+145
  if n==33:x=94;partx=105;namex=159;right=335
  b.txt('Ref.',x,y0-12,12,size);b.txt('No.',x,y0-6,12,size)
  if n==33:b.txt('Part No.',partx,y0-6,52,size)
  else:b.txt('Part',partx,y0-12,30,size);b.txt('No.',partx,y0-6,30,size)
  b.txt('Name.' if n==30 and col==1 else 'Name',namex+12,y0-6,right-namex-12,size)
  y=y0
  for ref,part,desc in rows:
   b.txt(ref,x,y,10,size,align=1)
   if part:b.txt(part,partx,y,namex-partx-2,size)
   for line in desc.split('\n'):
    b.txt(line,namex,y,right-namex,size);y+=step
 if len(columns)==2:
  name=s.createLine(198,y0-15,198,y0+max(sum(len(row[2].split('\n')) for row in col) for col in columns)*step-2)
  s.setLineWidth(.25,name);s.setLineColor('Black',name)

PLATEPOS={21:[(12,123),(13,1553)],22:[(14,512)],23:[(15,115)],24:[(16,119)],25:[(17,337)],26:[(18,281)],27:[(19,236),(20,1316)],28:[(21,119)],29:[(22,635)],30:[(23,147)],31:[(24,1563)],33:[(25,509)],34:[(26,90)],36:[(27,169)],37:[(28,341)],38:[(29,886)],39:[(30,514)],40:[(31,732)]}
CAPTIONS={21:[('CONTROL RODS',1336),('EPICYCLIC CASE',2278)],22:[('FAN BEVEL BOX',1741)],23:[('AIR PUMP',1456)],25:[('VENTILATOR FAN',1407)],26:[('ENGINE-OIL RESERVOIR',1839)],27:[('SIROCCO FAN',1130),('CHAIN DRIVE',2220)],29:[('AIR-PRESSURE PUMP',2060)],30:[('PRESSURE REGULATING TANK',1697)],31:[('COMBINATION TAP',2098)],33:[('GASOLINE TANK',1717)],34:[('SIDE OF HULL WITH SPONSON AND GUN',2430)],36:[('REAR END SHOWING TRIANGULAR SPLASH PLATE AND TOWING EYE',1727)],37:[('DOOR OF HULL SHOWING FITTINGS',2081)],38:[('PROGRESSIVE STEPS IN UNCOVERING REVOLVER HOLE',1445)],39:[('TOP OF HULL',1533)],40:[('SIDE OF TURRET SHOWING CAMOUFLAGE BRACKET',1648)]}

def main():
 global BODY
 for f in ['build-status.txt','build-error.txt']:(ROOT/f).unlink(missing_ok=True)
 available={r[0]:Path(r[5]) for r in s.getXFontNames()}
 for suffix in ['Roman','Bold','Italic']:
  actual=available.get('C059 '+suffix);bundled=ROOT/'fonts'/f'C059-{suffix}.otf'
  if actual is None or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(bundled.read_bytes()).digest():raise RuntimeError('Use bundled C059 OpenType fonts; disable conflicting Type 1 copies.')
 BODY=json.loads((ROOT/'data/body_batch02.json').read_text());assets=json.loads((ROOT/'data/assets.json').read_text())
 previous=json.loads((ROOT/'data/batch01_native_validation.json').read_text())['frames']
 s.openDoc(str(ROOT/'Handbook_Pilot_001-020_v1.sla'))
 if s.pageCount()!=20:raise RuntimeError('Baseline must contain exactly 20 pages.')
 s.setInfo('Ordnance Department; digital reconstruction','Preliminary Handbook of the Mark VIII Tank — cumulative pages 1–40','1918 handbook, reprinted March 6, 1925. Review checkpoint 02; provisional C059 and 5.5 x 8.5 inch canvas. See PROJECT_STATUS.json.')
 s.setRedraw(False)
 for n in range(21,41):
  s.newPage(-1);s.gotoPage(n)
  if n!=35:b.folio(n)
  body(n)
  for a in assets:
   if a['page']==n:art(a)
  for num,y in PLATEPOS.get(n,[]):b.txt('Plate No. '+str(num),267,17+y*.225,80,8.2,align=2)
  for text,y in CAPTIONS.get(n,[]):b.center(text,17+y*.225,6.1)
  if n==28:
   cap='LAYOUT OF GASOLINE PRESSURE-FEED SYSTEM USED ON 35-TON TANK, MARK VIII'
   obj=b.txt(cap,0,12,315,6.1,align=1);s.rotateObject(90,obj);s.moveObjectAbs(312,455,obj)
  if n==29:
   b.center('GASOLINE SYSTEM',49,8.5,'Bold');b.center('OUTLINE SPECIFICATIONS',65,6.5)
   specs(GASOLINE_SPECS,81,9.3,8.0,valuex=286)
  if n==33:b.txt('38285—25†——3',62,462,102,7.5)
  if n==35:
   b.center('Chapter II',72,10);b.center('HULL STRUCTURE',91,9.5,'Bold');b.center('Outline specifications',109,8.4,'Italic')
   specs(HULL_SPECS,119,9.36,7.9);b.center('(35)',487,8.3)
  parts(n)
  print('Appended page',n,flush=True)
 validation=[]
 for row in previous+b.frames:
  name=row['name'];s.layoutText(name)
  validation.append({**row,'overflow':bool(s.textOverflows(name)),'line_count':s.getTextLines(name),'text_matches':s.getAllText(name)==row['text']})
 errors=[r for r in validation if r['overflow'] or r['line_count']!=1 or not r['text_matches']]
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(pages=s.pageCount(),frames=validation,errors=errors,new_text_frames=len(b.frames),compressed_below_85_percent=b.fits),ensure_ascii=False,indent=2))
 if errors:raise RuntimeError('Text validation failed: '+repr(errors[:3]))
 s.gotoPage(1);s.saveDocAs(str(ROOT/'Handbook_Rebuilt_001-040_v2.sla'))
 pdf=s.PDFfile();pdf.file=str(ROOT/'Handbook_Master_001-040_v2.pdf');pdf.pages=list(range(1,41));pdf.version=15
 pdf.fonts=[];pdf.subsetList=['C059 Roman','C059 Bold','C059 Italic'];pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.downsample=0;pdf.save()
 (ROOT/'build-status.txt').write_text(f'PASS: 40 cumulative pages; {len(validation)} native text frames, including {len(b.frames)} new frames; no overflow or text mismatches.\n')
 s.setRedraw(True)
if __name__=='__main__':
 try:main()
 except Exception:
  (ROOT/'build-error.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True)
 finally:
  if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
