"""Reviewed transcription and native placement for source scans 0081–0100.
Braces encode native stacked fractions; raw OCR is retained independently.
"""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[1]
ocr={p['leaf']:p['lines'] for p in json.loads((R/'data/batch05_ocr_draft.json').read_text())}
fix={
81:{3:'all. The cam has six broad and six narrow noses or'},
82:{1:'to the insulated stud P, and primary current from the',4:'tacts. At Q there is another insulated stud to which the',10:'the knurled-headed socket nuts of the studs P-Q must be',18:'be described at some length. To secure an',22:'event of a failure of the other. Probably the',24:'auxiliary one T, and if this fail the other two may',29:'will not be interfered with. In any case should one of',31:'may be removed, and the engine run on one main lever',32:'only.'},
83:{3:'contact V, and the vulcanised-in rubber buffer pad W',5:'seen. The auxiliary lever T (Fig. 61) is generally',8:'8 ohms, instead of direct to the half-ring N already',9:'described. This auxiliary lever is timed about 5° in',17:'tacts open, circuit is broken, and spark occurs; (d),',44:'moulded in to form the rubbing track for the carbon'},
84:{10:'the primary winding are electrically connected to the'},
85:{2:'wire is connected to the primary winding, but the high',3:'potential end is connected to a fixed carbon brush'},
86:{2:'there are twelve circular studs or “segments,” each in',13:'upon a segment when the cams open the circuit by',22:'There is no special safety gap in the high tension',30:'The twelve high tension cables for each distributor',32:'hand unit firing the forward set of plugs and the right-',34:'pattern of 7 to 7{1/2} mm. rubber insulated flexible cable,'},
89:{5:'a “U” shaped aluminium conduit tube with a large',6:'opening at the base of the “U” by which the 24 leads',16:'is on left-hand side, 1, 9, 5, 11, 3, 7, and on right-hand',17:'side, 8, 4, 12, 6, 10, 2. The sequence through the',18:'whole engine is 1L, 6R, 5L, 2R, 3L, 4R, 6L, 1R, 2L,',19:'5R, 4L, 3R.',22:'moved in unison by operation of the hand control.',29:'“R,” upon the other side the letter “L.” When used',30:'on the right-hand unit, the letter “R” is to be out-',32:'letter “L” must be outward. In every respect, save',36:'for a movement of 1{5/8} in.',37:'The method of timing the ignition will be fairly'},
90:{4:'range so obtainable is 10° on the unit, or 20° on the',7:'timing of the ignition to be varied from the standard',13:'flanges, so that there can be no doubt of the position',14:'when reassembling.',21:'unless a lead is first removed from the generator ter-',22:'minal marked “GEN. ARM,” as otherwise the battery',24:'The alternative method is to wire up a couple of'},
91:{3:'opens, and there should be no more than 1{1/2}° between',15:'contact breaker levers is from 26 to 30 oz. The pressure',24:'certain cylinders, will most probably be due to defective',42:'irregular, and starting difficult or impossible. As the'},
92:{14:'up to some 800 r.p.m., the generator voltage will be',15:'from 9 to 10, and the ignition may therefore function'},
93:{3:'up as quickly as possible to about 700 r.p.m. on one igni-',8:'charge rate, or even 8 or 10 amperes in extreme cases.',19:'with the engine running at 800 r.p.m., or faster, it is',22:'defective switch, or a broken spring on a generator',25:'mally high, it may be due to a burnt-out or shorted',30:'ignition, but not charging the battery. This will',49:'battery alone; so even if the fault be one which necessi-'},
94:{11:'(See Fig. 55.) Should the ammeter not indicate',26:'have a drop of oil. Otherwise, practically no attention',35:'the reading should be not less than 7{1/2} volts. Should',36:'the voltages be lower, a freshly charged battery should',37:'be fitted.',43:'limits of 0.010 and 0.013 in., and the points should'},
95:{1:'5. Run over all leads, especially those on the',11:'break in the circuit, probably due to a loose terminal',14:'where. To detect a short in a coil as distinct from',17:'7. Immediately the engine stops, put both ignition',34:'than about {1/16} in. of play at the end of the distributor',37:'1. Let the weekly clean-up and inspection be, if',42:'3. Inspect and clean the voltage regulator. The'},
97:{3:'the following r.p.m. limits:—',4:'Maximum speed “running up” on the ground,',10:'1,750 r.p.m.',15:'1,750 r.p.m.',18:'hot, as there is a considerable risk of “baking” the',28:'over and above the calculated consumption for',38:'tank for about 1{1/2} gallons of oil, whenever the sump has',41:'oil, unless facilities are available for keeping the engine',42:'warm whilst in the hangar.'},
98:{21:'circulation is very sluggish. Under such conditions',37:'both switches are “on” during starting or slow-running.',40:'be kept in the off position when the engine is out of use,'},
99:{8:'etc.) As soon as the engine fires, the ignition should be',10:'put to “contact.” The engine cannot fire backwards,',17:'the delay. A satisfactory oil temperature is 40° Centi-',23:'Should a test of the altitude control be made, the',24:'tachometer should register a drop of approximately',25:'200 r.p.m. if the altitude control is fully opened for a',36:'“cracking” of the oil and petrol vapour, due to the high',37:'compression ratio of the engine, the volumetric efficiency',38:'of the H.C.7, and local causes peculiar to individual',39:'cylinders (e.g., overheated valves or pistons, carbon de-',40:'posit, or uneven mixture).'},
100:{2:'from ascribing the smoky exhaust to over-large jets.',4:'the smallest compatible with full r.p.m. at ground level.',8:'the following inspections:—',12:'iii. See that the water pump is not excessively',29:'sparking plugs.'}
}
folios=[279,321,294,274,280,337,299,314,261,235,276,273,290,286,245,309,255,248,332,249]
pages={n:dict(leaf=n,printed_page=n-2,folio_baseline=y,blocks=[],headings=[],captions=[],legends=[],tables=[],subheads=[],vertical=[],positioned_text=[]) for n,y in zip(range(81,101),folios)}
def block(n,a,b,y,first=108,cont=0,step=54):
 lines=[]
 for i in range(a,b+1):
  l=dict(text=fix.get(n,{}).get(i,ocr[n][i]['text']),indent=first if i==a else cont,source_ocr_index=i)
  if n==90 and i==23:l['italic_words']=['vide']
  if n==95 and i==7:l['italic_words']=['backward']
  lines.append(l)
 pages[n]['blocks'].append(dict(y=y,step=step,lines=lines))
for args in [
(81,1,5,386,0),(81,7,11,829),(81,15,22,2630,0),
(82,1,12,443,0),(82,16,32,2187),
(83,1,11,414),(83,12,21,1006),(83,22,39,1548),(83,41,48,2643),
(84,1,2,386,0),(84,3,6,502),(84,10,17,2648,0),
(85,1,6,389,0),(85,10,15,2745,0),
(86,2,15,445,0),(86,19,21,2172,0),(86,22,28,2338),(86,30,34,2830),
(89,1,19,370,0),(89,21,36,1527),(89,37,48,2387),
(90,1,14,342,0),(90,15,47,1095),(90,48,51,2877),
(91,1,13,389,0),(91,14,18,1087),(91,20,32,1442),(91,33,47,2143),(91,48,49,2957),
(92,12,25,2310,0),
(93,1,16,397,0),(93,17,39,1272),(93,40,49,2529),
(94,1,2,396,0),(94,3,15,504),(94,16,28,1203),(94,30,37,2039),(94,38,40,2484),(94,41,44,2660),(94,45,47,2889),
(95,1,3,361),(95,4,16,528),(95,17,18,1249),(95,20,24,1502),(95,25,29,1787),(95,30,35,2074),(95,37,38,2503),(95,39,41,2628),(95,42,45,2799),
(96,7,8,2996),
(97,1,3,342,0),(97,4,5,505,0,130),(97,6,7,613,0,130),(97,8,8,720,0),(97,9,10,774,0,130),(97,11,12,880),(97,13,15,988),(97,17,23,1288),(97,25,39,1775),(97,40,42,2590),(97,43,47,2753),
(98,2,9,390),(98,11,14,890),(98,15,23,1107),(98,24,26,1591),(98,28,35,1842),(98,36,41,2274),(98,43,46,2703),(98,47,49,2915),
(99,1,12,414,0),(99,14,22,1137),(99,23,29,1622),(99,32,40,2126),(99,41,50,2610),
(100,1,4,345),(100,6,8,662),(100,9,9,823,216,324),(100,10,11,878,216,324),(100,12,14,986,216,324),(100,15,15,1147,216,324),
(100,17,20,1301),(100,21,22,1517),(100,23,23,1624),(100,24,24,1678),(100,25,25,1732),(100,26,27,1787),(100,28,29,1896),(100,30,30,2003),(100,31,32,2056),(100,33,37,2165),(100,38,38,2433),
(100,40,40,2584),(100,41,41,2638),(100,42,43,2692),(100,44,44,2800),(100,45,45,2854),(100,46,46,2908),(100,47,47,2963)
]:block(*args)
# These reviewed source lines fill the measure despite fewer than 47 characters
# or a full stop at the right edge. Override the general short-line heuristic.
justified={82:[16,18,21,22],83:[12],90:[15],91:[47],93:[17],94:[3,11,30],95:[1,4,20],97:[4,25,27,28,29],99:[41],100:[4,15,22,23,28,31,42]}
for n,indices in justified.items():
 for b in pages[n]['blocks']:
  for l in b['lines']:
   if l['source_ocr_index'] in indices:l['align']=4
heads={81:[[731,'THE CONTACT BREAKERS.']],83:[[2562,'THE HIGH TENSION DISTRIBUTOR.']],86:[[2751,'HIGH TENSION CABLES.']],89:[[1436,'TIMING AND CONTROL GEAR.']],91:[[1378,'POSSIBLE TROUBLES.']],94:[[1948,'DAILY ROUTINE.']],95:[[1408,'WEEKLY ROUTINE.'],[2401,'MONTHLY ROUTINE.']],96:[[2679,'CHAPTER V.',12],[2843,'Running Instructions.',21,'Bold'],[2915,'MAXIMUM R.P.M.']],97:[[1191,'PRECAUTIONS WITH A NEW ENGINE.'],[1698,'FILLING WITH OIL.']],98:[[324,'COOLING SYSTEM.'],[825,'OIL PRESSURE.'],[1777,'A WARNING ABOUT THE SWITCHES.'],[2618,'STARTING THE ENGINE.']],99:[[1069,'AFTER STARTING UP.'],[2012,'SMOKY EXHAUST ON WIDE THROTTLE'],[2066,'OPENINGS.']],100:[[580,'AFTER THE PRELIMINARY RUN.'],[1220,'AFTER A FLIGHT.'],[2505,'PERIODIC ATTENTIONS']]}
for n,v in heads.items():pages[n]['headings']=v
caps={81:[[2370,'Fig. 66.'],[2459,'Cam Spindle Drive'],[2513,'(later pattern).']],82:[[1981,'Fig. 67.'],[2057,'A Main Contact Breaker Lever.']],84:[[2397,'Fig. 68.'],[2466,'The Distributor Head'],[2545,'(exterior).']],85:[[2515,'Fig. 69.'],[2578,'The Distributor Head'],[2641,'(interior).']],86:[[1945,'Fig. 70.'],[2038,'High Tension Cable Carrying Plate'],[2092,'(showing the numbering).']],87:[[2906,'Fig. 71.'],[2985,'Diagram indicating Sequence of Firing and'],[3039,'Distributor Connections.']],92:[[2166,'Fig. 73.'],[2230,'Main Wiring Diagram.']]}
for n,v in caps.items():pages[n]['captions']=v
for x,t in [(343,'Fig. 72.'),(357,'Ignition Timing Diagram'),(369,'(illustrating use of lamps).')]:pages[88]['vertical'].append(dict(x=x,y=565,width=437,text=t,align=1))
pages[96]['positioned_text']=[dict(x=28,y=2528,width=58,size=10.8,text='Fig. 74.',align=0),dict(x=95,y=2528,width=278,size=10.8,text='Rear View of Engine, showing Distributors and',align=1),dict(x=95,y=2582,width=278,size=10.8,text='Generator.',align=1)]
data=dict(batch=5,source_scans=[81,100],proofread_against='All twenty original staged scans, with close fractional, caption, spelling and misplaced-line checks.',pages=list(pages.values()))
(R/'data/batch05_transcription.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
alltext=json.loads((R/'data/baseline_v04_transcription.json').read_text());alltext['pages']+=data['pages'];(R/'data/transcription.json').write_text(json.dumps(alltext,ensure_ascii=False,indent=2))
changes=[dict(leaf=n,source_ocr_index=i,ocr=ocr[n][i]['text'],corrected=t) for n,vals in fix.items() for i,t in vals.items() if ocr[n][i]['text']!=t]
anomalies=[dict(leaf=81,text='pivotted'),dict(leaf=89,text='right-handedly..'),dict(leaf=90,text='GEN. ARM,'),dict(leaf=93,text='The fault may lay in'),dict(leaf=98,text='be drawn off by either of two methods, viz.:—',note='Misplaced printed line retained; the surrounding sentence continues on scan 0099 with minimum position.'),dict(leaf=100,text='aganst frost')]
(R/'data/batch05_corrections.json').write_text(json.dumps(dict(corrections=changes,retained_source_anomalies=anomalies,notes=['Source electrical/operating values retained without recalculation or modernization.','Braced fractions are editorial encoding for native stacked type.','Italic vide and backward retained as local character formatting.','Fig. 73 printed number is excluded only from its cleaned raster crop, with the nearby compass instruction preserved.']),ensure_ascii=False,indent=2))
if json.loads((R/'data/release.json').read_text())['release_id'].startswith('v04'):
 rid='v05_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 d=dict(release_id=rid,sla=f'Liberty_Master_scans0001-0100_{rid}.sla',pdf=f'Liberty_Master_scans0001-0100_{rid}.pdf',comparison=f'Liberty_Comparison_scans0081-0100_{rid}.pdf',package=f'Liberty_Project_scans0001-0100_{rid}.zip');(R/'data/release.json').write_text(json.dumps(d,indent=2))
print('Authored',len(pages),'pages;',sum(len(b['lines']) for p in pages.values() for b in p['blocks']),'body lines;',len(changes),'explicit OCR corrections.')
