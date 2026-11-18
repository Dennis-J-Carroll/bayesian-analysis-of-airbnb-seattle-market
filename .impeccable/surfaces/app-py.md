---
version: 1
slug: "app-py"
primary_target: "app.py"
related_targets: ["dashboard/pages"]
---

# Surface brief: dashboard app (Streamlit, all pages)

Scope: the whole Streamlit app (`app.py` + `dashboard/pages/*`). Mode: Operate, portfolio-facing. Audience: recruiters (one-minute skim) and technical DS reviewers (dig into the model). Pages tightened to: Predict, Neighborhoods, How the model works, Diagnostics, Data notes. No emojis.

## Direction contract

THESIS: One guest-count control remaps the price of every Seattle neighborhood at once; the varying-slopes model shown as a live type-specimen grid. Refuses the KPI-tile row over a lone histogram.

OWN-WORLD: Paper #FBFBFA ground, ink #111 text and curves, single vermilion #D6452B accent reserved for the selected neighborhood and the slider; muted #8A8A85 labels; 1px ink rules and hairline cell borders, no shadows, no radius beyond 2px, no glass, no gradients. Archivo for display numerals at enormous scale, JetBrains Mono for labels, readouts and axis ticks. Hierarchy by scale contrast and weight; small caps-style tracked mono labels.

STORY: Visitor sees a real price with its uncertainty, drags guests and watches all 88 neighborhood distributions shift, notices small neighborhoods pulled toward the city line, then opens the model and diagnostics pages to verify it.

FIRST VIEWPORT: Left mono nav rail (210px). Top band: giant predicted median ($164) with its 94% range and neighborhood select, guest slider to the right with tick readout. Below: grid of 88 small posterior curves (11 columns), selected neighborhood in vermilion. Primary action is the slider.

FORM: Live Specimen (fused variable-font-specimen challenger, user's choice over assigned Link Line); seed:2041fbc8df5b66da

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
