#!/usr/bin/env python3
"""Find a free local port for the PR's dev server, or free one that is safe to free.

Usage:
  dev_port.py free   [--first 3000] [--last 3010]   print the first free port
  dev_port.py owners [--first 3000] [--last 3010]   print who holds each busy port
  dev_port.py stop PORT                             stop the server on PORT, only if its PR is MERGED

`stop` looks up the owner again inside the same command, so the answer cannot go stale.
A server whose branch has no PR, an open PR, or a closed PR is never stopped.
Exit: 0 ok, 1 no free port, 2 stop refused, 4 lsof missing.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time


def capture(command: list[str], cwd: str | None = None) -> str:
    try:
        done = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    except FileNotFoundError:
        if command[0] == "lsof":
            print(json.dumps({"error": "lsof not found"}), file=sys.stderr)
            sys.exit(4)
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def can_bind(port: int) -> bool:
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def listener_pid(port: int) -> int | None:
    pids = capture(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"]).split()
    return int(pids[0]) if pids else None


def process_cwd(pid: int) -> str:
    for line in capture(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"]).splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def pr_state(cwd: str, branch: str) -> str:
    if not branch:
        return "unknown"
    found = capture(["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number,state", "--limit", "1"], cwd)
    prs = json.loads(found) if found else None
    if prs is None:
        return "unknown"
    return prs[0]["state"] if prs else "none"


def owner(port: int) -> dict | None:
    pid = listener_pid(port)
    if pid is None:
        return None
    cwd = process_cwd(pid)
    branch = capture(["git", "--no-optional-locks", "branch", "--show-current"], cwd) if cwd else ""
    return {"port": port, "pid": pid, "cwd": cwd, "branch": branch, "pr_state": pr_state(cwd, branch)}


def stop_allowed(state: str) -> bool:
    return state == "MERGED"


def terminate(pid: int, port: int, wait: float = 5.0) -> bool:
    os.kill(pid, signal.SIGTERM)
    end = time.monotonic() + wait
    while time.monotonic() < end:
        if can_bind(port):
            return True
        time.sleep(0.2)
    return can_bind(port)


def busy(port: int) -> bool:
    return listener_pid(port) is not None or not can_bind(port)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("free", "owners"):
        sub = commands.add_parser(name)
        sub.add_argument("--first", type=int, default=3000)
        sub.add_argument("--last", type=int, default=3010)
    commands.add_parser("stop").add_argument("port", type=int)
    args = parser.parse_args()

    if args.command == "stop":
        found = owner(args.port)
        if found is None:
            print(json.dumps({"stopped": False, "reason": "nothing is listening on that port"}))
            return 0
        if not stop_allowed(found["pr_state"]):
            print(json.dumps({"stopped": False, "reason": f"PR state is {found['pr_state']}, not MERGED", **found}))
            return 2
        print(json.dumps({"stopped": terminate(found["pid"], args.port), **found}))
        return 0

    ports = range(args.first, args.last + 1)
    if args.command == "free":
        free = next((port for port in ports if not busy(port)), None)
        print(json.dumps({"free_port": free}))
        return 0 if free else 1
    print(json.dumps([found for found in map(owner, ports) if found], indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
