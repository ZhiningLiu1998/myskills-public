# Inbox configuration and operations

The helper requires Python 3.10+ on macOS/Linux and the installed authenticated
GitHub CLI. It uses only GET requests and never launches a shell from message
content. Local state contains original private messages; keep it outside Git,
with access limited to the operator. Use one state directory on one consumer
host. SQLite and local file locks do not coordinate independent copies across
machines; remote compute should still be driven by that consumer.
Check `python3 --version` in the execution directory; if it is older than 3.10,
use an existing compatible interpreter's absolute path for all commands.

## Sources

Start from `assets/config.example.json`; `init` fills repository metadata,
default branch, project path, and the current account's ignored numeric ID.
Replace the default file paths with the project's real guidelines.

```json
[
  {
    "id": "guide",
    "kind": "files",
    "ref": "main",
    "paths": ["docs/EXPERIMENTS.md", "collab/agent/requests/*.md"],
    "trusted": true
  },
  {"id": "requests", "kind": "issue", "number": 12},
  {"id": "inline", "kind": "pull_review", "number": 24},
  {"id": "commit-review", "kind": "commit", "sha": "FULL_COMMIT_SHA"}
]
```

These are supported options, not a recommendation to enable all of them.
An `issue` source also covers an existing PR's main conversation, including its
body. `pull_review` covers inline review comments, not review-summary bodies.
Files use shell-style `fnmatch` paths over repository-relative paths; `*` can
match `/`. Keep patterns narrow and exclude result paths.

The repository's numeric ID is checked on every poll. Each source ID binds to
its kind and path/ref/thread specification. Changing that binding requires a
new source ID and baseline review; do not delete the database to force replay.
Source additions and removals are operator decisions.

File snapshots are read at a single commit SHA, without merging or modifying the
checkout. A truncated tree, invalid encoding, unsupported file mode, oversized
document, or failed page makes that source unknown for the poll. The helper
does not turn a partial response into deletions. Documents are limited to
512 KiB each; select small guidance files, not logs or datasets.

Comments are filtered by numeric author ID, ignored operator IDs, bot account
type, and the first-line command prefix. Filtered versions are retained as
`ignored` with a reason. GitHub author metadata does not authenticate the last
editor; approve comment channels with that limitation in mind. Granting a new
author later does not silently replay their historical comments.

## Commands

Run these from the installed skill directory, or use the script's absolute path.
`--state-dir` is required and precedes the subcommand.

```sh
python3 scripts/inbox.py --state-dir /absolute/local/state init \
  --repo OWNER/REPO --host github.com --project-dir /absolute/checkout
python3 scripts/inbox.py --state-dir /absolute/local/state ready
python3 scripts/inbox.py --state-dir /absolute/local/state poll
python3 scripts/inbox.py --state-dir /absolute/local/state events --status pending
python3 scripts/inbox.py --state-dir /absolute/local/state show EVENT_ID
python3 scripts/inbox.py --state-dir /absolute/local/state record EVENT_ID \
  needs_input --note 'The requested dataset is outside the approved scope'
python3 scripts/inbox.py --state-dir /absolute/local/state status
```

`events` returns metadata, not message bodies. Use `show` to obtain original
text, provenance, and the complete receipt history. Accepted work can progress
through `accepted`, `queued`, `running`, `validated`, and `reported`; alternatives
include `needs_input`, `failed`, `ignored`, `superseded`, and `cancelled`.
`validated` and `reported` require an evidence argument. These are records of
agent decisions; they do not independently validate experiments.

Initial eligible messages are `baseline`, not `pending`. The agent reviews
which initial requests to accept. First observations after a failed setup
read are also baseline and require that review. Every later observed content
revision gets an immutable event; unchanged bodies do not produce new events
merely because metadata timestamps changed. File content reversions are new
revisions when observed. Missing objects retain their last snapshot and create
`needs_input`, without cancelling anything.

`poll` returns 0 for a fully successful check, 3 for a partial/failed/deferred
remote check, and 2 for configuration or local-state errors. Read the JSON
receipt and process independently healthy sources; do not treat exit 3 as an
empty inbox. Rate-limit reset headers and retry delays are preserved. Network
and server failures back off. Access denial halts automatic acquisition until
the cause is resolved:

```sh
python3 scripts/inbox.py --state-dir /absolute/local/state retry-source SOURCE_ID
```

This resets a read error, not authentication, native policy, or request status.
It must not be used to continue after an unresolved denial.

## Optional collector process

```sh
python3 -u scripts/inbox.py --state-dir /absolute/local/state watch
```

One collector holds `watch.lock`. Each poll holds `poll.lock`, so a pre-launch
manual poll can run between background polls without duplicate events. Lock
contention makes a one-shot poll report busy; the original watcher waits for a
manual poll to release the lock and continues. Do not launch another watcher.
Watcher sleeps are interruptible and its health records
running/stopped state, PID, start time, and heartbeat.

Keep the process attached to the execution session unless the user requested
persistence beyond it. For a persistent collector, use the existing supervisor
or one user-level service/tmux objective according to host conventions. Verify
its live process, recent successful poll, and an active consumer. Do not enable
system-wide services or a reboot autostart as an incidental setup change.

The collector never sends Coopa messages. A local active agent consumes events
directly. If a project already has an authorized wakeup service, retain its
delivery identifiers and semantics; do not claim a generic exactly-once wakeup.

## GitHub API references

Consult these when changing the adapter:

- [Pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api):
  follow the server's `Link` header through all pages.
- [Issue comments](https://docs.github.com/en/rest/issues/comments):
  issue comments include PR conversation comments.
- [Git trees](https://docs.github.com/en/rest/git/trees):
  recursive trees can be truncated; that is not a complete snapshot.
- [REST best practices](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api):
  honor rate-limit headers and pause rather than retrying continuously.

Private-repository guidance informed this workflow's design; no project-specific
models, cloud accounts, collaborator identities, or experiment permissions are
embedded in the skill.

## Validate helper changes

Run `scripts/test_inbox.py -v` with a compatible Python and `TMPDIR` set to a
task-owned scratch directory. The tests use local fixtures, including a real
collector subprocess with a fake GitHub CLI; no external comments or experiments
are created. Inspect the exit status. A passed helper suite does not replace a
project-specific launcher smoke test.
