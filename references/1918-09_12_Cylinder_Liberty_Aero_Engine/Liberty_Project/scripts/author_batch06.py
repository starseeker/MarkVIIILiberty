"""Reviewed text and native placements for scans 0101–0120 (printed pp99–118).
Original OCR remains separate. Braces encode native stacked fractions.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
ocr={p['leaf']:p['lines'] for p in json.loads((R/'data/batch06_ocr_draft.json').read_text())}
fix={
102:{6:'1. An engine must not be dismantled in any place',8:'2. There must be no mixing of parts. The various',12:'part is removed, it should be disposed of in a way which',13:'will insure its being refitted in its original location, e.g.,',15:'nuts loosely screwed back on to their studs or bolts, etc.',16:'3. As each part is removed, it should be cleaned,',20:'getting into the engine.',21:'4. All petrol and oil pipes or leads must be blown',23:'5. When a joint is made with an adhesive (e.g.,',24:'gold size) or with a paper washer, all traces of the old',28:'1. A number of “soft” washers are fitted to various',29:'joints in the distribution gear. New washers will'},
103:{4:'the special instructions on page 115; otherwise the',11:'heats up; and the mesh should therefore be set as',27:'way of exposing the main and big end bearings for'},
104:{5:'tapering oval,, so that the manifold can swing on the',6:'upper studs, as shown in Fig. 78. If one manifold is',33:'Minor attentions can be paid to the valves without',35:'makeshift method may be adopted in emergencies, e.g.,'},
105:{16:'127.',36:'The reference numbers are retained in the first two',37:'sets of notes which follow the sequence; the notes deal',38:'with:—',40:'(pp. 105—108).',41:'(b) The inspection and adjustment of the'},
106:{4:'tion of individual units (pp. 109—116).',6:'(pp. 116—129).'},
107:{6:'2. Wiring U and cables. Distributor covers',8:'3. Carburettors.',9:'4. Water elbows and induction manifolds.',10:'5. Camshafts, complete with upper inclined',12:'6. Lower inclined shafts.',13:'7. Vertical (generator) shaft.',14:'8. Oil pump unit.',15:'9. Water pump and lower vertical shaft.',16:'10. Cylinders.',17:'11. Pistons.',18:'12. Lower half of base chamber.',19:'13. Connecting rods.',20:'14. Crankshaft.',42:'then unscrew it five turns. Screw in outer nut till it'},
108:{1:'(i) Hold the inner nut and shaft stationary,',4:'(ii) Alternatively screw out the inner nut'},
109:{15:'5. Camshafts.—Each of these is removed as a unit,',18:'Unscrew packing nuts at base of long inclined',24:'In dismantling the units notice that—',28:'(ii) The lids of the cam compartments are not',32:'(iv) The bearings are “stepped” in external',34:'front. Each bearing is {1/32} in. larger than',38:'6. Lower Inclined Shafts.—These lift straight out'},
110:{18:'9. Water Pump Unit.—The dismantling of this unit'},
111:{2:'These details have been deliberately separated from',7:'applied to the various units.',8:'1. Propeller Hub.—Should be lapped to a fit on the',9:'shaft, about .001 in. tighter at the large end of the taper',11:'.010 in. between the top of the key and the bottom of',12:'the keyway in the hub.',22:'Remove traces of old adhesive from all jointing faces,'},
112:{7:'from .005-.010 in. end play, and from .001-.0015 in.',10:'rollers should have .010 in. side play in their forks, and',12:'is .001 in.',28:'.001-.003 in. on the shaft—i.e., the shake should just be',30:'should have .001-.003 in. end play between the camshaft',36:'.0005 in.; lower bush, 1.125 in. plus or minus .0005 in.'},
113:{3:'less than .005 in. or more than .010 in.',7:'{1/32} in. in outside diameter from front to rear. Line them'},
114:{4:'bearings must not exceed .004 in. Shims (.002 in.',11:'upper and lower vertical shafts is minimum .005 in.,',12:'maximum .010 in. (cold).',15:'cal clearance for all five gears in their housing is .001 in.,',16:'maximum, .005 in., select for .004 in. Their end play',17:'should not exceed .003 in.',24:'dowel pins carefully).',30:'(g) Fit lower filter, washer, and cover.',34:'9. Water Pump.—Examine rubber connections,',37:'End play at the ball bearing should not exceed .005 in.',38:'Scrap the old packing, and fit two new pieces, {3/16} in.',39:'in diameter and about 8{1/2} in. long, rubbing them with',41:'should not exceed .010 in. The lower vertical shaft',43:'of between .0015 in. and .0025 in. in its bush, and the',44:'end play should be between .005 in. and .008 in.',45:'Reassembling.—(a) Fit pump shaft and bearing in'},
115:{8:'the nut. Bolt up casing to ball bearing housing.',11:'play on shaft, .010 in.',12:'(g) Fit washer and pump cover.',15:'10. Cylinders.—The valves and cylinders will, of',18:'coils. and a strength of 23{1/2} lbs. when compressed to',19:'2{1/4} in.; outer exhaust springs ten coils, and a strength',20:'of 45 lbs. when compressed to 2{1/4} in. Test the valve'},
116:{2:'inlets, .002-.0045 in.',4:'“Ex” or “In,” together with the cylinder number—',5:'e.g., “R4.” Cylinders are marked with “R” or “L”',19:'are .018-.022 in.; the gudgeon pin fit in the piston,',22:'connecting rod are minimum .00025 in., maximum',24:'in the cylinder. The gap should be between .021 in.',25:'and .041 in. Select the top ring for .003 in. up and'},
117:{2:'must be of exactly the same weight as the scrapped',4:'3 lbs. is stamped on one of the flats outside the gudgeon',7:'location marks—e.g., “4R.” The pistons should be',10:'have from .010-.020 in. side play on the crankpin,',11:'and from .003-.004 in. diametrical clearance. The',14:'Worn parts should only be refitted by a skilled man.',19:'more than .008 in. end play. In reassembling the',21:'assembled bearing will not have more than .001 in. end',30:'Reassembling.—Bolt the gear wheel to its flange so',31:'that tooth marked “O” is in line with “O” on crank-'},
118:{6:'man. A clearance of .010 in. must exist between the',8:'the fit is known to be perfect, the hub may be re-',12:'nut need only be screwed up so that it bears snugly',15:'See that the base chamber studs are tight. Be'},
119:{5:'assembled with the tooth marked “O”',6:'in line with the “O” on the crankshaft',8:'(b) The washers (or “sleeves”) of the',9:'thrust bearing are selected from “thick”',10:'and “thin,” so that the end play in the',12:'.001 in. on assembly.',34:'housing. Fit the shaft. and test the mesh of its upper',36:'be .007 in. cold, with limits of .005 in. and .010 in. If',38:'thick) between the crankshaft bevel and its flange until',39:'the mesh is correct. Then tighten up the nuts on the',41:'assembly and fit all the bolts to the flanged joint of the',44:'location (e.g., “R3”) and for weight in one of the',46:'the engine. The weight marks indicate the number of',47:'ounces by which a piston exceeds 3 lbs.; if a piston is',48:'scrapped, the replacement should be of the original',49:'weight to an ounce. Oil the gudgeon pins before inser-'},
120:{4:'“R3”) on the edge of its base flange near the water',13:'to the cylinders. It is advisable to stop up the spark-',15:'being dropped into the combustion chambers.',21:'by which the manifolds are fixed to the cylinders. and',27:'9. Soak the washers for the water joints between',34:'slip the coupling tube and its rubber connections into'}
}
folios=[278,245,300,290,254,307,314,274,312,289,270,314,270,252,250,240,266,275,255,248]
pages={n:dict(leaf=n,printed_page=n-2,folio_baseline=y,blocks=[],headings=[],captions=[],legends=[],tables=[],subheads=[],vertical=[],positioned_text=[]) for n,y in zip(range(101,121),folios)}
def block(n,a,b,y,first=125,cont=0,step=54):
 lines=[]
 for i in range(a,b+1):
  l=dict(text=fix.get(n,{}).get(i,ocr[n][i]['text']),indent=first if i==a else cont,source_ocr_index=i)
  if n==111 and i==17:l['italic_words']=['et seq.']
  if (n,i) in [(116,5),(119,44),(120,4)]:l['small_digit_tokens']=['R4' if n==116 else 'R3']
  lines.append(l)
 pages[n]['blocks'].append(dict(y=y,step=step,lines=lines))
for args in [
(102,4,5,712,108),(102,6,7,820,108),(102,8,15,927,108),(102,16,20,1361,108),(102,21,22,1631,108),(102,23,26,1740,108),(102,28,35,2068,108),(102,36,40,2502,108),(102,41,45,2769,108),
(103,1,14,419,108),(103,17,20,1411,108),(103,22,31,1798,108),(103,33,38,2510,108),(103,40,41,2977,108),
(104,1,13,408,0),(104,15,25,1250,108),(104,26,31,1838,108),(104,33,42,2306,108),(104,44,45,2985,108),
(105,1,3,361,0),(105,6,16,771,108),(105,18,27,1545,108),(105,29,32,2243,108),(105,34,38,2618,125),(105,39,40,2889,250,375),(105,41,41,2996,250),
(106,3,4,2367,375,375),(106,5,6,2468,250,375),(106,8,8,2793,125),(106,9,12,2880,250,375),
(107,1,5,423,375,375),(107,6,7,691,250,375),(107,8,8,789,250),(107,9,9,844,250),(107,10,11,909,250,375),(107,12,12,1006,250),(107,13,13,1072,250),(107,14,14,1126,250),(107,15,15,1180,250),(107,16,16,1234,220),(107,17,17,1288,220),(107,18,18,1342,220),(107,19,19,1396,220),(107,20,20,1450,220),(107,35,43,2577,125),
(108,1,3,401,250,375),(108,4,6,592,250,375),(108,7,9,819,125),
(109,1,3,421),(109,4,7,584),(109,8,11,804),(109,12,14,1026),(109,15,16,1196),(109,17,17,1303),(109,18,20,1360),(109,21,22,1526),(109,23,24,1640),(109,25,27,1758,250,375),(109,28,30,1924,250,375),(109,31,31,2091,250),(109,32,35,2147,250,375),(109,36,37,2367,250,375),(109,38,44,2485),(109,45,48,2869),
(110,1,7,410,0),(110,8,12,789),(110,18,22,2332),(110,23,24,2603),(110,25,29,2712),(110,30,31,2976),
(111,2,7,456),(111,8,12,785),(111,17,17,2687),(111,18,23,2738),
(112,1,5,442),(112,6,12,709),(112,27,31,2362),(112,32,36,2634),(112,37,40,2894),
(113,2,3,1264),(113,4,13,1373),(113,16,17,2557),(113,18,19,2666),(113,20,24,2775),
(114,1,2,374),(114,3,12,518),(114,13,17,1104),(114,18,19,1405),(114,20,20,1514),(114,21,22,1568),(114,23,24,1677),(114,25,26,1784),(114,27,29,1893),(114,30,30,2051),(114,31,33,2110),(114,34,44,2303),(114,45,46,2936),
(115,1,2,362),(115,3,4,471),(115,5,5,577),(115,6,8,632),(115,9,11,793),(115,12,12,956),(115,15,21,2653),
(116,1,2,351,0),(116,3,7,491),(116,13,29,2103),
(117,1,5,376),(117,6,8,643),(117,9,13,808),(117,14,14,1076),(117,18,27,2224),(117,28,29,2764),(117,30,32,2872),
(118,1,14,397,0),(118,15,17,1156),(118,23,25,2688),(118,26,29,2852),
(119,2,3,372),(119,4,7,480,250,375),(119,8,12,695,250,375),(119,13,14,973),(119,15,24,1075),(119,25,28,1617,0),(119,29,31,1835),(119,32,42,1998),(119,43,49,2593),
(120,1,2,370,0),(120,3,15,478),(120,20,26,2170),(120,27,31,2548),(120,32,35,2808)
]:block(*args)
# Source line endings determine justification, including short full-width lines.
# A minimum text length excludes false wide OCR boxes on tiny terminal lines.
for n,p in pages.items():
 ls=[l for b in p['blocks'] for l in b['lines']]
 if not ls:continue
 rights=sorted(ocr[n][l['source_ocr_index']]['box'][2] for l in ls)
 edge=rights[int((len(rights)-1)*.8)]
 for l in ls:
  l['align']=4 if len(l['text'])>28 and '{' not in l['text'] and ocr[n][l['source_ocr_index']]['box'][2]>=edge-45 else 0
adjustments=[]
for p in pages.values():
 previous=None
 for b in p['blocks']:
  old=b['y']
  if p['leaf']==107 and b['lines'][0]['source_ocr_index']<=20:
   b['y']=423+(b['lines'][0]['source_ocr_index']-1)*54
  if previous is not None:b['y']=max(b['y'],previous+54)
  if b['y']!=old:adjustments.append(dict(leaf=p['leaf'],first_source_ocr_index=b['lines'][0]['source_ocr_index'],original_baseline=old,final_baseline=b['y']))
  previous=b['y']+(len(b['lines'])-1)*b['step']
heads={102:[[369,'CHAPTER VI.',12],[519,'Dismantling & Reassembling.',21,'Bold'],[615,'I.—PRELIMINARY NOTES.'],[1975,'SPECIAL HINTS.']],103:[[1222,'II.—ACCESSIBILITY OF INDIVIDUAL'],[1292,'COMPONENTS.'],[1681,'THE CRANKSHAFT.'],[2394,'CARBURETTORS.'],[2881,'INDUCTION MANIFOLDS.']],104:[[1155,'CAMSHAFTS AND CAMCASES.'],[2213,'VALVES.'],[2890,'CYLINDERS.']],105:[[575,'MAIN DRIVING BEVEL OF DISTRIBUTION'],[660,'GEAR.'],[1429,'DYNAMO GENERATOR.'],[2145,'OIL AND WATER PUMPS.'],[2537,'III.—GENERAL OVERHAUL.']],106:[[2706,'III.A.—DISMANTLING SEQUENCE.']],107:[[2457,'NOTES ON DISMANTLING OPERATIONS.']],111:[[371,'III.B.—REASSEMBLY OF UNITS.']],118:[[2625,'III.c.—NOTES ON RE-ERECTION.']]}
for n,v in heads.items():pages[n]['headings']=v
caps={101:[[2900,'Fig. 75.'],[2972,'Three-quarter Side View of Engine.']],106:[[2088,'Fig. 76.'],[2174,'Front End View of Engine.']],107:[[2256,'Fig. 77.'],[2346,'Details of Propeller Hub.']],108:[[2617,'Fig. 78.'],[2725,'Mode of removing Induction Manifolds.'],[2813,'(In the sketch the R.H. manifold is being swung up.)'],[2933,'A—Tapered holes for lower studs.'],[3021,'B—Point where slight clearance is allowed.']],110:[[2200,'Fig. 79.'],[2254,'Water Pump Unit.']],111:[[2362,'Fig. 80.'],[2449,'Low Compression Piston'],[2536,'(Navy type).']],112:[[2157,'Fig. 81.'],[2243,'Camshaft Bearings.']],113:[[1061,'Fig. 82.'],[1147,'Camshaft Bearing (showing assembling marks).'],[2346,'Fig. 83.'],[2431,'Camcase Cover (showing location mark).']],115:[[2363,'Fig. 84.'],[2450,'Valve.']],116:[[1860,'Fig. 85.'],[1949,'Main Thrust Bearing.']],117:[[2064,'Fig. 86.'],[2143,'Mounting of Main Driving Bevel on Crankshaft.']],118:[[2493,'Fig. 87.'],[2552,'Upper Half of Crankcase (rear end), showing Oil Trap.']],120:[[2043,'Fig. 88.'],[2100,'Housing and Bush of Lower Vertical Shaft.']]}
for n,v in caps.items():pages[n]['captions']=v
pages[112]['legends']=[dict(x=65,y=2041,width=266,step=43,size=9,align=1,lines=['A and A1—oil holes in plate and washer, to','be registered with oil duct A2 in bush.'],small_digit_tokens=['A1','A2'])]
data=dict(batch=6,source_scans=[101,120],proofread_against='All twenty original scans, including close fractional, decimal, caption and printed-anomaly views.',layout_adjustments=adjustments,pages=list(pages.values()))
(R/'data/batch06_transcription.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
alltext=json.loads((R/'data/baseline_v05_transcription.json').read_text());alltext['pages']+=data['pages'];(R/'data/transcription.json').write_text(json.dumps(alltext,ensure_ascii=False,indent=2))
changes=[dict(leaf=n,source_ocr_index=i,ocr=ocr[n][i]['text'],corrected=t) for n,vals in fix.items() for i,t in vals.items() if ocr[n][i]['text']!=t]
anomalies=[dict(leaf=102,text='nuts tc their original studs.'),dict(leaf=104,text='tapering oval,,',note='Apparent duplicate comma visible in the source.'),dict(leaf=107,text='The hub may now',note='The misplaced line on printed p96 appears to belong between this line and the two methods on p106; original page order and wording retained.'),dict(leaf=110,text='nine nuts Remove; shaft This; quite free If; soft drift The',note='Missing full stops retained.'),dict(leaf=115,text='coils. and a strength'),dict(leaf=117,text='deter / mine',note='No printed hyphen at the p115/116 split.'),dict(leaf=119,text='pange.'),dict(leaf=119,text='British practice The; Fit the shaft. and'),dict(leaf=120,text='cylinders. and')]
(R/'data/batch06_corrections.json').write_text(json.dumps(dict(corrections=changes,retained_source_anomalies=anomalies,notes=['Historical technical values retained without recalculation.','Native stacked fractions, italic et seq., and small baseline A1/A2/R3/R4 numerals.','Figure 75 uniformly reduced to fit the wider source crop on the existing page; no geometry correction or invented left border.','Figure 88 caption-only raster exclusion preserves both Dowel labels and leaders.']),ensure_ascii=False,indent=2))
print('Authored',len(pages),'pages;',sum(len(b['lines']) for p in pages.values() for b in p['blocks']),'body lines;',len(changes),'explicit OCR corrections.')
