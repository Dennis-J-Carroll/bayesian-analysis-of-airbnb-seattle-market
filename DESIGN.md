---
name: Seattle Airbnb, Bayesian price model
description: A live type-specimen of 88 neighborhood price posteriors; paper, ink, one vermilion selection.
colors:
  paper: "#FBFBFA"
  paper-secondary: "#F0F0EE"
  ink: "#111111"
  vermilion: "#D6452B"
  muted: "#6E6E69"
  rule: "#D8D8D6"
  dark-ground: "#111111"
  dark-ink: "#ECEBE6"
  dark-muted: "#9A9CA0"
  dark-rule: "#2A2B2E"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(64px, 13vw, 150px)"
    fontWeight: 800
    lineHeight: 0.84
    letterSpacing: "-0.04em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(34px, 5vw, 56px)"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontWeight: 800
    letterSpacing: "-0.02em"
  numeral:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  body:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontWeight: 400
  caption:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0"
  readout:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "16px"
    fontWeight: 400
    fontFeature: "tnum"
  label:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.06em"
  data:
    fontFamily: "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.18
    fontFeature: "tnum"
rounded:
  hairline: "2px"
  round: "50%"
components:
  select:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.hairline}"
    padding: "8px 34px 8px 10px"
  button-default:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.hairline}"
  button-primary:
    backgroundColor: "{colors.vermilion}"
    rounded: "{rounded.hairline}"
  nav-item:
    textColor: "{colors.ink}"
    typography: "{typography.label}"
  nav-item-active:
    backgroundColor: "{colors.rule}"
    textColor: "{colors.ink}"
    rounded: "{rounded.hairline}"
  slider-thumb:
    backgroundColor: "{colors.vermilion}"
    rounded: "{rounded.round}"
    size: "18px"
  specimen-cell:
    textColor: "{colors.muted}"
    typography: "{typography.data}"
    height: "44px"
  readout:
    textColor: "{colors.ink}"
    typography: "{typography.headline}"
    padding: "8px 0 4px"
  readout-line:
    textColor: "{colors.muted}"
    typography: "{typography.caption}"
    padding: "10px 0 0"
---

# Design System: Seattle Airbnb, Bayesian price model

## Overview

**Creative North Star: "The Live Specimen"**

The app is set like a type-specimen sheet whose specimens are posterior distributions. One enormous Archivo numeral states a price; beneath it, every neighborhood's price curve sits in a dense grid of hairline cells, all on one log-price axis, so the eye compares 88 shapes the way it compares weights of a typeface. A single guest-count control remaps every specimen at once. The page is paper and ink; colour appears only where the visitor has made a choice.

Density is high and quiet. Hierarchy comes from scale contrast (a 150px numeral against 11px mono labels) and weight (Archivo 800 against JetBrains Mono 400), never from boxes, shadows or tinted panels. Uncertainty is drawn, not decorated: bands are a faint ink wash under a 1px curve, sparse evidence is a thinner dashed stroke, and the raw data is a hollow dot. Light and dark are two inkings of the same sheet, not two designs.

**Key Characteristics:**
- Paper ground, ink type and curves, one vermilion accent for the selection, the slider thumb and the primary action.
- Archivo 800 for numerals and headings; JetBrains Mono for everything that is read as data or label.
- 1px rules and hairline cell borders do all the structural work; no shadows, blur or gradients.
- Every interval shown is the equal-tailed 94% interval (3rd to 97th percentile).
- Mark grammar is fixed across pages: band = 94% range, dashed = under 10 listings, hollow dot = raw median, muted vertical = city typical.

## Colors

A near-achromatic paper-and-ink palette with a single warm vermilion that only ever marks the visitor's current choice.

### Primary
- **Survey Vermilion** (vermilion): the selected neighborhood's curve (1.5px stroke, 16% fill), the slider thumb, the native slider's filled track, and the primary button. It never marks a category, a status, a heading or a link.

### Neutral
- **Specimen Paper** (paper): page, sidebar, chart plot and paper grounds in light mode; also the ground of every input, select, popover and button so native widgets never show Streamlit's own fills.
- **Paper Shade** (paper-secondary): set in the Streamlit config as the secondary background for native widget chrome in light mode. Not used by custom components.
- **Press Ink** (ink): all type, curves, axis lines and ticks, the sidebar's right rule, the ink rule under the specimen band and above every readout, select borders, focus outlines, selection highlight.
- **Margin Grey** (muted): labels, captions, cell names, tick numbers, the city-typical line, extrapolated curves and track. At 11px on paper it holds AA.
- **Hairline** (rule): cell top borders, table row rules, plot gridlines, expander and widget borders, the active nav pill and popover hover.
- **Night Ground / Night Ink / Night Grey / Night Hairline** (dark-ground, dark-ink, dark-muted, dark-rule): the same roles in dark mode. Ink is warm off-white rather than pure white; vermilion is unchanged across themes.

### Named Rules
**The One Selection Rule.** Vermilion marks what the visitor chose or is manipulating: the selected neighborhood, the slider thumb and fill, the primary action. Nothing else. The active nav item is ink on a hairline pill, and the theme toggle runs ink-on-ground, so neither borrows the accent.

**The Same Sheet Rule.** Dark mode swaps the four neutral tokens and nothing else. Every component reads its colours from the active theme's tokens; no component hard-codes a light value.

## Typography

**Display Font:** Archivo 800 (with Helvetica Neue, Arial, sans-serif); 400 is loaded for select values.
**Body Font:** JetBrains Mono 400 (with ui-monospace, SFMono-Regular, Menlo, monospace)
**Label/Mono Font:** JetBrains Mono 400 and 600, the same family as body.

**Character:** A tight, heavy grotesque for numbers that must be seen from across the room, paired with a monospace that makes every figure, label and caption read as an instrument readout.

### Hierarchy
- **Display** (Archivo 800, 64 to 150px fluid, line-height 0.84, tracking -0.04em, tabular figures): the predicted median price on Predict. One per page at most.
- **Headline** (Archivo 800, 34 to 56px fluid, line-height 1.05, tracking -0.02em, tabular): readout values on Model, Diagnostics and Data notes.
- **Title** (Archivo, tracking -0.02em; h1 at 800): page titles and section subheaders, at Streamlit's native sizes.
- **Numeral** (Archivo 800, 30px, line-height 1): the live guest count beside each slider.
- **Readout** (JetBrains Mono 16px, tabular): the two interval lines in the specimen band.
- **Body / Caption** (JetBrains Mono 400; captions 13px, line-height 1.5): prose capped at 72ch, captions in muted at 80ch, case preserved because they carry notation.
- **Label** (JetBrains Mono 400, 11px, tracking 0.06em, uppercase, muted): field labels, readout labels, table headers, nav entries (nav at 12px, ink), legend entries.
- **Data** (JetBrains Mono 11px, tabular): cell names, cell prices and counts, slider ticks, chart tick labels and axis titles.

### Named Rules
**The 11px Floor Rule.** No functional text goes below 11px: cell names, ticks, legend, axis ticks and labels all sit at exactly 11px. When space runs short the specimen grid drops columns and long names truncate with an ellipsis; the type does not shrink.

**The Tabular Figures Rule.** Every number that can change (prices, guest counts, percentages, n) uses tabular figures so a live remap never makes columns jitter.

**The Tracked-Labels-Only Rule.** Uppercase with 0.06em tracking is for short labels only. Captions and prose keep their case.

## Layout

A wide Streamlit page with a left sidebar (ink right rule) holding the mono nav, the "SEATTLE / BAYES" wordmark, a one-line caption, the Dark toggle and the source link. The main column's top padding is trimmed to 2rem (4rem at 640px and below to clear the fixed header).

The Predict page is one fixed-height specimen frame (1390px). Its top band is a three-column grid (auto, minmax(220px, 1fr), minmax(300px, 400px); 40px column gap, 20px row gap) closed by a 1px ink rule. Below it, the board's grid uses `repeat(auto-fill, minmax(124px, 1fr))` with 3px by 10px gaps, which yields 7 columns at a 1440px viewport. At 1080px and below the controls drop to a full-width row; at 640px and below everything stacks, cells shrink to a 100px minimum, percentage deltas are hidden, and a "Scroll for all 88 neighborhoods" hint appears with a visible scrollbar.

Other pages are a single prose column: title, optional controls in a 3:2 column split, readout row or readout line, then a chart, then a caption. Readout rows auto-fit at a 150px minimum with a 24px gap. Spacing values are local to each component; there is no shared spacing scale.

## Elevation & Depth

Fully flat. There are no shadows anywhere; Streamlit's widget, expander and slider shadows are explicitly removed. Depth is conveyed only by line weight (hairline rule vs 1px ink rule vs 1.5px selected curve) and by translucent ink washes inside charts (8 to 18% alpha bands, 16% vermilion for the selection).

### Named Rules
**The Ruled Sheet Rule.** Separation is a line, never a lifted surface: 1px ink to close a section or head a readout, 1px hairline between peers. No cards, no tinted panels, no blur, no gradients.

## Shapes

Rectangular with a 2px maximum corner (hairline) on every box: selects, buttons, inputs, expanders, the upload dropzone, the active nav pill, scrollbar thumbs. Round forms are reserved for handles and point marks: the 18px slider thumb, the Dark toggle, the 6px hollow raw-median dot and chart point markers. Specimen cells have no corners at all; each is defined only by its top border.

## Components

### Buttons
- **Shape:** hairline corners (2px), 1px hairline border, no shadow.
- **Default:** paper ground, ink text.
- **Primary:** vermilion ground and border. Styled in the theme but not instanced by any page.
- **Upload dropzone:** paper ground, 1px dashed muted border, its button with a 1px ink border.

### Inputs / Fields
- **Select (specimen):** paper ground, 1px ink border, 2px corners, 13px mono, an inline SVG chevron in ink; focus is a 1px ink outline offset 2px.
- **Select (native):** paper ground, 1px hairline border, value set in Archivo; popover list on paper with hairline hover and selected rows.
- **Slider (specimen):** 2px track, ink across the observed guest range and muted beyond it; 18px vermilion thumb; mono 11px ticks with the current value in ink 600. Focus is a 1px ink outline offset 3px on the thumb.
- **Slider (native, Neighborhoods):** vermilion thumb and fill from the Streamlit primary colour; its own value bubble and tick bar are hidden in favour of the same Archivo 30px numeral and mono tick row as the specimen.
- **Toggle:** ink track with a ground-coloured knob when on.

### Navigation
- Streamlit's sidebar nav, mono uppercase, 12px, ink. Active page: 600 weight on a hairline-toned pill with 2px corners. No icons.

### Readouts
- **Readout row:** auto-fit cells at a 150px minimum; each opens with a 1px ink top rule, then a label (11px muted tracked uppercase), a headline numeral, and an 11px muted sub-line. A quiet variant drops the numeral to 13px mono for text such as "no listings at this size". Replaces Streamlit's metric tiles everywhere.
- **Readout line:** one wrapping mono line at 13px under a 1px ink rule; values in ink 600, connecting words in muted. Used where the page leads with a chart.

### Tables
- Mono 13px tabular, no outer border; header row in label style over a 1px ink rule, body rows separated by hairline rules, 6px by 8px cell padding.

### Charts
- Plotly on the theme ground: ink axis lines and ticks, hairline gridlines, 11px mono ticks with muted axis titles, Archivo titles, ink-bordered hover labels on paper. Colourway is ink then muted; charts set vermilion themselves and only on the selected series.

### The Specimen Cell (signature)
- A borderless button with a 1px hairline top border (ink on hover), a 44px SVG plot, then the name (11px muted, ellipsis) and a row of price, percent versus city (ink when above the city) and n (muted).
- Curve: 1px ink stroke over an 8% ink band clipped to the 94% range; a muted vertical at the city typical price; a hollow raw-median dot on the baseline.
- Under 10 listings: 0.75px stroke dashed 3/2 with no band. Extrapolated beyond observed sizes: curve and band in muted. Selected: 1.5px vermilion stroke and 16% vermilion band.
- Motion: curve, band and clip ease over 120ms on cubic-bezier(0.22, 1, 0.36, 1); disabled under reduced motion.

## Do's and Don'ts

### Do:
- **Do** use the equal-tailed 94% interval (3rd to 97th percentile) for every band, range and interval, and say "94%" in its label.
- **Do** keep the mark grammar identical on every page: light ink band = 94% range, dashed thinner stroke = fewer than 10 listings, hollow dot = raw median, muted vertical = city typical.
- **Do** keep functional text at 11px or larger and let the grid drop columns before type shrinks.
- **Do** read every colour from the active theme's tokens so light and dark stay one system.
- **Do** head readouts with a 1px ink rule and set changing numbers in tabular figures.

### Don't:
- **Don't** use vermilion for anything other than the selected neighborhood, the slider thumb and fill, and the primary action.
- **Don't** use dashes on neighborhood curves or intervals for anything but the under-10-listings state.
- **Don't** add shadows, blur, gradients or tinted cards; separate with 1px rules.
- **Don't** round boxes beyond 2px; round forms are for handles and point marks (slider thumb, toggle, raw-median dot, chart markers).
- **Don't** use Streamlit metric tiles or a KPI tile row; use the readout row or readout line.
- **Don't** use emojis anywhere in the UI; the few icons the build draws itself (select chevron, legend keys) are inline SVG strokes in ink.
