# Document patterns

Use the pattern that matches the reader's main need. These are starting points;
follow an existing template or house style when one is given.

## Proposal or decision

The reader decides whether to approve or choose something.

- **Problem:** what is wrong or missing now, and who it affects, with evidence.
- **Proposal:** the change, its scope, and what stays the same.
- **Alternatives:** the live options compared on the same constraints. When a
  decision has been made, explain why the chosen option won; otherwise present
  the tradeoffs and a recommendation if there is one. For performance
  comparisons, match measurement conditions, including warm or cold query
  state; record gaps in evaluation as open questions.
- **Consequences:** what becomes easier or harder, cost, migration, and open
  questions.
- **Status:** proposed, accepted, or replaced, when the document will outlive
  the decision.

Keep the decision record once the work ships, and describe current behavior in
separate, maintained documentation rather than in the proposal.

## Design or architecture explanation

The reader wants to understand how the system works and why.

- Start with what the system does for its users and the boundary of what is
  covered.
- Walk through one representative request or data flow: who starts it, what
  each component does, and what comes out.
- Explain each significant choice next to the constraint behind it, such as
  latency, consistency, cost, or team ownership.
- Note limits that affect how others build on it.

Add a diagram when a picture makes a relationship or flow easier to follow
than prose; keep the prose able to stand without it.

## How-to guide

The reader is in the middle of work and needs to reach a specific result.

- Title it by the goal ("Rotate the signing key"), not by the tool.
- State prerequisites and the starting state.
- Number the steps. Each step is one action with its expected result, so the
  reader can tell it worked.
- Put explanation in a link or a short note, not between steps.
- End with how to confirm the result and what to do if a common step fails.

## Reference

The reader looks up a fact: an option, field, command, limit, or error.

- Organize it like the thing it describes, such as one entry per flag or
  endpoint, in a consistent order.
- Give the fields that apply, such as type, default, and allowed values, and a
  minimal example where usage is not obvious.
- Keep it current and complete for the requested or supported surface; leave
  tutorials and rationale to other pages.

## Experiment or results report

The reader judges what was learned and whether to act on it.

- Question or hypothesis, and why it matters.
- Setup: data, versions, configuration, and comparison baseline, enough to
  reproduce.
- Results with the actual numbers, and links to logs or runs.
- Interpretation, kept separate from the results, including what the results
  do not show. A claim of improvement needs the candidate and baseline measured
  under matching conditions; repeating only the candidate run checks its
  variance, not its gain over the baseline.
- Next step or decision. When proposing a follow-up run, state which pair of
  measurements it adds and what that comparison would establish.

Report runs that failed or are still running as such.

## Progress update

The reader, often a manager or collaborator, needs current state and what
they must do.

- What changed since the last update, as outcomes with links.
- What is blocked, on whom, and what is needed.
- What comes next, with timing when it is known.

Keep completed work separate from expected results.

## Before and after

An original example of a design-doc paragraph. The system is fictional.

Source facts gathered while inspecting the project:

- Rebuilding a search result takes about 2 s, per the service's latency
  dashboard.
- `LruStore` keeps results in each API server's memory with a 60 s TTL;
  `RemoteTier` reads and writes a shared Redis cache.
- `CacheManager.get` checks `LruStore`, then `RemoteTier`, and rebuilds only
  when both miss.
- Request logs show most repeat queries return to the same server within a
  minute.
- `WarmupScheduler` preloads popular queries at startup.

Before:

> The CacheManager leverages a robust multi-tier architecture to seamlessly
> optimize performance. It utilizes `LruStore`, `RemoteTier`, and
> `WarmupScheduler` to ensure efficient and scalable access to data.

After:

> Rebuilding a search result takes about 2 s, so each API server keeps recent
> results in memory and falls back to a shared Redis cache. A request checks
> local memory first, then Redis, and rebuilds only when both miss. We chose a
> local tier because request logs show most repeat queries return to the same
> server within a minute; the cost is that a result updated in Redis can stay
> stale locally for up to the 60 s TTL.

Every detail in the revision comes from the source facts. It names the
reader-visible problem, follows one request through the system, ties the
design to its evidence, and states the tradeoff a reader would need before
relying on the cache. Startup warmup is left out because it does not affect
this paragraph's point.
