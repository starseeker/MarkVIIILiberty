"""Oil-pump component reconstruction in engine-aligned axes, mounting face Z=0.

Printed fits are retained separately from estimated cast profiles, gear geometry,
shaft lobes and passages. Assembly containers never add physical material.
"""
import math
import FreeCAD as App
import Part
from engine_crossmember_parts import box
from transmission_planet_parts import gear_outline
from transmission_stud_parts import hex_x
from transmission_core_parts import revolve

V=App.Vector;X,Y,Z=V(1,0,0),V(0,1,0),V(0,0,1)

def cylinder(r,a,b,x=0.,y=0.):
    assert b>a
    return Part.makeCylinder(r,b-a,V(x,y,a),Z)

def ring(ro,ri,a,b):
    return cylinder(ro,a,b).cut(cylinder(ri,a-1,b+1))

def united(shapes):
    return shapes[0].multiFuse(shapes[1:]) if len(shapes)>1 else shapes[0]

def moved(s,x=0,y=0,z=0,angle=0):
    s=s.copy()
    if angle:s.rotate(V(),Z,angle)
    s.translate(V(x,y,z));return s

def rod(a,b,r):
    a,b=V(*a),V(*b);v=b-a
    return Part.makeCylinder(r,v.Length,a,v/v.Length)

def channel(points,r):
    # Spherical junctions preserve a continuous estimated drilled/cast passage.
    return united([rod(a,b,r) for a,b in zip(points,points[1:])]+[Part.makeSphere(r,V(*p)) for p in points[1:-1]])

def hex_z(af,low,high):
    s=hex_x(af,low,high);s.rotate(V(),Y,-90);return s

def lobes(core,tip,width,count,a,b):
    return united([cylinder(core,a,b)]+[moved(box(core-.5,tip,-width/2,width/2,a,b),angle=360*i/count) for i in range(count)]).common(cylinder(tip,a,b))

def rounded_plate(hx,hy,r,a,b):
    return united([box(-hx+r,hx-r,-hy,hy,a,b),box(-hx,hx,-hy+r,hy-r,a,b)]+[cylinder(r,a,b,sx*(hx-r),sy*(hy-r)) for sx in [-1,1] for sy in [-1,1]])

def mount_outline(c,low,high):
    """Circular flange with a tangent, rounded forward nose (estimated profile)."""
    radius=c['mount_nose_tip_radius'];center=V(c['mount_nose_x']+radius,0,low)
    upper=V(-c['mount_flange_radius']+c['mount_nose_overlap'],c['mount_nose_half_width'],low)
    delta=upper-center;length2=delta.dot(delta);assert length2>radius**2
    tangent=center+delta*(radius**2/length2)+V(-delta.y,delta.x,0)*(radius*math.sqrt(length2-radius**2)/length2)
    lower=V(upper.x,-upper.y,low);other=V(tangent.x,-tangent.y,low)
    edges=[Part.makeLine(upper,tangent),Part.Arc(tangent,V(c['mount_nose_x'],0,low),other).toShape(),Part.makeLine(other,lower),Part.makeLine(lower,upper)]
    nose=Part.Face(Part.Wire(edges)).extrude(V(0,0,high-low))
    return cylinder(c['mount_flange_radius'],low,high).fuse(nose)

def rev_z(profile):
    s=revolve(profile);s.rotate(V(),X,90);return s

def parts(c,progress=None):
    p={};occ=[];d={};groups=['EngineOilPumpLowerBody','EngineOilPumpUpperBody','EngineOilPumpRotors','EngineOilPumpRelief','EngineOilPumpStrainers','EngineOilPumpFasteners']
    def add(key,name,xyz=(0,0,0),angle=0,group='EngineOilPumpRotors'):
        occ.append(dict(key=key,name='EngineOilPump_'+name,xyz=list(xyz),rotation=list(App.Rotation(Z,angle).Q),assembly=group))
    def audit(key):
        s=p[key]
        if progress:progress(key,s)
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,(key,len(s.Solids),s.isValid())
    n=c['gear_teeth'];rp=n*c['gear_module']/2;spacing=2*rp;gap=c['gear_endplay'];radial=c['gear_diametrical_clearance']/2
    plate=c['partition_stock'];lower_bottom=-c['lower_gear_width']-gap;upper_top=plate+c['upper_gear_width']+gap
    gear_bands={'lower':[lower_bottom+gap/2,-gap/2],'upper':[plate+gap/2,upper_top-gap/2]}
    profile_reports={};tip={}
    for level in ['lower','upper']:
        tip[level]=rp+c[level+'_addendum'];face,profile_reports[level]=gear_outline(n,rp,rp-c[level+'_dedendum'],tip[level],c['gear_pressure_angle'],c['gear_thinning'],c['gear_flank_samples'])
        face.rotate(V(),X,90);lo,hi=gear_bands[level];blank=face.extrude(Z*(hi-lo));blank.translate(V(0,0,lo))
        bore=lobes(c['shaft_core_radius']+c['shaft_gear_gap'],c['shaft_lobe_radius']+c['shaft_gear_gap'],c['shaft_lobe_width']+2*c['shaft_gear_gap'],c['shaft_lobe_count'],lo-1,hi+1)
        p[level+'_driving_gear']=blank.cut(bore)
        p[level+'_idler_gear']=blank.cut(cylinder(c['idler_pin_radius']+c['idler_pin_gap'],lo-1,hi+1))
        add(level+'_driving_gear',level.title()+'DrivingGear')
        add(level+'_idler_gear',level.title()+'Idler1',(0,-spacing,0),180/n)
        if level=='upper':add(level+'_idler_gear','UpperIdler2',(0,spacing,0),180/n)
    shaft=lobes(c['shaft_core_radius'],c['shaft_lobe_radius'],c['shaft_lobe_width'],c['shaft_lobe_count'],gear_bands['lower'][0]-.01,upper_top+.5)
    shaft=shaft.fuse(cylinder(c['shaft_core_radius'],c['shaft_bottom_z'],upper_top+1))
    shaft=shaft.fuse(cylinder(c['shaft_journal_radius'],c['upper_bush_bottom'],c['shaft_coupling_high']))
    shaft=shaft.fuse(cylinder(c['shaft_collar_radius'],c['shaft_collar_z'],c['shaft_collar_z']+c['shaft_collar_stock']))
    shaft=shaft.fuse(lobes(c['coupling_core_radius'],c['coupling_tip_radius'],c['coupling_lobe_width'],c['coupling_lobes'],c['shaft_coupling_low'],c['shaft_coupling_high']))
    p['shaft']=shaft;add('shaft','DrivingShaft')
    # Separate fixed idler pins: the long one supports both stages.
    p['long_pin']=cylinder(c['idler_pin_radius'],lower_bottom-c['pin_lower_embed'],upper_top+c['pin_upper_embed'])
    p['short_pin']=cylinder(c['idler_pin_radius'],-c['pin_lower_embed'],upper_top+c['pin_upper_embed'])
    add('long_pin','LongIdlerPin',(0,-spacing,0));add('short_pin','ShortIdlerPin',(0,spacing,0))
    p['upper_bush']=ring(c['upper_bush_radius'],c['shaft_journal_radius']+c['shaft_upper_bush_gap'],c['upper_bush_bottom'],c['upper_bush_top'])
    p['upper_bush']=p['upper_bush'].fuse(ring(c['upper_bush_flange_radius'],c['shaft_journal_radius']+c['shaft_upper_bush_gap'],c['upper_bush_top']-c['upper_bush_flange_stock'],c['upper_bush_top']))
    add('upper_bush','UpperBush',group=groups[1])
    p['lower_bush']=ring(c['lower_bush_radius'],c['shaft_core_radius']+c['shaft_upper_bush_gap'],c['lower_bush_bottom'],c['lower_bush_top'])
    add('lower_bush','LowerBush',group=groups[0])
    # Steel partition follows the two lower gear wells and bridges the upper pair.
    separator=united([cylinder(tip['lower']+3,0,plate,0,y) for y in [-spacing,0]])
    for y,r in [(0,c['shaft_lobe_radius']+.1),(-spacing,c['idler_pin_radius']+.05)]:separator=separator.cut(cylinder(r,-1,plate+1,0,y))
    p['partition']=separator;add('partition','SeparatingPlate',group=groups[0])
    top=upper_top+c['upper_body_top_stock'];upper=rounded_plate(c['upper_body_half_x'],c['upper_body_half_y'],c['upper_body_corner_radius'],0,c['upper_body_flange_stock'])
    upper=upper.fuse(united([cylinder(tip['upper']+c['upper_body_wall'],0,top,0,y) for y in [-spacing,0,spacing]]))
    upper=upper.fuse(cylinder(c['upper_boss_radius'],top-1,c['upper_boss_top']))
    upper=upper.cut(united([cylinder(tip['upper']+radial,plate,upper_top,0,y) for y in [-spacing,0,spacing]]))
    # Cut the full pocket envelope: subtracting the perforated separator itself
    # leaves disconnected islands in its shaft/pin holes.
    upper=upper.cut(united([cylinder(tip['lower']+3,0,plate,0,y) for y in [-spacing,0]]))
    for y in [-spacing,spacing]:upper=upper.cut(cylinder(c['idler_pin_radius']+c['idler_pin_gap'],-1,upper_top+c['pin_upper_embed']+.1,0,y))
    upper=upper.cut(cylinder(c['upper_bush_radius']+c['bush_cast_gap'],c['upper_bush_bottom'],c['upper_bush_top']+1))
    upper=upper.cut(cylinder(c['shaft_lobe_radius']+.1,-1,c['upper_bush_bottom']+.1))
    upper=upper.cut(cylinder(c['upper_bush_flange_radius']+c['bush_cast_gap'],c['upper_bush_top']-c['upper_bush_flange_stock'],c['upper_bush_top']+1))
    # Lower body: external filter chamber, separate close-fitting gear wells,
    # lower bushing support and a complete mounting flange with forward ports.
    bottom=c['lower_body_bottom'];ro=c['lower_body_radius'];ri=ro-c['lower_body_wall'];fr=c['mount_flange_radius']
    lower=ring(ro,ri,bottom,0).fuse(mount_outline(c,-c['mount_flange_stock'],0))
    lower=lower.fuse(ring(fr,ri,bottom,bottom+c['bottom_flange_stock']))
    lower=lower.fuse(united([cylinder(tip['lower']+c['body_gear_wall'],lower_bottom-c['body_gear_bottom_stock'],0,0,y) for y in [-spacing,0]]))
    lower=lower.fuse(cylinder(c['lower_bush_boss_radius'],c['lower_bush_bottom']-1,lower_bottom+1))
    lower=lower.cut(united([cylinder(tip['lower']+radial,lower_bottom,1,0,y) for y in [-spacing,0]]))
    lower=lower.cut(cylinder(c['lower_bush_radius']+c['bush_cast_gap'],c['lower_bush_bottom']-.1,c['lower_bush_top']))
    lower=lower.cut(cylinder(c['shaft_core_radius']+.1,c['lower_bush_bottom']-2,1))
    lower=lower.cut(cylinder(c['idler_pin_radius']+c['idler_pin_gap'],lower_bottom-c['pin_lower_embed']-.1,1,0,-spacing))
    lower=lower.cut(cylinder(c['idler_pin_radius']+c['idler_pin_gap'],-c['pin_lower_embed']-.1,1,0,spacing))
    # Add supporting stock under the short idler's blind locating socket.
    lower=lower.fuse(cylinder(c['idler_pin_radius']+4,-c['pin_lower_embed']-2,-1,0,spacing))
    lower=lower.cut(cylinder(c['idler_pin_radius']+c['idler_pin_gap'],-c['pin_lower_embed']-.1,1,0,spacing))
    upper_bolts=[(sx*c['upper_bolt_x'],sy*c['upper_bolt_y']) for sx in [-1,1] for sy in [-1,1]]
    for x,y in upper_bolts:
        # HB joint grip is restored by the discrete lower boss; the bolt stack
        # will be added from the independently selected printed hardware stock.
        lower=lower.fuse(cylinder(7.5,-(c['upper_bolt_head_nut_span']-2*c['washer_stock']-c['upper_body_flange_stock']),0,x,y))
        for which in ['lower','upper']:
            tool=cylinder(c['bolt_diameter']/2+c['bolt_hole_gap'],-20,10,x,y)
            if which=='lower':lower=lower.cut(tool)
            else:upper=upper.cut(tool)
    p['dowel']=cylinder(c['dowel_diameter']/2,-c['dowel_length']/2,c['dowel_length']/2)
    for index,sign in enumerate([-1,1],1):
        x,y=sign*c['dowel_x'],sign*c['dowel_y'];hole=cylinder(c['dowel_diameter']/2+c['bolt_hole_gap'],-c['dowel_length']/2-.1,c['dowel_length']/2+.1,x,y)
        lower=lower.cut(hole);upper=upper.cut(hole);add('dowel','LocatingDowel'+str(index),(x,y,0),group=groups[0])
    p.update(lower_body=lower,upper_body=upper)
    add('lower_body','LowerBody',group=groups[0]);add('upper_body','UpperBody',group=groups[1])
    d.update(gear_bands=gear_bands,gear_profiles=profile_reports,gear_center_spacing=spacing,gear_cavity_floor=lower_bottom,gear_cavity_roof=upper_top,upper_body_top=top,upper_bolt_centers=upper_bolts,
             selected_source_clearances=dict(diametrical=c['gear_diametrical_clearance'],axial=c['gear_endplay']),missing=['Passages and relief unit','Strainers and covers','Installed hardware and lock wires','Case receiving revision and tank mounting'])
    for key in p:audit(key)
    return p,occ,groups,d
