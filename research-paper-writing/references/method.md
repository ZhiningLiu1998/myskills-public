# Method

The Method section should let a reader understand why each part of the method
exists and reproduce it. Draft it from the pipeline figure outward.

## Before drafting

List the modules of the method. For each one, answer three questions: how it
runs, why it is needed, and why it works. A table is usually enough; see
"Pre-writing table" in `references/examples/method.md`.

Then sketch the pipeline figure and use it to decide the subsections, usually
one per module.

## Structure

1. **Overview.** State the setting (input and output), the core idea, a pointer
   to the pipeline figure, and what each subsection covers.
2. **One subsection per module.** Cover three elements:
   - **Motivation:** the problem that requires this module. A useful form is
     "because X fails or is missing, we need Y."
   - **Design:** the representation, network, or data structure, then the
     forward process in execution order, from input through each step to
     output.
   - **Advantage:** why this design is better than the obvious alternatives,
     tied to a measurable effect where possible.
3. **Implementation details.** Hyperparameters, layer sizes, normalization,
   coordinate conventions, and training settings, at the end of the section or
   in their own subsection.

It often helps to write the design first, since it is the most concrete, and
add motivation and advantage afterward.

Examples of the overview, a full module subsection, and sentence patterns:
`references/examples/method.md`.

## Clarity check

- **Logic:** summarize the section in a few sentences. Does the order make
  sense?
- **Paragraphs:** does each first sentence say what the paragraph is about, and
  does each paragraph carry one message?
- **Sentences:** is it clear why each sentence is there? Are key terms used
  consistently?

"Common issues after drafting" in `references/examples/method.md` lists
frequent problems to look for.
