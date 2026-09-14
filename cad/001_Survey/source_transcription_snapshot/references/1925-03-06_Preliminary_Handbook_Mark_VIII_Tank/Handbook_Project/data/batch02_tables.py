"""Explicit, source-checked specification and plate-reference tables, pages 21–40."""
GASOLINE_SPECS=[
('Total gasoline capacity','240 gallons.'),('Number of tanks','3.'),('Capacity per tank','80 gallons.'),
('Size of pipe to carburetor','¼-inch.'),('Other gasoline piping','½-inch.'),('Type of feed','Pressure.'),
('Type of pump','Reciprocating.'),('Pressure on system','2 to 4 pounds.')]
HULL_SPECS=[
('Length','34 feet 2½ inches.'),('Thickness of side plates','12 mm.'),
('Thickness of backplates, rear of gasoline (petrol) tank','16 mm.'),('Thickness of front wing plates','10 mm.'),
('Outside skirting plate','10 mm.'),('Thickness of front diaphragm plate','12 mm.'),
('Thickness of main turret side plates','16 mm.'),('Thickness of main turret top plates','6 mm.'),
('Thickness driver’s turret plates','6 mm.'),('Thickness of hemispherical turrets in doors and main turret','14 mm.'),
('Thickness of lookout turret plating, top','6 mm.'),('Thickness of lookout plating, side','16 mm.'),
('Thickness of sponson floor plates','8 mm.'),('Thickness of sponson roof plates','6 mm.'),
('Thickness of sponson top shield','8 mm.'),('Thickness of sponson bottom shield','8 mm.'),
('Thickness of sponson side plates','12 mm.'),('Thickness of sponson floor plates, forward','12 mm.'),
('Thickness of sponson floor plates, aft','6 mm.'),('Thickness of roof plate abaft turret','6 mm.'),
('Thickness of roof plate over engine','6 mm.'),('Thickness of roof plate over petrol, gasoline tank','10 mm.'),
('Thickness of roof plate over driver','6 mm.'),('Thickness of doors','12 mm.'),
('Length of main turret, over all','10 feet 3½ inches.'),('Width of main turret, over all','3 feet 4½ inches.'),
('Height of main turret, without outlook turret','1 foot 10½ inches.'),('Length of driver’s turret','2 feet 3 inches.'),
('Width of driver’s turret','1 foot 7 inches.'),('Height of driver’s turret','1 foot 1 inch.'),
('Height of lookout turret above main turret','12½ inches.'),('Inside length of lookout turret','18 inches.'),
('Inside width of observer’s turret','18 inches.')]
# Two columns of (reference, part number, description); '\n' retains source wrap.
PARTS={
29:[
[('1','SH900B','Air-pressure pump pulley.'),('2','SH900A','Air-pressure pump bushing.'),('3','SH900C','Air-pressure pump cylinder.'),('4','SH900D','Air-pressure pump shaft.'),('5','SH903A','Air-pressure pump base.')],
[('6','SH901E','Air-pressure pump displacement\nplug.'),('7','SH901A','Air-pressure pump spring.'),('8','SH901D','Air-pressure pump piston.')]],
30:[
[('1','SH950C','Float.'),('2','SH950A','Tank.'),('3','SH950F','Float rod.'),('4','SH950G','Pin for valve bracket.'),('5','SH950B','Valve bracket.')],
[('6','SH950E','Valve.'),('7','SH950H','Valve bracket holder and gas inlet'),('8','SH950D','Air-pipe connection.'),('9','SH972A','Regulating tank support.')]],
31:[[[ '1','M-1764','Combination tap plug.']],[[ '2','M-1763','Combination tap body.']]],
33:[[('1','M-1755','Petrol tank.'),('2','M-1785','Port cover for petrol tank.'),('3','M-1786','Starboard cover for petrol tank.'),('4','M-984 A B & C','Petrol tubes from tank to combination tap.'),('5','M-981 A B & C','Air-pressure tubes tank to combination tap.'),('6','','Filling cap.')]],
39:[
[('1','M-1264','Road track.'),('2','M-2630','Revolver port cover.'),('3','','Peephole.'),('4','M-2380','Outlook turret.'),('5','M-3120','Cover plate for hemispherical turret.')],
[('6','M-2355','Main turret roof doorplate, starboard'),('7','M-2356','Main turret roof doorplate, port.'),('8','M-3922','Roof towing bracket.'),('9','M-2440','Camouflage net support socket.')]]}
