"""Compact source-decision freshness report; never accepts or rewrites decisions."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad_packets'))
from common import digest,read,sha


def value_at(value,pointer):
    for key in pointer.lstrip('/').split('/') if pointer else []:
        key=key.replace('~1','/').replace('~0','~')
        value=value[int(key)] if isinstance(value,list) else value[key]
    return value


def dependency_hash(dependency,root=ROOT):
    path=Path(root)/dependency['path']
    return digest(value_at(read(path),dependency['pointer'])) if 'pointer' in dependency else sha(path)


def inspect(ledger,root=ROOT):
    ids=set();rows=[]
    for item in ledger['decisions']:
        if item['id'] in ids: raise ValueError('Duplicate decision ID')
        ids.add(item['id'])
        if item['status'] not in ['reviewed_approximation','open_identity','open_evidence']:
            raise ValueError('Unsupported decision status')
        for key in ['scope','reason','uncertainty','limits','reopen_when','dependencies']:
            if not item.get(key): raise ValueError('Incomplete decision: '+item['id']+'/'+key)
        if item['status']=='reviewed_approximation' and not item.get('review'):
            raise ValueError('Approximation requires a recorded review')
        changed=[]
        for dependency in item['dependencies']:
            try: current=dependency_hash(dependency,root)
            except (OSError,ValueError,KeyError,IndexError,TypeError): current=None
            if current!=dependency['sha256']: changed.append(dependency['path']+dependency.get('pointer',''))
        rows.append(dict(id=item['id'],status=item['status'],dependencies_current=not changed,
                         changed=changed,action='reopen_review' if changed else
                         'retain_open' if item['status'].startswith('open_') else 'reuse_within_recorded_scope'))
    return dict(decisions=rows,all_dependencies_current=all(v['dependencies_current'] for v in rows),
                automatic_acceptance=False,production_promoted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('ledger',type=Path)
    args=parser.parse_args();result=inspect(read(args.ledger));print(json.dumps(result,indent=2))
    if not result['all_dependencies_current']: raise SystemExit(1)
