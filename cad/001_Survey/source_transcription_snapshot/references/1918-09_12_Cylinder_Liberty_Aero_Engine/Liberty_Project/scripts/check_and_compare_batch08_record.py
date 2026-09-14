"""Validate native exports, add PDF folio labels/bookmarks, and build comparison.
Uses PyMuPDF and Pillow; the exported manual pages remain Scribus-produced.
"""
from pathlib import Path
import json,hashlib,io,re,unicodedata
from collections import Counter
import fitz
from PIL import Image
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
R=json.loads((ROOT/'data/release.json').read_text());pdfpath=ROOT/R['pdf']
src=fitz.open(pdfpath)
labels=[dict(startpage=0,prefix='Cover',style=''),dict(startpage=1,prefix='Inside cover',style=''),dict(startpage=2,prefix='Title',style=''),dict(startpage=3,prefix='Frontispiece',style=''),dict(startpage=4,prefix='',style='D',firstpagenum=3)]
labels += [dict(startpage=124,prefix='Blank — scan 0125',style=''),dict(startpage=125,prefix='',style='D',firstpagenum=123),dict(startpage=127,prefix='Blank — scan 0128',style=''),dict(startpage=128,prefix='',style='D',firstpagenum=125)]
labels += [dict(startpage=148,prefix='Blank — scan 0149',style=''),dict(startpage=149,prefix='',style='D',firstpagenum=145),dict(startpage=150,prefix='Blank — scan 0151',style=''),dict(startpage=151,prefix='',style='D',firstpagenum=146),dict(startpage=152,prefix='Blank — scan 0153',style=''),dict(startpage=153,prefix='',style='D',firstpagenum=147),dict(startpage=155,prefix='Blank — scan 0156',style=''),dict(startpage=156,prefix='',style='D',firstpagenum=149),dict(startpage=158,prefix='Blank — scan 0159',style=''),dict(startpage=159,prefix='',style='D',firstpagenum=151)]
src.set_page_labels(labels)
src.set_toc([[1,'Cover',1],[1,'Title',3],[1,'The Liberty Engine — frontispiece',4],[1,'Table of contents',5],[1,'Introductory note — p5',7],[1,'Index of illustrations — pp6–8',8],[1,'Leading particulars — pp8–10',10],[1,'General description — p11',13],[2,'Cylinders — p12',14],[2,'Pistons — p13',15],[2,'Connecting rods — p15',17],[2,'Crankshaft — p17',19],[2,'Base chamber — p18',20],[2,'Valves — p23',25],[2,'Camshafts and valve gear — p25',27],[2,'Distribution gear — p26',28],[2,'Cooling system — p28',30],[2,'Starter — p30',32],[1,'Lubrication — p31',33],[2,'Oil pumps — p31',33],[2,'Main and big end bearings — p36',38],[2,'Gudgeon pins — p37',39],[2,'Camshaft lubrication — p37',39],[2,'Thrust and generator drive bearings — p40',42],[1,'Carburation — p42',44],[2,'Zenith carburettors — p43',45],[3,'Zenith altitude control — p48',50],[2,'Claudel-Hobson H.C. 7 — p49',51],[3,'Diffuser adjustments — p55',57],[3,'Fitting notes — p56',58],[3,'Possible causes of trouble — p57',59],[3,'Claudel altitude control — p57',59],[3,'Use of the vacuum control — p58',60],[1,'Ignition — p61',63],[2,'Generator — p61',63],[2,'Voltage regulator — p64',66],[2,'Switchboard — p67',69],[2,'Battery — p69',71],[3,'Battery preparation — p71',73],[3,'Battery maintenance — p71',73],[3,'Fitting the battery — p73',75],[2,'Ignition units — p76',78],[3,'Contact breakers — p79',81],[3,'High tension distributor — p81',83],[3,'High tension cables — p84',86],[3,'Timing and control gear — p87',89],[2,'Possible ignition troubles — p89',91],[2,'Daily ignition routine — p92',94],[2,'Weekly and monthly routine — p93',95],[1,'Running instructions — p94',96],[2,'Maximum engine speeds — p94',96],[2,'New engine precautions — p95',97],[2,'Oil and cooling — pp95–96',97],[2,'Starting and running — pp96–97',98],[2,'Smoky exhaust — p97',99],[2,'After flight and periodic attention — p98',100],[1,'Dismantling and reassembling — p100',102],[2,'Preliminary notes — p100',102],[2,'Accessibility of individual components — p101',103],[2,'General overhaul — p103',105],[3,'Dismantling sequence — p104',106],[3,'Notes on dismantling — p105',107],[2,'Reassembly of units — p109',111],[3,'Camshaft bearings — pp110–111',112],[3,'Oil and water pumps — p112',114],[3,'Cylinders and pistons — pp113–115',115],[3,'Crankshaft and connecting rods — p115',117],[2,'Notes on re-erection — p116',118],[2,'Valve timing instructions — p120',122],[3,'Timing data and cylinder numbering — p120',122],[3,'Timing marks — pp121–123',123],[3,'Distribution timing foldout — p123',126],[3,'Timing methods — pp124–128',127],[3,'New camshaft or camshaft gear — p126',130],[3,'Timing without the marks — p127',131],[2,'Reassembling notes continued — p129',133],[1,'Possible troubles — p130',134],[2,'Difficulty in starting and loss of power — p130',134],[2,'Overheating and lubrication troubles — p132',136],[1,'Installation of Liberty engine — p133',137],[2,'Engine mounting and controls — p133',137],[2,'Petrol system — p134',138],[2,'Lubrication system — p135',139],[2,'Cooling system — p136',140],[2,'Cowling, exhaust and wiring — p137',141],[1,'C. C. synchronizing gear — pp138–139',142],[1,'Standard fits and clearances — pp140–141',144],[1,'Appendix — carburettor controls and drawings',146],[2,'Adjusting Zenith controls — p142',146],[2,'Carburettor control drawings — p143',147],[2,'Installation: front elevation — p144',148],[2,'Installation: rear elevation foldout — p145',150],[2,'Installation: side elevation foldout — p146',152],[2,'Installation: plan view foldout — p147',154],[2,'Rear elevation — p148',155],[2,'Transverse section through cylinders — p149',157],[2,'Front elevation — p150',158],[2,'Longitudinal section foldout — p151',160]])
tmp=ROOT/'_labelled.pdf';src.save(tmp,garbage=4,deflate=True);src.close();tmp.replace(pdfpath);src=fitz.open(pdfpath)
assert len(src)==160
frames=json.loads((ROOT/'data/native_frames.json').read_text());by={n:[] for n in range(1,161)}
for f in frames:by[f['page']].append(f)
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t))
mismatches=[];bounds=[]
for n,page in enumerate(src,1):
 expected=Counter(norm(''.join(f['text'] for f in by[n])));actual=Counter(norm(page.get_text()))
 if expected!=actual:mismatches.append(dict(page=n,missing=dict(expected-actual),extra=dict(actual-expected)))
 for b in page.get_text('dict')['blocks']:
  if b['type']==0:
   for l in b['lines']:
    for s in l['spans']:
     x0,y0,x1,y1=s['bbox']
     if x0<-.1 or y0<-.1 or x1>page.rect.width+.1 or y1>page.rect.height+.1:bounds.append(dict(page=n,text=s['text'],bbox=s['bbox']))
tree=etree.parse(str(ROOT/R['sla']));links=[]
for x in tree.findall('.//PAGEOBJECT'):
 if x.get('PFILE'):
  path=Path(x.get('PFILE'));path=path if path.is_absolute() else ROOT/path
  links.append(dict(path=x.get('PFILE'),exists=path.is_file(),relative=not Path(x.get('PFILE')).is_absolute()))
report=dict(pages=len(src),pdf_sha256=hashlib.sha256(pdfpath.read_bytes()).hexdigest(),text_character_mismatches=mismatches,text_outside_pages=bounds,image_links=links,page_labels=src.get_page_labels(),page_dimensions_points=[list(p.rect)[2:] for p in src])
(ROOT/'data/pdf_validation.json').write_text(json.dumps(report,indent=2))
if mismatches or bounds or any(not x['exists'] for x in links):raise RuntimeError('PDF validation failed; inspect data/pdf_validation.json')
# A 20-sheet proof, source on left and the native reconstruction on right.
out=fitz.open();mapping=[]
pagedata={p['leaf']:p for p in json.loads((ROOT/'data/batch08_transcription.json').read_text())['pages']}
for i in range(140,160):
 p=src[i]
 wide=i+1 in [150,152,154,160];panel_width=p.rect.width
 sheet=out.new_page(width=2*panel_width+88,height=759);right=panel_width+61
 meta=pagedata[i+1];label='Blank leaf' if meta['blank'] else 'Printed page '+str(meta['printed_page'])+(' (foldout)' if wide else '')
 sheet.insert_text((26,25),f'LIBERTY ENGINE HANDBOOK | {R["release_id"]} | scan {i+1:04} | {label}',fontsize=9,fontname='helv')
 sheet.insert_text((26,46),'SOURCE SCAN',fontsize=8,fontname='hebo');sheet.insert_text((right,46),'SCRIBUS RECONSTRUCTION',fontsize=8,fontname='hebo')
 im=Image.open(ROOT/'sources'/f'liberty12cylinde00grea_{i+1:04}.jp2').convert('RGB');im.thumbnail((1450,2500));b=io.BytesIO();im.save(b,format='JPEG',quality=92)
 sheet.insert_image(fitz.Rect(26,57,26+panel_width,748),stream=b.getvalue(),keep_proportion=True)
 if not meta['blank']:sheet.show_pdf_page(fitz.Rect(right,57,right+panel_width,748),src,i)
 mapping.append(dict(comparison_page=i-139,source_leaf=i+1,master_page=i+1,label=label,printed_folio=meta['printed_page'],blank=meta['blank'],page_size_points=meta['page_size_points']))
out.save(ROOT/R['comparison'],garbage=4,deflate=True);out.close()
(ROOT/'data/comparison_map.json').write_text(json.dumps(mapping,indent=2))
review=ROOT.parent/'qa';review.mkdir(exist_ok=True)
for n in range(141,161):
 pix=src[n-1].get_pixmap(matrix=fitz.Matrix(2,2));b=pix.tobytes('png');Image.open(io.BytesIO(b)).load();(review/'batch08'/f'final_{n:02}.png').write_bytes(b)
print('160 pages verified; exact per-page native/PDF character inventory matches; no text outside pages. Comparison written.')
