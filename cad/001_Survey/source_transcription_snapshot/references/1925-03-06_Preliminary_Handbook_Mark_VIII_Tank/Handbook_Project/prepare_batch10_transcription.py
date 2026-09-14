#!/usr/bin/env python3
"""Source-checked transcription for printed pages 181–200.
OCR is a coordinate scaffold only; column identities and quantities are explicit.
Original readings are retained, including apparent printing errors.
"""
from pathlib import Path
import json,csv,re,statistics
import numpy as np
R=Path(__file__).resolve().parent
L=json.loads((R/'data/batch10_source_ocr_lines.json').read_text())
BODY_PATCH={
181:{0:'III. Fittings—Continued.',8:'IV. Tools (to be supplied in tool box with trays and place for each',9:'tool indicated in proper tray):',10:'Mechanics’—',11:'1 fitter’s chisel.',12:'1 drift, round, ⅞-inch.',13:'1 file, half round, 6-inch.',14:'1 file, round, 10-inch.',15:'1 32-ounce fitter’s hammer.',16:'1 pair electrician’s pliers.',17:'2 dozen assorted split pins.',18:'1 screw driver, 9-inch.',19:'1 set box spanners, complete.',20:'1 15-inch adjustable spanner.',21:'1 small spanner.',22:'1 spanner, double-ended, ⅛ by 3/16 inch.',23:'1 spanner, double-ended, ¼ by 5/16 inch.',24:'1 spanner, double-ended, ⅜ by 7/16 inch.',25:'1 spanner, double-ended, ½ by ⅝ inch.',26:'1 spanner, double-ended, ⅝ by ¾ inch.',27:'Tools (E.):',28:'Mechanics’—',29:'6 spanner, double-ended, ¾ by ⅞ inch.',30:'1 spanner, double-ended, ¾ by 1 inch.',31:'1 single-ended spanner, 1-inch.',32:'1 wrench pipe, 9-inch.',33:'1 oil syringe.',34:'4 grease guns.',35:'1 roll insulating tape.',36:'1 roll of 6 feet bare copper wire, No. 18, B. W. G.',37:'Following supplied, but not in tool box:',38:'1 wire cutter.',39:'2 oil cans.'},
182:{4:'V. Spares:',5:'Engine (A.)—',20:'Note.—This list of engine spare parts is intended as a general',21:'outline. U. S. A. must advise exact spares to be furnished with engine.',22:'Track. (from factory assembled): 1 complete road track shoe,',23:'links and pins, assembled.',24:'Transmission (A.): Brake band linings.',25:'Lighting system (E.):',29:'1 Bulb and battery for Hellesen hand light.',30:'1 Roll fuse wire.',31:'The above to be supplied in a tin box. (Similar to ammunition box.)'},
183:{9:'The side, front, and rear towing brackets have a V shackle, 1½',10:'inches in diameter and 2⅜ inches between jaws, and a shackle pin',11:'1½ inches in diameter which is threaded for a nut.',13:'turret by means of six ¾-inch bolts. It has a post 2½ inches in',14:'diameter and 2½ inches high, over which fits a steel cap 5 inches in',15:'diameter and 1⅛ inches high. The post is taped and threaded for a',16:'1-inch set screw, which passes through a hole in the cap and is',20:'1½ inches in diameter, each end of which has an eye 4½ inches in'}
}
HEAD={181:[],182:[32,39],183:[0]}
START={181:[40,42],182:[0,20,22,24],183:[1,4,9,12,19]}
SHORT={181:[41,43],182:[3,21,23,24,38],183:[3,8,11,18,21]}
BODY={}
for n,count in [(181,44),(182,44),(183,22)]:
 groups={}
 for w in csv.DictReader((R/f'data/ocr_batch10/p{n}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  if w['level']=='5' and w['text'].strip():groups.setdefault(tuple(w[k] for k in ['block_num','par_num','line_num']),[]).append(w)
 groups=list(groups.values()); assert len(groups)==len(L[str(n)])
 rows=[]
 for i in range(count):
  src=L[str(n)][i];box=src['box'];t=BODY_PATCH.get(n,{}).get(i,src['text']);head=i in HEAD[n]
  words=[w for w in groups[i] if re.fullmatch(r'[A-Za-z0-9.:-]+',w['text']) and not re.search('[gjpqy]',w['text']) and 12<=int(w['height'])<=50 and len(w['text'])>1]
  baseline=statistics.median(55+int(w['top'])+int(w['height']) for w in words) if words else box[3]-5
  if head:baseline=box[3]-1
  row=dict(source_line_index=i,text=t,source_box=box,baseline=baseline,heading=head,indent=10 if i in START[n] else 0,justify=not head and i not in SHORT[n],x=50,width=296,region='full')
  if n==181 and i<40:
   x=80
   if i in [0,8,27]:x=50
   if i in [1,10,28,37]:x=60
   if i==9:x=70
   row.update(x=x,width=346-x,indent=0,justify=i==8,region='list')
  if n==182 and (4<=i<=19 or 25<=i<=31 or 33<=i<=38 or 40<=i<=43):
   x=80
   if i==4:x=50
   if i in [5,15,16,25,31] or 33<=i<=37 or i>=40:x=60
   if i==38:x=50
   row.update(x=x,width=346-x,indent=0,justify=i==37,region='list')
  italic={(181,0):['Fittings'],(181,8):['Tools'],(181,27):['Tools'],(182,4):['Spares:']}.get((n,i))
  if italic:row['italic_runs']=italic
  if (n,i)==(182,20):row['smallcaps_prefix']='Note.'
  rows.append(row)
 # Keep source line breaks, but straighten the flatbed baseline drift.
 runs=[];run=[]
 for r in rows:
  if r['heading']:
   if run:runs.append(run);run=[]
   continue
  if run and (r['baseline']-run[-1]['baseline']>80 or r['region']!=run[-1]['region']):runs.append(run);run=[]
  run.append(r)
 if run:runs.append(run)
 for run in runs:
  if len(run)<2:continue
  yy=np.array([r['baseline'] for r in run]);xx=np.arange(len(run));step=float(np.clip(np.polyfit(xx,yy,1)[0],45,55));origin=float(np.median(yy-step*xx))
  for j,r in enumerate(run):r['source_baseline']=r['baseline'];r['baseline']=round(origin+step*j,3)
 BODY[str(n)]=rows

TABLES={};PATCH={};SECTIONS={}
def patch(n,changes):PATCH.setdefault(n,{}).update(changes)
def section(n,heads,indices,codes):
 """One source section, wrapped description lines grouped in a tuple."""
 parts=[v.rsplit(':',1) for v in codes.split()]
 assert len(indices)==len(parts),(n,heads,len(indices),len(parts))
 SECTIONS.setdefault(n,[]).append((heads,indices,parts))
def seq(a,z):return list(range(a,z+1))

section(184,[(19,7.3),(20,6.0)],seq(21,29),'M-3188:1 M-3189:2 M-3190:2 M-3191:2 M-3193:1 M-3196:1 M-3197:1 M-3198:1 M-568:2')
section(184,[(30,6.0)],seq(31,49),'M-3063:2 M-3064:2 M-3065:2 M-3066:10 M-3067:2 M-3068:2 M-3069:2 M-3070:2 M-3071:2 M-3072:2 M-3073:2 M-3020:10 O-38—21192:10 M-3023:10 M-3024:10 M-3025:10 A-37—21191:98 B-37—21191:98 M-2437:4')
section(184,[(50,6.0)],seq(51,68),'M-3015:split M-3016:1 M-3017:1 M-3018:1 M-3019:2 M-3020:12 M-3022:2 Q-38—21192:12 M-3023:12 M-3024:12 M-3025:12 M-3026:4 A-37—21191:60 B-37—21191:60 M-3029:1 M-3030:4 M-3031:1 M-3032:6')
section(184,[(69,7.3)],seq(70,83),'P-1:1 P-2:1 P-3:2 P-4:2 P-5:2 P-25:1 P-44:1 P-45:1 P-26:1 P-27:1 P-46:4 P-47:4 P-48:4 P-49:4')
patch(184,{51:'Side plate platform.',77:'Float-bolt nut.'})
section(185,[(4,7.3)],seq(5,44)+seq(46,55)+[57],'P-50:4 P-51:4 P-52:1 P-53:1 P-54:2 P-55:2 P-35:1 P-36:1 P-37:1 P-38:1 P-39:2 P-56:1 P-28:1 P-41:1 P-57:1 P-42:1 P-58:1 P-250:2 P-251:2 P-257:2 P-255:2 P-256:2 P-252:2 P-258:1 P-150:1 P-154:2 P-600:2 P-602:2 P-300:2 P-302:2 P-303:6 P-314:2 P-315:2 P-316:1 P-317:1 P-550:6 P-6:2 P-403:2 P-404:2 P-406:12 P-405:2 P-407:2 P-650:2 P-653:2 P-654:2 P-700:2 P-701:4 P-702:2 P-703:2 P-704:2 P-705:2')
section(185,[(58,7.3)],seq(59,70),'M-1583:4 M-1584:2 M-1585:4 M-1586:4 M-1587:1 M-1588:1 M-1590:1 M-1591:1 M-1592:1 M-1593:2 M-1594:2 M-1581:2')
section(185,[(72,7.3)],seq(73,83),'SH862A:1 SH861D:4 SH862B:1 SH866A:1 SH861A:6 SH861B:6 SH865D:6 SH861C:6 SH861E:1 SH867A:1 SH869A:1')
patch(185,{22:'Air valve.',23:'Air-valve cage.',31:'By-pass screws.',42:'Throat.',50:'Idling adjusting-screw bushing.',55:'Yoke end washer.',82:'Inner clutch drum.'})
section(188,[(4,7.3)],seq(5,23),'SH864B:1 SH864C:1 SH864A:1 SH863A:1 SH863B:1 SH863D:1 SH863C:1 SH855A:2 M-855:1 SH865B:1 SH865C:1 M-856:2 M-858:1 M-308:1 SH136A:1 SH849A:2 SH849B:1 SH849C:1 SH849D:1')
section(188,[(24,7.3)],seq(25,55),'SH953A:1 SH953B:2 -:2 SH953C:1 SH953D:1 -:3 M-4163:1 M-4162:1 M-4161:2 M-4155:4 M-4164:1 M-4160:1 M-4153:1 M-4148:1 M-4158:1 M-4159:1 M-4150:1 M-4156:1 M-4172:5 M-4152:1 -:1 M-4165:1 -:1 M-4151:1 S-673:1 S-676:1 SH955A:2 M-4175:2 M-4157:1 -:1 M-4154:1')
section(188,[(63,7.3)],seq(64,81),'M-563:2 M-564:4 M-565:1 M-566:1 M-567:64 M-568:64 M-569:42 M-570:12 M-571:1 M-572:2 M-573:2 M-574:3 M-575:2 M-576:5 M-577:2 M-578:2 M-579:2 M-581:1')
patch(188,{19:'Crank-shaft nut.',27:'No. 6 taper pins 2¾ inches long.',30:'⅛-inch diameter cotter pins.',36:'Clutch-stop anchor plate.',45:'⅛-inch split pin.',47:'5/32-inch split pin.',51:'Clutch-stop rod nut.',54:'⅛-inch split pin.',64:'High-speed brake-rod spring.',75:'Low-speed brake rod (forward) and clutch rod (center).',77:'Clutch rod (forward), high-speed brake rod (center), foot-brake rod (forward).',81:'Clutch rod (rear), Liberty.'})
section(189,[(6,7.3),(7,6.0)],[8,9]+seq(44,65),'SH964A:2 SH964B:2 SH964C:2 SH964D:2 SH964E:2 SH964F:4 SH964G:2 SH965A:1 SH965B:2 SH965C:2 SH965D:2 SH965E:4 SH965F:1 SH965G:2 SH965H:2 SH966A:2 SH966B:1 SH966C:1 SH966D:1 SH966E:1 SH966F:2 SH966G:2 SH967A:1 SH967B:1')
section(189,[(66,6.0)],seq(67,89),'SH967C:1 SH967D:1 SH967E:12 SH967F:5 SH967G:3 SH968A:1 SH968B:1 SH968C:1 SH968D:1 SH968H:1 SH968E:5 SH968F:12 SH968G:5 SH968K:1 SH969A:2 SH969B:1 SH969C:1 SH969D:2 SH970A:1 SH970B:1 SH970D:1 SH970E:1 SH970F:1')
section(189,[(90,7.3),(91,6.0)],seq(92,98),'M-638:1 M-639:3 M-640:10 M-641:2 M-642:1 M-4137:5 M-4131:1')
section(189,[(99,7.3),(100,6.0)],seq(101,108),'M-764:1 M-765:1 M-766:1 M-767:1 M-768:3 M-769:2 M-770:1 M-771:8')
patch(189,{8:'Engine-control lever bracket.',9:'Engine-control lever hub.',71:'5/16-engine control clevises.',79:'5/16-Clevis pins.',108:'Brake connecting link.'})
section(190,[(9,7.3),(10,6.0)],seq(11,38),'M-738:2 M-739:3 M-740:6 M-741:2 M-742:3 M-743:2 M-744:4 M-745:5 M-746:1 M-747:1 M-748:2 M-749:2 M-750:2 M-751:1 M-752:1 M-753:2 M-754:2 M-755:2 M-756:1 M-757:1 M-758:1 M-759:1 M-760:2 M-761:2 M-762:2 M-763:2 M-798:1 M-799:1')
section(190,[(39,7.3),(40,6.0)],seq(41,70),'M-772:1 M-773:1 M-774:1 M-775:4 M-776:2 M-777:1 M-778:1 M-779:1 M-780:1 M-781:2 M-782:1 M-783:1 M-784:4 M-785:1 M-786:1 M-787:1 M-788:2 M-789:4 M-790:3 M-791:1 M-792:1 M-793:1 M-794:1 M-795:1 -:1 -:1 -:2 M-810:4 M-811:1 M-812:1')
section(190,[(71,7.3),(72,6.0)],seq(73,82),'M-4128:1 M-4129:2 M-4130:2 M-4131:5 M-4132:2 M-4133:1 M-4134:1 M-4135:2 M-4136:2 M-4137:4')
patch(190,{19:'Control-lever fulcrum, starboard.',39:'CONTROL UNIT',49:'Reverse-lever pawl.',68:'Quadrant rack ferrule.'})
section(191,[(13,7.3),(14,6.0)],seq(15,18),'M-1032:1 M-1033:1 M-1034:1 M-1035:1')
section(191,[(19,7.3),(20,6.0)],seq(21,28)+[(29,30),31,32,(33,34)]+seq(35,40)+[(41,42)]+seq(43,52)+[(53,54),55,(56,57),58,59,60,(61,62)]+seq(63,72),'12211:1 8079:1 8056:1 8069:1 8213:2 8059:2 8058:1 12071:1 12075:2 8133:1 158:1 131:8 159:1 12517:1 8214:1 212:1 8215:1 12435:1 12081:1 111:8 101:8 8510:x 8345:1 8077:1 8239:1 8062:2 8065:1 8064:1 174:1 154:1 113:1 177:1 12123:1 12096:1 12097:1 12128:4 8453:8 8152:12 8450:24 8426:1 116:2 174:1 111:4 8133:1 101:2 106:2')
section(191,[(73,7.3),(74,6.0)],seq(75,89),'M-878:1 M-879:1 M-880:1 M-881:2 SH607C:606 M-886:1 M-887:1 M-888:2 M-889:1 M-891:2 M-892:1 M-897:1 M-898:1 M-899:1 SH606A:1')
patch(191,{14:'AIR DUCTS',29:'Water-pump outlet connection (cast with body) (tube 1⅜ inches O. D. by',30:'0.065 wall by 1⅞ inches).',31:'Water-pump body drain (plug ⅝ inch by 18 thd., hex. head).',32:'Water-pump body drain plug gasket (⅝ inch annular).',33:'Water-pump cover stud (¼ inch–28 by 1¼ inches, standard) (¼ inch be-',35:'Water-pump shaft key (3/16 inch by ⅛ by ⅝ inch)',41:'Water-pump inlet connection (cast with cover) (tube 2 inches O. D. by',42:'0.065 wall by 1⅞ inches).',43:'Water-pump cover stud washer (¼ inch).',44:'Water-pump cover stud nut (¾ inch by 28 thd., standard).',52:'Water-pump bevel-driver bushing dowel (3/16 inch by ⅜ inch).',53:'Water-pump bevel-driver bushing housing (rear) screw (¾ inch–16 by 3¼',55:'Water-pump bevel-driver bushing housing (rear) screw washer (⅜ inch).',57:'M. Ga. No. 18 (0.0475) by 6).',60:'Cylinder water-inlet manifold extension (left).',61:'Cylinder water-inlet manifold extension hose (1⅜ inches I. D. by 1⅝ inches',62:'O. D. by 1¾ inches long).'})
section(192,[(5,7.3),(6,6.0)],seq(7,15),'SH606B:1 SH606C:1 SH606D:1 SH607A:1 SH607B:2 SH611A:1 SH611B:1 SH612A:1 SH612B:1')
section(192,[(16,6.0)],seq(17,19),'M-889:1 M-891:2 M-892:1')
section(192,[(20,6.0)],seq(21,26),'M-1193:1 M-1194:1 M-1195:1 M-1196:1 M-1197:1 BA109—21149:1')
section(192,[(48,6.0)],seq(49,85),'M-1228:1 M-1229:1 M-1230:1 M-1231:1 SH975C:3 M-1233:1 SH975B:1 SH975A:1 M-1236:1 SH976C:2 M-1238:1 M-1239:1 -:1 -:1 -:1 -:2 -:2 -:2 -:1 M-1240:1 M-1241:2 M-1242:1 SH199C:1 -:2 -:4 -:1 -:1 M-1244:1 M-1245:1 -:2 -:1 SH199B:2 SH976B:1 SH975E:1 SH976A:2 SH974A:1 SH975D:1')
section(192,[(86,7.3)],seq(87,90),'SH40AB:50 SH40AC:50 SH40AD:50 SH40AE:50')
section(192,[(91,7.3),(92,6.0)],seq(93,98),'12104:1 12105:1 8100:2 8400:2 8111:2 8112:2')
patch(192,{18:'Radiator support bracket (front).',20:'WATER TANK',60:'Plate bracket for radiator drain cock.',61:'½-inch bore cock inlet tapped ½-inch pipe thread outlet to take hose pipe.',62:'¾-inch by 2-inch bolt for plate bracket.',63:'½-inch bore copper pipe, 16-gage, 7 feet 8 inches long.',66:'Union with one end screwed ¾-inch pipe thread.',67:'¾-inch W. I. knee with nipple.',68:'Pipe joint for water tank. outlet.',71:'Vapor pipe from engine-water outlet.',72:'Flexible coupling 2½ inches long (for 1-inch W. I. piping).',73:'Clips for coupling 2½ inches long (for 1-inch W. I. piping).',74:'1-inch Whit. Gas. plug (on M 1229).',78:'⅜-inch and ⅞-inch bolt (with Grover washer).',79:'½-inch by ½-inch set screw (with grover washer).',89:'Collar busihng.'})
section(194,[(11,7.3),(12,6.0)],seq(13,27)+[(28,29)],'8481:2 8113:2 8114:2 8482:2 8115:2 8116:2 8483:2 8117:2 8118:2 8484:2 8119:2 8120:2 12485:2 12248:2 12249:2 8101:48')
section(194,[(30,7.3),(31,6.0)],[32,33,34,(35,36)]+seq(37,42)+[(43,44)]+seq(45,52),'12250:2 8376:2 8219:8 177:2 8379:2 8108:14 157:14 177:12 8093:2 8059:x 171:14 200:14 106:14 13006:2 12486:2 12124:2 8095:10 8467:2 8133:2')
section(194,[(53,7.3),(54,6.0)],seq(55,61)+[(62,63)]+seq(64,72),'158:2 178:36 102:36 112:72 107:36 8088:2 169:2 177:2 8462:2 157:4 8122:2 8133:1 8425:12 8424:12 8020:12 8019:12 8471:48')
section(194,[(73,7.3),(74,6.0)],seq(75,79),'8082:24 8083:24 8084:24 8085:24 8086:24')
patch(194,{28:'Cam-shaft bearing upper to lower half screw (screw No. 8—32 by ½-inch',39:'Cam-shaft bearing lock screw gasket (⅜-inch annular).',42:'Cam-shaft gear shim.',43:'Cam-shaft gear bolt (¼-in.–28 by 11/16-inch special) (1⅝ inches between head',45:'Cam-shaft gear bolt nut (¼-inch–28.)',46:'Cam-shaft gear bolt cotter (1/16 inch by ½).',50:'Cam-shaft housing cover.',55:'Cam-shaft housing cover (propeller end plug gasket) (⅝ inch annular).',56:'Cam-shaft housing cover bolt (5/16-inch—24 by 2 3/32 inches special).',57:'Cam-shaft housing cover bolt nut (5/16-inch—24 thd. standard).',58:'Cam-shaft housing cover bolt washer (5/16-inch).',59:'Cam-shaft housing cover bolt cotter (1/16 inch by ⅝ inch).',61:'Cam-shaft housing front cover gasket (1⅞-inch annular).',64:'Cam-shaft housing front end cover oil connection.',65:'Cam-shaft housing front end cover oil connection gasket (⅜-inch annular).',77:'Cam-shaft rocker lever roller pin sleeve.'})
section(196,[(10,7.3),(11,6.0)],seq(12,25),'8087:24 8089:24 102:24 107:24 8102:2 8107:2 8092:2 8094:2 160:4 156:2 8109:2 8103:2 8110:2 186:2')
section(196,[(26,7.3),(27,6.0)],[28,(29,30),(31,32),33,34,35],'8139:2 181:8 101:8 106:8 8068:2 8066:2')
section(196,[(36,7.3),(37,6.0)],seq(38,48),'8208:2 8141:2 8063:4 8070:2 8343:2 8072:2 3144:2 3076:2 8142:2 172:2 159:4')
section(196,[(49,7.3),(50,6.0)],seq(51,60)+[(61,62)]+seq(63,71),'12243:1 12036:1 12038:1 8518:1 157:1 12135:1 12136:6 8174:2 12039:1 8040:1 158:1 161:1 161:2 8033:14 8034:2 115:16 12548:16 110:32 105:32 8018:7')
section(196,[(72,7.3),(73,6.0)],[(74,75),76,77,78,79],'132:10 140:4 8131:2 8130:11 8129:1')
patch(196,{20:'Cam-shaft driving shaft (upper) gear key (3/16 by ⅛ by 13/16 inch).',21:'Cam-shaft driving shaft (upper) gear pin (⅛ by 1 3/32 inches).',24:'Cam-shaft driving shaft (upper) housing flange.',29:'Cam-shaft driving shaft (upper) housing flange stud (¼-inch—28 by 1¼',30:'inches std.) (¼ inch between nut and surface)',31:'Cam-shaft driving shaft (upper) housing flange .stud nut (¼-inch—28 thd.,',33:'Cam-shaft driving shaft (upper) housing flange stud nut (1/16 inch by ½ inch).',44:'Cam-shaft driving shaft (lower) bearing spacer.',45:'Cam-shaft driving shaft (lower) gear.',46:'Cam-shaft driving-shaft (lower) nut (nut ⅝ inch—18 thd. special).',47:'Cam-shaft driving-shaft, lower cotter (⅛ inch by 1 inch).',48:'Cam-shaft driving-shaft, lower gear key (3/16 inch by ⅛ inch by ⅝ inch).',51:'Crank case, lower half assembly.',54:'Crank case, lower half oil-hole plug (plug ⅝ inch—18 thd. Hex. head).',55:'Crank case, lower half oil hold plug gasket (⅜-inch annular).',60:'Crank case, lower half oil pump-suction tube extension.',61:'Crank case, lower half oil-pump suction tube extension gasket (⅝-inch',63:'Crank case, lower half oil manifold plug (⅛-inch pipe).',64:'Crank case, lower half oil-pump suction tube plug (⅛-inch pipe).',65:'Crank-shaft bearing bolt (long).',67:'Crank-shaft bearing bolt washer ½ (inch).',69:'Crank-shaft bearing bolt cotter (3/32 inch by ⅞ inch).',70:'Crank-shaft bearing bolt nut (½ inch—20 thd. std).',74:'Oil pump to crank-case stud (¼ inch—28 by 1 7/16 inch standard) (7/16 inch be-',76:'Water pump to crank-case stud (⅜ inch—24 by 1 15/16 inch standard).'})

section(198,[(18,7.3),(19,6.0)],[12,13,20,14,21,22,23,24,25,15,(26,27),28,16],'8530:1 8527:1 8528:1 8529:1 12244:1 12035:1 8216:1 8217:1 8344:1 8218:1 117:2 101:2 106:2')
section(198,[(29,7.3),(30,6.0)],[31,32,33,17]+seq(34,48)+[(49,50)]+seq(51,60)+[(61,62)]+seq(63,70)+[(71,72),73,74,75,(76,77),(78,79),80,81,82,(83,84),85,86,87,88],'12137:1 8156:2 8155:2 8162:2 8151:2 8157:2 8159:2 8163:2 8160:2 261:4 261:6 261:4 8166:2 8164:2 8165:2 8523:2 8522:2 8521:2 8158:2 132:4 111:4 101:4 106:4 12237:1 8206:1 8205:1 245:6 8365:1 8366:1 8172:1 131:2 111:2 101:2 106:2 13148:1 13418:1 13459:6 13435:6 8390:1 116:50 111:100 101:50 106:50 187:2 165:2 113:8 103:4 108:4 151:100 108:100 103:72 108:4 101:3')
patch(198,{0:'NOMENCLATURE LIST—Continued',5:'Description and Location',14:'Crank case, lower half sump (front) oil strainer screen-top.',16:'Crank case, upper half drain tube bolt nut (1/16 inch by ½ inch).',22:'Crank case, upper half.',26:'Crank case, upper half drain tube bolt (¼ inch—28 by 1⅛ inch standard)',27:'(11/16 inch between head and nut).',28:'Crank case, upper half drain tube bolt nut (¼ inch—28 thd. standard).',32:'Crank case oil-filler assembly.',39:'Crank-case oil-filler cover spring escutcheon pin (No. 14 by ⅜ inch).',40:'Crank-case oil-filler cover hinge escutcheon pin (No. 14 by ⅜ inch).',41:'Crank-case oil-filler cover lock escutcheon pin (No. 14 by ⅜ inch).',49:'Crank-case oil-filler stud ((¼ inch—28 by 1 7/16 inches, standard) (7/16 inch',51:'Crank-case oil-filler stud washer (¼ inch.).',52:'Crank-case oil-filler stud nut (¼ inch—28 thd., standard).',53:'Crank-case oil-filler stud cotter (1/16 by ½ inch.).',57:'Crank-case (rear end) cover screw (⅜ inch—24 by 1 inch).',60:'Crank-case breather gasket (2-bolt gasket 11/16-inch hole).',61:'Crank-case breather stud (¼ inch—28 by 1¼ inches, standard) (¼ inch',62:'between nut and surface).',63:'Crank-case breather stud washer (¼ inch).',64:'Crank-case breather stud nut (¼ inch—28 thd., standard).',65:'Crank-case breather stud cotter (1/16 inch by ½ inch).',70:'Propeller hub thrust bearing oil cup (brass).',71:'Crank-case, upper to lower half bolt (small) (¼ inch—28 by 15/16 inch) (½',72:'inch between head and nut).',73:'Crank case, upper to lower half bolt, small washer (¼ inch).',74:'Crank case, upper to lower half bolt, small nut (¼ inch—28 thd., standard).',75:'Crank case, upper to lower half bolt, small cotter (1/16 by ½ inch).',76:'Crank case, upper to lower half bolt, short (⅜ inch—24 by 4⅜ inches, special)',77:'(3⅞ inches between head and nut).',78:'Crank case, upper to lower half bolt, long (⅜ inch—24 by 5⅛ inches, special)',79:'(4⅝ inches between head and nut).',80:'Crank case, upper to lower half bolt washer (⅜ inch).',81:'Crank case, upper to lower half bolt nut (⅜ inch—24 thd., standard).',82:'Crank case, upper to lower half bolt, cotter (3/32 inch by ⅝ inch).',83:'Cylinder to crank-case stud (⅜ inch—24 by 1⅞ inches, special) (¼ inch be-',84:'tween nut and surface).',85:'Cylinder to crank-case stud cotter (3/32 inch by ⅝ inch).',86:'Cylinder to crank-case stud nut (⅜ inch—24, standard).',87:'Water pump to crank-case stud cotter (3/32 inch by ⅝ inch).'})
section(199,[(7,7.3),(8,6.0)],seq(9,15)+[(16,17),(18,19)]+seq(20,26),'103:4 113:4 111:10 8348:1 106:10 8389:1 177:3 101:8 106:8 12346:4 8234:28 12353:1 197:4 13157:1 101:10 13443:-')
section(199,[(27,7.3),(32,6.0)],seq(33,38)+[(39,40)]+seq(41,57),'12514:1 12546:1 8138:1 13142:6 8067:1 8502:x 198:6 102:6 107:6 13481:1 13482:1 13483:11 13484:12 13485:12 13486:11 13487:1 13488:6 13489:5 103:12 157:24 108:12 13490:12 12048:1 12252:1')
section(199,[(58,7.3),(60,6.0)],seq(61,75),'13442:6 13440:6 12250:24 13228:12 13220:24 107:24 13460:6 13461:6 8028:12 13441:6 13422:12 13227:6 13251:12 109:12 8007:12')
section(199,[(76,7.3),(77,6.0)],seq(78,82),'8385:12 8106:12 8231:12 8098:12 8031:12')
patch(199,{9:'Water pump to crank-case stud nut (⅜ inch—24, standard).',10:'Water pump to crank-case stud washer (⅜ inch).',11:'Oil pump to crank-case stud washer (¼ inch).',13:'Oil pump to crank-case stud cotter (1/16 inch by ½ inch).',16:'Cam-shaft driving shaft, lower bearing connecting-stud nut (¼ inch—28,',17:'standard).',18:'Cam-shaft driving shaft, lower bearing connecting-stud cotter (1/16 inch by ½',38:'Crank-shaft gear shim.',39:'Crank-shaft gear bolt (5/16 inch—24 by ⅞ inch, special) (3/32 inch between head',41:'Crank-shaft gear bolt (5/16 inch—24, standard).',42:'Crank-shaft gear-bolt cotter nut (1/16 inch by ⅝ inch).',43:'Crank-shaft gear end plug.',47:'Gasket (1¼ inches, annular).',48:'Gasket (1⅜ inches, annular).',65:'Connecting-rod (forked end) bolt nut (5/16 inch—24 thd., standard).',66:'Connecting-rod (forked end) bolt cotter (1/16 inch by ⅝ inch).',68:'Connecting-rod crank-shaft bearing (lower half).',69:'Connecting-rod crank-shaft bearing dowel.',70:'Connecting-rod (plain end) and piston pin bushing assembly.',72:'Connecting-rod (plain end) cap.',73:'Connecting-rod (plain end) bolt nut (7/16 inch—20 thd., special).',74:'Connecting-rod (plain end) bolt cotter (3/32 inch by ¾ inch).'})
section(200,[(43,7.3),(44,6.0)],seq(45,61)+[(62,63),(64,65),66,67,(68,69),(70,71)]+seq(72,85),'8032:12 8030:24 8099:12 8359:12 8025:12 8026:12 8126:12 8127:12 8021:24 8253:24 8254:12 8357:12 8090:24 8023:24 8524:48 8591:24 181:24 179:12 180:12 102:24 107:24 162:24 163:24 103:24 108:24 167:24 112:24 8176:12 113:24 108:24 113:24 8173:12 8170:12 8171:12 8539:12 8538:12 8152:12')
section(200,[(86,7.3),(87,6.0)],seq(88,99)+[(100,101)]+seq(102,107),'12229:2 8358:2 116:10 111:20 101:10 106:10 8333:1 8468:1 8469:1 8470:1 210:2 8472:1 8338:1 8340:1 196:2 106:2 12490:1 12282:1 12283:6')
section(200,[(108,7.3),(109,6.0)],seq(110,117),'12388:2 12387:2 8332:24 8397:24 -:24 8417:1 12987:1 12988:1')
patch(200,{44:'CYLINDER—continued',46:'Cylinder-elbow flange.',59:'Valve-spring collar key.',61:'Spark-plug gasket (¾ inch, annular).',62:'Cam-shaft housing to cylinder stud short (5/16 inch—24 by 2 7/10 inches, special)',63:'(1 7/16 inches between nut and surface).',64:'Cam-shaft housing to cylinder stud long (5/16 inch by 4⅜ inches, special) (3⅜',65:'inches, between nut and surface).',66:'Cam-shaft housing to cylinder stud nut (5/16 inch—24 thd., standard).',68:'Exhaust header stud (⅜ inch—24 by 1¼ inches, special) (5/16 inch between nut',70:'Intake header stud (⅜ inch—24 by 1½ inches, special) (9/16 inch between nut',71:'and surface.',73:'Intake header stud cotter (3/32 inch by ⅝ inch).',74:'Exhaust header stud nut (⅜ inch—24 thd., special).',75:'Cam-shaft housing to cylinder stud washer (5/16 inch).',78:'Exhaust header stud cotter (3/32 inch by ⅝ inch).',79:'Intake header stud washer (⅜ inch).',90:'Distributor bolt (¼ inch—28 by 15/16 inches) (½ inch between head and nut).',91:'Distributor-bolt washer (¼ inch).',92:'Distributor-bolt nut (¼ inch—28 std.).',93:'Distributor-bolt cotter (1/16 inch by ½ inch).',97:'Distributor-control connecting-rod clevis (brazing) (5/16-inch clevis brazing).',99:'Distributor-control connecting-rod end (¼-inch rod end).',100:'Distributor-control connecting-rod clevis (right hand) (¼ inch adj. clevis',102:'Distributor-control connecting-rod clevis—RH check nut (¼ inch, 28 thd.).',103:'Distributor-control connecting-rod clevis pin (¼-inch clevis).',104:'Distributor-control connecting-rod clevis pin cotter (1/16 inch by ½ inch).'})

def clean(n,i):
 if i in PATCH.get(n,{}):return PATCH[n][i]
 t=L[str(n)][i]['text']
 if '|' in t:t=t.rsplit('|',1)[-1]
 return t.strip()

for n,sections in SECTIONS.items():
 groups={}
 for w in csv.DictReader((R/f'data/ocr_batch10/p{n}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  if w['level']=='5' and w['text'].strip():groups.setdefault(tuple(w[k] for k in ['block_num','par_num','line_num']),[]).append(w)
 groups=list(groups.values());assert len(groups)==len(L[str(n)])
 desc_min={184:680,185:530,188:685,189:530,190:685,191:530,192:630,194:680,196:680,198:660,199:550,200:580}[n]
 def baseline(i):
  ww=[w for w in groups[i] if int(w['left'])+100>=desc_min and 10<=int(w['height'])<=32 and re.fullmatch('[A-Za-z0-9.()—–-]+',w['text']) and not re.search('[gjpqy]',w['text']) and len(w['text'])>1]
  return float(statistics.median(55+int(w['top'])+int(w['height']) for w in ww)) if ww else float(L[str(n)][i]['box'][3]-3)
 out=[]
 for heads,indices,codes in sections:
  hs=[dict(text=clean(n,i),size=size,baseline=baseline(i),source_line_index=i) for i,size in heads]
  lines=[];rr=[]
  for item,(code,qty) in zip(indices,codes):
   ids=list(item) if isinstance(item,tuple) else [item]
   row=dict(part='' if code=='-' else code,quantity='' if qty=='-' else qty,source_line_indices=ids,lines=[])
   for i in ids:
    r=dict(text=clean(n,i),baseline=baseline(i),source_line_index=i,source_box=L[str(n)][i]['box']);lines.append(r);row['lines'].append(r)
   rr.append(row)
  # A robust common baseline grid preserves intentional blank lines and wraps.
  yy=np.array([r['baseline'] for r in lines]);d=np.diff(yy);step=float(statistics.median(v for v in d if 17<v<37)) if len(yy)>1 else 25.
  steps=[0]
  for v in d:steps.append(steps[-1]+max(1,round(v/step)))
  step=float(np.clip(np.polyfit(steps,yy,1)[0],22,28)) if len(yy)>1 else step
  origin=float(statistics.median(yy-np.array(steps)*step))
  for j,r in enumerate(lines):r['source_baseline']=r['baseline'];r['baseline']=round(origin+steps[j]*step,3)
  if n==184 and rr[0]['part']=='M-3015':
   # Description and part number are centered across the two hand quantities.
   rr[0]['split_quantities']=['(L.H.) 2','(R.H.) 1']
   rr[0]['lines'][0]['baseline']-=13
  if n==190 and any(r['source_line_indices']==[65] for r in rr):
   for row in rr:
    if row['source_line_indices'][0] in [65,66,67]:row['part_group']='No numbers'
  out.append(dict(headings=hs,rows=rr))
 title=clean(n,1 if n==199 else 0)
 TABLES[str(n)]=dict(title=title,title_baseline=baseline(1 if n==199 else 0),sections=out)

for name,obj in [('body_batch10.json',BODY),('tables_batch10.json',TABLES),('batch10_source_ocr_lines.json',L)]:
 (R/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(R/'data/batch10_body_transcription.txt').write_text('\n\n'.join(f'PRINTED PAGE {n}\n'+'\n'.join(r['text'] for r in rr) for n,rr in BODY.items())+'\n')
(R/'data/batch10_table_transcription.tsv').write_text('page\tpart_number\tquantity\tdescription\n'+''.join(f'{n}\t{r["part"]}\t{r["quantity"]}\t'+ ' / '.join(l['text'] for l in r['lines'])+'\n' for n,t in TABLES.items() for sec in t['sections'] for r in sec['rows']))
print('Body lines:',sum(map(len,BODY.values())),'table rows:',sum(len(s['rows']) for t in TABLES.values() for s in t['sections']))
