from pathlib import Path
import json,hashlib,zipfile,shutil,ast
R=Path(__file__).resolve().parent;W=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in R.rglob('*.py'):ast.parse(p.read_text())
for p in list(R.rglob('__pycache__')):shutil.rmtree(p)
for pattern in ['*.bak','*.sla~','*.pyc']:
 for p in R.rglob(pattern):p.unlink()
for f in ['build-error.txt','check-error.txt','plate-update-error.txt','review-fixes-error.txt']:
 if (R/f).exists():raise RuntimeError((R/f).read_text())
for name in ['native_validation','reopen_validation','pdf_validation','preservation_validation','comparison_validation','render_validation','source_reference_validation']:
 v=json.loads((R/f'data/{name}.json').read_text());assert not v['errors'],name
native=json.loads((R/'data/native_validation.json').read_text());pdf=json.loads((R/'data/pdf_validation.json').read_text());assert pdf['sha256']==sha(R/pdf['pdf'])
render=json.loads((R/'data/render_validation.json').read_text());assert render['pdf_sha256']==pdf['sha256']
assert len(render['pages'])==11 and all(sha(R/r['path'])==r['sha256'] for r in render['pages'])
assert pdf['pages']==251 and len(native['frames'])==15235
state=json.loads((R/'PROJECT_STATUS.json').read_text());assert state['checkpoint']==13 and state['next_batch'] is None
assert not (R/'Handbook_Master.pdf').exists()
assert all(row['identical'] for row in pdf['earlier_pdf_comparison']['pages'])
comp=R/'Handbook_Comparison_241-251_v13.pdf';assert comp.read_bytes().rstrip().endswith(b'%%EOF')
assert json.loads((R/'data/comparison_validation.json').read_text())['sha256']==sha(comp)
assert len(pdf['earlier_pdf_comparison']['pages'])==240
assert json.loads((R/'data/preservation_validation.json').read_text())['master_sha256']==sha(R/'Handbook_Master.sla')
refs=json.loads((R/'data/source_reference_validation.json').read_text());assert refs['transcription_sha256']==sha(R/'data/index_batch13.json')
assert refs['entries']==491 and refs['column_ocr_agreements']+refs['manual_confirmations']==489
assert len(json.loads((R/'data/page_map.json').read_text()))==251
assert len(json.loads((R/'data/source_inventory.json').read_text())['sources'])==126
assert 'checkpoint 13' in (R/'data/visual_review.md').read_text()

# Manifest covers all portable project members other than this manifest itself.
manifest=R/'data/release_manifest.json';rows=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and p!=manifest:rows.append(dict(path=p.relative_to(R).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
x=dict(project=state['project'],checkpoint=13,release_date=state['release_date'],cumulative_pages=[1,251],comparison_pages=[241,251],master_pdf=state['master_pdf'],master_pdf_sha256=sha(R/state['master_pdf']),native_master_sha256=sha(R/'Handbook_Master.sla'),files=rows)
manifest.write_text(json.dumps(x,indent=2)+'\n')
out=W.parent/'Handbook_Project_001-251_v13.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(R.rglob('*')):
  if p.is_file():z.write(p,Path('Handbook_Project')/p.relative_to(R))
with zipfile.ZipFile(out) as z:
 bad=z.testzip();assert bad is None,bad
 for row in rows:
  raw=z.read('Handbook_Project/'+row['path']);assert len(raw)==row['size_bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
 print('Verified',len(rows),'manifest members and ZIP CRCs')
digest=sha(out);out.with_suffix('.zip.sha256').write_text(digest+'  '+out.name+'\n')
print(out.name,out.stat().st_size,digest)
print(state['master_pdf'],(R/state['master_pdf']).stat().st_size,sha(R/state['master_pdf']))
