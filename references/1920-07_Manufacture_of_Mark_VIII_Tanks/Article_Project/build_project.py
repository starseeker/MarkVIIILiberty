"""Run in Scribus 1.6.x: Script > Execute Script. Creates a fresh seven-page edition.
The reviewed JSON, bundled fonts and linked artwork are authoritative inputs.
Save manual edits with another filename before rebuilding this release.
"""
from pathlib import Path
import os,json,traceback
import scribus as s
ROOT=Path(__file__).resolve().parent
R=json.loads((ROOT/'data/release.json').read_text())
D=json.loads((ROOT/'data/reviewed_transcription.json').read_text())
LAY=json.loads((ROOT/'data/layout.json').read_text())
A=json.loads((ROOT/'data/artwork.json').read_text())
MET=json.loads((ROOT/'fonts/metrics.json').read_text())
W,H=612.,864.;SX=522./2080.;LEFT,TOP=45.,45.
FONT={'Roman':'C059 Roman','Bold':'C059 Bold','Italic':'C059 Italic'}
frames=[];rules=[];styles={};images=[];serial=0
def measure(t,size,font):return sum(MET['C059-'+font].get(c,.5) for c in t)*size
def text(t,x,y,w,size=10.5,font='Roman',align=0,name=None,scale=100):
 global serial
 serial+=1;name=name or 'p%d-text-%04d'%(s.currentPage()+26,serial)
 scale=min(scale,(w-1.5)/max(measure(t,size,font),.1)*100)
 key=(size,font,align,round(scale,4));lead=size*1.25
 if key not in styles:
  sty='Jordan '+str(len(styles)+1)
  s.createCharStyle(name=sty+' character',font=FONT[font],fontsize=size,fillcolor='Black',language='en_US',scaleh=scale/100)
  s.createParagraphStyle(name=sty,charstyle=sty+' character',linespacingmode=0,linespacing=lead,alignment=align,gapbefore=0,gapafter=0)
  styles[key]=sty
 o=s.createText(x,y-lead,w,lead+size*.65+3,name);s.setText(t,o);s.setParagraphStyle(styles[key],o)
 s.setTextDistances(0,0,0,0,o);s.setFirstLineOffset(s.FLOP_LINESPACING,o);s.setTextFlowMode(o,0);s.layoutText(o)
 for attempt in range(8):
  if not s.textOverflows(o) and s.getTextLines(o)==1:break
  scale*=.98;s.setTextScalingH(scale,o);s.layoutText(o)
 for ital in ['i. e.','(a)','(b)','(c)','(d)','(e)']:
  if ital in t:
   s.selectText(t.index(ital),len(ital),o);s.setFont(FONT['Italic'],o);s.selectText(0,0,o)
 s.layoutText(o)
 for attempt in range(10):
  if not s.textOverflows(o) and s.getTextLines(o)==1:break
  scale*=.97;s.setTextScalingH(scale,o);s.layoutText(o)
 frames.append(dict(name=o,page=s.currentPage()+26,text=t,x=x,baseline=y,width=w,size=size,font=font,scale=scale,alignment=align))
 return o
def center(t,y,size=10.5,font='Roman'):return text(t,LEFT,y,522,size,font,1)
def rule(x,y,x1,y1,width=.4):
 o=s.createLine(x,y,x1,y1);s.setLineColor('Black',o);s.setLineWidth(width,o);s.setTextFlowMode(o,0);rules.append(o)
def rectangle(x,y,w,h,width=.4):
 rule(x,y,x+w,y,width);rule(x+w,y,x+w,y+h,width);rule(x+w,y+h,x,y+h,width);rule(x,y+h,x,y,width)
def title_page():
 center('Manufacture of Mark VIII Tanks',75,26.5)
 center('at Rock Island Arsenal',106,26.5)
 center('By',129,11,'Italic');center('HARRY B. JORDAN',154,14)
 center('Charter Member A. O. A.',165,7);rule(274,178,338,178,.4)
 text('E',45,222,29,37)
 center('Col. Harry B. Jordan',608,7.4)
 center('Commanding Officer Rock Island Arsenal',619,7.2)
 # The inset congratulatory letter is editable, including its signature.
 x,y,w,h=175,636,259,130;rectangle(x,y,w,h,.35)
 def l(t,xx,yy,ww,align=0,font='Roman',size=7.2):return text(t,xx,yy,ww,size,font,align)
 l('June 14, 1920.',327,653,86,2)
 l('Colonel H. B. JORDAN,',188,662,197,size=7.1)
 l('Rock Island Arsenal,',204,671,196)
 l('Rock Island, Ill.',235,679,179)
 l('Dear Jordan:',188,692,197)
 l(D['letter'][5],240,701,181,4)
 for j,t in enumerate(D['letter'][6:9]):l(t,188,710+j*9,232,0 if j==2 else 4)
 l('Sincerely yours,',255,737,165,1)
 l('[Signed]',197,748,59)
 l('C. C. WILLIAMS,',312,748,107,1)
 l(D['letter'][-1],270,757,151,2,'Italic',7)
 center('27',784,9)
def main():
 missing=set(FONT.values())-set(s.getFontNames())
 if missing:raise RuntimeError('Install bundled fonts: '+str(missing))
 for name in ['build_error.txt','data/build_success.json']:
  if (ROOT/name).exists():(ROOT/name).unlink()
 s.newDocument((W,H),(45,45,40,34),s.PORTRAIT,27,s.UNIT_POINTS,s.PAGE_2,1,7)
 s.setInfo('Harry B. Jordan','Manufacture of Mark VIII Tanks at Rock Island Arsenal — '+R['release_id'],'Editable reconstruction of Army Ordnance, July–August 1920, pp. 27–33. Original line sequence and folios; photographs from supplied repository scans.')
 s.setRedraw(False)
 for page in range(27,34):
  s.gotoPage(page-26)
  if page==27:title_page()
  elif page in [28,29]:center(str(page),845,9)
  else:
   center('ARMY ORDNANCE' if page%2==0 else 'MARK VIII TANKS',46,10.5)
   text(str(page),LEFT if page%2==0 else W-LEFT-32,46,32,11,align=0 if page%2==0 else 2)
   rule(LEFT,53,W-LEFT,53,.35)
  for a in [a for a in A if a['page']==page]:
   x,y,w,h=a['normalized_box'];x=LEFT+x*SX;y=TOP+y*SX;w*=SX;h*=SX
   # Preserve the rectified image aspect; avoid any second independent scaling.
   h=w*a['size'][1]/a['size'][0]
   o=s.createImage(x,y,w,h,a['id']);s.loadImage(str(ROOT/'assets'/a['asset']),o);s.setScaleImageToFrame(True,True,o);s.setTextFlowMode(o,0)
   rectangle(x-1,y-1,w+2,h+2,.4);images.append(dict(name=o,page=page,asset=a['asset'],x=x,y=y,width=w,height=h))
  for r in [r for r in LAY if r['page']==page]:
   t=r['text'];x=LEFT+r['frame_x']*SX;y=TOP+r['y']*SX;w=r['frame_width']*SX
   if page==33 and r['region']=='R' and 1<=r['index']<=4:
    vals=[('45 machinists,','30 heaters,'),('65 specialists,','100 assemblers,'),('30 riveters,','300 skilled laborers,'),('30 buckers,','200 laborers,')][r['index']-1]
    text(vals[0],x,y,113);text(vals[1],x+115,y,140);continue
   if r['heading']:text(t,x,y,w,10.8,'Italic' if t=='Tests' else 'Bold',1)
   else:text(t,x,y,w,10.5,align=r['align'])
  if page in [28,29,30]:
   a=[a for a in images if a['page']==page][0];yy=a['y']+a['height']+11
   text(D['captions'][str(page)][0],LEFT,yy,522,7.0 if page!=30 else 6.85,align=2 if page==28 else 0)
  if page==33:rule(262,285,350,285,.4)
 s.setRedraw(True)
 (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
 errs=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
 if errs:raise RuntimeError('Overflow/multiline: '+str(errs))
 path=ROOT/R['sla'];s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
 reopen_fits=[]
 for cycle in range(8):
  for f in frames:s.layoutText(f['name'])
  fit=[f for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
  if not fit:break
  for f in fit:
   f['scale']*=.98;s.selectText(0,len(f['text']),f['name']);s.setTextScalingH(f['scale'],f['name']);s.selectText(0,0,f['name']);s.layoutText(f['name'])
   reopen_fits.append(dict(name=f['name'],cycle=cycle,scale=f['scale']))
  s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
 errs2=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1 or s.getAllText(f['name'])!=f['text']]
 if errs2:
  details=[dict(f,overflow=s.textOverflows(f['name']),lines=s.getTextLines(f['name']),actual=s.getAllText(f['name'])) for f in frames if f['name'] in errs2]
  (ROOT/'data/reopen_errors.json').write_text(json.dumps(details,ensure_ascii=False,indent=2))
  raise RuntimeError('Reopen mismatch: '+str(errs2))
 s.saveDocAs(str(path))
 pdf=s.PDFfile();pdf.file=str(ROOT/R['pdf']);pdf.pages=list(range(1,8));pdf.version=15;pdf.compress=True;pdf.compressmtd=2;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.outdst=0;pdf.bookmarks=True;pdf.fonts=[];pdf.subsetList=list(FONT.values());pdf.save();del pdf
 (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
 (ROOT/'data/native_images.json').write_text(json.dumps(images,indent=2))
 (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(frames),images=len(images),overflow_before=errs,overflow_after_reopen=errs2,reopen_fits=reopen_fits,minimum_horizontal_scale=min(f['scale'] for f in frames),frames_below_85=[f for f in frames if f['scale']<85]),indent=2))
 s.closeDoc();(ROOT/'data/build_success.json').write_text(json.dumps(R,indent=2))
try:main()
except BaseException:
 (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
 if os.environ.get('JORDAN_BATCH')=='1':os._exit(0)
