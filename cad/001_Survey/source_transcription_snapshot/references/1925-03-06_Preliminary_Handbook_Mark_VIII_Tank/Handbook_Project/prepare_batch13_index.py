#!/usr/bin/env python3
"""Source-checked index entries, printed pages 241–251.
Explicit text and references are authoritative; OCR is only a draft aid.
Baselines use a straight 42-source-pixel grid within each printed section.
A trailing | with no number denotes a genuinely blank printed reference.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
P={}
def group(n,letter,heading_y,first_y,text,step=42):
 rows=[]
 for line in text.strip('\n').splitlines():
  entry,ref=line.rsplit('|',1);assert ref=='' or ref.isdigit(),(n,line)
  rows.append(dict(text=entry,reference=ref,source_baseline=first_y+len(rows)*step))
 P.setdefault(str(n),dict(sections=[]))['sections'].append(dict(letter=letter,source_heading_baseline=heading_y,source_step=step,rows=rows))

group(241,'',None,205,'''Hull, main|217
Hull, revolving hole|223
Hull, revolving peephole|223
Hull, roof|225
Hull, spherical mounting|225
Hull, sponsons|225
Hull, turret, hemispherical|229
Hull, turret|231
Hull, turret outlook|233''')
group(241,'J',596,648,'''Jockey pulley|233''')
group(241,'L',716,769,'''Lighting dynamo|233
Louvre, inlet|233
Louvre, outlet|233''')
group(241,'O',913,968,'''Oil tanks|235''')
group(241,'R',1031,1084,'''Road track, adjusting wheel|235
Road track, driving wheel|235
Road track, link and shoes|237
Road track, lower roller, with spring|237
Road track, lower roller, without spring|237
Road track, top roller|237''')
group(241,'S',1357,1410,'''Silencer|239
Speedometer|239
Starting motor and generator|239''')
group(241,'T',1556,1609,'''Towing gear|239''')
group(241,'Y',1674,1727,'''Yardometer drive|239''')

group(242,'A',365,443,'''Adjustment, brake|150
Adjustments, carburetor|76
Adjusting shaft, track|139
Adjusting the generator switch or cutout|169
Adjusting the regulator|169
Adjusting wheel, road track|138
Air-pressure gauge|53
Air-pressure system|32
Air pump|24
Air valve|75
Aligning connecting rods|94
Ammunition and armament, general description|171
Ammunition and armament specifications|171
Ammunition, machine gun|171
Assembly, cylinder|87
Assembling, oil pump|86
Assembly, oil pump|110
Assembling the cam shaft|81''')
group(242,'B',1210,1264,'''Base, distributor|67
Bearings, fitting connection rod|92
Bevel box, fan|24
Bevel driver, water pump|102
Brake adjustment|150
Brake connections|149
Brake control, linkage reduction|158
Brake, track|
Breakers, synchronizing|107
Breathers, crank case|110
Brief description|11
Bulkhead door, to open|42
Bulkhead, mounted on|42''')
group(242,'C',1826,1880,'''Cam shaft, assembling the|81
Cam shaft, disassembling and inspection|79
Cam shaft housing units|78
Capacity of fan|176
Carburetor|72
Carburetor adjustments|76
Carburetor description|72
Carburetor function, unusual|76
Carburetors|103
Carden brake, to adjust|150
Care, inspection and, carburetor|77''')

group(243,'',None,200,'''Care and maintenance of generator|169
Casing, chain|24
Center control rods|20
Chain casing|134
Chain casing, to remove|134
Chain, drive|24
Chain drive specifications|130
Chain, driving sprocket|132
Chain sprocket pinion|130
Chain sprocket and roller pinion|132
Clean valves|88
Clearances, summary of|113
Clutch|25
Clutch, compound|115
Clutch description|115
Clutch lever|149
Clutch shaft|24
Clutch specifications|115
Clutch throw-out, to adjust|151
Clutch, to remove|118
Clutch, to reline|118
Cold-weather suggestions|55
Compound clutch|115
Connections, brake|149
Connections, gasoline pipe|32
Connecting rods|91
Cooling fan|22
Cooling system|97
Constant current generators|166
Control and drive|14
Control linkage|148
Control system, general description|146
Control system specifications|146
Controls, speed|146
Correct functioning, tests|165
Crank case|96
Crank case breathers|110
Crank case, lower half|101
Crank shaft|94
Crank shaft|101
Cutouts or generator switch, adjusting|169
Cylinder assembly|87
Cylinders|102''')
group(243,'D',2017,2075,'''Description, brief|11
Description, carburetor|72
Description, engine and engine systems|45
Description, oiling system|83
Description of ventilating system|176
Device for unditching|177
Disassembling and inspection, high tension wiring|67
Disassembling and inspection, oil pump|86
Disassembling and inspection, connecting rods|91''')

group(244,'',None,192,'''Disassembling and inspection, cooling system|98
Disassembling and inspection cam shaft|79
Disassembling generator drive|83
Dismounting the pistons|89
Distributors|65
Distributor base|67
Doors, hull|39
Drive and control|14
Drive, chain|130
Drive chain, to remove|134
Drive, how to|15
Drive, low gear|126
Drive, progress of|120
Drive, the air pump|31
Drive, to disassemble cam shaft|81
Driver, water pump bevel|100
Driving member specifications|126
Driving sprocket chain|132
Driving wheel, road track|137
Driving wheel, road track|137''')
group(244,'E',1039,1082,'''Electrical equipment|63
Electrical equipment, general description|160
Electrical equipment specifications|160
Engine, timing|103
Engine, to assemble the|101
Engine, to drain|57
Engine, to remove|110
Engine, to start|51
Engine-cooling system|98
Engine inspection|61
Engine lubrication|17
Engine-oil specifications|
Engine overhaul|63
Engine troubles|57
Engine and engine systems description|45
Engine and engine systems specifications|45
Epicyclic drive, progress|120
Epicyclic gear|18
Epicyclic gear, to remove|127
Epicyclic gear set, to mount|127
Epicyclic transmission specifications|119
Equipment, electrical|63
Equipment carried on Mark VIII machine|177
Equipment of machine|177''')
group(244,'F',2110,2158,'''Fan bevel box|24
Fan capacity|176
Fan, to remove the sirocco|98
Fans, cooling|22
Fans, ventilating|22
Filling oil reservoir|51''')

group(245,'',None,201,'''Firing point, tappet gap and|105
Fitting connecting rod bearings|92
Fittings and equipment, miscellaneous|177
Front control rods|19''')
group(245,'G',390,433,'''Gas motor, to start|161
Gasoline, mileage per gallon|17
Gasoline flow, to start|31
Gasoline petrol system|30
Gasoline pipe connections|32
Gasoline system|30
Gasoline system specifications|29
Gasoline tanks|30
Gauge, air pressure|53
Gear, epicyclic|18
Gear, towing|182
General description ammunition and armament|171
General description chain drive|130
General description control system|146
General description electrical equipment|160
General description epicyclic transmission|119
General description road track and track drive|136
Generator|25
Generator, care and maintenance|169
Generator, to dismount the|70
Generator drive, disassembling|83
Generator switch or cut-out, adjusting|169
Generator test|168
Governor|110
Ground pressures|11''')
group(245,'H',1495,1538,'''Headers, intake|102
Headers, outlet|103
Headers, to remove intake|77
Headers, to remove water outlet|77
High-speed brake, to adjust|151
High-speed brake, to reline|154
High-speed progression|120
High-tension wiring, disassembling and inspection|67
Hinges, sponson|26
Hotchkiss spare parts|173
How to drive|15
How to steer|15
Hull, openings in|43
Hull doors|39
Hull layout|11
Hull structure specifications|35''')
group(245,'I',2227,2270,'''Ignition, timing|107
Ignition switch|71
Inlet louver|176''')

group(246,'',None,194,'''Inspection, engine|61
Inspection, disassembling and|70
Inspection, disassembling and|86
Inspection, disassembling and|91
Inspection, disassembling and|99
Inspection and care|77
Instructions, lubricating|17
Instructions, operating|14
Instruction, special starting|160
Intake headers|102''')
group(246,'J',616,659,'''Jockey pulley|25''')
group(246,'L',726,774,'''Layout, hull|11
Lever, clutch|149
Levers, reverse|150
Linkage, control|148
Linkage reduction brake control|158
Links, track|137
Location of machine guns|175
Location of machine guns|182
Location of 6-pounder guns|175
Location of 6-pounder shells|171
Louvers|40
Louvers, to remove|41
Low, shifting to|15
Low gear drive|126
Low-gear brake, to reline|154
Low-speed brake, to adjust|154
Lower cam-shaft drive shafts|81
Lower road track roller, to remove|144
Lower road track rollers|18
Lower road track rollers with spring plates|141
Lower road track rollers without spring plates|141
Lubricating instructions|17
Lubricating routine|26
Lubrication, engine|17''')
group(246,'M',1800,1848,'''Machine, equipment|177
Machine-gun ammunition|171
Machine-gun, to mount|175
Machine guns, location|175
Machine guns, location|182
Main turret|38
Maintenance and care of generator|169
Manifolds, water inlet|109
Mark VIII machine, equipment carried|177
Mileage per gallon gasoline|17
Miscellaneous fittings and equipment|176
Motor, starting|25
Mounted on bulkhead|42''')

group(247,'N',126,168,'''Neutral point|104''')
group(247,'O',235,277,'''Obstructions, passing over|16
Oil pump|86
Oil-pump assembly|110
Oiling system|83
Oiling system, description|83
Openings in hull|43
Operating instructions|14
Operation and description, constant current generators|166
Operation and description, starting motor|162
Outlet headers|103
Outline specifications|9
Overhaul, engine|63''')
group(247,'P',796,841,'''Parts, 6-pounder|174
Passing over obstructions|16
Pinion, chain sprocket|130
Pinions, roller|24
Pins, track link|22
Pistons|89
Pistons, dismounting the|89
Point, neutral|104
Precaution|166
Preliminary to starting|14
Preparing engine for service|46
Pressures, ground|11
Progression, high speed|120
Progress of epicyclic drive|120
Progress of drive|13
Pulley, jockey|25
Pump, air|24
Pump, oil|86''')
group(247,'R',1622,1667,'''Radiator, to remove the|98
Rear control rods|22
Regulator|167
Regulator, adjusting|169
Regulator, voltage|71
Remedies and troubles|165
Remove the track|142
Reservoir, filling engine oil|51
Reversing|15
Reverse levers|150
Reverse speeds|126
Rings|89
Road track|25
Road track adjusting screw|23
Road track adjusting wheel|138
Road track adjusting wheel|23
Road track adjusting wheel, to remove|143''')

group(248,'',None,186,'''Road track and track drive specifications|136
Road track driving wheel|23
Road track driving wheel|133
Road track driving wheel|137
Road track driving wheel, to remove|143
Road track rollers|140
Rod, connecting|101
Rods, aligning connecting|94
Rods, center control|20
Rods, front control|19
Rods, rear control|22
Roller, lower road track|18
Roller, sponson|38
Rollers, upper road track|19
Roller pinion, to remove|135
Roller pinion, to remove|144
Roller pinion and chain sprocket|132
Roller pinions|24
Roller spring, to remove|144
Rollers, road track|140
Rollers, top road track|142
Rollers, upper road track|18
Rollers with spring plates, lower road track|141
Rollers without spring plates, lower road track|141
Routine, lubricating|26''')
group(248,'S',1242,1284,'''Service, preparing engine for|46
Screw, road track adjusting|23
Shaft clutch|24
Shafts, lower cam-shaft drive|81
Shifting to low|15
Shifting to reverse|15
Shock|166
Six-pounder guns, location|174
Six-pounder guns, to remove and replace|175
Six-pounder guns, to withdraw|174
Six-pounder parts|174
Six-pounder shells, location|171
Smoke bombs|172
Spare barrels|182
Spare machine-gun barrels|172
Spare parts, Hotchkiss|173
Spark and throttle|148
Special starting instruction|160
Specifications, ammunition and armament|171
Specifications, chain drive|130
Specifications, control system|146
Specifications, driving members|126
Specifications, electrical equipment|160
Specifications, engine and engine systems|45
Specifications, engine oil|49
Specifications, epicyclic transmission|119
Specifications, gasoline system|29''')

group(249,'',None,202,'''Specifications, hull structure|35
Specifications, road track and track drive|136
Specifications, table of|9
Specifications, ventilating system|176
Speed controls|146
Speeds, reverse|126
Sponson hinges|26
Sponson roller|38
Sponsons, to remove|42
Sponsons, to replace|42
Starting motor|25
Starting motor, operation and description|162
Starting, preliminary to|14
Steering|15
Steering|148
Sticking|165
Suggestions, cold weather|55
Summary of clearances|113
Switch, ignition|71
Synchronizing breakers|107
System, air pressure|32
System, cooling|97
System, engine cooling|97
System, gasoline|29
System, gasoline petrol|30
System, oiling|83
System, to fill cooling|47
System, to fill gasoline|31
Systems, the gasoline|47''')
group(249,'T',1436,1478,'''Table of specifications|9
Table of weights|9
Tank, gasoline|30
Tappet gap and firing point|105
Tests to insure correct functioning|165
Timing ignition|107
The air-pump drive|31
The clutch lever|149
The gasoline systems|47
Throttle and spark|148
Throttles|103
Timing engine|103
Top road track roller, to remove|143
Top road track rollers|142
Towing gear|182
Track adjusting shaft|139
Track brake|156
Track brake, to adjust|158
Track drive and road track specifications|136
Track link, to remove|142
Track link pins|22
Track links|137
Track, road|25''')

group(250,'',None,205,'''Track, to adjust|142
Track, to remove|142
Transporting Mark VIII machine|17
Troubles, engine|57
Troubles and remedies|165
Turn, to make a wide|16
Turret, main|38
To adjust the Cardan brake|150
To adjust the clutch throw-out|151
To adjust the high-speed brake|151
To adjust the low-speed brake|154
To adjust the track|142
To adjust the track brake|158
To advance or retard valve setting|106
To assemble the engine|101
To disassemble cam-shaft drive|81
To dismount the generator|70
To drain engine|57
To fill cooling system|47
To fill gasoline system|31
To make a wide turn|16
To mount epicycle gear set|127
To mount machine gun|175
To open bulkhead door|42
To reassemble water pumps|100
To reline clutch|118
To reline high-speed brake|154
To reline low-gear brake|154
To remove and replace the 6-pounder guns|175
To remove chain casing|134
To remove engine|110
To remove intake headers|77
To remove louvers|41
To remove lower road track roller|144
To remove roller pinion|135
To remove roller pinion|144
To remove roller spring|144
To remove sponsons|42
To remove the clutch|118
To remove the drive chain|134
To remove the epicyclic gear|127
To remove the radiator|98
To remove the road track adjusting wheel|143
To remove the road track driving wheel|143
To remove the sirocco fan|98
To remove the track|142
To remove top road track roller|143
To remove track link|142
To remove valves|87
To remove water-outlet headers|77
To replace sponsons|42
To start engine|51
To start gasoline flow|31
To start the gas motor|161
To withdraw the 6-pounder guns|174''')

group(251,'U',180,225,'''Unditching device|177
Units, cam-shaft housing|78
Unusual carburetor function|76
Upper road track rollers|18''')
group(251,'V',420,465,'''Valve, air|75
Valve setting, to advance or retard|106
Valves|87
Valves, clean|88
Ventilating fans|22
Ventilating system, description|176
Ventilating system specifications|176
Voltage regulator|71''')
group(251,'W',833,878,'''Water-inlet manifolds|109
Water-pump bevel driver|100
Weights, table of|9
Wheels, road track adjusting|138
Wheel road track driving|133
Wiring|160
Wiring, high-tension, disassembling and inspection|67''')

for n,p in P.items():
 p.update(page=int(n),source=f'MarkVIII{int(n)//2+1:03}.jpg',source_side='right' if int(n)%2 else 'left',source_policy='Direct transcription from full source half; first OCR draft may clip initial letters near the binding. Printed repetitions and blanks retained.',entry_font_size_pt=9.0)
 p['page_header_baseline']=p['sections'][0]['rows'][0]['source_baseline']-42
 if n=='241':p['signature']={'text':'38285—25†——16','baseline':1774}
 if n=='249':p['signature']={'text':'38285—25†——17','baseline':2456}
 if n=='242':p.update(title='GENERAL INDEX',title_baseline=212,title_rule_y=272,bottom_folio_baseline=2360)
 if n=='251':p['end_mark']={'shape':'ellipse','source_top':1180,'width_pt':8.1,'height_pt':8.1}
rows=[(n,s,r) for n,p in P.items() for s in p['sections'] for r in s['rows']]
(R/'data/index_batch13.json').write_text(json.dumps(P,ensure_ascii=False,indent=2)+'\n')
(R/'data/batch13_index_transcription.tsv').write_text('printed_page\tletter\tentry\tpage_reference\n'+''.join(f'{n}\t{s["letter"]}\t{r["text"]}\t{r["reference"]}\n' for n,s,r in rows))
(R/'data/body_batch13.json').write_text('{}\n')
print('Index entries',len(rows),'per page',{n:sum(len(s['rows']) for s in p['sections']) for n,p in P.items()})
print('Blank references',[(n,r['text']) for n,s,r in rows if not r['reference']])
