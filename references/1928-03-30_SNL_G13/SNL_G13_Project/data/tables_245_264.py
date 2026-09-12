"""Photograph-led transcription of printed pages 245–264.
Original page breaks, blank fields and apparent source errors retained.
"""
from .parts_tables import row
from .opening_tables import entry,component,composed
from .tables_045_064 import assembly
from .tables_065_084 import pieces,stacked
from .tables_225_244 import append_rows,grouped
TABLES={}
def start(page):
 TABLES[page]=[]
 return TABLES[page]
def add(page,content):
 r=start(page);append_rows(r,content);return r

r=start(245)
component(r,'*one M3292    engine oil tank BODY (1)',ord='19',price='26.60')
pieces(r,'''one SH978S   engine oil tank BUSHING, (bottom),
one M3301    engine oil tank delivery PIPE,
one M3294    engine oil tank filler CAP,
one M3295    engine oil tank filler cap GASKET,
one SH978N   engine oil tank filler flange PLUG,
one SH978M   engine oil tank filler plug FLANGE,
one M3293    engine oil tank filling cover FLANGE,
one —        engine oil tank FILTER, assembly,
one M3305B   engine oil tank indicator flange CAP,
one M3307    engine oil tank indicator float TUBE,
two M3315    engine oil tank suction and delivery FLANGE,
four M3310   engine oil tank support CLEAT,
one M3304    indicator FLANGE,''')
component(r,'*one M3311    FLANGE, drain cock (2)',ord='165',price='.49')
pieces(r,'''one Q52B     PLUG, pipe, square head, ¼″,
one Q52D     PLUG, pipe, square head, ½″,
one Q52E     PLUG, pipe, square head, ¾″,
twenty-four —      RIVET, button head, ¼″ x ¾″,
   eighteen —      RIVET, button head, ¼″ x ⅞″,
     twelve —      RIVET, button head, ¼″ x 1″.)''')
assembly(r,'TANK, gasoline, assembly','90.24',note='(gal)&',ident='—',plate='8',qty='(3)')
component(r,'*one M1755      gasoline TANK (3)',ident='1',plate='8',ord='238',price='75.00')
pieces(r,'''one E152/21255  gasoline tank drain PLUG,
one M1757       gasoline tank drain plug FLANGE,
one —           gasoline tank filler cap FLANGE, assembly,''')
component(r,'*one M1756      gasoline tank filler cap flange stiffening RING (inside\n                       tank) (3)',ord='235',price='.85')
component(r,'*one M1761      gasoline tank filler cap flange stiffening RING (3)',ord='235',price='1.50')
pieces(r,'''one M1766       gasoline tank filler flange JOINT,
one —           gasoline tank STRAINER, assembly,
one B153/21256  gasoline tank strainer CAP,
one M1758       gasoline tank strainer drain plug WASHER,
one D153/21256  gasoline tank strainer flange WASHER,
one M1765       gasoline tank suction PIPE,
 six —          RIVET, button head, ¼″ x ½″,
eight —         RIVET, button head, ⅜″ x 1⅛″,
eight —         SCREW, cap, U. S. Std., hexagon head, ⅜″ x ⅝″.)''')

r=start(246)
assembly(r,'TANK, regulating, assembly','$17.64',note='%',ident='14\n24',plate='8\n2')
r[-2].update(space_before=.5,space_after=.5,cell_baseline_offsets={'ident':-.5,'plate':-.5})
pieces(r,'''one SH950D  air pipe regulating tank CONNECTION,''')
component(r,'*one SH950A  regulating TANK (1)',price='6.50')
pieces(r,'''one SH962H  regulating tank air COCK, No. 1,
one —       regulating tank CAP, assembly,
one SH950M  regulating tank cap GASKET,
one —       regulating tank FLOAT, assembly,
one SH962C  regulating tank relief valve FLOAT,
one —       regulating tank relief valve guide FRAME, assembly,
one —       regulating tank relief valve STEM, assembly,
one SH962A  regulating tank relief valve SUPPORT,
one SH950E  regulating tank VALVE,
one SH950B  regulating tank valve BRACKET,
one —       regulating tank valve bracket PIN, assembly,''')
component(r,'*one SH950H  valve bracket HOLDER, with gas inlet',price='1.03')
pieces(r,'''twenty —       BOLT, U. S. Std., hexagon head, ¼″ x ⅝″, with plain~                     nut and lock washer,
  four —       BOLT, U. S. Std., hexagon head, ¼″ x 1″, with plain nut~                     and lock washer,
   six —       RIVET, button head, ⅛″ x ⅜″,
   six —       RIVET, button head, ⅛″ x 7/16″,
   two —       SCREW, machine, No. 10 (3/16″) x ¾″, with machine screw~                     nut, plain copper washer and lock washer,
   one —       SCREW, set, U. S. Std., square head, round point, ⅛″ x~                     ⅜″.)''')
assembly(r,'TANK, transmission mechanical lubricator, with lubricator, assembly','56.68')
component(r,'one —       transmission mechanical LUBRICATOR, assembly,')

r=start(247)
pieces(r,'''one SH104G transmission mechanical lubricator cover GASKET,
one SH101H transmission mechanical lubricator drive SHAFT,
one —      transmission mechanical lubricator oil TANK, assembly,
one SH102A transmission mechanical lubricator PULLEY,
one SH102K transmission mechanical lubricator shaft stop COLLAR~                (large),
one SH101F transmission mechanical lubricator shaft stop COLLAR~                (small),
one —      transmission mechanical lubricator sight feed HOOD,~                assembly,
one SH104A transmission mechanical lubricator stuffing box GASKET,
one SH101D transmission mechanical lubricator stuffing box gland~                NUT,
one SH102C transmission mechanical lubricator tank stuffing BOX,
one SH103C transmission mechanical lubricator tank stuffing box~                GLAND,
one SH103D transmission mechanical lubricator WORM,
one —      COCK, drain, ½″, tee handle,
one —      KEY, Woodruff, No. 2,
one —      PIN, taper, type A, No. 0 x ⅝″,
two —      SCREW, machine, round head, No. 8—30 x 3/16″,
twelve —   SCREW, machine, round head, No. 8—30 x 5/16″,
 six —     SCREW, machine, round head, No. 8—30 x ⅜″,
one —      SCREW, set, square head, cup point, ¼″ x ¼″,
one —      SCREW, set, square head, cup point, ¼″ x ⅜″,
one —      SCREW, set, square head, cup point, ¼″ x ⅝″.)''')
assembly(r,'TANK, transmission mechanical lubricator oil, assembly','11.03',note='&')
component(r,'*one M3311    drain cock FLANGE (1)',ord='165',price='.49 P')
component(r,'one M3304    indicator FLANGE,')
component(r,'*two SH558D  oil tank reinforcing PLATE',price='.40')
component(r,'one M3305A  transmission mechanical lubricator oil indicator flange\n                CAP,')
component(r,'*one SH559A  transmission mechanical lubricator oil tank BODY (1)',price='2.15')
component(r,'*one SH558B  transmission mechanical lubricator oil tank BOTTOM (1)',price='.83')
component(r,'*one SH558C  transmission mechanical lubricator oil tank bracket\n                BRACE (1)',price='3.28')
component(r,'*one SH558A  transmission mechanical lubricator oil tank COVER (1)',price='.83')

r=start(248)
entry(r,'TANK, transmission mechanical lubricator oil, assembly—Continued.',note='&');composed(r)
component(r,'*one SH559B transmission mechanical lubricator oil tank reinforcing\n                FRAME, top.)',note='&',price='$1.25')
assembly(r,'TANK, water, assembly','24.03',note='&')
component(r,'one M1195 radiator pipe FLANGE,')
component(r,'*one M1193 water TANK (1)',ident='—',plate='24',ord='175',price='18.00')
component(r,'one M1194 water tank filler pipe FLANGE,')
component(r,'*one M1196 water tank flow pipe flange stiffening PLATE (1)',ord='167',price='.85')
pieces(r,'''one M1231 water tank outlet CONNECTION,
one M1240 water tank outlet pipe GASKET,
eight —    RIVET, button head, 5/16″ x 1″,
 four —    RIVET, button head, 5/16″ x 1⅛″,
three —    RIVET, button head, ⅜″ x 1¼″.)''')
assembly(r,'TAPPET, cam shaft rocker lever, assembly','.39 P',qty='(24)')
component(r,'*one LQ67A cam shaft locker lever TAPPET (24)',mfr='8085',price='.35')
pieces(r,'''one LQ51A NUT, special, S. A. E., 5/16″,
one —     PIN, split, 1/16″ x ⅝″.)''')
append_rows(r,'''%(pf)R|||||Q51DB|TEE, plain, ¼″ pipe thread (M. I.). (For tube C8012 (1).)|3|.04 P
%(pf)R||||||TEE, M. I., beaded, ⅜″ x ⅜″ x ½″. (For regulating tank flexible tube con-~  nection (1).)|1|.07 P
&(pf)R|||||Q51UB|TEE, M. I., beaded, 1″. (For pipe M1229 (1).)|1|.18 P
&|||||B101971A|TEE, soldering, ¼″ brass. (For tube C8013 (2).)|2|.33 P
%X|||||B101963A|TEE, ½″—24 with ⅛″—27 pipe thread. (For tubes C8014A, C8014B, and C8014C.)|3|.40 P
&|—|24|||SH975A|TEE, radiator outlet|1|3.25 P
&(pf)R||||||TEE, reducing, M. I., beaded, ⅜″ x ¼″ x ¼″. (For combination valve to flexible~  tube connection (1).)|1|.04 P
&(pf)R||||||TEE, reducing, M. I., beaded, ½″ x ⅜″ x ¼″. (For combination valve to flexible~  tube connection (1).)|1|.05 P''')

r=add(249,'''&(pf)R||||||TEE, reducing, M. I., beaded, 1″ x ¾″ x 1″. (For pipe M1229 (1).)|1|.09 P
&|||||LQ381A|TERMINAL, battery, negative. (For ignition battery cable, Willard No. Q179).|1|.05 P
&|||||LQ380A|TERMINAL, battery, positive. (For ignition battery cable, Willard No. Q178).|1|.05 P
&(ee)R|||||B7028J|TERMINAL, cable. (For starting motor to starting switch cable (2); starting~  motor to battery negative terminal cover cable (2); starting switch to starting~  battery positive terminal cover cable (2); three ground wires cable (1); starting~  and lighting battery positive terminal cable (1); starting and lighting battery~  negative terminal cable (1).)|11|.08 P
&(ee)R||||||TERMINAL, cable, S. A. E., A5. (For starting battery to fuze box (2); starting~  battery positive to ground (1); 12-volt ammeter to battery, negative (1).)|6|.05 P
(b)&|||D13698|||TERMINAL, distributor head high tension, assembly|24|.08 P
&|||8332||LQ328A|TERMINAL, high-tension cable (distributor end) (seamless tubing, O. D. ⅛″,~  length 1 9/16″. (For cable LQ328A (1); cable LQ360A (1); cable LQ332A (1); cable~  LQ334A (1); cable LQ336A (1); cable LQ338A (1); cable LQ342A (1); cable~  LQ340A (1); cable LQ346A (1); cable LQ344A (1); cable LQ350A (1); cable~  LQ348A (1); cable LQ352A (1); cable LQ354A (1); cable LQ356A (1); cable~  LQ362A (1); cable LQ366A (1); cable LQ364A (1); cable LQ370A (1); cable~  LQ368A (1); cable LQ374A (1); cable LQ372A (1); cable LQ378A (1); cable~  LQ376A (1).)|24|.01 P
&|||8397||LQ329A|TERMINAL, high-tension cable (spark plug end) (½″ x 1 23/32″ snap type.) (For~  cable SH1021N (1); cable SH1021M (1); cable SH102L (1); cable LQ358A (1);~  cable LQ360A (1); cable LQ332A (1); cable LQ334A (1); cable LQ336A (1); cable~  LQ338A (1); cable LQ342A (1); cable LQ340A (1); cable LQ346A (1); cable~  LQ344A (1); cable LQ350A (1); cable LQ348A (1); cable LQ352A (1); cable~  LQ354A (1); cable LQ356A (1); cable LQ362A (1); cable LQ366A (1); cable~  LQ364A (1); cable LQ370A (1); cable LQ368A (1); cable LQ374A (1); cable~  LQ372A (1); cable LQ378A (1); cable LQ376A (1).)|48|.10 P
(ee)R||||||TERMINAL, low-tension cable, with threaded ferrule, 3/16″ hole. (For distribu-~  tor to ignition switch cable, left (2); distributor to ignition switch cable, right (2);~  12-volt regulator cable (1); 8-volt regulator to ground terminal cable (1); 12-volt~  ammeter to battery negative cable (1); 8-volt generator field to 8-volt regulator~  field cable (2); ignition battery positive to ignition switch cable (1); starting bat-~  tery to fuze-box cable (2); fuze box to lighting-switch cable (2); 8-volt generator~  voltage regulator armature terminal to ignition switch (1); lead A266 (2).)|28|.05 P
%(ee)R||||||TERMINAL, low-tension cable, with threaded ferrule, ¼″ hole. (For 8-volt~  generator armature to 8-volt regulator armature cable (2); 8-volt generator volt-~  age regulator armature terminal to ignition switch (1).)|3|.05 P
&|||D30565|||THROWER, distributor shaft oil|2|.45 P''')

r=start(250)
assembly(r,'THROWOUT, clutch, assembly','$78.32',qty='')
pieces(r,'''one SH953C   clutch throwout auxiliary operating SHAFT,
one —        clutch throwout auxiliary ROD, rear, assembly,
four SH943C  clutch throwout ball bearieg WASHER,
two SH943B   clutch throwout bearing retainer WASHER,
one M4153    clutch throwout bell crank carrier PLATE,
one —        clutch throwout bell crank PIN, assembly,
one M4162    clutch throwout LEVER, left,
one M4163    clutch throwout LEVER, right,
five M4172   clutch throwout lever feather KEY,
two —        clutch throwout lever PIN, assembly,
two —        clutch throwout lever pin locking set SCREW, assembly,
one M4164    clutch throwout operating LEVER,
one M4150    clutch throwout SHAFT,
one M4148    clutch throwout shaft BRACKET,
one —        clutch throwout shaft BRACKET, (left), assembly,
one —        clutch throwout stop BAND, assembly,
one —        clutch throwout stop band PIN, assembly,
one SH87A    clutch throwout stop bell CRANK,
one —        clutch throwout stop ROD, assembly,
one —        clutch throwout stop rod EYEBOLT, assembly,
one —        clutch throwout stop rod PIN, assembly,
one SH955C   clutch throwout stop SPRING,
two SH953E   control rod fork END,
two (SH953F) fork end PIN, assembly,
two SKF1207  BEARING, ball, radial, dia. 2.8346″, bore 1.378″, height~                  .6693″,
one —        PIN, split, 5/32″ x 1″,
one —        SCREW, set, square head, cup point, ⅝″ x ⅞″.)''')

r=add(251,'''&|||||SH104D|TOP, transmission mechanical lubricator suction tube screen|6|.06''')
assembly(r,'TRACK, sponson roller, left, assembly','6.06',note='&')
component(r,'*one M1944B sponson roller TRACK, left (1)',ord='522',price='3.15')
component(r,'*one M1946B sponson roller track CLEAT, center, left (1)',ord='522',price='.95')
component(r,'*one M1945B sponson roller track CLEAT, inside, left',ord='522',price='.95')
component(r,'*one M1947   sponson roller track CLEAT, outside (2)',ord='522',price='.95')
component(r,'six —       RIVET, button head, 11/16″ x 2⅜″.)')
assembly(r,'TRACK, sponson roller, right, assembly','6.06 P',note='&')
component(r,'*one M1944A sponson roller TRACK, right (1)',ord='522',price='3.15')
component(r,'*one M1946A sponson roller track CLEAT, center, right (1)',ord='522',price='.95')
component(r,'*one M1945A sponson roller track CLEAT, inside, right (1)',ord='522',price='.95')
component(r,'*one M1947   sponson roller track CLEAT, outside (2)',ord='522',price='.95')
component(r,'six —       RIVET, button head, 11/16″ x 2⅜″.)')
assembly(r,'TRANSMISSION, assembly','3,649.77',note='(gq)&')
pieces(r,'''one MX101 air pressure pump BRACKET, left,
one MX100 air pressure pump BRACKET, right,''')
component(r,'two {Fafnir} BEARING, ball, single thrust, dia. 6.1024″, bore 4.1339″,\n    {1821}   height 1.5748″,')
r[-1]['item_layout']=[dict(text='two',x=31,y=.5,width=16),dict(text='{Fafnir\n 1821 }',x=49,width=34),dict(text='BEARING, ball, single thrust, dia. 6.1024″, bore 4.1339″,\n  height 1.5748″,',x=87,width=160)]
pieces(r,'''four M337   brake band suspension LINK,
two (M363) high speed brake anchor PIN, assembly,
two —      high speed brake BAND, long, assembly,
two —      high speed brake BAND, short, assembly,
four M356   high speed free end brake band PIN,
 six M272   large planet pinion BUSHING, bronze,
 six M283   large planet pinion BUSHING, steel,
two M286    large planet pinion DISK,
 six (M284) large planet pinion PIN, assembly,
two M285    large planet pinion RING,
 six (M318) large planet pinion ring BOLT, assembly,
two M348    low speed brake anchor PIN,
one —       low speed brake BAND, lower half, left, assembly,
one —       low speed brake BAND, lower half, right, assembly,
one —       low speed brake BAND, upper half, left, assembly,
one —       low speed brake BAND, upper half, right, assembly,
eight (M336) low speed free end brake PIN, assembly,
two M339    low speed and track brake suspension PIN, assembly''')

r=start(252)
entry(r,'TRANSMISSION, assembly—Continued.',note='(gq)&');composed(r)
pieces(r,'''six M280     planet PINION, large,
six M270     planet PINION, small,
six M290     retaining RING,
six M282     small planet pinion BUSHING, bronze,
six M271     small planet pinion BUSHING, steel,
six (M274)  small planet pinion PIN, assembly,
two M273     small planet pinion RING,
six (M317)  small planet pinion ring BOLT, assembly,
two (MX12) STUD, ½″ x 3⅞″, threaded U. S. Std. 13/16″ and S. A. E.~                 ⅞″, assembly,
two M353     track brake anchor PIN,
one —        track brake BAND, lower half, left, assembly,
one —        track brake BAND, lower half, right, assembly,
one —        track brake BAND, upper half, left, assembly,
one —        track brake BAND, upper half, right, assembly,
two M292     track brake DRUM,
two —        transmission bevel GEAR, assembly,
one —        transmission bevel gear case COVER, assembly,
fourteen —   transmission bevel gear case cover to case BOLT, assembly,
two M326     transmission bevel gear case GASKET,
two M260     transmission bevel gear SHIM, laminated,''')
component(r,'sixteen M254 transmission bevel gear SHIM,',ord='(gd)')
pieces(r,'''four M332    transmission brake adjusting NUT,
four M335    transmission brake adjusting SPRING,
four SH687A transmission brake adjusting spring SPACER,
four M331    transmission brake adjusting swivel PIN,
 ten MX60    transmission brake anchor bracket and stop SCREW,
four MX76    transmission brake to anchor bracket SCREW.''')

r=start(253)
pieces(r,'''four M333   transmission brake band adjusting SCREW,
twelve MX38 transmission brake band anchor to end SCREW,
 two —      transmission brake band stop BRACKET, assembly,
four —      transmission brake band stop SCREW, assembly,
 two M265   transmission brake bearing BUSHING,
 two —      transmission brake bearing CAP, assembly,
four M330   transmission brake LEVER,
four (MX88) transmission brake stop bar set SCREW, assembly,
 two M291   transmission chain sprocket PINION,
 one M255   transmission cross SHAFT,
 two M256   transmission cross shaft retaining RING,
 two M262   transmission flanged sleeve BUSHING, outer,
 two M310   transmission flanged sleeve outer bushing oil RETAINER,
 one —      transmission FRAME, with brackets and caps, assembly,
 two M278   transmission gear CASE, brake drum half,
 two M277   transmission gear CASE, plain half,
thirty-two — transmission gear case to brake BOLT, assembly,
four M315   transmission gear case GASKET,
 one M311B  transmission gear case oil filling PLUG, bronze,
 two M311A  transmission gear case oil filling PLUG, C. I.,
three M316  transmission (gear case) oil filling plug GASKET,
 two M365   transmission high speed brake band CLIP,
 two M357   transmission high speed brake adjusting NUT,
 two M358   transmission high speed brake adjusting SCREW,
 two M369   transmission high speed brake adjusting SPRING,
 two MX78A transmission high speed brake adjusting spring WASHER,~                I. D. 11/16″,
 two MX78B transmission high speed brake adjusting spring WASHER,~                I. D. 13/16″,
 two M362   transmission high speed brake anchor BRACKET,
 two M366   transmission high speed brake band bottom STOP,
 two M398   transmission high speed brake band STOP,
 two M399   transmission high speed brake band top STOP,
 two M269   transmission high speed brake DRUM,
 two —      transmission high speed brake LEVER, assembly,
 six —      transmission high speed brake stop set SCREW, assembly,
 one —      transmission pinion shaft bearing HOUSING, assembly,
 two M288   transmission planet disk WASHER,
 one M301   transmission shifter FORK,''')

r=start(254)
entry(r,'TRANSMISSION, assembly—Continued.',note='(gq)&');composed(r)
pieces(r,'''one —        transmission shifter fork SHAFT, assembly,
one M257A    transmission shifter GEAR,
one M307     transmission shifter shaft detent PLUNGER,
one M309     transmission shifter shaft plunger CAP,
two —        transmission sprocket bearing BUSHING, inside, assem-~                  bly,
two —        transmission sprocket bearing BUSHING, outside, assem-~                  bly,
two M289     transmission sprocket SHAFT,
two M279     transmission spur RING, large,
two —        transmission spur RING, small, assembly,
two M287     transmission sun PINION, large,
two —        transmission sun PINION, small, assembly,
one —        transmission vertical shifter SHAFT,
two M306     transmission vertical shifter shaft BEARING,
two (MX11)  transmission vertical shifter shaft bearing to bevel-gear case~                  BOLT, assembly,
two Q52PA    COUPLING, pipe, ⅛″,
two —        CUP, grease, No. 0 x ⅛″,
one —        CUP, grease, No. 4 x ½″,
one Q51QD    ELBOW, M. I., 45°, beaded, ½″,
one —        NIPPLE, pipe, W. I., close, ½″ x 1¾″,
two SH671A   PIPE, W. I., ⅛″ x 7″,
one M308     SPRING, wire, O. D. 11/16″, length 1½″,
twelve —     WASHER, lock, ⅜″,
 four —      WASHER, lock, ½″,
  ten —      WASHER, lock, ⅝″.)''')
entry(r,'TRIGGER, hand lever. (For lever M738A (1); lever M738B (1); lever M177 (1).)',note='&',brit='M739',ord='228',qty='3',price='$0.58')

r=add(255,'''&||||M3122|428|TRUNNION, hemispherical turret|6|.72''')
assembly(r,'TUBE, air, combination valve to center gasoline tank, assembly','2.70 P',ident='6',plate='8',ord='SH981C')
pieces(r,'''two B101910A ADAPTER, ½″—14 pipe thread, with ½″—14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″—14 pipe thread,''')
component(r,'*one B101911A flexible metal TUBING, w/braid, ½″ I. D. x 10⅞″.)',price='.80')
assembly(r,'TUBE, air, combination valve to left gasoline tank, assembly','3.50 P',ident='7',plate='8',ord='SH981B')
pieces(r,'''two B101910A ADAPTER, ½″—14 pipe thread, with ½″—14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″—14 pipe thread,''')
component(r,'*one B101911B flexible metal TUBING, w/braid, ½″ I. D. x 25″.)',price='1.60')
assembly(r,'TUBE, air, combination valve to right gasoline tank, assembly','3.95 P',ident='5',plate='8',ord='SH981A')
pieces(r,'''two B101910A ADAPTER, ½″—14 pipe thread, with ½″—14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″—14 pipe thread,''')
component(r,'*one B101911C flexible metal TUBING, w/braid ½″ I. D. x 33¾″.)',price='2.05')
assembly(r,'TUBE, air, combination valve to tee, assembly','2.20 P',ident='15',plate='8',ord='SH981G',qty='(3)')
pieces(r,'''two B101972B ADAPTER, 9/16″—24 S. A. E., with ¼″—18 male pipe~                  thread end,
two B101363A COUPLING, soldering, 9/16″—24 S. A. E.,''')
component(r,'*one B101911L flexible metal TUBING, w/braid, ¼″ I. D. x 25½″.)',price='1.00')
assembly(r,'TUBE, air, gages to hand pressure pump, assembly','5.35 P',ident='17',plate='8',ord='C8013')
pieces(r,'''one B101972A ADAPTER, ½″—24 S. A. E., with ⅛″—27 male pipe~                  thread end,
four B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all (brass),
one Q52PA    pipe COUPLING, ⅛″, WI,
three B101964A soldering COCK, ¼″ (brass),
two B101971A soldering TEE, ¼″ (brass),''')
component(r,'*one B101960A TUBING, copper, ¼″ O. D. x ¾″',price='.05')
component(r,'*one B101960B TUBING, copper, ¼″ O. D. x 2″',price='.05')
component(r,'*one B101960C TUBING, copper, ¼″ O. D. x 4″',price='.05')
component(r,'*one B101960D TUBING, copper, ¼″ O. D. x 11″',price='.10')
component(r,'*one B101960E TUBING, copper, ¼″ O. D. x 12″',price='.15')

r=start(256)
entry(r,'TUBE, air, gages to hand pressure pump, assembly—Continued.',note='%X',ident='17',plate='8');composed(r)
component(r,'*one B101960G TUBING, copper, ¼″ O. D. x 15″',price='$0.20')
component(r,'*one B101960H TUBING, copper, ¼″ O. D. x 18″',price='.24')
component(r,'four B101965B UNION (brass) 29/64″—28.)')
assembly(r,'TUBE, air, pressure pump to regulating tank, assembly','3.90 P',ident='20',plate='8',ord='C8011')
pieces(r,'''two B101972B ADAPTER, 9/16″—24 S. A. E., with ¼″—18 male pipe~                  thread end,
one B101363A COUPLING, soldering, 9/16″—24 S. A. E.,
one B101364A COUPLING, soldering elbow, 9/16″—24 S. A. E. (brass),''')
component(r,'*one B101911P flexible metal TUBING, w/braid, ¼″ I. D. x 88.25″.)',price='2.50')
assembly(r,'TUBE, air, pressure pump to tee, assembly','2.05 P',ident='18',plate='8',ord='SH981E',qty='(2)')
pieces(r,'''two B101972B ADAPTER, 9/16″—24 S. A. E., with ¼″—18 male pipe~                  thread end,
two B101363A COUPLING, soldering, 9/16″—24 S. A. E.,''')
component(r,'*one B101911M flexible metal TUBING, w/braid, ¼″ I. D. x 26.5″.)',price='.85')
assembly(r,'TUBE, air, pressure pump to tee, assembly','2.30',ident='19',plate='8',ord='SH981F')
pieces(r,'''two B101972B ADAPTER, 9/16″—24 S. A. E., with ¼″—18 male pipe~                  thread end,
one B101363A COUPLING, soldering, 9/16″—24 S. A. E.,
one B101364A COUPLING, soldering elbow, 9/16″—24 S. A. E. (brass),''')
component(r,'*one B101911N flexible metal TUBING, w/braid, ¼″ I. D. x 30″ long.)',price='.90')
assembly(r,'TUBE, air, regulating tank to pressure gage, front half, assembly','1.40',ident='21',plate='8',ord='C8016')
component(r,'one B101972A ADAPTER, ½″—24 S. A. E., with ⅛″—27 male pipe\n                  thread end,')
component(r,'*one B101960Q copper TUBING, ¼″ O. D. x 15½″',price='.25')

r=start(257)
pieces(r,'''one Q51CC   ELBOW, plain, ⅛″ pipe (M. I.),
two B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
two B101965B UNION, 29/64″—28.)''')
assembly(r,'TUBE, air, regulating tank to pressure gage, rear half, assembly','',ident='22',plate='8',ord='C8015')
pieces(r,'''one B101972A ADAPTER, ½″—24 S. A. E., with ⅛″—27 male pipe~                  thread end,
one —        air COCK, ¼″ pipe thread,
one B6495X   BUSHING, pipe, ¼″ x ⅛″ (M. I.),
*one B101960S copper TUBING, ¼″ O. D. x 96″,
one B101958A COUPLING, soldering, 29/64″—28,
one Q51EA    CROSS, plain, ¼″ (M. I.),
one B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
one B101964A horizontal check VALVE, ¼″ pipe thread,
one B6498B   NIPPLE, pipe, close, ¼″ x ⅞″,
one B101965B UNION, 29/64″—28.)''')
assembly(r,'TUBE, air, tee to pressure gage, front half, assembly','1.35 P',ident='23',plate='8',ord='C8014A')
component(r,'*one B101960E copper TUBING, ¼″ O. D. x 12″',price='.25')
pieces(r,'''one Q51CC   ELBOW, plain, ⅛″ pipe thread (M. I.),
two B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
one B101963A TEE, ½″—24 with ⅛″—27 pipe thread,
two B101965B UNION, 29/64″—28 (brass).)''')
assembly(r,'TUBE, air, tee to pressure gage, front half, assembly','1.40',ident='24',plate='8',ord='C8014B')
component(r,'*one B101960Q copper TUBING, ¼″ O. D. x 15½″',price='.25')
pieces(r,'''one Q51CC   ELBOW, plain, ⅛″ pipe thread (M. I.),
two B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
one B101963A TEE, ½″—24 with ⅛″—27 pipe thread,
two B101965B UNION, 29/64″—28.)''')
assembly(r,'TUBE, air, tee to pressure gage, front half, assembly','1.45',ident='25',plate='8',ord='C8014C')
component(r,'*one B101960R copper TUBING, ¼″ O. D. x 19″',price='.25')
pieces(r,'''one Q51CC   ELBOW, plain, ⅛″ pipe thread (M. I.),
two B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
one B101963A TEE, ½″—24 with ⅛″—27 pipe thread,
two B101965B UNION, 29/64″—28 (brass).)''')

r=start(258)
assembly(r,'TUBE, air, tee to pressure gage, rear half, assembly','$4.65 P',ident='26',plate='8',ord='C8012',qty='(3)')
pieces(r,'''one B101972A ADAPTER, ½″—24 S. A. E., with ⅛″—27 male pipe~                  thread end,
one B6495X   BUSHING, pipe, ¼″ x ⅛″ (M. I.),''')
component(r,'*one B101960P copper TUBING, ¼″ O. D. x 132″',price='1.32')
pieces(r,'''one B101958A COUPLING, soldering, 29/64″—28,
one B101966B GLAND, soldering, 5/16″ O. D. x ½″ over all,
one B6498QA NIPPLE, short, ¼″ x 1½″ (G. I.),
one Q51DB    TEE, plain, ¼″ pipe thread (M. I.),
one B101965B UNION, 29/64—28,
one B101941A vertical check VALVE, ¼″ pipe thread.)''')
assembly(r,'TUBE, crank case drain, assembly','1.90 P',note='&',ident='—',plate='34')
component(r,'*one LQ209A crank case drain TUBE (1)',mfr='8217',price='1.40')
component(r,'*one LQ210A crank case drain tube CUP (1)',mfr='8394',price='.25')
component(r,'*one LQ211A crank case drain tube FLANGE (1).)',mfr='8212',price='.25')
assembly(r,'TUBE, crank case to cam shaft housing oil, assembly','.30 P',qty='(2)')
component(r,'*one LQ461A crank case to cam shaft housing oil TUBE (2)',mfr='L8460',price='.10')
pieces(r,'''two LQ463A CONE, male union,
two LQ462A NUT, tube union, ¼″.)''')
assembly(r,'TUBE, engine to oil gage, assembly','1.34 P',ord='B101992A')
component(r,'two A16323   COLLET, pipe, ¼″,')
component(r,'*one B101960M seamless copper TUBING, ¼″, length 116″ (1)',price='.84')
component(r,'two B101965C UNION, brass, 7/16″—20-NF2A.)')
append_rows(r,'''&||||M3307|165|TUBE, engine oil tank indicator float|1|1.42 P
%X|||||SH207A|TUBE, engine oil tank return (armored flexible brass tubing, ¾″, length 42″)|1|6.70 P
%X|||||SH207B|TUBE, engine oil tank suction (armored flexible brass tubing, ¾″, length 66″)|1|7.30 P''')

r=add(259,'''&|8|20||M1128|196|TUBE, fan bevel gear box long distance|1|.18
&|9|20||M1127|196|TUBE, fan bevel gear box short distance|1|.12''')
assembly(r,'TUBE, gasoline, center tank to combination valve, assembly','3.00 P',ident='3',plate='8',ord='SH984B')
pieces(r,'''two B101910A ADAPTER, ½″-14 pipe thread, with ½″-14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″-14 pipe thread,''')
component(r,'*one B101911E flexible metal TUBING, w/braid, ½″ I. D. x 14–½″.)',price='1.10')
assembly(r,'TUBE, gasoline, combination valve to regulating tank, assembly','7.65 P',ident='10',plate='8',ord='SH984D')
pieces(r,'''two B101910A ADAPTER, ½″-14 pipe thread, with ½″-14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″-14 pipe thread,''')
component(r,'*one B101911G flexible metal TUBING, w/braid, ½″ I. D. x 81″.)',price='5.75')
assembly(r,'TUBE, gasoline, left tank to combination valve, assembly','4.00 P',ident='4',plate='8',ord='SH984C')
pieces(r,'''two B101910A ADAPTER, ½″-14 pipe thread, with ½″-14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″-14 pipe thread,''')
component(r,'*one B101911F flexible metal TUBING, w/braid, ½″ I. D. x 27″.)',price='2.10')
assembly(r,'TUBE, gasoline, regulating tank to front carburetor, assembly','1.75',ident='8',plate='8',ord='SH984F')
pieces(r,'''two B101972B ADAPTER, 9/16″-24 S. A. E., with ¼″-18 male pipe~                  thread end,
two B101363A COUPLING, soldering, 9/16″-24 S. A. E.,''')
component(r,'*one B101911R flexible metal TUBING, w/braid, ¼″ I. D. x 15–¼″.)',price='.55')
assembly(r,'TUBE, gasoline, regulating tank to rear carburetor, assembly','2.15',ident='9',plate='8',ord='SH984E')
pieces(r,'''two B101972B ADAPTER, 9/16″-24 S. A. E., with ¼″-18 male pipe~                  thread end,
one B101363A COUPLING, soldering, 9/16″-24 S. A. E.,
one B101364A COUPLING, soldering elbow, 9/16″-24 S. A. E.,''')
component(r,'*one B101911Q flexible metal TUBING, w/braid, ¼″ I. D. x 20–½″.)',price='.75')
assembly(r,'TUBE, gasoline, right tank to combination valve, assembly','2.80 P',ident='2',plate='8',ord='SH984A')
pieces(r,'''two B101910A ADAPTER, ½″-14 pipe thread, with ½″-14 male pipe~                  thread end,
two B5932C   COUPLING, soldering, ½″-14 pipe thread,''')
component(r,'*one B101911D flexible metal TUBING, w/braid, ½″ I. D. x 11″.)',price='.90')

r=start(260)
assembly(r,'TUBE, high tension cable, with cables, assembly','$23.10 P')
for number in range(1,7):
 for side in ['left','right']:
  label='distributing' if number==1 and side=='left' else 'distributor'
  component(r,f'one —      high tension CABLE, ({label} left) to spark plug #{number},\n                 {side}, assembly,')
for side in ['left','right']:
 component(r,f'one —      high tension CABLE, (distributor right) to spark plug #1,\n                 {side}, assembly,')

r=start(261)
for number in range(2,7):
 for side in ['left','right']:
  component(r,f'one —      high tension CABLE, (distributor right) to spark plug #{number},\n                 {side}, assembly,')
pieces(r,'''two LQ327A high tension cable SEPARATOR,
one (LQ324A) high tension cable TUBE, assembly,
six LQ325A high tension cable tube CLIP.)''')
assembly(r,'TUBE, high tension cable, assembly','7.86 P',note='&')
component(r,'*one LQ324A high tension cable TUBE (1)',price='6.98')
component(r,'*two LQ326A high tension cable tube END (2)',price='.05')
component(r,'*twenty-six —      FERRULE, steel, approx. ½″.)',price='.03')
append_rows(r,'''&|||||SH234F|TUBE, jockey pulley distance|1|.42 P
&|||||SH234E|TUBE, jockey pulley long distance|1|.78 P
&|||||SH234D|TUBE, jockey pulley short distance|1|.22 P
&|35|141|B12039||LQ186A|TUBE, lower crank case oil pump suction|1|2.50 P''')
assembly(r,'TUBE, oil, assembly. (From mechanical lubricator to left outer sprocket bearing\n  (1); mechanical lubricator to left roller pinion shaft (1).)','4.57 P',note='',ord='B101982E',qty='(2)')
component(r,'one A16309    ADAPTER, elbow, 7/16″–22-NPS, with ⅛″–27 NPT,')
component(r,'*one B101976E armor TUBING, 5/16″ I. D. x 135½″ (2)',price='2.83')
component(r,'one A16323    COLLET, pipe, ¼″,')
component(r,'*one B101960U seamless copper TUBING, ¼″ O. D. x 137″ (2)',price='1.37')
component(r,'one SH102E    UNION, brass, 7/16″–22.)')

r=start(262)
assembly(r,'TUBE, oil, mechanical lubricator to left inner sprocket bearing, assembly','$4.09 P',note='',ord='B101982D')
component(r,'one A16309    ADAPTER, elbow, 7/16″–22-NPS, with ⅛″–27 NPT,')
component(r,'*one B101976D armor TUBING, 5/16″ I. D. x 120½″ (1)',price='2.50')
component(r,'one A16323    COLLET, pipe, ¼″,')
component(r,'*one B101960T seamless copper TUBING, ¼″ O. D. x 122″ (1)',price='1.22')
component(r,'one SH102E    UNION, brass, 7/16″–22.)')
assembly(r,'TUBE, oil, mechanical lubricator to right inner sprocket bearing, assembly','1.58 P',note='',ord='B101982B')
component(r,'one A16309    ADAPTER, elbow, 7/16″–22-NPS, with ⅛″–27 NPT,')
component(r,'*one B101976B armor TUBING, 5/16″ I. D. x 38½″',qty='(1)',price='.81')
component(r,'one A16323    COLLET, pipe, ¼″,')
component(r,'*one B101960X seamless copper TUBING, ¼″ O. D. x 40″ (1)',price='.40')
component(r,'one SH102E    UNION, brass, 7/16″–22.)')
assembly(r,'TUBE, oil, mechanical lubricator to right outer sprocket bearing, assembly','1.27 P',note='',ord='B101982A')
component(r,'one A16309    ADAPTER, elbow, 7/16″–22-NPS with ⅛″–27-NPT,')
component(r,'*one B101976A armor TUBING, 5/16″ I. D. x 28½″',qty='(1)',price='.60')
component(r,'one A16323    COLLET, pipe, ¼″,')
component(r,'*one B101960W seamless copper TUBING, ¼″ O. D. x 30″ (1)',price='.30')
component(r,'one SH102E    UNION, brass, 7/16″–22.)')
assembly(r,'TUBE, oil, mechanical lubricator to right roller pinion shaft, assembly','2.66 P',note='',ord='B101982C')
component(r,'one A16309    ADAPTER, elbow, 7/16″–22-NPS, with ⅛″–27-NPT,')
component(r,'*one B101976C armor TUBING, 5/16″ I. D. x 73½″',qty='(1)',price='1.54')
component(r,'one A16323    COLLET, pipe, ¼″,')
component(r,'*one B101960K seamless copper TUBING, ¼″ O. D. x 75″ (1)',price='.75')
component(r,'one SH102E    UNION, brass, 7/16″–22.)')
append_rows(r,'''&|||||SH607C|TUBE, radiator|606|.37 P
X|||||SH281D|TUBE, radiator cooling fan drive distance|1|1.28 P''')

r=add(263,'''&||||X247|802|TUBE, semaphore handle, long|1|.06
&||||X272|802|TUBE, semaphore handle, short|1|.09
%X|||||SH922C|TUBE, terminal cover (fiber, 1⅜″, length, 4½″)|3|.20 P
&|||||SH104F|TUBE, transmission mechanical lubricator sight feed|6|.08 P
&|||||SH101B|TUBE, transmission mechanical lubricator suction|6|.12 P
&|55|2|A37/21191||551|TUBE, 6-pdr. shell (shell storage, rear)|182|1.05
&|||B37/21191||551|TUBE, 6-pdr. shell expansion|182|.48
&|||C37/21191||267|TUBE, 6-pdr. shrapnel (rear of left pedestal (7); right (7); side of left pedestal (6);~  right (6).)|26|1.25
&||||M3817|266|TUBE, 6-pdr. shrapnel expansion (rear of left pedestal (7); right (7); side of left~  pedestal (6); side of right pedestal (6).)|26|.78
(mh)X||||||TUBING, armor, 5/16″ I. D., ft. (Penflex type) (1 piece 28½″ long required for tube~  B101982A; 1 piece 38½″ long required for tube B101982B; piece 73½″ long re-~  quired for tube B101982C; 1 piece 135½″ long required for tube B101982E; 1 piece~  120½″ long required for tube B101982D)|—|.25 P
(mh)X||||||TUBING, armor flexible, brass, ¾″, ft. (Titeflex type) (1 piece 42″ long re-~  quired for tube SH207A; one piece 66″ long required for tube SH207B)|—|1.20 P
(mh)X|||||—|TUBING, metal, flexible, with braid, ¼″ I. D., ft. (Titeflex type) (1 piece 88¼″~  long required for tube C8011; 2 pieces 26½″ long required for tube SH981E;~  1 piece 30″ long required for tube SH981F; 3 pieces 25½″ long required for tube~  SH981G; 1 piece 20½″ long required for tube SH984E; 1 piece 15¼″ long required~  for tube SH984F)|—|.35 P
(mh)X|||||—|TUBING, metal, flexible, with braid, ½″ I. D., ft. (Titeflex type) (1 piece 10⅞″~  long required for tube SH981C; 1 piece 25″ long required for tube SH981B; 1 piece~  33¾″ long required for tube SH981A; one piece 11″ long required for tube SH984A;~  1 piece 14½″ long required for tube SH984B; 1 piece 27″ long required for tube~  SH984C; 1 piece 81″ long required for tube SH984D)|—|.85 P
(mh)X||||||TUBING, seamless copper, ¼″, ft. (3 pieces 132″ long required for tube C8012;~  1 piece 15½″ long required for tube C8016; 1 piece 12″ long required for tube~  C8014A; 1 piece 19″ long required for tube C8014C; 1 piece 96″ long required for tube~  C8015; 1 piece 15½″ long required for tube C8014B; pieces ¾″, 2″, 4″, 11″, 12″,~  15″ and 18″ long required for tube C8013; 2 pieces 16⅞″ long required for crank~  case to camshaft housing oil tube (LQ461A); 1 piece 30″ long required for tube~  B101982A; 1 piece 40″ long required for tube B101982B; 1 piece 122″ long required~  for tube B101982D; 1 piece 75″ long required for tube B101982C; 1 piece 137″ long~  required for tube B101982E; 1 piece 116″ long required for tube B101992A).|—|.30 P''')

r=start(264)
assembly(r,'TURRET, hemispherical, assembly','$97.78',note='',ident='41',plate='2',qty='(3)')
component(r,'one B40B    ball mount FLANGE, inner,',ord='15–1K–40')
component(r,'one B40A    ball mount FLANGE, outer,',ord='15–1K–40')
component(r,'one D/20793 (ball mount) splash RING,')
component(r,'*one M3117   hemispherical TURRET (3)',ord='430',price='75.00')
pieces(r,'''six SH428A  hemispherical turret SCREW,
one M3127   locking SCREW,
six —       SCREW, cap, U. S. Std., hexagon head, ½″ x ⅞″,
six —       WASHER, lock, ½″.)''')
assembly(r,'TURRET, outlook, (Officer’s), assembly','180.78',note='(gm)&',ident='44\n4',plate='2\n9')
r[-2].update(space_before=.5,space_after=.5,cell_baseline_offsets={'ident':-.5,'plate':-.5})
component(r,'*one M2370A outlook turret bottom ANGLE, front (1)',ord='437',price='.78')
component(r,'*one M2370B outlook turret bottom ANGLE, rear (1)',ident='2',plate='10',ord='437',price='.78')
component(r,'two M2371   outlook turret bottom ANGLE, side,')
component(r,'*two M2347  outlook turret PLATE, front and rear (2)',ord='436',price='44.09')
component(r,'*two M2346  outlook turret PLATE, side (2)',ord='436',price='40.38')
component(r,'*two M2367  outlook turret top ANGLE, front and rear (2)',ord='436',price='.58')
component(r,'*two M2368  outlook turret top ANGLE, side (2)',ord='436',price='.72')
component(r,'*two M2369A outlook turret vertical ANGLE, left rear or right front (2)',ord='436',price='.48')
component(r,'*two M2369B outlook turret vertical ANGLE, right rear or left front (2)',ord='436',price='.48')
component(r,'*four M2845   peep hole splash PLATE (4)',ord='437',price='.86')
pieces(r,'''fifty —       RIVET, button head, 7/16″ x 1⅜″,
eighteen —    RIVET, button head, 7/16″ x 1½″.)''')
assembly(r,'UNILET, type LL, 1½″ (Appleton Electric Co. type), assembly','1.00 P',note='(ee)&')
component(r,'*one — UNILET, type LL, 1½″ (1)',price='.80')
pieces(r,'''one — unilet COVER, 2 hole,
two — SCREW, machine, round head, brass, No. 10—32 x ⅜″.~           For conduit A8403 (1).)''')
