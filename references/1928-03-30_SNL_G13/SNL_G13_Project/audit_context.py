#!/usr/bin/env python3
"""Reproducible cross-book review-log update, using the retained pre-audit log.

Decisions were made by visual source comparison, not by automatic substitution.
Candidate matches are discovery aids, not evidence that the original is correct.
"""
from pathlib import Path
import importlib,json,re,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
AUDIT=ROOT/'audit'; AUDIT.mkdir(exist_ok=True)
baseline=json.loads((AUDIT/'review_before_context_audit.json').read_text())
rows=[]
for f in sorted((ROOT/'data').glob('*.py')):
 if f.stem not in ['parts_tables','opening_tables'] and not f.stem.startswith('tables_'):continue
 module=importlib.import_module('data.'+f.stem)
 for page,rr in module.TABLES.items():
  for number,row in enumerate(rr,1):rows.append(dict(page=page,row=number,**row))
assert len(rows)==7571

findings=[]
def finding(id,indices,status,title,pages,reading,evidence,change=None):
 findings.append(dict(id=id,baseline_indices=indices,status=status,title=title,pages=pages,
                      reading=reading,evidence=evidence,change=change))
finding('A01',[23],'corrected','Chain-collar bushing',[43,61],'SH40AD',
 'The individual bushing on 43 and the chain component on 61 both read SH40AD. '
 'The extra 1 in SH40A1D was a transcription error.',
 dict(page=43,row=22,field='ord',frame='p43-r22-ord',old='SH40A1D',new='SH40AD'))
finding('A02',[25],'corrected','Water-pipe connection clip',[31,66],'SH976C',
 'The last clip code on 66 reads SH976C on renewed source inspection. The bolt-use '
 'list on 31 independently names clips SH976A and SH976C. SH975C on 108 is a hose, '
 'so those other occurrences must not be replaced. The two blank quantities on 66 remain blank.',
 dict(page=66,row=28,field='ord',frame='p66-r28-ord',old='SH975C',new='SH976C'))
finding('A03',[35],'corrected','First transmission-frame rivet length',[97,169],'½″ diameter × 1⅛″ length',
 'The enlarged first rivet line on 97 reads 1⅛″. The individual ½″ × 1⅛″ '
 'button-head rivet listing on 169 explicitly allocates four to the transmission frame, '
 'matching the four components on 97.',
 dict(page=97,row=3,field='item',frame='p97-r03-item',old='1½″',new='1⅛″'))
finding('A04',[38],'confirmed','Flanged tachometer-shaft bushing',[44,110],'D22921',
 'D22921 is legible in both the individual flanged-bushing listing on 44 and the '
 'component list on 110. Its unusual number sequence is not grounds to change it. '
 'A separate disagreement in the adjacent plain-bushing code has been logged.')
finding('A05',[42],'explained','Same manifold component in left and right assemblies',[122,123,309],'SH599A on both sides',
 'The assemblies carry note (go). On 309 that note explicitly says their components '
 'are identical; assembly at 61° produces noninterchangeable left and right units. '
 'The repeated SH599A component code on 123 therefore needs no correction.')
finding('A06',[46,93],'confirmed','Carburetor spring wording',[134,219],'scoup',
 'The pin description on 134 says screw for scoup spring; the spring listing on 219 '
 'also prints scoup. Both photographs support the same spelling. This confirms the '
 'literal transcription, without asserting that it is standard terminology.')
finding('A07',[85,105],'confirmed','Ignition-switch screw thread notation',[204,244],'D26948: No. 6—38 × ¼″',
 'The individual screw entry on 204 and the D1120 switch component on 244 both '
 'visibly print No. 6—38. This resolves the reading only; it does not independently '
 'validate the manufactured thread or justify changing 38 to 40.')
finding('A08',[111,117],'confirmed','Damaged brass-union code and fine fraction',[256,257,258,265],'B101965B; 29/64″—28',
 'The damaged code on 265 is supported by the repeated B101965B component listings '
 'on 256–258. The individual union and its component entries agree on 29/64—28 '
 'and the C8012/C8013/C8014/C8015/C8016 applications. Existing source punctuation stays unchanged.')
finding('A09',[114],'confirmed','Radiator tube quantity',[73,262],'606',
 'The quantity on 262 is visually consistent with 606. Page 73 independently spells '
 'out three hundred and three SH607C tubes in each of the front and rear radiator '
 'cores: 303 + 303 = 606. This corroborates an existing value, rather than filling a blank.')
finding('A10',[118],'confirmed','Damaged generator-washer identification',[268,288],'8209',
 'Page 268 retains 8209 in the identification column, supported by the clear 8209 '
 'manufacturer entry in that row. Plate 16 on 288 independently labels the '
 'ring-shaped washer 8209, resolving the damaged identification digit.')

updates={
9:('Likely identity only','The other lock-wire codes LQ512A/C/D/E occur on 20, 57 and 90. '
   'Page 276 corroborates four five-inch wire pieces for lock LQ559A, but does not '
   'repeat the full LQ512B mark. The photographed dash on 20 remains; no prefix is invented.'),
18:('Source disagreement','The separate terminal entries on 249 distinguish distributor-end '
    'LQ328A from spark-plug-end LQ329A and include cable LQ366A. They identify the '
    'likely intended component on 46, but do not justify altering a conflicting printed code.'),
22:('Stronger corroboration; conflict retained','The individual LQ196A stud entry on 237 '
    'also gives 1 9/16 inches, agreeing with 58 and 105. Page 59 retains 1 3/16. '
    'Note (ge) on 309 specifies a different oversize replacement, LQ484A; it does '
    'not explain two lengths for the same LQ196A code.'),
26:('Source disagreement','The individual collar entries on 67 and components on 79 '
    'reverse the lower/upper descriptions for LQ296A/LQ297A. No explicit correction '
    'was found in the supplied notes. Both source forms remain; orientation is unresolved.'),
34:('Likely identity only','The photographs of 107 and the transcription on 223 support '
    'NB1B as the common No. 2 fastener identity. Page 93 looks like NBIB; whether '
    'its middle glyph is an I or a 1 is not settled by the repeated identity alone. '
    'The literal earlier reading is retained with the cross-reference.'),
48:('Physical dimension unresolved','The 13/16-inch inside diameter is repeated on 219. '
    'The source on 138 shows 1½-inch outside diameter, while 219 shows ½ inch; '
    'both appear to give 1-inch thickness. Repetition confirms a textual problem, '
    'not a usable spring specification. Note (gh) supplies no missing dimensions.'),
91:('Physical dimension unresolved','Cross-check with 138 confirms the shared SH642B '
    'identity and inside diameter, but conflicting outside diameters and apparent '
    'thickness remain. Do not infer a physically plausible dimension.'),
61:('Two source issues remain','The piston assembly on 146 calls LQ469A bottom, '
    'whereas its individual ring entry on 165 calls it top. Notes (gw)/(gaj) explain '
    'old versus replacement pistons but do not settle that ring-position discrepancy. '
    'For A6951, the visible (a) has no standalone definition in 307–311; note (d) '
    'on 308 discusses the chain-ring/S-hook replacement and is a plausible intended '
    'reference, but the source (a) and blank quantity are retained.'),
102:('Likely identity only','Note (ge) on 309 and the other stud listings use LQ88A. '
     'The apparent LA88A occurrence on 237 is retained as a source variant, '
     'with LQ88A recorded only as the likely intended identity.'),
103:('Stronger corroboration; conflict retained','The component on 59 also gives '
     'LQ229A a 1 15/16-inch thread, supporting 237. The continuation on 238 still '
     'prints 1 5/16 and identification 1354 rather than 13154. Neither conflicting '
     'source field is silently normalized.'),
113:('Likely plate reference only','There are 34 plates, so 141 cannot be a plate '
     'number within this book. Plate 14 is a plausible intended reference; that '
     'range check does not establish which printed character is erroneous.')
}
closed={i:f for f in findings for i in f['baseline_indices']}
review=json.loads(json.dumps(baseline));review['open_items']=[]
screening=[]
for i,item in enumerate(baseline['open_items']):
 oldid=f'R{i+1:03d}'
 text=' '.join(str(v) for v in item.values())
 tokens=sorted(set(re.findall(r'\b(?:[A-Z]{1,4}\d+[A-Z0-9]*|\d+[A-Z][A-Z0-9]*)\b',text)))
 candidates={t:sorted({r['page'] for r in rows if re.search(r'(?<![A-Z0-9])'+re.escape(t)+r'(?![A-Z0-9])',' '.join(str(v) for v in r.values()))}) for t in tokens}
 status='open';detail='No sufficient resolution recorded in this targeted pass; retain the prior flag.'
 if item['field'] in ['geometry','sequence and size','page size','major-item glyph','transcription']:
  status='outside_targeted_reading_audit';detail='General proofreading, typography, sequence, or physical-layout issue; not closed by text cross-references.'
 if i in closed:
  f=closed[i];status=f['status'];detail=f['evidence']
  review['resolved_items'].append(dict(**item,audit_id=oldid,audit_finding=f['id'],
    previous_reading=item.get('reading',''),resolved_reading=f['reading'],
    resolution_type=f['status'],evidence=f['evidence'],audit_date='2026-09-12'))
 else:
  if i in updates:
   status='open_with_context';detail=updates[i][1]
   item=dict(item,context_audit=dict(date='2026-09-12',finding=updates[i][0],evidence=detail))
  review['open_items'].append(item)
 screening.append(dict(audit_id=oldid,baseline_index=i,page=item['page'],field=item['field'],
                       status=status,detail=detail,exact_code_candidate_pages=candidates))
new_issue=dict(page='44, 110',record='plain tachometer drive shaft bushing',field='manufacturer part number',
 reading='D22920 on 44; D29920 on 110',reason='Both forms are visible in the photographs. '
 'The flanged companion D22921 is now corroborated, but that does not resolve the '
 'plain-bushing discrepancy. Original values remain unchanged.',audit_date='2026-09-12')
review['open_items'].append(new_issue)
review['context_audit_summary']=dict(date='2026-09-12',baseline_open_entries=125,
 closed_entries=len(closed),distinct_findings=len(findings),corrected_cells=3,
 new_source_discrepancies=1,open_entries=len(review['open_items']),
 report='Transcription_Ambiguity_Audit.pdf',data='audit/ambiguity_audit.json',
 scope='Targeted audit of prior flags using all structured tables, notes, selected source photographs and one plate; not a fresh full-book independent proofread.')
(ROOT/'review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
result=dict(summary=review['context_audit_summary'],findings=findings,open_context_updates=updates,
            new_source_issue=new_issue,screening=screening)
(AUDIT/'ambiguity_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result['summary'],indent=2))
