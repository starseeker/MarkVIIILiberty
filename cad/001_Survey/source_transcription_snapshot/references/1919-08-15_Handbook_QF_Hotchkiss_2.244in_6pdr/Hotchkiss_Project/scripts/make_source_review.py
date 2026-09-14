from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from PIL import Image
import io,fitz
ROOT=Path(__file__).resolve().parents[1];(ROOT.parent/'qa').mkdir(parents=True,exist_ok=True);OUT=ROOT/'Hotchkiss_Source_Review_v01.pdf';W,H=864,648
c=canvas.Canvas(str(OUT),pagesize=(W,H));c.setTitle('Hotchkiss handbook - source review and reconstruction v01');c.setAuthor('Digital reconstruction project')
ink=HexColor('#182d39');muted=HexColor('#526675');rulecol=HexColor('#bfd0d7')
normal=ParagraphStyle('normal',fontName='Helvetica',fontSize=11,leading=15,textColor=ink)
small=ParagraphStyle('small',fontName='Helvetica',fontSize=9.5,leading=12.8,textColor=muted)
def para(t,x,y,w,sty=normal):
 p=Paragraph(t,sty);ww,hh=p.wrap(w,H);p.drawOn(c,x,H-y-hh);return hh

def title(t,sub,num):
 c.setFillColor(ink);c.setFont('Helvetica-Bold',23);c.drawString(40,H-48,t)
 para(sub,40,61,W-80,small);c.setStrokeColor(rulecol);c.line(40,H-94,W-40,H-94)
 c.setFont('Helvetica',8.5);c.setFillColor(muted);c.drawString(40,22,'HOTCHKISS HANDBOOK / 1919 / RECONSTRUCTION v01');c.drawRightString(W-40,22,str(num))

def pic(path,x,y,w,h):
 im=Image.open(path).convert('RGB');im.thumbnail((2000,2400),Image.Resampling.LANCZOS)
 iw,ih=im.size;scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;b=io.BytesIO();im.save(b,'PNG')
 c.drawImage(ImageReader(b),x+(w-dw)/2,H-y-dh,dw,dh)

title('A complete edition from two complementary scans','Source assessment, editorial treatment, and checked Scribus output - 13 September 2026',1)
para('The two scans support a 32-page content reconstruction: preliminary matter, printed pages 7-21, photographic Plates A-C, and drawing Plates I-X. The clearer primary scan supplies most content; the second fills four gaps.',40,113,780)
rows=[['Resource','Observed content','Use in v01'],['Primary PDF / 70.0 MB','28 pages; mostly 400 dpi images; Plate I about 600 dpi','Main text, photographs, eight drawings'],['Secondary PDF / 1.91 MB','34 pages; text mostly 300 dpi; artwork about 150 dpi','Document notice, page 3, Plates II and V'],['OCR + JP2 derivatives','Separate derivative sets exist for both source PDFs','OCR starts transcription; source PDF pixels preferred']]
t=Table([[Paragraph(v,small) for v in r] for r in rows],colWidths=[178,327,279]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#eaf0f3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,rulecol),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]));tw,th=t.wrap(784,300);t.drawOn(c,40,H-176-th)
y=190+th
para('<b>Editable reconstruction.</b> 836 native text frames and 97 editable rules cover the wording, tables, contents, and photo captions. Drawings and their labels retain source pixels. C059 approximates the original typography; 6 x 9 inch text pages and landscape plate pages are modern layout choices.',40,y,780)
y+=67
para('<b>Checks.</b> The native document was reopened in Scribus 1.6.1 with zero text overflows. Every editable frame string matches the text extracted from its intended PDF page. All pages were rendered and inspected; every plate is present. The PDF has 32 navigation bookmarks.',40,y,780)
y+=66
para('<b>Remaining limit.</b> Plates II and V retain faint reverse-side printing and paper texture. Their 150 dpi JPEG source limits detail. No replacement geometry, automatic tracing, or guessed lettering has been introduced. Apparent original wording errors are recorded in the project notes.',40,y,780)
url='https://archive.org/details/HandbookForTheQ.F.Hotchkiss2.244Inch6Pdr.6Cwt.MarkIIGunWithTankMounting'
para(f'Sources: <link href="{url}" color="#23617f">Internet Archive item and scan description</link> | <link href="{url.replace("/details/","/download/")}" color="#23617f">Complete file listing</link>. Exact filenames, hashes, and page mappings are bundled in the project. The two final library/barcode and blank-back-cover pages of the secondary scan are omitted.',40,561,780,small)
c.showPage()
for num,src,proof,label,sub in [(2,'primary_06.png',8,'Printed page 7: type and specification table','The wording is reset as native text; the table uses editable labels, values, and leaders.'),(3,'primary_18.png',20,'Printed page 19: dense prose and table','Source line endings are retained; ink marks no longer distort the reconstructed text baselines.')]:
 title(label,sub,num)
 c.setFillColor(muted);c.setFont('Helvetica-Bold',10);c.drawString(40,H-117,'SOURCE SCAN');c.drawString(447,H-117,'SCRIBUS RECONSTRUCTION')
 pic(ROOT/'sources'/src,40,131,376,465)
 d=fitz.open(ROOT/'Hotchkiss_Master_v01.pdf');pix=d[proof-1].get_pixmap(matrix=fitz.Matrix(2,2));tmp=ROOT.parent/'qa'/f'review_native_{proof:02}.png';pix.save(tmp);d.close()
 pic(tmp,447,131,376,465);c.showPage()
title('Plate II: conservative cleanup, visible limitations','The second scan supplies this otherwise missing plate. Faint reverse-side printing is preserved where separation is uncertain.',4)
c.setFillColor(muted);c.setFont('Helvetica-Bold',10);c.drawString(40,H-124,'SECONDARY SOURCE');c.drawString(447,H-124,'CLEANED CANDIDATE IN THE MASTER')
pic(ROOT/'sources/secondary_24.jpeg',40,143,376,317);pic(ROOT/'assets/plate_II.png',447,143,376,317)
para('The treatment normalizes uneven paper tone and modestly increases contrast. All front-side marks remain sampled image content; no hidden lines or lettering have been reconstructed. Plate V has the same source limitation and receives the same treatment.',40,459,780)
para('A sharper scan of these two leaves would offer more improvement than additional thresholding. The package retains the untouched source images and deterministic processing script so that future comparisons or replacements remain traceable.',40,517,780)
c.showPage();c.save();print(OUT)
