"""CLI permission profiles: candidate tools and external validators are isolated."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def profile(readable, writable):
    filesystem = {':minimal': 'read', '/snap': 'read'}
    filesystem.update({str(Path(p).resolve()): 'write' for p in writable})
    filesystem.update({str(Path(p).resolve()): 'read' for p in readable})
    table = '{' + ','.join(json.dumps(k) + '=' + json.dumps(v)
                           for k, v in filesystem.items()) + '}'
    return ['-c', 'default_permissions="cad-packet"',
            '-c', 'permissions.cad-packet.filesystem=' + table,
            '-c', 'permissions.cad-packet.network.enabled=false']


def sandbox(cwd, readable, writable, command):
    return ['codex', 'sandbox', '--include-managed-config', '-P', 'cad-packet',
            '--cd', str(cwd), *profile(readable, writable), '--', *map(str, command)]


def execute(command, cwd, stdout, stderr, timeout, prompt=None):
    """Kill the entire process group on timeout/interruption; keep raw evidence."""
    start = time.monotonic()
    timed_out = False
    with open(stdout, 'wb') as output, open(stderr, 'wb') as errors:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE if prompt else subprocess.DEVNULL,
                                   stdout=output, stderr=errors, start_new_session=True)
        try:
            process.communicate(prompt.encode() if prompt else None, timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            timed_out = isinstance(exc, subprocess.TimeoutExpired)
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
            if not timed_out:
                raise
        finally:
            # Prevent descendants surviving an early CLI exit and changing artifacts later.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    return dict(returncode=process.returncode, timed_out=timed_out,
                seconds=time.monotonic() - start)
