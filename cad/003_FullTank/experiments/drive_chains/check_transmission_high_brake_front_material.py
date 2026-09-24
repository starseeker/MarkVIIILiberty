"""Check bounded material changes, lining support and remaining case bridge stock.

Read saved BReps and occurrence frames; do not invoke a geometry builder. The
steel-head recesses and small axial lining overhangs are explicit exceptions,
not evidence of complete face contact. Negative controls exercise support tests.
"""
import argparse,math,sys
from pathlib import Path
import FreeCAD as App
import Part
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path.insert(0,str(H.parents[1]))
from lib.evidence import read,write,sha
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args();out=a.candidate.resolve()
r=read(out/'report.json');m=read(out/'isolated/manifest.json');source=ROOT/r['source_native'];old=read(source.parent/'isolated/manifest.json')
assert sha(out/r['native_file'])==r['native_sha256']==m['native_sha256']
assert sha(source)==r['source_native_sha256']==old['native_sha256']
assert all(sha(ROOT/f)==v for f,v in r['input_hashes'].items())
rows={v['name']:v for v in m['occurrences']};checks=[];cache={};V=App.Vector;c=r['controls'];bc=r['band_controls']
def ck(name,passed,**details):
 checks.append(dict(name=name,passed=bool(passed),**details));write(out/'material_check_progress.json',checks);print(name,bool(passed),flush=True)
def empty(s):return s.isValid() and not s.Faces and abs(s.Volume)<1e-5
def definition(key,previous=False):
 rec=(old if previous else m)['definitions'][key];digest=rec['brep_sha256']
 if digest not in cache:
  assert sha(rec['brep_path'])==digest;s=Part.Shape();s.read(rec['brep_path']);assert s.Placement.isIdentity();cache[digest]=s
 return cache[digest].copy()
def pose(name):return App.Placement(App.Matrix(*rows[name]['frame']))
def world(name):
 s=definition(rows[name]['definition']);s.Placement=pose(name);return s
def cylinder(radius,height,placement,z=0):
 s=Part.makeCylinder(radius,height,V(0,0,z));s.Placement=placement;return s
def remaining(shape,tools):return shape.cut(Part.makeCompound(tools)) if shape.Faces else shape
def cylindrical(s,radius):return [f for f in s.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-6]
def coverage(wanted,support,exceptions=()):
 records=[]
 for f in wanted:
  matching=[g for g in support if abs(f.Surface.Radius-g.Surface.Radius)<1e-6 and f.Surface.Axis.cross(g.Surface.Axis).Length<1e-7 and (f.Surface.Center-g.Surface.Center).cross(g.Surface.Axis).Length<1e-6]
  missing=f.cut(Part.makeCompound(matching)) if matching else f.copy();area=missing.Area
  rest=remaining(missing,exceptions) if exceptions else missing
  records.append(dict(passed=rest.isValid() and not rest.Faces and abs(rest.Area)<1e-5,uncovered_area_mm2=area,unexplained_faces=len(rest.Faces),unexplained_area_mm2=rest.Area))
 return bool(records) and all(v['passed'] for v in records),records

# Backing may lose only the three steel bores/countersinks and the specified
# normal copper-tail spotfaces. No added stock or changed outline is allowed.
for role in ['Long','Short']:
 name='PortHighSpeedBrake'+role+'Band';key=rows[name]['definition'];before=definition(key,True);after=definition(key);inv=pose(name).inverse();tools=[]
 for i in range(1,4):
  placement=inv.multiply(pose('PortHighSpeedBrake'+role+'FrontSteelRivet'+str(i)))
  slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2));hole=c['steel_shank_diameter']/2+c['steel_hole_clearance']
  depth=(c['steel_head_radius']-hole)/slope
  tool=Part.makeCylinder(hole,50,V(0,0,-5)).fuse(Part.makeCone(c['steel_head_radius']+5*slope,hole,depth+5,V(0,0,-5)));tool.Placement=placement;tools.append(tool)
 for n,row in rows.items():
  if not n.startswith('PortHighSpeedBrake'+role+'LiningFastener') or 'lining_normal_' not in row['definition']:continue
  grip=bc['lining_stock']+bc['steel_stock']-c['lining_head_recess']-c['lining_tail_spotface']
  tools.append(cylinder(c['lining_tail_radius']+.05,15,inv.multiply(pose(n)),grip))
 removed=before.cut(after);extra=after.cut(before);rest=remaining(removed,tools)
 ck(role+' backing changes confined to fastener recesses',empty(extra) and empty(rest),removed_mm3=removed.Volume,extra_faces=len(extra.Faces),unexplained_faces=len(rest.Faces))

# The enlarged rear anchor receives one longer copper rivet. Check both change
# directions against separate bounded witnesses and retain its old eye/coupling.
key='Def_HighBrake_anchor_end';before=definition(key,True);after=definition(key);outer=bc['inner_radius']+bc['lining_stock']+bc['steel_stock'];ro=outer+r['rear_controls']['anchor_outer_stock']
start=math.radians(r['rear_controls']['anchor_end_deg']);end=math.radians(c['rear_anchor_end_deg']);y=-bc['width']/2
def pt(rad,theta):return V(rad*math.cos(theta),y,rad*math.sin(theta))
edges=[Part.Arc(pt(outer,start),pt(outer,(start+end)/2),pt(outer,end)).toShape(),Part.makeLine(pt(outer,end),pt(ro,end)),Part.Arc(pt(ro,end),pt(ro,(start+end)/2),pt(ro,start)).toShape(),Part.makeLine(pt(ro,start),pt(outer,start))]
extension=Part.Face(Part.Wire(edges)).extrude(V(0,bc['width'],0))
inv=pose('PortHighSpeedBrakeAnchorEnd').inverse();placement=inv.multiply(pose('PortHighSpeedBrakeShortLiningFastener1'))
grip=bc['lining_stock']+bc['steel_stock']+r['rear_controls']['anchor_outer_stock']-c['lining_head_recess']-c['lining_tail_spotface']
holes=[cylinder(bc['steel_hole_radius'],40,placement,-1),cylinder(c['lining_tail_radius']+.05,15,placement,grip)]
removed=before.cut(after);added=after.cut(before)
ck('M361 extension and rivet recess are the only material changes',empty(remaining(removed,holes)) and empty(remaining(added,[extension])),added_mm3=added.Volume,removed_mm3=removed.Volume)
ck('M361 complete extension stock outside rivet recess retained',empty(remaining(extension.cut(after),holes)))

# Independent recreation of the allowed case envelopes from actual brake/case
# frames. Material outside these envelopes must remain exactly where it was.
case_name='CenterTransmissionCore_bevel_case';key=rows[case_name]['definition'];before=definition(key,True);after=definition(key);inv=pose(case_name).inverse();tools=[]
for hand in ['Port','Starboard']:
 center=inv.multVec(pose(hand+'HighSpeedBrakeLongBand').Base);width=bc['width']+2*c['case_axial_margin'];low=center.y-width/2
 envelope=Part.makeCylinder(c['case_clearance_radius'],width,V(center.x,low,center.z),V(0,1,0))
 window=Part.makeBox(c['case_relief_x_max']-c['case_relief_x_min'],width,2*c['case_relief_half_height'],V(c['case_relief_x_min'],low,-c['case_relief_half_height']))
 tool=envelope.common(window);tools.append(tool)
 ck(hand+' continuous case clearance envelope empty',empty(after.common(tool)))
 ck(hand+' former bridge fails new hardware clearance',before.common(tool).Volume>1)
 # A continuous 15.98mm witness spans the unchanged bridge root to its bearing
 # saddle. The 0.01mm edge inset avoids coincident-face topology ambiguity.
 ymin,ymax=(110.01,308.9285714285715) if hand=='Port' else (-308.9285714285715,-110.01)
 witness=Part.makeBox(15.98,ymax-ymin,71.98,V(-223.99,ymin,-35.99))
 ck(hand+' continuous minimum bridge stock retained',empty(witness.cut(after)),witness_stock_mm=15.98,structural_strength_qualified=False)
 removed=before.cut(after);added=after.cut(before)
ck('Case changes only remove the two bounded bridge recesses',empty(added) and empty(remaining(removed,tools)),removed_mm3=removed.Volume,extra_faces=len(added.Faces))
ck('Case remains one connected closed solid',after.isValid() and len(after.Solids)==1 and after.Solids[0].isClosed())

# Entire lining surfaces are checked, not a few point samples. Explicit
# countersunk steel-head pockets interrupt the backing contact locally.
support_records=[]
for hand in ['Port','Starboard']:
 drum=world(hand+'TransmissionCore_high_drum');df=cylindrical(drum,190.5);bb=Part.makeCompound(df).BoundBox
 clip=Part.makeBox(1000,bb.YLength,1000,V(bb.XMin-300,bb.YMin,bb.ZMin-300))
 for role in ['Long','Short']:
  prefix=hand+'HighSpeedBrake'+role;lining=world(prefix+'Lining');band=world(prefix+'Band');exceptions=[]
  for i in range(1,4):
   slope=math.tan(math.radians(c['steel_countersink_angle_deg']/2));hole=c['steel_shank_diameter']/2+c['steel_hole_clearance'];depth=(c['steel_head_radius']-hole)/slope
   pocket=Part.makeCone(c['steel_head_radius']+5*slope,hole,depth+5,V(0,0,-5));pocket.Placement=pose(prefix+'FrontSteelRivet'+str(i));exceptions.append(pocket)
  ok,records=coverage(cylindrical(lining,196.85),cylindrical(band,196.85),exceptions)
  ck(prefix+' entire backing contact outside steel-head recesses',ok,coverage=records)
  moved=band.copy();moved.translate(V(.05,0,0));negative,_=coverage(cylindrical(lining,196.85),cylindrical(moved,196.85),exceptions)
  ck(prefix+' displaced backing loses contact',not negative)
  faces=cylindrical(Part.makeCompound(cylindrical(lining,190.5)).common(clip),190.5);ok,records=coverage(faces,df)
  width=Part.makeCompound(cylindrical(lining,190.5)).BoundBox.YLength;ratio=bb.YLength/width
  ck(prefix+' entire drum-width friction surface supported',ok and .97<ratio<=1,axial_coverage_fraction=ratio,overhang_per_edge_mm=(width-bb.YLength)/2,coverage=records)
  moved=drum.copy();moved.translate(V(.05,0,0));negative,_=coverage(faces,cylindrical(moved,190.5));ck(prefix+' displaced drum loses contact',not negative)
  support_records.append(dict(name=prefix,axial_coverage_fraction=ratio,backing_pockets='Three bounded recessed steel heads; complete contact is not claimed inside those pockets.'))
result=dict(passed=all(v['passed'] for v in checks),native_sha256=r['native_sha256'],checker_sha256=sha(Path(__file__)),checks=checks,support=support_records,scope='Bounded material changes, remaining case bridge and full lining faces with explicit countersink/axial-overhang exceptions. No historical casting or structural-strength qualification.')
write(out/'material_checks.json',result)
assert result['passed'],[v['name'] for v in checks if not v['passed']]
