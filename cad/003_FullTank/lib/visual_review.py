"""Software-rendered native geometry and fixed-calibration source comparisons."""
import base64
import html
import io
from pathlib import Path

import FreeCAD as App
import fitz
import numpy as np
from PIL import Image

from .cad_build import COLORS
from .evidence import REPO, write
from .model import point


def shaded(items, path, direction, title, context=(), up_direction=(0,0,1), canvas=(1600,900)):
    direction = App.Vector(*direction)
    direction.normalize()
    up = App.Vector(*up_direction)
    if abs(direction.dot(up)) > 0.99:
        up = App.Vector(0, 1, 0)
    right = up.cross(direction)
    right.normalize()
    up = direction.cross(right)
    up.normalize()
    batches, coords, guides, edge_lines = [], [], [], []
    mesh_cache = {}
    camera = np.array([[right.x,-up.x,direction.x],[right.y,-up.y,direction.y],[right.z,-up.z,direction.z]])
    bounds = App.BoundBox()
    for item in list(items) + list(context):
        bounds.add(item["shape"].BoundBox)
    deflection = max(0.6, bounds.DiagonalLength/2500)
    for item in list(context) + [i for i in items if not i["shape"].Faces]:
        for edge in item["shape"].Edges:
            vertices = edge.discretize(Deflection=2.0)
            line = [(v.dot(right), -v.dot(up)) for v in vertices]
            guides.append(line)
            coords.extend(line)
    for item in items:
        if not item["shape"].Faces:
            continue
        color = COLORS[item["system"]]
        if item["representation"] == "assembly" and item["definition"].startswith("track_"):
            color = (0.43,0.47,0.42) if item["definition"] == "track_shoe" else (0.64,0.66,0.61)
        key = item["definition"]
        target = item["target"].Shape
        if key not in mesh_cache:
            vertices,indices = target.tessellate(deflection)
            local = np.array([[v.x,v.y,v.z] for v in vertices])
            indices = np.array(indices,dtype=np.int32)
            cells = local[indices]
            normals = np.cross(cells[:,1]-cells[:,0],cells[:,2]-cells[:,0])
            lengths = np.linalg.norm(normals,axis=1)
            valid = lengths>1e-12
            indices,normals = indices[valid],normals[valid]/lengths[valid,None]
            edges = []
            if item["representation"] == "assembly":
                edges = [np.array([[v.x,v.y,v.z] for v in edge.discretize(Deflection=deflection)]) for edge in target.Edges]
            mesh_cache[key] = local,indices,normals,edges
        local,indices,normals,edges = mesh_cache[key]
        transform = item["shape"].Placement.multiply(target.Placement.inverse())
        matrix = transform.toMatrix()
        rotation = np.array([[matrix.A11,matrix.A12,matrix.A13],[matrix.A21,matrix.A22,matrix.A23],[matrix.A31,matrix.A32,matrix.A33]])
        translation = np.array([matrix.A14,matrix.A24,matrix.A34])
        projected = (local@rotation.T+translation)@camera
        # Cross-check a mesh vertex against the CAD kernel's placement operation.
        expected = transform.multVec(App.Vector(*local[0]))
        actual = local[0]@rotation.T+translation
        if np.linalg.norm(actual-np.array([expected.x,expected.y,expected.z]))>1e-7:
            raise ValueError("Preview mesh placement differs from native CAD placement")
        light = 0.58+0.37*np.abs(normals@(rotation.T@np.array([0.3,-0.5,0.8])))
        rgb = np.clip(light[:,None]*np.array(color)[None,:]*255,0,255).astype(np.uint8)
        batches.append((projected[indices],rgb))
        coords += [(float(projected[:,0].min()),float(projected[:,1].min())),
                   (float(projected[:,0].max()),float(projected[:,1].max()))]
        edge_lines.extend((edge@rotation.T+translation)@camera for edge in edges)
    if not coords:
        raise ValueError("No solid geometry in requested preview")
    xmin, xmax = min(x for x,y in coords), max(x for x,y in coords)
    ymin, ymax = min(y for x,y in coords), max(y for x,y in coords)
    width, height = canvas
    scale = min((width-100)/max(xmax-xmin, 1), (height-150)/max(ymax-ymin, 1))
    def screen(points):
        return [((width-(xmax-xmin)*scale)/2+(x-xmin)*scale, 100+(y-ymin)*scale) for x,y in points]
    from .raster import paint
    vertices = np.concatenate([x[0] for x in batches])
    colors = np.concatenate([x[1] for x in batches])
    del batches
    vertices[:,:,0] = (width-(xmax-xmin)*scale)/2+(vertices[:,:,0]-xmin)*scale
    vertices[:,:,1] = 100+(vertices[:,:,1]-ymin)*scale
    pixels,depth_buffer = paint(vertices,colors,width,height,path.parent.parent/"runtime")
    del vertices,colors
    # Native boundaries use the same cached rigid transform and depth buffer.
    for line in edge_lines:
        xy = screen(line[:,:2])
        depths = line[:,2]
        for a,b,za,zb in zip(xy,xy[1:],depths,depths[1:]):
            steps = max(2,int(max(abs(b[0]-a[0]),abs(b[1]-a[1])))+2)
            t = np.linspace(0,1,steps)
            xx = np.rint(a[0]+(b[0]-a[0])*t).astype(int)
            yy = np.rint(a[1]+(b[1]-a[1])*t).astype(int)
            z = za+(zb-za)*t
            valid = (xx>=0)&(xx<width)&(yy>=0)&(yy<height)
            xx,yy,z = xx[valid],yy[valid],z[valid]
            seen = z >= depth_buffer[yy,xx]-1.5/scale
            pixels[yy[seen],xx[seen]] = (48,54,47)
    bitmap = io.BytesIO()
    Image.fromarray(pixels).save(bitmap, format="PNG")
    guide_svg = "".join('<polyline fill="none" stroke="#657c82" stroke-width="1" opacity=".5" points="' +
                        " ".join(f"{x:.2f},{y:.2f}" for x,y in screen(line)) + '"/>' for line in guides)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
           f'<image width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(bitmap.getvalue()).decode()}"/>{guide_svg}'
           f'<text x="40" y="36" font-family="sans-serif" font-size="24">{html.escape(title)}</text>'
           '<text x="40" y="65" font-family="sans-serif" font-size="16">Subsystem colors · reconstruction in progress · layout envelopes are provisional</text></svg>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)
    with fitz.open(stream=svg.encode(), filetype="svg") as doc:
        doc[0].get_pixmap().save(str(path.with_suffix(".png")))


def comparison(data, items, specification, folder):
    key = specification["id"]
    cal = data["calibrations"][specification["calibration"]]
    path = REPO / cal["image"]
    with Image.open(path) as src:
        source = src.convert("RGB")
        angle = cal.get("rotation_ccw_deg", 0)
        if angle:
            source = source.rotate(angle, expand=True)
    source.save(folder / (key + "_source.png"))
    small_track_hardware = {"track_pin","track_bushing","track_cotter","track_rivet"}
    selected = [i for i in items if i["definition"] not in set(specification["exclude"])|small_track_hardware]
    shaded(selected, folder / (key + "_cad.svg"), (0,1,0), key + " | installed native geometry")
    record = {"id": key, "mode": cal["mode"], "description": specification["description"],
              "source": cal["image"], "display_rotation_ccw_deg": cal.get("rotation_ccw_deg", 0),
              "projection": "orthographic XZ; front to left", "selected_occurrences": [i["id"] for i in selected],
              "fitting_performed": False}
    if cal["mode"] != "conditional_metric":
        record["limitation"] = "Side-by-side qualitative comparison only; no metric transform is assigned."
        return record, ""
    origin_x, origin_z = point(data, specification["calibration"], [0,0])
    x1,z1 = point(data, specification["calibration"], [1,1])
    sx,sz = x1-origin_x,z1-origin_z
    w,h = source.size
    source_bytes = io.BytesIO()
    source.save(source_bytes, format="PNG")
    svg = [f'<svg id="{key}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
           f'<image width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(source_bytes.getvalue()).decode()}"/>',
           '<g class="cad-layer" fill="none" stroke-width="1.6" opacity="0.75">']
    for item in selected:
        color = "#%02x%02x%02x" % tuple(int(v*205) for v in COLORS[item["system"]])
        svg.append(f'<g data-system="{item["system"]}" stroke="{color}"><title>{html.escape(item["id"])}</title>')
        for edge in item["shape"].Edges:
            points = edge.discretize(Deflection=2.0)
            coords = " ".join(f"{(p.x-origin_x)/sx:.3f},{(p.z-origin_z)/sz:.3f}" for p in points)
            svg.append(f'<polyline points="{coords}"/>')
        svg.append("</g>")
    svg.append("</g></svg>")
    overlay = "\n".join(svg)
    (folder / (key + "_overlay.svg")).write_text(overlay)
    with fitz.open(stream=overlay.encode(), filetype="svg") as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(str(folder / (key + "_overlay.png")))
    checks = []
    for check in cal.get("checks", []):
        scale = abs(sx if check["axis"] == "x" else sz)
        measured = abs(check["pixels"][1]-check["pixels"][0])*scale
        target = data["values"][check["parameter"]].value
        allowance = 2*cal["point_uncertainty_px"]*scale
        checks.append(dict(check, measured_mm=measured, target_mm=target,
                           residual_mm=measured-target, picking_allowance_mm=allowance,
                           within_picking_allowance=abs(measured-target)<=allowance))
    record["independent_calibration_checks"] = checks
    record["limitation"] = "Source-traced profiles agree by construction. Independent handbook comparison and held-out dimensions are separate evidence."
    return record, overlay


def run(data, items, out):
    folder = out / "comparisons"
    folder.mkdir(parents=True, exist_ok=True)
    visible = [i for i in items if i["definition"] not in {"central_hull", "track_frame", "track_path", "track_pin", "track_bushing", "track_cotter", "track_rivet"}]
    context = [i for i in items if i["definition"] in {"central_hull", "track_frame", "track_path"}]
    for name,direction in [("isometric",(1,1,0.6)),("side",(0,1,0)),("front",(1,0,0)),("top",(0,0,1))]:
        shaded(visible, out / "previews" / (name + ".svg"), direction, "Mark VIII | reconstruction in progress", context)
    reports, sections = [], []
    for spec in data["visual_reviews"]["comparisons"]:
        record, overlay = comparison(data, items, spec, folder)
        reports.append(record)
        key = spec["id"]
        sections += [f'<h2>{html.escape(key)}</h2><p>{html.escape(spec["description"])}</p>',
                     f'<div class="pair"><figure><img src="{key}_source.png"><figcaption>Source</figcaption></figure>',
                     f'<figure><img src="{key}_cad.png"><figcaption>Native geometry, selected installation envelopes</figcaption></figure></div>']
        if overlay:
            sections += ['<p>Overlay opacity <input class="opacity" type="range" min="0" max="1" step=".05" value=".75"></p>', overlay]
    track = [i for i in items if i["id"].startswith(tuple("PortTrack_Unit"+str(k).zfill(3)+"_" for k in range(3))) and i["representation"] == "assembly"]
    if track:
        for key,direction in [("track_top",(0,0,1)),("track_oblique",(0.18,0.28,1)),("track_side",(0,1,0))]:
            shaded(track, folder/(key+".svg"), direction, "Track unit | printed pitch retained",
                   up_direction=(1,0,0) if key != "track_side" else (0,0,1),
                   canvas=(900,1050) if key != "track_side" else (1600,450))
        source = "references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate84.png"
        Image.open(REPO/source).save(folder/"track_hb84_source.png")
        sections += ['<h2>Track unit — HB Plate 84</h2><p>Qualitative comparison of three units. Photograph perspective and CAD orthographic camera are not fitted. Printed width/pitch and SNL component counts govern the reconstruction.</p>',
                     '<div class="pair"><img src="track_hb84_source.png"><img src="track_oblique.png"></div>',
                     '<p><a href="track_top.png">Orthographic top</a> · <a href="track_side.png">Side / lapped eyes</a></p>']
        reports.append({"id":"track_hb84", "mode":"visual_only", "source":source,
                        "fitting_performed":False, "selected_occurrences":[i["id"] for i in track],
                        "limitation":"Photographic comparison; forging, pressing and fits remain reconstructed."})
    upper = [i for i in items if i["definition"].startswith("upper_")]
    if upper:
        for key,direction in [("upper_front",(1,1,.7)),("upper_rear",(-1,-1,.7)),("upper_underneath",(-1,-1,-.5))]:
            shaded(upper, folder/(key+".svg"), direction, "Upper plates | standard assembled configuration")
        source = "references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate30.png"
        Image.open(REPO/source).save(folder/"upper_hb30_source.png")
        source2 = "references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p281-geometry.png"
        Image.open(REPO/source2).save(folder/"upper_snl7_source.png")
        sections += ['<h2>Upper plate shells — HB30 and SNL7</h2><p>Standard closed leaves, hollow enclosures and individually identified plates. Printed HB35 dimensions control; perspective sources are qualitative. Fittings, covers and fasteners remain pending.</p>',
                     '<div class="pair"><img src="upper_hb30_source.png"><img src="upper_rear.png"></div>',
                     '<div class="pair"><img src="upper_snl7_source.png"><img src="upper_front.png"></div>',
                     '<p><a href="upper_underneath.png">Inspection from below, without moving any component</a></p>']
        reports.append({"id":"upper_plates", "mode":"visual_only", "source":source,"additional_source":source2,
                        "fitting_performed":False,"selected_occurrences":[i["id"] for i in upper],
                        "limitation":"Printed dimensions conflict with the fixed SNL2 side trace. Undimensioned form and joints remain approximate."})
    hull = [i for i in items if i["definition"].startswith(("hull_","upper_"))]
    if any(i["definition"].startswith("hull_") for i in hull):
        for key,direction in [("hull_oblique",(1,1,.7)),("hull_right_side",(0,-1,0)),("hull_rear",(-1,-1,.7)),("hull_underside",(-1,-1,-.7))]:
            shaded(hull,folder/(key+".svg"),direction,"Hull plates | standard assembly, partial detail")
        sources=[("hull_snl7","references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p281-geometry.png"),
                 ("hull_snl1","references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p277-geometry.png")]
        for key,source in sources:Image.open(REPO/source).save(folder/(key+"_source.png"))
        sections += ['<h2>Main hull plates — SNL7 and SNL1</h2><p>Source-identified shell plates, open sponson/louver apertures and closed split side doors. Seams and unprinted forms remain approximate; braces, chutes, roof strips and fittings are pending. Camera changes do not move parts.</p>',
                     '<div class="pair"><img src="hull_snl7_source.png"><img src="hull_oblique.png"></div>',
                     '<div class="pair"><img src="hull_snl1_source.png"><img src="hull_right_side.png"></div>',
                     '<p><a href="hull_rear.png">Rear inspection</a> · <a href="hull_underside.png">Underside inspection</a></p>']
        reports.append({"id":"hull_plates","mode":"visual_only","sources":[p for _,p in sources],
                        "fitting_performed":False,"selected_occurrences":[i["id"] for i in hull],
                        "limitation":"Photographic/oblique comparisons are qualitative. The fixed SNL2 overlay remains independent of these camera views."})
    sponsons=[i for i in items if i['definition'].startswith('sponson_') and i['representation']=='assembly']
    if sponsons:
        port=[i for i in sponsons if i['id'].startswith('sponson_port_')]
        starboard=[i for i in sponsons if i['id'].startswith('sponson_starboard_')]
        for key,selected,direction in [('sponson_port',port,(1,1,.65)),('sponson_starboard',starboard,(1,-1,.65)),
                                       ('sponson_inside',port,(-.3,-1,.55)),('sponson_underneath',port,(1,1,-.65))]:
            shaded(selected,folder/(key+'.svg'),direction,'Sponson plates | standard installation, partial detail')
        source='references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p281-geometry.png'
        Image.open(REPO/source).save(folder/'sponson_snl7_source.png')
        sections += ['<h2>Standard sponson shells — SNL7</h2><p>Individual plates with hollow interiors and handed viewing openings. Armor thicknesses are printed; tapered contours, lower rake, shield infills and seams are approximations. Rotating gun shields/mounts, hinges, support gear and fittings remain pending.</p>',
                     '<div class="pair"><img src="sponson_snl7_source.png"><img src="sponson_port.png"></div>',
                     '<div class="pair"><img src="sponson_starboard.png"><img src="sponson_inside.png"></div>',
                     '<p><a href="sponson_underneath.png">Underside inspection without moving components</a></p>']
        reports.append({'id':'sponson_plates','mode':'visual_only','source':source,'fitting_performed':False,
                        'selected_occurrences':[i['id'] for i in sponsons],
                        'limitation':'Source topology informs the reconstruction; unprinted geometry, thickness scope and M2764 handedness remain provisional.'})
    louvers=[i for i in items if i['definition'].startswith('louver_')]
    if louvers:
        for key,direction in [('louvers_oblique',(-1,1,.9)),('louvers_top',(0,0,1)),('louvers_end',(-1,0,.2))]:
            shaded(louvers,folder/(key+'.svg'),direction,'Roof louvers | source counts, provisional section and frames')
        close=[i for i in louvers if i['id'] in {'louver_inlet_blade_015','louver_inlet_blade_016','louver_inlet_blade_017'}]
        from .louver_geometry import layout as louver_layout
        a=louver_layout(data,'inlet')
        shaded(close,folder/'louver_blade_section.svg',(-a['cosine'],0,-a['cosine']*a['slope']),
               'Three inlet blades | 6 mm armor, provisional bend interpretation')
        source='references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p278-geometry.png'
        Image.open(REPO/source).save(folder/'louvers_snl4_source.png')
        sections += ['<h2>Engine-roof louvers — SNL4/7</h2><p>Lengthwise blades follow the top-view photograph. Counts provisionally follow the later SNL (34 inlet, 28 outlet); handbook alternatives remain recorded. Bent sections, radius reference, guard assignment and frame details are provisional. Spacing/support hardware remains pending.</p>',
                     '<div class="pair"><img src="louvers_snl4_source.png"><img src="louvers_oblique.png"></div>',
                     '<p><a href="louvers_top.png">Top inspection</a> · <a href="louvers_end.png">End inspection</a> · <a href="louver_blade_section.png">Three-blade section</a></p>']
        reports.append({'id':'roof_louvers','mode':'visual_only','source':source,'fitting_performed':False,
                        'selected_occurrences':[i['id'] for i in louvers],
                        'limitation':'Perspective photograph supports broad orientation; it does not resolve blade section, pitch or conflicting quantities.'})
    rollers=[i for i in items if i['definition'].startswith('roller_')]
    if rollers:
        for number,kind in [(0,'plain'),(1,'spring'),(29,'upper')]:
            stack=[i for i in rollers if i['id'].startswith(f'PortRollers_Unit{number:03d}_')]
            shaded(stack,folder/('roller_'+kind+'.svg'),(1,1,.7),'Roller '+kind+' stack | partial source reconstruction')
        port=[i for i in rollers if i['id'].startswith('Port')]
        track=[i for i in items if i['id'].startswith('PortTrack_') and i['definition'] in {'track_shoe','track_link_left','track_link_right'}]
        shaded(port+track,folder/'roller_rail_installation.svg',(0,1,0),'Roller stations and native rails | hull omitted')
        shaded(rollers,folder/'roller_banks.svg',(1,1,.6),'60 roller stations | lower and upper quantity scopes retained')
        from types import SimpleNamespace
        import Part
        from .roller_geometry import stations
        for number,kind in [(1,'spring'),(29,'upper')]:
            x=stations(data)[number]['x']
            cutting=Part.makeBox(20000,10000,10000,App.Vector(x,-5000,-5000))
            section=[]
            for item in [i for i in rollers if i['id'].startswith(f'PortRollers_Unit{number:03d}_')]:
                shape=item['shape'].cut(cutting)
                if shape.Solids:
                    section.append(dict(item,definition=item['id'],shape=shape,target=SimpleNamespace(Shape=shape)))
            shaded(section,folder/('roller_'+kind+'_section.svg'),(1,0,0),kind.title()+' stack section | dimensions and forms remain provisional')
        sources={
            'roller_hb88':'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate88.png',
            'roller_hb89':'references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate89.png',
            'roller_snl29':'references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p301-geometry.png'}
        for key,source in sources.items():
            Image.open(REPO/source).save(folder/(key+'_source.png'))
            reports.append(dict(id=key,mode='visual_only',source=source,fitting_performed=False,
                limitation='Qualitative topology comparison; no transverse calibration or perspective fit is claimed.'))
        sections += ['<h2>Lower and upper roller stacks</h2><p>58 lower stations (28 spring / 30 plain), plus two handbook upper stations and four partial M2092 upper angles. Pin flats and flange/washer seats follow the suspended-toe topology. Lower long angles and their attachment bolts are shown below; upper attachments/covers and lower removable retention remain incomplete.</p>',
            '<div class="pair"><img src="roller_hb88_source.png"><img src="roller_upper.png"></div>',
            '<div class="pair"><img src="roller_hb88_source.png"><img src="roller_upper_section.png"></div>',
            '<div class="pair"><img src="roller_hb89_source.png"><img src="roller_spring.png"></div>',
            '<div class="pair"><img src="roller_snl29_source.png"><img src="roller_spring_section.png"></div>',
            '<p><a href="roller_plain.png">Plain lower stack</a> · <a href="roller_rail_installation.png">Installed stations and rails</a> · <a href="roller_banks.png">Both roller banks</a></p>']
    wheels=[i for i in items if i['id'].startswith('PortIdler_')]
    if wheels:
        for key,direction in [('idler_oblique',(1,1,.6)),('idler_elevation',(0,1,0))]:
            shaded(wheels,folder/(key+'.svg'),direction,'Idler wheel and adjustment | partial reconstructed installation')
        import Part
        from .wheel_geometry import station
        st=station(data);section=[]
        half=Part.makeBox(20000,10000,10000,App.Vector(st['x']-20000, -5000, -2000))
        for item in wheels:
            shape=item['shape'].common(half)
            if not shape.isNull() and shape.Faces:
                # The renderer expects local target geometry, so create a
                # temporary feature matching the section's world coordinates.
                class Target:pass
                target=Target();target.Shape=shape
                section.append(dict(item,shape=shape,target=target,definition=item['id']))
        shaded(section,folder/'idler_section.svg',(1,0,0),'Idler transverse half section | approximate formed diaphragm')
        neighbors=[i for i in items if i['id'].startswith(tuple(f'PortTrack_Unit{k:03d}_' for k in range(18,27)))
                   and i['definition'] in {'track_link_left','track_link_right','track_bushing','track_shoe'}]
        neighbors += [i for i in items if i['id'].startswith('PortRollers_Unit000_')]
        shaded(wheels+neighbors,folder/'idler_installation.svg',(0,1,0),'Front idler / track / foremost roller | static fit only')
        source='references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate87.png'
        Image.open(REPO/source).save(folder/'idler_hb87_source.png')
        sections += ['<h2>Front idler wheels — HB87 / SNL28</h2><p>Two rims, two perforated disks, a boss, five X and one Y diaphragm, 108 rivets and two bushes per wheel. Shafts, adjustment screws, brackets, plates, guards and retaining hardware are now populated. X/Y distinguishing form, exact profiles, guard retention and inner plate attachments remain unresolved.</p>',
            '<div class="pair"><img src="idler_hb87_source.png"><img src="idler_elevation.png"></div>',
            '<div class="pair"><img src="idler_hb87_source.png"><img src="idler_section.png"></div>',
            '<p><a href="idler_oblique.png">Oblique wheel</a> · <a href="idler_installation.png">Installed track and foremost roller</a></p>']
        mounts=[i for i in wheels if not i['definition'].startswith('wheel_')]
        shaded(mounts,folder/'idler_mount_detail.svg',(1,1,.6),'Idler shaft and mounting hardware | profiles and drilling inferred')
        from .idler_geometry import values as idler_values
        iv=idler_values(data);center=data['values']['track_centers'].value/2
        half=Part.makeBox(20000,iv['screw_y'],10000,App.Vector(-5000,center,-2000));cut=[]
        for item in mounts:
            shape=item['shape'].common(half)
            if not shape.isNull() and shape.Faces:
                class Target:pass
                target=Target();target.Shape=shape
                cut.append(dict(item,shape=shape,target=target,definition=item['id']))
        shaded(cut,folder/'idler_mount_section.svg',(0,1,0),'Idler mounting section through adjusting screw axis | static only')
        sections += ['<div class="pair"><img src="idler_hb87_source.png"><img src="idler_mount_detail.png"></div>',
                     '<p><a href="idler_mount_section.png">Adjustment-axis section</a>. Source-counted hardware is separate; threads and exact casting profiles remain approximate.</p>']
        reports.append({'id':'idler_wheels','mode':'visual_only','source':source,
                        'fitting_performed':False,'selected_occurrences':[i['id'] for i in wheels]})
    drives=[i for i in items if i['id'].startswith('PortDrive_')]
    if drives:
        import Part
        from types import SimpleNamespace
        from .cad_build import frame
        center=frame('port_drive',data).Base
        for key,direction in [('drive_oblique',(1,1,.6)),('drive_elevation',(0,1,0))]:
            shaded(drives,folder/(key+'.svg'),direction,
                   'Drive wheel | 35-tooth hypothesis | shaft and supports pending')
        half=Part.makeBox(20000,10000,10000,App.Vector(center.x-20000,-5000,-2000));cut=[]
        for item in drives:
            shape=item['shape'].common(half)
            if shape.Faces:
                cut.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),definition=item['id']))
        shaded(cut,folder/'drive_section.svg',(1,0,0),'Drive transverse half section | inferred shared wheel interface')
        neighbors=[]
        for item in items:
            if not item['id'].startswith('PortTrack_') or item['definition'] not in {'track_shoe','track_link_left','track_link_right','track_bushing'}:continue
            b=item['shape'].optimalBoundingBox(False)
            if b.XMin<center.x+750 and b.XMax>center.x-750:neighbors.append(item)
        shaded(drives+neighbors,folder/'drive_installation.svg',(0,1,0),
               'Fixed drive axis and track | static clearance only; engagement unresolved')
        source='references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate86.png'
        Image.open(REPO/source).save(folder/'drive_hb86_source.png')
        snl='references/1928-03-30_SNL_G13/SNL_G13_Project/assets/p299-geometry.png'
        Image.open(REPO/snl).save(folder/'drive_snl27_source.png')
        section_source='references/1925-03-06_Preliminary_Handbook_Mark_VIII_Tank/Handbook_Project/assets/plate125.png'
        Image.open(REPO/section_source).save(folder/'drive_hb125_source.png')
        sections += ['<h2>Driving wheels — HB86 / SNL27</h2><p>Each wheel has two M1401 toothed rims and the same boss, disks, diaphragms and rivet definitions as the idlers. Two M1409 bushes are included; five shaft-assembly constituents per side and the separate bearing supports remain pending. HB130/HB133 print 35 teeth, while HB119 prints 9:37. Circular reliefs and crest rounding are explicit hypotheses; operating engagement is unresolved.</p>',
            '<div class="pair"><img src="drive_hb86_source.png"><img src="drive_oblique.png"></div>',
            '<div class="pair"><img src="drive_snl27_source.png"><img src="drive_elevation.png"></div>',
            '<div class="pair"><img src="drive_hb125_source.png"><img src="drive_section.png"></div>',
            '<p><a href="drive_section.png">Shared-interface section</a> · <a href="drive_installation.png">Drive/track installation</a></p>']
        reports.append(dict(id='drive_wheels',mode='visual_only',source=source,additional_source=snl,
            section_source=section_source,
            fitting_performed=False,selected_occurrences=[i['id'] for i in drives],
            limitation='Source-common definitions and static fit; exact profiles, source tooth conflict, shafts/supports and operating engagement remain unresolved.'))
    lower=[i for i in items if i['id'].startswith('PortLowerSupports_')]
    if lower:
        bank=[i for i in items if i['id'].startswith('PortRollers_') and not i['id'].startswith('PortRollers_Unit029_')]
        shaded(lower+bank,folder/'lower_support_bank.svg',(0,1,.35),'Port bank: 17 lower angles and 38 bolts | vehicle total: 34 angles and 76 bolts',canvas=(1900,500))
        for name,indices,runs in [('front',range(6),['01','02','03']),('rear',range(23,29),['08'])]:
            group=[i for i in bank if i['id'].startswith(tuple(f'PortRollers_Unit{k:03d}_' for k in indices))]
            group += [i for i in lower if any('_Run'+key+'_' in i['id'] for key in runs)]
            shaded(group,folder/('lower_support_'+name+'.svg'),(1,1,.6),'Lower supports | '+name+' | contours and retention remain partial')
            if name=='front':
                import Part
                from types import SimpleNamespace
                slab=Part.makeBox(2450,800,1100,App.Vector(7000,500,100));context=[]
                for item in items:
                    if not item['definition'].startswith('hull_port_'):continue
                    if not item['shape'].optimalBoundingBox(False).intersect(slab.optimalBoundingBox(False)):continue
                    shape=item['shape'].common(slab)
                    if shape.Solids:
                        context.append(dict(item,shape=shape,target=SimpleNamespace(Shape=shape),
                                            definition=item['definition']+'_front_crop'))
                shaded(group+context,folder/'lower_support_front_in_hull.svg',(1,1,.6),
                       'Front skirt and installed supports | diagnostic section crop')
        source=data['calibrations']['snl_2']['image']
        from PIL import ImageDraw,ImageFont
        calibration=data['calibrations']['snl_2']
        trace=Image.open(REPO/source).convert('RGB');drawing=ImageDraw.Draw(trace)
        for key,color in [('hull_initial_layout','#c83227'),('hull','#0579b4')]:
            points=[tuple(p) for p in calibration['profiles'][key]]
            drawing.line(points+[points[0]],fill=color,width=1)
        crop=trace.crop((100,310,750,570)).resize((1625,650),Image.Resampling.NEAREST)
        border_image=Image.new('RGB',(1625,700),'#f5f3eb');border_image.paste(crop,(0,50))
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
        ImageDraw.Draw(border_image).text((15,12),
            'SNL Plate 2 | red: initial coarse hull profile | blue: revised front border and retained transition',
            fill='#29382f',font=font)
        border_image.save(folder/'lower_front_border_review.png')
        sections += ['<h2>Lower support runs — SNL Plate 2 / HB89</h2><p>All 34 angles and 76 short bolts are separate source-counted parts. Front units follow inclined pin seats. Inner No5 retains both printed lengths. Rear run ownership, curved profiles, tapped receiving holes and HB144 removable retention remain unresolved.</p>',
                     '<img src="snl_longitudinal_source.png"><img src="lower_support_bank.png">',
                     '<div class="pair"><img src="roller_hb89_source.png"><img src="lower_support_front.png"></div>',
                     '<img src="lower_support_front_in_hull.png"><img src="lower_front_border_review.png">',
                     '<p>The diagnostic hull crop exposes installed support seats. The border comparison retains original source pixels and both traces. A separately recorded 6 mm nose setback provides native track-rivet clearance; it does not alter the source calibration. The middle transition and remaining outline are still approximate.</p>',
                     '<p><a href="lower_support_rear.png">Rear support detail</a>. Arrangement comparison only; no camera or source-scale fitting was performed.</p>']
        reports.append(dict(id='lower_supports',mode='visual_only',source=source,fitting_performed=False,
                            selected_occurrences=[i['id'] for i in lower+bank]))
    findings = data["visual_reviews"]["findings"]
    sections.append("<h2>Recorded findings</h2>")
    for finding in findings:
        sections.append(f'<p><b>{html.escape(finding["id"])} — {html.escape(finding["subject"])}</b>: '
                        f'{html.escape(finding["finding"])}<br>Next: {html.escape(finding["action"])}</p>')
    page = """<!doctype html><meta charset="utf-8"><title>Mark VIII source comparisons</title>
<style>body{font:16px system-ui;margin:2em;background:#f8f7f1;color:#252d27}img,svg{width:100%}.pair{display:grid;grid-template-columns:1fr 1fr;gap:1em}figure{margin:0}figcaption{font-size:14px}input{vertical-align:middle;width:18em}</style>
<h1>Source comparisons — reconstruction in progress</h1>
<p>The CAD views come from the actual installed native solids. Source images retain their pixels;
the SNL overlay uses the recorded calibration without refitting. Discrepancies require interpretation,
not automatic geometry correction. Layout envelopes do not count as completed component models.</p>
<p>Whole-vehicle preview/overlay views omit small track pins, bushings, cotters and rivets for legibility and rendering cost. Native CAD, STEP and the close track views retain every component.</p>
""" + "\n".join(sections) + """
<script>for(const slider of document.querySelectorAll('.opacity')){slider.addEventListener('input',()=>{slider.parentElement.nextElementSibling.querySelector('.cad-layer').style.opacity=slider.value;});}</script>"""
    (folder / "index.html").write_text(page)
    result = {"comparisons": reports, "findings": findings,
              "review_status": "generated_pending_visual_inspection",
              "previous_inspection": data["visual_reviews"].get("inspection")}
    write(folder / "report.json", result)
    return result
