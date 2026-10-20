# Experiments

The Experiments section provides the evidence for the paper's claims. Plan it
from the claims, not from the results that happen to exist.

## Plan from claims and modules

- For each contribution claimed in the Abstract and Introduction, name the
  experiment that tests it.
- For each key module or parameter in the pipeline figure, plan an ablation
  that removes, replaces, or varies it.

Most papers then answer three questions:

1. **Does it beat strong baselines?** Compare with recent and strong methods
   using the same data splits, preprocessing, and standard metrics.
2. **Which parts cause the gain?** Report ablations against the full model, and
   test interactions when modules depend on each other.
3. **Where does it hold, and where does it fail?** Evaluate harder or
   out-of-distribution settings and show failure cases.

A typical order is setup, main comparisons, ablations, then analysis or harder
settings. Pair important ablations with qualitative results when they make the
difference visible.

## Tables and figures

- Put table captions above the table. Keep captions to setting, protocol, and
  notation.
- Use `booktabs` rules (`\toprule`, `\midrule`, `\bottomrule`) instead of
  vertical lines and dense `\hline`s.
- Mark metric direction (`PSNR ↑`, `LPIPS ↓`) and units in headers.
- Use the same precision within a column and highlight only the few numbers
  that matter.
- Give each table one message. Group settings with `\multicolumn` and
  `\cmidrule`.

## Check

- Are the baselines recent and relevant, and the comparisons fair?
- Does each key design claim have an ablation?
- Do the Abstract and Introduction claim only what the numbers show?
- Are the limits of the evaluation stated?
