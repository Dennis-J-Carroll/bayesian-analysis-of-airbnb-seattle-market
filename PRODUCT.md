# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: hiring audiences evaluating Dennis Carroll as a data scientist, in two layers.

- **General recruiters** skimming for about a minute. They need to see, quickly and without statistics vocabulary, what was built and that it works.
- **Technical reviewers** (data-science / ML hiring managers) who will open the model and check it: priors, hierarchy, convergence, how intervals are computed, whether claims match the code.

The dashboard serves both: a short readable story on top, statistical depth one click down.

## Product Purpose

A portfolio piece that demonstrates applied Bayesian modeling on real data: the Seattle Airbnb market (Inside Airbnb listings). Success means a recruiter leaves understanding "this person can build and explain a hierarchical Bayesian model," and a technical reviewer who digs in finds the work correct and honestly reported.

## Positioning

Uncertainty is the point. Every price estimate comes with a posterior distribution and credible interval, and neighborhood effects are partially pooled (88 neighborhoods share strength through a hierarchy). Rigor and honesty over feature count: the dashboard shows only what the deployed model actually does.

## Operating Context

- Streamlit multi-page app, entry `app.py`, deployed on Streamlit Community Cloud (bayesian-analysis-dashboard.streamlit.app). Hugging Face Spaces front matter in README is legacy, not a target.
- Visitors arrive from a resume, LinkedIn, or GitHub link, usually on a laptop, sometimes a phone.
- Source repo: github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market.

## Capabilities and Constraints

- Deployed model (`outputs/model_trace.nc`): PyMC hierarchical regression on log(price) with varying intercepts and varying slopes for `accommodates` across 88 neighborhoods (`alpha`, `beta`, hyperpriors `mu_alpha`, `mu_beta`, `sigma_alpha`, `sigma_beta`, noise `sigma`); 4 chains x 2000 draws; includes posterior predictive.
- Predictions must use the real model: neighborhood-specific effects, the raw guest count (the model was trained on unstandardized `accommodates`), and observation noise for predictive intervals. Inputs the model does not use must not be offered.
- Data: `data/raw/listings.csv` (6,862 rows). Contains 635 missing prices and 83 prices over $1,000, including placeholders ($40k-$50k/night, CBD hotel rooms); analysis must handle these consistently across every page.
- CSV upload for other cities' data exists (schema detection, aliases).
- Undecided: whether to later train and deploy the larger "enhanced" model (property type, amenities, reviews).

## Brand Commitments

- No emojis anywhere in the UI (navigation, headings, labels, messages).
- Honest claims only: README and in-app numbers must match what the deployed model and data produce.

## Evidence on Hand

- Real trained trace, real listing/calendar/review data, four notebooks (`notebooks/01`-`04`), analysis scripts in `src/`.
- Unverified: README metrics (R² 0.687, RMSE $74.23, "enterprise-grade," "production-ready"). These describe a model the dashboard does not run and must not be shown until reproduced.
- No testimonials, users, or business outcomes exist; do not fabricate any.

## Product Principles

1. Show the uncertainty, not just the point estimate.
2. Every claim is reproducible from the repo.
3. Layered depth: a one-minute story first, full model detail one click away.
4. Data-quality decisions (outliers, missing values) are stated, not hidden.

## Accessibility & Inclusion

Readable in light and dark themes; chart colors distinguishable without relying on hue alone; works at laptop and phone widths.
