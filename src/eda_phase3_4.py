import pandas as pd
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# Load and clean data
print("Loading and cleaning data...")
listings = pd.read_csv("listings.csv")
listings["price_clean"] = listings["price"].str.replace("$", "").str.replace(",", "")
listings["price_numeric"] = pd.to_numeric(listings["price_clean"], errors="coerce")
listings = listings[listings["price_numeric"] > 0]
listings = listings[listings["price_numeric"] < 1000]
listings["log_price"] = np.log(listings["price_numeric"])

# =============================================
# PHASE 3: HIERARCHICAL STRUCTURE PREPARATION
# =============================================

print("\n" + "=" * 50)
print("PHASE 3: HIERARCHICAL STRUCTURE PREPARATION")
print("=" * 50)

# 3.1 Sample Size Analysis by Group
print("\n3.1 Sample Size Analysis by Group")
print("-" * 35)

# Calculate sample sizes by neighborhood
neighborhood_counts = (
    listings["neighbourhood_cleansed"].value_counts().sort_values(ascending=False)
)
print(f"Total neighborhoods: {len(neighborhood_counts)}")
print(f"Total listings: {len(listings)}")


# Categorize neighborhoods by sample size
def categorize_sample_size(count):
    if count >= 100:
        return "Data-rich (100+)"
    elif count >= 20:
        return "Moderate (20-99)"
    else:
        return "Sparse (<20)"


neighborhood_categories = neighborhood_counts.apply(categorize_sample_size)
category_counts = neighborhood_categories.value_counts()

print(f"\nNeighborhood categories by sample size:")
for category, count in category_counts.items():
    pct = (count / len(neighborhood_counts)) * 100
    total_listings = neighborhood_counts[neighborhood_categories == category].sum()
    listing_pct = (total_listings / len(listings)) * 100
    print(
        f"{category}: {count} neighborhoods ({pct:.1f}%), {total_listings} listings ({listing_pct:.1f}%)"
    )

# Top and bottom neighborhoods by sample size
print(f"\nTop 10 neighborhoods by sample size:")
for i, (neighborhood, count) in enumerate(neighborhood_counts.head(10).items(), 1):
    print(f"{i:2d}. {neighborhood}: {count} listings")

print(f"\nBottom 10 neighborhoods by sample size:")
for i, (neighborhood, count) in enumerate(neighborhood_counts.tail(10).items(), 1):
    print(f"{i:2d}. {neighborhood}: {count} listings")

# 3.2 Variance Components Exploration
print("\n3.2 Variance Components Exploration")
print("-" * 35)

# Calculate variance components
city_mean = listings["log_price"].mean()
neighborhood_means = listings.groupby("neighbourhood_cleansed")["log_price"].mean()

# Between-neighborhood variance
between_var = np.var(neighborhood_means)

# Within-neighborhood variance (weighted by sample size)
within_var_components = []
for neighborhood in listings["neighbourhood_cleansed"].unique():
    neighborhood_data = listings[listings["neighbourhood_cleansed"] == neighborhood][
        "log_price"
    ]
    if len(neighborhood_data) > 1:
        within_var_components.append(np.var(neighborhood_data, ddof=1))

within_var = np.mean(within_var_components)

# Total variance
total_var = np.var(listings["log_price"], ddof=1)

# Intraclass correlation coefficient (ICC)
icc = between_var / (between_var + within_var)

print(f"Variance components analysis (log price):")
print(f"Between-neighborhood variance: {between_var:.4f}")
print(f"Within-neighborhood variance: {within_var:.4f}")
print(f"Total variance: {total_var:.4f}")
print(f"Intraclass correlation coefficient: {icc:.4f}")
print(f"Percentage of variance explained by neighborhoods: {icc*100:.1f}%")

# =============================================
# PHASE 4: MODEL PREPARATION INSIGHTS
# =============================================

print("\n" + "=" * 50)
print("PHASE 4: MODEL PREPARATION INSIGHTS")
print("=" * 50)

# 4.1 Transformation Validation
print("\n4.1 Transformation Validation")
print("-" * 30)

# Compare raw vs log price normality
raw_shapiro = stats.shapiro(listings["price_numeric"].sample(min(5000, len(listings))))
log_shapiro = stats.shapiro(listings["log_price"].sample(min(5000, len(listings))))

print(f"Normality tests (Shapiro-Wilk):")
print(f"Raw price p-value: {raw_shapiro.pvalue:.2e}")
print(f"Log price p-value: {log_shapiro.pvalue:.2e}")

# Skewness comparison
raw_skew = stats.skew(listings["price_numeric"])
log_skew = stats.skew(listings["log_price"])

print(f"\nSkewness comparison:")
print(f"Raw price skewness: {raw_skew:.3f}")
print(f"Log price skewness: {log_skew:.3f}")

# 4.2 Preliminary Model Intuition Building
print("\n4.2 Preliminary Model Intuition Building")
print("-" * 40)

# Simple linear regression benchmarks
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import LabelEncoder

# Prepare features
features_data = listings[
    ["accommodates", "number_of_reviews", "room_type", "neighbourhood_cleansed"]
].copy()
features_data = features_data.dropna()

# Encode categorical variables
le_room = LabelEncoder()
le_neighborhood = LabelEncoder()

features_data["room_type_encoded"] = le_room.fit_transform(features_data["room_type"])
features_data["neighborhood_encoded"] = le_neighborhood.fit_transform(
    features_data["neighbourhood_cleansed"]
)

# Get corresponding log prices
log_prices = listings.loc[features_data.index, "log_price"]

# Model 1: Without neighborhood effects
X1 = features_data[["accommodates", "number_of_reviews", "room_type_encoded"]]
model1 = LinearRegression()
model1.fit(X1, log_prices)
r2_1 = r2_score(log_prices, model1.predict(X1))

# Model 2: With neighborhood effects
X2 = features_data[
    ["accommodates", "number_of_reviews", "room_type_encoded", "neighborhood_encoded"]
]
model2 = LinearRegression()
model2.fit(X2, log_prices)
r2_2 = r2_score(log_prices, model2.predict(X2))

print(f"Preliminary model performance (R-squared):")
print(f"Without neighborhood effects: {r2_1:.3f}")
print(f"With neighborhood effects: {r2_2:.3f}")
print(f"Improvement from neighborhood effects: {r2_2 - r2_1:.3f}")

# Key findings summary
print("\n" + "=" * 50)
print("KEY FINDINGS SUMMARY")
print("=" * 50)

print(f"\n1. DATA STRUCTURE:")
print(f"   • {len(listings)} listings across {len(neighborhood_counts)} neighborhoods")
print(f"   • {category_counts.get('Data-rich (100+)', 0)} data-rich neighborhoods")
print(
    f"   • {category_counts.get('Sparse (<20)', 0)} sparse neighborhoods requiring hierarchical pooling"
)

print(f"\n2. HIERARCHICAL JUSTIFICATION:")
print(
    f"   • Intraclass correlation: {icc:.3f} ({icc*100:.1f}% variance from neighborhoods)"
)
print(f"   • Neighborhood effects add {r2_2 - r2_1:.3f} to model R-squared")
print(f"   • Strong case for hierarchical modeling")

print(f"\n3. TRANSFORMATION VALIDATION:")
print(f"   • Log transformation reduces skewness from {raw_skew:.2f} to {log_skew:.2f}")
print(f"   • Supports Gaussian likelihood assumption")

print(f"\n4. BUSINESS INSIGHTS:")
top_neighborhood = neighborhood_counts.index[0]
top_count = neighborhood_counts.iloc[0]
neighborhood_stats = (
    listings.groupby("neighbourhood_cleansed")["price_numeric"]
    .mean()
    .sort_values(ascending=False)
)
highest_price_neighborhood = neighborhood_stats.index[0]
highest_price = neighborhood_stats.iloc[0]
lowest_price_neighborhood = neighborhood_stats.index[-1]
lowest_price = neighborhood_stats.iloc[-1]

print(f"   • {top_neighborhood} has most listings ({top_count})")
print(f"   • {highest_price_neighborhood} has highest avg price (${highest_price:.0f})")
print(f"   • {lowest_price_neighborhood} has lowest avg price (${lowest_price:.0f})")
print(
    f"   • Price gap: ${highest_price - lowest_price:.0f} represents strategic opportunity"
)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Sample size distribution
axes[0, 0].hist(neighborhood_counts.values, bins=20, edgecolor="black", alpha=0.7)
axes[0, 0].set_xlabel("Number of Listings")
axes[0, 0].set_ylabel("Number of Neighborhoods")
axes[0, 0].set_title("Sample Size Distribution by Neighborhood")

# Variance components
var_components = ["Between\nNeighborhoods", "Within\nNeighborhoods"]
var_values = [between_var, within_var]
axes[0, 1].bar(var_components, var_values, alpha=0.7)
axes[0, 1].set_ylabel("Variance")
axes[0, 1].set_title("Variance Components (Log Price)")

# Price by neighborhood (top 15)
top_15_neighborhoods = neighborhood_stats.head(15)
axes[1, 0].barh(range(len(top_15_neighborhoods)), top_15_neighborhoods.values)
axes[1, 0].set_yticks(range(len(top_15_neighborhoods)))
axes[1, 0].set_yticklabels(top_15_neighborhoods.index, fontsize=8)
axes[1, 0].set_xlabel("Average Price ($)")
axes[1, 0].set_title("Top 15 Neighborhoods by Price")

# Model comparison
model_names = ["Without\nNeighborhoods", "With\nNeighborhoods"]
r2_values = [r2_1, r2_2]
axes[1, 1].bar(model_names, r2_values, alpha=0.7)
axes[1, 1].set_ylabel("R-squared")
axes[1, 1].set_title("Model Performance Comparison")

plt.tight_layout()
plt.savefig("phase3_4_analysis.png", dpi=300, bbox_inches="tight")
plt.close()

print(f"\n✓ Analysis complete! Visualizations saved to 'phase3_4_analysis.png'")
print(f"✓ Ready for hierarchical Bayesian modeling")
