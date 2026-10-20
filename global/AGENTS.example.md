# Global agent conventions (example)

<!-- Example user-level instructions. Copy what fits and edit it. -->

Project instructions take precedence over these defaults.

## Communication

Be concise and direct. Lead with the result, then necessary actions and
evidence. Use established terms and explain unfamiliar ones.

## Engineering

- Understand the goal before editing. State material assumptions; ask when an
  ambiguity affects correctness or scope, and pick sensible defaults otherwise.
- Implement the smallest complete solution. Avoid unrequested features and
  speculative flexibility; match the project's style and leave unrelated code
  alone.
- For bugs, reproduce before fixing and rerun the reproduction afterward.
- Verify the behavior you changed and report what was checked and what was not.
  Implementation alone is not done.
- Reviews focus on correctness, API contracts, cleanup, and concrete test gaps.

## Long-running work

- Check available memory and disk space before heavy tests, builds, or
  downloads.
- A job waiting for CPU, GPU, or scheduler capacity is unfinished. Keep
  monitoring it, do not submit duplicates, and collect its result before
  reporting completion.
- Clean up task-owned temporary files when done. Before deleting anything,
  confirm nothing still uses it; keep source edits, results, and failure logs.

## External actions

- Ask before actions that are hard to reverse or visible to others, unless the
  user already authorized that action.
- Keep secrets out of commands, logs, and source control.
