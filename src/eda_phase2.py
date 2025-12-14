import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings("ignore")

# Load cleaned data from Phase 1
print("Loading cleaned data...")
listings = pd.read_csv("listings.csv")
neighbourhoods = pd.read_csv("neighbourhoods.csv")

# Clean price data (from Phase 1)
listings["price_clean"] = listings["price"].str.replace("$", "").str.replace(",", "")
listings["price_numeric"] = pd.to_numeric(listings["price_clean"], errors="coerce")
listings = listings[listings["price_numeric"] > 0]
listings = listings[listings["price_numeric"] < 1000]
listings["log_price"] = np.log(listings["price_numeric"])

# =============================================
# PHASE 2: UNVEILING RELATIONSHIPS
# =============================================

print("\n" + "=" * 50)
print("PHASE 2: UNVEILING RELATIONSHIPS")
print("=" * 50)

# 2.1 Geographic Analysis - Neighborhood Effects
print("\n2.1 Geographic Analysis - Neighborhood Effects")
print("-" * 45)

# Calculate neighborhood-level statistics
neighborhood_stats = (
    listings.groupby("neighbourhood_cleansed")
    .agg(
        {
            "price_numeric": ["mean", "median", "std", "count"],
            "log_price": ["mean", "std"],
        }
    )
    .round(2)
)

# Flatten column names
neighborhood_stats.columns = [
    "price_mean",
    "price_median",
    "price_std",
    "count",
    "log_price_mean",
    "log_price_std",
]
neighborhood_stats = neighborhood_stats.reset_index()

# Calculate city-wide averages
city_avg_price = listings["price_numeric"].mean()
city_avg_log_price = listings["log_price"].mean()

# Calculate neighborhood effects (preliminary)
neighborhood_stats["price_effect"] = neighborhood_stats["price_mean"] - city_avg_price
neighborhood_stats["log_price_effect"] = (
    neighborhood_stats["log_price_mean"] - city_avg_log_price
)

# Sort by effect size
neighborhood_stats = neighborhood_stats.sort_values("price_effect", ascending=False)

print(f"City-wide average price: ${city_avg_price:.2f}")
print(f"Number of neighborhoods: {len(neighborhood_stats)}")
print(f"\nTop 10 highest-priced neighborhoods:")
print(
    neighborhood_stats[
        ["neighbourhood_cleansed", "price_mean", "price_effect", "count"]
    ].head(10)
)

print(f"\nBottom 10 lowest-priced neighborhoods:")
print(
    neighborhood_stats[
        ["neighbourhood_cleansed", "price_mean", "price_effect", "count"]
    ].tail(10)
)

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Neighborhood price effects
top_15 = neighborhood_stats.head(15)
bottom_15 = neighborhood_stats.tail(15)
extreme_neighborhoods = pd.concat([top_15, bottom_15])

axes[0, 0].barh(
    range(len(extreme_neighborhoods)), extreme_neighborhoods["price_effect"]
)
axes[0, 0].set_yticks(range(len(extreme_neighborhoods)))
axes[0, 0].set_yticklabels(extreme_neighborhoods["neighbourhood_cleansed"], fontsize=8)
axes[0, 0].set_xlabel("Price Effect ($)")
axes[0, 0].set_title("Neighborhood Price Effects (Top/Bottom 15)")
axes[0, 0].axvline(x=0, color="red", linestyle="--", alpha=0.7)

# Sample size distribution
axes[0, 1].hist(neighborhood_stats["count"], bins=20, edgecolor="black", alpha=0.7)
axes[0, 1].set_xlabel("Number of Listings")
axes[0, 1].set_ylabel("Number of Neighborhoods")
axes[0, 1].set_title("Sample Size Distribution by Neighborhood")

# Price vs sample size
axes[1, 0].scatter(
    neighborhood_stats["count"], neighborhood_stats["price_mean"], alpha=0.6
)
axes[1, 0].set_xlabel("Number of Listings")
axes[1, 0].set_ylabel("Average Price ($)")
axes[1, 0].set_title("Price vs Sample Size by Neighborhood")

# Box plot of prices by top neighborhoods
top_neighborhoods = neighborhood_stats.head(10)["neighbourhood_cleansed"].tolist()
top_data = listings[listings["neighbourhood_cleansed"].isin(top_neighborhoods)]

sns.boxplot(data=top_data, x="neighbourhood_cleansed", y="price_numeric", ax=axes[1, 1])
axes[1, 1].set_xticklabels(axes[1, 1].get_xticklabels(), rotation=45, ha="right")
axes[1, 1].set_xlabel("Neighborhood")
axes[1, 1].set_ylabel("Price ($)")
axes[1, 1].set_title("Price Distribution: Top 10 Neighborhoods")

plt.tight_layout()
plt.savefig("phase2_neighborhood_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# 2.2 Accommodates Variable Analysis
print("\n2.2 Accommodates Variable Analysis")
print("-" * 35)

# Clean accommodates data
listings = listings[listings["accommodates"] <= 16]  # Remove extreme outliers

# Summary statistics
print("Accommodates summary:")
print(listings["accommodates"].describe())

# Price vs accommodates analysis
accommodate_stats = (
    listings.groupby("accommodates")
    .agg({"price_numeric": ["mean", "median", "std", "count"], "log_price": "mean"})
    .round(2)
)

accommodate_stats.columns = [
    "price_mean",
    "price_median",
    "price_std",
    "count",
    "log_price_mean",
]
accommodate_stats = accommodate_stats.reset_index()

print(f"\nPrice by accommodates:")
print(accommodate_stats)

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Price vs accommodates scatter
axes[0, 0].scatter(listings["accommodates"], listings["price_numeric"], alpha=0.3)
axes[0, 0].set_xlabel("Accommodates")
axes[0, 0].set_ylabel("Price ($)")
axes[0, 0].set_title("Price vs Accommodates")

# Log price vs accommodates
axes[0, 1].scatter(listings["accommodates"], listings["log_price"], alpha=0.3)
axes[0, 1].set_xlabel("Accommodates")
axes[0, 1].set_ylabel("Log Price")
axes[0, 1].set_title("Log Price vs Accommodates")

# Average price by accommodates
axes[1, 0].plot(
    accommodate_stats["accommodates"], accommodate_stats["price_mean"], "o-"
)
axes[1, 0].set_xlabel("Accommodates")
axes[1, 0].set_ylabel("Average Price ($)")
axes[1, 0].set_title("Average Price by Accommodates")

# Distribution of accommodates
axes[1, 1].hist(
    listings["accommodates"], bins=range(1, 17), edgecolor="black", alpha=0.7
)
axes[1, 1].set_xlabel("Accommodates")
axes[1, 1].set_ylabel("Frequency")
axes[1, 1].set_title("Distribution of Accommodates")

plt.tight_layout()
plt.savefig("phase2_accommodates_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# 2.3 Room Type Analysis
print("\n2.3 Room Type Analysis")
print("-" * 25)

# Room type distribution
room_type_counts = listings["room_type"].value_counts()
print("Room type distribution:")
print(room_type_counts)

# Price by room type
room_type_stats = (
    listings.groupby("room_type")
    .agg({"price_numeric": ["mean", "median", "std", "count"], "log_price": "mean"})
    .round(2)
)

room_type_stats.columns = [
    "price_mean",
    "price_median",
    "price_std",
    "count",
    "log_price_mean",
]
room_type_stats = room_type_stats.reset_index()

print(f"\nPrice by room type:")
print(room_type_stats)

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Room type distribution
axes[0, 0].pie(
    room_type_counts.values, labels=room_type_counts.index, autopct="%1.1f%%"
)
axes[0, 0].set_title("Room Type Distribution")

# Price by room type box plot
sns.boxplot(data=listings, x="room_type", y="price_numeric", ax=axes[0, 1])
axes[0, 1].set_xlabel("Room Type")
axes[0, 1].set_ylabel("Price ($)")
axes[0, 1].set_title("Price Distribution by Room Type")

# Room type by neighborhood (top 10 neighborhoods)
top_neighborhoods = neighborhood_stats.head(10)["neighbourhood_cleansed"].tolist()
top_data = listings[listings["neighbourhood_cleansed"].isin(top_neighborhoods)]

room_type_neighborhood = pd.crosstab(
    top_data["neighbourhood_cleansed"], top_data["room_type"], normalize="index"
)
room_type_neighborhood.plot(kind="bar", stacked=True, ax=axes[1, 0])
axes[1, 0].set_xlabel("Neighborhood")
axes[1, 0].set_ylabel("Proportion")
axes[1, 0].set_title("Room Type Mix by Neighborhood (Top 10)")
axes[1, 0].legend(title="Room Type")
axes[1, 0].tick_params(axis="x", rotation=45)

# Accommodates vs room type
sns.boxplot(data=listings, x="room_type", y="accommodates", ax=axes[1, 1])
axes[1, 1].set_xlabel("Room Type")
axes[1, 1].set_ylabel("Accommodates")
axes[1, 1].set_title("Accommodates by Room Type")

plt.tight_layout()
plt.savefig("phase2_room_type_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# 2.4 Reviews Analysis
print("\n2.4 Reviews Analysis")
print("-" * 20)

# Reviews distribution
print("Number of reviews summary:")
print(listings["number_of_reviews"].describe())

# Price vs reviews analysis
print(
    f"\nCorrelation between price and number of reviews: {listings['price_numeric'].corr(listings['number_of_reviews']):.3f}"
)

# Create review count categories
listings["review_category"] = pd.cut(
    listings["number_of_reviews"],
    bins=[0, 1, 10, 50, 100, 500],
    labels=["No reviews", "1-10", "11-50", "51-100", "100+"],
)

review_stats = (
    listings.groupby("review_category")
    .agg({"price_numeric": ["mean", "median", "count"]})
    .round(2)
)

review_stats.columns = ["price_mean", "price_median", "count"]
review_stats = review_stats.reset_index()

print(f"\nPrice by review category:")
print(review_stats)

# Visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Price vs reviews scatter
axes[0, 0].scatter(listings["number_of_reviews"], listings["price_numeric"], alpha=0.3)
axes[0, 0].set_xlabel("Number of Reviews")
axes[0, 0].set_ylabel("Price ($)")
axes[0, 0].set_title("Price vs Number of Reviews")

# Log scale version
axes[0, 1].scatter(listings["number_of_reviews"], listings["price_numeric"], alpha=0.3)
axes[0, 1].set_xlabel("Number of Reviews (log scale)")
axes[0, 1].set_ylabel("Price ($)")
axes[0, 1].set_xscale("log")
axes[0, 1].set_title("Price vs Number of Reviews (Log Scale)")

# Reviews distribution
axes[1, 0].hist(listings["number_of_reviews"], bins=50, edgecolor="black", alpha=0.7)
axes[1, 0].set_xlabel("Number of Reviews")
axes[1, 0].set_ylabel("Frequency")
axes[1, 0].set_title("Distribution of Number of Reviews")

# Price by review category
sns.boxplot(data=listings, x="review_category", y="price_numeric", ax=axes[1, 1])
axes[1, 1].set_xlabel("Review Category")
axes[1, 1].set_ylabel("Price ($)")
axes[1, 1].set_title("Price by Review Category")

plt.tight_layout()
plt.savefig("phase2_reviews_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

print("\nPhase 2 Complete!")

# Save processed data for next phases
listings.to_csv("listings_processed.csv", index=False)
neighborhood_stats.to_csv("neighborhood_stats.csv", index=False)
