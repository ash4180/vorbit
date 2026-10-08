<!-- GENERATED from skills/tutorial/SKILL.md — edit the canonical file, then run: python3 -m vorbit_core.project_skills --write -->

# Tutorial Skill

Write a user tutorial for a finished feature: numbered steps, one screenshot per step, a short GIF for the main path, plain words for someone who has never opened the app. The doc copies the project's existing docs. When no docs exist, the user picks the format and folder before anything is written.

Read and follow `../references/execution-contract.md` before starting.

Read `../references/spec-files.md` for spec path resolution before any spec read.

The doc is for end users, not developers. Developer reference docs, code comments, QA plans, and acceptance checks belong to other skills.

## Step 1: Find the Doc Pattern

1. Look for existing user docs: `docs/`, `documentation/`, `guides/`, `help/`, `wiki/`, a docs site config (`mkdocs.yml`, `docusaurus.config.*`, `mint.json`, `_sidebar.md`), or a `README` section that walks a user through a feature.
2. When found, read the two most recent tutorial-like docs. Note the pattern: folder, file naming, front matter, heading order, image folder, image naming, tone, callout style. The new doc copies this pattern exactly. Never invent a new format when one exists.
3. When nothing tutorial-like exists, ask the user, batched: format (Markdown by default), doc folder, image folder, and file name. Never write before the user answers.
4. If a doc for this feature already exists, this run is a revision: keep its file name, update it in place, and never create a duplicate.

## Step 2: Read the Feature

1. Resolve the spec folder per `../references/spec-files.md`. Read `prd.md` when it exists: its user stories and flows become the tutorial sections and steps. Read `epic.md` for screen and route names when present.
2. **No PRD is not a blocker.** Ask the user, batched: what the feature does in one sentence, who uses it, the main path from start to done, and what the user needs first (account, role, data). Record `Source: conversation` in the session report.
3. Ask, batched, whatever the sources leave open: audience (end user, admin, internal team), where the running app is (URL, test account), and which flows to include when there are several. Never guess the audience.

## Step 3: Capture Screenshots and a GIF

Run when the runtime has a browser-automation capability that can take screenshots (for example Playwright MCP tools or a connected browser) and the app is reachable:

1. Confirm the app URL and test account with the user once. Sign in with the test account only, never with the user's real account.
2. Walk the flow step by step. Take one screenshot per step where the screen changes. Size the browser to the area that matters (a phone width for mobile flows). Hide test data that looks private.
3. Record one short GIF (about 5 to 15 seconds) of the main happy path when a GIF recorder is available. Skip the GIF, without asking, when none is.
4. Save files into the image folder from Step 1 as `<doc-slug>-<NN>-<short-label>.png` and `<doc-slug>-flow.gif`. Match the project's existing image naming when it has one.
5. Never describe a screen the agent did not see. A step without a captured image gets a placeholder (Step 4).

When no browser capability exists, the app is unreachable, or a step cannot be shown (real phone, email inbox, camera): skip capture for that step and keep going. Do not stop.

## Step 4: Write the Doc

**Writing rules (every line):**
- Plain, everyday words. Sentences of 12 words or fewer, one idea each. No long dash. No metaphors or idioms.
- Name buttons, fields, and screens exactly as the user sees them, in bold. No code words, file paths, or internal names.
- One step = one action plus what the user sees next. If a step needs "and then" twice, split it.
- Every step that changes the screen has an image right after it.
- Missing image: keep the image line as a placeholder plus a marker: `![Step 3: Tap Save](images/<doc-slug>-03-save.png) <!-- TODO screenshot: what to show -->`.

### Doc schema (default; the project's own pattern wins when one exists)

```markdown
# How to [do the thing]

[One sentence: what the user gets at the end.]

**Before you start:** [what the user needs: account, role, data]. Takes about [N] minutes.

![Main flow](images/<doc-slug>-flow.gif)

## Steps

1. Open **[Screen]**. You see [what].
   ![Step 1: Open Screen](images/<doc-slug>-01-open.png)
2. Click **[Button]**. [What appears].
   ![Step 2: Click Button](images/<doc-slug>-02-click.png)

## Done

[What the user should now see or be able to do.]

## If something goes wrong

- [Error or empty state the user may see]: [what to do].

## Related

- [Link to a related doc, if any]
```

Show the full draft in the session with the list of captured images and placeholders. Save only after the user approves. Apply their edits and show the draft again if anything changed.

## Step 5: Save and Share

1. Write the doc and images to the folder from Step 1. Report the paths and the placeholder count.
2. **Notion (optional):** when a Notion connector is connected, ask once whether to post a copy. If yes, save via the connected platform's current content-creation tools (inspect schemas first) and pass the doc text; record the page URL. Images that cannot upload stay as links to the repo file; say so.
3. **Linear (optional):** when a Linear connector is connected and the story has a ticket (the `## Linear Sync` section in `prd.md`, or an ID the user gives), ask once, batched:
   - add the doc link to the ticket (attachment or link): yes or no
   - leave one comment that mentions someone: yes or no, and who
   Read the ticket's existing comments first and copy the team's mention style (for example a leading `@Name`). Show the exact comment text and post only after the user approves it. This is the one Linear comment a Vorbit workflow may post, and only on the user's explicit yes in this session.
4. Skip 2 and 3 silently when the connector is absent.

## Step 6: Report in the Session

- Doc path, plus Notion URL and Linear ticket when used, one line each
- Images: N captured, M placeholders (list the placeholders so the user can add them)
- Source: `prd.md` or conversation
- Next: fill the placeholders and re-run this skill to revise, or run `$vorbit-prepare-pr` to ship the doc with the branch

End with one terminal status per the execution contract.
