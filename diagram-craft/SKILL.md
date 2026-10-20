---
name: diagram-craft
description: Create or revise editable technical diagrams and README teaser figures from project sources or a provided explanation. Use for architecture, workflows, component relationships, and method overviews. Prefer other tools for data plots, screenshots, and raster illustration.
---

# Diagram Craft

Make a diagram that helps a reader understand a system or mechanism at a glance.
Use SVG as the default editable deliverable, with a rendered preview for checking
the result. Follow the requested format and preserve an existing diagram's native
source when editing it.

## Establish what the figure should explain

Read the provided material and, for a repository diagram, the README and relevant
entry points or modules. Inspect enough to verify the part being drawn; a teaser
does not need an exhaustive dependency graph.

Choose the reader's question and the figure's main takeaway before placing shapes.
Infer the audience, language, destination, and visual style from the request and
existing assets. State consequential assumptions briefly. Ask only when an
unresolved relationship or missing context would change the meaning of the figure.

Treat every component, boundary, and arrow as a claim. Ground them in the source
or the user's description, and distinguish proposed behavior from implemented
behavior. Do not invent benchmark results, integrations, or screenshots to make a
teaser more persuasive.

Keep a revision within the requested scope. Preserve useful layout, wording, and
relationships unless changing them serves the request.

## Choose a composition that carries the explanation

| Reader's question | Useful starting composition |
| --- | --- |
| What does this project let me do? | A representative input, the distinctive mechanism, and the resulting output |
| How do the parts work together? | Components grouped by responsibility, with labeled relationships |
| What happens during one operation? | A directional path with explicit decisions, branches, or feedback |
| What changes between two approaches? | Aligned panels that use the same labels, scale, and comparison conditions |

Adapt the composition to the content. A README teaser should make one useful
mechanism or experience apparent before asking the reader to study internal
details. Use a small concrete example when abstract labels alone would not explain
the result. Prefer another panel or figure when squeezing in detail makes the
opening image hard to read.

Arrange the important relationships before polishing boxes. Separate membership
from flow: an enclosing region groups things, while an arrow describes an action,
dependency, or movement of data. Use one meaning consistently or explain the
difference. Label consequential arrows with what travels or happens.

Reserve space for connectors and their labels. Route around node interiors and
text; make arrowheads meet the intended boundaries. Separate returning paths
from the forward path so their directions remain clear. Remove incidental edges
that obscure the intended explanation.

Use the project's visual language where one exists. Otherwise, choose a restrained
palette, a clear type hierarchy, and enough spacing to distinguish groups.
Color should reinforce labels and relationships. Choose the background for the
destination; a dark theme is a style choice, not a default requirement.

## Build a portable, editable asset

When creating SVG, write native shapes, paths, and text directly so wording and
relationships remain editable.
A generation script is useful for repeated geometry; a single figure does not
need a new diagram framework or a model API.

- Give the root an SVG namespace and a `viewBox` that includes the complete
  drawing. Include a concise `<title>` and `<desc>`.
- Keep labels as text. Wrap deliberately with separate lines or `tspan` elements,
  and size containers around the rendered text rather than character counts.
- Draw group backgrounds behind connectors and node content. Keep strokes,
  arrowheads, and text out of clipping regions and away from the canvas edge.
- For README assets, keep the SVG self-contained. Avoid scripts, remote fonts,
  external stylesheets, and HTML `foreignObject` labels. Use explicit colors and
  a deliberate background so the image survives embedding on another page.
- Use fonts that can render the requested language. Check Chinese and other
  non-Latin labels for missing glyphs; a font installed on the authoring machine
  does not establish that it exists on the reader's machine.

Design for the displayed size. For example, a 24-unit label in a 1600-unit-wide
figure becomes 12 pixels when displayed at 800 pixels. Enlarge or simplify the
content when it needs browser zoom to read at its intended README width.

Use the user's destination or the project's existing asset directory. For a
standalone request without an established destination, `output/diagrams/` is a
reasonable default. Keep generated figures and temporary previews out of the
installed skill directory.

## Render and check the result

Parse the SVG to catch malformed XML, then render it with an available local SVG
renderer or headless browser. Reuse the project's export tools when suitable;
there is no required Bun, Node, or image-generation service dependency.

Inspect the rendered image at its intended display width as well as at full size.
Check that the main takeaway is apparent, labels and arrowheads are legible,
relationships match the evidence, and nothing overlaps or clips. Check the
embedded result when changing a README. A successful export alone does not
establish that the layout works.

Fix observed problems and inspect the affected result again. If visual inspection
is unavailable, report what was checked and what remains unverified.

Export PNG when requested or useful for the destination. Retain the editable
source alongside any export, and render PNG at sufficient resolution for its
displayed size. Inspect the exported file too if a different renderer produced it.

## Deliver

Return the figure and its editable source with their paths. Include a short alt
text or caption when the figure is intended for documentation, and report the
rendering check and any unresolved factual assumptions. Update a README embed
when that is part of the requested work.

## Source

[JimLiu/baoyu-skills: baoyu-diagram](https://github.com/JimLiu/baoyu-skills/tree/main/skills/baoyu-diagram)
informed the SVG workflow. These instructions are independently written.
Consult the upstream source when revising this skill; ordinary use is
self-contained.
