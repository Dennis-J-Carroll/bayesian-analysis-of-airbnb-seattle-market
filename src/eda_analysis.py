import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# Set style
plt.style.use("default")
sns.set_palette("husl")

# Load the merged data
print("Loading and merging datasets...")
listings = pd.read_csv("listings.csv")
calendar = pd.read_csv("calendar.csv")
reviews = pd.read_csv("reviews (1).csv")
neighbourhoods = pd.read_csv("neighbourhoods.csv")

print(
    f"Loaded {len(listings)} listings, {len(calendar)} calendar entries, {len(reviews)} reviews"
)

# =============================================
# PHASE 1: FOUNDATION - DATA RECONNAISSANCE
# =============================================

print("\n" + "=" * 50)
print("PHASE 1: FOUNDATION - DATA RECONNAISSANCE")
print("=" * 50)

# 1.1 Dataset Structure Analysis
print("\n1.1 Dataset Structure Analysis")
print("-" * 30)
print(f"Listings shape: {listings.shape}")
print(f"Calendar shape: {calendar.shape}")
print(f"Reviews shape: {reviews.shape}")
print(f"Neighbourhoods shape: {neighbourhoods.shape}")

# Check missing values for key variables
key_vars = [
    "id",
    "name",
    "neighbourhood_cleansed",
    "room_type",
    "accommodates",
    "price",
    "number_of_reviews",
    "review_scores_rating",
]
print("\nMissing values in key variables:")
for var in key_vars:
    if var in listings.columns:
        missing_pct = (listings[var].isnull().sum() / len(listings)) * 100
        print(f"{var}: {missing_pct:.1f}%")

# 1.2 Target Variable Deep Dive - Price Analysis
print("\n1.2 Target Variable Deep Dive - Price Analysis")
print("-" * 45)

# Clean price data
listings["price_clean"] = listings["price"].str.replace("$", "").str.replace(",", "")
listings["price_numeric"] = pd.to_numeric(listings["price_clean"], errors="coerce")

# Remove invalid prices
listings = listings[listings["price_numeric"] > 0]
listings = listings[listings["price_numeric"] < 1000]  # Remove extreme outliers

print(f"Price statistics:")
print(f"Mean: ${listings['price_numeric'].mean():.2f}")
print(f"Median: ${listings['price_numeric'].median():.2f}")
print(f"Std: ${listings['price_numeric'].std():.2f}")
print(f"Min: ${listings['price_numeric'].min():.2f}")
print(f"Max: ${listings['price_numeric'].max():.2f}")

# Create log price
listings["log_price"] = np.log(listings["price_numeric"])

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Raw price distribution
axes[0, 0].hist(listings["price_numeric"], bins=50, edgecolor="black", alpha=0.7)
axes[0, 0].set_title("Raw Price Distribution")
axes[0, 0].set_xlabel("Price ($)")
axes[0, 0].set_ylabel("Frequency")

# Log price distribution
axes[0, 1].hist(listings["log_price"], bins=50, edgecolor="black", alpha=0.7)
axes[0, 1].set_title("Log Price Distribution")
axes[0, 1].set_xlabel("Log Price")
axes[0, 1].set_ylabel("Frequency")

# Q-Q plot for raw price
stats.probplot(listings["price_numeric"], dist="norm", plot=axes[1, 0])
axes[1, 0].set_title("Q-Q Plot: Raw Price")

# Q-Q plot for log price
stats.probplot(listings["log_price"], dist="norm", plot=axes[1, 1])
axes[1, 1].set_title("Q-Q Plot: Log Price")

plt.tight_layout()
plt.savefig("phase1_price_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# Test for normality
shapiro_raw = stats.shapiro(listings["price_numeric"].sample(5000))
shapiro_log = stats.shapiro(listings["log_price"].sample(5000))
print(f"\nShapiro-Wilk test (sample of 5000):")
print(f"Raw price p-value: {shapiro_raw.pvalue:.2e}")
print(f"Log price p-value: {shapiro_log.pvalue:.2e}")

print(f"\nPrice transformation validation:")
print(f"Raw price skewness: {stats.skew(listings['price_numeric']):.3f}")
print(f"Log price skewness: {stats.skew(listings['log_price']):.3f}")

print("\nPhase 1 Complete!")
