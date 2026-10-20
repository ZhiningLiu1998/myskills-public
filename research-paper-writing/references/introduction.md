# Introduction

The introduction tells the reader which problem matters, why existing methods
do not solve it, what this paper does, and why that works. A reader who stops
after it should be able to describe the paper accurately.

## Plan backward, write forward

Plan from the contribution back to the opening:

1. Which technical challenge does the paper solve, and why is it still open?
2. What does the paper contribute: a task, a metric, a technique, or a finding?
3. Why does the contribution address the challenge, and what insight does it
   offer?
4. Which prior methods lead the reader most directly to that challenge?

Then write in reading order: task and motivation, prior methods leading to the
challenge, the proposed approach and why it works, evidence, and a short list
of contributions.

## Opening: task and motivation

Pick the opening by how familiar the task is:

- **Less familiar task:** define it (output from input), then give a few
  applications.
- **Familiar task:** start with why it matters.
- **New setting of a known task:** start from the general task, then narrow to
  this paper's input, output, and assumptions.
- **Challenge in the first paragraph:** when readers know the task, state how
  current methods work and where they fail right away. This works only when the
  failure is easy to explain.

## Prior methods and the challenge

This part makes the reader want the solution. Every limitation should include
its technical cause, and the last one should be the challenge the paper solves.

- **Existing task:** move from the general difficulty, through earlier and
  recent methods, to the remaining limitation.
- **Insight with older roots:** if classical work used a similar idea, show why
  it was insufficient and what has changed.
- **New task:** with no direct prior methods, state the goal and list the
  separate reasons it is hard.

Avoid describing a naive solution and then presenting the method as a fix to
it. That framing makes the contribution look obvious, even when it is not.

## The proposed approach

State the key idea in one sentence, point to a teaser figure if there is one,
explain how it works concretely, and then state its advantages over prior
methods. For a second contribution, introduce the problem the first one leaves
and present the second as the response. When the idea starts from an
observation, state the observation plainly before the mechanism.

Describe the actual mechanism. New terms with no explanation of what the method
computes look like an attempt to make a simple idea seem novel.

Examples of each opening, challenge, and approach pattern:
`references/examples/introduction.md`.

## Check

- Does each paragraph's first sentence state its point?
- Are the challenge, its cause, and the paper's mechanism all explicit?
- Is each claim backed by an experiment in the paper?
