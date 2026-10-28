#!/usr/bin/env python3
"""State and change detection for the pr-watch skill. Run it inside the PR's worktree.

Commands (all print JSON):
  slack-ts LINK                 channel id and thread ts from a Slack link
  context PR                    facts about the PR and the local worktrees on its branch
  init PR [--slack LINK]...     create .vorbit/pr<N>-monitor.md (never overwrites)
  tick PR                       compare the PR with the monitor file, log one line
  mark PR WHAT VALUE            record reviewed (review and QA both done) or commented (a SHA), or told (a time)
  set-status PR STATUS [WHY]    watching, waiting_for_user or stopped
  permit PR comment|approve     allow it from now on (--off takes it back)

PR is a number or a GitHub PR URL. Add --repo OWNER/REPO when a number is not enough.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

EXIT_NO_TOOL, EXIT_GH, EXIT_STATE = 4, 5, 6

PR_FIELDS = (
    "number,url,title,author,baseRefName,headRefName,headRefOid,state,isDraft,"
    "statusCheckRollup,comments,reviews,body"
)
FIELDS = (
    "PR", "Repo", "Branch", "Author", "Base", "Ticket", "Slack threads",
    "Auto-comment", "Auto-approve", "Approval rule", "Baseline SHA",
    "Reviewed SHA", "Commented SHA", "Told until", "Status", "Status reason",
)
MARKS = {"reviewed": "Reviewed SHA", "commented": "Commented SHA", "told": "Told until"}
STATUSES = ("watching", "waiting_for_user", "stopped")
PERMITS = {"comment": "Auto-comment", "approve": "Auto-approve"}
APPROVAL_RULE = (
    "no finding from this branch, every runnable QA flow passed with a recording, "
    "GitHub checks green"
)
NOTES_HEADING = "## Notes"
LOG_HEADING = "## Tick log"
FAILED_CONCLUSIONS = {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
PENDING_STATES = {"PENDING", "EXPECTED"}


def fail(code: int, message: str) -> None:
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(code)


def run(args: list[str], code: int = EXIT_GH) -> str:
    try:
        done = subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError:
        fail(EXIT_NO_TOOL, f"{args[0]} not found. Install it, then run again.")
    if done.returncode != 0:
        fail(code, f"{' '.join(args[:4])} failed: {done.stderr.strip()}")
    return done.stdout


def git(*args: str) -> str:
    return run(["git", "--no-optional-locks", *args], EXIT_STATE).strip()


def git_ok(*args: str) -> bool:
    return subprocess.run(["git", "--no-optional-locks", *args], capture_output=True).returncode == 0


def slack_ref(link: str) -> tuple[str, str] | None:
    match = re.search(r"/archives/([A-Z0-9]+)/p(\d{10})(\d{6})", link)
    if not match:
        return None
    channel, seconds, micros = match.groups()
    root = parse_qs(urlparse(link).query).get("thread_ts")
    return channel, root[0] if root else f"{seconds}.{micros}"


def pr_ref(ref: str, repo: str | None) -> tuple[str | None, str]:
    match = re.search(r"github\.com/([^/]+/[^/]+)/pull/(\d+)", ref)
    if match:
        return match.group(1), match.group(2)
    if not ref.isdigit():
        fail(2, f"not a PR number or URL: {ref}")
    return repo, ref


def find_ticket(*texts: str) -> str | None:
    for text in texts:
        match = re.search(r"\b([A-Za-z][A-Za-z0-9]+-\d+)\b", text or "")
        if match:
            return match.group(1).upper()
    return None


def check_state(rollup: list[dict]) -> dict:
    failing, pending = [], False
    for item in rollup or []:
        name = item.get("name") or item.get("context") or "check"
        if item.get("__typename") == "StatusContext":
            state = item.get("state", "")
            failing += [name] if state in {"FAILURE", "ERROR"} else []
            pending = pending or state in PENDING_STATES
        else:
            failing += [name] if item.get("conclusion") in FAILED_CONCLUSIONS else []
            pending = pending or item.get("status") != "COMPLETED"
    if failing:
        return {"state": "failing", "failing": failing}
    if pending:
        return {"state": "pending", "failing": []}
    return {"state": "green" if rollup else "none", "failing": []}


TEAM_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR", "CONTRIBUTOR"}


def new_comments(view: dict, me: str, after: str) -> tuple[list[dict], int]:
    """Teammate replies after `after`, and how many bot or outsider ones were skipped."""
    found = list(view.get("comments", []))
    for review in view.get("reviews", []):
        said_something = review.get("body") or review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
        if said_something and review.get("submittedAt"):
            found.append({**review, "createdAt": review["submittedAt"]})
    teammates, skipped = [], 0
    for item in sorted(found, key=lambda entry: entry["createdAt"]):
        login = (item.get("author") or {}).get("login", "")
        if item["createdAt"] <= after or login == me:
            continue
        if item.get("authorAssociation") not in TEAM_ASSOCIATIONS or login.endswith("[bot]"):
            skipped += 1
            continue
        lines = (item.get("body") or item.get("state", "")).strip().splitlines() or [""]
        teammates.append({"author": login, "at": item["createdAt"], "first_line": lines[0][:120], "url": item.get("url", "")})
    return teammates, skipped


def pick_event(state: str, head: str, reviewed: str, comments: list[dict]) -> str:
    if state in {"MERGED", "CLOSED"}:
        return state.lower()
    if head != reviewed:
        return "new_push"
    return "new_comment" if comments else "no_change"


def changes_since(reviewed: str, head: str) -> dict:
    if not reviewed:
        return {"changed_files": None, "needs_pull": False, "history_rewritten": False}
    if not (git_ok("cat-file", "-e", f"{reviewed}^{{commit}}") and git_ok("cat-file", "-e", f"{head}^{{commit}}")):
        return {"changed_files": None, "needs_pull": True, "history_rewritten": False}
    ancestor = git_ok("merge-base", "--is-ancestor", reviewed, head)
    base = reviewed if ancestor else git("merge-base", reviewed, head)
    files = git("diff", "--name-only", f"{base}..{head}").splitlines()
    return {"changed_files": files, "needs_pull": False, "history_rewritten": not ancestor}


def worktrees_on_branch(branch: str) -> list[str]:
    paths, current = [], ""
    for line in git("worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            current = line.removeprefix("worktree ")
        elif line == f"branch refs/heads/{branch}":
            paths.append(current)
    return paths


def view_pr(number: str, repo: str | None) -> dict:
    command = ["gh", "pr", "view", number, "--json", PR_FIELDS]
    return json.loads(run(command + (["--repo", repo] if repo else [])))


def spec_dir() -> Path:
    return Path(git("rev-parse", "--show-toplevel")) / ".vorbit"


def ensure_gitignore() -> bool:
    ignore = spec_dir().parent / ".gitignore"
    text = ignore.read_text() if ignore.exists() else ""
    if any(line.strip().rstrip("/") == ".vorbit" for line in text.splitlines()):
        return False
    ignore.write_text(text + ("" if text.endswith("\n") or not text else "\n") + ".vorbit/\n")
    return True


@dataclass
class Monitor:
    path: Path
    title: str
    fields: dict[str, str]
    notes: str
    log: list[str]

    def render(self) -> str:
        lines = [f"# PR Watch: {self.title}", ""]
        lines += [f"{key}: {self.fields[key]}".rstrip() for key in FIELDS if key in self.fields]
        parts = ["\n".join(lines), f"{NOTES_HEADING}\n{self.notes.strip()}", f"{LOG_HEADING}\n" + "\n".join(self.log)]
        return "\n\n".join(parts).rstrip() + "\n"

    def write(self) -> None:
        self.path.parent.mkdir(exist_ok=True)
        handle, temp = tempfile.mkstemp(dir=self.path.parent, prefix=self.path.name)
        with os.fdopen(handle, "w") as out:
            out.write(self.render())
        os.replace(temp, self.path)

    @classmethod
    def parse(cls, path: Path, text: str) -> "Monitor":
        head, _, tail = text.partition(f"\n{LOG_HEADING}\n")
        top, _, notes = head.partition(f"\n{NOTES_HEADING}\n")
        title = re.match(r"# PR Watch: (.*)", top)
        fields = {}
        for line in top.splitlines():
            key, _, value = line.partition(":")
            if key in FIELDS:
                fields[key] = value.strip()
        log = [line for line in tail.splitlines() if line.startswith("- ")]
        return cls(path, title.group(1) if title else "", fields, notes, log)

    @classmethod
    def load(cls, number: str) -> "Monitor":
        path = spec_dir() / f"pr{number}-monitor.md"
        if not path.is_file():
            fail(EXIT_STATE, f"no monitor file at {path}. Run init first, or check git worktree list.")
        monitor = cls.parse(path, path.read_text())
        branch = git("branch", "--show-current")
        if monitor.fields.get("Branch") != branch:
            fail(EXIT_STATE, f"monitor file is for branch {monitor.fields.get('Branch')}, this worktree is on {branch}. Ask the user.")
        return monitor


def default_notes(number: str) -> str:
    return "\n".join([
        f"- Only act on PR #{number}. Other PRs linked in the Slack thread are not ours.",
        "- Dev server: not started yet",
        "- Login renew command: not found yet",
        "- Last QA run folder: none yet",
        "- Open finding: none",
        "- Pre-existing, not blockers: none",
    ])


def cmd_context(args: argparse.Namespace) -> dict:
    repo, number = pr_ref(args.pr, args.repo)
    view = view_pr(number, repo)
    return {
        "number": view["number"], "url": view["url"], "title": view["title"],
        "author": view["author"]["login"], "base": view["baseRefName"],
        "head_branch": view["headRefName"], "head_sha": view["headRefOid"],
        "state": view["state"], "is_draft": view["isDraft"],
        "files": run(["gh", "pr", "diff", number, "--name-only"] + (["--repo", repo] if repo else [])).split(),
        "checks": check_state(view["statusCheckRollup"]),
        "ticket": find_ticket(view["headRefName"], view["title"], view["body"]),
        "worktrees_on_branch": worktrees_on_branch(view["headRefName"]),
        "current_branch": git("branch", "--show-current"),
    }


def cmd_init(args: argparse.Namespace) -> dict:
    repo, number = pr_ref(args.pr, args.repo)
    path = spec_dir() / f"pr{number}-monitor.md"
    if path.exists():
        return {"created": False, "path": str(path)}
    view = view_pr(number, repo)
    branch = git("branch", "--show-current")
    if branch != view["headRefName"]:
        fail(EXIT_STATE, f"this worktree is on {branch}, the PR branch is {view['headRefName']}.")
    threads = []
    for link in args.slack:
        ref = slack_ref(link)
        if not ref:
            fail(2, f"not a Slack message link: {link}")
        threads.append("/".join(ref))
    seen = [item["createdAt"] for item in view["comments"]]
    seen += [item["submittedAt"] for item in view["reviews"] if item.get("submittedAt")]
    fields = {
        "PR": view["url"], "Repo": re.search(r"github\.com/([^/]+/[^/]+)/pull", view["url"]).group(1),
        "Branch": branch, "Author": view["author"]["login"], "Base": view["baseRefName"],
        "Ticket": find_ticket(branch, view["title"], view["body"]) or "none",
        "Slack threads": ", ".join(threads) or "none",
        "Auto-comment": "yes" if args.auto_comment else "no",
        "Auto-approve": "yes" if args.auto_approve else "no",
        "Approval rule": APPROVAL_RULE, "Baseline SHA": view["headRefOid"],
        "Reviewed SHA": "", "Commented SHA": "",
        "Told until": max(seen, default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
        "Status": "watching", "Status reason": "",
    }
    appended = ensure_gitignore()
    Monitor(path, f"PR #{number}, {view['title']}", fields, default_notes(number), []).write()
    return {"created": True, "path": str(path), "gitignore_appended": appended}


def cmd_tick(args: argparse.Namespace) -> dict:
    repo, number = pr_ref(args.pr, args.repo)
    monitor = Monitor.load(number)
    fields = monitor.fields
    if fields["Status"] == "stopped":
        return {"event": "already_stopped", "reason": fields["Status reason"]}
    view = view_pr(number, repo or fields["Repo"])
    me = run(["gh", "api", "user", "--jq", ".login"]).strip()
    comments, skipped = new_comments(view, me, fields["Told until"])
    head = view["headRefOid"]
    event = pick_event(view["state"], head, fields["Reviewed SHA"], comments)
    result = {
        "event": event, "head_sha": head, "reviewed_sha": fields["Reviewed SHA"],
        "commented_sha": fields["Commented SHA"],
        "already_commented_on_head": fields["Commented SHA"] == head,
        "checks": check_state(view["statusCheckRollup"]), "new_comments": comments,
        "skipped_bot_or_outsider_comments": skipped, "status": fields["Status"],
    }
    if event == "new_push":
        result.update(changes_since(fields["Reviewed SHA"], head))
    monitor.log.append(f"- {datetime.now().strftime('%Y-%m-%d %H:%M')} head {head[:7]} {event}")
    monitor.write()
    return result


def cmd_mark(args: argparse.Namespace) -> dict:
    _, number = pr_ref(args.pr, args.repo)
    monitor = Monitor.load(number)
    if args.what != "told" and not re.fullmatch(r"[0-9a-f]{7,40}", args.value):
        fail(2, f"{args.what} needs a commit SHA, got {args.value}")
    monitor.fields[MARKS[args.what]] = args.value
    monitor.write()
    return {MARKS[args.what]: args.value}


def cmd_set_status(args: argparse.Namespace) -> dict:
    _, number = pr_ref(args.pr, args.repo)
    monitor = Monitor.load(number)
    monitor.fields["Status"], monitor.fields["Status reason"] = args.status, args.why
    monitor.write()
    return {"Status": args.status, "Status reason": args.why}


def cmd_permit(args: argparse.Namespace) -> dict:
    _, number = pr_ref(args.pr, args.repo)
    monitor = Monitor.load(number)
    monitor.fields[PERMITS[args.what]] = "no" if args.off else "yes"
    monitor.write()
    return {PERMITS[args.what]: monitor.fields[PERMITS[args.what]]}


def cmd_slack_ts(args: argparse.Namespace) -> dict:
    ref = slack_ref(args.link)
    if not ref:
        fail(2, f"not a Slack message link: {args.link}")
    return {"channel": ref[0], "thread_ts": ref[1]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    def add(name: str, handler, pr: bool = True) -> argparse.ArgumentParser:
        sub = commands.add_parser(name)
        sub.set_defaults(handler=handler)
        if pr:
            sub.add_argument("pr")
            sub.add_argument("--repo")
        return sub

    add("context", cmd_context)
    init = add("init", cmd_init)
    init.add_argument("--slack", action="append", default=[])
    init.add_argument("--auto-comment", action="store_true")
    init.add_argument("--auto-approve", action="store_true")
    add("tick", cmd_tick)
    mark = add("mark", cmd_mark)
    mark.add_argument("what", choices=sorted(MARKS))
    mark.add_argument("value")
    status = add("set-status", cmd_set_status)
    status.add_argument("status", choices=STATUSES)
    status.add_argument("why", nargs="?", default="")
    permit = add("permit", cmd_permit)
    permit.add_argument("what", choices=sorted(PERMITS))
    permit.add_argument("--off", action="store_true")
    add("slack-ts", cmd_slack_ts, pr=False).add_argument("link")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(json.dumps(args.handler(args), indent=2))


if __name__ == "__main__":
    main()
