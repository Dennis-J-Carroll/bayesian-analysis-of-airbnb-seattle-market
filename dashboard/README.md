# Enterprise Airbnb Seattle Analytics Dashboard

A production-ready Streamlit application for Airbnb pricing intelligence and investment analysis.

## 🚀 Quick Start

### Installation

```bash
# Navigate to project root
cd /path/to/Dashboard-Attempt_1-airbnb-seattle-market

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard/app.py
```

### First-Time Setup

1. **Ensure data files exist**:
   - `data/raw/listings.csv` (required)
   - Model trace file (optional - will generate synthetic if missing)

2. **Run the dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```

3. **Open browser**:
   - Local URL: http://localhost:8501
   - Network URL: Will be displayed in terminal

## 📋 Requirements

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
pymc>=5.9.0
arviz>=0.16.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
xarray>=2023.1.0
```

## 🎯 Features

### 1. Price Predictor
- Instant price estimates with confidence intervals
- Bayesian uncertainty quantification
- Neighborhood comparison
- Reliability scoring
- Three pricing strategies (conservative, balanced, aggressive)

### 2. Investment Analyzer
- ROI projections with Monte Carlo simulation
- Risk assessment and breakdown
- Sensitivity analysis
- Stress testing scenarios
- Portfolio optimization

### 3. Neighborhood Comparison
- Side-by-side comparison of up to 4 neighborhoods
- Market metrics and trends
- Strategic scoring
- Visual comparisons

### 4. Model Validation
- Real property test cases
- Aggregate performance metrics
- Actual vs. predicted plots
- Calibration analysis

### 5. Feature Impact Calculator
- Calculate value of adding amenities
- ROI for property improvements
- Feature prioritization
- Investment payback analysis

## 📁 Project Structure

```
dashboard/
├── app.py                          # Main application entry point
├── components/                     # Dashboard components
│   ├── __init__.py
│   ├── price_predictor.py         # Price prediction tool
│   ├── investment_analyzer.py     # Investment analysis (to be created)
│   ├── neighborhood_comparison.py # Neighborhood comparison (to be created)
│   ├── model_validation.py        # Model validation (to be created)
│   └── feature_impact.py          # Feature impact calculator (to be created)
├── utils/                          # Utilities
│   ├── __init__.py
│   ├── data_loader.py             # Data and model loading
│   └── styling.py                 # Custom CSS and styling
└── README.md                       # This file
```

## 🎨 Customization

### Styling

Edit `dashboard/utils/styling.py` to customize:
- Color scheme (gradient colors)
- Card styling
- Fonts and typography
- Layout spacing

### Components

Each component is modular. To add new features:

1. Create new file in `dashboard/components/`
2. Implement page function: `def my_component_page():`
3. Import in `dashboard/app.py`
4. Add to navigation menu

## 🔧 Configuration

### Model Configuration

The dashboard automatically:
- Loads data from `data/raw/listings.csv`
- Attempts to load trained model from `models/hierarchical_model_trace.nc`
- Generates synthetic trace if model not found (for demo purposes)

### Data Configuration

Required columns in `listings.csv`:
- `price` - Listing price (format: "$XX.XX")
- `accommodates` - Number of guests
- `neighbourhood_cleansed` - Neighborhood name

Optional columns:
- `latitude`, `longitude` - For map visualization
- `room_type` - Type of accommodation
- `amenities` - List of amenities

## 📊 Performance Optimization

### Caching

The dashboard uses Streamlit's caching:
- `@st.cache_resource` for model/data loading
- `@st.cache_data` for computations

### Large Datasets

For datasets > 50k rows:
1. Enable data sampling in `data_loader.py`
2. Increase server memory limits
3. Consider database backend instead of CSV

## 🚀 Deployment

### Streamlit Cloud

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Deploy

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t airbnb-dashboard .
docker run -p 8501:8501 airbnb-dashboard
```

### AWS/Cloud

See deployment guides in `docs/deployment/`

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Data file not found"
- **Solution**: Ensure `data/raw/listings.csv` exists

**Issue**: "Module not found"
- **Solution**: Install requirements: `pip install -r requirements.txt`

**Issue**: "Model trace not found"
- **Solution**: Dashboard will generate synthetic trace automatically

**Issue**: Slow loading
- **Solution**: Model trace caching is enabled - first load is slow, subsequent loads are fast

### Debug Mode

Enable debug output:
```bash
streamlit run dashboard/app.py --logger.level=debug
```

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! See CONTRIBUTING.md

## 📧 Support

- Issues: https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/issues
- Documentation: See `docs/` folder

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by PyMC (Bayesian modeling)
- Inspired by modern data science best practices

---

**Version**: 1.0.0
**Last Updated**: 2025-01-20
