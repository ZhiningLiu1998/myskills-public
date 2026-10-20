---
name: doc-writing
description: Draft, revise, or review technical documents such as proposals, design and architecture explanations, how-to and reference guides, experiment reports, and project updates. Use when the reader needs to decide, understand, or do something from the document. Prefer readme-craft for READMEs and research-paper-writing for academic papers when available.
---

# Doc writing

Write documents that let a specific reader decide, understand, or act without
asking the author what was meant. Write in the user's language. Keep code
identifiers, product names, and established technical terms in their original
form.

## When to use

Use for technical proposals, design and architecture explanations, engineering
how-to and reference material, experiment and results write-ups, and progress
updates, including focused edits to one section of an existing document. For a
README or an academic paper, use `readme-craft` or `research-paper-writing`
when they are installed. This skill does not render `.docx` files, write
marketing copy, or change code.

## Inputs

- The document or notes to work from, and any template or section boundary.
- The sources behind the content: code, data, results, discussions, linked docs.
- The audience and purpose when stated. Otherwise infer them from the document,
  where it will be published, and the surrounding project.

## Steps

1. **Establish context.** Read the supplied document and the sources it
   describes, enough to verify what it will say. Identify the reader, what they
   already know, and what they should be able to do afterward. Ask only about
   gaps that would change the content or its correctness, and keep working on
   sections that are already grounded. Done when you can state reader, purpose,
   and scope in one sentence each.
2. **Choose the shape.** Decide what the reader mainly needs: steps to complete
   a task, an explanation of how and why something works, facts to look up, or
   a decision to make. One document can combine these in separate sections. For
   type-specific structure, read `references/document-patterns.md`. For a
   substantial new or restructured document, write a short outline first and
   continue without waiting for approval unless the user asked to review it;
   short edits and brief updates go straight to step 3. Done when each planned
   section answers one reader question.
3. **Draft or edit.** Put the problem, decision, or outcome early. Explain
   mechanisms through concrete inputs, actors, behavior, and outputs; mention
   implementation symbols where the reader needs them. Tie each design choice
   to the constraint or tradeoff that motivated it. Place evidence (a result,
   link, measurement, or code path) next to the claim it supports. Distinguish
   what exists, what is planned, and what is a hypothesis wherever that changes
   how the reader should interpret a statement. Something not yet evaluated is
   unknown, not shown false. For a comparison claim or a proposed check, name
   the baseline, metric, and conditions that affect the conclusion, and pair
   only measurements taken under matching conditions. Use paragraphs for
   reasoning, lists for parallel items or steps, and tables for comparisons.
   Link to existing documentation instead of restating it. State limitations that
   affect a decision or use. Write explanation as connected paragraphs, with
   familiar words and precise verbs, and make a concrete point early in each.
   Drop repeated caveats, formulaic praise or contrasts, and closing lines that
   only restate; keep the rationale and real limitations. Done when the
   requested sections are written.
4. **Preserve what the user set.** Keep the requested scope, facts, figures,
   links, examples, prompts, templates, and the author's useful voice. Edit only
   the requested sections, and change wording surgically rather than rewriting
   text that already works. Done when unrequested parts are unchanged.
5. **Read as the reader.** Reread the result without your working context, or
   ask a fresh agent when one is available and the document is substantial.
   Check that the main point appears early, terms unfamiliar to this reader are
   explained before use, and the conclusions and factual claims that affect
   interpretation are supported. Ordinary connecting prose needs no citation.
   Done when found problems are fixed.

## Outputs

The edited document or new draft in the requested location and format. For a
review-only request, return specific findings with suggested wording, and do
not edit the document. Report only material open questions or limitations.

## Verification

Check the actual artifact: numbers, names, and commands against their sources;
changed links and file references; and the rendered result when a renderer or
the destination's preview is available. Say which checks were not possible.

## Failure handling

If a source cannot be read or a fact cannot be verified, write the supported
parts, mark the gap in place, and report it. Do not fill gaps with invented
results or benchmarks.

## Permissions

Edit only the documents the user asked to change. Publish, share, or send the
document only within the user's existing authorization, using the tools they
selected.

## Resources

- `references/document-patterns.md`: read when choosing a structure for a
  proposal, design explanation, how-to, reference, experiment report, or
  progress update, or when you need the before/after example.
- `references/sources.md`: read when revising this skill; ordinary use does
  not need it.
