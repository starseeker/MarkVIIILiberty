#!/usr/bin/env python3
"""Produce the batch-13 source comparison, using pages 241–251 of the cumulative PDF."""
from pathlib import Path
import argparse,io,json
from PIL import Image
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
ROOT=Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('ReviewSans',str(ROOT/'fonts/comparison/DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('ReviewSans-Bold',str(ROOT/'fonts/comparison/DejaVuSans-Bold.ttf')))
ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,default=ROOT.parent);args=ap.parse_args()
PW,PH=842,595;NAVY=(.12,.20,.26);GRAY=(.35,.39,.42)
def header(c,title,k):
 c.setFillColorRGB(*NAVY);c.setFont('ReviewSans-Bold',17);c.drawString(29,558,title)
 c.setFillColorRGB(*GRAY);c.setFont('ReviewSans',8);c.drawRightString(813,24,f'Mark VIII Handbook | Batch 13 | {k}')
 c.setStrokeColorRGB(.77,.81,.82);c.line(29,544,813,544)
def para(c,text,x,y,width=755,size=10,leading=14):
 c.setFillColorRGB(*NAVY);c.setFont('ReviewSans',size)
 for line in simpleSplit(text,'ReviewSans',size,width):c.drawString(x,y,line);y-=leading
 return y
base=io.BytesIO();c=canvas.Canvas(base,pagesize=(PW,PH),initialFontName='ReviewSans',initialFontSize=10);c.setTitle('Mark VIII handbook: batch 13, source comparisons for printed pages 241–251')
header(c,'Cumulative Scribus checkpoint: pages 1–251',1)
y=514
state=json.loads((ROOT/'PROJECT_STATUS.json').read_text())
items=[('This iteration completes the available scans',f"Eleven index pages, 241–251: 491 entries. The cumulative master has 251 pages, {state['native_text_frames']:,} native text frames and 146 linked artwork assets."),('Editable final index','Entry wording, page references, letter headings, folios, printer signatures and leaders are native Scribus objects. The closing circle on page 251 is a native ellipse. No new raster artwork was needed.'),('Earlier pages are preserved','The exact 240-page v12 master was preserved before appending. Earlier page objects retain content, geometry and style assignments. PDF pages 1–240 are pixel-identical to v12 at 144 dpi.'),('Source readings and review limits','Repeated entries, inconsistent references and the two blank references are retained. C059 and physical trim remain provisional. This preparation review does not replace an independent proofread.'),('Full handbook: ready for review','Scan 126 right ends at printed page 251, with the final W entry and closing circle. No further scans or blank end leaves are present. Use Handbook_Master_001-251_v13.pdf and the cumulative ZIP for further review and refinement.')]


for title,body in items:
 c.setFillColorRGB(*NAVY);c.setFont('ReviewSans-Bold',11);c.drawString(29,y,title);y-=18;y=para(c,body,29,y,size=10,leading=14)-23
c.showPage()
for n in range(241,252):
 header(c,f'Printed page {n} | source and Scribus reconstruction',n-239)
 c.setFont('ReviewSans-Bold',9);c.drawString(30,528,'SOURCE SCAN');c.drawString(438,528,'CUMULATIVE MASTER')
 c.setFont('ReviewSans',7.5);scan=n//2+1;side='right' if n%2 else 'left';c.drawString(30,40,f'MarkVIII{scan:03}.jpg, {side} half')
 c.drawString(438,40,'Working page size and typography are approximate.');c.showPage()
c.save();doc=fitz.open(stream=base.getvalue(),filetype='pdf');master=fitz.open(ROOT/'Handbook_Master_001-251_v13.pdf')
for n in range(241,252):
 scan=n//2+1;im=Image.open(args.source_dir/f'MarkVIII{scan:03}.jpg').convert('RGB').crop((1750,0,3509,2550) if n%2 else (0,0,1750,2550));im.thumbnail((1600,2000),Image.Resampling.LANCZOS)
 b=io.BytesIO();im.save(b,format='JPEG',quality=80,optimize=True)
 p=doc[n-240];p.insert_image(fitz.Rect(28,77,401,539),stream=b.getvalue(),keep_proportion=True);p.show_pdf_page(fitz.Rect(438,77,811,539),master,n-1,keep_proportion=True)
 url='https://github.com/starseeker/MarkVIIILiberty/blob/main/references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/'+f'MarkVIII{scan:03}.jpg'
 p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(28,542,365,560),'uri':url})
doc.set_toc([[1,'Checkpoint and continuity',1]]+[[1,'Printed page '+str(n),n-239] for n in range(241,252)])
out=ROOT/'Handbook_Comparison_241-251_v13.pdf';doc.save(out,garbage=4,deflate=True);print(out.name,out.stat().st_size)
