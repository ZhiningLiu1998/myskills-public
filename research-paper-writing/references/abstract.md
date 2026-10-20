# Abstract

A reviewer decides from the abstract whether the paper is worth a careful
read. In one paragraph, they should learn the problem, why it is still open,
what the paper does about it, and what evidence supports that.

## Before drafting

Write short answers to these questions:

- What problem does the paper solve, and why do current methods fall short?
- What is the main technical contribution?
- Why does it work: what property of the problem does it exploit?
- What result shows that it works?

If one answer is vague, fix it in the paper's story before polishing
sentences.

## Choose a shape

All three shapes start with the task and end with a short summary of the
evidence. They differ in the middle.

| Shape | Middle of the abstract | Use when |
| --- | --- | --- |
| Challenge -> contribution | The prior methods' limitation and its cause, then the contribution that removes it. | One contribution whose motivation is easy to see. |
| Challenge -> insight -> contribution | The limitation, then the observation that makes it solvable, then the method that uses that observation. | The paper rests on a real insight. This is often the clearest shape. |
| Several contributions | Each contribution in one sentence together with its advantage. | Two or three contributions that matter on their own. |

Examples of each: `references/examples/abstract.md`.

## Sentence-level guidance

- Describe prior work only as far as it leads to the limitation the paper
  addresses.
- Name the contribution with a term readers can understand on first reading.
  Save the steps for the Method section.
- A sentence that states a contribution together with its benefit is often the
  most useful sentence in the abstract.
- Each sentence should carry one message.

## Check

- Can a reader name the task, challenge, contribution, and evidence after one
  read?
- Does every claim match a result reported in the paper?
