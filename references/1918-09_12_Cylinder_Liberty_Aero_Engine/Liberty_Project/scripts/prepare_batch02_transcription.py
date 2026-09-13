"""Reviewed source-line transcription for scans 0021–0040. OCR is only a draft."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
D={p['leaf']:p['lines'] for p in json.loads((R/'data/batch02_ocr_draft.json').read_text())}
FIX={
22:{7:'In addition, eight pairs of heavy studs are fixed in the',9:'bearing, and one pair at each of the six shorter bearings;'},
23:{26:'rust.'},
25:{4:'piece is heavily ribbed, both laterally and longitudinally,',5:'to support the front main bearing. The lower half of',8:'rectangular section, and houses the drive for the oil and',14:'in caps from bolts.',21:'pumps, the oil pump unit being bolted beneath the rear',30:'half of the base chamber. Screwed plugs at either end',45:'stems are inclined towards the cylinder axis at 13{1/2}°, the',48:'within the included angle. All the valves are inter-'},
27:{3:'machined on the valve stem.',8:'marked “R” and “L” respectively. The camcases are',13:'rear ends of the shafts. Notched flanges or “hubs,”',18:'“stepped” in outside diameter, that at the rear end',19:'being the largest, the next {1/32} in. smaller, etc. The five',22:'the camcase by large grubscrews entered from the side.'},
28:{17:'in a square hole at the outer end of the arm: the bolt',27:'tribution gears. The main bevel on the crankshaft',28:'drives upper and lower vertical shafts. The upper'},
29:{20:'with its top and bottom bevels, and runs in a split'},
30:{4:'through this bearing. The bottom bevel (21 teeth) of',10:'is provided with a phosphor bronze bush at the top of',11:'the pump casing. The pumps run at 1{1/2} times engine',16:'of 22 teeth, so that all three shafts run at 1{1/2} times',20:'in two pieces, coupled together by a splined joint at the',22:'at the top of the inclined shafts have 16 teeth, and the',24:'illustrations show, the upper vertical shaft runs in two',28:'a phosphor bronze bush, housed in the shaft casing.',36:'vertical shaft at 1{1/2} times engine speed. The spindle is',40:'wound round the shaft inside two sleeves; a star washer is',45:'water pump towards the right- and left-hand sides of the',48:'side of the engine below the cylinder base level. The'},
31:{3:'and are jointed to rubber connections by stub pipes',5:'The type of water clip employed throughout the Liberty'},
33:{28:'follows:—',31:'of the pump until it has actually been dismantled; it',32:'is plentifully illustrated by sectioned and perspective',33:'drawings in Figs. 24-29. The diagram in Fig. 25 and'},
34:{4:'filter is secured by the bottom cover. The relief valve',5:'is situated immediately outside the delivery port of the',32:'at C1, passing on its way the relief valve D.',44:'in the front catchpit will be sucked along the pipe E1'},
38:{2:'catchpit, i.e., the pump casing. It will enter the second',4:'and at F1 it will enter the main return pipe F, leading',6:'zontally, drainage oil will collect in both oil wells',11:'state that they suck oil quite efficiently over a much',14:'pumps being formed of only three gear wheels, which-',17:'Figs. 27-30 show various sectioned views of the',32:'along the centre line. This trough accommodates two',39:'the main bearings, in which the oil is distributed by suit-',43:'crankshaft through a suitable hole, travels up the',44:'rear web of the throw into the crank-pin, and is forced'},
39:{9:'The little end bushes are lubricated solely by splash,',11:'centre of the little end.'},
40:{3:'The front end of each camcase is sealed by a screwed',25:'the bearings into each compartment, and is splashed up',29:'above the point at which the roller arm joins the spindle:',30:'a small baffle cast on the under side of the camcase lid'}
}
# start, end, baseline in source pixels, first-line indent in source pixels.
BLOCKS={
22:[(1,4,1416,108),(5,12,1633,108)],
23:[(2,14,348,108),(17,26,2254,0),(27,30,2788,108)],
25:[(1,11,335,108),(12,14,924,108),(15,22,1087,108),(23,36,1516,108),(37,38,2267,108),(39,41,2376,108),(43,49,2631,108)],
26:[(3,7,1942,108)],
27:[(2,3,322,0),(7,9,1428,108),(10,15,1591,108),(16,29,1914,108),(30,35,2670,108)],
28:[(1,22,373,108),(26,32,2662,108)],
29:[(1,2,351,0),(3,5,450,108),(17,20,2788,108)],
30:[(1,12,320,0),(13,28,969,108),(29,30,1831,108),(32,43,2075,108),(44,48,2726,108)],
31:[(1,7,419,0),(8,17,795,108),(18,19,1338,108),(20,21,1444,108)],
32:[(2,5,559,108)],
33:[(3,20,721,108),(21,26,1695,108),(27,28,2020,108),(30,35,2234,108),(36,46,2553,108)],
34:[(1,6,457,0),(26,32,1877,108),(33,42,2283,108),(43,47,2856,108)],
38:[(1,8,406,0),(9,16,839,108),(17,24,1274,108),(25,28,1703,108),(31,46,2219,108)],
39:[(2,4,396,0),(5,7,557,108),(9,11,875,108),(30,41,2421,108)],
40:[(1,2,413,108),(3,17,521,108),(21,33,2272,0),(34,35,2974,108)]}
pages=[]
for n in range(21,41):
 blocks=[]
 for start,end,y,indent in BLOCKS.get(n,[]):
  lines=[dict(text=FIX.get(n,{}).get(i,D[n][i]['text']),indent=indent if i==start else 0,ocr_line=i) for i in range(start,end+1)]
  blocks.append(dict(y=y,step=54,lines=lines))
 pages.append(dict(leaf=n,printed_page=n-2,blocks=blocks))
O=dict(batch=2,source_leaves=[21,40],review='All source pages visually read; OCR errors corrected; historic terminology, line-end hyphenation, figure references and page breaks retained.',pages=pages)
(R/'data/batch02_transcription.json').write_text(json.dumps(O,ensure_ascii=False,indent=2))
base=json.loads((R/'data/batch01_transcription.json').read_text());base['pages']+=pages
(R/'data/transcription.json').write_text(json.dumps(base,ensure_ascii=False,indent=2))
(R/'data/batch02_transcription_corrections.json').write_text(json.dumps(FIX,ensure_ascii=False,indent=2))
print(sum(len(b['lines']) for p in pages for b in p['blocks']),'reviewed body lines')
