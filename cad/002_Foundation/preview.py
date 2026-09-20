"""Portable shaded CAD previews, with exact B-rep edge projections alongside them."""
import html
import base64
import io
from pathlib import Path

import fitz
import numpy as np
from PIL import Image
import FreeCAD as App
import Part
import TechDraw


def render(items, path, direction, title):
    """Orthographic tessellation is for the preview only; FCStd/STEP remain exact B-rep."""
    d=App.Vector(*direction);d.normalize()
    up=App.Vector(0,0,1)
    if abs(d.dot(up))>0.99:up=App.Vector(0,1,0)
    right=up.cross(d);right.normalize();up=d.cross(right);up.normalize()
    tris=[];lines=[];coords=[]
    for label,shape,is_ref in items:
        color=(157,176,184) if is_ref else (143,124,75)
        for face in shape.Faces:
            vertices,indices=face.tessellate(2.0 if is_ref else 0.15)
            for tri in indices:
                vs=[vertices[i] for i in tri]
                normal=(vs[1]-vs[0]).cross(vs[2]-vs[0]);normal.normalize()
                light=0.57+0.38*abs(normal.dot(App.Vector(0.3,-0.5,0.8)))
                rgb=tuple(min(255,int(c*light)) for c in color)
                p=[(q.dot(right),-q.dot(up)) for q in vs];coords+=p
                tris.append(([q.dot(d) for q in vs],p,rgb))
        for edge in shape.Edges:
            try:vertices=edge.discretize(Deflection=0.2)
            except Exception:vertices=edge.discretize(Number=12)
            p=[(q.dot(right),-q.dot(up)) for q in vertices];coords+=p
            lines.append((p,is_ref))
    if not coords:raise ValueError('Empty preview')
    xmin,xmax=min(x for x,y in coords),max(x for x,y in coords)
    ymin,ymax=min(y for x,y in coords),max(y for x,y in coords)
    width,height=1400,850;scale=min((width-100)/max(xmax-xmin,1),(height-130)/max(ymax-ymin,1))
    def screen(ps):return [(50+(x-xmin)*scale,85+(y-ymin)*scale) for x,y in ps]
    def points(ps):return ' '.join(f'{x:.2f},{y:.2f}' for x,y in screen(ps))
    # A real depth buffer is necessary: sorting whole triangles by mean depth
    # draws large plate faces over smaller foreground parts at some viewpoints.
    pixels=np.full((height,width,3),(246,244,237),dtype=np.uint8)
    zbuffer=np.full((height,width),-np.inf)
    for depths,ps,rgb in tris:
        (ax,ay),(bx,by),(cx,cy)=screen(ps)
        x0=max(0,int(min(ax,bx,cx)));x1=min(width,int(max(ax,bx,cx))+2)
        y0=max(0,int(min(ay,by,cy)));y1=min(height,int(max(ay,by,cy))+2)
        denominator=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
        if abs(denominator)<1e-10 or x0>=x1 or y0>=y1:continue
        yy,xx=np.mgrid[y0:y1,x0:x1];xx=xx+0.5;yy=yy+0.5
        a=((by-cy)*(xx-cx)+(cx-bx)*(yy-cy))/denominator
        b=((cy-ay)*(xx-cx)+(ax-cx)*(yy-cy))/denominator
        c=1-a-b
        depth=a*depths[0]+b*depths[1]+c*depths[2]
        target=zbuffer[y0:y1,x0:x1]
        mask=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)&(depth>target)
        target[mask]=depth[mask];pixels[y0:y1,x0:x1][mask]=rgb
    buffer=io.BytesIO();Image.fromarray(pixels).save(buffer,format='PNG')
    bitmap=base64.b64encode(buffer.getvalue()).decode()
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         f'<image width="{width}" height="{height}" href="data:image/png;base64,{bitmap}"/>',
         f'<text x="40" y="34" font-family="sans-serif" font-size="22">{html.escape(title)}</text>',
         '<text x="40" y="59" font-family="sans-serif" font-size="14">Blue-grey: reference envelopes • ochre: physical pilot parts • documented approximations</text>']
    # Reference outlines remain visible through envelopes. Physical details use
    # opaque shaded faces; do not draw hidden rear edges through those solids.
    for ps,ref in lines:
        if ref:
            svg.append(f'<polyline points="{points(ps)}" fill="none" stroke="#526675" stroke-width="0.65" opacity="0.45"/>')
    svg.append('</svg>');text='\n'.join(svg)
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    with fitz.open(stream=text.encode(),filetype='svg') as doc:
        doc[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(str(path.with_suffix('.png')))


def exact_projection(shape, path, direction):
    # Native TechDraw hidden-line projection, retained as a vector artifact.
    fragment=TechDraw.projectToSVG(shape,App.Vector(*direction))
    # Use projected B-rep bounds for the viewport, not the source-space bounds.
    projected=TechDraw.project(shape,App.Vector(*direction))
    bounds=Part.makeCompound([s for s in projected if not s.isNull()]).BoundBox
    x,y=bounds.XMin,-bounds.YMax
    margin=max(bounds.XLength,bounds.YLength)*0.03+1
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-margin} {y-margin} '
         f'{bounds.XLength+2*margin} {bounds.YLength+2*margin}">'+fragment+'</svg>')
    Path(path).write_text(svg)
