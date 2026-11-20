# Run an existing plan with Sonnet or Luna

Use this handoff for qa-report Step 2.5 only, after the parent completes Steps 1, 2, and 2.4. A small run (Step 2.5: 3 or fewer flow tests) skips this handoff; the parent runs those tests. Planning, writing flow tests, automated commands, API speed analysis, suggested fixes, final judgment, and publishing stay with the parent. Prefer Claude Fable or Codex Astra (`gpt-6-astra`) for that work; a skill cannot switch the parent model. Honor an explicit caller model override and record the actual selection.

## Choose the runner

Use the host's native subagent tool. Inspect its actual parameters before calling it; a model name in the prompt does not select a model.

| Parent host | Launch | Continue the same agent |
|---|---|---|
| Claude Code | `Agent` with `subagent_type: "vorbit:qa-runner"`; the plugin's `agents/qa-runner.md` sets `model: sonnet`. Pass `model: "sonnet"` too when the tool supports it. | Use the returned agent ID with `SendMessage`, or the installed version's native resume operation. |
| Codex with per-agent model selection | `spawn_agent` with `model: "gpt-6-luna"`, `fork_turns: "none"`, a unique task name, and the handoff message. | Use `followup_task` with the returned ID, or the host's native equivalent that wakes a finished agent. |
| Other Codex hosts, Gemini, or an IDE | Require a native runner with explicit selection of the requested model, either a supported model parameter or an already configured agent role whose model setting you have read. | Inspect the host's continuation operation. Do not invent parameters or assume an ordinary message wakes a finished agent. |

The Claude agent ships with the plugin and inherits available tools and permissions while denying nested `Agent` calls. Do not substitute Explore or Plan: these are not browser execution agents. If `vorbit:qa-runner` is missing, reload the installed plugin or restart Claude; do not claim it ran. For a source checkout, `bash dev-setup.sh` at the plugin root installs newly added plugin components before the restart.

Start **one subagent per run**, unless Parallel runners below applies. It runs flow tests as `recording.md` Flow tests items 7 to 9 say: safe flows together in one batch, the rest one by one, then one judging pass. It drives flows with a browser tool one by one, in plan order. Keep the exact current worktree; do not request worktree isolation. Codex full-history forks may inherit the parent's model and reject an override, so use a fresh context with `fork_turns: "none"` when that control exists. Supply all required paths and constraints explicitly. Never assume the child sees the parent's conversation, loaded skills, or browser connection.

If native delegation, model selection, or continuation is unavailable, affected flows are `Not done` with the specific reason. Do not silently use the parent, another model, or a shell-launched CLI session. An explicit caller choice to run in the parent is allowed and must be recorded as an override, not a subagent run. Missing-data and human-only checks keep their Step 1 reasons. If all flows are already ineligible, record those reasons without launching a runner.

## Parallel runners

Flow tests need no extra runner: one runner runs the `Parallel: yes` flows together with Playwright workers (`recording.md` Flow tests, item 7). This section is for flows driven with a browser tool.

Start more than one runner only when the caller allows it (for example "up to 2 runners") and the plan tags flows `Parallel: yes`. Otherwise start one runner, run the flows in plan order, and ignore the tags.

1. Split the `Parallel: yes` flows across the runners, in plan order inside each runner. Runner N gets its own browser context and its own files in the run folder: `runner-task-N.md`, `runner-ready-N.json`, `runner-session-N.json`, `flow-results-N.json`, and `created-data-N.json`. A single runner keeps the names below, without `-N`.
2. Before launch, the parent signs in once per `sign-in.md`, starts the app once, checks that it answers, and opens one recorded browser page itself. Each `runner-task-N.md` names the app address and that check, and for each account its saved-login file, env key names, and hand sign-in steps. A runner trusts the check and opens no test browser in Prepare. An app login can end mid-run, so the parent renews every saved login again right before launch.
   - A runner that runs flow tests (`recording.md` Flow tests) uses the project's own sign-in setup and needs none of the steps below. They apply to a runner that drives a browser tool.
   - Each runner copies the saved logins it needs into its own `login-N/` folder in the run folder, and loads only those copies.
   - A runner never runs the renew command and never writes the project's saved-login files, because the other runners load them too.
   - When the sign-in screen appears, the runner signs in by hand per `sign-in.md` in a new context. It saves that state over its own copy and restarts the flow from its first step, once per flow.
   - If that sign-in fails, the flow is `Not done: cannot sign in as [account]`, and the parent reruns it in step 5.
3. Each runner creates its own flows' setup records per `test-data.md`, just before each flow's recording, so no runner waits for all the data. A flow test creates them in its own setup. It logs each record in its `created-data-N.json` as soon as the record exists, and opens the flow's start screen by the new record's ID. It never searches for, reuses, or changes a record it did not create. A flow whose record cannot be created is `Not done: need [X]`, and the runner goes on to its next flow.
4. Prepare all runners, then execute them together, each with the steps below and its own files. While they run, the parent runs Step 2's automated checks, which need no records.
5. After every parallel runner has finished, one runner runs the `Parallel: no` flows, untagged flows, and the reruns, in plan order, with no other runner active.
6. Parent review checks each runner's files. Then the parent writes one `flow-results.json` with every flow in plan order, so later steps read one file. Step 2.8 deletes the records in every `created-data` file.

## Prepare the handoff

The parent owns the unique evidence folder already created in Step 1. Resolve absolute paths and write `runner-task.md` there, containing:

- `Role: flow runner; do not delegate`. The first invocation is **Prepare only**. Do not execute flows until resumed by the parent with `runner-session.json`.
- The exact worktree path, branch, revision, whether it has local changes, absolute `qa-plan.md` path, and run evidence folder. Record a digest of the plan and current source diff, including relevant untracked source files, so concurrent changes can be detected. Exclude this run's generated evidence from the source digest.
- Absolute paths to the installed qa-report workflow, this reference, `recording.md`, `sign-in.md`, `test-data.md`, the execution contract, and the browser/recording skills to read. For Codex/Gemini installations the workflow is in the sibling `vorbit-shared/workflows/qa-report.md`; references remain in the installed qa-report skill. Resolve paths for the runner's runtime.
- The requested model, environment, ordered flow IDs in scope, exact steps and `You should see:` text (or the plan path containing them), the absolute path of the run folder's `flow-tests/` handoffs from Step 2.4, and every Step 1 eligibility decision. Include human-only and missing-data flows so none disappear from the report.
- The caller's testing authorization and restrictions, and the sign-in method from Step 1 per `sign-in.md`. Name env keys; never copy passwords or tokens into prompts or evidence files.
- Write scope: evidence and runner result files inside this run folder, records created per `test-data.md` and logged in `created-data.json`, and the saved-login files the sign-in renew command rewrites. The child may run that renew command, except as a parallel runner, which writes only its own `login-N/` copies. It must not re-plan, run the parent's automated commands, write or edit flow tests, fix source, edit the plan/report, publish, or launch other agents or CLI sessions. Do not invoke the full qa-report workflow recursively.
- The requirement to follow the workflow's Flow rules and recording reference, check console errors, retain failures, and never fake server responses. Release owned browser contexts and remove only temporary files created by this run.

Do not run a second browser driver or change source, plan, or test data while the runner uses them. The parent can read existing evidence while waiting.

## Prepare, record the launch, then execute

### 1. Prepare (subagent)

Launch with the absolute handoff path and the instruction **Prepare only; return without executing flows**. The subagent reads the handoff and its referenced instructions, checks its actual working directory against the handoff, rechecks eligibility, and inspects its own browser/recording tools and permissions. It may perform read-only capability checks, but must not run flow actions or change application data.

The subagent writes `runner-ready.json` with `worktree`, `plan_digest`, `source_digest`, `status` (`ready` or `blocked`), `eligible_ids`, `not_done` (ID and reason per ineligible flow), `browser_tool`, `recording_method`, and `blockers`. Name actual tools/methods verified from the installed setup. Screenshot support alone is not recording support. Preserve the execution contract's connector login rules. A denied required action is a blocker; do not alter permissions to bypass it. Return the readiness file path and stop this turn.

Use `ready` only when at least one assigned flow can run with the required browser and recording capability. Per-flow missing needs stay in `not_done` while other eligible flows may proceed. Use `blocked` when no flow can run or a required shared capability is missing.

### 2. Record the launch (parent)

Wait for Prepare to finish. Save the returned native agent ID, not a name invented in chat. Validate the readiness file's worktree, digests, scope, and capability findings. Record all launch failures even if no file was written.

Write `runner-session.json` in the evidence folder with:

- `agent_id`: the handle returned by the native tool; null if launch failed.
- `runtime`, `requested_model`, `actual_model`, and `model_evidence`: distinguish the requested model from the model confirmed by runtime metadata. An agent's self-description is not confirmation. When metadata is unavailable, use null for `actual_model` and say `requested via native model selection; actual model unverified`.
- `worktree`, `plan_digest`, `source_digest`, the assigned `flow_ids`, and the readiness-file path.
- `status`: `prepared`, `running`, `completed`, `blocked`, `failed`, or `canceled`, plus `reason` when needed. These describe the runner, not QA verdicts.

Require a successful explicit model selection via the native tool or loaded agent configuration. If runtime metadata reveals a different model, stop and report the substitution; a caller override must be explicit. A host that accepts the selection but exposes no resolved-model metadata may continue, with that verification limit recorded.

Tell the user `QA runner prepared: [runtime], requested [model], agent [returned ID]` only after readiness is `ready`; state any model verification limit. If readiness is `blocked`, no agent ID exists, or the readiness result is unusable, save a blocked session record and mark affected flows Not done. Never resume execution from a blocked readiness result or write `prepared` merely because a prompt was composed.

### 3. Execute (same subagent)

Only after the session record is saved, resume the **same** agent with: `Execute the assigned flows from runner-task.md. Read runner-session.json at [absolute path] first. Do not delegate.` Use Claude's `SendMessage` to that ID (or native resume on versions that expose it), or Codex's `followup_task` (or equivalent). Keep the selected model on continuation when the host requires it. Do not create a second agent. Set the session status to `running` when continuation succeeds.

The runner requires `runner-ready.json` to be `ready` and the session status to be `prepared` or `running`, then checks the saved worktree, digests, and flow IDs against its handoff before flow actions. It follows Step 2.5's Flow rules in plan order and writes `flow-results.json` after each judged flow using a temporary file and atomic rename. With flow tests, every run comes before the judging pass, and each command's evidence is collected right after it, so an interrupted run keeps its evidence. It copies `agent_id` from the session record for correlation, not as independent proof of identity. It returns evidence paths and blockers when finished. Partial evidence must survive interruption.

### 4. Wait and collect (parent)

Keep the native agent handle and wait for its completion notification. A message delivery acknowledgment or temporary silence is not completion. A ready response is not an execution result. If work stops early, retain valid completed evidence and mark remaining flows Not done. Resume interrupted work only after checking partial results and test-data state; do not blindly repeat mutations or restart the whole run.

On cancellation, stop the owned subagent using the host's native control and verify it stopped before taking over its browser. Preserve evidence and release only its owned resources. Do not close or terminate unrelated user sessions. Update the session status from the native completion/error result; `completed` does not mean all flows passed.

## Result contract

The child writes `flow-results.json` (parallel runner N: `flow-results-N.json`) in the run evidence folder. Paths to clips and screenshots are relative to that folder. Use JSON null for absent evidence, never an invented path. Example of one completed flow:

```json
{
  "schema_version": 1,
  "worktree": "/absolute/path/to/worktree",
  "revision": "revision recorded by the parent",
  "plan_digest": "digest supplied by the parent",
  "source_digest": "digest supplied by the parent",
  "agent_id": "handle copied from runner-session.json",
  "started_at": "2026-10-20T04:20:00Z",
  "finished_at": "2026-10-20T04:21:00Z",
  "complete": true,
  "blockers": [],
  "flows": [
    {
      "id": "QA1",
      "result": "Passed",
      "reason": "Every expected result matched",
      "steps": [
        {"step": 1, "expected": "Billing page opens", "observed": "Billing page opened", "matched": true}
      ],
      "console_errors": [],
      "video": "QA1-billing.webm",
      "screenshot": "QA1-billing.png",
      "extra_evidence": []
    }
  ]
}
```

`result` is exactly `Passed`, `Failed`, or `Not done`; it is a provisional result until the parent reviews it. Include each performed step's expected and observed result, all console errors, and supporting clips/screenshots in `extra_evidence` (including popup recordings and console screenshots when applicable). Each Not done row needs a specific reason. A failure stays Failed even if recording also fails. Model selection and runtime verification belong in the parent-owned `runner-session.json`, not in the runner's self-report.

`complete` means every assigned flow has a row, including Not done rows; it does not mean every flow passed. During execution use `complete: false` and `finished_at: null`. Prepare or launch failures may leave no result file at all.

## Parent review

1. Wait for the subagent execution to finish. Read its native completion/error result, parse the result file, and match its agent ID, worktree, revision, and digests to the saved handoff and session record. Recheck the plan and source against the starting state. If either changed during execution, do not claim results cover the new state; record the gap and reconcile before rerunning.
2. Compare result IDs with the assigned list. Missing IDs become Not done; duplicate or unknown IDs, malformed JSON, or a mismatched run identity are evidence errors, never passes. On an evidence error, retain artifacts for inspection and mark unverifiable flows Not done. A native failure/cancellation or `complete: false` must stay visible in the report even when some completed flows have valid evidence.
3. Verify each linked file resolves inside this run folder, exists, and is nonempty. Review the recording's result segment and compare the observed steps with the original plan. A child's Passed label is insufficient. Missing recording means Not done; observed mismatches or new console errors mean Failed even if the clip is missing. Never infer a human confirmation from a child result.
4. Use verified results in Steps 2.6–4. The parent performs pre-existing-failure classification, suggests fixes, writes the final report, updates only the plan's result lines and Updated date, and publishes only when requested. Under For developers, link `runner-session.json` and `flow-results.json`, recording the runtime, requested/verified model, agent ID, terminal state, and execution gaps. Keep infrastructure failures visible in the verdict; they cannot produce Ready through missing rows.

Claude runtime reference: [custom subagents, model selection, and continuation](https://code.claude.com/docs/en/sub-agents). Codex tool parameters vary by host; inspect the live tool schema.
