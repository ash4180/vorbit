# Create and delete test data

Read before Step 1 checks the plan's needs. On the local app or DEV, a missing record is created, not reported as missing. Everything this run creates is deleted at the end.

## When to create

1. Setup records are created only on the local app or the DEV environment. On staging, production, or an unknown environment, a missing record stays `Not done: need [X]`. A flow whose own steps create a record (for example "Create a schedule") runs freely on the local app or DEV. On any other environment, an attended run asks once, batched with Step 1's other questions, before the first flow. An unattended run marks those flows `Not done: creates data on [environment], needs approval`. Log and delete every created record the same way.
2. The parent creates setup records in Step 1, before the runner starts. Prefer the project's API or test helpers; the app's screens are allowed too. The runner creates only what its flow steps create.
3. Create the records the plan marks `Agent creates:`, and any other record a flow needs that the test accounts can make. Use the app's screens or the project's own API or test helpers (seed scripts, fixtures). Never write to the database directly.
4. Create only what the flows need, in the starting state the plan names (for example two rotations with the same start time, or enough rows to cross a page).
5. Never change or delete a record this run did not create. To act on a shared record, create an own copy and act on that.
6. A record that sends messages (pages, alerts, emails, SMS, chat) is created only when every recipient is a test account. When the plan's record would reach a real person, build an own copy whose recipients are all test accounts, if that still tests the flow. Otherwise the flow is `Not done: needs a person (would message a real person)`.
7. Data the test accounts cannot create (billing, a real device, an outside service) stays `Not done: need [X]`.

## How to create

1. When the record has a name, name it `QA <YYYY-MM-DD HHMM> <what>`, so people can see it is test data.
2. Right after each create, add an entry to `created-data.json` in the run evidence folder: type, name, ID, environment, account, and how to delete it. Write the entry before the next action, so a crash still leaves the list. The runner also logs every record its flows create.
3. Create setup records before the flow's recording starts, unless creating them is the tested flow.

## Delete at the end (parent)

1. After the runner finishes, delete every record in `created-data.json`, newest first, with the same account and method. Do this even when the run failed or stopped early.
2. Confirm each one is gone by opening or searching for it, then mark it deleted in the file.
3. A record that cannot be deleted goes under For developers with its type, name, ID, and reason, and in the session report.
4. Never delete a record that is not in the list, even one that looks like old test data.
