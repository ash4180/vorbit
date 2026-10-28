"""The pr-watch skill's helper scripts: state and change detection, screenshot comments, port safety."""

from __future__ import annotations

import importlib.util
import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Importing a script writes __pycache__ beside it, and the mirror check treats that as drift.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/pr-watch/scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # @dataclass looks its module up here while loading
    spec.loader.exec_module(module)
    return module


pr_state = load("pr_state")
comment = load("comment_with_images")
dev_port = load("dev_port")
review_recording = load("review_recording")


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo, capture_output=True, text=True, check=True,
    )
    return done.stdout.strip()


def commit(repo: Path, name: str) -> str:
    (repo / name).write_text(name)
    git(repo, "add", name)
    git(repo, "commit", "-q", "-m", name)
    return git(repo, "rev-parse", "HEAD")


def cli(repo: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "pr_state.py"), *arguments],
        cwd=repo, capture_output=True, text=True,
    )


# --- pr_state: pure rules ---------------------------------------------------------------

def test_slack_link_gives_channel_and_thread_ts():
    link = "https://acme.slack.com/archives/C0892L7HUB1/p1793154612071909"
    assert pr_state.slack_ref(link) == ("C0892L7HUB1", "1793154612.071909")


def test_slack_reply_link_points_at_the_thread_root():
    link = "https://acme.slack.com/archives/C0892L7HUB1/p1793154999000100?thread_ts=1793154612.071909&cid=C0892L7HUB1"
    assert pr_state.slack_ref(link) == ("C0892L7HUB1", "1793154612.071909")


def test_non_slack_link_is_rejected():
    assert pr_state.slack_ref("https://example.com/archives/nope") is None


def test_ticket_comes_from_branch_first_then_title_then_body():
    assert pr_state.find_ticket("feature/vib-5072-chat-search", "title VIB-1", "") == "VIB-5072"
    assert pr_state.find_ticket("main", "fix (VIB-1316)", "VIB-9") == "VIB-1316"
    assert pr_state.find_ticket("main", "no ticket", "") is None


@pytest.mark.parametrize("rollup,expected", [
    ([], "none"),
    ([{"__typename": "CheckRun", "name": "lint", "status": "COMPLETED", "conclusion": "SUCCESS"}], "green"),
    ([{"__typename": "CheckRun", "name": "lint", "status": "COMPLETED", "conclusion": "SKIPPED"}], "green"),
    ([{"__typename": "CheckRun", "name": "e2e", "status": "IN_PROGRESS", "conclusion": ""}], "pending"),
    ([{"__typename": "StatusContext", "context": "vercel", "state": "PENDING"}], "pending"),
    ([{"__typename": "CheckRun", "name": "e2e", "status": "COMPLETED", "conclusion": "FAILURE"},
      {"__typename": "CheckRun", "name": "lint", "status": "IN_PROGRESS", "conclusion": ""}], "failing"),
    ([{"__typename": "StatusContext", "context": "ci", "state": "ERROR"}], "failing"),
])
def test_check_state_failing_beats_pending_beats_green(rollup, expected):
    assert pr_state.check_state(rollup)["state"] == expected


def comment_item(login, when, association, body="hello", **extra):
    return {"author": {"login": login}, "createdAt": when, "authorAssociation": association, "body": body, "url": "u", **extra}


def test_new_comments_keep_teammates_only_and_count_the_skipped():
    view = {
        "comments": [
            comment_item("hannah", "2026-10-28T10:00:00Z", "MEMBER", "Fixed it, thanks"),
            comment_item("me", "2026-10-28T10:05:00Z", "MEMBER"),
            comment_item("linear-code", "2026-10-28T10:06:00Z", "NONE"),
            comment_item("old", "2026-10-28T08:00:00Z", "MEMBER"),
        ],
        "reviews": [
            {"author": {"login": "sam"}, "authorAssociation": "COLLABORATOR", "state": "APPROVED", "body": "", "submittedAt": "2026-10-28T10:10:00Z"},
            {"author": {"login": "sam"}, "authorAssociation": "COLLABORATOR", "state": "COMMENTED", "body": "", "submittedAt": "2026-10-28T10:11:00Z"},
            {"author": {"login": "sam"}, "authorAssociation": "COLLABORATOR", "state": "COMMENTED", "body": "one more", "submittedAt": None},
        ],
    }
    teammates, skipped = pr_state.new_comments(view, "me", "2026-10-28T09:00:00Z")
    assert [(c["author"], c["first_line"]) for c in teammates] == [("hannah", "Fixed it, thanks"), ("sam", "APPROVED")]
    assert skipped == 1


@pytest.mark.parametrize("state,head,reviewed,comments,expected", [
    ("MERGED", "b", "a", [{}], "merged"),
    ("CLOSED", "b", "b", [], "closed"),
    ("OPEN", "b", "a", [{}], "new_push"),
    ("OPEN", "b", "", [], "new_push"),
    ("OPEN", "b", "b", [{}], "new_comment"),
    ("OPEN", "b", "b", [], "no_change"),
])
def test_event_priority(state, head, reviewed, comments, expected):
    assert pr_state.pick_event(state, head, reviewed, comments) == expected


def review(login, state, oid):
    return {"author": {"login": login}, "state": state, "commit": {"oid": oid}}


def test_your_approval_counts_only_on_the_current_head_by_you():
    view = {"reviews": [review("me", "APPROVED", "old"), review("sam", "APPROVED", "head"), review("me", "COMMENTED", "head")]}
    assert pr_state.approved_by(view, "me", "head") is False
    view["reviews"].append(review("me", "APPROVED", "head"))
    assert pr_state.approved_by(view, "me", "head") is True
    assert pr_state.approved_by({"reviews": []}, "me", "head") is False


@pytest.mark.parametrize("state,head,reviewed,approved,expected", [
    ("OPEN", "b", "b", True, "you_approved"),
    ("OPEN", "b", "a", True, "new_push"),
    ("MERGED", "b", "b", True, "merged"),
    ("OPEN", "b", "b", False, "no_change"),
])
def test_your_approval_ends_the_watch_only_when_nothing_new_was_pushed(state, head, reviewed, approved, expected):
    assert pr_state.pick_event(state, head, reviewed, [], approved) == expected


def test_ready_mark_is_saved_and_old_files_without_it_still_load(temp_project):
    path = sample_monitor(temp_project)
    commit(temp_project, "a.txt")
    assert cli(temp_project, "mark", "7", "ready", "abc1234").returncode == 0
    assert pr_state.Monitor.parse(path, path.read_text()).fields["Ready SHA"] == "abc1234"
    assert pr_state.Monitor.parse(path, path.read_text().replace("Ready SHA: abc1234\n", "")).fields.get("Ready SHA", "") == ""


# --- pr_state: git facts, on a real repo -------------------------------------------------

def test_changes_since_lists_files_after_a_fast_forward(temp_project, monkeypatch):
    first = commit(temp_project, "a.txt")
    head = commit(temp_project, "b.txt")
    monkeypatch.chdir(temp_project)
    assert pr_state.changes_since(first, head) == {"changed_files": ["b.txt"], "needs_pull": False, "history_rewritten": False}


def test_changes_since_says_pull_when_the_new_commit_is_not_local(temp_project, monkeypatch):
    first = commit(temp_project, "a.txt")
    monkeypatch.chdir(temp_project)
    result = pr_state.changes_since(first, "1" * 40)
    assert result["needs_pull"] is True and result["changed_files"] is None


def test_changes_since_flags_a_force_push(temp_project, monkeypatch):
    base = commit(temp_project, "a.txt")
    old = commit(temp_project, "old.txt")
    git(temp_project, "reset", "-q", "--hard", base)
    new = commit(temp_project, "new.txt")
    monkeypatch.chdir(temp_project)
    result = pr_state.changes_since(old, new)
    assert result["history_rewritten"] is True
    assert result["changed_files"] == ["new.txt"]


def test_worktrees_on_branch_finds_the_checkout(temp_project, monkeypatch):
    commit(temp_project, "a.txt")
    git(temp_project, "checkout", "-q", "-b", "feature/x")
    monkeypatch.chdir(temp_project)
    assert pr_state.worktrees_on_branch("feature/x") == [str(temp_project)]
    assert pr_state.worktrees_on_branch("nope") == []


# --- pr_state: monitor file --------------------------------------------------------------

def sample_monitor(repo: Path, branch: str = "feature/x") -> Path:
    git(repo, "checkout", "-q", "-b", branch)
    path = repo / ".vorbit" / "pr7-monitor.md"
    fields = {"PR": "https://github.com/o/r/pull/7", "Repo": "o/r", "Branch": branch, "Status": "watching",
              "Reviewed SHA": "", "Told until": "2026-10-28T09:00:00Z"}
    pr_state.Monitor(path, "PR #7, title", fields, "- my own note\n- Dev server: port 3001", ["- 2026-10-28 14:00 head abc1234 no_change"]).write()
    return path


def test_monitor_round_trip_keeps_notes_log_and_empty_fields(temp_project):
    path = sample_monitor(temp_project)
    loaded = pr_state.Monitor.parse(path, path.read_text())
    assert loaded.fields["Reviewed SHA"] == ""
    assert loaded.fields["Told until"] == "2026-10-28T09:00:00Z"
    assert "Dev server: port 3001" in loaded.notes
    assert loaded.log == ["- 2026-10-28 14:00 head abc1234 no_change"]
    assert pr_state.Monitor.parse(path, loaded.render()).render() == loaded.render()


def test_mark_and_status_update_only_their_own_line(temp_project):
    path = sample_monitor(temp_project)
    commit(temp_project, "a.txt")
    assert cli(temp_project, "mark", "7", "reviewed", "abc1234").returncode == 0
    assert cli(temp_project, "set-status", "7", "waiting_for_user", "needs your go").returncode == 0
    loaded = pr_state.Monitor.parse(path, path.read_text())
    assert loaded.fields["Reviewed SHA"] == "abc1234"
    assert loaded.fields["Status"] == "waiting_for_user"
    assert loaded.fields["Status reason"] == "needs your go"
    assert "my own note" in loaded.notes and len(loaded.log) == 1


def test_permit_turns_a_standing_permission_on_and_off(temp_project):
    path = sample_monitor(temp_project)
    commit(temp_project, "a.txt")
    assert json.loads(cli(temp_project, "permit", "7", "approve").stdout) == {"Auto-approve": "yes"}
    assert pr_state.Monitor.parse(path, path.read_text()).fields["Auto-approve"] == "yes"
    assert json.loads(cli(temp_project, "permit", "7", "approve", "--off").stdout) == {"Auto-approve": "no"}
    assert "Auto-comment" not in pr_state.Monitor.parse(path, path.read_text()).fields


def test_mark_refuses_a_value_that_is_not_a_sha(temp_project):
    path = sample_monitor(temp_project)
    before = path.read_text()
    done = cli(temp_project, "mark", "7", "commented", "not-a-sha")
    assert done.returncode == 2
    assert path.read_text() == before


def test_monitor_for_another_branch_stops_the_run(temp_project):
    sample_monitor(temp_project)
    commit(temp_project, "a.txt")
    git(temp_project, "checkout", "-q", "-b", "other")
    done = cli(temp_project, "mark", "7", "reviewed", "abc1234")
    assert done.returncode == pr_state.EXIT_STATE
    assert "Ask the user" in done.stderr


def test_missing_monitor_file_points_at_init(temp_project):
    commit(temp_project, "a.txt")
    done = cli(temp_project, "set-status", "9", "stopped")
    assert done.returncode == pr_state.EXIT_STATE
    assert "Run init first" in done.stderr


def test_slack_ts_command_prints_json(temp_project):
    done = cli(temp_project, "slack-ts", "https://a.slack.com/archives/C1ABC/p1793154612071909")
    assert json.loads(done.stdout) == {"channel": "C1ABC", "thread_ts": "1793154612.071909"}


def test_gitignore_line_is_added_once(temp_project, monkeypatch):
    commit(temp_project, "a.txt")
    monkeypatch.chdir(temp_project)
    assert pr_state.ensure_gitignore() is True
    assert pr_state.ensure_gitignore() is False
    assert (temp_project / ".gitignore").read_text().count(".vorbit/") == 1


# --- comment_with_images -----------------------------------------------------------------

def test_tags_are_found_in_both_github_forms_and_in_order():
    text = (
        'x <img width="10" alt="a" src="https://github.com/user-attachments/assets/aaa" /> y\n'
        "![b](https://github.com/user-attachments/assets/bbb)\n"
        "![not ours](https://example.com/c.png)\n"
        "![Uploading c.png…]()"
    )
    assert comment.extract_tags(text) == [
        '<img width="10" alt="a" src="https://github.com/user-attachments/assets/aaa" />',
        "![b](https://github.com/user-attachments/assets/bbb)",
    ]


def test_placeholders_are_replaced_by_position_and_repeat_safely():
    body = "{{image:2}} then {{image:1}} then {{image:2}}"
    assert comment.fill_placeholders(body, ["ONE", "TWO"]) == "TWO then ONE then TWO"


def test_placeholder_beyond_the_images_fails():
    with pytest.raises(comment.Fail) as error:
        comment.fill_placeholders("{{image:3}}", ["ONE", "TWO"])
    assert error.value.code == comment.EXIT_INPUT


def test_inputs_must_be_images_that_the_body_uses(tmp_path):
    shot = tmp_path / "shot.png"
    shot.write_bytes(b"x")
    note = tmp_path / "note.txt"
    note.write_text("x")
    comment.check_inputs([str(shot)], "see {{image:1}}")
    for images, body in [([str(note)], "{{image:1}}"), ([str(shot)], "no placeholder"), ([str(tmp_path / "gone.png")], "{{image:1}}")]:
        with pytest.raises(comment.Fail) as error:
            comment.check_inputs(images, body)
        assert error.value.code == comment.EXIT_INPUT


def test_a_comma_in_a_file_name_is_refused_because_upload_joins_names_with_commas(tmp_path):
    shot = tmp_path / "a,b.png"
    shot.write_bytes(b"x")
    with pytest.raises(comment.Fail):
        comment.check_inputs([str(shot)], "{{image:1}}")


# --- dev_port: a real listening process --------------------------------------------------

needs_lsof = pytest.mark.skipif(shutil.which("lsof") is None, reason="lsof not installed")


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture
def server(temp_project):
    commit(temp_project, "a.txt")
    git(temp_project, "checkout", "-q", "-b", "feature/unpublished")
    port = free_port()
    code = f"import socket,time; s=socket.socket(); s.bind(('127.0.0.1',{port})); s.listen(); time.sleep(60)"
    process = subprocess.Popen([sys.executable, "-B", "-c", code], cwd=temp_project)
    deadline = time.monotonic() + 5
    while dev_port.can_bind(port) and time.monotonic() < deadline:
        time.sleep(0.05)
    yield port, process, temp_project
    process.kill()
    process.wait()


@needs_lsof
def test_owner_names_the_folder_and_branch_of_the_server(server):
    port, process, repo = server
    found = dev_port.owner(port)
    assert found["pid"] == process.pid
    assert Path(found["cwd"]).resolve() == repo
    assert found["branch"] == "feature/unpublished"


@needs_lsof
def test_stop_refuses_when_the_pr_is_not_merged_and_leaves_the_server_running(server):
    port, process, _ = server
    done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "dev_port.py"), "stop", str(port)], capture_output=True, text=True)
    assert done.returncode == 2
    assert json.loads(done.stdout)["stopped"] is False
    assert process.poll() is None


@needs_lsof
def test_free_skips_a_busy_port(server):
    port, _, _ = server
    done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "dev_port.py"), "free", "--first", str(port), "--last", str(port)], capture_output=True, text=True)
    assert done.returncode == 1
    assert json.loads(done.stdout) == {"free_port": None}


@pytest.mark.parametrize("state,allowed", [("MERGED", True), ("OPEN", False), ("CLOSED", False), ("none", False), ("unknown", False), ("", False)])
def test_only_a_merged_pr_allows_a_stop(state, allowed):
    assert dev_port.stop_allowed(state) is allowed


@needs_lsof
def test_terminate_stops_the_process_and_frees_the_port(server):
    port, process, _ = server
    assert dev_port.terminate(process.pid, port) is True
    assert process.wait(timeout=5) is not None
    assert dev_port.can_bind(port)


# --- review_recording ---------------------------------------------------------------------

import os

needs_video_tools = pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None or importlib.util.find_spec("PIL") is None,
    reason="ffmpeg and Pillow are needed",
)


def flow(**fields):
    return {"id": "QA1", "name": "Search a word", "result": "Passed", "reason": "ok", "clip": None, **fields}


def write_manifest(folder: Path, flows: list, **top) -> Path:
    path = folder / "review-manifest.json"
    path.write_text(json.dumps({"title": "PR #7: Search", "commit": "abc1234", "ticket": "VIB-1", "verdict": "Not ready", "flows": flows, **top}))
    return path


def bad_manifest(tmp_path, flows, match):
    with pytest.raises(review_recording.Fail) as error:
        review_recording.load_manifest(write_manifest(tmp_path, flows))
    assert error.value.code == review_recording.EXIT_MANIFEST
    assert match in str(error.value)


def test_a_passed_browser_flow_without_a_clip_is_refused(tmp_path):
    bad_manifest(tmp_path, [flow()], "A pass needs a recording")


def test_a_passed_test_command_may_have_no_clip(tmp_path):
    review_recording.load_manifest(write_manifest(tmp_path, [flow(id="QP1", kind="command")]))


def test_manifest_rules_for_reason_result_clip_and_ids(tmp_path):
    bad_manifest(tmp_path, [flow(result="Not done", reason="")], "needs a reason")
    bad_manifest(tmp_path, [flow(result="Flaky")], "result must be one of")
    bad_manifest(tmp_path, [flow(result="Failed", clip="gone.webm")], "missing or empty")
    bad_manifest(tmp_path, [flow(result="Not done", reason="x"), flow(result="Not done", reason="y")], "appears twice")
    bad_manifest(tmp_path, [], "at least one flow")
    (tmp_path / "empty.webm").write_bytes(b"")
    bad_manifest(tmp_path, [flow(result="Failed", clip="empty.webm")], "missing or empty")


def test_cards_show_counts_and_say_when_a_pass_is_from_an_earlier_commit():
    manifest = {"title": "T", "commit": "abc1234", "ticket": "VIB-1", "verdict": "Ready", "flows": [
        flow(), flow(id="QA2", result="Failed", commit="old9999"), flow(id="QA3", result="Not done", reason="no data")]}
    opening = [text for text, _, _ in review_recording.card_lines(manifest, None)]
    assert "1 passed, 1 failed, 1 not done" in opening
    earlier = [text for text, _, _ in review_recording.card_lines(manifest, 1)]
    assert "Tested earlier, on commit old9999" in earlier
    assert not any("Tested earlier" in text for text, _, _ in review_recording.card_lines(manifest, 0))


def make_clip(path: Path, seconds: int, size: str) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"testsrc=duration={seconds}:size={size}:rate=25", "-c:v", "libvpx", str(path)],
        check=True,
    )


def frame_at(video: Path, seconds: float, out: Path):
    from PIL import Image
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(seconds), "-i", str(video), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


@needs_video_tools
def test_recording_joins_cards_and_clips_in_order_with_real_footage(tmp_path):
    make_clip(tmp_path / "a.webm", 2, "320x240")
    make_clip(tmp_path / "b.webm", 1, "640x360")
    flows = [
        flow(id="QA1", name="First", clip="a.webm"),
        flow(id="QA2", name="Second", result="Failed", reason="Saw the wrong thing", clip="b.webm"),
        flow(id="QA3", name="Third", result="Not done", reason="need data"),
        flow(id="QP1", name="Tests", kind="command", reason="3 of 3"),
    ]
    out = tmp_path / "out" / "review.mp4"
    done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "review_recording.py"), str(write_manifest(tmp_path, flows)), "--out", str(out)], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert (result["passed"], result["failed"], result["not_done"]) == (2, 1, 1)
    expected = 4 + 4 * 3 + 2 + 1
    assert abs(result["seconds"] - expected) < 1.0
    assert not list(out.parent.glob(".*partial*"))

    opening = frame_at(out, 1, tmp_path / "f1.png")
    assert opening.getextrema()[0][1] > 200, "the opening card has bright text"
    footage = frame_at(out, 4 + 3 + 0.5, tmp_path / "f2.png")
    assert len(footage.getcolors(maxcolors=100000)) > 50, "the clip frame is real picture content, not a flat card"
    no_clip_card = frame_at(out, 4 + 3 + 2 + 3 + 1 + 1.5, tmp_path / "f3.png")
    assert no_clip_card.getextrema()[0][1] > 120, "the Not done card has text"


@needs_video_tools
def test_a_bad_manifest_makes_no_video(tmp_path):
    out = tmp_path / "review.mp4"
    done = subprocess.run([sys.executable, "-B", str(SCRIPTS / "review_recording.py"), str(write_manifest(tmp_path, [flow()])), "--out", str(out)], capture_output=True, text=True)
    assert done.returncode == review_recording.EXIT_MANIFEST
    assert "A pass needs a recording" in done.stderr
    assert not out.exists()
