"""Source-checked front matter; original order and apparent anomalies retained."""
TOC = {
3: [
('I','GENERAL DESCRIPTION AND INSTRUCTIONS', [('General weights and specifications','9'),('General description','11'),('Driving instructions','15'),('Lubricating instructions','17'),('Gasoline system','29'),('Air-pressure system','32')]),
('II','HULL STRUCTURE',[('Hull specifications','35'),('Hull description','35'),('Openings in hull','43')]),
('III','ENGINE AND ENGINE SYSTEMS',list(zip(['Engine specifications','Engine description','Preparing engine for service','Engine-oil specifications','To start engine','Engine overhaul','Engine ignition','Carburetor','Cam shaft','Engine oiling system','Engine valves','Pistons','Connecting rods','Crank case','To assemble engine','Valve timing','Summary of clearances'],['45','45','46','49','51','63','65','72','78','83','87','89','91','96','101','106','113']))),
('IV','COMPOUND CLUTCH',list(zip(['Clutch specifications','Clutch description','To remove clutch','To reline clutch'],['115','115','118','118']))),
('V','EPICYCLIC TRANSMISSION',list(zip(['Epicyclic specifications','Epicyclic gear description','High-speed progression','Low-speed progression','To remove epicyclic'],['119','119','120','126','127']))),
('VI','CHAIN DRIVE',list(zip(['Chain-drive specifications','Chain-drive description','Chain-sprocket pinion','Driving-sprocket chain','Road track driving wheel','To remove chain','To remove chain casing','To remove roller pinion'],['130','130','130','132','133','133','134','135'])))],
4: [
('VII','ROAD TRACK AND ROAD TRACK DRIVE',list(zip(['Track specifications','Track description','Track links','Road track adjusting wheel','Track-adjusting shaft','Road-track rollers','To remove track','To adjust track'],['136','136','137','138','139','140','142','142']))),
('VIII','CONTROL SYSTEM',list(zip(['Control specifications','Control description','Steering','Spark and throttle','Brake connections','Reverse levers','To adjust Cardan brake','To adjust throwout','To adjust high-speed brake','To adjust low-speed brake','To adjust track brake'],['146','146','148','148','149','150','150','151','151','154','158']))),
('IX','ELECTRICAL EQUIPMENT',list(zip(['Electrical specifications','Electrical units, description','Starting motor','Starter troubles','Generator','Regulator','Maintenance of generator'],['160','160','162','165','166','167','169']))),
('X','AMMUNITION AND ARMAMENT',list(zip(['Armament specifications','Armament description','Spare machine-gun barrels','Hotchkiss spare parts','Removing and replacing guns'],['171','171','172','173','174']))),
('XI','MISCELLANEOUS FITTINGS AND EQUIPMENT',list(zip(['Ventilator specifications','Ventilator description','List of equipment'],['176','176','177']))) ]}
# number|wording|reference; a slash within wording is the original line break.
PLATE_ROWS='''1|Right side view of 35-ton tank, Mark VIII|8
2|Sectional view through the 35-ton tank, Mark VIII|10
3|Towing gear|12
4|Top of machine|13
5|Three-quarter front view of Mark VIII machine|14
6|Driver’s seat and controls, also showing ammunition storage|16
7|Lower road track roller|17
8|Lower road track roller|18
9|Upper road track roller|19
10|Epicyclic oiler|20
11|Epicyclic cup|20
12|Control rods|21
13|Epicyclic case|21
14|Fan bevel box|22
15|Air pump|23
16|Roller pinion lubrication|24
17|Ventilator fan|25
18|Engine-oil reservoir|26
19|Sirocco fan|27
20|Chain drive|27
21|Layout of gasoline pressure-feed system used on 35-ton tank, Mark/VIII|28
22|Air-pressure pump|29
23|Pressure-regulating tank|30
24|Combination tap|31
25|Gasoline tank|33
26|Side of hull with sponson and gun|34
27|Rear end, showing triangular splash plate and towing eye|36
28|Door of hull, showing fittings|37
29|Progressive steps in uncovering revolver hole|38
30|Top of hull|39
31|Side of turret showing camouflage bracket|40
32|Side of hull|41
33|Side towing bracket|43
34|Front of machine|44
35|Sirocco cooling fan|48
36|Cooling system|50
37|Valve and pump drive|52
38|Engine-oil system|54
39|Cam-shaft assembly|56
40|Longitudinal engine section|58
41|Distributor end of engine|60
42|Propeller end of engine|62
43|Outline dimensions|64
44|Crank-case dimensions|66
45|Dimensions front elevation|68
46|Ignition switch|71
47|Section through carburetor|73
48|Carburetor jets and valves|74
49|Outline of carburetor|75
50|Valve rocker arm|78
51|Generator drive shaft|82
52|Water-pump assembly|85
53|Cylinder assembly|87
54|Removing piston pin|89
55|Removing pin (alternative method)|89
56|Fitting rings|90
57|Connecting rods|91
58|Aligning rods|93
59|Aligning rods|93
60|Aligning rods|93
61|End of crankshaft|95
62|Jockey pulley|95
63|Crank case|96
64|Pipe installation|97
65|Fan bevel gear drive|99
66|Test lamps and current|108
67|Section of governor and linkage|111
68|Section through governor|112
69|Muffler|112
70|Fan bevel box|114
71|Compound clutch|116
72|Pattern of clutch|117
73|Epicyclic transmission|121
74|High speed, forward|123
75|High speed, reverse|123
76|Low speed, forward|124
77|Low speed, reverse|124
78|Epicyclic drive|125
79|Exterior view epicyclic transmission|126
80|Epicyclic planetary ring|128
81|Progressive drive|129
82|Roller pinion and track drive|131
83|Road track driving wheel|133
84|Road track link|137
85|Top track rail upon which track slides|138
86|Road track driving wheel|139
87|Road track adjusting wheel|140
88|Top road track roller|140
89|Lower road track roller|143
90|Road track wheel|144
91|Track roller|145
92|Layout of the control system, showing linkage and levers|147
93|Positions of speed lever|149
94|Positions of reversing lever|150
95|Brake adjustment|151
96|Spark or throttle lever|152
97|Low-gear brake lining|152
98|Track brake lining|153
99|High-speed brake lining|154
100|High-speed brake|155
101|Track brake|156
102|Arrangement of low-gear brake|157
103|Bulkhead with instrument board removed|158
104|Control rod ends with epicyclic transmission removed from hull|159
105|Wiring of lighting, starting, and ignition|161
106|Starter pinion shift|162
107|Third brush regulation|163
108|Six-pounder gun, showing also ammunition storage|172
109|Ammunition storage box|173
110|Layout of ventilating system|178
111|Compound clutch|186
112|Top of road track|186
113|Control system|187
114|Regulating tank assembly|193
115|Air-pressure pump|195
116|Jockey pulley|195
117|Muffler|197
118|Gasoline tank|197
119|Road-track driving wheel|202
120|Road track adjusting wheel|204
121|Arrangement of epicyclic bevel drive|204
122|Epicyclic trains|206
123|Epicyclic drive|208
124|Fan bevel box|210
125|Road track driving-wheel section|210
126|Characteristic speed and governor curves of engine in 35-ton, Mark/VIII tank|212
127|Oil tank|214
128|Upper part of hull|216
129|Hull plating|218
130|Sponson rolled back for shipping purposes|220
131|Gasoline tank installation|222
132|Roller sprocket and road track driving wheel|224
133|High-speed brake|226
134|Low-speed brake|228
135|Track brake|230
136|Top road track roller|232
137|Lower road track roller without springs|232
138|Lower road track roller with springs|232
139|Water pump|234
140|Combination tap|234
141|Fuel supply system|236
142|Proper way to lift engine|238
143|Proper way to lift engine|238'''
PLATES=[(int(n),t,p) for n,t,p in (row.split('|') for row in PLATE_ROWS.splitlines())]
SPECS='''Length, over all|34 feet 2½ inches.
Width, over all|12 feet.
Width, sponsons withdrawn|9 feet.
Height, over all|10 feet 3 inches.
Ground clearance under hull|1 foot 8¾ inches.
Weight, loaded|40 tons.
Area of ground contact|41.052 square feet.
Unit ground pressure at 1″ submersion|975 tons per square foot.
Tread, center to center of tracks|5 feet 9½ inches.
Width of track shoe|2 feet 2½ inches.
Forward speed at 1,400 r. p. m.:|
    High gear|5.2 m. p. h.
    Low gear|1.4 m. p. h.
Diameter of turning circle|40.5 feet.
Length of ground contact|9 feet 3½ inches.
Number of track links|78.
Length of track, expanded|72 feet 6 inches.
Engine, B. H. P. at 1,400|338.
Number of forward speeds|2.
Number of reverse speeds|2.
Total high-speed ratio|32.545 to 1.
Total low-speed ratio|126.64 to 1.
Number of gasoline (petrol) tanks|3.
Total gasoline (petrol) capacity|240 gallons.
Number of 6-pounder guns|2.
Number of machine guns|7.
Number of spare machine-gun barrels|7.
Number of round 6-pound common shell|182.
Number of round 6-pound case shell|26.
Number of doors|3.
Weight of engine|850 pounds.
Weight of gasoline (petrol) carried|1,440 pounds.
Type of radiator|Tubular.
Total cooling area|89.5 square feet.'''
