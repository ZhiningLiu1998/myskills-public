---
name: readme-craft
description: Write or improve a project's README with natural developer prose, a clear reading path, and real demonstrations of its value. Use for README creation, rewrites, copy reviews, or choosing examples and screenshots for a README.
---

# README craft

Help a developer understand the project, see something worth trying, and get a
first result. Prioritize factual accuracy, reader understanding, the author's
voice, and then decoration.

Keep the requested scope: a paragraph edit stays a paragraph edit, and a review
produces findings unless edits were requested. Follow the README's language and
the user's audience and style choices. Release announcements and social posts
are separate deliverables.

## Start with the project and its evidence

Read the current README, the relevant entry points and package metadata, and
existing examples, documentation, and demo assets. Inspect enough to establish
the main use case and verify what you plan to say; an exhaustive code audit is
usually unnecessary.

Identify the intended reader and one useful scenario they can recognize. Infer
these from the project where possible. Ask when missing context would materially
change the positioning or example.

Choose the demonstration before writing the main pitch:

| What makes the project useful | A suitable demonstration |
| --- | --- |
| A visible interaction or workflow | A real screenshot or short recording showing the action and result |
| A command that saves effort | The command, representative input, and its actual output |
| An approachable API | A small, complete example with an observable result |
| Better speed, size, or resource use | Measurements with the comparison, conditions, and reproduction method |

Reuse useful material. Capture or run a focused demonstration when needed and
within the task's permissions. Choose material suitable for the intended
audience; make illustrative or synthetic data recognizable as such.

Claims about features, availability, performance, and adoption MUST match the
available evidence. Keep planned behavior recognizable as a plan. If a useful
asset is missing, narrow the claim or give a concrete capture request in the
handoff. Do not present an imagined screenshot, result, testimonial, or number
as something observed.

## Arrange the reader's path

For a full README, a useful default is:

1. **Recognize the project.** Say what it does and who has a reason to use it.
2. **See it work.** Put the strongest example near the benefit it demonstrates.
3. **Try it.** Give the shortest supported route to a useful first result.
4. **Decide whether it fits.** Explain relevant conditions, limits, and tradeoffs.
5. **Go deeper.** Link to detailed configuration, reference material, contribution
   guidance, support, and licensing as the project needs.

Adapt this order. A prerequisite that determines whether someone can use the
project belongs before they invest time in setup. Keep existing sections that
already serve readers, and merge or omit sections that would only repeat
information.

Let the opening screen communicate the purpose and distinctive value without a
long preamble. Make each section answer a reader's question. Use tables for
comparisons, lists for parallel choices or steps, and paragraphs for explanation.
Move long reference material behind useful links when it obscures the first use.

Keep badges and decoration when they convey a useful status or help navigation.
Preserve required notices and accurate limitations when shortening the document.

## Write in a recognizable human voice

Use the user's writing sample or the project's established voice when one is
available. Keep technical names and necessary terms precise; explain an unfamiliar
term when the reader needs it to follow the example.

- Name the actor, action, and result. Replace praise such as "powerful" or
  "seamless" with the specific behavior that earns it.
- Lead with the information. Cut generic scene-setting, repeated instructions,
  ceremonial transitions, and summaries that add nothing.
- Keep humor, a pointed observation, or an unusual phrase when it fits the
  author and helps the reader remember the project.
- Choose punctuation, paragraph length, and sentence rhythm for the passage.
  Rigid bans on particular words or punctuation are poor substitutes for editing.
- Keep rationale about the writing process in the handoff, separate from the
  README. The reader needs the project, not the drafting conversation.

Prefer a main claim another developer could repeat accurately after seeing the
example. A memorable claim should remain specific enough to prove.

## Verify and deliver

Check the claims and demonstration against the inspected project. Exercise
changed commands or examples with the project's relevant checks when feasible;
report anything not run. Distinguish a source inspection from an observed run.

Check changed links and asset paths. Inspect the rendered README, especially its
opening, example readability, and heading hierarchy, when a renderer is available.
If only Markdown source was checked, say so.

Deliver the requested review or edited README and any necessary demo assets.
Briefly report verification and concrete remaining gaps. An asset request should
name the scenario, what the reader should see, and how to capture it.

## Sources

These sources informed this independently written synthesis. Ordinary README
work uses the guidance above without loading upstream skills. Revisit sources
when deliberately revising this skill.

- [Evil Martians: good-readme](https://evilmartians.com/agent-skills) and
  [open-source project presentation](https://evilmartians.com/chronicles/how-to-make-your-open-source-popular):
  progressive explanation and demonstrations.
- [blader/humanizer](https://github.com/blader/humanizer/blob/main/SKILL.md):
  concrete language, removal of formulaic prose, and author voice.
- [coreyhaines31/marketingskills: copywriting](https://github.com/coreyhaines31/marketingskills/blob/main/skills/copywriting/SKILL.md):
  audience, supported benefits, and clear next actions.
- [obra/the-elements-of-style](https://github.com/obra/the-elements-of-style/blob/main/skills/writing-clearly-and-concisely/SKILL.md):
  concise, precise sentences.
- [softaworks/agent-toolkit: crafting-effective-readmes](https://github.com/softaworks/agent-toolkit/blob/main/skills/crafting-effective-readmes/README.md):
  project-specific organization and useful onboarding.
