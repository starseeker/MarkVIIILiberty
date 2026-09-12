#!/usr/bin/env python3
"""Execute inside Scribus 1.6.x. Editable sample pages, ordered by original folio.

Run prepare_assets.py with ordinary Python first to regenerate image assets.
Install the bundled C059 OpenType fonts before opening or rebuilding the SLA.
"""
import os, sys, json, traceback, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import scribus as s
import build_front_matter as f
from data.parts_tables import TABLES as ORIGINAL_TABLES
from data.opening_tables import TABLES as OPENING_TABLES
from data.tables_025_044 import TABLES as TABLES_025_044
from data.tables_045_064 import TABLES as TABLES_045_064
from data.tables_065_084 import TABLES as TABLES_065_084
from data.tables_085_104 import TABLES as TABLES_085_104
from data.tables_105_124 import TABLES as TABLES_105_124
from data.tables_125_144 import TABLES as TABLES_125_144
from data.tables_145_164 import TABLES as TABLES_145_164
from data.tables_165_184 import TABLES as TABLES_165_184
from data.tables_185_204 import TABLES as TABLES_185_204
from data.tables_205_224 import TABLES as TABLES_205_224
from data.tables_225_244 import TABLES as TABLES_225_244
from data.tables_245_264 import TABLES as TABLES_245_264
from data.tables_265_276 import TABLES as TABLES_265_276, END_NOTICE
from data.notes import NOTES, MANUFACTURERS
TABLES={**ORIGINAL_TABLES,**OPENING_TABLES,**TABLES_025_044,**TABLES_045_064,**TABLES_065_084,**TABLES_085_104,**TABLES_105_124,**TABLES_125_144,**TABLES_145_164,**TABLES_165_184,**TABLES_185_204,**TABLES_205_224,**TABLES_225_244,**TABLES_245_264,**TABLES_265_276}

from project_sequence import ORDER, LABELS, PLACEMENT, FOLDOUT_SIZE_POINTS
WIDTHS=[34,22,22,64,50,40,250,28,32]
KEYS=['note','ident','plate','mfr','brit','ord','item','qty','price']
LEADING=8.15
GLYPH_WIDTHS=json.loads((ROOT/'data/font_widths.json').read_text())

def measure(value,size):
 return sum(GLYPH_WIDTHS.get(str(ord(c)),.5) for c in value)*size

def leader(name,x1,y,x2,rotated=False):
 if x2-x1<3:return
 if rotated:x1,y1,x2,y2=y,648-x1,y,648-x2
 else:y1=y2=y
 obj=s.createLine(x1,y1,x2,y2,name)
 s.setLineColor('Black',obj);s.setLineWidth(.25,obj);s.setLineStyle(2,obj);s.setTextFlowMode(obj,0)

def txt(name,x,baseline,w,value,style,leading,lines=1):
 return f.text(name,x,baseline,w,value,style,leading,lines)

def rotated_text(name,x,baseline,w,value,style,leading,lines=1):
 # Landscape layout (648 x 432) -> portrait page (432 x 648).
 top=baseline-leading
 obj=txt(name,top,648-x+leading,w,value,style,leading,lines)
 s.rotateObjectAbs(90,obj,s.BASEPOINT_TOPLEFT)
 s.moveObjectAbs(top,648-x,obj)
 return obj

def line(name,x1,y1,x2,y2,rotated=False,width=.25):
 if rotated: x1,y1,x2,y2=y1,648-x1,y2,648-x2
 obj=s.createLine(x1,y1,x2,y2,name)
 s.setLineWidth(width,obj);s.setLineColor('Black',obj);s.setTextFlowMode(obj,0)

def header(page):
 x=282 if page%2 else 28
 obj=txt(f'p{page}-running-identifier',x,31,122,'S. N. L. No. G–13.','Running identifier',12.6)
 s.setPDFBookmark(1,obj)
 txt(f'p{page}-folio',190,621,52,str(page),'Folio',10)

def table(page):
 header(page)
 even=page%2==0
 left=62
 top=49 if even else 45
 baseline=118 if even else 52
 if even:
  rotated_text(f'p{page}-tank-title',left,35,sum(WIDTHS),'TANK, MARK VIII','Table title',10)
  rotated_text(f'p{page}-parts-title',left+sum(WIDTHS[:6]),107,WIDTHS[6],'PARTS' if page==2 else 'PARTS—Continued','Table title',10)
  labels=['Note\nsymbol','Identi-\nfication\nNo.','Plate\nNo.','#Manufacturers’\npart No. or\nSignal Corps\npart No.','British\npiece mark','Ordnance\npiece mark\nor drawing\nNo.','Item','Quantity\nper unit\nassembly','Unit\nprice']
  x=left
  for i,(w,label) in enumerate(zip(WIDTHS,labels)):
   count=len(label.splitlines())
   rotated_text(f'p{page}-column-{i}',x+1,66,w-2,label,'Table column',7.5,count)
   x+=w
  line(f'p{page}-header-rule',left,96,left+sum(WIDTHS),96,True)
 y=baseline
 for ri,row in enumerate(TABLES[page]):
  y+=row.get('space_before',0)*LEADING
  nlines=len(row['item'].splitlines())
  x=left
  for ci,(key,w) in enumerate(zip(KEYS,WIDTHS)):
   value=row[key]
   if value:
    b=y+(nlines-1)*LEADING if key in ['qty','price'] else y
    b+=row.get('cell_baseline_offsets',{}).get(key,0)*LEADING
    style='Table item' if key=='item' else 'Table number' if key in ['qty','price','plate','ident'] else 'Table cell'
    if key=='item' and row.get('item_layout'):
     for fi,fragment in enumerate(row['item_layout']):
      t=fragment['text'];fw=fragment['width']
      obj=rotated_text(f'p{page}-r{ri+1:02}-item-{fi}',x+2+fragment['x'],b+fragment.get('y',0)*LEADING,fw,t,style,LEADING,len(t.splitlines()))
      longest=max(measure(v,6.1) for v in t.splitlines())
      if longest>fw-2:s.setTextScalingH(min(100,100*(fw-2)/longest),obj)
    else:
     obj=rotated_text(f'p{page}-r{ri+1:02}-{key}',x+2,b,w-4,value,style,LEADING,len(value.splitlines()))
     longest=max(measure(v,6.1) for v in value.splitlines())
     # A little right-edge clearance avoids Scribus rounding a final digit
     # into a second line in narrow right-aligned identification cells.
     if longest>w-6:
      s.setTextScalingH(min(100,100*(w-6)/longest),obj)
   # Sparse grouped references retain their native editable brace marks.
   if value and key in row.get('cell_braces',{}):
    bt=b-5.8;bb=b+(len(value.splitlines())-1)*LEADING+1.5;mid=(bt+bb)/2
    for side in row['cell_braces'][key]:
     bx=x+1 if side=='left' else x+w-1
     sign=1 if side=='left' else -1
     points=[(bx+sign*1.5,bt),(bx+sign*.5,bt+1),(bx+sign*.5,mid-1.5),(bx,mid),(bx+sign*.5,mid+1.5),(bx+sign*.5,bb-1),(bx+sign*1.5,bb)]
     for bi,(a,z) in enumerate(zip(points,points[1:])):
      line(f'p{page}-r{ri+1:02}-{key}-brace-{side}-{bi}',*a,*z,True,width=.2)
   if key=='item' and (row['qty'] or row['price']):
    last=value.split('\n')[-1] if value else ''
    scale=min(1,(w-6)/max(measure(v,6.1) for v in value.splitlines())) if value else 1
    start=x+2+measure(last,6.1)*scale+2
    leader(f'p{page}-leader-{ri}-{ci}',start,y+(nlines-1)*LEADING-1,x+w-2,True)
   x+=w
  y+=(nlines+row.get('space_after',0))*LEADING
 bottom=y-LEADING+4
 x=left
 for ci,w in enumerate(WIDTHS[:-1]):
  x+=w
  line(f'p{page}-vertical-{ci}',x,top,x,bottom,True)
 if even: line(f'p{page}-top-rule',left,top,left+sum(WIDTHS),top,True)
 line(f'p{page}-bottom-rule',left,bottom,left+sum(WIDTHS),bottom,True)
 if page==15:
  txt('p15-printer-imprint',28,621,120,'53476—28——2','Printer imprint',8)
 if page==31:
  txt('p31-printer-imprint',28,621,120,'53476—28——3','Printer imprint',8)
 if page==47:
  txt('p47-printer-imprint',28,621,120,'53476—28——4','Printer imprint',8)
 if page==63:
  txt('p63-printer-imprint',28,621,120,'53476—28——5','Printer imprint',8)
 if page==79:
  txt('p79-printer-imprint',28,621,120,'53476—28——6','Printer imprint',8)

 if page==95:
  txt('p95-printer-imprint',28,621,120,'53476—28——7','Printer imprint',8)

 if page==111:
  txt('p111-printer-imprint',28,621,120,'53476—28——8','Printer imprint',8)

 if page==127:
  txt('p127-printer-imprint',28,621,120,'53476—28——9','Printer imprint',8)
 if page==143:
  txt('p143-printer-imprint',28,621,120,'53476—28——10','Printer imprint',8)
 if page==159:
  txt('p159-printer-imprint',28,621,120,'53476—28——11','Printer imprint',8)
 if page==175:
  txt('p175-printer-imprint',28,621,120,'53476—28——12','Printer imprint',8)
 if page==191:
  txt('p191-printer-imprint',28,621,120,'53476—28——13','Printer imprint',8)
 if page==207:
  txt('p207-printer-imprint',28,621,120,'53476—28——14','Printer imprint',8)
 if page==223:
  txt('p223-printer-imprint',28,621,120,'53476—28——15','Printer imprint',8)
 if page==239:
  txt('p239-printer-imprint',28,621,120,'53476—28——16','Printer imprint',8)
 if page==255:
  txt('p255-printer-imprint',28,621,120,'53476—28——17','Printer imprint',8)

 if page==271:
  txt('p271-printer-imprint',28,621,120,'53476—28——18','Printer imprint',8)
 if page==276:
  rotated_text('p276-end-notice',left+2,bottom+16,sum(WIDTHS)-4,END_NOTICE,'Table item',LEADING)

def title_leaf():
 for i,value in enumerate(['STANDARD','NOMENCLATURE LIST','No. G–13']):
  obj=txt(f'p1-title-{i+1}',28,286+31*i,376,value,'Half-title',30)
  s.sizeObject(376,40,obj)
  if i==0:s.setPDFBookmark(1,obj)
 txt('p1-folio',190,621,52,'1','Folio',10)

def manufacturers(page,y):
 x=64; widths=[119,142,51]
 line('p308-manufacturers-top',x,y-3,x+sum(widths),y-3)
 xx=x
 for i,(title,w) in enumerate(zip(['Item','Name of Manufacturer','Symbol'],widths)):
  txt(f'p308-mfr-header-{i}',xx+3,y+9,w-6,title,'Manufacturer heading',10)
  xx+=w
 line('p308-manufacturers-header-rule',x,y+17,x+sum(widths),y+17)
 yy=y+32
 for ri,record in enumerate(MANUFACTURERS):
  xx=x
  for ci,(value,w) in enumerate(zip(record,widths)):
   if value:txt(f'p308-mfr-{ri}-{ci}',xx+4,yy,w-8,value,'Manufacturer cell',10.5)
   if ci<2 and value:
    leader(f'p308-mfr-leader-{ri}-{ci}',xx+5+measure(value,8.7)+2,yy-1,xx+w-3)
   xx+=w
  yy+=10.5
 for xx in [x+widths[0],x+sum(widths[:2])]:line(f'p308-mfr-vertical-{xx}',xx,y,xx,yy-4)
 line('p308-manufacturers-bottom',x,yy,x+sum(widths),yy)
 return yy+17

def notes(page):
 header(page)
 txt(f'p{page}-notes-heading',28,49,376,'NOTES' if page==307 else 'NOTES—Continued','Notes heading',12)
 leading=10.45
 y=64
 for pi,para in enumerate(NOTES[page].split('\n\n')):
  if para=='{MANUFACTURERS}':
   y=manufacturers(page,y+2)
   continue
  lines=para.splitlines()
  for li,value in enumerate(lines):
   x=28 if li==0 else 65
   sty='Notes spread' if li<len(lines)-1 else 'Notes text'
   txt(f'p{page}-note-{pi:02}-line-{li+1:02}',x,y,376-(x-28),value,sty,leading)
   y+=leading
 if page==311:
  txt('p311-prices-heading',28,137,376,'USE OF PRICES','Notes heading',12)
  txt('p311-prices-instruction-1',39,155,365,'(See instructions under above heading in Introduction to The Ordnance','Notes spread',10.45)
  txt('p311-prices-instruction-2',28,165.45,376,'Catalogue.)','Notes text',10.45)
  txt('p311-signature-name',245,193,145,'C. C. Williams','Signature name',11)
  txt('p311-signature-role',208,205,196,'Major General, Chief of Ordnance.','Signature role',11)
  txt('p311-office-reference',46,210,145,'(O. O. 140.2/1741)','Printer imprint',8)
  txt('p311-printing-office',226,630,178,'U. S. GOVERNMENT PRINTING OFFICE : 1928','Government imprint',8)

def figure_artwork(page,transforms):
 cfg=transforms[str(page)]
 iw,ih=cfg['output_size']
 rotate=cfg.get('rotate',0)
 if not rotate:
  bx,by,maxw,maxh=PLACEMENT.get(page,[28,49,376,550])
  factor=min(maxw/iw,maxh/ih);w,h=iw*factor,ih*factor
  obj=s.createImage(bx+(maxw-w)/2,by,w,h,f'p{page}-plate-artwork')
 else:
  bx,by,maxw,maxh=PLACEMENT.get(page,[62,35,540,355])
  factor=min(maxw/iw,maxh/ih);w,h=iw*factor,ih*factor
  lx,ly=bx+(maxw-w)/2,by+(maxh-h)/2
  obj=s.createImage(ly,648-lx,w,h,f'p{page}-plate-artwork')
  s.rotateObjectAbs(90,obj,s.BASEPOINT_TOPLEFT)
  s.moveObjectAbs(ly,648-lx,obj)
 s.loadImage(str(ROOT/'assets'/f'p{page}-geometry.png'),obj)
 s.setScaleImageToFrame(True,True,obj);s.setTextFlowMode(obj,0)
 s.setObjectAttributes([dict(Name='Source and geometry',Type='string',Value=f'p{page}.jpg; '+cfg['method']+'; '+cfg['status'],Parameter='',Relationship='',RelationshipTo='',AutoAddTo='')],obj)


def figure(page,transforms):
 header(page)
 figure_artwork(page,transforms)
 if page==303:
  txt('p303-printer-imprint',28,621,120,'53476—28——20','Printer imprint',8)
 if page==287:
  txt('p287-printer-imprint',28,621,120,'53476—23——19','Printer imprint',8)


def make_foldout():
 # Scribus swaps the supplied dimensions for landscape documents.
 s.newDocument((648,1296),(24,24,24,24),s.LANDSCAPE,1,s.UNIT_POINTS,s.PAGE_1,0,1)
 s.setInfo('Ordnance Department; digital reconstruction','Plate 2 — Face p. 277',
  'Provisional 18 x 9 inch foldout canvas; unnumbered insertion, original pixel aspect ratio retained.')
 cfg=json.loads((ROOT/'calibration/figure_transforms.json').read_text())['277_foldout']
 iw,ih=cfg['output_size'];factor=min(1248/iw,600/ih);w,h=iw*factor,ih*factor
 obj=s.createImage((1296-w)/2,(648-h)/2,w,h,'p277-foldout-plate-2')
 s.loadImage(str(ROOT/'assets/p277_foldout-geometry.png'),obj);s.setScaleImageToFrame(True,True,obj)
 s.setObjectAttributes([dict(Name='Original insertion',Type='string',Value='Plate 2, Face p. 277. Working reading order after p277; physical imposition unconfirmed.',Parameter='',Relationship='',RelationshipTo='',AutoAddTo='')],obj)
 s.saveDocAs(str(ROOT/'Foldout_Plate_2.sla'));s.closeDoc()

def main():
 (ROOT/'build-error.txt').unlink(missing_ok=True)
 (ROOT/'build-status.txt').unlink(missing_ok=True)
 make_foldout()
 f.main(False)
 s.setInfo('Ordnance Department; digital reconstruction',
  'S. N. L. No. G-13 — supplied-page pilot',
  f'{len(LABELS)} supplied pages/leaves ordered by original folio, including Plate 2 foldout. Main pages 6 x 9 inches; provisional foldout 18 x 9. See page_inventory.json and calibration records.')
 s.setRedraw(False)
 f.style('Half-title',20.5,f.BOLD,leading=30,align=1)
 f.style('Table cell',6.1,leading=LEADING)
 f.style('Table item',6.1,leading=LEADING)
 f.style('Table number',6.1,leading=LEADING,align=2)
 f.style('Table column',5.2,leading=7.5,align=1)
 f.style('Table title',8.3,leading=10,align=1)
 f.style('Notes heading',10.0,leading=12,align=1)
 f.style('Notes text',9.1,leading=10.45)
 f.style('Notes spread',9.1,leading=10.45,align=4)
 f.style('Manufacturer heading',7.4,leading=10,align=1)
 f.style('Manufacturer cell',8.7,leading=10.5)
 f.style('Signature name',9.7,leading=11,align=1,features='smallcaps')
 f.style('Signature role',9.0,f.ITALIC,leading=11,align=2)
 f.style('Government imprint',5.5,f.BOLD,leading=8,tracking=4)
 transforms=json.loads((ROOT/'calibration'/'figure_transforms.json').read_text())
 for page in ORDER:
  if os.environ.get('SNL_BATCH')=='1' and isinstance(page,int) and page%20==0:print(f'Building printed page {page}',flush=True)
  if page=='277_foldout':
   s.importPage(str(ROOT/'Foldout_Plate_2.sla'),(1,),1,2)
   continue
  s.newPage(-1)
  s.gotoPage(s.pageCount())
  if page==1:title_leaf()
  elif page in TABLES:table(page)
  elif page in NOTES:notes(page)
  else:figure(page,transforms)
 validation=[]
 for frame_index,(name,expected) in enumerate(f.frames,1):
  if os.environ.get('SNL_BATCH')=='1' and frame_index%2000==0:print(f'Checking text frame {frame_index} of {len(f.frames)}',flush=True)
  s.layoutText(name)
  validation.append(dict(frame=name,overflow=bool(s.textOverflows(name)),expected_lines=expected,actual_lines=s.getTextLines(name)))
 (ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
 errors=[r for r in validation if r['overflow'] or r['expected_lines']!=r['actual_lines']]
 # Save even a failing proof for diagnosis; status is only PASS once all checks pass.
 s.gotoPage(1)
 if os.environ.get('SNL_BATCH')=='1':print('Saving native document and exporting PDF',flush=True)
 s.saveDocAs(str(ROOT/'SNL_G13_Pilot.sla'))
 # Finish the native export on ordinary temporary storage before committing
 # bytes to the project path; this also catches incomplete PDF writes.
 with tempfile.TemporaryDirectory(prefix='snl-g13-export-') as temp:
  target=Path(temp)/'pilot.pdf'
  pdf=s.PDFfile();pdf.file=str(target);pdf.pages=list(range(1,s.pageCount()+1))
  pdf.version=15;pdf.fonts=[];pdf.subsetList=[f.ROMAN,f.BOLD,f.ITALIC]
  pdf.compress=1;pdf.quality=0;pdf.resolution=300;pdf.save()
  data=target.read_bytes()
  if not data.rstrip().endswith(b'%%EOF'):raise RuntimeError('Incomplete PDF export')
  (ROOT/'SNL_G13_Pilot.pdf').write_bytes(data)
 s.setRedraw(True);s.redrawAll()
 if errors:raise RuntimeError('Text layout errors: '+repr(errors))
 (ROOT/'build-status.txt').write_text(f'PASS: {s.pageCount()} pages; {len(validation)} native text frames; no overflow; expected line counts.\n')

if __name__=='__main__':
 try: main()
 except Exception: (ROOT/'build-error.txt').write_text(traceback.format_exc())
 finally:
  if os.environ.get('SNL_BATCH')=='1':os._exit(0)
