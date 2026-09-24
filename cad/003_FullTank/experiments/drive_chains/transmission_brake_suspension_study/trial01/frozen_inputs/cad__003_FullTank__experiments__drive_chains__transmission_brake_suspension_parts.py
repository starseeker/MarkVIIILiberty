"""Source-proportioned M338 hanger and estimated M385 stop.

The bracket origin is its pin axis, local +X forward, +Y along the pin, +Z up.
The stop origin is the upper channel front/underside at its brake plane.
These profiles and thicknesses are reconstruction hypotheses, not shop drawings.
"""
import FreeCAD as App
import Part
from transmission_support_parts import box


def dimensions(c, web_span):
    sx=c['channel_depth']/(c['source_channel_x_px'][1]-c['source_channel_x_px'][0])
    sz=web_span/(c['source_channel_web_z_px'][1]-c['source_channel_web_z_px'][0])
    x=lambda pixel: -(pixel-c['source_channel_x_px'][0])*sx
    px,pz=c['source_pin_px']
    pin_x=x(px);drop=(pz-c['source_channel_web_z_px'][0])*sz+c['pin_drop_adjustment']
    front,rear=[x(v)-pin_x for v in c['source_foot_x_px']]
    radius=(c['source_lug_x_px'][1]-c['source_lug_x_px'][0])*sx/2
    stop_height=(c['stop_source_top_bottom_px'][1]-c['stop_source_top_bottom_px'][0])*web_span/(c['stop_source_frame_webs_px'][1]-c['stop_source_frame_webs_px'][0])
    return dict(scale_x_mm_px=sx,scale_z_mm_px=sz,pin_x_relative_channel_mm=pin_x,
                pin_drop_mm=drop,foot_rear_mm=rear,foot_front_mm=front,
                foot_stock_mm=c['source_foot_stock_px']*sz,lug_radius_mm=radius,
                stop_height_mm=stop_height,web_span_mm=web_span)


def parts(c,d):
    V=App.Vector;radius=d['lug_radius_mm'];half=c['lug_stock']/2
    crown=d['pin_drop_mm']-d['foot_stock_mm']
    assert crown>0 and radius>c['pin_bore_diameter']/2+c['pin_bore_clearance']
    # One closed outline gives an analytic semicircular lower end and a flat
    # upper root, avoiding a coincident box/cylinder seam in the bore region.
    a,b=V(-radius,-half,crown),V(radius,-half,crown)
    cc,dd=V(radius,-half,0),V(-radius,-half,0)
    wire=Part.Wire([Part.makeLine(a,b),Part.makeLine(b,cc),
                    Part.Arc(cc,V(0,-half,-radius),dd).toShape(),Part.makeLine(dd,a)])
    lug=Part.Face(wire).extrude(V(0,c['lug_stock'],0))
    foot=box(d['foot_rear_mm'],d['foot_front_mm'],-c['foot_width']/2,c['foot_width']/2,
             crown,d['pin_drop_mm'])
    bracket=foot.fuse(lug).cut(Part.makeCylinder(c['pin_bore_diameter']/2+c['pin_bore_clearance'],
        c['lug_stock']+2,V(0,-half-1,0),V(0,1,0)))
    rear=-c['channel_depth'];s=c['stop_stock'];w=c['stop_width']/2;depth=c['stop_toe_depth']
    assert 0<s<depth and d['stop_height_mm']>s
    stop=box(rear,rear+s,-w,w,-d['stop_height_mm'],0).fuse(box(rear,rear+depth,-w,w,-s,0))
    result=dict(bracket=bracket,stop=stop)
    for name,shape in result.items():
        assert shape.isValid() and len(shape.Solids)==1,name
    return result
