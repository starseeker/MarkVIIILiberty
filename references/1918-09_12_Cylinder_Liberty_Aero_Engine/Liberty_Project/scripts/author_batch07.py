"""Reviewed source text and native placements, scans 0121–0140.
Original OCR stays separate; braces identify editable stacked fractions.
"""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
ocr={p['leaf']:p['lines'] for p in json.loads((R/'data/batch07_ocr_draft.json').read_text())}
fix={
121:{1:'11. Insert the bolts by which the carburettors are',2:'slung from the induction manifolds; fit the carburettors.',6:'four points, viz.:—',10:'(b) Joints between mixing and throttle',20:'(a) and (b); take great care to clean off old adhesive',32:'from sheet “Hallite.”'},
122:{8:'follows:—',10:'(ii) Timing with a new camshaft or gear wheel,',11:'p. 126.',12:'(iii) Timing regardless of the marks (as, for in-',26:'and inlet opening angles are identical; this point is',27:'termed the “neutral point” in American instructional',31:'clearance, .019 in.',43:'1L, 6R, 5L, 2R, 3L, 4R, 6L, 1R, 2L, 5R, 4L, 3R.'},
123:{6:'points are vital:—',7:'(i) The main crankshaft bevel must be bolted',9:'marked “O” registers with the “O”',16:'(ii) The three zero marks stamped on the',20:'(iii) The driving bevel of the long inclined',21:'shaft has a tooth marked “O.” This',24:'of the engine—i.e., so that the three “O”',25:'marks described in the last paragraph are',28:'If the above parts are assembled in the stated rela-'},
124:{7:'inlet opening angles (or “neutral points”). In lieu of',9:'of the nose piece to indicate the centre line of each',11:'T.D.C.)',15:'quired by experienced mechanic’s, but may be of assist-',16:'ance to fitters accustomed only to vertical engines:—',23:'tion, and this position is the same for',24:'both cylinder blocks—i.e., after timing'},
127:{1:'the crankshaft is not moved on 45° to',12:'fitted. Otherwise, the order of procedure is as follows:—',13:'1. See that the “O” tooth on the crankshaft',14:'bevel registers with the “O” on the crankshaft flange.',19:'fitted after the “idler” or short inclined shafts are in',32:'hand cylinder block, or 12{1/2}° to the left of a vertical line',35:'timing operations are complete, and remains in this',40:'5. Fit the “idler” or short (lower) inclined shafts.',43:'lines indicated by these opposed marks must run “fore',44:'and aft”—i.e., parallel to the crankshaft axis; but it'},
129:{1:'6. Be sure that the “O” tooth of the small bevel',4:'line with the “O” marks on the camshaft and large cam-',7:'clined shaft into the “fore and aft” position.',22:'inclined shaft and the “idler” or short inclined shaft',28:'9. Being careful not to disturb the settings of the'},
130:{1:'cylinder in either block is the “neutral point” of No. 6',2:'cylinder on the same side, i.e., Nc. 6 piston is also at 10°',7:'or if No. 3 is at the firing point, No. 4 is at the neutral',10:'shaft and watch the exhaust valve of cylinder No. R1.',12:'opens, cylinder No. R.1 must be on its firing point (fully',13:'retarded)—i.e., correct for the setting of its clearances.',15:'be between .019 and .021 in., and the inlet tappet clearance',16:'between .014 and .016 in. If the clearances are incorrect,',23:'other parts as follows:—',45:'turbing the setting of the camshaft or inclined shaft,'},
131:{3:'fashion. (Exhausts are now set to close at 8° A.T.D.C.).',9:'“L”) over the bolts, so that its marked notch is lined',12:'Lastly, tighten up the bolts, and punch an “O”',19:'exhaust has just shut, and No. R1 inlet is about to open.',20:'Set the camshaft gear wheel as directed for the left-hand',26:'inclined shaft, i.e., in the centre line of the right-hand',31:'without reference to the marks. In this case, the',34:'peller hub; the procedure will be as follows:—',35:'1. Unbolt both camshaft gear wheels.',36:'2. Set the crankshaft at 10° past T.D.C. for',37:'cylinder No. L1.',44:'5. Turn the crankshaft clockwise (as viewed from',46:'will be at 10° past T.D.C. in R6 cylinder.'},
132:{17:'6. Set the right-hand camshaft so that the inlet',18:'valve of cylinder R1 is just about to open, its',20:'7. Replace the driven bevel of the right-hand cam-',27:'hand camshaft settles the cylinder to be em-',28:'ployed in setting the right-hand camshaft, i.e.,',32:'It is not possible, as might be supposed, to lift out'},
133:{9:'13. Time the Ignition.—Full directions are given',11:'14. Connect up the sparking plug cables. Sparking',16:'15. Fit the water pump unit. Be careful not to',18:'the bevel gears (minimum backlash .005 in.,',19:'maximum .010 in.). If the mesh is incorrect,',22:'16. Fit the water inlet manifolds on either side of',28:'17. Fit the oil pump unit. Make a sound joint with',29:'a washer, but see that the washer clears the',32:'18. Fit the base chamber breathers and the cover'},
134:{7:'(i) Weak mixture. Insufficient doping, or cylinders',12:'clear cylinders.)',13:'(iii) Valves stuck or blowing.',15:'acid. (See p. 92.)',23:'(vii) Air leaks at joints of carburettors and induc-',25:'(viii) Engine “gummy” with congealed oil.',28:'(Note: In cold weather an engine which has not',30:'period after first starting up.)',34:'(b) Excessive gap (the correct gap is .015 in.).'},
135:{1:'(ii) Defects in distributor “heads.” Test each',6:'(iii) Carburation, e.g.—',9:'(c) Feed pipe partly choked.',11:'worn needle, toggle, levers sticking, or a',12:'punctured float.',30:'(vi) Piston rings broken or “baked” into grooves.',31:'(vii) Valves.',33:'clearances are .015 in. for the inlets, and',34:'.019 in. for the exhausts).',36:'is required to compress an outer',37:'exhaust spring to 2{1/4} in., and 23{1/2} lbs. for',40:'after T.D.C., closes 45° after B.D.C. Ex-',43:'(viii) Compression faults.',46:'(c) Faulty piston rings. (Note:—All aluminium'},
136:{7:'of lubricating oil, or of oil mixed with',8:'paraffin, may be employed.)',9:'(iii) Incorrect jets: the standard sizes for the',10:'Liberty engines are:—',11:'Zenith:—Main, 280 cc.; compensator, 340 cc.',12:'Claudel:—Main jet, 490 c.c.; slow-running jet,',13:'200 c.c.',15:'(i) Water circulation troubles.',23:'(ii) Other causes.',25:'(b) Engine carbonised and in need of cleaning.',31:'(e) Lubrication defective.',33:'(i) Gauge registers over 55 lbs. Relief valve is de-',34:'ranged. Stop engine and repair fault, or some pipe or',36:'(ii) Gauge registers little or no pressure. Leak',40:'The oil pressure varies with the engine revolutions,',41:'and will always be low when the engine is only “ticking”'},
137:{8:'proof construction, so far as possible. Air intake pipes',9:'are to be arranged to come clear of the cowling, and the',14:'Care is to be taken in mounting the engine in the',19:'possible to the following parts:—',23:'be less than 10 in.)',33:'push-and-pull rods, levers, bellcranks, and torsional',40:'equalising cock, the latter being required between the',42:'“Cooling System,” “Lubrication System,” and'},
138:{1:'“Petrol System.”) Guides are to be provided for all',9:'mended. The system of fuel feed to be installed is',10:'that in which a head corresponding to a pressure of',11:'2 lb. per sq. in. is derived from a small gravity tank,',17:'than those incorporated in the design, and supplied',18:'with the tanks. Where self-sealing tanks are not',34:'must be provided with a vent hole of not less than {3/16} in.'},
139:{1:'running pipes behind the longerons, and, in a dual',6:'to suitable parts of the machine. The area of the main',9:'when the carburettor unions are uncoupled and the',16:'of Air Board standard mesh, the latter accessible for',31:'of 4 in. over the inlet nipple of the oil pump. The in-',32:'structions regarding petrol tank filler caps and the',35:'must not be less than 1{1/4} in. O.D., and enlarging nipples',44:'fitted between the tank and the oil pump, provision is'},
140:{3:'in the oil tank for cooling the heated oil returned by the',11:'must in all cases be approved by the Controller, Techni-',12:'cal Department. The water system is to be so',19:'for according to the following formula:—',25:'The reserve water must be carried at the highest',26:'point of the system, and a suitable header tank must',31:'do not fall, and that reverse bends are avoided in all',36:'must be arranged so that it may be completely drained.',38:'means of lccking them in closed position. Means are'}
}
folios={121:119,122:120,123:121,124:122,125:None,126:123,127:124,128:None,**{n:n-4 for n in range(129,141)}}
fb={121:285,122:286,123:285,124:269,126:26/(396/1893),127:232,129:307,130:291,131:325,132:300,133:273,134:252,135:227,136:183,137:232,138:233,139:267,140:223}
pages={n:dict(leaf=n,printed_page=folios[n],folio_baseline=fb.get(n),page_size_points=[612,691] if n==126 else [396,691],blank=n in [125,128],blocks=[],headings=[],captions=[],legends=[],tables=[],subheads=[],vertical=[],positioned_text=[],native_rules=[]) for n in range(121,141)}
def block(n,a,b,y,first=125,cont=0,step=54):
 lines=[]
 for i in range(a,b+1):
  l=dict(text=fix.get(n,{}).get(i,ocr[n][i]['text']),indent=first if i==a else cont,source_ocr_index=i)
  if (n,i) in [(123,1),(124,14),(127,10)]:l['font_runs']=[dict(text={123:'Timing Marks.',124:'Timing Hints.',127:'Timing by the Marks.'}[n],font='Sans')]
  if n==131 and i in [18,19,37]:l['small_digit_tokens']=['L1' if i==37 else 'R1']
  if n==132 and i==18:l['small_digit_tokens']=['R1']
  lines.append(l)
 pages[n]['blocks'].append(dict(y=y,step=step,lines=lines))
for args in [
(121,1,2,401),(121,3,6,539,0),(121,7,9,784,250,375),(121,10,11,983,250,375),(121,12,13,1126,250,375),(121,14,15,1262,250,375),(121,18,23,2221),(121,24,32,2580),
(122,1,1,399),(122,2,2,451),(122,4,6,604),(122,7,8,766),(122,9,9,884),(122,10,11,940,125,310),(122,12,14,1048,125,310),(122,25,31,1763),(122,38,38,2734),(122,41,42,2910),(122,43,43,3018,85),
(123,1,6,402),(123,7,10,794,250,375),(123,16,19,2158,250,375),(123,20,27,2420,250,375),(123,28,30,2908),
(124,2,5,1732),(124,7,11,1950,0),(124,12,13,2221),(124,14,16,2330),(124,17,20,2508,250,375),(124,21,26,2724,250,375),
(127,1,3,334,375,375),(127,4,8,501,280,375),(127,10,12,933),(127,13,14,1090),(127,15,21,1200),(127,22,26,1585),(127,27,33,1857),(127,34,39,2230),(127,40,47,2564),
(129,1,5,412),(129,6,7,720),(129,19,23,2113),(129,24,27,2400),(129,28,30,2637),(129,31,35,2810),
(130,1,19,411,0),(130,22,23,1716),(130,24,29,1840),(130,30,32,2167),(130,33,34,2328),(130,35,38,2438),(130,39,41,2656),(130,42,46,2816),
(131,1,3,436,0),(131,4,6,598),(131,7,11,760),(131,12,15,1032),(131,16,21,1249),(131,22,27,1575),(131,29,34,2083),(131,35,35,2439),(131,36,37,2495,125,250),(131,38,40,2600,125,250),(131,41,43,2763,125,250),(131,44,46,2926,125,250),
(132,17,19,1910,125,250),(132,20,31,2074,125,250),(132,32,35,2725),(132,36,38,2940),
(133,9,10,1870,125,250),(133,11,15,1978,125,250),(133,16,21,2250,125,250),(133,22,27,2564,125,250),(133,28,31,2899,125,250),(133,32,33,3106,125,250),
(134,3,5,1036),(134,7,9,1369),(134,10,12,1531),(134,13,13,1693),(134,14,15,1748),(134,16,16,1856),(134,17,17,1910),(134,18,18,1964,250),(134,19,20,2018,250,375),(134,21,21,2128,250),(134,22,22,2180,250),(134,23,24,2236),(134,25,25,2344,90),(134,28,30,2434),(134,32,32,2781),(134,33,33,2834,250),(134,34,34,2888,250),(134,35,35,2942,250),(134,36,36,2996,250),
(135,1,5,334),(135,6,6,624),(135,7,7,676,250),(135,8,8,730,250),(135,9,9,784,250),(135,10,12,838,250,375),(135,13,13,1000,250),(135,14,14,1054,250),(135,15,16,1108,250,375),(135,17,17,1216,250),(135,18,20,1283),(135,21,21,1458),(135,22,23,1514,250,375),(135,24,24,1622,250),(135,25,25,1676,250),(135,26,26,1730,250),(135,27,28,1784,250,375),(135,29,29,1892,250),(135,30,30,1965),(135,31,31,2045),(135,32,34,2102,250,375),(135,35,38,2266,250,375),(135,39,42,2481,250,375),(135,43,43,2712),(135,44,44,2768,250),(135,45,45,2822,250),(135,46,47,2876,250,375),
(136,1,8,293,375,375),(136,9,10,738),(136,11,11,846),(136,12,13,900),(136,15,15,1178),(136,16,17,1233,250,375),(136,18,18,1343,250),(136,19,20,1397,250,375),(136,21,22,1507,250,375),(136,23,23,1645),(136,24,24,1702,250),(136,25,25,1756,250),(136,26,27,1810,250,375),(136,28,30,1923,250,375),(136,31,31,2085,250),(136,33,35,2306),(136,36,38,2480),(136,39,39,2658),(136,40,42,2725),
(137,5,11,797),(137,14,19,1366),(137,20,23,1690),(137,24,25,1907),(137,26,27,2018),(137,28,28,2126),(137,29,29,2180),(137,31,42,2353),
(138,1,6,343,0),(138,8,48,765),
(139,1,18,375,0),(139,19,25,1371),(139,27,46,1960),
(140,1,5,333,0),(140,7,19,722),(140,25,40,1725),(140,41,48,2592)
]:block(*args)
# Source-bound justification; paragraph ends are retained even if they fall short.
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
heads={122:[[531,'IV.—VALVE TIMING INSTRUCTIONS.']],127:[[829,'TIMING METHODS.']],130:[[1521,'Timing with a New Camshaft or New Camshaft',11.5,'Sans'],[1608,'Gear Wheel.',11.5,'Sans']],131:[[1997,'Timing Without Using the Marks.',11.5,'Sans']],133:[[1815,'Reassembling Notes (continued from p. 120.)',11.5,'Sans']],134:[[684,'CHAPTER VII.',12],[901,'Possible Troubles.',21,'Bold'],[1271,'I.—DIFFICULTY IN STARTING.'],[2675,'II.—LOSS OF POWER.']],136:[[1068,'III.—OVERHEATING.'],[2197,'IV.—LUBRICATION TROUBLES.']],137:[[334,'CHAPTER VIII.',12],[527,'Installation of “Liberty”',21,'Bold'],[645,'Engine.',21,'Bold'],[723,'ENGINE MOUNTING.'],[1221,'ACCESSIBILITY OF ENGINE AND AUXILIARY'],[1293,'FITTINGS.'],[2279,'ENGINE CONTROLS.']],138:[[688,'PETROL SYSTEM.']],139:[[1838,'LUBRICATION SYSTEM.']],140:[[638,'COOLING SYSTEM.']]}
for n,v in heads.items():pages[n]['headings']=v
caps={121:[[1981,'Fig. 89.'],[2068,'Water Joint Clip.']],122:[[2478,'Fig. 90.'],[2548,'Numbering of Cylinders.'],[2615,'(N.B.—The cylinders are numbered from the rear,'],[2670,'not from the propeller.)']],123:[[1744,'Fig. 91.'],[1882,'Timing Marks on Camshaft Flange and'],[1953,'Distributor Hub.']],124:[[1588,'Fig. 92.'],[1662,'Timing Marks on Propeller Hub Flange.']],129:[[1839,'Fig. 94.'],[1927,'Timing Marks on Camshafts and Inclined Shafts.']],132:[[1562,'(Note: Exhaust now opens 48° B.B.D.C., and'],[1616,'closes 8° A.T.D.C.)'],[1704,'Fig. 95.'],[1773,'Timing Diagram.']],133:[[1615,'Fig. 96.'],[1677,'Rear End of Crankcase from beneath, with'],[1731,'Oil Pump removed.']]}
for n,v in caps.items():pages[n]['captions']=v
SX=396/1893
pages[126]['captions']=[[611/SX,'Fig. 93.'],[630/SX,'Distribution Gear in Section, explaining Timing Marks.']]
pages[126]['legends']=[dict(x=145,y=646/SX,width=340,step=12/SX,size=10.8,align=0,lines=['(N.B.—Crankshaft must be retained in above position']),dict(x=168,y=658/SX,width=320,step=12/SX,size=10.8,align=0,lines=['for timing both camshafts, when timing is done by','the marks.)'],italic_words=['both'])]
def positioned(n,t,x,y,w,size=10.8,font='Roman',align=0):
 pages[n]['positioned_text'].append(dict(text=t,x=x,y=y,width=w,size=size,font=font,align=align))
# Native timing table: independent cells and native dotted leaders.
positioned(122,'Timing Data.—',72,1220,210,11.5,'Sans')
for t,x,y,w,al in [('Crank angle.',165,1275,92,1),('Mm. on stroke.',272,1275,80,1)]:positioned(122,t,x,y,w,10.8,align=al)
for k,(label,angle,stroke) in enumerate([('Inlet valve opens','10° after T.D.C.','1 mm. down'),('Inlet valve closes','45° after B.D.C.','111.5 mm. down'),('Exhaust valve opens','50° before B.D.C.','118 mm. down'),('Exhaust valve closes','10° after T.D.C.','1 mm. down')]):
 y=1329+54*k;pages[122]['tables'].append(dict(x=46,width=217,refwidth=107,y=y,step=54,rows=[[label,angle]]));positioned(122,stroke,274,y,76,10.2,align=2)
positioned(122,'Valve clearance:',46,1545,99)
for t,x,y,w in [('Inlet',144,1545,42),('.015 in. (.38 mm.)',213,1545,137),('Exhaust',144,1599,52),('.020 in. (.50 mm.)',213,1599,137),('Maximum ignition',46,1653,120)]:positioned(122,t,x,y,w)
pages[122]['tables'].append(dict(x=103,width=160,refwidth=107,y=1707,step=54,rows=[['advance','30° before T.D.C.']]))
positioned(122,'19.2 mm. down',274,1707,76,10.2,align=2)
positioned(122,'Propeller',93,2820,68)
positioned(122,'{',150,2843,16,24)
positioned(122,'2, 10, 6, 12, 4, 8, Right',164,2788,185)
positioned(122,'7, 3, 11, 5, 9, 1, Left.',164,2842,185)
# Reserve-water definitions and stacked formula, all native text/rule objects.
positioned(140,'When',72,1429,39)
positioned(140,'N = Normal engine B.H.P.,',112,1429,230)
positioned(140,'and',72,1483,39)
positioned(140,'H = Hours’ fuel capacity allowed,',112,1483,235)
positioned(140,'C = Reserve water required (gallons).',112,1537,238)
positioned(140,'Then C = 1 +',160,1632,82)
positioned(140,'H.N.',244,1597,39,10.8,align=1)
positioned(140,'1600',244,1667,39,10.8,align=1)
pages[140]['native_rules']=[dict(x=244,y=1615*SX,x2=283,y2=1615*SX,width=.35)]
# The three definition lines are consistently aligned; the formula reserves
# extra leading for a full-size numerator and denominator.
data=dict(batch=7,source_scans=[121,140],proofread_against='All twenty original scans; closer views of source anomalies, firing sequences, dimensions and the foldout.',layout_adjustments=adjustments,pages=list(pages.values()))
(R/'data/batch07_transcription.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
cumulative=json.loads((R/'data/baseline_v06_transcription.json').read_text());cumulative['pages']+=data['pages'];(R/'data/transcription.json').write_text(json.dumps(cumulative,ensure_ascii=False,indent=2))
changes=[dict(leaf=n,source_ocr_index=i,ocr=ocr[n][i]['text'],corrected=t) for n,v in fix.items() for i,t in v.items() if ocr[n][i]['text']!=t]
anomalies=[dict(leaf=123,text='tooth marked / marked “O”',note='Duplicate marked retained.'),dict(leaf=124,text='mechanic’s',note='Apparent apostrophe retained after close review.'),dict(leaf=129,text='Step 6 followed by step 8',note='No step 7 is printed on this leaf; no number supplied.'),dict(leaf=130,text='Nc. 6; bock.; lower / lower',note='Source readings retained, including the duplicated lower.'),dict(leaf=130,text='R6 / R1 / R6 / R6 / R.1',note='Apparently inconsistent cylinder references preserved without correction.'),dict(leaf=136,text='compressicn; (iii) Incorrect jets',note='Visible c-for-o reading and restarted list number retained.'),dict(leaf=137,text='must nct'),dict(leaf=138,text='fillers caps'),dict(leaf=139,text='pump fcr those'),dict(leaf=140,text='lccking')]
(R/'data/batch07_corrections.json').write_text(json.dumps(dict(corrections=changes,retained_source_anomalies=anomalies,notes=['No technical value recalculated or modernized.','Scans 0125 and 0128 are blank; scan 0126 visibly carries printed folio 123.','The foldout uses a provisional 612 × 691 pt canvas and uniform original-pixel artwork scale.','Timing table, Propeller brace and reserve-water formula are native objects.','Source inline slash fraction 2 1/7 remains inline; five new stacked numeric fractions and one formula rule are editable.']),ensure_ascii=False,indent=2))
inv=json.loads((R/'data/source_inventory.json').read_text())
for f in inv['sources']:
 if f['leaf'] in pages:f['verified_printed_folio']=str(folios[f['leaf']]) if folios[f['leaf']] is not None else None;f['visual_classification']='blank with show-through' if f['leaf'] in [125,128] else 'foldout' if f['leaf']==126 else 'printed manual page'
(R/'data/source_inventory.json').write_text(json.dumps(inv,indent=2))
print('Authored',len(pages),'scans;',sum(len(b['lines']) for p in pages.values() for b in p['blocks']),'body lines;',len(changes),'explicit OCR corrections;',len(adjustments),'baseline adjustments.')
