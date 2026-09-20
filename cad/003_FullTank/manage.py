#!/usr/bin/env python3
"""Build and inspect the evidence-led Mark VIII reconstruction."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import traceback

from lib.evidence import STAGE, REPO, verify_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["inventory", "dossier", "check", "build", "export", "review", "validate"])
    parser.add_argument("part_id", nargs="?", help="Survey part ID for dossier")
    parser.add_argument("--output", type=Path, default=STAGE / "build")
    parser.add_argument("--subsystem", help="Build a separate subsystem deliverable")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    out = args.output.resolve()
    protected = [REPO/"references", REPO/"cad/001_Survey", REPO/"cad/002_Foundation",
                 STAGE/"data", STAGE/"lib", STAGE/"packets", REPO/"docs",
                 REPO/".git", REPO/".agents", REPO/".codex"]
    if out in {REPO, STAGE} or any(out == p or p in out.parents or out in p.parents for p in protected):
        parser.error("Output must be separate from authored data, code and frozen research")
    if args.subsystem and (not args.subsystem.isidentifier() or "/" in args.subsystem):
        parser.error("Invalid subsystem identifier")
    if args.subsystem and not args.worker:
        out = out / args.subsystem
    out.mkdir(parents=True, exist_ok=True)
    if args.command == "dossier":
        if not args.part_id:
            parser.error("dossier requires a survey part ID")
        from lib.inventory import dossier
        from lib.evidence import write
        result = dossier(args.part_id)
        path = out / "dossiers" / (args.part_id + ".json")
        write(path, result)
        print(json.dumps({"dossier": str(path), "name": result["part"]["canonical_name"]}, indent=2))
        return 0
    if args.command == "inventory":
        from lib.inventory import build
        verify_sources()
        model, instances = None, []
        if (out/"reports/build.json").is_file():
            from lib.worker import check_build
            from lib.model import load
            report = check_build(out)
            model = load()
            instances = [x for x in model["occurrences"] if x["id"] in report["geometry"]]
        result = build(out, model, instances)
        print(json.dumps({k:result[k] for k in ["canonical_records","dispositions","vehicle_occurrence_count"]}, indent=2))
        return 0
    if not args.worker:
        from lib.runtime import environment
        command = [sys.executable, str(STAGE/"manage.py"), args.command, "--output", str(out), "--worker"]
        if args.subsystem:
            command += ["--subsystem", args.subsystem]
        return subprocess.run(command, env=environment(out)).returncode
    from lib import runtime
    try:
        from lib.worker import run
        result = run(args.command, out, args.subsystem)
        print(json.dumps({"command":args.command,"output":str(out),"success":True,"result":result},indent=2))
        return 0
    finally:
        runtime.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
