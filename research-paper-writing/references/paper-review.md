# Paper Review

Before submission, read the draft as a skeptical reviewer would and fix the
problems most likely to cause rejection. Focus on the paper's actual claims and
the venue's expectations.

## Claims and evidence

Each major claim, especially in the Abstract and Introduction, should be
technically correct and supported by a result in the paper. When a claim lacks
support, add the evidence or narrow the claim.

## Common reasons for rejection

| Area | Typical problem |
| --- | --- |
| Contribution | The failure case is minor, or the technique and its gain are already well known. |
| Clarity | Missing details make the method hard to reproduce, or a module has no stated reason. |
| Results | Gains over prior work are marginal, or absolute performance is still weak. |
| Evaluation | Missing ablations, baselines, or metrics, or datasets too easy to be convincing. |
| Method design | An unrealistic setting, a technical flaw, heavy per-case tuning, or new limitations that outweigh the benefit. |

## Self-review questions

Answer these against the draft and note where the answer comes from:

1. **Contribution:** What does a reader learn that they did not know? Is the
   problem worth solving, and is the idea more than standard practice?
2. **Clarity:** Could an expert reimplement the method? Does each module have a
   stated motivation? Are terms consistent?
3. **Results:** Are the gains meaningful and consistent across datasets and
   metrics? Are failure cases shown?
4. **Evaluation:** Are the strongest baselines included under fair settings,
   with ablations for the key design choices?
5. **Method design:** Is the setting realistic? Do the benefits justify the
   added complexity?

Mark each finding as fixed, needing revision, or needing a new experiment.
Address the issues a reviewer is most likely to raise first; not every question
needs a change.
