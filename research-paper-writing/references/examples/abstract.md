# Abstract Examples

These examples are illustrative and written for this skill. They describe a
hypothetical method, BoundaryFill, for depth completion of transparent objects.
The method, results, and dataset names are invented. Bracketed text such as
`[metric]` marks where a real paper reports its own evidence.

Running scenario: commodity RGB-D cameras often return missing or wrong depth
on glass and clear plastic. BoundaryFill infers that depth from the reliable
depth of surrounding opaque surfaces, guided by object boundaries detected in
the RGB image.

Use the sentence roles, not the wording.

## Version 1: Challenge -> Contribution

```latex
% Task
We address depth completion for transparent objects from a single RGB-D frame.
% Technical challenge of previous methods (limitation + technical reason)
Existing learning-based methods regress depth for each transparent pixel
directly from image appearance. Because the appearance of a transparent object
mostly reflects its background, these methods generalize poorly to object shapes
not seen during training.
% Contribution, named rather than explained step by step
We propose BoundaryFill, which completes the missing depth by propagating valid
depth from the surrounding surfaces across each detected object region.
% Benefit of the contribution
Since this propagation depends on object boundaries rather than on the
transparent surface's appearance, it does not need to have seen the object's
shape during training.
% Experiment summary
Experiments on [benchmarks] show that BoundaryFill improves [metric] over
[baselines], with the largest gain on [unseen-shape split].
```

## Version 2: Challenge -> Insight -> Contribution

```latex
% Task
We address depth completion for transparent objects from a single RGB-D frame.
% Technical challenge of previous methods
Existing methods regress depth directly from the appearance of transparent
pixels, which mostly shows the background, so they fail on unseen shapes.
% Insight, in one sentence
Our key observation is that even when depth on the object is missing, its
boundary is visible in the RGB image and the opaque surfaces around it still
have reliable depth.
% Contribution that implements the insight
Building on this observation, we propose BoundaryFill, a boundary-guided
propagation module that fills each object region from the depth along its
boundary.
% Benefit of the technical novelty
This turns an appearance regression problem into a geometric interpolation
problem, which depends less on the training distribution of object shapes.
% Experiment summary
Experiments on [benchmarks] show [main result].
```

## Version 3: Multiple contributions

```latex
% Task
We address depth completion for transparent objects from a single RGB-D frame.
% Optional contrast with prior methods
Unlike prior methods that regress depth from transparent-pixel appearance, we
infer it from reliable surrounding geometry.
% Contribution 1 + its technical advantage
First, a boundary-guided propagation module fills each object region from the
depth along its boundary, which removes the dependence on seen object shapes.
% Contribution 2 + its technical advantage
Second, a confidence-weighted surface prior favors smooth, closed surfaces
inside each region, which suppresses errors where the boundary depth is itself
noisy.
% Experiment summary
Experiments on [benchmarks] show [main result], and ablations show that each
component contributes to [metric].
```

## Pattern to avoid

```latex
We propose a novel, powerful framework that achieves state-of-the-art results
by exploiting rich boundary cues in an effective way.
```

The sentence names no task, no challenge, and no mechanism, and its claims are
not tied to evidence. Each version above replaces it with a stated challenge,
a named mechanism, and a pointer to the evidence.
