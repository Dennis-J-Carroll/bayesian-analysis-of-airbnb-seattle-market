"""Neighborhoods: 88 estimates with intervals, and how pooling moves them."""

import pandas as pd
import streamlit as st

from dashboard.components.charts import forest_plot, price_histogram, shrinkage_plot
from dashboard.components.readouts import MISSING, Readout, render_readouts
from dashboard.utils.artifacts import load_artifacts, neighborhood_by_name
from dashboard.utils.data_loader import load_listings
from dashboard.utils.session_manager import AppState

CHART_CONFIG = {"displayModeBar": False}
DEFAULT_NEIGHBORHOOD = "Broadway"
DEFAULT_GUESTS = 2
SHOWCASE = "Holly Park"  # two listings: the clearest case of pooling


@st.cache_data(show_spinner=False)
def _prices(name: str) -> pd.Series:
    df = load_listings()
    return df.loc[df["neighbourhood_cleansed"] == name, "price"].reset_index(drop=True)


def _money(v: float | None) -> str:
    return MISSING if v is None else f"${v:,.0f}"


def _md(v: float | None) -> str:
    """Money for Markdown text: a bare $ pair would start LaTeX."""
    return _money(v).replace("$", "\\$")


def _plural(n: int, word: str) -> str:
    return f"{n:,} {word}" if n == 1 else f"{n:,} {word}s"


def _shrinkage_caption(art, guests: int, omitted: int) -> str:
    i = guests - 1
    city = art.neighborhoods["city"]["typical"]["median"][i]
    holly = neighborhood_by_name(art, SHOWCASE)
    model = holly["typical"]["median"][i]
    raw = holly["raw_median_by_guests"].get(str(guests))
    n = holly["n_listings"]
    base = (
        "Each circle is a neighborhood: its raw median price on the horizontal "
        "axis, the model's typical price on the vertical, and circle area grows "
        "with listings. Circles off the diagonal were pulled toward the "
        f"citywide line (typical {_md(city)}) by partial pooling, thin "
        "neighborhoods most of all. "
    )
    if raw is not None:
        holly_txt = (
            f"{SHOWCASE} has only {_plural(n, 'listing')}, a raw median of "
            f"{_md(raw)} at this size, and the model puts its typical price "
            f"near {_md(model)}. "
        )
    else:
        holly_txt = (
            f"{SHOWCASE} has only {_plural(n, 'listing')}, none at this size, "
            f"so it is not drawn; the model still puts its typical price near "
            f"{_md(model)} by borrowing from the city. "
        )
    omit = f"{_plural(omitted, 'neighborhood')} with no listings at this size are not drawn."
    return base + holly_txt + omit


def render() -> None:
    art = load_artifacts()
    theme = AppState.theme()
    nbhds = art.neighborhoods["neighborhoods"]
    names = sorted(n["name"] for n in nbhds)

    st.title("Neighborhoods")
    c1, c2 = st.columns([3, 2])
    selected = c1.selectbox(
        "Neighborhood", names, index=names.index(DEFAULT_NEIGHBORHOOD), key="nbhd"
    )
    guests = c2.slider("Guests", 1, 16, DEFAULT_GUESTS, key="nbhd_guests")

    i = guests - 1
    n = neighborhood_by_name(art, selected)
    city = art.neighborhoods["city"]["typical"]["median"][i]
    typ = n["typical"]
    raw = n["raw_median_by_guests"].get(str(guests))

    st.subheader(selected)
    render_readouts(
        [
            Readout("Listings", f"{n['n_listings']:,}", "after cleaning", "listings"),
            Readout(
                "Typical price",
                _money(typ["median"][i]),
                f"94% range {_money(typ['lo'][i])} to {_money(typ['hi'][i])}",
                "typical-price",
            ),
            (
                Readout("Raw median", _money(raw), f"{guests} guests", "raw-median")
                if raw is not None
                else Readout(
                    "Raw median",
                    "no listings at this size",
                    f"{guests} guests",
                    "raw-median",
                    quiet=True,
                )
            ),
            Readout(
                "Vs city",
                f"{typ['median'][i] / city:.2f}x",
                f"city typical {_money(city)}",
                "premium",
            ),
        ],
        theme,
    )

    prices = _prices(selected)
    st.plotly_chart(
        price_histogram(prices, theme, "Nightly price, all sizes"),
        use_container_width=True,
        config=CHART_CONFIG,
    )

    st.subheader(f"Typical price at {guests} guests, all {len(nbhds)} neighborhoods")
    st.caption(
        "Dots are the model's typical price, lines the 94% interval, sorted by "
        "price. Dashed lines mark neighborhoods with fewer than 10 listings: "
        "their intervals are wider because there is less data. The vertical "
        "line is the city."
    )
    st.plotly_chart(
        forest_plot(nbhds, guests, selected, theme, city_median=city),
        use_container_width=True,
        config=CHART_CONFIG,
    )

    st.subheader("Raw medians against the model")
    fig = shrinkage_plot(nbhds, guests, theme, city_median=city)
    st.plotly_chart(fig, use_container_width=True, config=CHART_CONFIG)
    st.caption(_shrinkage_caption(art, guests, fig.layout.meta["omitted"]))
