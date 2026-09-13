"""Reviewed scan-to-native transcription for source leaves 61–80.
Explicit corrections are auditable against retained OCR and original JP2s.
Braced fractions are typeset with native numerators, rules and denominators.
"""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[1]
ocr={p['leaf']:p['lines'] for p in json.loads((R/'data/batch04_ocr_draft.json').read_text())}
fix={
61:{13:'descending from 20,000 feet to 15,000 feet; otherwise,'},
63:{4:'battery-coil ignition, designed as an integral part of the',6:'cylinders being 45°, it is not possible to use a conven-',8:'schemes for the use of magnetos were considered, the',9:'present arrangement was finally adopted as providing the',14:'plied by the generator or battery to two complete ignition',20:'tion coil in which high tension current is induced at the',21:'moment of “break,” and a distributor which passes the',26:'this portion of the system goes, there is absolute dupli-',30:'running with only one unit switched on, by the battery.',36:'run the ignition service, but the engine cannot then be',41:'15 amperes at 10 volts, the normal output being consider-',42:'ably lower, or about 5 amperes. In constructional',44:'yoke A is held between cast aluminium end shields or'},
65:{5:'with three lugs by which the generator is studded down',6:'to the crankcase between the cylinders, and is extended',10:'end of the latter being splined to fit a corresponding',14:'generator, but care should be taken to see that the splined',19:'conductors being double-cotton-covered copper, with 20',21:'and is 1{1/4} in. in diameter. The four field coils each con-',23:'resistance being approximately {3/4} ohm per coil at 60° F.',33:'from 1 to 1{1/4} lb. per brush. The brush gear is',35:'which the two cable terminal studs project: one of these,',37:'“GEN. ARM”; the other, H, takes the field current,',38:'and is marked “GEN. FIELD.” The end of the cover',41:'stud ends, instead of a complete lining.',42:'Practically the only attention required by the genera-',47:'carefully looked over, and any necessary adjustments',48:'made; the windings should be well dusted by the use of',50:'repacked with grease. The commutator must be watched'},
66:{3:'copper bars tend to stand proud of the surface, it should',6:'hacksaw blade. The commutator and brushes should',10:'the commutator, so as to bring them to the proper',13:'lifted well clear of the commutator.',16:'and so on; such work is for experts at base depôts only.',19:'No provision is made in the generator itself to effect',22:'device is employed to regulate the voltage, and conse-',25:'the field and keeping the voltage down to the desired'},
67:{2:'aluminium cup A, which normally is fixed behind the',3:'switchboard. It consists of a soft iron core wound with',5:'core due to the flow of current in these windings serving',6:'to pull down an “armature” blade B, and so break the',7:'direct path to earth for the field current. When the',9:'that to which the regulator is set—say 10 volts, the pair',10:'of contacts C are closed, and the field current can pass to',12:'pull of the core opposes, and eventually overcomes that',16:'of 115 ohms resistance, and the other—wound non-induc-',22:'Adjustment of the regulator to maintain any line',29:'from .005 to .007 in. when the armature blade B is pulled',30:'down upon the stop pin; the pin projects from .043 to',35:'the armature blade is in a state of continual movement,',37:'of a trembler coil or a bell. The adjustable contact screw',44:'As the regulator is very inaccessible when fitted',46:'the wood board on which the two are mounted, as indi-'},
69:{3:'switchboard are delivered assembled on a piece of {3/8} in.',7:'washers C provided are to be fitted as indicated, the lugs',23:'to connect the generator to the battery for charging;',25:'when both switches are in the “on” position together.'},
70:{7:'switches be put to “on” before the engine has run up to',15:'charging can commence. Therefore, after starting the',23:'sary to warm the engine up sufficiently to work it up to',24:'a higher speed. It is of the utmost importance, however,',31:'sist of four-armed spiders riding over metal contact',38:'tance of the ignition coils is very low—about {1/2} ohm—the',39:'current would be very high without these 1 ohm steadying',44:'completed the ammeter will read about 5 amperes,'},
71:{31:'box, measuring approximately 5{1/2} in. long by 3{3/4} in. wide',32:'by 6{3/4} in. high to top of terminals. The battery is of the',33:'so-called “unspillable” type, but is not absolutely so: it'},
73:{2:'batteries are as follows:—',9:'57) with electrolyte taken from the glass bottle',25:'(7) Allow the battery to stand for fifteen minutes;',29:'Fig. 58).',36:'the baffle plate “E,” as shown in cross section of',39:'water down to plate “E” with hydrometer syringe,',43:'following manner:—',44:'(1) Battery should be flushed, as described above.',46:'should be put on charge at 1 ampere, and charged'},
75:{4:'during this charge.) The battery should then be',31:'between 1.290 and 1.310. If gravity is not correct',34:'allowed to run into a rubber or glass jar. The elec-',39:'plate “E,” as shown in Fig. 57. Battery should then',42:'moved to top of plate “E” with hydrometer syringe,'},
77:{25:'back of switchboard marked “POS. BATT.”, and nega-',29:'special cab-tyre sheathed cable of 6 mm, diameter will',31:'being used also for the lead which connects the three',32:'terminals marked “GEN. ARM.” on the generator,'},
78:{6:'several figures.',9:'base A of the contact breaker shown in detail in Fig. 61.',18:'with four studs C which pass through slotted holes in'},
}
pages={n:dict(leaf=n,printed_page=n-2,folio_baseline=y,blocks=[],headings=[],captions=[],legends=[],tables=[],subheads=[],vertical=[]) for n,y in zip(range(61,81),[296,273,291,273,359,333,324,305,329,328,205,247,199,178,266,244,255,281,277,289])}
def block(n,a,b,y,first=108,cont=0,step=54):
 lines=[dict(text=fix.get(n,{}).get(i,ocr[n][i]['text']),indent=first if i==a else cont,source_ocr_index=i) for i in range(a,b+1)]
 pages[n]['blocks'].append(dict(y=y,step=step,lines=lines))
for args in [
(61,1,5,403),(61,6,15,673),(62,3,6,1629),
(63,3,10,618),(63,11,22,1050),(63,23,28,1698),(63,29,37,2023),(63,39,47,2615),
(65,2,17,468,0),(65,18,23,1326),(65,24,41,1648),(65,42,51,2631),
(66,1,13,443,0),(66,14,16,1185),(66,19,26,2688),
(67,1,21,445),(67,22,39,1596),(67,40,43,2595),(67,44,48,2844),
(69,1,9,439,0),(69,17,28,2455),
(70,1,29,448),(70,30,48,2032),(70,49,49,3061),
(71,1,14,313,0),(71,29,37,2500),(72,1,11,358,0),
(73,1,2,301),(73,6,6,679,216,108),(73,7,10,732,216,108),(73,11,16,948,216,108),(73,17,17,1274,216,108),(73,19,19,1383,216,108),(73,20,24,1436,216,108),(73,25,29,1707,216,108),(73,33,40,2225,216,108),(73,42,43,2712,216,108),(73,44,44,2820,216,108),(73,45,46,2874,216,108),
(75,1,8,373,108,108),(75,30,43,2049,216,108),(75,45,46,2932),
(77,1,3,363,0),(77,4,8,526),(77,24,33,2482,0),
(78,2,6,498),(78,7,9,768),(78,13,21,2579,0),
(79,1,3,372,0),(79,7,13,1669,0),(79,16,16,2824,0),(79,17,19,2878),
(80,1,7,401,0),(80,11,18,2234,0),(80,19,25,2678)]:block(*args)
heads={63:[[454,'CHAPTER IV.',12],[535,'IGNITION.',14,'Sans'],[2539,'THE GENERATOR.']],66:[[2571,'THE VOLTAGE REGULATOR.']],69:[[2347,'THE SWITCHBOARD.']],71:[[2403,'THE BATTERY.']],73:[[476,'INSTRUCTIONS FOR PREPARING BATTERY'],[528,'FOR SERVICE.'],[2037,'INSTRUCTIONS FOR MAINTENANCE IN'],[2090,'SERVICE.']],75:[[2851,'FITTING THE BATTERY.']],78:[[378,'THE IGNITION UNITS.']]}
for n,v in heads.items():pages[n]['headings']=v
caps={
61:[[2733,'Fig. 49.'],[2806,'Diagram illustrating three positions of H.C. 7'],[2860,'Altitude Control Cock.']],
62:[[1361,'Fig. 50.'],[1449,'Photograph of H.C. 7 Altitude Control Cock.']],
64:[[2970,'Fig. 51.'],[3024,'The Generator.']],
66:[[2335,'Fig. 52.'],[2410,'Voltage Regulator.']],
69:[[1829,'Fig. 55'],[1902,'Mounting of Switchboard and Voltage Regulator.']],
71:[[2232,'Fig. 56.'],[2303,'Section through End Cell of a Willard Battery.']],
72:[[2854,'Fig. 57.'],[2924,'Measuring the Depth of Electrolyte above the'],[2978,'Baffle Plate.']],
74:[[2795,'Fig. 58.'],[2921,'Removing Surplus Electrolyte.']],
75:[[1890,'Fig. 59.'],[1966,'Taking the Gravity of Electrolyte.']],
76:[[2734,'Fig. 60.'],[2839,'An Ignition Unit.'],[2927,'(Distributor head and cables removed to expose the'],[2981,'contact breakers, condenser, and H.T. rotor.)']],
77:[[2234,'Fig. 61.'],[2294,'The Contact Breaker'],[2375,'(showing H.T. Rotor).']],
78:[[2337,'Fig. 62.'],[2414,'Contact Breaker Base Plate'],[2483,'(back view).']],
79:[[1428,'Fig. 63.'],[1498,'Attachment of Contact Breaker Base (B)'],[1551,'to Main Flange (A).'],[2644,'Fig. 64.'],[2714,'The Cam and Cam Spindle.']],
80:[[2002,'Fig. 65.'],[2071,'Cam Spindle Drive'],[2126,'(early pattern).']]}
for n,v in caps.items():pages[n]['captions']=v
pages[61]['legends']=[dict(x=90,y=2917,step=54,size=10.8,width=290,lines=['Top: Suction holes shut.','Centre: Suction holes just opening.','Bottom: Suction holes at maximum opening.'])]
pages[69]['legends']=[dict(x=70,y=2026,step=54,size=10.8,width=290,lines=['A—Cut hole in wood as shown by dotted line.','B—Two bolt holes, {7/32} in. diameter.','C—When permanently fixed, bend up one ear of','    tab-washer against nut.'])]
pages[73]['subheads']=[[98,608,'Filling.'],[91,1326,'First Charge.—'],[91,2174,'Flushing.—'],[91,2658,'Charging and Adjusting Gravity.—']]
v=pages[68]['vertical']
for x,y,w,t in [(324,633,209,'Fig. 53'),(336,633,209,'Front of Switchboard.'),(324,357,246,'Fig. 54.'),(336,357,246,'Back of Switchboard.')]:v.append(dict(x=x,y=y,width=w,text=t,align=1))
for j,t in enumerate(['A—To positive terminal battery (use heavy cable).','C—To right-hand ignition unit.','D—To left-hand ignition unit.']):v.append(dict(x=347+j*11.3,y=651,width=281,text=t,align=0))
for j,t in enumerate(['B—To terminal marked “GEN. ARM.” on voltage','    regulator, and thence to generator (use heavy','    cable).']):v.append(dict(x=347+j*11.3,y=346,width=295,text=t,align=0))
data=dict(batch=4,source_scans=[61,80],proofread_against='All twenty staged source scans, full-page views, sideways reading view and fractional/type details.',pages=list(pages.values()))
(R/'data/batch04_transcription.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
alltext=json.loads((R/'data/baseline_v03_transcription.json').read_text());alltext['pages']+=data['pages']
(R/'data/transcription.json').write_text(json.dumps(alltext,ensure_ascii=False,indent=2))
changes=[dict(leaf=n,source_ocr_index=i,ocr=ocr[n][i]['text'],corrected=t) for n,vals in fix.items() for i,t in vals.items()]
(R/'data/batch04_corrections.json').write_text(json.dumps(dict(corrections=changes,retained_source_anomalies=[dict(leaf=61,text='e.g.. after'),dict(leaf=66,text='interefered with.'),dict(leaf=67,text='so at to permit of'),dict(leaf=71,text='battery. of Willard'),dict(leaf=77,text='6 mm, diameter')],notes=['Fractions visually checked against source; native stacked fraction syntax is editorial encoding only.','110/36 and 64/33 are retained as printed conductor designations, with baseline slashes.','Technical illustrations retain printed orientation, including sideways figures 53–54.']),ensure_ascii=False,indent=2))
if json.loads((R/'data/release.json').read_text())['release_id'].startswith('v03'):
 rid='v04_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 release=dict(release_id=rid,sla=f'Liberty_Master_scans0001-0080_{rid}.sla',pdf=f'Liberty_Master_scans0001-0080_{rid}.pdf',comparison=f'Liberty_Comparison_scans0061-0080_{rid}.pdf',package=f'Liberty_Project_scans0001-0080_{rid}.zip')
 (R/'data/release.json').write_text(json.dumps(release,indent=2))
print('Authored',len(pages),'pages;',len(changes),'explicit OCR corrections.')
