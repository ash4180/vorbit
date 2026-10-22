# Sign in with the test accounts

Read before Step 1 checks the plan's accounts, and before a runner's first flow. When a test account "cannot sign in", the cause is most often the method, not the password. Use the project's own way in.

## Find the method (parent, Step 1)

1. Take each account, and the env keys that hold it, from the plan's `Needs:` lines and the env file the project's tests load (for example `.env.local`). Never use an account from memory, chat history, or an old report. A retired account fails the same way a broken one does.
2. Find how the project's own tests sign in: an auth setup test or global setup, its sign-in helper, and the test README. For each account, note its saved-login file (a saved browser state, for example Playwright `storageState`), the command that renews it, and every hand sign-in step. Copy unusual steps exactly, such as an SSO bypass button or a different address typed on an earlier screen.
3. Renew every saved login with the project's command right before the first flow. Point the command at the same address and port the flows use, through the project's base-URL or port setting. A saved login works only at the address where it was made, port included. After any environment, host, or port change, force a fresh sign-in with the project's reseed option.
4. An account with no saved-login setup is signed in by hand, per the steps below.
5. Put the method in `runner-task.md`. For each account, list the env key names (never their values), the saved-login file, the renew command, and the hand sign-in steps.

## Sign in (parent and runner)

1. Use a new browser context for each account, and load its saved login when one exists. Never sign in as a second account where another account was signed in, because the old login can win.
2. Without a saved login, follow the hand sign-in steps. Typing a test account's password from the env file is allowed and expected. Prefer a script that reads the value from the environment, so it never appears in chat. Never print or echo it, and never write it into messages, logs, evidence, or the report.
3. Sign in before a flow's recording starts. Sign in within its own context and save that context's browser state. Then open the recording context with that state loaded. When sign-in is itself the tested flow, hide the typed value per `recording.md`.
4. Before the first step, confirm the signed-in account from what the app shows, such as the profile menu or account page. If it is a different account, that role's flows are `Not done: signed in as the wrong account`; never record their results.
5. When the sign-in screen appears mid-run, renew that saved login once and restart the flow from its first step.
6. If sign-in still fails, that account's flows are `Not done: cannot sign in as [account]`. Under For developers, record the address, the step that failed, and the exact message shown (for example "Wrong email or password", a callback error, or a redirect to a company SSO page). Never report a sign-in failure without that detail.
