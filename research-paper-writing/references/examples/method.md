# Method Examples

These examples are illustrative and written for this skill. They continue the
hypothetical BoundaryFill method from [abstract.md](abstract.md) and
[introduction.md](introduction.md). Module names, design choices, and settings
are invented for demonstration; bracketed values mark details a real paper
must supply.

Use them with [method.md](../method.md).

## Pre-writing table

Answer three questions for every module before writing paragraphs:

| Module | How does it run? | Why is it needed? | Why does it work? |
| --- | --- | --- | --- |
| Boundary detection | Predicts a boundary map and object masks from the RGB image. | Propagation needs to know where each object starts and ends. | Transparent-object outlines are visible in RGB even when depth is missing. |
| Boundary-guided propagation | Samples valid depth just outside each mask, then diffuses it inward along image edges. | Depth inside the mask is missing or wrong. | Surrounding opaque surfaces keep reliable depth. |
| Confidence-weighted surface prior | Weights each boundary sample by estimated reliability and regularizes the filled surface. | Noisy boundary samples spread errors inward. | Most transparent objects have smooth, closed surfaces. |

## Overview subsection

```latex
\section{Method}
% Setting, in one or two sentences
Given an RGB image and a depth map with missing or corrupted values on
transparent objects, our goal is to recover dense depth on those objects.
% Core contribution
Instead of regressing depth from appearance, we fill each object region from the
reliable depth along its boundary.
% Pointer to the pipeline figure
Figure 2 shows an overview of BoundaryFill.
% Map of subsections
We first detect transparent-object boundaries and masks (Section 3.1). We then
propagate boundary depth into each region (Section 3.2) and refine the result
with a confidence-weighted surface prior (Section 3.3).
```

## Module subsection with the three elements

```latex
\subsection{Boundary-guided propagation}

% Motivation: the problem that requires this module
After detection, each transparent object has a mask, but the depth inside it
is still missing or wrong. Interpolating directly from the nearest valid pixels
would mix in depth from the background seen through the object.

% Module design: data structure
We represent the known depth as a set of boundary samples, each taken from a
valid pixel within [k] pixels outside the object mask.

% Module design: forward process (input -> steps -> output)
Given the mask and the boundary samples, we first initialize every pixel inside
the mask with the depth of its nearest sample. We then run [T] iterations of
edge-aware diffusion, where each pixel updates its depth from its neighbors with
weights predicted from the RGB image. The output is a dense depth map inside
the mask, which Section 3.3 refines.

% Technical advantage
Because each update uses only depth from inside the same mask, background
depth seen through the object cannot leak into the result. The edge-aware
weights let the filled depth follow visible creases and rims rather than
forming a flat patch.
```

## Module design sentence pattern

1. `We represent [quantity] with [structure].`
2. `Given [input], we first [step], then [step], and finally [step].`
3. `This produces [output], which is used by [next module].`

## Motivation sentence patterns

State the specific failure before introducing the module, and keep the
motivation separate from implementation details.

- `A remaining problem is that [failure], because [reason].`
- `However, [previous step] cannot handle [case], since [reason].`
- `Previous methods have difficulty with [case], because [reason].`

## Common issues after drafting

Use this checklist after a full Method draft:

1. **Missing motivation.** A module appears with no stated problem. Add the
   problem first, or remove the module if nothing requires it.
2. **Steps out of order.** The forward process jumps between modules or
   describes outputs before inputs. Rewrite it in execution order.
3. **Undefined or drifting terms.** A quantity is named twice in different ways,
   or used before definition. Fix one name and define it at first use.
4. **Unreproducible design.** Shapes, iteration counts, losses, or coordinate
   conventions are missing. Add them in the subsection or in Implementation
   Details.
5. **Advantage without evidence.** A stated benefit has no experiment or
   ablation behind it. Add the evidence or weaken the claim.
