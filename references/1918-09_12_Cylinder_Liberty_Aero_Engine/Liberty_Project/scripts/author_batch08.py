"""Reviewed transcription, native tables and captions for scans 0141–0160.
All technical values retain the printed reading; original OCR stays separate.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];SX=396/1893
ocr={p['leaf']:p['lines'] for p in json.loads((R/'data/batch08_ocr_draft.json').read_text())}
folios={**{n:n-4 for n in range(141,149)},149:None,150:145,151:None,152:146,153:None,154:147,155:148,156:None,157:149,158:150,159:None,160:151}
wide={150:612,152:792,154:792,160:792}
folio_y={141:297,142:312,143:329,144:298,145:285,146:270,147:289,148:297,155:275,157:252,158:255}
pages={n:dict(leaf=n,printed_page=folios[n],blank=folios[n] is None,page_size_points=[wide.get(n,396),691],folio_baseline=folio_y.get(n,36/SX),headings=[],blocks=[],captions=[],legends=[],subheads=[],vertical=[],positioned_text=[],native_rules=[],tables=[],clearance_tables=[]) for n in range(141,161)}
fix={
141:{21:'accessibility of certain parts of the engine is to be borne',22:'in mind in designing the cowling (see “Accessibility”',31:'to the direction in which the exhaust is discharged; the',35:'The wiring and switch system must be that incor-'},
142:{2:'should accordingly be 110/36 or area equivalent. The',4:'outside, and thoroughly painted internally with anti-',11:'the Liberty engine in ‘De H. 9a aeroplanes is available',30:'camshaft with a “single row” ball bearing, and the'},
143:{2:'shaft. On the camshaft are mounted, first, a fixed',11:'These holes on the first engines are tapped 1 in. × 18 T,',13:'end to fit this, has been got out. The holes in the',19:'are supplied tapped {3/4} in. B.S.P., which will enable the',25:'type pipe lines, reservoir, etc., and B or C trigger'},
146:{4:'throttle valves, and it may occasionally be found that',8:'carefully “set” so that the closing points agree.',14:'adjustment “X” in Fig. 99. If it is impossible to syn-',21:'Finally. the throttle stop screws (“Z” in Fig. 99)'}
}
def block(n,a,b,y,first=125,cont=0,step=54):
 lines=[dict(text=fix.get(n,{}).get(i,ocr[n][i]['text']),indent=first if i==a else cont,source_ocr_index=i) for i in range(a,b+1)]
 pages[n]['blocks'].append(dict(y=y,step=step,lines=lines))
for args in [(141,1,5,400),(141,7,24,820),(141,26,33,1949),(141,35,43,2513),(141,44,45,2994),
 (142,1,9,420,0),(142,10,12,967),(142,25,30,2778),
 (143,1,8,439,0),(143,9,23,886),(143,24,29,1721),(143,30,32,2114),(143,33,36,2296),
 (146,3,8,636),(146,9,20,988),(146,21,24,1675)]:block(*args)
adjustments=[]
for n,p in pages.items():
 ls=[l for b in p['blocks'] for l in b['lines']]
 if not ls:continue
 rights=sorted(ocr[n][l['source_ocr_index']]['box'][2] for l in ls);edge=rights[int((len(rights)-1)*.8)]
 for l in ls:l['align']=4 if len(l['text'])>28 and '{' not in l['text'] and ocr[n][l['source_ocr_index']]['box'][2]>=edge-45 else 0
 previous=None
 for b in p['blocks']:
  old=b['y']
  if previous is not None:b['y']=max(old,previous+54)
  if b['y']!=old:adjustments.append(dict(leaf=n,first_source_ocr_index=b['lines'][0]['source_ocr_index'],original_baseline=old,final_baseline=b['y']))
  previous=b['y']+(len(b['lines'])-1)*b['step']
heads={141:[[740,'COWLING.'],[1867,'EXHAUST PIPES.'],[2435,'WIRING SYSTEM.']],142:[[2321,'CHAPTER IX.',12],[2488,'C. C. Synchronizing Gear on',21,'Bold'],[2640,'Liberty Engine.',21,'Bold']],144:[[566,'Standard',21,'Bold'],[681,'Fits and Clearances.',21,'Bold'],[809,'(Expressed in fractions of an inch.)',11.2,'Italic']],146:[[421,'ADJUSTING CONTROLS OF ZENITH'],[484,'CARBURETTOR.']]}
for n,v in heads.items():pages[n]['headings']=v
caps={142:[[2083,'Fig. 97.'],[2160,'C.C. Gun Gear.']],147:[[1277,'Fig. 98.'],[3018,'Fig. 99.']],148:[[2727,'Fig. 100.'],[2842,'Installation Drawing.'],[2925,'(Front Elevation).']],155:[[2912,'Fig. 104.'],[3013,'Rear Elevation.']],157:[[2845,'Fig. 105.'],[2960,'Transverse Section through Cylinders.']],158:[[2876,'Fig. 106.'],[2983,'Front Elevation.']]}
for n,v in caps.items():pages[n]['captions']=v

def pos(n,t,x,y,w,size=9.4,font='Roman',align=0,italic_words=None):
 v=dict(text=t,x=x,y=y,width=w,size=size,font=font,align=align)
 if italic_words:v['italic_words']=italic_words
 pages[n]['positioned_text'].append(v)
def pt(n,t,x,y,w,size=10.8,font='Roman',align=0):pos(n,t,x,y/SX,w,size,font,align)
# Dates stay at the source's right-hand position; captions remain editable.
pos(148,'April, 1918',280,3023,90,10.8,align=2)
# Foldout caption positions follow their placement relative to original art.
for j,t in enumerate(['Fig. 101.','Installation Drawing.','(Rear Elevation.)']):pt(150,t,98,573+14*j,170,align=1)
pt(150,'April, 1918.',454,626,110,align=2)
for j,t in enumerate(['Fig. 102','Installation Drawing.','(Side Elevation).']):pt(152,t,87,599+14*j,170,align=1)
pt(152,'April, 1918.',641,629,110,align=2)
for j,t in enumerate(['Fig. 103.','Installation Drawing.','(Plan View).']):pt(154,t,90,453+14*j,170,align=1)
pt(154,'April, 1918,',641,483,110,align=2)
# The large longitudinal section is the last reconstructed source in this batch.
pt(160,'Fig. 107.',35,565,722,align=1)
pt(160,'General Arrangement (Longitudinal Section).',35,591,722,align=1)
# All table cells and leaders are native, not a flattened image of the table.
# Source coordinates have been aligned into fixed columns. A blank desired
# value stays blank, and the visibly missing decimal in 00125 is not supplied.
TABLE_SIZE=9.4
for n,y in [(144,1027),(145,486)]:
 for t,x,w in [('MINIMUM.',171,68),('MAXIMUM.',231,68),('DESIRED'+('.' if n==145 else ''),295,70)]:pos(n,t,x,y,w,9.2,align=1)
# One source heading has an italic continuation, preserved by a local font run.
pos(145,'Standard Fits and Clearances.—continued.',46,392,330,11.5,italic_words=['continued.'])
# Source's double rule under the main heading.
for y,width in [(874,.8),(884,.35)]:pages[144]['native_rules'].append(dict(x=157,y=y*SX,x2=237,y2=y*SX,width=width))

def head(n,t,y,x=46):pos(n,t,x,y,210,10.8,'Sans')
def sub(n,t,y,x=56):pos(n,t,x,y,206,9.2)
def row(n,label,minimum,maximum,desired,y,indent=0):
 # Each desired value can occupy several source lines; line pitch is 45 pixels.
 desired=desired if isinstance(desired,list) else [desired] if desired else []
 pages[n]['clearance_tables'].append(dict(label=label,minimum=minimum,maximum=maximum,desired=desired,y=y,x=64+indent,label_width=127-indent,minimum_x=193,maximum_x=249,desired_x=295,minimum_width=56,maximum_width=62,desired_width=70,size=TABLE_SIZE,desired_step=45))
head(144,'Crankshaft.',1090)
row(144,'Diametrical Clearance','.0025','.00325','',1150)
row(144,'End Play','.0575','.0775','',1195)
head(144,'Connecting Rods.',1297);sub(144,'FORKED END—',1352)
row(144,'Diametrical Clearance','.003','.004','',1412)
row(144,'End Play','.008','.020','',1457)
sub(144,'PLAIN END—',1518)
row(144,'Diametrical Clearance','.005','.0065','',1579)
row(144,'End Play','.004','.008','',1624)
head(144,'Gudgeon Pin.',1724)
row(144,'Fit in Rod','.00025','00125',['Select for','.001','Clearance'],1778)
row(144,'Fit in Piston','.00025 tight','.00075 tight',['Select for','light drive','fit'],1929)
head(144,'Piston Rings.',2104)
row(144,'Fit in Grooves','.00125','.003,',['Top .003','Mid. & Bot.','.002'],2160)
row(144,'Gap','.021','.041','.030',2311)
head(144,'Piston.',2405)
row(144,'Fit in Cylinder','.018','.022',['Select for','.020','Clearance'],2476)
head(144,'Camshaft.',2618)
row(144,'Diametrical Clearance','.001','.003','',2678)
row(144,'End Play','.000','.004','Min. .002',2723)
head(144,'Camshaft Upper Drive',2822);head(144,'Shaft.',2876,56)
sub(144,'Diametrical Clearance—',2929,64)
row(144,'Large Bushing','.0005','.0025','Min. .0015',2981,18)
row(144,'Small Bushing','.0005','.0025','Min. .0015',3026,18)
row(144,'End Play','.002','.008','Min. .004',3071)
head(145,'Rocker Levers.',548)
row(145,'Diametrical Clearance','.00025','.00175','Min. .001',610)
row(145,'End Play','.005','.010','.0075',655)
head(145,'Valves.',747);sub(145,'FIT OF STEMS IN GUIDES.',808)
sub(145,'Diametrical Clearances—',869,64)
row(145,'Exhaust Valves','.004','.0065','.005',915,18)
row(145,'Inlet Valves','.002','.0045','.003',960,18)
head(145,'Water Pump Shaft.',1058)
row(145,'Diametrical Clearance','.0015','.0035','Min. .0025',1114)
row(145,'End Play','.006','.010','.010',1159)
head(145,'Water Pump Bevel',1259);head(145,'Driver.',1313,56)
row(145,'Diametrical Clearance','.001','.0025','',1376)
row(145,'End Play','.005','.008','',1421)
head(145,'Oil Pump.',1504);sub(145,'FIT OF GEARS IN HOUSING.',1560)
row(145,'Diametrical Clearance','.001','.005',['Select for','.004','Clearance'],1621)
row(145,'End Play','.002','.007',['Select for','.003','Clearance'],1778)
head(145,'Tappet Gap.',1912)
row(145,'Exhaust Valves','.019','.021','',1967)
row(145,'Inlet Valves','.014','.016','',2012)
# These two labels are bold in the source and span the usual indentation.
row(145,'Contact Breaker Gap','.010','.013','',2109,-18);pages[145]['clearance_tables'][-1]['label_font']='Sans'
row(145,'Sparking Plug Gap','.015','.018','.015',2209,-18);pages[145]['clearance_tables'][-1]['label_font']='Sans'
head(145,'Regulator.',2304)
row(145,'Contact Gap','.005','.007','',2364)
row(145,'Height of Pin','.043','.045','',2409)

data=dict(batch=8,source_scans=[141,160],table_layout_adjustments=[dict(leaf=144,heading='Camshaft Upper Drive / Shaft.',baseline_pitch_before=45,baseline_pitch_after=54,following_rows_shift_source_pixels=9),dict(leaf=145,heading='Water Pump Bevel / Driver.',baseline_pitch_before=45,baseline_pitch_after=54,following_rows_shift_source_pixels=9)],proofread_against='All twenty original scans; detail views of the decimal point, table values, source anomalies and foldout dimensions.',layout_adjustments=adjustments,pages=list(pages.values()))
(R/'data/batch08_transcription.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
cumulative=json.loads((R/'data/baseline_v07_transcription.json').read_text());cumulative['pages']+=data['pages'];(R/'data/transcription.json').write_text(json.dumps(cumulative,ensure_ascii=False,indent=2))
changes=[dict(leaf=n,source_ocr_index=i,ocr=ocr[n][i]['text'],corrected=t) for n,v in fix.items() for i,t in v.items() if ocr[n][i]['text']!=t]
anomalies=[dict(leaf=142,text='‘De H. 9a',note='Apparent isolated opening mark retained.'),dict(leaf=143,text='lubricatcr; attach- / attachment',note='Printed c-for-o reading and repeated attach retained.'),dict(leaf=144,text='00125',note='Maximum gudgeon-pin fit in rod visibly lacks a decimal point; retained, not supplied.'),dict(leaf=144,text='.003,',note='Printed comma after piston-ring groove maximum retained.'),dict(leaf=144,text='.008 forked-rod end play; .000 camshaft end play',note='Printed table values retained despite differences from earlier prose.'),dict(leaf=146,text='Finally.',note='Printed full stop retained; damaged throttle letters resolved from the visible word.')]
(R/'data/batch08_corrections.json').write_text(json.dumps(dict(corrections=changes,retained_source_anomalies=anomalies,notes=['All two-page clearance table cells were separately read and authored as structured native rows.','No printed technical value recalculated, modernized or silently reconciled.','Two split bold table headings use a minimum 54-source-pixel pitch, moving following rows by nine source pixels.','The plan-view foldout date retains its printed comma after 1918.','Visible foldout folios: scan 0150=145, 0152=146, 0154=147, 0160=151.','Blank scans: 0149, 0151, 0153, 0156, 0159; small edge fragments from the folded drawing are not treated as separate printed content.','Figure 101 uses a caption-only exclusion because its Mod. label and leader extend lower than the caption.','Four new foldouts use provisional widths 612 or 792 pt and the established 691 pt height.']),ensure_ascii=False,indent=2))
inv=json.loads((R/'data/source_inventory.json').read_text())
for f in inv['sources']:
 if f['leaf'] in pages:
  f['verified_printed_folio']=str(folios[f['leaf']]) if folios[f['leaf']] is not None else None
  f['visual_classification']='blank with show-through or fold edge' if folios[f['leaf']] is None else 'foldout' if f['leaf'] in wide else 'printed manual page'
(R/'data/source_inventory.json').write_text(json.dumps(inv,indent=2))
print('Authored',len(pages),'scans;',sum(len(b['lines']) for p in pages.values() for b in p['blocks']),'body lines;',sum(len(p['clearance_tables']) for p in pages.values()),'native table rows;',len(changes),'explicit OCR corrections;',len(adjustments),'baseline adjustments.')
