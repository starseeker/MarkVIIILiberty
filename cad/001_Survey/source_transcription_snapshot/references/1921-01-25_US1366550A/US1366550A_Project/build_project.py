"""Execute with Scribus 1.6.x (Script > Execute Script) to rebuild this edition.
Save manual edits under a different filename before rebuilding.
"""
from pathlib import Path
import json,os,traceback
import scribus as s
ROOT=Path(__file__).resolve().parent
R=json.loads((ROOT/'data/release.json').read_text())
D=json.loads((ROOT/'data/reviewed_transcription.json').read_text())
A=json.loads((ROOT/'data/artwork.json').read_text())
MET=json.loads((ROOT/'fonts/metrics.json').read_text())
FONT={'Roman':'C059 Roman','Bold':'C059 Bold','Italic':'C059 Italic','Sans':'Nimbus Sans Bold'}
FILES={'Roman':'C059-Roman','Bold':'C059-Bold','Italic':'C059-Italic','Sans':'NimbusSans-Bold'}
frames=[];art=[];styles={};serial=0
def measure(t,size,font):return sum(MET[FILES[font]].get(c,.5) for c in t)*size
def text(t,x,y,w,size=10.3,font='Roman',align=0,name=None,scale=100):
    global serial
    serial+=1;name=name or 'page%d-text-%03d'%(s.currentPage(),serial)
    scale=min(scale,(w-2.0)/max(measure(t,size,font),.1)*100)
    key=(size,font,align,round(scale,4));lead=size*1.2
    if key not in styles:
        sty='Patent style '+str(len(styles)+1)
        s.createCharStyle(name=sty+' character',font=FONT[font],fontsize=size,fillcolor='Black',language='en_US',scaleh=scale/100)
        s.createParagraphStyle(name=sty,charstyle=sty+' character',linespacingmode=0,linespacing=lead,alignment=align,gapbefore=0,gapafter=0)
        styles[key]=sty
    o=s.createText(x,y-lead,w,lead+size*.65+3,name)
    s.setText(t,o);s.setParagraphStyle(styles[key],o);s.setTextDistances(0,0,0,0,o)
    s.setFirstLineOffset(s.FLOP_LINESPACING,o);s.setTextFlowMode(o,0);s.layoutText(o)
    for attempt in range(12):
        if not s.textOverflows(o) and s.getTextLines(o)==1:break
        scale*=.98;s.setTextScalingH(scale,o);s.layoutText(o)
    frames.append(dict(name=o,page=s.currentPage(),text=t,x=x,baseline=y,width=w,size=size,font=font,scale=scale,alignment=align))
    return o
def center(t,y,size=10.3,font='Roman'):return text(t,53,y,506,size,font,1)
def rule(x,y,x1,y1,width=.35):
    o=s.createLine(x,y,x1,y1);s.setLineColor('Black',o);s.setLineWidth(width,o);s.setTextFlowMode(o,0)
def drawing_header(page):
    text('H. W. ALDEN.',225,111,162,8.7,'Sans',1)
    text('TANK.',225,124,162,7.4,'Sans',1)
    text('APPLICATION FILED DEC. 14, 1918.',193,134.5,226,5.8,'Sans',1)
    text('1,366,550.',101,150,165,15.2,'Bold')
    text('Patented Jan. 25, 1921.',361,152,170,11.4,'Bold',2)
    text('2 SHEETS-SHEET '+str(page)+'.',388,162,143,6.2,'Bold',2)
def specification_header():
    center('UNITED STATES PATENT OFFICE.',85,21,'Bold')
    rule(259,94,353,94,.4)
    text('HERBERT W. ALDEN, OF THE UNITED STATES ARMY, ASSIGNOR TO NEWTON D.',68,114,490,9.2,'Bold')
    text('BAKER, SECRETARY OF WAR OF THE UNITED STATES OF AMERICA, TRUS-',85,124,474,9.2,'Bold')
    text('TEE.',85,134,60,9.2,'Bold')
    center('TANK.',145,8.7,'Bold')
    text('1,366,550.',53,166,140,11,'Bold')
    text('Specification of Letters Patent.',222,166,171,8,'Bold',1)
    text('Patented Jan. 25, 1921.',394,166,165,10.3,'Bold',2)
    center('Application filed December 14, 1918.  Serial No. 266,817.',184,8.2,'Bold')
    center('(FILED UNDER THE ACT OF MARCH 3, 1883, 22 STAT. L., 625.)',202,8.2,'Bold')
def body(page):
    base=222 if page==3 else 111
    for col in ['L','R']:
        rows=D[str(page)+col];xx=68 if col=='L' else 314;w=230
        start=1 if col=='L' else (55 if page==3 else 49)
        for i,r in enumerate(rows):
            indent=11 if r['indent'] else 0
            align=0 if r['last'] else 4
            italic=page==3 and col=='L' and i==0
            if italic:align=0
            text(r['text'],xx+indent,base+i*10,w-indent,10.7,'Italic' if italic else 'Roman',align,name=f'p{page}_{col}_line{start+i:03d}')
            if (start+i)%5==0:
                text(str(start+i),47 if col=='L' else 550,base+i*10,17,6.5,'Roman',2 if col=='L' else 0,name=f'p{page}_number{start+i:03d}')
    if page==4:text('HERBERT W. ALDEN.',363,586,196,10.3,'Bold',2)
def main():
    missing=set(FONT.values())-set(s.getFontNames())
    if missing:raise RuntimeError('Install bundled fonts: '+str(missing))
    for name in ['build_error.txt','data/build_success.json']:
        if (ROOT/name).exists():(ROOT/name).unlink()
    s.newDocument((612.,792.),(32,32,32,26),s.PORTRAIT,1,s.UNIT_POINTS,s.PAGE_1,0,4)
    s.setInfo('Herbert W. Alden','U.S. Patent 1,366,550 - Tank - '+R['release_id'],'January 25, 1921. Four-page source-faithful reconstruction, with editable printed text and source-traced vector drawings.')
    s.setRedraw(False)
    for page in range(1,5):
        s.gotoPage(page)
        if page<=2:
            drawing_header(page)
            for a in [a for a in A if a['page']==page]:
                s.placeSVG(str(ROOT/'assets'/a['svg']),a['x']+a['ink_offset'][0],a['y']+a['ink_offset'][1])
                selected=[s.getSelectedObject(i) for i in range(s.selectionCount())]
                art.append(dict(**a,objects=selected))
                s.deselectAll()
        elif page==3:specification_header();body(page)
        else:
            text('2',53,85,25,12,'Bold');center('1,366,550',85,10,'Bold');body(page)
    s.setRedraw(True)
    errors=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
    if errors:raise RuntimeError('Text overflow: '+str(errors))
    path=ROOT/R['sla'];s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
    refits=[]
    for cycle in range(10):
        for f in frames:s.layoutText(f['name'])
        fit=[f for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1]
        if not fit:break
        for f in fit:
            f['scale']*=.98;s.selectText(0,len(f['text']),f['name']);s.setTextScalingH(f['scale'],f['name']);s.selectText(0,0,f['name']);s.layoutText(f['name'])
            refits.append(dict(name=f['name'],cycle=cycle,scale=f['scale']))
        s.saveDocAs(str(path));s.closeDoc();s.openDoc(str(path))
    errors=[f['name'] for f in frames if s.textOverflows(f['name']) or s.getTextLines(f['name'])!=1 or s.getAllText(f['name'])!=f['text']]
    if errors:raise RuntimeError('Reopen text mismatch or overflow: '+str(errors))
    s.saveDocAs(str(path))
    pdf=s.PDFfile();pdf.file=str(ROOT/R['pdf']);pdf.pages=[1,2,3,4];pdf.version=15
    pdf.compress=True;pdf.compressmtd=2;pdf.quality=0;pdf.downsample=0;pdf.resolution=600;pdf.outdst=0
    pdf.bookmarks=True;pdf.fonts=[];pdf.subsetList=list(FONT.values());pdf.save();del pdf
    (ROOT/'data/native_frames.json').write_text(json.dumps(frames,ensure_ascii=False,indent=2))
    (ROOT/'data/native_artwork.json').write_text(json.dumps(art,indent=2))
    (ROOT/'data/native_validation.json').write_text(json.dumps(dict(scribus_version=s.scribus_version,pages=s.pageCount(),editable_text_frames=len(frames),source_traced_artwork=len(art),overflow_after_reopen=errors,reopen_refits=refits,minimum_horizontal_scale=min(f['scale'] for f in frames)),indent=2))
    s.closeDoc();(ROOT/'data/build_success.json').write_text(json.dumps(R,indent=2))
try:main()
except BaseException:
    (ROOT/'build_error.txt').write_text(traceback.format_exc());raise
finally:
    if os.environ.get('PATENT_BATCH')=='1':os._exit(0)
