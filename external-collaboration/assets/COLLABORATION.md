# Working with the experiment agent

This repository is our shared record of requests and verified results. The
agent runs work within the project scope and resources agreed with its operator.

## Where to write

- Guidelines: `<existing guidelines or collab/agent/INSTRUCTIONS.md>`
- New requests: `<collab/agent/requests/*.md or selected GitHub thread>`
- Results and execution receipts: `<collab/agent/STATUS.md and results/>`
- Expected polling interval: `<300 seconds>`

For a selected comment thread, begin the first line with `@coopa`. Only the
configured collaborator accounts are accepted. Please create a new message for
a material revision so it remains visible between polls.

For a watched file, commit the request to the agreed branch. Keep agent-written
status and results outside watched input paths.

## Example request

```markdown
@coopa
Request: compare-retrieval-03
Target: retrieval experiment
Change: Compare the current baseline with top-k=8 on the agreed validation split.
Effective: Next unsubmitted batch; let existing jobs finish.
Supersedes: none

Use the existing seeds, model revision, prompt, and scorer. Report per-seed
accuracy, runtime, and failures, with the command and code revision needed to
reproduce each run. Completion means all planned runs have valid scorer output.
```

Plain prose is fine; the agent will map it to the existing experiment plan.
For a correction, cite the old request ID and explain which runs it affects.
Do not silently edit past results. Deleting a request does not cancel a job.
To pause new submissions or cancel a specific owned job, say so explicitly.

## What the status means

| Status | Evidence |
|---|---|
| Received | The request revision was saved. |
| Accepted | The agent read it and mapped it to an authorized plan. |
| Queued | The original scheduler/session recorded the submission. |
| Running | The original job has started. |
| Validated | The run exited and passed its stated acceptance checks. |
| Reported | Verified results reached the agreed report destination. |
| Needs input | A specific ambiguity or authority gap prevents this request. |
| Failed | The attempted run failed; original evidence is retained. |

Feedback includes the request ID/revision, affected run IDs, actual status,
result location, and any decision needed. Unchanged polling does not generate
commits or repeated replies. Positive and negative results use the same checks.

New requests cannot grant access to unrelated data, change the operator's
permissions, increase an agreed budget, publish to a new destination, or erase
results. The operator resolves those changes; other authorized work continues.
