Implementing a Dynamic Grid Layout in Streamlit::

(((Implementing UI from: https://discuss.streamlit.io/t/dynamic-grid-layout-ui/2097 )))

This guide explains how to add a "Dynamic Grid" feature to your app.py. This allows you to pass a list of items (like cards, metrics, or graphs) and a number of columns, and the layout will automatically handle the rows and wrapping.Step 1: Add the Helper FunctionFirst, we need a utility function that splits a list of data into chunks and creates rows of columns.Add this function to your app.py (preferably near the top, after your imports and before st.set_page_config, or inside a utils file if you prefer).def render_dynamic_grid(data, num_columns, render_item_func):
    """
    Renders a list of items in a dynamic grid layout.
    
    Args:
        data (list): List of data items to display.
        num_columns (int): Number of columns per row.
        render_item_func (function): Function to render a single item. 
                                     It should accept a single argument (the item).
    """
    # Loop through the data in batches of 'num_columns'
    for i in range(0, len(data), num_columns):
        # Create a row of columns
        cols = st.columns(num_columns)
        
        # Get the current batch of items
        batch = data[i:i+num_columns]
        
        # Render each item in its respective column
        for col, item in zip(cols, batch):
            with col:
                render_item_func(item)
Step 2: Define Your DataIn your show_home_page function, you currently have hardcoded HTML cards. First, let's define the data structure so it can be easily expanded.# Define the data for the grid
capabilities_data = [
    {
        "title": "💰 Price Intelligence",
        "items": ["Bayesian predictions", "Confidence intervals", "Uncertainty quantification"]
    },
    {
        "title": "📊 Investment Analysis",
        "items": ["ROI projections", "Risk assessment", "Portfolio optimization"]
    },
    {
        "title": "📍 Market Intelligence",
        "items": ["Neighborhood scoring", "Competitive analysis", "Market trends"]
    },
    # You can now easily add a 4th item without breaking the layout!
    {
        "title": "✅ Model Validation",
        "items": ["Real-world backtesting", "Error metrics", "Calibration plots"]
    }
]
Step 3: Implement the "Misty Morning" PaletteWe will inject CSS to apply the specific hex codes you requested.Dark Green/Slate: #2f4f4f (Text/Headers)Grey Blue: #778899 (Borders)Beige: #f5f5dc (App Background - Optional)Light Blue: #add8e6 (Card Background)Sky Blue: #87ceeb (Accents)Add this function to your app.py or inside show_home_page:def apply_misty_theme():
    st.markdown("""
    <style>
        /* Optional: Set the main app background to Beige */
        .stApp {
            background-color: #f5f5dc;
        }

        /* Feature Card Styling */
        div.feature-card {
            background-color: #add8e6;       /* Light Blue */
            border: 2px solid #778899;       /* Grey Blue */
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            height: 100%;
        }

        /* Card Headers */
        div.feature-card h3 {
            color: #2f4f4f;                  /* Dark Slate */
            border-bottom: 2px solid #87ceeb; /* Sky Blue */
            padding-bottom: 10px;
            margin-bottom: 10px;
        }

        /* List Items */
        div.feature-card ul li {
            color: #2f4f4f;                  /* Dark Slate */
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
Step 4: Create the Render FunctionNow define the function that draws a single card using the CSS class feature-card we defined above.def render_feature_card(item):
    """Helper function to render a single feature card"""
    # Create HTML list items
    list_html = "".join([f"<li>{sub}</li>" for sub in item['items']])
    
    # Render the card
    st.markdown(f"""
    <div class="feature-card">
        <h3>{item['title']}</h3>
        <ul>
            {list_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)
Complete Example for app.pyHere is how the updated show_home_page function in your app.py should look, integrating both the grid layout and the color palette:def show_home_page():
    """Display home page with overview and key metrics"""

    # 1. Apply the Custom Color Palette
    # ---------------------------------------------------------
    st.markdown("""
    <style>
        /* Misty Morning Palette Implementation */
        div.feature-card {
            background-color: #add8e6;        /* Light Blue */
            border: 2px solid #778899;        /* Grey Blue */
            border-radius: 12px;
            padding: 20px;
            height: 280px;                    /* Fixed height for uniformity */
            box-shadow: 0 4px 6px rgba(47, 79, 79, 0.2);
            transition: transform 0.2s;
        }
        div.feature-card:hover {
            transform: translateY(-5px);
        }
        div.feature-card h3 {
            color: #2f4f4f;                   /* Dark Slate */
            border-bottom: 3px solid #87ceeb; /* Sky Blue */
            padding-bottom: 12px;
            margin-bottom: 15px;
            font-size: 1.2rem;
            font-weight: bold;
        }
        div.feature-card ul {
            padding-left: 20px;
            margin: 0;
        }
        div.feature-card li {
            color: #2f4f4f;                   /* Dark Slate */
            margin-bottom: 8px;
            font-size: 0.95rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # ... [Previous Welcome Section Code] ...

    # 2. Define Data
    # ---------------------------------------------------------
    features = [
        {
            "title": "💰 Price Intelligence",
            "items": ["Bayesian predictions", "Confidence intervals", "Neighborhood benchmarking"]
        },
        {
            "title": "📊 Investment Analysis",
            "items": ["ROI projections", "Risk assessment", "Sensitivity analysis"]
        },
        {
            "title": "📍 Market Intelligence",
            "items": ["Neighborhood comparison", "Strategic scoring", "Competitive analysis"]
        },
        {
            "title": "⚙️ Feature Impact",
            "items": ["Amenity valuation", "Upgrade ROI", "Premium features"]
        } 
    ]

    # 3. Define Render Function
    # ---------------------------------------------------------
    def render_card(feature):
        items_html = "".join([f"<li>{x}</li>" for x in feature['items']])
        st.markdown(f"""
        <div class="feature-card">
            <h3>{feature['title']}</h3>
            <ul>{items_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    # 4. Call Dynamic Grid
    # ---------------------------------------------------------
    st.markdown("### 🎯 Platform Capabilities")
    
    # Render with 3 columns (it will wrap the 4th item automatically)
    render_dynamic_grid(features, 3, render_card)

    st.markdown("---")

    # ... [Rest of your existing code] ...

