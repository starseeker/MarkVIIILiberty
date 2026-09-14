"""Reviewed batch-01 text, retaining source line endings and printed anomalies.
This preparation script overwrites data/transcription.json; edit the JSON directly
after initial generation and do not rerun this file over subsequent manual edits.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
draft={p['leaf']:p['lines'] for p in json.loads((ROOT/'data/ocr_draft.json').read_text())}
pages={n:dict(leaf=n,label=['Cover','Inside cover (blank)','Title','Frontispiece'][n-1] if n<=4 else str(n-2),blocks=[]) for n in range(1,21)}
def block(n,start,end,y,step=54,x=195,indent=107,changes=None):
 ls=[]
 for i in range(start,end+1):
  l=draft[n][i];t=(changes or {}).get(i,l['text'])
  ls.append(dict(text=t,indent=indent if l['box'][0]>x+65 else 0))
 pages[n]['blocks'].append(dict(y=y,step=step,x=x,width=1455,lines=ls))
def manual(n,y,text,step=54,x=195,width=1455):
 ls=[]
 for t in text.strip('\n').splitlines():
  ind=107 if t.startswith('>') else 0
  ls.append(dict(text=t.lstrip('>'),indent=ind))
 pages[n]['blocks'].append(dict(y=y,step=step,x=x,width=width,lines=ls))

block(7,12,47,1080,x=198,changes={14:'is 5 in. (127 mm.), and the stroke 7 in. (177.8 mm.). The',15:'“dry” weight is 820 lbs. The engine is constructed in two',17:'ratio (5.3 : 1) than the naval type (4.78 : 1); the maximum',18:'r.p.m. of both types are 1750, at which speed 425',24:'steel tube with welded jackets: there are two valves per',27:'cated by splash. Oil is pressure-fed to the rest of the',31:'Ignition is by the Delco system. A twelve-point',36:'the current is furnished by a dynamo generator,',42:'Two duplex Zenith carburettors (type 52 D.F.) of',43:'American manufacture are fitted on the engines now being',44:'delivered, but later engines will be equipped with two',45:'Claudel-Hobson carburettors, type H.C. 7.',46:'An electric starter is to be fitted, for which a'})
manual(10,1790,'''Number and arrangement of cylinders.—12. Vee at 45°.
Bore.—5 ins. (127 mm.).
Stroke.—7 ins. (177.8 mm.).
Stroke : bore ratio.—1.4 : 1.
Stroke volume of one cylinder.—137.45 cub. ins. (2,252
>cub. cms.).
Total stroke volume of engine.—1,648.8 cub. ins. per rev.
>(27,040 cub. cms.).
Area of one piston.—19.63 sq. ins. (126.6 sq. cms.).
Total piston area of engine.—235.6 sq. ins. (1,520
>sq. cms.).
Clearance volume of one cylinder.—36.4 cub. ins. (naval
>type), 31.9 cub. ins. (army type).
Compression ratio.—4:78 (naval type), 5:3 (army type).
Normal B.H.P. and speed.—405 h.p. at 1,650 r.p.m.
Maximum r.p.m. near ground.—1,500 r.p.m.
Maximum r.p.m. at altitude.—1,750 r.p.m. (above 6,000
>ft. only).
Piston speed.—1,925 ft./min. at 1,650 r.p.m.
Brake mean effective pressure.—118 lbs./sq. in for
>405 h.p. at 1,650 r.p.m.
Cub. in. of stroke volume per b.h.p.—4.07 cub. ins.
>(66.69 cub. cms.).
Sq. in. of piston area per b.h.p.—.582 sq. in. (3.75
>sq. cms.)''',x=248)
manual(11,238,'''H.P. per cub. ft. of stroke volume.—424 (15.0 h.p.
>per cub. metre).
H.P. per sq. ft. of piston area.—247 (2.666 h.p. per
>sq. metre).
Rotation of crank.—Right-hand tractor (left-hand
>pusher).
Rotation of propeller.—As above.
Speed of propeller.—Ungeared.
Lubrication system.—Force feed to main bearings, big
>ends, and camshafts. Splash to pistons and gud-
>geon pins. Dry sump.
Oil recommended.—Mobiloil BB.
Oil pressure recommended.—Minimum, 25 lbs. per sq.
>in.; Maximum, 35 lbs. per sq. in.—at 1,650 r.p.m.
Oil temperature recommended.—40° Centigrade.
Oil consumption per hour.—8 to 12 pints per hour.
Oil consumption per b.h.p. hour.—Average .03 pint
>H.P. hour.
Specific gravity of oil.—.9.
Carburettors.—Two American Duplex Zenith, type
>52 D.F., with modified altitude control (vacuum);
>or two Claudel-Hobson, type H.C. 7.
Fuel consumption per hour.—198.5 lbs.
Fuel consumption per b.h.p. hour.—.49 lbs.
Specific gravity of fuel.—.72.
Ignition.—Delco system. Two distributors: four con-
>tact breakers in parallel; dynamo generator,
>supplemented by accumulator for starting and slow
>running.
Firing sequence of engine.—
>Left, 1, 9, 5, 11, 3, 7
>Right, 8, 4, 12, 6, 10, 2
Numbering of cylinders.—Left, 1, 2, 3, 4, 5, 6
Numbering of cylinders.—Right, 1, 2, 3, 4, 5, 6
Speed of low tension generator.—1{1/2} times engine speed.
Maximum ignition advance.—30°.
Inlet valve opens.—10° after T.D.C.
Inlet valve closes.—45° after B.D.C.
Inlet tappet clearance.—.015 in. (.0381 cm.).
Number of inlet valves.—One per cylinder.
Maximum lift of inlet valve.—{7/16} in. (1.11 cms.).
Smallest diameter of inlet valve.—2{1/2} ins. (6.35 cms.).
Area of inlet valve opening.—3.44 sq. ins. (22.2 sq. cms.).
Mean gas velocity through inlet valve.—177.7 ft. per sec.
Exhaust valve opens.—50° before B.D.C. (now 48°).
Exhaust valve closes.—10° after T.D.C. (now 8°).
Exhaust tappet clearance.—.020 in. (.0508 cm.) (now
>.019 in.).
Maximum lift of exhaust valve.—{3/8} in.
Rev. counter drive rotates.—Clockwise, facing shaft on
>engine.
Weight of engine, minus water, fuel and oil.—820 lbs.''')
manual(12,265,'''Weight per b.h.p., minus water, fuel and oil.—2.02 lbs.
Weight of exhaust manifold.—
Weight of oil carried in engine.—Nil.
Weight of starting gear.—
Weight of water carried in engine.—45.8 lbs. (4.58 gal-
>lons.)
Weight of fuel per hour.—
Weight of oil per hour.—''',x=225)
manual(12,2700,'''Total fuel and oil weight per hour.—
Gross weight of engine in running order, minus fuel
>and oil.—1,083 lbs.
Weight per b.h.p. minus fuel and oil.—2.67 lbs.
Gross weight of engine in running order, plus fuel and
>oil for six hours.—
Weight per b.h.p. plus fuel and oil for six hours.—''',x=245)
manual(13,385,'''>In the following descriptions, the propeller end of
the engine is termed the “front”; the words “right”
and “left” are used on the supposition that the engine
is viewed from the rear or distribution gear end.''',x=190)
block(14,2,13,545,x=284,changes={4:'end of the tube is closed down to form the cylinder head,',6:'The holding-down flange is “jumped up” after local',7:'heating, leaving a spigot 2{15/16} in. deep. The water jacket',11:'the two valve pockets, sparking plug bosses, upper and'})
block(14,16,19,2485,x=280,changes={17:'and short studs supporting the camcase must be inter-',19:'the left-hand block and vice versâ. (See Fig. 2.)'})
block(14,20,25,2740,x=278,changes={24:'holding-down nuts are made with circular bases of'})
block(15,1,11,430,x=151,changes={6:'water jacket of one of the four induction manifolds.'})
block(15,16,22,2720,x=155,changes={16:'The high compression pistons (Fig. 7) are of cast',18:'at the centre over a circle 2{3/8} in. in diameter. (The low',20:'internal ribs, but the crown is {3/8} in. thick, and the upper'})
block(16,6,11,2740,x=287,changes={7:'shallow circumferential oil groove is machined round',10:'are machined circumferentially on the outside of the',11:'skirt, which is not drilled at any point.'})
block(17,1,11,367,x=186,changes={9:'centres are threaded to take an extractor. The gudgeon'})
block(17,16,24,2555,x=188,changes={22:'and prevent them from “spreading”; the caps are not'})
block(18,1,4,378,x=280,changes={4:'are given on page 36.'})
block(19,3,11,1850,x=195,changes={7:'length, and the six rear bearings are 49 mm. long. The'})
block(19,12,18,2358,x=195)
block(19,19,24,2753,x=192)
block(20,2,6,1020,x=275,changes={5:'so that when assembled they leave .001 in. end play in'})
block(20,7,11,1325,x=275)
block(20,12,12,1625,x=275)
block(20,18,26,2570,x=282,changes={20:'the level of the main bearing centres, as usual. There',21:'are no “feet” or bearer brackets on the upper half: its',22:'flange overhangs the lower half for the full length of',24:'in the fuselage by seven bolts on each side. This pro-'})

toc={5:[['I','GENERAL DESCRIPTION.',[['Cylinders','12'],['Pistons','13'],['Connecting Rods','15'],['Crankshaft','17'],['Base Chamber','18'],['Valves','23'],['Camshafts, and Valve Gear','25'],['Distribution Gear','26'],['Cooling','28'],['Starter','30']]],['II','LUBRICATION SYSTEM.',[['General Description','31'],['Oil Pumps','31'],['Main and Big End Bearings','36'],['Gudgeon Pins','37'],['Camshafts','37'],['Thrust Bearing','40'],['Generator Drive','40']]]],6:[['III','CARBURATION.',[['Zenith, Type 52 D.F.','43'],['Claudel-Hobson, Type H.C.7','49']]],['IV','IGNITION.',[['Introduction','61'],['Generator','61'],['Voltage Regulator','64'],['Switchboard','67'],['Battery','69'],['Preparing the Battery','71'],['Maintaining the Battery','71'],['Fitting the Battery','73'],['Ignition Units','76'],['Contact Breakers','79'],['Distributors','81'],['H.T. Cables','84'],['Timing and Control Gear','87'],['Possible Troubles','89'],['Routine Maintenance','92']]],['V','RUNNING INSTRUCTIONS.',[['Maximum R.P.M.','94'],['Precautions with New Engine','95'],['Oil','95'],['Cooling','95'],['Oil Pressure','96'],['Warning about the Switches','96'],['Starting Up','96'],['Smoky Exhaust','97'],['After Preliminary Run','98'],['After a Flight','98'],['Periodic Attention','98']]],['VI','DISMANTLING AND OVERHAULING.',[['Preliminary Notes','100'],['Individual Accessibility','101'],['Dismantling Sequence','104'],['Notes on Dismantling Operations','105'],['Adjustment and Reassembling of Units','109'],['Re-erecting the Engine','116'],['Timing Data','120'],['Timing by the Marks','124'],['Timing with Unmarked Camshaft Gears','127'],['Timing without Marks','127'],['Completing the Reassembling','129']]] ]}
index_raw='''1|The Liberty engine|Frontispiece
2|Cylinders (photograph)|10
3|Section of cylinder, showing welded joints|11
4|Cylinder head|12
5|Side view of a cylinder|13
6|Section of a cylinder through valve gear|14
7|Broken view of high compression piston|15
8|Pistons and gudgeon pins (photograph)|16
9|Pair of connecting rods (assembled)|16
10|Pair of connecting rods (dismantled)|17
11|Main bearing (lower half)|18
12|Crankshaft taper and key|18
13|The Liberty engine (three-quarter side~view)|19
14|Top half of crankcase|20
15|Top half of crankcase (from beneath)|20
16|Bottom half of crankcase|21
17|Bottom half of crankcase, with crankshaft~in position|22
18|Valve|24
19|Camshaft|24
20|Camcase|25
21|Valve rockers|26
22|Diagram of distribution gear|27
23|Water pump, shown dismantled|29
24|Broken view of oil pump unit|30
25|Diagram of oil pump unit|32
26|Diagram of lubrication system|33
27|Plan view of scavenge sumps|34
28|Plan view of pressure pump|34
29|Cross section of oil pump, showing rear~half)|35
30|Cross section of oil pump (showing front~half)|35
31|Front main bearing, showing oil leads|37
32|Camshaft oil connection|38
33|Oil-pump unit dismantled (photograph)|39
34|Oil pump unit, photographed from~below; cover removed|39
34a|Details of valve rocker oiling|40
35|Three-quarter top view of engine|41
36|Photograph of Zenith carburettor|42
37|Diagram of the Zenith principle|43
38|Broken view of Zenith carburettor|44
39|Section of Zenith (between the two~mixing chambers)|46
40|Section of Zenith (through jets)|47
41|Plan of Zenith carburettor|47
42|Diagram of Zenith altitude control|49
43|Photograph of H.C.7 duplex carburettor|50
44|Section of H.C.7 duplex carburettor|52
45|H.C.7 throttle barrel|52
46|Section of H.C.7 diffuser|53
47|H.C.7 diffuser, shown dismantled|54
48|Diagram showing arrangement of H.C.7~altitude control|58
49|Diagram showing positions of H.C.7~altitude control cock|59
50|Photograph of H.C.7 altitude control cock|60
51|Generator|62
52|Voltage regulator|64
53|Front of switchboard|66
54|Back of switchboard|66
55|Mounting of switchboard and regulator|67
56|Section through Willard cell|69
57|Measuring depth of electrolyte|70
58|Removing surplus electrolyte|72
59|Taking gravity of electrolyte|73
60|An ignition unit|74
61|Contact breaker|75
62|Back of contact breaker base plate|76
63|Attachment of contact breaker base|77
64|Cam and cam spindle|77
65|Cam spindle drive (early pattern)|88
66|Cam spindle (later pattern)|79
67|Main contact breaker lever|80
68|Distributor head (exterior)|82
69|Distributor head (interior)|83
70|Cable plate|84
71|Sequence of firing, and distributor~connections|85
72|Ignition timing diagram|86
73|Wiring diagram|90
74|Rear end view of engine showing distri-~butors and generator|94
75|Three-quarter side view of engine|99
76|Front end view of engine|104
77|Details of propeller hub|105
78|Mode of removing induction manifolds|106
79|Broken view of water pump unit|108
80|Low compression piston|109
81|Camshaft bearings|110
82|Camshaft bearing (showing location~marks)|111
83|Camcase cover (showing location mark)|111
84|Valve|113
85|Main thrust bearing|114
86|Mounting of main driving bevel on~crankshaft|115
87|Oil trap in upper half of crankcase|116
88|Housing and bush of lower vertical shaft|118
89|Water joint clip|119
90|Numbering of cylinders|120
91|Timing marks on camshaft flange and~distributor hub|121
92|Timing marks on propeller hub flange|122
93|Distribution gear in section, explaining~timing marks|123
94|Timing marks on camshafts and inclined~shafts|125
95|Timing diagram|128
96|Rear end of crankcase from beneath, with~oil pump removed|129
97|C.C. gun gear|138
98, 99|Adjustment of Zenith controls|143
100-103|Installation drawings|144, etc.
104-106|Sections and elevations of engine|148, etc.
107|General arrangement|151'''
indices={8:[],9:[],10:[]}
for raw in index_raw.splitlines():
 n,t,p=raw.split('|');v=int(n.split(',')[0].split('-')[0].replace('a',''));leaf=8 if v<=40 else 9 if v<=85 else 10
 indices[leaf].append(dict(number=n,text=t.split('~'),reference=p))
(ROOT/'data/transcription.json').write_text(json.dumps(dict(pages=list(pages.values()),contents=toc,illustration_index=indices),ensure_ascii=False,indent=2))
print('Prepared reviewed text, contents and',sum(map(len,indices.values())),'illustration-index entries.')
