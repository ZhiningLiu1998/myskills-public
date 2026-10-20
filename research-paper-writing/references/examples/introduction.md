# Introduction Examples

These examples are illustrative and written for this skill. They use the same
hypothetical method as [abstract.md](abstract.md): BoundaryFill, which completes
missing depth on transparent objects by propagating reliable depth from the
surrounding opaque surfaces, guided by object boundaries in the RGB image. The
method, prior-method descriptions, and results are invented for demonstration.
In a real paper, every prior-method statement needs a citation and every
benefit claim needs evidence.

Sections A, B, and C follow the opening, challenge, and approach parts of
[introduction.md](../introduction.md), in the same order.

## A. Task and application

### Version 1: Task first, then applications

```latex
% Task: what output from what input
Transparent-object depth completion aims to recover dense, accurate depth on
glass and clear plastic from a single RGB-D frame.
% Applications
It is needed by robotic grasping in kitchens and laboratories, by augmented
reality that places virtual content on tabletops, and by inventory systems that
scan packaged goods.
```

### Version 2: Applications first, for a familiar task

```latex
Depth completion supports applications such as robotic grasping, augmented
reality, and 3D scanning, all of which require accurate depth on every surface
in the scene.
```

### Version 3: General task first, then the specific setting

```latex
% General task and its value
Depth sensing is a basic input for robotic manipulation and augmented reality.
% Narrow to this paper's setting, with exact input and output
This paper focuses on a setting where commodity sensors routinely fail:
recovering depth on transparent objects from a single RGB-D frame, without
object models or multiple views.
```

### Version 4: Open with the challenge

```latex
% Importance, how prior methods work, and where they fail, in one paragraph
Robots that grasp glassware need accurate depth on transparent surfaces, where
RGB-D sensors return missing or wrong values. Given the RGB image and the
corrupted depth, previous methods typically train a network to predict the
transparent region's depth from its appearance. Although this works on objects
similar to the training set, it fails on new shapes because a transparent
surface's appearance mostly shows its background.
```

## B. Technical challenge of previous methods

### Version 1: Existing task, chain of prior methods

```latex
% General challenge
This problem is challenging because sensors provide no reliable measurement on
the transparent surface itself.
% Traditional methods + limitation
Traditional depth inpainting fills holes by smoothly interpolating the
surrounding depth. However, it treats transparent objects like any missing
region and blurs across object boundaries.
% Recent methods (1) + limitation with technical reason
Recently, learning-based methods regress the missing depth from RGB appearance.
However, they generalize poorly to unseen shapes, because appearance inside a
transparent object reflects the background rather than the object's geometry.
% Final limitation = the challenge this paper solves
The remaining challenge is to infer transparent geometry from cues that remain
reliable across object shapes.
```

### Version 2: Existing task, insight with roots in traditional methods

```latex
% Mainstream methods + limitation
Learning-based methods regress transparent depth from appearance, which fails
on unseen shapes.
% Traditional line that already contains a similar insight
A long-standing alternative is to infer missing depth from the geometry around
the hole, as in classical boundary-constrained surface interpolation.
% Why the traditional line was still insufficient
However, these methods assume the hole boundary is known and the surface is
simple, neither of which holds for cluttered scenes with curved glassware.
% Bridge to this paper
We revisit this geometric view and make it practical by learning where object
boundaries are and how surfaces continue between them.
```

### Version 3: Novel task, no direct prior methods

```latex
In this work, our goal is to recover both the outer surface and the wall
thickness of transparent containers from a single RGB-D frame. This problem is
challenging for three reasons.
First, the sensor gives no direct measurement of either surface.
Second, the inner and outer walls produce overlapping boundaries in the image,
so their correspondence is ambiguous.
Finally, no existing dataset provides ground-truth wall thickness for training
or evaluation.
```

## C. The proposed pipeline

### Version 1: One contribution with several advantages

```latex
In this paper, we propose BoundaryFill, a depth completion method for
transparent objects. The basic idea is illustrated in Figure 1.
% Key novelty in one sentence
Instead of predicting each transparent pixel's depth from its appearance,
BoundaryFill fills each object region from the reliable depth along its
boundary.
% Mechanism
Specifically, we first detect transparent-object boundaries in the RGB image,
then sample valid depth just outside each boundary, and finally propagate it
inward with a learned, edge-aware diffusion.
% Advantage 1
In contrast to previous methods, this propagation depends on boundary geometry
rather than surface appearance, so it does not require the object's shape to
appear in training.
% Advantage 2
Another advantage is that the module works with the output of any boundary
detector, so it can benefit from improvements in boundary detection.
```

### Version 2: Two contributions

```latex
In this paper, we propose BoundaryFill. Our innovation is in completing
transparent depth from the surrounding geometry rather than from appearance.
The basic idea is illustrated in Figure 1.
% Contribution 1 and its advantage
Specifically, a boundary-guided propagation module fills each object region from
the depth along its boundary, which removes the dependence on seen shapes.
% Remaining challenge
However, depth near the boundary is itself noisy, and propagation spreads that
noise inward.
% Contribution 2 as the response
To address this, we add a confidence-weighted surface prior that down-weights
unreliable boundary samples and favors smooth, closed surfaces.
```

### Version 3: New module on an existing pipeline

```latex
% Prior pipeline
Following previous methods, we use an encoder-decoder network that takes the
RGB image and corrupted depth as input.
% New module
Our innovation is a propagation module inserted before the decoder.
% Observation that motivates it
We observe that the depth just outside a transparent object remains accurate
even when the depth on the object is missing.
% Mechanism and comparison
Considering this, the module propagates that boundary depth inward along
image edges. In contrast to generic attention layers, which can draw depth from
anywhere in the image, it restricts propagation to each object's region.
```

### Version 4: Contribution driven by one observation

```latex
% Key innovation first
Our innovation is to treat transparent depth completion as filling a region
from its boundary.
% Observation as motivation, easy to state aloud
We observe that a person can estimate the shape of a glass from its outline and
the table it stands on, without seeing through it.
% Implementation
Considering this, we detect object boundaries and propagate the surrounding
depth inward with a learned diffusion.
% Advantage and evidence
This reduces dependence on training shapes and improves [metric] on
[unseen-shape split].
```

### Not recommended: Abstract insight without the method

```latex
We introduce the concept of geometric context transfer, which rethinks
transparency through the lens of structural reasoning. Guided by this
principle, our framework unlocks a new paradigm for depth completion.
```

This paragraph introduces new terms without saying what the method computes.
A reviewer cannot tell whether the idea is new or how it works. Prefer the
concrete mechanism in Version 1.
