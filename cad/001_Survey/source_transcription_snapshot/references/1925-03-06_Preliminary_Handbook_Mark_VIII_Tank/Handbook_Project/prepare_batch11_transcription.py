#!/usr/bin/env python3
"""Source-checked native parts lists, printed pages 201–220."""
from pathlib import Path
import json,csv,re,statistics
import numpy as np
R=Path(__file__).resolve().parent
L=json.loads((R/'data/batch11_source_ocr_lines.json').read_text())
BODY={}
TABLES={};PATCH={};SECTIONS={}
def patch(n,changes):PATCH.setdefault(n,{}).update(changes)
def section(n,heads,indices,codes):
 """One source section, wrapped description lines grouped in a tuple."""
 parts=[v.rsplit(':',1) for v in codes.split()]
 assert len(indices)==len(parts),(n,heads,len(indices),len(parts))
 SECTIONS.setdefault(n,[]).append((heads,indices,parts))
def seq(a,z):return list(range(a,z+1))

section(201,[(27,7.3),(28,6.0)],seq(29,44),'8408:1 12868:1 8245:1 -:1 12945:1 12819:2 13181:2 12999:1 12825:1 12935:2 12748:6 12821:6 12892:2 12890:1 12826:1 12885:3')
section(201,[(46,7.3),(47,6.0)],seq(48,55),'12701:3 12820:6 12788:6 12772:16 12641:16 12790:8 12736:1 12737:1')
section(201,[(57,7.3),(58,6.0)],seq(59,61),'SH868A:1 SH136B:1 SH64JH:2')
section(201,[(62,7.3),(63,6.0)],seq(64,82)+[86,(110,87)],'8210:1 8146:1 8501:1 8060:1 8524:1 8544:x 8154:1 8149:1 8080:1 8150:1 8148:1 8060:1 8147:1 8209:1 8074:1 8151:1 173:1 160:4 8511:x 8347:1 214:1')
section(201,[(88,7.3),(89,6.0)],seq(90,107),'SH144B:1 SH141A:1 SH145A:1 SH143A:1 SH143B:1 SH143C:1 SH143D:1 SH142A:1 SH142B:1 SH142C:1 SH142D:1 SH142E:1 SH142F:1 SH142G:2 SH142H:1 SH44C:1 SH193A:1 SH144A:1')
patch(201,{27:'ENGINE—Continued',28:'ELECTRICAL EQUIPMENT—continued',80:'Generator driving-shaft cotter (⅛ inch by 1⅜ inches).',81:'Generator driving-gear key (3/16 inch by ⅛ inch by 1 3/16 inches).',110:'Generator driving-shaft ball-bearing (upper) retainer screw (¼ by 20 by ¾-'})
section(203,[(16,7.3),(17,6.0)],seq(18,33)+[(34,35)]+seq(36,40),'8200:1 8190:1 161:1 8420:2 207:2 8185:1 8186:1 8178:1 8138:1 8383:1 8179:1 8177:2 8187:1 8189:1 8221:2 8201:1 118:4 111:8 101:4 106:4 8184:1 8368:1')
section(203,[(41,7.3),(42,6.0)],seq(43,51)+[(52,53),54,55,(56,57)]+seq(58,62),'8384:1 8191:1 8192:1 177:1 8220:1 8203:1 8466:1 8465:1 8381:1 8133:1 158:1 8382:1 116:10 111:20 101:10 106:10 8531:1 8534:1')
section(203,[(63,7.3),(64,6.0)],seq(65,75),'8533:1 8532:1 8535:1 8536:1 174:1 8461:2 8463:1 8236:1 131:2 101:2 106:2')
section(203,[(76,7.3),(77,6.0)],seq(78,82),'13149:12 13138:12 8057:12 8055:24 12547:24')
patch(203,{20:'Oil-pump body (lower half) plug (⅛-inch pipe).',22:'Oil-pump tube connection gasket (⅞-inch annular).',24:'Oil-pump (lower) driving gear.',34:'Oil-pump body bolt (¼ inch—28 by 1 5/16 inches, standard) (⅞ inch between',36:'Oil-pump body bolt washer (¼ inch).',37:'Oil-pump body bolt nut (¼ inch—28 std.).',38:'Oil-pump body bolt cotter (1/16 by ½ inches).',45:'Oil-pump pressure relief valve.',52:'Oil-pump body (lower half) cover drain plug (plug ⅝ inch—18 thd., hex.',54:'Oil-pump body (lower) half cover drain plug gasket (⅝ inch annular).',56:'Oil-pump body (lower) half cover bolt (¼ inch—28 by 15/16 inch) (½ inch',58:'Oil-pump body (lower) half cover bolt washer (¼ inch).',59:'Oil-pump body (lower) half cover bolt nut (¼ inch—28 thd. std.).',60:'Oil-pump body (lower) half cover bolt cotter (1/16 inch by ½ inch).',69:'Oil-pump screen (upper) dowel.',70:'Crank case to cam-shaft oil-tube assembly (3/16 inch by ⅜ inch).',73:'Stud (¼ inch—28 by 1¼ inches std.).',74:'Nut (¼ inch—28 std.).',75:'Cotter (1/16 inch by ½ inch).'})
section(205,[(37,7.3),(38,6.0)],seq(39,50),'M-178:1 M-179:1 M-180:1 M-181:1 M-182:1 M-183:1 M-184:1 M-185:1 M-186:1 M-187:1 M-188:2 M-189:1')
section(205,[(51,7.3),(52,6.0)],seq(53,65),'988A:1 988B:1 988C:1 988D:1 -:1 -:1 989A:1 990A:1 990B:1 990C:1 990C:1 -:4 -:4')
section(205,[(66,7.3)],seq(67,112),'M-246:1 M-247:1 M-248:1 M-249:2 M-250:1 M-251:1 M-252:1 M-253:1 M-254:1 M-255:1 M-256:2 M-257:1 M-258:2 M-259:2 M-260:2 M-261:2 M-262:2 M-263:1 M-264:1 M-265:2 M-266:2 M-267:2 M-268:2 M-269:2 M-270:6 M-271:6 M-272:6 M-273:2 M-274:6 M-275:2 M-276:2 M-277:2 M-278:2 M-279:2 M-280:6 M-281:2 M-282:6 M-283:6 M-284:6 M-285:2 M-286:2 M-287:2 M-288:2 M-289:2 M-290:6 M-291:2')
patch(205,{41:'Transverse channel (back).',57:'½ by ⅝ headless set screw for ratchet.',58:'5/16 by 3⅜ pin for collar.',64:'½ by 1½ bolt with nuts for flange.',65:'½ lock washers.',96:'Epicyclic spur rings (small).'})
section(207,[(24,7.3)],seq(25,43)+seq(11,20)+seq(67,107)+[(108,109),(110,111)]+seq(112,114),'M-292:2 M-293:2 M-294:2 M-295:4 M-296:2 M-297:2 M-298:2 M-299:2 M-300:8 M-301:1 M-302:1 M-303:1 M-304:1 M-305:1 M-306:2 M-307:1 M-308:1 M-309:1 M-310:2 M-311:3 M-313:6 M-314:7 M-315:4 M-316:3 M-317:6 M-318:6 M-326:2 M-328:1 M-330:4 M-331:4 M-332:4 M-335:4 M-335:4 M-336:8 M-337:4 MX:- M-338:4 M-339:2 M-340:2 M-341:2 M-342:2 M-343:4 M-344:4 M-346:12 M-348:2 M-349:4 M-351:12 M-352:1 M-353:2 M-355:2 M-356:4 M-357:2 M-358:2 M-359:2 M-360:2 M-361:2 M-362:2 M-363:2 M-364:6 M-365:2 M-366:2 M-367:2 M-369:2 M-372:1 M-373:1 M-374:1 M-375:1 M-376:1 M-377:1 M-378:2 M-380:2 M-382:2 M-383:2 M-384:2 M-385:2')
patch(207,{43:'Oil-retaining washer for bushing.',15:'Joint ring for oil-filling cup.',39:'Vertical shaft bearings for reversing gear.',108:'Top gusset left inner diaphragm.',109:'Bottom guset right inner diaphragm.',110:'Top gusset right inner diaphragm.'})
section(209,[(4,7.3)],seq(5,21),'M-386:8 M-387:4 M-388:2 M-389:2 M-390:2 M-391:2 M-392:2 M-393:2 M-394:4 M-395:2 M-396:2 M-397:4 M-398:2 M-399:2 M-400:6 M-401:2 MX:-')
section(209,[(22,7.3)],seq(23,52),'SH140C:1 SH140E:1 SH140D:1 SH140F:1 SH158D:4 SH139D:6 M-3713:2 M-3716:2 M-3714:2 SH158D:12 SH403C:2 SH402F:2 SH402Q:4 SH403A:2 SH403B:2 SH401A:2 SH402A:2 SH403B:2 SH402C:2 SH402D:2 SH402E:2 M-48:2 SH402G:2 SH402H:2 SH403A:2 SH403B:2 SH403C:2 SH599A:2 SH158A:2 SH158B:12')
section(209,[(54,7.3),(55,6.0)],seq(56,76),'M-1123:1 M-1124:1 M-1125:2 M-1126:1 M-1127:1 M-1128:1 M-1129:1 SH193C:1 M-1131:1 M-1132:1 B-113—21153:1 M-1133:4 M-1134:1 M-1135:2 SH146A:1 SH146B:2 SH194A:1 SH194B:2 SH196A:2 SH196B:2 SH196C:2')
patch(209,{7:'Holding bolts “A” epicyclic gear frame.',8:'Screws “B” epicyclic gear frame.',9:'Screws “C” epicyclic gear frame.',11:'Sprocket bearing brass (inside).',21:'MX numbers not noted.',28:'3/32 by 1⅛ inch taper pin.',40:'Cut-out lever.',51:'Filler plate for exhaust hole in floor plate.',67:'Timken roller bearing 316–312.',69:'Whittle belt.',75:'⅝-inch nut.'})
section(211,[(5,7.3),(6,6.0)],seq(7,28),'M-1030:1 M-1031:1 M-1032:1 M-1033:1 M-1034:1 M-1035:1 M-1036:1 M-1037:1 M-1038:1 M-1039:1 M-1040:1 M-1041:1 M-1042:1 M-1045:2 M-1046:1 M-1047:1 M-1048:1 M-1049:1 M-1050:1 M-1062:1 A-113—21153:1 M-564:1')
section(211,[(29,7.3),(31,6.0)],seq(35,52),'SH957A:1 SH958A:1 SH958B:1 SH958C:1 SH958D:1 SH958E:2 SH958F:2 SH958G:1 SH958H:4 SH959A:1 SH959B:1 SH959C:1 SH959D:1 SH959E:3 SH960A:1 SH960B:1 SH961A:1 M-1054:1')
section(211,[(54,7.3),(55,6.0)],seq(56,66),'SH900A:2 SH900B:1 SH900C:4 SH900D:1 SH901A:4 SH901B:4 SH901C:2 SH901D:4 SH901E:4 SH901F:1 SH903A:1')
section(211,[(68,6.0)],[69,71,72,73,75,(77,78,79),80,81,(82,83,84)],'SH981A:1 SH981B:1 SH981C:1 SH981D:1 SH981E:1 SH981F:1 SH981G:2 SH981H:- SH982A:1')
patch(211,{8:'Arm for jockey pulley.',26:'Journal bearing ¾-inch bore, 2-inch O. D., 11/16 inch wide.',42:'Inlet stud.',69:'Air tube 33¼ long',71:'Air tube 25 long',72:'Air tube 10⅜ inches long',73:'Air tube 26 inches long',75:'Air tube 25 inches long',77:'Air tube 29¾ long—armored flexible brass tubing—¼ inside diameter—Union',78:'and ¼-inch male pipe adapter one end—Union—elbow and ⅛-inch male',80:'Air tube 26 long',81:'Air tube 31¼ long',82:'Air tube 88 long—armored flexible brass tubing ¼ inside diameter—Union',83:'and ¼ male pipe adapter one end—Union—elbow and ⅛-inch male pipe'})
section(213,[(4,7.3),(5,6.0)],[tuple(seq(6,13)),14,15,(16,17,18),tuple(seq(19,27)),tuple(seq(28,33)),tuple(seq(34,36))]+seq(37,47),'SH982B:3 SH982C:3 SH982D:1 SH982E:- 982F:1 982G:1 982H:1 SH980A:1 SH980B:1 SH980C:3 -:9 SH980C:2 -:4 -:- SH985C:2 SH985D:1 SH985E:1 SH985B:1')
section(213,[(48,7.3),(49,6.0)],seq(50,58),'SH950A:1 SH950B:1 SH950C:1 SH950D:1 SH950E:1 SH950F:1 SH950G:1 SH972A:2 SH950H:1')
section(213,[(59,6.0)],seq(60,70),'SH984A:1 SH984B:1 SH984C:1 SH984D:1 SH894E:1 SH985B:2 SH985C:2 SH985D:1 SH985G:1 SH985A:1 SH985F:-')
section(213,[(71,6.0)],seq(72,77),'M-1755:3 M-1757:3 M-1758:3 SH951B:3 M-1761:3 SH951C:1')
patch(213,{4:'GASOLINE (PETROL)—Continued',6:'Air tube, copper tubing ¼ outside diameter.',8:'1, ¼ brazing union, brazing both ends.',9:'1, ¼ brazing union, ⅛ male pipe thread one end.',10:'1, ¼ by ⅛ pipe bushing mall iron.',11:'1, ¼ mall iron tee.',12:'1, ¼ W. I. pipe nipple 1¼ long.',13:'1, ¼ brass vertical ball check valve.',14:'Air tube A=12½',15:'Air tube A=16',16:'Air tube A=19½',17:'1 brazing union tee, ⅛ male pipe thread each side.',18:'1, ¼ by ⅛ reducing elbow.',19:'Air tube, copper tubing ¼ inch outside diameter. Following parts fastened',23:'1, ⅛ by ¼ bushing mall iron.',24:'1, ¼ cross.',25:'1, ¼ air cock brass.',26:'1, ¼ close nipple.',27:'1, ¼ brass horizontal check valve.',28:'Air tube—copper tubing ¼ in. outside dia. Fastened in tube are following',32:'1 brazing union, ⅛-inch male pipe thd. one end.',33:'1 ¼ by ⅛ reducer.',34:'Air tube—copper tubing ¼ in. outside dia. Fastened to tube are:',35:'1 brazing union—⅛-inch male pipe thd. one end.',36:'1 ¼ by ⅛ reducing elbow.',40:'No. 4 by ¾ round head brass wood screws.',42:'⅜ by 1 bolts gauge boards with nuts.',43:'¼ by ⅝ bolts gauge pump.',44:'½ mal. iron elbows.',45:'½-inch w. i. pipe nipple, 2 inches long.',46:'½-inch w. i. pipe nipple, 3¼ inches long.',47:'½ street elbow.',57:'Regulating tank support.',66:'5 m. i. elbow.',70:'Subassembly-connecting-req. tank to flexible tubing.'})
section(215,[(42,7.3),(43,6.0)],seq(44,71),'SH951E:1 M-1765:3 C-153—21256:3 B-153—21256:3 D-153—21256:3 E-152—21256:3 M-1785:1 M-1786:1 M-1787:1 M-1788:1 M-1789:4 M-1790:4 M-1791:4 J-206—21067:2 M-1794:2 M-716:2 M-1756:3 M-1766:3 SH951F:3 SH951G:3 SH951A:3 M-718:2 M-720:2 M-722:2 M-1793:2 H-20—21195:3 M-1756:3 M-1766:3')
section(215,[(72,7.3)],seq(73,94),'M-3777:1 M-3778:1 M-3779:2 M-3780:2 M-3781:2 M-3782:2 M-3783:2 M-3784:2 M-3785:2 M-3786:2 M-3789:2 M-3788:2 M-3790:2 M-3791:2 M-3792:1 M-3793:1 M-3794:2 M-3795:2 M-3796:2 M-3797:2 M-3798:4 M-3799:2')
section(215,[(95,7.3)],seq(96,109),'M-3800:1 M-3803:2 M-3804:2 M-3805:2 M-3806:2 M-3024:6 M-3025:6 M-3023:6 Q-38—21192:6 M-3020:6 C-37—21191:26 M-3817:26 A-37—21192:24 B-37—21191:24')
section(215,[(110,7.3),(111,6.0)],seq(112,114),'M-702:1 M-703:1 M-704:1')
patch(215,{64:'Thackeray “washer” for tap plugs.',113:'Side door (upper part) starboard side.',114:'Side door (lower part), port side.'})
section(217,[(52,7.3),(53,6.0)],seq(54,74),'M-705:1 M-706:8 M-707:4 M-708:4 M-709:4 M-710:2 M-711:2 M-712:2 M-713:1 M-714:1 M-715:2 M-716:2 M-717:2 M-718:2 M-719:2 M-720:2 M-721:4 M-722:4 M-20—21195:4 M-3120:2 M-2431:4')
section(217,[(75,6.0)],seq(76,98),'M-1927:1 M-1928:1 M-1929:1 M-1930:1 M-1931:1 M-1932:1 M-1933:1 M-1934:1 M-1935:1 M-1936:1 M-1937:1 M-1938:1 M-1939:1 M-1940:1 M-1941:1 M-1942:2 M-1943:1 M-1944:2 M-1945:2 M-1946:2 M-1947:2 M-1948:1 M-1949:1')
section(217,[(100,6.0)],seq(101,128),'M-1961:2 M-1962:2 M-1963:2 M-1964:2 M-1965:2 M-1966:2 M-1967:2 M-1968:2 M-1969:2 M-1970:2 M-1971:2 M-1972:2 M-1973:1 M-1974:1 M-1975:2 M-1976:2 M-1977:2 M-1978:2 M-1979:2 M-1980:2 M-1981:2 M-1982:2 M-1983:2 M-1984:2 M-1985:2 M-1986:2 M-1987:2 M-1988:2')
patch(217,{53:'DOOR—SIDE—continued',67:'Packing piece for side door lock (starboard).',72:'Handle for side door lock.',80:'Floor plate No. 1.',81:'Floor plate No. 2.',82:'Floor plate No. 3.',83:'Floor plate No. 4.',84:'Floor plate No. 5.',85:'Floor plate No. 6.',86:'Floor plate No. 7.',120:'Butt strap under sponson (front)'})
section(219,[(4,7.3),(5,6.0)],[6,7,8,9]+seq(27,100),'M-1989:2 M-1990:2 M-1991:1 M-1992:2 M-1993:2 M-1994:2 M-1995:2 M-1998:4 M-1999:4 M-2000:2 M-2001:2 M-2002:2 M-2003:1 M-2004:4 M-2005:4 M-2006:2 M-2007:2 M-2008:2 M-2009:4 M-2010:4 M-2011:4 M-2012:4 M-2013:4 M-2014:1 M-2015:2 M-2016:2 M-2017:2 M-2018:2 M-2019:2 M-2020:2 M-2021:1 M-2022:2 M-2023:2 M-2024:1 M-2025:1 M-2026:2 M-2027:2 M-2028:2 M-2029:1 M-2030:2 M-2031:2 M-2032:2 M-2033:1 M-2034:3 M-2035:2 M-2036:2 M-2037:4 M-2038:2 M-2039:4 M-2040:2 M-2041:1 M-2042:1 M-2043:1 M-2044:2 M-2045:2 M-2046:1 M-2047:1 M-2048:2 M-2049:2 M-2055:2 M-2056:2 M-2057:4 M-2058:2 M-2059:2 M-2060:2 M-2061:4 M-2062:2 M-2063:2 M-2064:2 M-2065:2 M-2066:4 M-2067:2 M-2068:1 M-2069:2 M-2070:1 M-2071:2 M-2072:3 M-2073:1')
patch(219,{6:'Front mud chute (back plate).',7:'Side plate (No. 3 engine room).',8:'Removable plate for engine room.',9:'Side plates, top of sponson.',38:'Exterior longitudinal butt strap.',79:'Vertical beam shaft sponson (starboard).'})

def clean(n,i):
 if i in PATCH.get(n,{}):return PATCH[n][i]
 t=L[str(n)][i]['text']
 if '|' in t:t=t.rsplit('|',1)[-1]
 return t.strip()

for n,sections in SECTIONS.items():
 groups={}
 for w in csv.DictReader((R/f'data/ocr_batch11/p{n}.tsv').open(),delimiter='\t',quoting=csv.QUOTE_NONE):
  if w['level']=='5' and w['text'].strip():groups.setdefault(tuple(w[k] for k in ['block_num','par_num','line_num']),[]).append(w)
 groups=list(groups.values());assert len(groups)==len(L[str(n)])
 desc_min={201:515,203:515,205:540,207:550,209:550,211:490,213:530,215:560,217:560,219:570}[n]
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
  out.append(dict(headings=hs,rows=rr))
 title=clean(n,1 if n in [205,211] else 0)
 TABLES[str(n)]=dict(title=title,title_baseline=baseline(1 if n in [205,211] else 0),sections=out)

from batch11_special_tables import customize
customize(TABLES)

for name,obj in [('body_batch11.json',BODY),('tables_batch11.json',TABLES),('batch11_source_ocr_lines.json',L)]:
 (R/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
(R/'data/batch11_body_transcription.txt').write_text('\n\n'.join(f'PRINTED PAGE {n}\n'+'\n'.join(r['text'] for r in rr) for n,rr in BODY.items())+'\n')
(R/'data/batch11_table_transcription.tsv').write_text('page\tpart_number\tquantity\tdescription\n'+''.join(f'{n}\t{r["part"]}\t{r["quantity"]}\t'+ ' / '.join(l['text'] for l in r['lines'])+'\n' for n,t in TABLES.items() for sec in t['sections'] for r in sec['rows']))
print('Body lines:',sum(map(len,BODY.values())),'table rows:',sum(len(s['rows']) for t in TABLES.values() for s in t['sections']))

(R/'data/batch11_shared_descriptions.txt').write_text('\n\n'.join(f'PRINTED PAGE {n}, SHARED BLOCK {j+1}\n'+'\n'.join(block['lines']) for n,t in TABLES.items() for j,block in enumerate(t.get('shared_blocks',[])))+'\n')
