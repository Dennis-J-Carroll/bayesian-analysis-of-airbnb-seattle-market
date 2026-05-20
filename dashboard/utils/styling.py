"""
Custom CSS styling for enterprise-grade dashboard
"""

import streamlit as st
import yaml
from pathlib import Path


def inject_minimal_theme():
    """Phase 1 minimal theme - white background + sage green accents."""
    st.markdown(
        """
    <style>
    /* Phase 1: Minimal Modern Neutral theme */
    .main {
        background-color: #ffffff !important;
    }

    .stApp {
        background-color: #ffffff !important;
    }

    .block-container {
        background-color: #ffffff !important;
    }

    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #77b899;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .insight-box {
        background: #f0fdf7;
        border-left: 3px solid #77b899;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""

    st.markdown(
        """
    <style>
    /* Main app styling - Misty Morning theme */
    .main {
        background-color: #f5f5dc !important;
    }

    /* Force light background for main content */
    .stApp {
        background-color: #f5f5dc !important;
    }

    /* Main content block */
    .block-container {
        background-color: #f5f5dc !important;
    }

    /* Header styling - Misty Morning theme */
    .main-header {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }

    .main-header .subtitle {
        color: #add8e6;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Info boxes - Misty Morning theme */
    .info-box {
        background-color: #add8e6;
        border-left: 4px solid #2f4f4f;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #1a1a1a;
    }

    .info-box h2, .info-box h4 {
        color: #2f4f4f;
        margin-top: 0;
    }

    .info-box p, .info-box li, .info-box ol {
        color: #1a1a1a;
    }

    /* Feature cards - Misty Morning theme */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        height: 100%;
        border-top: 3px solid #77b899;
        color: #1a1a1a;
    }

    .feature-card h3 {
        color: #2f4f4f;
        margin-top: 0;
        font-size: 1.3rem;
    }

    .feature-card h4 {
        color: #333333;
    }

    .feature-card p {
        color: #333333;
    }

    .feature-card ul {
        list-style-type: none;
        padding-left: 0;
        color: #333333;
    }

    .feature-card li {
        color: #333333;
    }

    .feature-card li:before {
        content: "✓ ";
        color: #2e7d32;
        font-weight: bold;
        margin-right: 0.5rem;
    }

    /* Metric cards - Misty Morning theme */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2f4f4f;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #333;
        font-weight: 600;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
    }

    /* Buttons - Misty Morning theme */
    .stButton > button {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }

    /* Sidebar styling - Misty Morning theme */
    .css-1d391kg {
        background-color: #f5f5dc;
    }

    section[data-testid="stSidebar"] {
        background-color: #2f4f4f;
        color: #ffffff;
    }

    section[data-testid="stSidebar"] .stRadio > label {
        color: #ffffff;
        font-weight: 600;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff;
    }

    section[data-testid="stSidebar"] .stMarkdown p {
        color: #ffffff;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff;
    }

    /* Sidebar text color fix */
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
    }

    /* Sidebar metric labels and values - white text */
    section[data-testid="stSidebar"] div[data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stMetricValue"] {
        color: #add8e6 !important;
    }

    /* Warning boxes */
    .stAlert {
        border-radius: 5px;
        padding: 1rem;
    }

    /* Success box text */
    .stSuccess {
        color: #1a1a1a !important;
    }

    /* Warning box text */
    .stWarning {
        color: #1a1a1a !important;
    }

    /* Error box text */
    .stError {
        color: #1a1a1a !important;
    }

    /* Info box text */
    .stInfo {
        color: #1a1a1a !important;
    }

    /* Data tables */
    .dataframe {
        border: none !important;
        border-radius: 5px;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        color: white !important;
        font-weight: 600;
        padding: 0.75rem;
        border: none;
    }

    .dataframe tbody tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    .dataframe tbody tr:hover {
        background-color: #e7f3ff;
        cursor: pointer;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 5px;
        font-weight: 600;
        color: #1a1a1a !important;
    }

    /* Expander content */
    .streamlit-expanderContent {
        color: #1a1a1a !important;
    }

    /* Expander content paragraphs and lists */
    .streamlit-expanderContent p, .streamlit-expanderContent li {
        color: #1a1a1a !important;
    }

    /* Tab styling - Misty Morning theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        color: white;
    }

    /* Slider styling - Misty Morning theme */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
    }

    /* Select box styling */
    .stSelectbox > div > div {
        border-radius: 5px;
        border: 2px solid #e0e0e0;
    }

    /* Number input styling */
    .stNumberInput > div > div > input {
        border-radius: 5px;
        border: 2px solid #e0e0e0;
    }

    /* Success/Error/Warning boxes with icons */
    .element-container .stAlert > div {
        border-radius: 5px;
        padding: 1rem 1rem 1rem 3rem;
        position: relative;
    }

    /* Loading spinner - Misty Morning theme */
    .stSpinner > div {
        border-top-color: #77b899 !important;
    }

    /* Charts and plots */
    .js-plotly-plot, .plot-container {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 3rem;
    }

    /* Custom card component - Misty Morning theme */
    .custom-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        color: #1a1a1a;
    }

    .custom-card h2 {
        color: #2f4f4f;
        margin-top: 0;
    }

    .custom-card h3 {
        color: #2f4f4f;
        margin-top: 0;
        border-bottom: 2px solid #77b899;
        padding-bottom: 0.5rem;
    }

    .custom-card p {
        color: #333333;
    }

    /* Prediction result box - Misty Morning theme */
    .prediction-result {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .prediction-result h2 {
        margin-top: 0;
        font-size: 2rem;
    }

    .prediction-result .value {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }

    /* ROI indicator */
    .roi-positive {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #155724;
    }

    .roi-positive h3 {
        color: #155724;
    }

    .roi-negative {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #721c24;
    }

    .roi-negative h3 {
        color: #721c24;
    }

    .roi-neutral {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #856404;
    }

    .roi-neutral h3 {
        color: #856404;
    }

    /* Comparison table - Misty Morning theme */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: white;
        border-radius: 5px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .comparison-table th {
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }

    .comparison-table td {
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }

    .comparison-table tr:hover {
        background-color: #f8f9fa;
    }

    /* Risk indicator */
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }

    .risk-medium {
        color: #ffc107;
        font-weight: bold;
    }

    .risk-high {
        color: #dc3545;
        font-weight: bold;
    }

    /* Progress bar - Misty Morning theme */
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(135deg, #2f4f4f 0%, #77b899 100%);
        transition: width 0.3s ease;
    }

    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #666;
        cursor: help;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Global text color contrast fixes */
    .main .block-container {
        color: #1a1a1a !important;
    }

    /* Ensure all headings have good contrast */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a !important;
    }

    /* Ensure all paragraph text has good contrast */
    p {
        color: #1a1a1a !important;
    }

    /* List items */
    li {
        color: #1a1a1a !important;
    }

    /* Ordered and unordered lists */
    ol, ul {
        color: #1a1a1a !important;
    }

    /* Ensure proper contrast for all text elements */
    .stMarkdown {
        color: #1a1a1a !important;
    }

    /* All markdown content */
    .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: #1a1a1a !important;
    }

    /* Comparison table text */
    .comparison-table td {
        color: #1a1a1a;
    }

    /* Data table body text */
    .dataframe tbody {
        color: #1a1a1a !important;
    }

    /* Data table cells */
    .dataframe tbody td {
        color: #1a1a1a !important;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }

        .feature-card {
            margin-bottom: 1rem;
        }

        .prediction-result .value {
            font-size: 2rem;
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def create_metric_card(title, value, subtitle=None, icon=None):
    """
    Create a custom metric card

    Args:
        title: Card title
        value: Main value to display
        subtitle: Optional subtitle
        icon: Optional emoji icon

    Returns:
        HTML string for the metric card
    """

    subtitle_html = (
        f"<p style='color: #666; margin: 0;'>{subtitle}</p>" if subtitle else ""
    )
    icon_html = (
        f"<span style='font-size: 2rem; margin-right: 0.5rem;'>{icon}</span>"
        if icon
        else ""
    )

    return f"""
    <div class="custom-card">
        <div style='display: flex; align-items: center;'>
            {icon_html}
            <div style='flex: 1;'>
                <h3 style='margin: 0; color: #2f4f4f;'>{title}</h3>
                <div style='font-size: 2rem; font-weight: bold; color: #333; margin: 0.5rem 0;'>{value}</div>
                {subtitle_html}
            </div>
        </div>
    </div>
    """


def create_prediction_card(price, ci_lower, ci_upper, neighborhood_comparison=None):
    """
    Create a prediction result card

    Args:
        price: Predicted price
        ci_lower: Lower confidence interval
        ci_upper: Upper confidence interval
        neighborhood_comparison: Optional comparison text

    Returns:
        HTML string for prediction card
    """

    comparison_html = (
        f"<p style='margin: 0; font-size: 1.1rem;'>{neighborhood_comparison}</p>"
        if neighborhood_comparison
        else ""
    )

    return f"""
    <div class="prediction-result">
        <h2>Predicted Price</h2>
        <div class="value">${price:.0f}/night</div>
        <p style='font-size: 1.2rem; margin: 0.5rem 0;'>
            90% Confidence Interval: ${ci_lower:.0f} - ${ci_upper:.0f}
        </p>
        {comparison_html}
    </div>
    """


def create_roi_card(roi, recommendation, probability_profit=None):
    """
    Create ROI result card with color-coded recommendation

    Args:
        roi: ROI percentage (as decimal)
        recommendation: Text recommendation
        probability_profit: Optional probability of profit

    Returns:
        HTML string for ROI card
    """

    if roi > 0.20:
        card_class = "roi-positive"
        icon = "✅"
        color = "#28a745"
    elif roi > 0:
        card_class = "roi-neutral"
        icon = "⚠️"
        color = "#ffc107"
    else:
        card_class = "roi-negative"
        icon = "🛑"
        color = "#dc3545"

    prob_html = (
        f"<p style='margin: 0.5rem 0;'>Probability of Profit: {probability_profit:.1%}</p>"
        if probability_profit
        else ""
    )

    return f"""
    <div class="{card_class}">
        <h3 style='margin: 0; display: flex; align-items: center;'>
            <span style='font-size: 2rem; margin-right: 0.5rem;'>{icon}</span>
            {recommendation}
        </h3>
        <div style='font-size: 2.5rem; font-weight: bold; margin: 1rem 0; color: {color};'>
            {roi:.1%} ROI
        </div>
        {prob_html}
    </div>
    """


def create_progress_bar(value, max_value=100, label=None):
    """
    Create a progress bar

    Args:
        value: Current value
        max_value: Maximum value (default 100)
        label: Optional label

    Returns:
        HTML string for progress bar
    """

    percentage = (value / max_value) * 100
    label_html = (
        f"<p style='margin: 0 0 0.5rem 0; font-weight: 600;'>{label}</p>"
        if label
        else ""
    )

    return f"""
    {label_html}
    <div class="progress-bar">
        <div class="progress-bar-fill" style="width: {percentage}%;"></div>
    </div>
    <p style='margin: 0.25rem 0; color: #666; font-size: 0.9rem;'>{value} / {max_value}</p>
    """


def load_theme_config(theme_name: str) -> dict:
    """Load theme configuration from YAML."""
    config_path = Path(__file__).parent.parent / "config" / "themes.yaml"
    with open(config_path) as f:
        themes = yaml.safe_load(f)
    return themes.get(theme_name, themes["modern_neutral"])


def apply_theme(theme_name: str = "modern_neutral"):
    """Apply CSS theme via st.markdown."""
    theme = load_theme_config(theme_name)
    colors = theme["colors"]

    css = f"""
    <style>
    /* WARNING: Targets Streamlit 1.38.0 internal DOM */
    :root {{
        --bg-primary: {colors['bg_primary']};
        --bg-secondary: {colors['bg_secondary']};
        --bg-sidebar: {colors['bg_sidebar']};
        --bg-card: {colors['bg_card']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --text-muted: {colors['text_muted']};
        --accent: {colors['accent']};
        --accent-hover: {colors['accent_hover']};
        --success: {colors['success']};
        --warning: {colors['warning']};
        --danger: {colors['danger']};
        --border: {colors['border']};
        --shadow: {colors['shadow']};
    }}

    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }}

    section[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar);
    }}

    div[data-testid="stMetric"] {{
        background: var(--bg-card);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid var(--accent);
        box-shadow: var(--shadow);
    }}

    div[data-testid="stMetricLabel"] {{
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
    }}

    .insight-box {{
        background: {colors['bg_secondary']};
        border-left: 3px solid var(--accent);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}

    .insight-box-title {{
        color: var(--accent);
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .insight-box-content {{
        color: var(--text-primary);
        font-size: 0.9375rem;
        line-height: 1.5;
    }}

    .stButton > button {{
        background-color: var(--accent);
        color: white;
        border: none;
        border-radius: 0.375rem;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }}

    .stButton > button:hover {{
        background-color: var(--accent-hover);
        box-shadow: var(--shadow);
    }}

    h1, h2, h3 {{
        color: var(--text-primary);
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def get_chart_template(theme_name: str = "modern_neutral") -> str:
    """Get Plotly template name for current theme."""
    theme = load_theme_config(theme_name)
    return theme["chart"]["template"]


def get_chart_palette(theme_name: str = "modern_neutral") -> list[str]:
    """Get color palette for charts."""
    theme = load_theme_config(theme_name)
    return theme["chart"]["palette"]
