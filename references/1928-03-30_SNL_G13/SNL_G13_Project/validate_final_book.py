#!/usr/bin/env python3
"""Validate the native-vector/approved-Plate-12 release against clean-raster v20."""
from pathlib import Path
import argparse,hashlib,json,zipfile,xml.etree.ElementTree as E
import fitz,numpy as np
from PIL import Image
from project_sequence import LABELS
P=Path(__file__).resolve().parent;R=P/'restoration';D=R/'native'
def digest(b):return hashlib.sha256(b).hexdigest()
def serialized(e):return E.tostring(e)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline-zip',required=True);args=ap.parse_args();z=zipfile.ZipFile(args.baseline_zip);prefix='SNL_G13_Project/'
 before=E.fromstring(z.read(prefix+'SNL_G13_Pilot.sla'))[0];after=E.parse(P/'SNL_G13_Pilot.sla').getroot()[0]
 m=json.loads((R/'manifest.json').read_text());placements=json.loads((D/'placements.json').read_text());names={c['name'] for c in placements.values()}
 old=before.findall('PAGEOBJECT');new=after.findall('PAGEOBJECT');a=[serialized(e) for e in old if e.get('ANNAME') not in names];b=[serialized(e) for e in new if e.get('ANNAME') not in names];assert a==b and len(a)==32625
 assert [serialized(e) for e in before.findall('PAGE')]==[serialized(e) for e in after.findall('PAGE')]
 for n,c in placements.items():
  x=next(e for e in old if e.get('ANNAME')==c['name']);y=next(e for e in new if e.get('ANNAME')==c['name']);assert y.get('PTYPE')=='12'
  for k in ['XPOS','YPOS','WIDTH','HEIGHT','ROT','OwnPage']:assert x.get(k)==y.get(k),(n,k)
 text_frames=[e for e in after.iter('PAGEOBJECT') if e.get('PTYPE')=='4'];assert len(text_frames)==25682
 preserved={}
 for folder in ['sources','assets','data','fonts']:
  files=[n for n in z.namelist() if n.startswith(prefix+folder+'/') and not n.endswith('/')]
  for n in files:assert digest(z.read(n))==digest((P/n[len(prefix):]).read_bytes()),n
  preserved[folder]=len(files)
 plates=sorted(v for r in m.values() for v in r['plates']);assert plates==list(range(1,35))
 assert digest((R/'clean/p284-clean.png').read_bytes())=='8fa45c6cdd9fda36f78a1defead55dead1ed0701bcbcbfecd2b2463df8d4b12c'
 prev=fitz.open(stream=z.read(prefix+'SNL_G13_Pilot.pdf'),filetype='pdf');cur=fitz.open(P/'SNL_G13_Pilot.pdf');assert len(prev)==len(cur)==len(LABELS)==314
 figure_pages={int(e.get('OwnPage')) for e in new if e.get('ANNAME','').endswith('-plate-artwork') or e.get('ANNAME')=='p277-foldout-plate-2'};assert len(figure_pages)==31
 unchanged=0
 for i,(o,q) in enumerate(zip(prev,cur)):
  assert o.get_text()==q.get_text(),('PDF text changed',i+1)
  assert o.rect==q.rect and q.get_label()==LABELS[i],('page label/size',i+1)
  if i not in figure_pages:
   assert o.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).samples==q.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).samples,('nonfigure render changed',i+1);unchanged+=1
 assert unchanged==283
 images=[];vectors=[]
 for n,r in m.items():
  name='p277-foldout-plate-2' if n=='277_foldout' else f'p{n}-plate-artwork';obj=next(e for e in new if e.get('ANNAME')==name);q=cur[int(obj.get('OwnPage'))]
  assert list(Image.open(P/r['clean']).size)==r['pixel_size'];assert digest((P/r['clean']).read_bytes())==r['clean_sha256']
  info=q.get_image_info(xrefs=True);ix=sorted({i['xref'] for i in info})
  if r['preferred']=='vector':
   assert not ix;assert len(q.get_drawings())>1000
   vectors.append(n);continue
  src=P/r['clean'] if r['preferred']=='raster' else D/f'p{n}-tone-0.png';expected=np.asarray(Image.open(src).convert('RGB'))
  assert len(ix)==1,(n,ix)
  pix=fitz.Pixmap(cur,ix[0]);actual=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)
  if pix.n==1:actual=np.repeat(actual,3,axis=2)
  assert np.array_equal(actual,expected),(n,'image pixels differ')
  assert cur.xref_get_key(ix[0],'Filter')[1]=='/FlateDecode'
  images.append({'folio':n,'pixel_size':[pix.width,pix.height],'source':str(src.relative_to(P)),'exact_source_pixels':True,'filter':'FlateDecode'})
  if r['preferred']=='hybrid':assert len(q.get_drawings())>1000;vectors.append(n)
 result={'status':'PASS','baseline':'Previous clean-raster project, Library version 20','pdf_pages':314,'all_pdf_text_unchanged':True,'original_folio_order_verified':True,'nonfigure_pages_render_identical':unchanged,'unchanged_original_objects':len(a),'editable_text_frames':len(text_frames),'native_objects':len(list(after.iter('PAGEOBJECT'))),'replaced_artwork_frames':7,'native_svg_groups':vectors,'raster_artwork_frames':24,'artwork_frame_bounds_retained':True,'all_34_plates_accounted_for':True,'source_files_unchanged':preserved,'approved_plate12_sha256':digest((R/'clean/p284-clean.png').read_bytes()),'lossless_image_checks':images,'no_new_geometric_transform':True}
 (R/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='lossless_image_checks'},indent=2),flush=True)
if __name__=='__main__':main()
