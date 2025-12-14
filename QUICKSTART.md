# Seattle Airbnb Dashboard - Quick Start Guide

Welcome! This guide will get you up and running with the Seattle Airbnb Pricing & Investment Dashboard in under 5 minutes.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd /home/dennisjcarroll/Desktop/Dashboard-Attempt_1-airbnb-seattle-market

# Install all required packages
pip install -r requirements-dashboard.txt
```

**Note**: This may take 5-10 minutes as it installs PyMC and other scientific packages.

### Step 2: Verify Data Files

Make sure you have the data files:

```bash
ls data/raw/listings.csv
ls data/raw/neighbourhoods.csv
```

If these files don't exist, you'll need to download them from [Inside Airbnb](http://insideairbnb.com/get-the-data/).

### Step 3: Launch the Dashboard

```bash
streamlit run airbnb_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

**First Launch Note**: The first time you run the dashboard, it will:
1. Load the data (~3,800 listings)
2. Fit the Bayesian model (~2-3 minutes with default settings)
3. Cache everything for faster subsequent loads

Subsequent launches will be almost instant thanks to Streamlit's caching!

---

## 📊 What Can You Do?

### For Airbnb Hosts:

**💰 Price Predictor**
- Get price recommendations for your property
- See confidence intervals
- Compare to neighborhood averages
- Get actionable pricing advice

**⚙️ Feature Impact Calculator**
- Estimate value of adding amenities (parking, A/C, hot tub, etc.)
- Calculate ROI for improvements
- See payback periods

### For Investors:

**📊 Investment Analyzer**
- Evaluate ROI for different neighborhoods
- See cash-on-cash returns
- Analyze payback periods
- Understand risk factors

**🗺️ Neighborhood Comparison**
- Compare 2-5 neighborhoods side-by-side
- Identify high-value areas
- Find underserved markets

### For Data Analysts:

**✅ Model Validation**
- Test model accuracy on real data
- See calibration metrics (MAE, RMSE, MAPE)
- Understand model limitations

---

## 🎯 Example Use Cases

### Use Case 1: "What should I charge for my Capitol Hill apartment?"

1. Go to **💰 Price Predictor**
2. Select "Capitol Hill" from neighborhood dropdown
3. Set number of guests (e.g., 4)
4. Click "🔮 Predict Price"
5. Get: Recommended price with confidence interval, competitive analysis, risk assessment

### Use Case 2: "Should I invest in a Fremont property?"

1. Go to **📊 Investment Analyzer**
2. Select "Fremont" neighborhood
3. Set investment amount (e.g., $100,000)
4. Set property capacity (e.g., 4 guests)
5. Adjust assumptions (occupancy, costs, appreciation)
6. Click "📈 Analyze Investment"
7. Get: ROI projections, payback period, risk analysis

### Use Case 3: "Which neighborhood has the best pricing power?"

1. Go to **🗺️ Neighborhood Comparison**
2. Select neighborhoods (e.g., Capitol Hill, Fremont, Ballard)
3. Set property capacity
4. View side-by-side comparison with visualizations

---

## ⚡ Performance Tips

### Faster Initial Load

If you want faster initial loading (at the cost of some accuracy), edit `airbnb_dashboard.py` line 91:

**Fast Mode** (loads in ~1 minute):
```python
model.fit_model(samples=250, tune=125, chains=2)
```

**Default** (loads in ~2-3 minutes):
```python
model.fit_model(samples=500, tune=250, chains=2)
```

**Production Quality** (loads in ~8-10 minutes):
```python
model.fit_model(samples=2000, tune=1000, chains=4)
```

### Clear Cache

If the dashboard seems stuck or you want to retrain the model:
1. Click the hamburger menu (☰) in top right
2. Select "Clear cache"
3. Refresh the page

---

## 🐛 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pymc'"

**Solution**: Install dependencies
```bash
pip install -r requirements-dashboard.txt
```

### Problem: "FileNotFoundError: data/raw/listings.csv"

**Solution**: Make sure data files exist in the correct location:
```bash
mkdir -p data/raw
# Download files from Inside Airbnb
```

### Problem: "Dashboard is very slow"

**Solutions**:
1. Use "Fast Mode" (see Performance Tips above)
2. Clear cache and reload
3. Close other applications to free up memory

### Problem: "Can't connect to localhost:8501"

**Solution**: Check if Streamlit is running:
```bash
# Kill any existing Streamlit processes
pkill -f streamlit

# Restart
streamlit run airbnb_dashboard.py
```

---

## 📚 Next Steps

Once you're comfortable with the basics:

1. **Read the full documentation**: `DASHBOARD_README.md`
2. **Explore the code**: Start with `src/hierarchical_bayesian_model.py`
3. **Customize**: Add your own features or neighborhoods
4. **Deploy**: Host on Streamlit Cloud for free

---

## 📁 Project Structure (Simplified)

```
.
├── airbnb_dashboard.py          ← Main dashboard (run this!)
├── QUICKSTART.md                 ← You are here
├── DASHBOARD_README.md           ← Full documentation
├── requirements-dashboard.txt    ← Dependencies
├── src/                          ← Analysis modules
│   ├── hierarchical_bayesian_model.py
│   ├── baseline_comparison.py
│   ├── varying_slopes_analysis.py
│   └── prescriptive_pricing.py
└── data/raw/                     ← Data files
    ├── listings.csv
    └── neighbourhoods.csv
```

---

## ✅ Checklist

Before using the dashboard:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements-dashboard.txt`)
- [ ] Data files present (`data/raw/listings.csv` and `neighbourhoods.csv`)
- [ ] Dashboard launched (`streamlit run airbnb_dashboard.py`)
- [ ] Browser opened to `http://localhost:8501`

---

## 🎉 You're Ready!

The dashboard should now be running. Try exploring the different pages:

1. **🏠 Home** - Get overview and stats
2. **💰 Price Predictor** - Get price recommendations
3. **📊 Investment Analyzer** - Evaluate investments
4. **🗺️ Neighborhood Comparison** - Compare areas
5. **✅ Model Validation** - Check model accuracy
6. **⚙️ Feature Impact** - Calculate feature value

**Need help?** Check `DASHBOARD_README.md` for detailed documentation.

**Found a bug?** Check the Troubleshooting section above.

Happy analyzing! 🚀📊
