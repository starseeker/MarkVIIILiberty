#!/usr/bin/env python3
"""Rebuild the sample with Scribus 1.6's Script > Execute Script.

Run inside Scribus, not ordinary Python. Outputs are written beside this script.
The native SLA is also directly editable; running this script is optional.
"""
import json
import os
import traceback
from pathlib import Path
import scribus as s

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 432.0, 648.0  # Provisional 6 x 9 inches; not measured from the object.
ROMAN, BOLD, ITALIC = 'C059 Roman', 'C059 Bold', 'C059 Italic'
frames = []

PLATES = [
    (1, 'Tank, Mark VIII—Right side view', '277'),
    (2, 'Tank, Mark VIII—Longitudinal sectioned view', '(Face p. 277)'),
    (3, 'Tank, Mark VIII—Rear view', '278'),
    (4, 'Tank, Mark VIII—Top view', '278'),
    (5, 'Air pressure pump—Assembled views', '279'),
    (6, 'Control system—Assembled views', '280'),
    (7, 'Tank, Mark VIII—Assembled view', '281'),
    (8, 'Gasoline tanks with pressure system—Assembled view', '282'),
    (9, 'Main turret—Assembled view', '282'),
    (10, 'Tank, Mark VIII—Front view', '283'),
    (11, 'Schematic wiring diagram', '283'),
    (12, 'Engine control rods—Assembled view', '284'),
    (13, 'Camshaft—Assembled view', '285'),
    (14, 'Liberty Engine—Longitudinal section', '286'),
    (15, 'Liberty Engine—Distributer end, assembled view', '287'),
    (16, 'Generator drive shaft—Parts', '288'),
    (17, 'Water Pump—Parts', '289'),
    (18, 'Connecting rods—Assembled view and parts', '290'),
    (19, 'Fan bevel gear drive—Parts', '291'),
    (20, 'Fan bevel box—Assembled view', '292'),
    (21, 'Clutch—Assembled view', '293'),
    (22, 'Transmission—Right half, sectional view', '294'),
    (23, 'Bevel pinion drive—Assembled view', '295'),
    (24, 'Radiator cooling system—Assembled', '296'),
    (25, 'Roller pinion and track drive—Assembled view', '297'),
    (26, 'Track link—Assembled view', '298'),
    (27, 'Track driving wheel—Assembled view', '299'),
    (28, 'Track adjusting wheel—Assembled views', '300'),
    (29, 'Track Roller, with flanges—Assembled view', '301'),
    (30, 'High speed brake band—Assembled view', '302'),
    (31, 'Track brake band—Assembled view', '303'),
    (32, 'Low speed brake band—Assembled view', '304'),
    (33, 'Oil pump—Parts', '305'),
    (34, 'Liberty Engine, transverse section—Assembled view', '306'),
]

def style(name, size, font=ROMAN, leading=None, align=0, tracking=0, features='', tabs=None):
    s.createCharStyle(name=name+' character', font=font, fontsize=size,
                     fillcolor='Black', language='en_US', tracking=tracking,
                     features=features)
    kw = dict(name=name, charstyle=name+' character', linespacingmode=0,
              linespacing=leading or size*1.2, alignment=align,
              gapbefore=0, gapafter=0)
    if tabs is not None:
        kw['tabs'] = tabs
    s.createParagraphStyle(**kw)

def text(name, x, baseline, width, content, sty, leading, lines=1, note=None):
    # First-line offset is explicitly the line spacing, so baseline is repeatable.
    name = s.createText(x, baseline-leading, width, leading*lines+4, name)
    s.setText(content, name)
    s.setParagraphStyle(sty, name)
    s.setTextDistances(0, 0, 0, 0, name)
    s.setFirstLineOffset(s.FLOP_LINESPACING, name)
    s.setTextFlowMode(name, 0)
    if note:
        s.setObjectAttributes([dict(Name='Reconstruction note', Type='string', Value=note,
            Parameter='', Relationship='', RelationshipTo='', AutoAddTo='')], name)
    frames.append((name, lines))
    return name

def rule(name, x, y, width):
    obj = s.createLine(x,y,x+width,y,name)
    s.setLineColor('Black',obj)
    s.setLineWidth(0.5,obj)
    s.setTextFlowMode(obj,0)

def plate_list(name, x, baseline, records):
    numbers='\n'.join('%d.' % row[0] for row in records)
    text(name+'-numbers',x-5,baseline,18,numbers,'Plate numbers',10.55,len(records))
    content='\n'.join('%s\t  %s' % row[1:] for row in records)
    return text(name,x+18,baseline,311.5,content,'Plate rows',10.55,len(records))

def main(export=True):
    for filename in ['build-status.txt', 'build-error.txt']:
        (ROOT/filename).unlink(missing_ok=True)
    missing=set([ROMAN,BOLD,ITALIC])-set(s.getFontNames())
    if missing:
        raise RuntimeError('Install the bundled fonts before rebuilding: '+', '.join(sorted(missing)))
    if s.haveDoc():
        # Opening a new document does not close or discard an existing document.
        pass
    s.newDocument((WIDTH,HEIGHT),(74,28,26,30),s.PORTRAIT,1,s.UNIT_POINTS,s.PAGE_1,0,2)
    s.setInfo('Ordnance Department; digital reconstruction',
        'S. N. L. No. G-13 — Tank, Mk. VIII — pages I–II',
        'Editable reconstruction of two photographs, dated March 30, 1928. '
        'Provisional page size 6 x 9 inches; C059 is a visual approximation. '
        'See README.md for transcription decisions and limits.')
    s.setRedraw(False)
    s.createLayer('Reconstructed print')
    s.setActiveLayer('Reconstructed print')
    style('Running identifier',10.5,BOLD,12.6,tracking=8)
    style('Catalog title',10.7,BOLD,12.5,1,tracking=5)
    style('Catalog subtitle',10.4,BOLD,12.5,1)
    style('Group',9.0,BOLD,11,features='smallcaps',tracking=10)
    style('Department',11.6,ROMAN,14,2)
    style('Dateline',10.6,ITALIC,13,2)
    style('Nomenclature',9.1,BOLD,11,1)
    style('Tank title',11.9,ROMAN,14,1,features='smallcaps')
    style('Parts heading',10.5,ROMAN,13,1)
    style('Body',10.4,ROMAN,12.0)
    style('Body spread',10.4,ROMAN,12.0,4)
    style('Contents heading',10.0,ROMAN,12,1)
    style('Column label',7.4,ROMAN,9)
    style('Right label',7.4,ROMAN,9,2)
    style('Contents rows',9.0,ROMAN,10.55,tabs=[(257,1,'-')])
    style('Class reference',9.0,ROMAN,10.55)
    style('Plate heading',8.5,ROMAN,10,1,features='smallcaps',tracking=8)
    style('Plate numbers',9.0,ROMAN,10.55,2)
    style('Plate rows',9.0,ROMAN,10.55,tabs=[(311,1,'-')])
    style('Price row',9.0,ROMAN,11,tabs=[(329,1,'-')])
    style('Printer imprint',6.6,ROMAN,8)
    style('Folio',8.0,ROMAN,10,1)

    s.gotoPage(1)
    text('I-running-identifier',306,39,104,'S. N. L. No. G–13.','Running identifier',12.6)
    text('I-catalog-title',74,59,329,'THE ORDNANCE CATALOG','Catalog title',12.5,
         note='The torn heading has been restored to THE ORDNANCE CATALOG.')
    text('I-catalog-subtitle',74,72,329,'(Ordnance Provision System)','Catalog subtitle',12.5,
         note='Characters obscured by the tear in Ordnance restored from context.')
    text('I-group',80,84,110,'Group G.','Group',11)
    text('I-department',154,96,220,'ORDNANCE DEPARTMENT,','Department',14)
    text('I-dateline',180,110,223,'Washington, March 30, 1928.','Dateline',13)
    text('I-nomenclature',74,128,329,'Standard Nomenclature List No. G–13','Nomenclature',11)
    text('I-tank-title',74,147,329,'Tank, Mk. VIII','Tank title',14)
    rule('I-upper-rule',223,164,30)
    obj=text('I-parts-heading',74,184,329,'(gam)  parts','Parts heading',13,
         note='Code (gam) is confirmed and explained in the supplied page 310 note.')
    s.selectText(7,5,obj)
    s.createCharStyle(name='Small-cap parts character',font=ROMAN,fontsize=10.5,features='smallcaps',tracking=8)
    s.setCharacterStyle('Small-cap parts character',obj)
    s.selectText(0,0,obj)
    rule('I-lower-rule',223,200,30)
    para=[
        ('For full information relative to Standard Nomenclature Lists, the',85.5,317.5),
        ('procedure followed and the principles employed in their compilation,',74,329),
        ('together with the purposes and uses thereof see Introduction to',74,329),
        ('The Ordnance Catalog.',74,329),
    ]
    for i,(line,x,w) in enumerate(para):
        text('I-introduction-line-%d'%(i+1),x,220+i*12,w,line,
             'Body spread' if i<3 else 'Body',12)
    text('I-contents-heading',74,275,329,'CONTENTS','Contents heading',12)
    text('I-drawing-column',99,281,80,'Drawing','Column label',9)
    text('I-page-column',373,281,30,'Page','Right label',9)
    rows=[('List of Plates','I'),('Major Item','307'),('Parts','2'),('Notes','307'),('Use of Prices','311')]
    text('I-contents-entries',146,291,257.5,'\n'.join(a+'\t  '+b for a,b in rows),'Contents rows',10.55,5)
    text('I-parts-classification',74,312.10,72,'Class 31 Div. 37','Class reference',10.55)
    text('I-list-of-plates-heading',74,350,329,'List of plates','Plate heading',10)
    text('I-plate-number-label',74,353,80,'Plate No.','Column label',9)
    plate_list('I-plates-01-to-23',74,363,PLATES[:23])
    text('I-printer-imprint',85,613,85,'53476—28——1','Printer imprint',8)
    text('I-folio',216,618,45,'I','Folio',10)

    s.gotoPage(2)
    text('II-running-identifier',28,30,160,'S. N. L. No. G–13.','Running identifier',12.6,
         note='Initial S partly clipped/damaged in the photograph; restored from page I.')
    text('II-plate-number-label',28,46,80,'Plate No.','Column label',9)
    text('II-page-column',327,46,30,'Page','Right label',9)
    plate_list('II-plates-24-to-34',28,56,PLATES[23:])
    text('II-unit-price-label',302,178,55,'Unit price','Right label',9)
    text('II-tank-unit-price',28,188,329.5,'ø  Tank, Mk. VIII\t  $45, 052. 24','Price row',11,
         note='The printed slashed-circle mark before Tank is approximated by U+00F8 (ø); '
              'page 307 identifies it as the major-item symbol. Price spacing is approximate.')
    text('II-folio',170,600,45,'II','Folio',10)

    if not export:
        return
    s.setRedraw(True)
    s.redrawAll()
    validation=[]
    for name,expected_lines in frames:
        s.layoutText(name)
        actual=s.getTextLines(name)
        validation.append(dict(frame=name,overflow=bool(s.textOverflows(name)),
            expected_lines=expected_lines,actual_lines=actual,characters=s.getTextLength(name)))
    errors=[r for r in validation if r['overflow'] or r['expected_lines']!=r['actual_lines']]
    (ROOT/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
    if errors:
        raise RuntimeError('Layout checks failed: '+repr(errors))
    s.gotoPage(1)
    s.saveDocAs(str(ROOT/'SNL_G13_Pages_I-II.sla'))
    pdf=s.PDFfile()
    pdf.file=str(ROOT/'SNL_G13_Pages_I-II.pdf')
    pdf.pages=[1,2]
    pdf.version=15
    pdf.fonts=[]
    pdf.subsetList=[ROMAN,BOLD,ITALIC]
    pdf.compress=1
    pdf.quality=0
    pdf.resolution=300
    pdf.save()
    (ROOT/'build-status.txt').write_text('PASS: two pages; no text overflow; expected line counts.\n')

if __name__ == "__main__":
    try:
        main()
    except Exception:
        (ROOT/'build-error.txt').write_text(traceback.format_exc())
    finally:
        if os.environ.get('SNL_BATCH')=='1':
            os._exit(0)
