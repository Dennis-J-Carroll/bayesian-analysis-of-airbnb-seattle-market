"""
Custom CSS styling for enterprise-grade dashboard
"""

import streamlit as st


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""

    st.markdown(
        """
    <style>
    /* Main app styling */
    .main {
        background-color: #f8f9fa;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        color: #e0e7ff;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* Info boxes */
    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #0d47a1;
    }

    .info-box h2, .info-box h4 {
        color: #0d47a1;
        margin-top: 0;
    }

    .info-box p, .info-box li, .info-box ol {
        color: #1a1a1a;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        height: 100%;
        border-top: 3px solid #667eea;
        color: #1a1a1a;
    }

    .feature-card h3 {
        color: #667eea;
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

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #666;
        font-weight: 600;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    section[data-testid="stSidebar"] {
        background-color: #1a252f;
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
        color: #ffffff;
    }

    /* Warning boxes */
    .stAlert {
        border-radius: 5px;
        padding: 1rem;
    }

    /* Data tables */
    .dataframe {
        border: none !important;
        border-radius: 5px;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    }

    /* Tab styling */
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
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

    /* Custom card component */
    .custom-card {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        color: #1a1a1a;
    }

    .custom-card h2 {
        color: #667eea;
        margin-top: 0;
    }

    .custom-card h3 {
        color: #667eea;
        margin-top: 0;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }

    .custom-card p {
        color: #333333;
    }

    /* Prediction result box */
    .prediction-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    /* Comparison table */
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
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    /* Progress bar */
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        color: #1a1a1a;
    }

    /* Ensure all headings have good contrast */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a;
    }

    /* Ensure all paragraph text has good contrast */
    p {
        color: #333333;
    }

    /* List items */
    li {
        color: #333333;
    }

    /* Ensure proper contrast for all text elements */
    .stMarkdown {
        color: #1a1a1a;
    }

    /* Comparison table text */
    .comparison-table td {
        color: #1a1a1a;
    }

    /* Data table body text */
    .dataframe tbody {
        color: #1a1a1a;
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
                <h3 style='margin: 0; color: #667eea;'>{title}</h3>
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
