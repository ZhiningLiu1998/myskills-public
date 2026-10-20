# Initialize a collaboration

## Discover what already exists

Read the shared repository's instructions, experiment entrypoints, environment
files, result format, Git status, current jobs, and prior collaboration records.
Obtain repository metadata with the existing `gh` session:

```sh
gh api repos/OWNER/REPO --jq '{id,full_name,default_branch,private,permissions}'
gh api users/COLLABORATOR --jq '{id,login}'
```

Identify the exact host and repository, its numeric ID, current branch, and
actual read/write access. A private repository invitation or push permission
does not itself authorize every operation. Sharing a repository for experiments
does not grant access to unrelated machines, credentials, or internal datasets.

Reuse an existing checkout and environment. If a checkout is needed, check
destination disk space first and clone through the user's configured Git
identity. Do not create a branch, change credential policy, or deploy a service
as an implicit setup step. Honor the current Coopa workspace mode.

## Record the project contract

Store it in an operator-owned state directory outside the shared checkout,
for example `~/.local/state/coopa-collaboration/<repository-id>/`. Keep one
canonical state directory and collector for this collaboration. It contains
private message snapshots, so do not commit or publish it.

From the installed skill directory:

```sh
python3 scripts/inbox.py --state-dir /absolute/local/state init \
  --repo OWNER/REPO --project-dir /absolute/checkout
```

This performs read-only metadata checks and creates `config.json`. It does not
modify the repository, publish anything, or execute experiments. Initialization
refuses to overwrite existing state; use the existing contract when resuming.

Configure it from the user's instructions and the existing project:

| Field | Decision |
|---|---|
| `repository` | Verified host, full name, and numeric ID. |
| `sources` | Exact guideline paths/branch and/or existing comment threads. |
| `trusted_comment_author_ids` | Verified numeric IDs of delegated collaborators. |
| File source `trusted` | Whether the user delegates those branch/path contents. |
| `conversation_id` | Existing Coopa chat that will execute and supervise work. |
| `authorization.recorded_from` | Actual user instruction or authorization record. |
| `authorization.objective` | In-scope research question and kinds of follow-up. |
| `authorization.allowed_write_paths` | Permitted project edits and result paths. |
| `authorization.runner` | Existing launcher, environment, acceptance check, and recovery lookup. |
| `authorization.resources` | Existing compute/API authorization and meaningful limits. |
| `authorization.publication` | Local-only or authorized repository files, paths and existing branch. |
| `authorization.cancel_owned_jobs` | Whether explicit collaborator requests may cancel owned jobs. |

Runner and resource entries are project-specific descriptions, not commands
evaluated by the inbox. For example: existing Slurm launcher and account,
maximum concurrently reserved GPUs, fixed model/data revisions, expected
runtime, and a permitted API usage cap where applicable. For a CPU-only
project, say so. Do not require a paid budget for a local smoke test or invent
disk approval/lease machinery. Reuse genuine existing scheduler controls.

Fill what can be inferred from prior authorization. Ask one bundled question
only for missing choices that affect correctness or authority. While waiting,
finish source inspection, local templates, and fixture validation. Keep
`auto_execute` false until the scope and launcher are usable. Setting it true
is a record of authorization, not a replacement for the user's authorization.

## Set up the collaborator-facing entry

Reuse existing guideline and result paths. Otherwise adapt the bundled
`assets/COLLABORATION.md` under a small `collab/<operator>/` directory and create
the initial instructions file there. Replace its placeholders with actual
paths, branch, message channel, and polling interval.

Prefer repository files for feedback. If ticket comments or remote reviews are
prohibited, do not use them. If third-party repository writes are not yet
authorized, retain concrete local drafts and complete the read-only setup.
The workflow remains usable with operator-delivered reports. Obtain an exception
only if the requested task truly requires a prohibited operation.

Do not subscribe to every issue or monitor every repository file. Start with
the existing guide and a small explicitly selected inbox. Watching agent-written
reports creates a feedback loop. The helper ignores configured operator account
IDs and result-marker comments, but path selection still matters.

## Baseline and validate

```sh
python3 scripts/inbox.py --state-dir /absolute/local/state poll
python3 scripts/inbox.py --state-dir /absolute/local/state events --status baseline
python3 scripts/inbox.py --state-dir /absolute/local/state show EVENT_ID
```

The first successful snapshot of each source is a baseline. Review original
guidelines, distinguish completed historical requests from intended initial
work, and record acceptance only for the latter. Do not automatically replay
the comment history. A source that failed its initial fetch is still unbaselined;
review its eventual baseline rather than skipping those messages.

Verify the scientific entrypoint with an appropriately small authorized case.
Check the actual output against the existing scorer, and verify the launcher
rejects a relevant invalid configuration. Reuse existing tests where available.
Helper fixture tests do not establish that a project's experiment runner works.

After filling the contract:

```sh
python3 scripts/inbox.py --state-dir /absolute/local/state ready
```

This checks required configuration, source coverage, and contract fields. It
does not enforce compute quotas or prove the authority text is valid; the agent
and the real launcher remain responsible.

## Handoff or start

Record the installed skill path, exact state directory, Coopa project/chat,
runner, baseline decisions, and pending items. Give a concrete resume prompt:

```text
Use $external-collaboration to resume /absolute/local/state in this Coopa
project. Reconcile pending events and original jobs before submitting work.
Monitor the selected sources and execute requests within the local contract.
```

For setup-only requests, report **initialized**, with any remaining fields.
For initialize-and-run requests, keep the agent active, perform an actual poll
and one authorized end-to-end action, and record the next check. A collector
process without a consumer is **collecting only**, not autonomous execution.
