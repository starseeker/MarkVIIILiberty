"""Native layouts for the final nomenclature and general index pages, 241–251."""
from pathlib import Path
import json
import scribus as s
import layout_helpers as b

DATA=json.loads((Path(__file__).resolve().parent/'data/index_batch13.json').read_text())

def baseline(y):return 17+y*.225

def indexrow(t,ref,y):
    x=50;size=9.;width=298;refw=22;end=x+width-refw-5
    natural=b.advance(t,size,'Roman');usable=end-x-3
    scale=min(100,usable/max(natural,.1)*100)
    b.txt(t,x,y,usable,size,scale=scale)
    start=x+natural*scale/100+2
    if start+1.5<end:b.rule(start,y-1.8,end-start,.25,True)
    # Two entries have no printed reference; retain leaders and the empty column.
    if ref:b.txt(ref,end+5,y,refw,size,align=2)

def extra(n):
    page=DATA[str(n)]
    if page.get('title'):
        b.center(page['title'],baseline(page['title_baseline']),10,'Bold')
        b.rule(174,baseline(page['title_rule_y']),48,.35)
    y=page.get('page_header_baseline')
    if y is None:
        y=page['sections'][0]['rows'][0]['source_baseline']-42
    b.txt('Page',325,baseline(y),23,7.3,align=2)
    for section in page['sections']:
        if section['letter']:
            b.center(section['letter'],baseline(section['source_heading_baseline']),8.5)
        for row in section['rows']:
            indexrow(row['text'],row['reference'],baseline(row['source_baseline']))
    if 'signature' in page:
        row=page['signature'];b.txt(row['text'],72,baseline(row['baseline']),170,6.5)
    if 'bottom_folio_baseline' in page:
        b.center(f'({n})',baseline(page['bottom_folio_baseline']),8.3)
    if 'end_mark' in page:
        mark=page['end_mark'];w=mark['width_pt'];h=mark['height_pt']
        obj=s.createEllipse(198-w/2,baseline(mark['source_top']),w,h,'p251-closing-circle')
        s.setLineColor('Black',obj);s.setLineWidth(.4,obj);s.setFillColor('None',obj)
