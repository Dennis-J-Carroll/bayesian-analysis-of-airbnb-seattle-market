# dashboard/pages/business_strategy.py
"""Investment strategy and data-driven recommendations."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from ..utils.session_manager import AppState
from ..utils.styling import get_chart_template, get_chart_palette


def _compute_revenue_potential(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate annual revenue potential per neighborhood.

    Revenue proxy = avg_price × occupied_days
    where occupied_days = 365 - avg_availability_365
    """
    grouped = df.groupby("neighbourhood_cleansed").agg(
        avg_price=("price", "mean"),
        avg_availability=("availability_365", "mean"),
        listing_count=("price", "count"),
    )
    grouped["occupied_days"] = (365 - grouped["avg_availability"]).clip(lower=0)
    grouped["revenue_potential"] = grouped["avg_price"] * grouped["occupied_days"]
    return grouped.reset_index().sort_values("revenue_potential", ascending=False)


def _compute_room_type_multipliers(df: pd.DataFrame) -> pd.DataFrame:
    """Price multiplier vs market median per room type."""
    median_price = df["price"].median()
    if median_price == 0:
        median_price = 1.0
    room_stats = (
        df.groupby("room_type")["price"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "avg_price", "count": "listings"})
        .reset_index()
    )
    room_stats["multiplier"] = (room_stats["avg_price"] / median_price).round(2)
    return room_stats.sort_values("avg_price", ascending=False)


def _compute_bedroom_roi(df: pd.DataFrame) -> pd.DataFrame:
    """Avg price by bedroom count for entire-home listings."""
    entire = df[df["room_type"] == "Entire home/apt"]
    if entire.empty:
        entire = df.copy()
    result = entire.copy()
    result["bedrooms_capped"] = result["bedrooms"].clip(upper=4).fillna(0).astype(int)
    return (
        result.groupby("bedrooms_capped")["price"]
        .agg(["mean", "count"])
        .rename(columns={"mean": "avg_price", "count": "listings"})
        .reset_index()
    )


@st.fragment
def _kpi_section(df: pd.DataFrame):
    """Top-line investment KPIs — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Investment Snapshot")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Key investment metrics computed from the active dataset. "
                "Neighborhood premium = top-3 avg price ÷ bottom-3 avg price."
            )

    nbhd_avg = df.groupby("neighbourhood_cleansed")["price"].mean()
    top_avg = nbhd_avg.nlargest(3).mean() if len(nbhd_avg) >= 3 else nbhd_avg.max()
    bot_avg = nbhd_avg.nsmallest(3).mean() if len(nbhd_avg) >= 3 else nbhd_avg.min()
    premium = top_avg / bot_avg if bot_avg > 0 else 1.0

    entire_avg = df[df["room_type"] == "Entire home/apt"]["price"].mean()
    private_avg = df[df["room_type"] == "Private room"]["price"].mean()
    multiplier = entire_avg / private_avg if private_avg > 0 else 1.0

    bedroom_roi = _compute_bedroom_roi(df)
    best_br = (
        int(bedroom_roi.loc[bedroom_roi["avg_price"].idxmax(), "bedrooms_capped"])
        if not bedroom_roi.empty
        else 2
    )

    market_median = df["price"].median()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Neighborhood Premium",
        f"{premium:.1f}×",
        help="Top-3 vs bottom-3 neighborhood avg price ratio",
    )
    col2.metric(
        "Entire Home vs Room",
        f"{multiplier:.1f}×",
        help="Entire home avg vs private room avg",
    )
    col3.metric(
        "Optimal Bedrooms",
        f"{best_br} BR",
        help="Bedroom count with highest avg price (entire homes)",
    )
    col4.metric(
        "Market Median",
        f"${market_median:.0f}/night",
        help="Median nightly price across all listings",
    )


@st.fragment
def _revenue_section(df: pd.DataFrame, theme: str):
    """Revenue potential chart — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Revenue Potential by Neighborhood")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Revenue proxy: avg_price × (365 − avg_availability). "
                "Higher = more earning potential based on price and historical occupancy."
            )

    template = get_chart_template(theme)
    palette = get_chart_palette(theme)

    top_n = st.slider(
        "Show top N neighborhoods", min_value=5, max_value=20, value=10, key="bs_top_n"
    )
    revenue_df = _compute_revenue_potential(df).head(top_n)

    fig = go.Figure(
        go.Bar(
            x=revenue_df["revenue_potential"],
            y=revenue_df["neighbourhood_cleansed"],
            orientation="h",
            marker=dict(
                color=revenue_df["revenue_potential"],
                colorscale=[[0, palette[2]], [1, palette[0]]],
                showscale=False,
            ),
            text=revenue_df["revenue_potential"].apply(lambda x: f"${x:,.0f}"),
            textposition="outside",
        )
    )
    fig.update_layout(
        xaxis_title="Revenue Potential ($/year proxy)",
        yaxis=dict(autorange="reversed"),
        template=template,
        showlegend=False,
        margin=dict(l=0),
    )
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def _room_type_section(df: pd.DataFrame, theme: str):
    """Room type multiplier chart — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Room Type Price Multipliers")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "How each room type prices relative to the market median. "
                "Values above 1.0 command a premium."
            )

    template = get_chart_template(theme)
    palette = get_chart_palette(theme)
    room_df = _compute_room_type_multipliers(df)

    fig = go.Figure(
        go.Bar(
            x=room_df["room_type"],
            y=room_df["multiplier"],
            marker_color=palette[1],
            text=room_df["multiplier"].apply(lambda x: f"{x:.2f}×"),
            textposition="outside",
        )
    )
    fig.add_hline(
        y=1.0, line_dash="dash", line_color="gray", annotation_text="Market median"
    )
    fig.update_layout(
        xaxis_title="Room Type",
        yaxis_title="Price Multiplier",
        template=template,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


@st.fragment
def _bedroom_roi_section(df: pd.DataFrame, theme: str):
    """Bedroom ROI chart + full revenue table — reruns independently."""
    col_title, col_info = st.columns([6, 1])
    with col_title:
        st.subheader("Bedroom Count ROI (Entire Homes)")
    with col_info:
        with st.popover("ℹ️"):
            st.markdown(
                "Average nightly price by bedroom count for entire-home listings. "
                "4+ bedrooms are grouped."
            )

    template = get_chart_template(theme)
    palette = get_chart_palette(theme)
    br_df = _compute_bedroom_roi(df)

    if not br_df.empty:
        x_labels = [str(int(b)) if b < 4 else "4+" for b in br_df["bedrooms_capped"]]
        fig = go.Figure(
            go.Bar(
                x=x_labels,
                y=br_df["avg_price"],
                marker_color=palette[3 % len(palette)],
                text=br_df["avg_price"].apply(lambda x: f"${x:.0f}"),
                textposition="outside",
            )
        )
        fig.update_layout(
            xaxis_title="Bedrooms",
            yaxis_title="Avg Price ($/night)",
            template=template,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Full Revenue Potential Data"):
        full_df = _compute_revenue_potential(df)
        st.dataframe(
            full_df[
                [
                    "neighbourhood_cleansed",
                    "avg_price",
                    "occupied_days",
                    "revenue_potential",
                    "listing_count",
                ]
            ]
            .rename(
                columns={
                    "neighbourhood_cleansed": "Neighborhood",
                    "avg_price": "Avg Price ($)",
                    "occupied_days": "Occupied Days/yr",
                    "revenue_potential": "Revenue Potential ($)",
                    "listing_count": "Listings",
                }
            )
            .round(0)
            .reset_index(drop=True),
            use_container_width=True,
        )


def render():
    """Render business strategy page with data-driven investment analysis."""
    st.title("Business Strategy")

    df = AppState.get_active_df()
    theme = st.session_state.get(AppState.THEME, "modern_neutral")

    _kpi_section(df)
    st.markdown("---")
    _revenue_section(df, theme)
    st.markdown("---")
    _room_type_section(df, theme)
    st.markdown("---")
    _bedroom_roi_section(df, theme)
