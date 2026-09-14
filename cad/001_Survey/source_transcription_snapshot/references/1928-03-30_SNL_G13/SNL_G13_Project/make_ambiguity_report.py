#!/usr/bin/env python3
"""Produce the context audit PDF and text report from the recorded decisions."""
from pathlib import Path
import json,io,sys
from xml.sax.saxutils import escape
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor,white
from reportlab.pdfgen import canvas
import proof_fonts
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'audit/ambiguity_audit.json').read_text())
findings=data['findings']; ink=HexColor('#203340'); pale=HexColor('#edf2f4')
styles={
 'title':ParagraphStyle('title',fontName='ProofSans-Bold',fontSize=21,leading=26,textColor=ink,spaceAfter=12),
 'h':ParagraphStyle('h',fontName='ProofSans-Bold',fontSize=12,leading=16,textColor=ink,spaceAfter=8,spaceBefore=7),
 'body':ParagraphStyle('body',fontName='ProofSans',fontSize=9.1,leading=13,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='ProofSans',fontSize=8.1,leading=11,spaceAfter=6),
 'cell':ParagraphStyle('cell',fontName='ProofSans',fontSize=8.5,leading=12),
 'label':ParagraphStyle('label',fontName='ProofSans-Bold',fontSize=8.5,leading=11,spaceAfter=4),
}
def P(t,style='body'):return Paragraph(escape(t).replace('\n','<br/>'),styles[style])
def table(headers,rows,widths):
 t=Table([[P(x,'label') for x in headers]]+[[P(x,'cell') for x in r] for r in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'ProofSans'),('BACKGROUND',(0,0),(-1,0),pale),('VALIGN',(0,0),(-1,-1),'TOP'),
   ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
   ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
   ('LINEBELOW',(0,0),(-1,0),.6,ink),('LINEBELOW',(0,1),(-1,-1),.25,HexColor('#ccd5da'))]))
 return t
def crop(page,box,width=490):
 im=PILImage.open(ROOT/'sources'/f'p{page:03}.jpg').rotate(-90,expand=True).crop(box)
 b=io.BytesIO();im.save(b,format='PNG');b.seek(0)
 return Image(b,width=width,height=width*im.height/im.width,hAlign='LEFT')
def footer(c,d):
 c.setFont('ProofSans',8);c.setFillColor(ink)
 c.drawString(46,767,'SNL G-13 · 1928 · Context audit · 12 September 2026')
 c.drawString(46,26,'References use original printed folios, not PDF page positions.')
 c.drawRightString(566,26,str(d.page))
story=[P('What the complete book resolves','title'),
 P('Ten findings close 13 previous review-log entries. Three require transcription corrections; '
   'six confirm existing readings; one is explained by the book’s own notes. The findings '
   'come from cross-referencing all 7,571 structured table records, the end notes, selected '
   'original photographs, and Plate 16.'),
 P('Three corrections applied','h'),
 table(['Folio','Earlier draft','Verified reading and evidence'],[
  ['43','SH40A1D','SH40AD. The bushing photograph and the matching chain component on 61 agree.'],
  ['66','SH975C','SH976C. The clip photograph and the bolt-use reference on 31 agree. SH975C remains a separate hose code.'],
  ['97','First rivet: 1½″ long','1⅛″ long, ½″ diameter. The four rivets match the individual listing on 169.'],
 ],[42,114,364]),Spacer(1,12),
 P('A repeated component code that is correct','h'),
 P('SH599A occurs in both left and right exhaust-manifold assemblies on 122–123. '
   'Note (go), page 309, explains that the components are identical and are assembled '
   'at 61° to form the noninterchangeable left and right units. This resolves the '
   'apparent duplication without changing the historical text.'),
 P('What “resolved” means here','h'),
 P('A confirmed reading is a statement about what the source says. It is not independent '
   'verification of a part’s manufactured dimensions. Conflicting printed values, uncertain '
   'glyphs and blank source cells are retained. This targeted audit does not replace a '
   'fresh, independent proofread of every page.'),
 P('The updated log has 113 open entries and 99 resolved entries. Thirteen older entries '
   'were closed; one newly noticed source discrepancy was added. Several log entries concern '
   'general proofreading or layout, so these counts are not counts of individual unreadable characters.','small'),PageBreak()]

story += [P('Photographic evidence for the corrections','title'),
 P('These are crops of the original photographs, rotated only for reading. No letters or '
   'numbers have been reconstructed in the images. Supporting folios remain in sources/.','small')]
evidence=[
 ('43 → SH40AD','The individual bushing code; compare the same code in the chain list on 61.',
  [(43,(690,704,1570,775)),(61,(904,526,1510,560))]),
 ('66 → SH976C','Both clips remain without quantities. The bolt-use list on 31 names SH976A and SH976C.',
  [(66,(875,1033,1525,1085)),(31,(850,470,1620,530))]),
 ('97 → 1⅛″','The first rivet line on 97; the individual entry on 169 explicitly includes four for this frame.',
  [(97,(830,132,1520,172)),(169,(803,850,1580,954))]),
]
for title,desc,images in evidence:
 story += [P(title,'h'),P(desc,'small')]
 for page,box in images:
  story += [P(f'Printed page {page}','label'),crop(page,box),Spacer(1,7)]
story += [PageBreak(),P('Existing readings now corroborated','title')]
for id in ['A04','A06','A07','A08','A09','A10']:
 f=next(x for x in findings if x['id']==id)
 story += [KeepTogether([P(f['reading']+' | '+', '.join(map(str,f['pages'])),'h'),P(f['evidence'])])]
story += [PageBreak(),P('Context helps, but does not settle everything','title'),
 table(['Issue','What the complete book adds','Decision'],[
  ['LQ196A stud\n58, 59, 105, 237','The individual listing on 237 joins 58 and 105 in giving 1 9/16″. Page 59 gives 1 3/16″.','Keep both printed lengths; stronger evidence favors 1 9/16″ as the intended specification.'],
  ['NBIB / NB1B\n93, 107, 223','Two later uses identify No. 2 strap fastener NB1B. The glyph on 93 still looks like I.','Record the likely identity; retain the literal uncertain reading on 93.'],
  ['SH642B spring\n138, 219','Both give I.D. 13/16″, but O.D. is 1½″ on 138 and ½″ on 219. Both appear to say 1″ thick.','No usable physical dimensions can be inferred safely from this conflict.'],
  ['Valve-spring collars\n67, 79','LQ296A and LQ297A have reversed upper/lower descriptions between the two lists.','Preserve the discrepancy; the notes do not supply an explicit correction.'],
  ['—Q512B wire\n20, 57, 90, 276','Related LQ512A/C/D/E codes and the five-inch wire usage support a likely LQ512B identity.','The missing/ambiguous initial L is not independently repeated. Leave the source reading flagged.'],
  ['A6951 note (a)\n165, 308','The ring entry points to an S hook. Note (d) explains that replacement; no standalone note (a) appears.','Probable erroneous note reference; retain (a), with the explanation recorded separately.'],
 ],[96,236,188]),Spacer(1,10),
 P('A new discrepancy to retain','h'),P('The plain tachometer-shaft bushing is D22920 on 44 and '
   'D29920 on 110. Both forms are visible. Confirming the neighboring flanged bushing D22921 '
   'does not settle which plain-bushing number was intended.'),
 P('Prices still needing better evidence','h'),P('The tentative prices on 3, 6, 15, 37, 147, 197, '
   '225, 229 and 245 were not resolved by a sufficient repeated same-item price. Assembly '
   'costs and neighboring price patterns are not substitutes for the original digits.','small')]
doc=SimpleDocTemplate(str(ROOT/'Transcription_Ambiguity_Audit.pdf'),pagesize=(612,792),
 leftMargin=46,rightMargin=46,topMargin=49,bottomMargin=44,
 title='SNL G-13 - Transcription ambiguity audit',author='SNL G-13 reconstruction project')
doc.build(story,onFirstPage=footer,onLaterPages=footer,
 canvasmaker=lambda *a,**k:canvas.Canvas(*a,**(k|{'initialFontName':'ProofSans'})))
md=['# Transcription ambiguity audit','',
 'Date: 2026-09-12. Original printed folios are used throughout.','',
 '13 previous log entries closed across 10 findings: 3 corrected cells, 6 corroborated readings, '
 'and 1 explained component relationship. One new original-source discrepancy was added. '
 'The log now has 113 open and 99 resolved entries.','']
for f in findings:
 md += ['## '+f['id']+' - '+f['title'], '',f"**{f['status']}** · Folios {', '.join(map(str,f['pages']))} · {f['reading']}",'',f['evidence'],'']
md+=['## Further context, still open','']
for i,(title,explanation) in data['open_context_updates'].items():md += [f'**Baseline R{int(i)+1:03d}: {title}.** '+explanation,'']
md+=['## Newly recorded source discrepancy','',
 'The adjacent plain tachometer-shaft bushing is D22920 on 44 but D29920 on 110. Both photographs clearly support their respective readings. Both source forms are retained; this is separate from the confirmed flanged-bushing code D22921.','']
md+=['## Scope and reproducibility','',data['summary']['scope'],
 'The machine-readable audit preserves a disposition and exact-code candidate-page map for each '
 'of the 125 earlier flags. Candidate matches are discovery aids, not automatically accepted readings.',
 '`audit/review_before_context_audit.json` preserves the previous review log. '
 '`audit_context.py` regenerates the review update. `apply_context_corrections.py` applies '
 'the three named native-cell corrections and verifies all text frames in Scribus. '
 '`audit/context_delivery_validation.json` records final preservation and export checks.','']
(ROOT/'TRANSCRIPTION_AUDIT.md').write_text('\n'.join(md))
print('Wrote Transcription_Ambiguity_Audit.pdf and TRANSCRIPTION_AUDIT.md')
