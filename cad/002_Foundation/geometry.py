"""Native part features and hierarchy. All tank geometry comes from authored records."""
import json
from pathlib import Path

import FreeCAD as App
import Part
import Sketcher
import _PartDesign
import AssemblyApp

from calibration import point
from evidence import CONFIG, arithmetic, write


def metadata(obj, pid, status, evidence, reference=False, notes=''):
    for key, value in [('SurveyId', pid or ''), ('Configuration', CONFIG), ('EvidenceStatus', status),
                       ('EvidenceReferences', json.dumps(evidence)), ('ReconstructionNotes', notes)]:
        obj.addProperty('App::PropertyString', key, 'Evidence')
        setattr(obj, key, value)
    obj.addProperty('App::PropertyBool', 'ReferenceOnly', 'Evidence')
    obj.ReferenceOnly = reference


def appearance(obj, reference=False):
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = (0.63, 0.73, 0.8) if reference else (0.48, 0.48, 0.4)
        obj.ViewObject.LineColor = (0.15, 0.18, 0.2)
        obj.ViewObject.Transparency = 75 if reference else 0


def polygon_sketch(body, name, points, placement=None):
    sketch = body.newObject('Sketcher::SketchObject', name)
    if placement:
        sketch.Placement = placement
    for i, (x, y) in enumerate(points):
        q = points[(i + 1) % len(points)]
        n = sketch.addGeometry(Part.LineSegment(App.Vector(x, y, 0), App.Vector(q[0], q[1], 0)), False)
        sketch.addConstraint(Sketcher.Constraint('Block', n))
    return sketch


def pad(body, name, sketch, length):
    feature = body.newObject('PartDesign::Pad', name)
    feature.Profile = sketch
    feature.Length = length
    body.Document.recompute()
    if sketch.ViewObject:
        sketch.ViewObject.Visibility = False
    return feature


def revolve(body, points):
    sketch = polygon_sketch(body, 'RadialSection', points)
    feature = body.newObject('PartDesign::Revolution', 'Revolve')
    feature.Profile = sketch
    feature.ReferenceAxis = (sketch, ['V_Axis'])
    feature.Angle = 360
    body.Document.recompute()
    if sketch.ViewObject:
        sketch.ViewObject.Visibility = False
    return feature


def along_y(y):
    return App.Placement(App.Vector(0, y, 0), App.Rotation(App.Vector(1, 0, 0), -90))


def annulus(body, name, ro, ri, y, length):
    s = body.newObject('Sketcher::SketchObject', name + 'Profile')
    s.Placement = along_y(y)
    for r in [ro] + ([ri] if ri else []):
        n = s.addGeometry(Part.Circle(App.Vector(), App.Vector(0, 0, 1), r), False)
        s.addConstraint(Sketcher.Constraint('Coincident', n, 3, -1, 1))
        s.addConstraint(Sketcher.Constraint('Radius', n, r))
    return pad(body, name, s, length)


def joint_holes(body, feature, v):
    # Sketch normal +Y; a pocket cuts back from front to rear through the vertical leg/plate.
    y = v['angle_thickness'] if body.Name == 'support_angle' else 0
    s = body.newObject('Sketcher::SketchObject', 'HoleLocations')
    s.Placement = along_y(y)
    for x in [-v['joint_hole_offset'], v['joint_hole_offset']]:
        n = s.addGeometry(Part.Circle(App.Vector(x, -v['angle_leg']/2, 0), App.Vector(0, 0, 1), v['joint_hole_diameter']/2), False)
        s.addConstraint(Sketcher.Constraint('Block', n))
    pocket = body.newObject('PartDesign::Pocket', 'JointHoles')
    pocket.Profile = s
    pocket.Length = v['angle_thickness'] if body.Name == 'support_angle' else v['plate_thickness']
    body.Document.recompute()
    if s.ViewObject:
        s.ViewObject.Visibility = False
        feature.ViewObject.Visibility = False
    return pocket


def make_part(key, spec, data, folder):
    v = data['values']
    doc = App.newDocument('Part_' + key)
    body = doc.addObject('PartDesign::Body', key)
    body.Label = key.replace('_', ' ').title()
    refs = sorted({r for k in spec['parameters'] for r in data['parameters'][k]['evidence']})
    metadata(body, spec['survey_id'], spec['status'], refs, notes=spec['notes'])
    parameters = doc.addObject('App::FeaturePython', 'Parameters')
    parameters.Label = 'Source parameters — scripts remain authoritative'
    for key_p in spec['parameters']:
        parameters.addProperty('App::PropertyLength', key_p, 'SourceParameters')
        setattr(parameters, key_p, v[key_p])
    builder = spec['builder']
    if builder == 'shoe':
        h = v['shoe_pitch']/2
        a, b, t, rise = v['shoe_lip_extension'], v['shoe_ramp_run'], v['shoe_thickness'], v['shoe_lift']
        # Sketch coordinates X and -Z because the normal points along +Y.
        points = [(-h-a, 0), (-h+a, 0), (-h+b, -rise), (h+a, -rise),
                  (h+a, -rise-t), (-h+b, -rise-t), (-h+a, -t), (-h-a, -t)]
        s = polygon_sketch(body, 'PressedSection', points, along_y(-v['shoe_width']/2))
        f = pad(body, 'ShoeWidth', s, v['shoe_width'])
        f.setExpression('Length', 'Parameters.shoe_width')
    elif builder == 'rail':
        length = v['shoe_pitch']-2*v['rail_end_margin']
        points = [(-length/2, 0), (length/2, 0), (length/2, -v['rail_height']), (-length/2, -v['rail_height'])]
        s = polygon_sketch(body, 'RailWeb', points, along_y(-v['rail_width']/2))
        f = pad(body, 'WebWidth', s, v['rail_width'])
    elif builder == 'roller':
        w, r, bore = v['roller_width']/2, v['roller_diameter']/2, v['tube_od']/2+v['roller_bore_clearance']
        fw, tr, waist = v['roller_flange_width'], v['roller_transition'], v['roller_waist_radius']
        f = revolve(body, [(bore,-w),(r,-w),(r,-w+fw),(waist,-w+fw+tr),
                           (waist,w-fw-tr),(r,w-fw),(r,w),(bore,w)])
    elif builder == 'tube':
        L, ro, ri = v['tube_length']/2, v['tube_od']/2, v['tube_id']/2
        g = L-v['ring_end_margin']; half=v['ring_width']/2+v['groove_clearance']; rg=v['ring_id']/2
        f = revolve(body, [(ri,-L),(ro,-L),(ro,-g-half),(rg,-g-half),(rg,-g+half),(ro,-g+half),
                           (ro,g-half),(rg,g-half),(rg,g+half),(ro,g+half),(ro,L),(ri,L)])
    elif builder == 'ring':
        ro = v['ring_id']/2+v['ring_radial']
        f = annulus(body, 'RingWidth', ro, v['ring_id']/2, -v['ring_width']/2, v['ring_width'])
        s = polygon_sketch(body, 'SplitSlot', [(-v['ring_gap']/2,0),(v['ring_gap']/2,0),
                            (v['ring_gap']/2,-ro-1),(-v['ring_gap']/2,-ro-1)], along_y(v['ring_width']/2))
        cut = body.newObject('PartDesign::Pocket','Split');cut.Profile=s;cut.Length=v['ring_width']
        doc.recompute()
        if s.ViewObject:s.ViewObject.Visibility=False;f.ViewObject.Visibility=False
        f=cut
    elif builder == 'angle':
        leg,t = v['angle_leg'],v['angle_thickness']
        # Sketch YZ plane; local coordinates are Y,Z, normal +X.
        placement=App.Placement(App.Vector(-v['angle_length']/2,0,0),App.Rotation(App.Vector(1,1,1),120))
        s=polygon_sketch(body,'AngleSection',[(0,0),(leg,0),(leg,t),(t,t),(t,leg),(0,leg)],placement)
        f=pad(body,'CouponLength',s,v['angle_length']);f=joint_holes(body,f,v)
    elif builder == 'plate':
        half=v['angle_length']/2
        s=polygon_sketch(body,'PlateOutline',[(-half,0),(half,0),(half,-v['joint_plate_height']),(-half,-v['joint_plate_height'])],along_y(-v['plate_thickness']))
        f=pad(body,'PlateThickness',s,v['plate_thickness'])
        f.setExpression('Length','Parameters.plate_thickness')
        f=joint_holes(body,f,v)
    elif builder == 'fastener':
        f=annulus(body,'Shank',v['fastener_shank']/2,0,-v['plate_thickness'],v['plate_thickness']+v['angle_thickness'])
        previous=f
        f=annulus(body,'Head',v['fastener_head_diameter']/2,0,v['angle_thickness'],v['fastener_head_height'])
        if previous.ViewObject:previous.ViewObject.Visibility=False
    else:
        raise ValueError('Unknown builder '+builder)
    doc.recompute()
    if not body.Shape.isValid() or len(body.Shape.Solids)!=1 or body.Shape.Volume<=0:
        raise ValueError(f'Invalid part geometry: {key}; states {[(o.Name, o.State) for o in doc.Objects]}')
    appearance(body)
    if f.ViewObject:f.ViewObject.Visibility=True
    doc.saveAs(str(folder/(key+'.FCStd')))
    return doc,body


def reference(doc, group, name, shape, refs, notes):
    obj=doc.addObject('PartDesign::Feature',name)
    obj.Shape=shape
    metadata(obj,None,'illustrative_provisional',refs,True,notes)
    group.addObject(obj)
    appearance(obj,True)
    return obj


def prism_xz(points, width):
    pts=[App.Vector(x,-width/2,z) for x,z in points]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,width,0))


def blockout(doc, data):
    v=data['values'];entry=data['calibrations']['snl_2']
    group=doc.addObject('App::Part','ReferenceGeometry');doc.Root.addObject(group)
    refs=['calibration:snl_2','issue:blockout','issue:configuration_transfer']
    for key,width in [('hull',2*v['blockout_half_width']),('upper',v['main_turret_width']),('outlook',v['main_turret_width']/2)]:
        pts=[point(entry,v,p) for p in entry['profiles'][key]]
        reference(doc,group,key.title()+'Envelope',prism_xz(pts,width),refs,'Reference envelope; excluded from physical BOM and STEP.')
    for side,sign in [('Port',1),('Starboard',-1)]:
        # Trapezoidal plan envelope; chamfer proportions are documented blockout conventions.
        x0,x1=v['sponson_rear_x'],v['sponson_front_x'];yi=v['blockout_half_width'];yo=v['vehicle_width']/2
        pts=[App.Vector(x0,sign*yi,v['sponson_base_z']),App.Vector(x0+(x1-x0)/5,sign*yo,v['sponson_base_z']),
             App.Vector(x1-(x1-x0)/5,sign*yo,v['sponson_base_z']),App.Vector(x1,sign*yi,v['sponson_base_z'])]
        shape=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,0,v['sponson_top_z']-v['sponson_base_z']))
        reference(doc,group,side+'SponsonEnvelope',shape,refs,'Provisional trapezoid, end bevels each one-fifth length; depth unverified.')
        track=[point(entry,v,p) for p in entry['profiles']['track']]
        for suffix,y in [('Inner',sign*(v['track_centers']-v['shoe_width'])/2),('Outer',sign*(v['track_centers']+v['shoe_width'])/2)]:
            pts=[App.Vector(x,y,z) for x,z in track]
            reference(doc,group,side+suffix+'TrackGuide',Part.makePolygon(pts+[pts[0]]),refs,'Polyline outline guide only; not an articulated track or physical part.')
        for key,pixel in entry['axes_pixels'].items():
            x,z=point(entry,v,pixel);y=sign*v['track_centers']/2;r=v[key+'_diameter']/2
            shape=Part.makeCircle(r,App.Vector(x,y,z),App.Vector(0,1,0))
            reference(doc,group,side+key.title()+'Axis',shape,refs,'Reference rim centered on approximate foldout axis.')
    doc.recompute()


def build(data,out):
    folder=Path(out)/'native';folder.mkdir(parents=True,exist_ok=True)
    for name in list(App.listDocuments()):App.closeDocument(name)
    parts={}
    for key,spec in data['model']['parts'].items():
        parts[key]=make_part(key,spec,data,folder)[1]
    doc=App.newDocument('MarkVIII_Pilot')
    root=doc.addObject('Assembly::AssemblyObject','Root');root.Label='Mark VIII — Rock Island production pilot'
    metadata(root,None,'illustrative_provisional',['issue:configuration_transfer'],notes=data['model']['physical_scope'])
    doc.saveAs(str(folder/'MarkVIII_Pilot.FCStd'))
    objects={'Root':root}
    for spec in data['model']['occurrences']:
        key=spec['id'];parent=objects[spec['parent']]
        obj=doc.addObject('App::Link' if spec['part'] else 'App::Part',key)
        parent.addObject(obj)
        if spec['part']:obj.setLink(parts[spec['part']])
        tr=[arithmetic(x,data['values']) for x in spec['translation']]
        rot=[arithmetic(x,data['values']) for x in spec['rotation']]
        placement=App.Placement(App.Vector(*tr),App.Rotation(*rot))
        if spec['part']:obj.LinkPlacement=placement
        else:obj.Placement=placement
        obj.addProperty('App::PropertyString','OccurrenceId','Evidence');obj.OccurrenceId=key
        metadata(obj,spec.get('survey_id') or (data['model']['parts'][spec['part']]['survey_id'] if spec['part'] else None),
                 spec['status'],spec['evidence'],notes='Occurrence placement; dimensional evidence is on the linked definition.')
        objects[key]=obj
    blockout(doc,data)
    doc.recompute()
    App.setActiveDocument(doc.Name)
    if App.GuiUp:
        import FreeCADGui as Gui
        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()
    doc.saveAs(str(folder/'MarkVIII_Pilot.FCStd'))
    write(Path(out)/'reports/parameters_resolved.json',data['values'])
    return doc


def leaves(doc):
    """World-space physical instances, never reference volumes or assembly-level duplicates."""
    result=[]
    def visit(obj,placement):
        local=obj.LinkPlacement if obj.TypeId=='App::Link' else obj.Placement
        world=placement.multiply(local)
        if obj.TypeId=='App::Link':
            if obj.LinkedObject is None:
                raise ValueError('Missing linked part: '+obj.Name)
            shape=obj.LinkedObject.Shape.copy()
            shape.Placement=world.multiply(shape.Placement)
            result.append((obj.Name,shape,obj))
        elif not getattr(obj,'ReferenceOnly',False):
            for child in getattr(obj,'Group',[]):
                if child.Name!='ReferenceGeometry':visit(child,world)
    visit(doc.Root,App.Placement())
    return result
