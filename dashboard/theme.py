"""Live Specimen visual tokens, app-wide CSS and the shared Plotly template.

Paper ground, ink text, one vermilion accent reserved for the selection, the
slider and the primary action. Archivo for display, JetBrains Mono for labels
and readouts. 1px rules, radius at most 2px, no shadows, blur or gradients.
"""

import plotly.graph_objects as go
import streamlit as st

TOKENS: dict[str, dict[str, str]] = {
    "light": {
        "ground": "#FBFBFA",
        "ink": "#111111",
        "accent": "#D6452B",
        "muted": "#6E6E69",
        "rule": "#D8D8D6",
    },
    "dark": {
        "ground": "#111111",
        "ink": "#ECEBE6",
        "accent": "#D6452B",
        "muted": "#9A9CA0",
        "rule": "#2A2B2E",
    },
}

FONTS_URL: str = (
    "https://fonts.googleapis.com/css2"
    "?family=Archivo:wght@400;800&family=JetBrains+Mono:wght@400;600&display=swap"
)

DISPLAY_FONT = "'Archivo', 'Helvetica Neue', Arial, sans-serif"
MONO_FONT = "'JetBrains Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace"

# Text-only selectors: a broad selector such as [class*="st-"] also hits
# Streamlit's icon font and turns every icon into its ligature name.
_HEADINGS = "h1, h2, h3, h4, h5, h6"
_BODY = "p, li, .stMarkdown"
_SMALL_LABELS = (
    "label, "
    '[data-testid="stMetricLabel"], '
    '[data-testid="stCaptionContainer"], '
    '[data-testid="stSidebarNav"] span'
)


def css(theme: str) -> str:
    """App-wide stylesheet for one theme ("light" or "dark")."""
    t = TOKENS[theme]
    return f"""
@import url('{FONTS_URL}');

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
  background: {t["ground"]};
  color: {t["ink"]};
}}
[data-testid="stSidebar"] {{
  background: {t["ground"]};
  border-right: 1px solid {t["ink"]};
}}

{_HEADINGS} {{
  font-family: {DISPLAY_FONT};
  color: {t["ink"]};
  letter-spacing: -0.02em;
}}
h1 {{ font-weight: 800; }}

{_BODY} {{
  font-family: {MONO_FONT};
  color: {t["ink"]};
}}
{_SMALL_LABELS} {{
  font-family: {MONO_FONT};
  font-size: 11px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: {t["muted"]};
}}
[data-testid="stSidebarNav"] span {{ font-size: 12px; color: {t["ink"]}; }}
[data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: {t["accent"]}; }}
[data-testid="stMetricValue"] {{
  font-family: {DISPLAY_FONT};
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  color: {t["ink"]};
}}

hr {{ border: none; border-top: 1px solid {t["rule"]}; }}
[data-testid="stExpander"] details {{
  border: 1px solid {t["rule"]};
  border-radius: 2px;
  box-shadow: none;
}}

.stButton button, .stDownloadButton button,
[data-baseweb="input"], [data-baseweb="textarea"],
[data-baseweb="select"] > div {{
  border: 1px solid {t["rule"]};
  border-radius: 2px;
  box-shadow: none;
}}
/* Streamlit's own theme is light; give native widgets the active ground and
   ink so the Dark toggle never leaves a pale field with pale text. */
[data-baseweb="input"], [data-baseweb="input"] > div,
[data-baseweb="textarea"], [data-baseweb="select"] > div,
[data-testid="stNumberInputContainer"] {{
  background: {t["ground"]};
  color: {t["ink"]};
}}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea,
[data-baseweb="select"] input, [data-baseweb="select"] div {{
  color: {t["ink"]};
}}
[data-testid="stNumberInput"] button {{
  background: {t["ground"]};
  color: {t["ink"]};
}}
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {{
  background: {t["ground"]};
  color: {t["ink"]};
}}
[data-baseweb="popover"] li, [data-baseweb="popover"] li * {{
  color: {t["ink"]};
}}
[data-baseweb="select"] svg, [data-testid="stNumberInput"] svg {{
  fill: {t["ink"]};
  color: {t["ink"]};
}}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {{
  background: {t["rule"]};
}}
.stButton button, .stDownloadButton button {{
  background: {t["ground"]};
  color: {t["ink"]};
}}
[data-baseweb="checkbox"] > span, [data-baseweb="radio"] > div:first-child {{
  border-color: {t["ink"]};
}}
.stButton button[kind="primary"] p {{ color: #FFFFFF; }}
.stButton button[kind="primary"] {{
  background: {t["accent"]};
  border-color: {t["accent"]};
  color: #FFFFFF;
}}
[data-testid="stSlider"] [role="slider"] {{
  background: {t["accent"]};
  box-shadow: none;
}}

[data-testid="stHeader"] button,
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapseButton"] button {{
  color: {t["ink"]};
}}

::selection {{ background: {t["ink"]}; color: {t["ground"]}; }}
a, .stApp [data-testid="stMarkdownContainer"] a {{
  color: {t["ink"]};
  text-underline-offset: 3px;
}}

footer, #MainMenu, [data-testid="stMainMenu"], [data-testid="stDecoration"] {{
  display: none;
}}
"""


def apply_theme(theme: str) -> None:
    """Inject the stylesheet for `theme` into the running Streamlit page."""
    st.markdown(f"<style>{css(theme)}</style>", unsafe_allow_html=True)


def plotly_template(theme: str) -> go.layout.Template:
    """Plotly template on the theme's ground. Charts set `accent` themselves,
    and only on the selected series."""
    t = TOKENS[theme]
    axis = dict(
        gridcolor=t["rule"],
        linecolor=t["ink"],
        zerolinecolor=t["rule"],
        tickcolor=t["ink"],
        tickfont=dict(family=MONO_FONT, size=11, color=t["ink"]),
        title=dict(font=dict(family=MONO_FONT, size=11, color=t["muted"])),
    )
    return go.layout.Template(
        layout=go.Layout(
            font=dict(family=MONO_FONT.replace("'", ""), size=12, color=t["ink"]),
            title=dict(font=dict(family=DISPLAY_FONT, size=20, color=t["ink"])),
            paper_bgcolor=t["ground"],
            plot_bgcolor=t["ground"],
            colorway=[t["ink"], t["muted"]],
            xaxis=axis,
            yaxis=axis,
            hoverlabel=dict(
                bgcolor=t["ground"],
                bordercolor=t["ink"],
                font=dict(family=MONO_FONT.replace("'", ""), color=t["ink"]),
            ),
            legend=dict(font=dict(family=MONO_FONT.replace("'", ""), size=11)),
        )
    )
