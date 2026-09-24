"""Source-section reconstruction of the central transmission shells and rotors.

Local axes retain tank X forward, Y port and Z up. Port planetary profiles use
the source-calibrated transverse station; starboard is a rigid half-turn about X.
No gear teeth or manufactured casting tolerances are asserted here.
"""
import FreeCAD as App
import Part

from transmission_support_parts import box
from transmission_frame_parts import xz_plate
from transmission_output_parts import spline_tools


def cylinder(radius, low, high):
    return Part.makeCylinder(radius, high-low, App.Vector(0,low,0), App.Vector(0,1,0))


def revolve(profile):
    points=[App.Vector(r,y,0) for r,y in profile]
    return Part.Face(Part.makePolygon(points+points[:1])).revolve(App.Vector(),App.Vector(0,1,0),360)


def spline_envelope(core, tip, width, count, low, high):
    pieces=[cylinder(core,low,high)]
    for n in range(count):
        tooth=box(-width/2,width/2,low,high,core-2,tip)
        tooth.rotate(App.Vector(),App.Vector(0,1,0),360*n/count)
        pieces.append(tooth)
    return pieces[0].multiFuse(pieces[1:]).removeSplitter()


def outline_face(segments, scale=1):
    # Explicit cubic Bezier poles become degree-three clamped B-spline edges.
    edges=[]
    for segment in segments:
        poles=[App.Vector(scale*x,0,scale*z) for x,z in segment]
        if len(poles)==2:edges.append(Part.makeLine(*poles))
        else:
            curve=Part.BSplineCurve()
            curve.buildFromPolesMultsKnots(poles,[4,4],[0,1],False,3)
            edges.append(curve.toShape())
    return Part.Face(Part.Wire(edges))


def core_parts(c,cal,chain,shaft_half_span,output_center_y,frame):
    scale=cal['mm_per_pixel']
    axial=lambda pixel:output_center_y+(cal['sprocket_center_x_px']-pixel)*scale
    profiles={}
    for name,picks in c['planetary_profiles_px'].items():
        profiles[name]=[(abs(cal['shaft_axis_y_px']-v)*scale,axial(u)) for u,v in picks]
    shapes={name:revolve(profile) for name,profile in profiles.items()}
    # The conical carrier connects to the existing splined M289 shaft.
    carrier=shapes['planet_disk']
    bb=carrier.BoundBox
    shapes['planet_disk']=carrier.cut(spline_tools(chain,bb.YMin-1,bb.YMax+1)).removeSplitter()

    low,high=map(axial,c['high_drum_faces_px'][::-1])
    neck_end=axial(c['high_drum_hub_end_px'])
    R=c['high_drum_diameter']/2; wall=c['high_drum_rim_stock'];hub=c['high_drum_hub_radius']
    web=low+c['high_drum_web_stock']
    profile=[(0,low),(R,low),(R,high),(R-wall,high),(R-wall,web),
             (hub,web),(hub,neck_end),(0,neck_end)]
    drum=revolve(profile)
    tool=spline_envelope(c['high_drum_bore_radius'],c['high_drum_spline_tip_radius'],
                         c['high_drum_spline_width'],c['splines'],low-1,neck_end+1)
    shapes['high_drum']=drum.cut(tool).removeSplitter()
    profiles['high_drum']=profile
    half=shaft_half_span-c['shaft_end_gap']
    shapes['cross_shaft']=spline_envelope(c['cross_shaft_root_radius'],c['cross_shaft_tip_radius'],
                                         c['cross_shaft_spline_width'],c['splines'],-half,half)

    outer=outline_face(c['bevel_outline_segments'])
    inner=outline_face(c['bevel_outline_segments'],c['bevel_cavity_scale'])
    width=c['bevel_half_width']; stock=c['bevel_end_stock'];gap=c['bevel_split_gap']/2
    blank=outer.extrude(App.Vector(0,2*width,0));blank.translate(App.Vector(0,-width,0))
    cavity=inner.extrude(App.Vector(0,2*(width-stock),0));cavity.translate(App.Vector(0,-width+stock,0))
    shell=blank.cut(cavity)
    back=shell.common(box(-500,-gap,-width-1,width+1,-500,500))
    front=shell.common(box(gap,500,-width-1,width+1,-500,500))
    # Source Plate23 front bearing-housing boss. The bearing assembly is separate.
    start,end=c['input_boss_x']; radius=c['input_boss_radius']
    boss=Part.makeCylinder(radius,end-start,App.Vector(start,0,0),App.Vector(1,0,0))
    front=front.fuse(boss)
    inlet=Part.makeCylinder(c['input_boss_bore_radius'],end-start+80,
                            App.Vector(start-79,0,0),App.Vector(1,0,0))
    front=front.cut(inlet)
    bore=cylinder(c['bevel_sleeve_bore_radius'],-width-1,width+1)
    front=front.cut(bore);back=back.cut(bore)
    # Cast mounting webs live at the end walls and meet the existing frame face.
    rear=frame['rear'];top=frame['top'];bottom=frame['bottom'];height=frame['height']
    outline=[(rear,bottom-height),(rear+c['bevel_foot_depth'],bottom-height),
             (-c['bevel_web_front_reach'],-c['bevel_web_inner_z']),
             (-c['bevel_web_front_reach'],c['bevel_web_inner_z']),
             (rear+c['bevel_foot_depth'],top+height),(rear,top+height)]
    webs=[xz_plate(outline,sign*(width-c['bevel_web_stock']) if sign>0 else -width,
                   width if sign>0 else -width+c['bevel_web_stock']) for sign in [1,-1]]
    back=back.multiFuse(webs).removeSplitter()
    shapes['bevel_case']=back
    shapes['bevel_cover']=front.removeSplitter()
    for key,shape in shapes.items():
        if not shape.isValid() or len(shape.Solids)!=1:raise ValueError('Invalid core part '+key)
    return shapes,dict(profiles_radial_axial_mm=profiles,cross_shaft_half_length_mm=half,
        high_drum_outer_diameter_mm=2*R,high_drum_axial_faces_mm=[low,high],
        bevel_frame_local_mm=frame,bevel_mounting_web_outline_xz_mm=outline,
        approximate_sections=True,gear_and_bearing_fit_qualified=False)
