#!/usr/bin/env python3
"""Source-checked native nomenclature, printed pages 221–239; index is in layout_batch12.py."""
from pathlib import Path
import json,csv,re,statistics
import numpy as np
R=Path(__file__).resolve().parent
L=json.loads((R/'data/batch12_source_ocr_lines.json').read_text())
BODY={};TABLES={};PATCH={};SECTIONS={}
def patch(n,changes):PATCH.setdefault(n,{}).update(changes)
def section(n,heads,indices,codes):
 parts=[v.rsplit(':',1) for v in codes.split()]
 assert len(indices)==len(parts),(n,heads,len(indices),len(parts))
 SECTIONS.setdefault(n,[]).append((heads,indices,parts))
def seq(a,z):return list(range(a,z+1))
def m(a,z,qty=2):return ' '.join(f'M-{i}:{qty}' for i in range(a,z+1))
section(221,[(4,7.3),(5,6)],seq(7,59),'M-2074:1 M-2075:1 M-2076:2 M-2077:1 '+m(2078,2081,4)+' M-2082:2 '+m(2083,2085,4)+' M-2086:1 '+m(2087,2091)+' M-2092:4 '+m(2093,2107)+' '+m(2108,2111,1)+' M-2112:2 M-2113:2 '+m(2114,2116,1)+' '+m(2118,2127,1))
section(221,[(60,7.3)],seq(61,78)+seq(80,82),m(2128,2133,1)+' M-2134:2 M-2135:1 '+m(2137,2139,1)+' '+m(2140,2142)+' M-2143:1 M-2144:1 M-2145:2 M-2146:2 '+m(2147,2149,4))
patch(221,{5:'MAIN—continued',18:'Roller support angle No. 8.',24:'Splash angle in rear of side door.',29:'Side sloping plate for rear mud chute.',74:'Vertical stiffening angle for bulkhead.',78:'Sliding door for bulkhead (access to engine room).'})
section(223,[(4,7.3)],seq(5,46),'M-2150:2 M-2151:3 '+m(2152,2155)+' M-2156:1 M-2157:2 M-2158:4 M-2159:2 M-2160:4 M-2161:2 M-2162:2 M-2163:4 M-2164:2 M-2165:2 '+m(2166,2168,1)+' M-2169:2 M-2170:1 M-2171:1 '+m(2172,2177)+' M-2178:1 M-2179:1 M-2181:1 M-2185:2 M-2186:6 M-2187:1 M-2188:- M-2189:2 M-2190:1 M-2191:2 M-2192:1 M-2193:1 M-2194:1 M-2195:4')
section(223,[(47,7.3),(48,6)],seq(49,59),'M-2627:11 C138/20384:10 A42/21221:12 C42/21221:12 D42/21221:12 E42/21221:12 F42/21221:24 M-2628:2 M-2629:2 M-2630:11 B42/21221:1')
section(223,[(61,7.3),(62,6)],seq(64,76),' '.join(f'{i}~by~90:{22 if i<=9 or i==14 else 44}' for i in list(range(1,13))+[14]))
patch(223,{39:'',72:'Spring.',73:'½-inch bolts, 1 15/16 inches long, heads 5/16 inch thick',74:'⅜-inch screws, ¾ inch long.',75:'⅜-inch rivets.',76:'Poaking piece for cover plate.'})
section(225,[(5,7.3),(6,6)],seq(7,36),m(1892,1894)+' M-1895:1 M-1896:1 M-1897:2 M-1898:1 M-1899:1 M-1900:1 M-1901:2 M-1902:2 M-1903:1 M-1904:1 M-1905:1 M-1906:2 '+m(1908,1913,1)+' M-1914:2 M-1915:1 M-1916:2 M-1917:2 M-1918:2 M-1919:1 M-1920:1 M-1921:1 M-1922:2')
section(225,[(37,7.3),(38,6)],seq(39,53),'A-20793:4 B-20793:4 C-20793:7 D-20793:4 E-20793:7 F-20793:7 G-20793:14 H-20793:4 J-20793:14 K-20793:4 K1-20793:14 K2-20793:14 L-20793:4 G-20793:28 P-20793:14')
section(225,[(54,7.3)],seq(55,76),'M-2732:2 M-2733:2 M-2734:2 M-2735:1 M-2735:1 M-2737:1 M-2738:2 M-2739:1 M-2740:2 '+m(2741,2750,1)+' H-172/21579:5 J-172/21579:3 C-45/21237:2')
patch(225,{14:'Roof beambat side of removable beam.',50:'⅛-inch jack chain.',63:'Sponson plate (sloping bottom).',71:'Sponson plate side (port side).'})
section(227,[(5,7.3),(6,6)],seq(7,84),'B-45/21237:2 M-2437:4 M-2756:2 M-2757:2 '+m(2758,2768,1)+' M-2769:2 M-2770:2 M-2626:5 M-2626:2 M-2661:7 '+m(2775,2779,1)+' '+m(2780,2786)+' '+m(2787,2789,1)+' '+m(2790,2794)+' M-2795:1 C-42/21221:2 M-2791:1 M-2798:2 '+m(2799,2808,1)+' M-2809:2 M-2810:2 M-2811:2 M-3812:2 M-2813:1 '+m(2814,2817,4)+' M-2818:2 M-2819:2 M-2820:4 M-2821:2 M-2822:2 M-2823:4 M-2824:2 M-2826:4 M-2827:2 M-2828:2 M-2829:4 M-2830:4 M-2831:4 M-2832:2 M-2833:2')
patch(227,{27:'Sponson pressing for roof plate (starboard side).',84:'Sponson shaft for roller.'})
section(229,[(4,7.3),(5,6)],seq(6,20),'M-2834:4 M-2835:4 M-2836:1 M-2837:1 M-2838:1 M-2839:2 M-2840:1 M-2841:1 M-2842:2 M-2843:1 M-2844:1 M-2845:20 M-2126:1 M-2127:1 M-2848:2')
section(229,[(21,7.3)],seq(22,32)+seq(46,94),'M-3117:3 M-3118:3 M-3119:3 M-3120:1 M-3121:6 M-3122:6 M-3123:6 M-3124:24 M-3125:24 M-3126:6 M-3127:9 M-3128:3 M-3130:3 M-3131:3 M-3132:2 M-3133:2 M-3134:10 M-3135:2 '+m(2348,2352,1)+' M-2353:2 M-2354:2 M-2355:1 M-2356:1 M-2357:1 M-2358:2 M-2359:4 M-2360:1 M-2362:1 M-2363:2 M-2364:1 M-2366:2 M-2372:1 M-2373:1 M-2374:4 M-2375:2 M-2376:2 M-2377:2 M-2378:1 M-2379:1 M-2381:1 M-2383:2 M-2384:1 M-2385:4 M-2386:2 M-2387:1 M-2388:1 M-2389:1 M-2390:2 M-2391:2 M-2392:2 M-2393:1 M-2394:2 M-2395:2 M-2396:1 M-2397:1 M-2398:1')
patch(229,{5:'SPONSONS—continued',20:'Ball bearing 40 m. m.; bore, 110 m. m.; O. D., 27 m. m wide.',27:'Trunnion for hemispherical turret.',59:'Main turret side plate junction piece.',60:'Main turret roof doorplate (starboard).',62:'Main turret roof door apron plate.',64:'Main turret roof door (end battons).',68:'Main turret rear peephole splash plate.',69:'Main turret pin for fastener arrangement.'})
section(231,[(5,7.3),(6,6)],seq(7,30),'M-2399:1 M-2400:1 M-2401:1 M-2402:1 M-2403:4 '+m(2404,2408,1)+' M-2409:2 M-2410:2 M-2411:1 M-2414:1 M-2415:2 M-2416:2 M-2417:1 M-2418:2 M-2419:2 M-2420:2 M-2422:4 M-2423:1 M-2425:1 H172—21579:1')
section(231,[(31,7.3)],seq(33,44)+seq(46,69)+[(70,71)]+seq(72,84),'M-2426:1 M-2427:2 M-2428:1 M-2429:1 M-2430:1 M-716:2 M-718:2 M-720:2 M-721:2 M-722:2 P20—21195:2 M-3117:- M-3118:1 M-3119:1 M-3120:1 M-3121:1 M-3122:2 M-3123:2 M-3124:8 M-3125:8 M-3126:2 M-3127:3 M-3128:1 M-3130:1 M-3131:1 A-20793:4 B-20793:4 C-20793:5 D-20793:4 E-20793:5 F-20793:5 G-20793:10 H-20793:4 J-20793:10 K-20793:4 K1-20793:10 K2-20793:5 L-20793:4 O-20793:20 P-20793:10 E43—21220:1 F19—21210:2 M45—21421:1 M-2627:2 C138—20384:3 A42—21221:3 C42—21221:3 D42—21221:3 E42—21221:3 F42—21221:6')
patch(231,{6:'TURRET—HEMISPHERICAL—continued',37:'Driver’s turret flap locking lever pin.',66:'Screw for fastening ring for Hotchkiss gun mounting.',70:'⅛-inch jack chain, 4 inches long each, for Hotchkiss gun mounting.',75:'Driver’s turret rubber washer for periscope.'})
section(233,[(5,7.3)],seq(6,21),'B42—21221:1 J206—21067:3 M-2845:10 '+' '.join(f'{i}~by~90:11' for i in range(1,10))+' M-1789:8 M-1790:8 M-1791:8 M-2432:1')
section(233,[(22,7.3),(23,6)],seq(24,36),'M-2346:2 M-2347:2 M-2361:1 M-2367:2 M-2368:2 M-2369:4 M-2370:2 M-2371:2 M-2409:2 M-2410:2 M-2411:2 M-2845:4 X-90:4')
section(233,[(37,7.3)],seq(38,47),'M-1030:1 M-1050:1 M-564:1 M-1047:1 M-1031:1 M-1045:1 M-1048:1 M-1049:1 M-1045A:1 M-1046:1')
section(233,[(48,7.3)],seq(49,53),'M-1613:1 M-1614:1 M-858:- M-874:- M-1615:2')
section(233,[(54,7.3),(55,6)],seq(56,68),'M-982:1 M-983:1 M-984:1 M-985:1 M-986:1 M-987:39 M-995:2 M-996:2 M-998:2 M-997:66 M-999:4 M-1000:2 M-1005:1')
section(233,[(72,7.3),(73,6)],seq(74,76),'M-988:2 M-989:1 M-990:1')
patch(233,{6:'Revolver port cover swivel pin and nut (right hand).',8:'Peep hole splash plate.',23:'TURRET OUTLOOK',30:'Outlook turret bottom angles (front and rear).',38:'Jockey pulley for large fan.'})
section(235,[(5,7.3),(6,6)],seq(7,16),'M-991:1 M-992:1 M-993:1 M-994:29 M-996:2 M-997:56 M-998:2 M-999:4 M-1000:2 M-1004:2')
section(235,[(42,7.3)],seq(43,65),m(3292,3301,1)+' M-3304:2 M-3305:2 M-3307:1 M-3308:1 M-3309:1 M-3310:4 M-3311:2 -:1 M-3312:1 SH971B+SH971A:2 M-3314:1 M-3315:2 M-3311:1')
section(235,[(66,7.3)],seq(67,73),'SH207A:1 SH207B:1 SH207C:2 SH207D:2 SH207E:1 SH207F:1 SH207G:2')
section(235,[(74,7.3),(75,6)],seq(76,90),'M-1472:2 M-1474:1 M-1479:2 M-1475:2 M-1476:2 M-1473:2 M-1477:2 M-1410:2 M-1471:2 M-1404:2 M-1405X+M-1405Y:6 M-1409:2 M-1483:2 M-1484:2 M-1403:1')
section(235,[(91,7.3),(92,6)],seq(93,96),'M-1401:2 M-1402:1 M-1403:1 M-1404:2')
patch(235,{83:'Plug ⅜ inch'})
section(237,[(5,7.3),(6,6)],seq(7,15),'M-1405:4 M-1406:1 M-1407:1 M-1409:2 M-1410:1 M-1411:2 M-1552:1 20297—D89:1 M-1477:2')
section(237,[(16,7.3),(17,6)],seq(18,22),'M-1261:312 M-1262:312 M-1263:312 M-1264:156 M-1265:312')
section(237,[(23,7.3),(24,6)],seq(25,33),'M-1333:1 M-1335:2 M-1332:2 M-1336:1 M-1334:2 M-1337:1 M-1339:2 M-1410:1 M-1338:2')
section(237,[(34,7.3),(35,6)],seq(36,42),'M-1333:1 M-1335:2 M-1332:2 M-1337:1 M-1339:2 M-1410:1 M-1338:2')
section(237,[(43,7.3),(44,6)],seq(45,56),'M-1541B:1 M-1542:18 M-1543:18 M-1550:18 M-1409:2 M-1544:1 M-1407:1 M-1546:1 M-1552:1 20297—D89:1 M-1549:2 M-1541A:1')
section(237,[(57,7.3),(58,6)],seq(59,65),'M-1333:1 M-1335:2 M-1341:2 M-1337:1 M-1339:2 M-1410:1 M-1338:2')
patch(237,{14:'Key for road track driving wheel shaft .',39:'Road track roller pin.',48:'⅛-inch taper plug for roller pin.',55:'¾-inch taper plug in shaft.'})
section(239,[(5,7.3)],seq(6,15),'M-37:1 M-38:1 M-39:1 M-40:1 M-41:2 M-42:6 M-43:2 M-44:2 M-45:2 M-48:2')
section(239,[(16,7.3)],[(17,18),19]+seq(21,28)+seq(38,52),'SH586A:1 B-5:1 B-94:1 K-67L:1 L-255L:1 L-256:1 D-60N:1 F-3WN:1 B-17-BKN:1 J-3:3 J-4:2 SH386D:1 P-199:1 P-303:1 P-30:1 P-390:2 P-59:1 P-27:1 P-55:1 P-29:1 S-374:1 S-372A:1 S-373:1 S-35:2 S-34:1')
section(239,[(53,7.3)],seq(54,57),'SH80A:1 SH137A:1 SH81A:1 SH137B:1')
section(239,[(58,7.3)],seq(60,67),'M-3917:1 M-3918:1 M-3919:2 M-3920:4 M-3921:8 D14/21202:4 M-3922:1 M-3923:1')
section(239,[(68,7.3)],seq(69,79),m(3883,3893,1))
patch(239,{17:'Distance recorder head assembly—model 26 DLh calibrated 2,500 revs.; 10',19:'Cup.',42:'5 Casing.',55:'Bracket.',76:'Fixing pin for gear pinion.',78:'Yardometer supporting bracket.'})

patch(225,{70:'Sponson plate side (lower port side).',74:'Hotchkiss gun clip.',75:'Hotchkiss gun clip support.'})
for n,sections in SECTIONS.items():
 groups={}
 for w in csv.DictReader((R/f'data/ocr_batch12/p{n}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  if w['level']=='5' and w['text'].strip():groups.setdefault(tuple(w[k] for k in ['block_num','par_num','line_num']),[]).append(w)
 groups=list(groups.values());assert len(groups)==len(L[str(n)])
 x0,slope={221:(546,.009),223:(538,-.001),225:(599,-.014),227:(550,-.010),229:(446,.010),231:(545,-.004),233:(510,-.009),235:(487,-.023),237:(496,.006),239:(485,-.039)}[n]
 def desc_words(i):
  y=L[str(n)][i]['box'][1];threshold=x0+slope*(y-400)
  return [w for w in groups[i] if threshold<=int(w['left'])+100<1540 and w['text'] not in ['|','!']]
 def clean(i,heading=False):
  if i in PATCH.get(n,{}):return PATCH[n][i]
  if heading:return L[str(n)][i]['text'].strip('| ')
  return ' '.join(w['text'] for w in desc_words(i)).strip()
 def baseline(i):
  ww=[w for w in desc_words(i) if 10<=int(w['height'])<=32 and re.fullmatch('[A-Za-z0-9.()—–-]+',w['text']) and not re.search('[gjpqy]',w['text']) and len(w['text'])>1]
  return float(statistics.median(55+int(w['top'])+int(w['height']) for w in ww)) if ww else float(L[str(n)][i]['box'][3]-3)
 out=[]
 for heads,indices,codes in sections:
  hs=[dict(text=clean(i,True),size=size,baseline=baseline(i),source_line_index=i) for i,size in heads]
  lines=[];rr=[]
  for item,(code,qty) in zip(indices,codes):
   ids=list(item) if isinstance(item,tuple) else [item]
   row=dict(part='' if code=='-' else code.replace('~',' '),quantity='' if qty=='-' else qty,source_line_indices=ids,lines=[])
   for i in ids:
    r=dict(text=clean(i),baseline=baseline(i),source_line_index=i,source_box=L[str(n)][i]['box']);lines.append(r);row['lines'].append(r)
    if r['text'] in ['Ditto.','Ditto,','Do.']:r['indent']=10
   rr.append(row)
  yy=np.array([r['baseline'] for r in lines]);d=np.diff(yy);step=float(statistics.median(v for v in d if 17<v<37)) if len(yy)>1 else 25.
  steps=[0]
  for v in d:steps.append(steps[-1]+max(1,round(v/step)))
  step=float(np.clip(np.polyfit(steps,yy,1)[0],22,28)) if len(yy)>1 else step
  origin=float(statistics.median(yy-np.array(steps)*step))
  for j,r in enumerate(lines):r['source_baseline']=r['baseline'];r['baseline']=round(origin+steps[j]*step,3)
  # Two pairs of printed part numbers share one quantity and description.
  # Restore half-line spacing at these braces; ordinary rows keep the source grid.
  for row in rr:
   if '+' in row['part']:
    row['part_group_codes']=row['part'].split('+');row['part']='';row['group_half_span_px']=12.5
  out.append(dict(headings=hs,rows=rr))
 ti=1 if n in [225,227,233,239] else 0
 TABLES[str(n)]=dict(title=clean(ti,True),title_baseline=baseline(ti),sections=out)

# The OCR recognizes only the stray ink in this intentionally blank row.
rows=TABLES['223']['sections'][0]['rows'];j=next(i for i,r in enumerate(rows) if r['source_line_indices']==[39]);rows[j]['lines'][0]['baseline']=(rows[j-1]['lines'][0]['baseline']+rows[j+1]['lines'][0]['baseline'])/2
# Preserve the half-line centering of printed grouped part numbers, without rounding
# the 1.5-line gaps to two lines and stretching the surrounding lists.
for sec in TABLES['235']['sections']:
 if any(r.get('part_group_codes') for r in sec['rows']):
  for r in sec['rows']:
   for l in r['lines']:l['baseline']=l['source_baseline']
for name,obj in [('body_batch12.json',BODY),('tables_batch12.json',TABLES)]:
 (R/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(R/'data/batch12_table_transcription.tsv').write_text('page\tpart_number\tquantity\tdescription\n'+''.join(f'{n}\t'+(' + '.join(r['part_group_codes']) if r.get('part_group_codes') else r['part'])+f'\t{r["quantity"]}\t'+ ' / '.join(l['text'] for l in r['lines'])+'\n' for n,t in TABLES.items() for sec in t['sections'] for r in sec['rows']))
print('Table rows:',sum(len(s['rows']) for t in TABLES.values() for s in t['sections']))
