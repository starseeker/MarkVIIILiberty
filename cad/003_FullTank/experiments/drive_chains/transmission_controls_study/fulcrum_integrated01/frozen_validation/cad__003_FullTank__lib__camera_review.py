"""Render saved FreeCAD occurrence geometry in an explicitly calibrated camera.

No fitAll, image warp, geometry editing or automatic acceptance. Tessellation is
for visual review only; native solids and exchange checks retain their own gates.
"""
import copy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial.transform import Rotation
from .source_camera import project


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rigid_frame(values):
    matrix = np.asarray(values,dtype=float).reshape(4,4)
    if not np.isfinite(matrix).all() or not np.allclose(matrix[3],[0,0,0,1],rtol=0,atol=1e-9):
        raise ValueError('Invalid affine frame')
    rotation = matrix[:3,:3]
    if not np.allclose(rotation.T@rotation,np.eye(3),rtol=0,atol=1e-8) or abs(np.linalg.det(rotation)-1)>1e-8:
        raise ValueError('Only proper rigid occurrence frames are supported')
    return matrix


def validate_native_bindings(packet, manifest):
    """Check selected archive shapes and composed frames against the saved FCStd."""
    selected=set(packet.get('render_occurrences',[]))
    selected.update(v['anchor']['occurrence'] for v in packet['landmarks'])
    rows={v['name']:v for v in manifest['occurrences']}
    with zipfile.ZipFile(packet['native_file']) as archive:
        tree=ET.fromstring(archive.read('Document.xml'))
        objects={v.get('name'):v for v in tree.findall('./ObjectData/Object')}
        types={v.get('name'):v.get('type') for v in tree.findall('./Objects/Object')}
        def prop(name, key): return objects[name].find('./Properties/Property[@name="'+key+'"]')
        def placement(name, key='Placement'):
            p=prop(name,key).find('PropertyPlacement')
            matrix=np.eye(4)
            matrix[:3,:3]=Rotation.from_quat([float(p.get('Q'+str(i))) for i in range(4)]).as_matrix()
            matrix[:3,3]=[float(p.get('P'+v)) for v in 'xyz']
            return matrix
        frames={}
        def walk(name, parent, seen):
            if name in seen: raise ValueError('Native ancestry cycle')
            if types[name]=='App::Link':
                if name in frames: raise ValueError('Multiple native occurrence paths')
                frames[name]=parent@placement(name,'LinkPlacement')
            elif types[name]=='App::Part':
                world=parent@placement(name)
                for child in prop(name,'Group').findall('./LinkList/Link'):
                    walk(child.get('value'),world,seen|{name})
            else: raise ValueError('Unsupported native assembly child: '+name)
        walk('Root',np.eye(4),set())
        checked=set()
        for name in selected:
            row=rows[name];obj=row['object'];definition=manifest['definitions'][row['definition']]
            link=prop(obj,'LinkedObject').find('XLink')
            if link.get('file') or link.get('name')!=row['definition']:
                raise ValueError('Native definition binding differs from manifest')
            scale=float(prop(obj,'Scale').find('Float').get('value'))
            vector=prop(obj,'ScaleVector').find('PropertyVector')
            if abs(scale-1)>1e-12 or any(abs(float(vector.get('value'+v))-1)>1e-12 for v in 'XYZ'):
                raise ValueError('Scaled native links are unsupported')
            if not np.allclose(frames[obj],rigid_frame(row['frame']),rtol=0,atol=1e-7):
                raise ValueError('Native placement differs from manifest: '+name)
            if not np.allclose(placement(row['definition']),np.eye(4),rtol=0,atol=1e-9):
                raise ValueError('Nonidentity native definition placement')
            if row['definition'] not in checked:
                entry=prop(row['definition'],'Shape').find('Part').get('file')
                if entry!=definition['archive_entry'] or hashlib.sha256(archive.read(entry)).hexdigest()!=definition['brep_sha256']:
                    raise ValueError('Native shape differs from manifest')
                checked.add(row['definition'])


def resolve_packet(packet):
    """Re-evaluate anchor coordinates from current extracted native placements.

Changed anchor definitions need an explicit locator review even if a local point
has the same coordinates. Unrelated geometry is deliberately absent from fit keys.
"""
    result=copy.deepcopy(packet)
    manifest=json.loads(Path(packet['manifest']).read_text())
    native=sha(packet['native_file'])
    if native!=manifest['native_sha256']: raise ValueError('Manifest does not match saved native geometry')
    validate_native_bindings(packet,manifest)
    rows={v['name']:v for v in manifest['occurrences']}
    bindings=[]
    for row in result['landmarks']:
        anchor=row['anchor'];occurrence=rows[anchor['occurrence']]
        definition=manifest['definitions'][occurrence['definition']]
        if not anchor.get('evidence'): raise ValueError('Landmark basis/evidence is required')
        if definition['brep_sha256']!=anchor['definition_sha256']:
            raise ValueError('Anchor definition changed; reverify locator: '+row['id'])
        if sha(definition['brep_path'])!=definition['brep_sha256']:
            raise ValueError('Anchor BRep changed')
        if not np.allclose(rigid_frame(definition['frame']),np.eye(4),rtol=0,atol=1e-9):
            raise ValueError('Only identity-frame shape definitions supported')
        frame=rigid_frame(occurrence['frame'])
        local=np.asarray(anchor['local_mm'],dtype=float)
        if local.shape!=(3,) or not np.isfinite(local).all(): raise ValueError('Invalid local anchor')
        row['world_mm']=(frame[:3,:3]@local+frame[:3,3]).tolist()
        bindings.append(dict(id=row['id'],occurrence=occurrence['name'],definition=occurrence['definition'],
                             definition_sha256=definition['brep_sha256'],world_mm=row['world_mm']))
    result['geometry_context']=dict(native_sha256=native,manifest_sha256=sha(packet['manifest']),anchor_bindings=bindings)
    return result,manifest


def render(packet,manifest,camera,out,runtime):
    import FreeCAD as App
    import Part
    from .raster import paint
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    width,height=camera['image_size_px']
    rows={v['name']:v for v in manifest['occurrences']}
    selected=packet['render_occurrences']
    if not selected or len(set(selected))!=len(selected): raise ValueError('Select unique render occurrences')
    deflection=float(packet.get('tessellation_mm',.5))
    if not np.isfinite(deflection) or deflection<=0: raise ValueError('Invalid display tessellation')
    cache={};triangles=[];colors=[];bindings=[]
    for name in selected:
        row=rows[name];definition=manifest['definitions'][row['definition']]
        key=definition['brep_sha256'];path=definition['brep_path']
        if not np.allclose(rigid_frame(definition['frame']),np.eye(4),rtol=0,atol=1e-9):
            raise ValueError('Only identity-frame shape definitions supported')
        if key not in cache:
            if sha(path)!=key: raise ValueError('Rendered BRep changed')
            shape=Part.Shape();shape.read(str(path))
            vertices,indices=shape.tessellate(deflection)
            cache[key]=(np.array([[v.x,v.y,v.z] for v in vertices]),np.array(indices,dtype=np.int32))
        local,indices=cache[key]
        if not len(indices): raise ValueError('Selected occurrence has no display faces: '+name)
        matrix=rigid_frame(row['frame']);world=local@matrix[:3,:3].T+matrix[:3,3]
        # Independently check matrix interpretation against the CAD runtime.
        expected=App.Placement(App.Matrix(*row['frame'])).multVec(App.Vector(*local[0]))
        if np.linalg.norm(world[0]-[expected.x,expected.y,expected.z])>1e-7:
            raise ValueError('Display placement differs from native placement')
        # Explicit failure across the near plane; do not silently drop geometry.
        projected=project(world,camera)
        cells=world[indices];normal=np.cross(cells[:,1]-cells[:,0],cells[:,2]-cells[:,0])
        length=np.linalg.norm(normal,axis=1);valid=length>1e-12
        normal=normal[valid]/length[valid,None]
        lighting=.5+.45*np.abs(normal@np.array([.3,-.4,.8660254]))
        color=packet.get('render_colors',{}).get(name,[.27,.60,.65])
        triangles.append(projected[indices[valid]])
        colors.append(np.clip(lighting[:,None]*np.array(color)*255,0,255).astype(np.uint8))
        bindings.append(dict(occurrence=name,definition_sha256=key,frame=row['frame']))
    pixels,depth=paint(np.concatenate(triangles),np.concatenate(colors),width,height,runtime)
    foreground=np.isfinite(depth)
    rgba=np.dstack([pixels,foreground.astype(np.uint8)*255])
    Image.fromarray(rgba).save(out/'geometry.png')
    with Image.open(packet['source_image']) as image: source=image.convert('RGB')
    combined=np.array(source).copy()
    combined[foreground]=np.rint(combined[foreground]*.55+pixels[foreground]*.45).astype(np.uint8)
    overlay=Image.fromarray(combined);draw=ImageDraw.Draw(overlay)
    for landmark in packet['landmarks']:
        px,py=landmark['pixel'];uv=project([landmark['world_mm']],camera)[0,:2]
        color='#0076b8' if landmark['use']=='fit' else '#d33183'
        draw.ellipse((px-4,py-4,px+4,py+4),outline=color,width=2)
        draw.line((px,py,*uv),fill=color,width=2)
        draw.line((uv[0]-3,uv[1],uv[0]+3,uv[1]),fill=color,width=1)
        draw.line((uv[0],uv[1]-3,uv[0],uv[1]+3),fill=color,width=1)
        draw.text((px+5,py+3),landmark['id'],fill=color)
    overlay.save(out/'overlay.png')
    return dict(images={name:sha(out/name) for name in ['geometry.png','overlay.png']},
                bindings=bindings,tessellation_mm=deflection,foreground_pixels=int(foreground.sum()),
                native_sha256=manifest['native_sha256'],camera_pixel_mapping='original source pixels; no automatic framing',
                limitation='Display mesh only. Near-plane crossings fail explicitly. Affine depth uses row cross-product convention.',
                renderer_sha256=sha(__file__),raster_sha256=sha(Path(__file__).with_name('raster.c')))
