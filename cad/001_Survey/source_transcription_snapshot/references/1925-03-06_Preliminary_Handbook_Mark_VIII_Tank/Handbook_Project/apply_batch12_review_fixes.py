"""Apply the two visual-review geometry corrections, idempotently.
The current build_project.py and asset preparation already include these fixes.
"""
from pathlib import Path
import scribus as s,json,os,traceback
R=Path(__file__).resolve().parent
try:
 s.openDoc(str(R/'Handbook_Master.sla'))
 a=next(x for x in json.loads((R/'data/assets.json').read_text()) if x['name']=='plate133')
 s.gotoPage(226);name='p226-plate133'
 s.moveObjectAbs(198+(a['crop'][0]-a['content_center_px'])*.225,17+a['crop'][1]*.225,name)
 s.sizeObject(a['output_size'][0]*.225,a['output_size'][1]*.225,name)
 s.loadImage(str(R/'assets/plate133.png'),name);s.setScaleImageToFrame(True,True,name)
 s.gotoPage(240);p=R/'data/native_validation.json';v=json.loads(p.read_text())
 row=next(x for x in v['frames'] if x['page']==240 and x['text']=='Page');target=17+291*.225
 s.moveObject(0,target-row['baseline'],row['name']);row['baseline']=target
 s.gotoPage(1);s.saveDocAs(str(R/'Handbook_Master.sla'));p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
except Exception:
 (R/'review-fixes-error.txt').write_text(traceback.format_exc())
finally:
 if os.environ.get('HANDBOOK_BATCH')=='1':os._exit(0)
