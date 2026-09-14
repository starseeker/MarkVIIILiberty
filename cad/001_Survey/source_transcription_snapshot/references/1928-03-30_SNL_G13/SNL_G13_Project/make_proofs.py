#!/usr/bin/env python3
"""Add original-folio navigation, render pages, and make geometry comparisons.

Requires Pillow, PyMuPDF and ReportLab. Run after the native Scribus build.
Comparison images are compact JPEG previews; delivered corrected assets are PNG.
"""
from pathlib import Path
import io, json, textwrap, sys, tempfile
import fitz
from PIL import Image
from reportlab.pdfgen import canvas
import proof_fonts
from reportlab.lib.utils import ImageReader
from project_sequence import LABELS
ROOT=Path(__file__).resolve().parent

def preview(path):
 im=Image.open(path).convert('RGB');im.thumbnail((1800,1800))
 b=io.BytesIO();im.save(b,format='JPEG',quality=94,subsampling=0);b.seek(0)
 return im.size,ImageReader(b)

def main():
 (ROOT/'proofs').mkdir(exist_ok=True)
 inventory=json.loads((ROOT/'page_inventory.json').read_text())
 supplied=sorted([r for r in inventory['pages'] if r['pilot_page']],key=lambda r:r['pilot_page'])
 assert [r['printed_label'] for r in supplied]==LABELS
 pdf=ROOT/'SNL_G13_Pilot.pdf';d=fitz.open(pdf)
 assert len(d)==len(LABELS)
 d.set_toc([[1,f"{r['printed_label']} — {r['page_type'].capitalize()}",r['pilot_page']] for r in supplied])
 d.set_page_labels([dict(startpage=r['pilot_page']-1,prefix=r['printed_label'],style='') for r in supplied])
 with tempfile.TemporaryDirectory(prefix='snl-g13-navigation-') as temp:
  out=Path(temp)/'navigation.pdf'
  d.save(out,garbage=4,deflate=True);d.close();pdf.write_bytes(out.read_bytes())
 d=fitz.open(pdf);results=[]
 for i,p in enumerate(d):
  r=supplied[i];stem=Path(r['source_filename']).stem
  p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(ROOT/'proofs'/f'printed-{stem}.png')
  result=dict(pilot_page=i+1,printed_label=r['printed_label'],
   size_points=[p.rect.width,p.rect.height],text_characters=len(p.get_text()),image_count=len(p.get_images()),
   fonts=[dict(name=f[3],embedded=bool(d.extract_font(f[0])[3])) for f in p.get_fonts()])
  assert result['size_points']==([1296.,648.] if r['page_type']=='foldout' else [432.,648.])
  assert all(f['embedded'] for f in result['fonts'])
  results.append(result)
 (ROOT/'pdf-validation.json').write_text(json.dumps(results,indent=2));d.close()
 if '--pilot-only' in sys.argv:
  print(f'PASS: {len(LABELS)} pilot pages rendered; navigation, expected sizes and embedded fonts verified.')
  return
 geometry_proof()

def geometry_proof():
 transforms=json.loads((ROOT/'calibration/figure_transforms.json').read_text())
 checks=json.loads((ROOT/'calibration/line_validation.json').read_text())['pages']
 audit={r['page']:r for r in json.loads((ROOT/'calibration/plate_review.json').read_text())['rows']}
 c=canvas.Canvas(str(ROOT/'Figure_Geometry_Proof.pdf'),pagesize=(1000,720),initialFontName='ProofSans')
 c.setTitle('SNL G-13 — reviewed figure geometry comparisons')
 for page,cfg in transforms.items():
  label='Face p. 277 (foldout)' if page=='277_foldout' else f'Printed page {page}'
  c.setFont('ProofSans-Bold',17)
  c.drawString(28,690,f"{label} — Plate{'s' if len(cfg['plates'])>1 else ''} {', '.join(map(str,cfg['plates']))}")
  c.setFont('ProofSans',10);c.drawString(28,671,cfg['method'].capitalize()+'.')
  constraints=ROOT/'proofs'/f'p{page}-constraints.png'
  left=constraints if constraints.exists() else ROOT/'proofs'/f'p{page}-before.png'
  for x,path,title in [(28,left,'Source: red = fitted, blue = reserved checks' if cfg.get('heldout_count') else 'Source region: red lines mark constraints' if constraints.exists() else 'Source region'),
                        (516,ROOT/'assets'/f'p{page}-geometry.png','Corrected artwork')]:
   c.setFont('ProofSans-Bold',11);c.drawString(x,648,title)
   (iw,ih),im=preview(path);factor=min(456/iw,482/ih);w,h=iw*factor,ih*factor
   c.drawImage(im,x+(456-w)/2,151+(482-h)/2,width=w,height=h)
  notes=[cfg['reference'],cfg['status'].capitalize()+'.', 'All-plate review: '+audit[page]['decision']+'.']
  if cfg.get('heldout_count'):
   notes.append(f"Reserved validation: {cfg['heldout_count']} labels/lines; RMS deviation {cfg['heldout_source_rms_pixels']:.2f} to {cfg['heldout_corrected_rms_pixels']:.2f} source pixels.")
  if page in checks:
   row=checks[page];err=max(v['p95_absolute_deviation_pixels'] for v in row['output_edge_checks'].values())
   notes.append(f"Source border bow: up to {row['source_max_bow_pixels']:.1f} pixels. Corrected border deviation (95th percentile): at most {err:.2f} pixels.")
  y=131;c.setFont('ProofSans',9)
  for note in notes:
   for line in textwrap.wrap(note,165):c.drawString(28,y,line);y-=11
  c.setFont('ProofSans',9)
  c.drawString(28,33,'Selected lines constrain the fit; these checks do not independently establish interior dimensions or original aspect ratio.')
  c.drawString(28,19,'Preview images only. Unmodified JPEGs, lossless corrected PNGs, line overlays and transform records are included in the project.')
  c.showPage()
 c.save()
 d=fitz.open(ROOT/'Figure_Geometry_Proof.pdf');assert len(d)==len(transforms)
 for i,p in enumerate(d):
  p.get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(ROOT/'proofs'/f'geometry-{i+1:02}.png')
 d.close()
 print(f'PASS: {len(transforms)} geometry comparisons rendered with embedded report fonts.')
if __name__=='__main__':
 geometry_proof() if '--geometry-only' in sys.argv else main()
