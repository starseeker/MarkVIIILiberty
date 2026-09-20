"""Persist completed validation stages, bound to inputs and exact output files."""
import copy
import hashlib
import json
from pathlib import Path
import time


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


class StageYield(Exception):
    """The current worker has durably completed its allotted stages."""


class Checkpoints:
    def __init__(self,out,binding,max_stages=0):
        self.out=Path(out).resolve();self.binding=copy.deepcopy(binding)
        self.binding_hash=digest(binding)
        self.root=self.out/'verification/checkpoints'/self.binding_hash
        self.max_stages=max_stages;self.completed_now=0;self.used=[];self.before={}

    def artifacts(self,paths):
        result={}
        for relative in paths:
            path=self.out/relative
            if self.out not in path.resolve().parents:
                raise ValueError('Checkpoint artifact is outside its output directory')
            if not path.exists():
                result[relative]=None
            elif path.is_file():
                result[relative]=file_sha(path)
            else:
                # Include the complete file set so additions and deletions also
                # invalidate a cached stage. Callers specify native/report/cache
                # directories, never changing GUI settings or temporary files.
                result[relative]={'files':{str(p.relative_to(path)):file_sha(p)
                    for p in sorted(path.rglob('*')) if p.is_file()}}
        return result

    def get(self,name,paths):
        path=self.root/(name+'.json')
        if not path.exists():return None
        try:
            entry=json.loads(path.read_text());payload=entry['payload']
            if entry['sha256']!=digest(payload):return None
            if payload['binding']!=self.binding or payload['name']!=name or payload['passed'] is not True:return None
            if payload['artifact_roots']!=paths or payload['artifacts']!=self.artifacts(paths):return None
        except (OSError,ValueError,KeyError,TypeError):
            return None
        self.used.append(dict(stage=name,mode='reused',checkpoint_sha256=file_sha(path)))
        print('Reusing completed validation stage:',name,flush=True)
        return copy.deepcopy(payload['result'])

    def put(self,name,result,paths):
        payload=dict(name=name,binding=self.binding,passed=True,result=copy.deepcopy(result),
                     artifact_roots=paths,artifacts=self.artifacts(paths),completed_utc_epoch=time.time())
        path=self.root/(name+'.json')
        write(path,dict(payload=payload,sha256=digest(payload)))
        self.used.append(dict(stage=name,mode='executed',checkpoint_sha256=file_sha(path)))
        self.completed_now+=1
        print('Saved completed validation stage:',name,flush=True)
        if self.max_stages and self.completed_now>=self.max_stages:raise StageYield(name)

    def result(self,name,function,paths):
        cached=self.get(name,paths)
        if cached is not None:return cached['value']
        value=function()  # Exceptions deliberately leave no completed checkpoint.
        self.put(name,{'value':value},paths)
        return value

    def enter(self,name,report,paths):
        cached=self.get(name,paths)
        if cached is not None:
            report.update(cached['report_delta']);return False
        self.before[name]=set(report)
        return True

    def commit(self,name,report,paths):
        keys=set(report)-self.before.pop(name)
        if not keys:raise ValueError('Validation stage produced no report fields: '+name)
        self.put(name,{'report_delta':{k:report[k] for k in sorted(keys)}},paths)

    def finish(self):
        # Re-check every consumed entry and its files after the whole function
        # finishes; a later stage must not quietly invalidate earlier evidence.
        for used in self.used:
            path=self.root/(used['stage']+'.json')
            if file_sha(path)!=used['checkpoint_sha256']:raise ValueError('Checkpoint changed during validation')
            entry=json.loads(path.read_text());payload=entry['payload']
            if entry['sha256']!=digest(payload) or payload['artifacts']!=self.artifacts(payload['artifact_roots']):
                raise ValueError('Completed stage artifacts changed: '+used['stage'])
        audit=dict(complete=True,binding_sha256=self.binding_hash,binding=self.binding,stages=self.used,
                   original_assertions_preserved=True,completed_stages=len(self.used))
        write(self.out/'reports/resumable_validation.json',audit)
        return audit
