"""
Business Strategy Development Framework for Airbnb Market Analysis
- Focus on disadvantaged neighborhoods with high strategic potential
- Service investment calculator based on neighborhood effects
- Dynamic pricing recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from hierarchical_bayesian_model import HierarchicalBayesianPriceModel
import warnings

warnings.filterwarnings("ignore")


class BusinessStrategyFramework:
    def __init__(self, model_path, hierarchical_model=None):
        """Initialize with data and optionally a fitted hierarchical model."""
        self.model_path = model_path
        self.hierarchical_model = hierarchical_model
        self.strategy_data = None
        self.investment_opportunities = None

    def load_market_data(self):
        """Load and prepare market data for strategic analysis."""
        df = pd.read_csv(self.model_path)

        # Clean price data
        df["price_clean"] = (
            df["price"].str.replace("$", "").str.replace(",", "").astype(float)
        )
        df = df.dropna(subset=["price_clean", "accommodates", "neighbourhood_cleansed"])
        df = df[(df["price_clean"] >= 10) & (df["price_clean"] <= 1000)]

        self.strategy_data = df
        return df

    def identify_strategic_neighborhoods(self):
        """Identify disadvantaged neighborhoods with high strategic potential."""

        if self.strategy_data is None:
            self.load_market_data()

        # Calculate neighborhood-level metrics
        neighborhood_metrics = (
            self.strategy_data.groupby("neighbourhood_cleansed")
            .agg(
                {
                    "price_clean": ["mean", "median", "std", "count"],
                    "accommodates": ["mean", "median"],
                    "number_of_reviews": ["mean", "median", "sum"],
                    "review_scores_rating": ["mean", "count"],
                    "availability_365": ["mean"],
                    "calculated_host_listings_count": ["mean"],
                }
            )
            .round(2)
        )

        # Flatten column names
        neighborhood_metrics.columns = [
            f"{col[0]}_{col[1]}" for col in neighborhood_metrics.columns
        ]
        neighborhood_metrics = neighborhood_metrics.reset_index()

        # Calculate strategic potential indicators

        # 1. Market Penetration (inverse of listing density - opportunity for growth)
        neighborhood_metrics["market_penetration_score"] = (
            1
            / (
                neighborhood_metrics["price_clean_count"] + 1
            )  # +1 to avoid division by zero
        ) * 100

        # 2. Price Growth Potential (low current prices but decent reviews)
        price_percentile = neighborhood_metrics["price_clean_mean"].rank(pct=True)
        rating_percentile = neighborhood_metrics["review_scores_rating_mean"].rank(
            pct=True
        )

        neighborhood_metrics["price_growth_potential"] = (
            (1 - price_percentile) * 0.7 + rating_percentile * 0.3
        ) * 100

        # 3. Supply Gap (high availability suggests undersupply)
        availability_percentile = neighborhood_metrics["availability_365_mean"].rank(
            pct=True
        )
        neighborhood_metrics["supply_gap_score"] = availability_percentile * 100

        # 4. Host Concentration (low concentration = opportunity for new hosts)
        host_concentration = neighborhood_metrics[
            "calculated_host_listings_count_mean"
        ].rank(pct=True)
        neighborhood_metrics["host_opportunity_score"] = (1 - host_concentration) * 100

        # 5. Review Activity (proxy for market activity)
        review_activity = neighborhood_metrics["number_of_reviews_sum"].rank(pct=True)
        neighborhood_metrics["market_activity_score"] = review_activity * 100

        # Composite Strategic Potential Score
        neighborhood_metrics["strategic_potential_score"] = (
            neighborhood_metrics["market_penetration_score"] * 0.25
            + neighborhood_metrics["price_growth_potential"] * 0.25
            + neighborhood_metrics["supply_gap_score"] * 0.20
            + neighborhood_metrics["host_opportunity_score"] * 0.15
            + neighborhood_metrics["market_activity_score"] * 0.15
        )

        # Identify disadvantaged neighborhoods (below median price but above median potential)
        median_price = neighborhood_metrics["price_clean_mean"].median()
        median_potential = neighborhood_metrics["strategic_potential_score"].median()

        neighborhood_metrics["is_strategic_opportunity"] = (
            neighborhood_metrics["price_clean_mean"] < median_price
        ) & (neighborhood_metrics["strategic_potential_score"] > median_potential)

        # Add investment priority ranking
        neighborhood_metrics["investment_priority"] = (
            neighborhood_metrics["strategic_potential_score"]
            .rank(ascending=False, method="dense")
            .astype(int)
        )

        self.investment_opportunities = neighborhood_metrics.sort_values(
            "strategic_potential_score", ascending=False
        )

        return self.investment_opportunities

    def calculate_service_investment_roi(
        self,
        neighborhood_name,
        investment_amount,
        expected_price_increase_pct=15,
        expected_occupancy_increase_pct=10,
    ):
        """Calculate ROI for service investments in specific neighborhoods."""

        if self.investment_opportunities is None:
            self.identify_strategic_neighborhoods()

        # Get neighborhood data
        neighborhood_data = self.investment_opportunities[
            self.investment_opportunities["neighbourhood_cleansed"] == neighborhood_name
        ]

        if neighborhood_data.empty:
            return None

        neighborhood_stats = neighborhood_data.iloc[0]

        # Current market conditions
        current_price = neighborhood_stats["price_clean_mean"]
        current_listings = neighborhood_stats["price_clean_count"]
        avg_reviews = neighborhood_stats["number_of_reviews_mean"]
        avg_availability = neighborhood_stats["availability_365_mean"]

        # Estimate current occupancy rate (inverse of availability)
        current_occupancy_rate = max(0.1, (365 - avg_availability) / 365)

        # Calculate baseline annual revenue per listing
        baseline_annual_revenue = current_price * 365 * current_occupancy_rate

        # Post-investment projections
        improved_price = current_price * (1 + expected_price_increase_pct / 100)
        improved_occupancy = min(
            0.95, current_occupancy_rate * (1 + expected_occupancy_increase_pct / 100)
        )
        improved_annual_revenue = improved_price * 365 * improved_occupancy

        # Revenue improvement per listing
        revenue_increase_per_listing = improved_annual_revenue - baseline_annual_revenue

        # Market penetration potential
        penetration_score = neighborhood_stats["market_penetration_score"]
        estimated_new_listings = max(
            1, int(current_listings * (penetration_score / 100))
        )

        # Total market impact
        total_revenue_increase = revenue_increase_per_listing * (
            current_listings + estimated_new_listings
        )

        # ROI calculation (assuming 3-year investment horizon)
        investment_horizon_years = 3
        total_benefit = total_revenue_increase * investment_horizon_years
        roi_percentage = ((total_benefit - investment_amount) / investment_amount) * 100

        # Risk adjustment based on neighborhood characteristics
        risk_factors = {
            "low_review_activity": avg_reviews < 10,
            "high_availability": avg_availability > 300,
            "low_listing_count": current_listings < 5,
        }

        risk_score = sum(risk_factors.values()) / len(risk_factors)
        risk_adjusted_roi = roi_percentage * (
            1 - risk_score * 0.3
        )  # Reduce by up to 30% for high risk

        return {
            "neighborhood": neighborhood_name,
            "investment_amount": investment_amount,
            "baseline_annual_revenue_per_listing": baseline_annual_revenue,
            "improved_annual_revenue_per_listing": improved_annual_revenue,
            "revenue_increase_per_listing": revenue_increase_per_listing,
            "current_listings": current_listings,
            "estimated_new_listings": estimated_new_listings,
            "total_revenue_increase_annual": total_revenue_increase,
            "total_benefit_3yr": total_benefit,
            "roi_percentage": roi_percentage,
            "risk_score": risk_score,
            "risk_adjusted_roi": risk_adjusted_roi,
            "strategic_potential_score": neighborhood_stats[
                "strategic_potential_score"
            ],
            "investment_recommendation": (
                "STRONG BUY"
                if risk_adjusted_roi > 50
                else (
                    "BUY"
                    if risk_adjusted_roi > 25
                    else "HOLD" if risk_adjusted_roi > 10 else "AVOID"
                )
            ),
        }

    def create_dynamic_pricing_strategy(self, neighborhood_name=None):
        """Create dynamic pricing recommendations based on neighborhood effects."""

        if self.hierarchical_model is None or self.hierarchical_model.trace is None:
            print("Hierarchical model not available. Loading and fitting...")
            self.hierarchical_model = HierarchicalBayesianPriceModel(self.model_path)
            self.hierarchical_model.load_and_clean_data()
            self.hierarchical_model.build_hierarchical_model()
            self.hierarchical_model.fit_model(samples=500, tune=250, chains=2)

        # Extract neighborhood effects from Bayesian model
        alpha_samples = self.hierarchical_model.trace.posterior["alpha"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )
        beta_samples = self.hierarchical_model.trace.posterior["beta"].values.reshape(
            -1, self.hierarchical_model.n_neighborhoods
        )

        # Calculate pricing strategies for each neighborhood
        pricing_strategies = []

        for i, neighborhood in enumerate(self.hierarchical_model.neighborhoods):
            if neighborhood_name and neighborhood != neighborhood_name:
                continue

            # Neighborhood-specific parameters
            alpha_mean = alpha_samples[:, i].mean()
            alpha_std = alpha_samples[:, i].std()
            beta_mean = beta_samples[:, i].mean()
            beta_std = beta_samples[:, i].std()

            # Dynamic pricing recommendations for different scenarios
            accommodates_range = range(1, 9)  # 1 to 8 guests

            for guests in accommodates_range:
                # Base price prediction
                log_price_pred = alpha_mean + beta_mean * guests
                base_price = np.exp(log_price_pred)

                # Uncertainty bounds
                log_price_lower = (alpha_mean - alpha_std) + (
                    beta_mean - beta_std
                ) * guests
                log_price_upper = (alpha_mean + alpha_std) + (
                    beta_mean + beta_std
                ) * guests

                price_lower = np.exp(log_price_lower)
                price_upper = np.exp(log_price_upper)

                # Dynamic pricing strategy
                strategy = {
                    "neighborhood": neighborhood,
                    "accommodates": guests,
                    "base_price": base_price,
                    "price_range_lower": price_lower,
                    "price_range_upper": price_upper,
                    "recommended_price": base_price,
                    "high_demand_price": price_upper
                    * 0.9,  # Use 90% of upper bound for high demand
                    "low_demand_price": price_lower
                    * 1.1,  # Use 110% of lower bound for low demand
                    "price_elasticity": abs(
                        beta_mean
                    ),  # Higher beta = more sensitive to group size
                    "pricing_confidence": 1
                    / (alpha_std + beta_std),  # Lower uncertainty = higher confidence
                }

                # Seasonal adjustments (simplified)
                strategy["summer_premium"] = base_price * 1.15
                strategy["winter_discount"] = base_price * 0.85
                strategy["weekend_premium"] = base_price * 1.10
                strategy["weekday_standard"] = base_price

                pricing_strategies.append(strategy)

        pricing_df = pd.DataFrame(pricing_strategies)
        return pricing_df

    def generate_investment_dashboard(self, top_n=10):
        """Generate comprehensive investment opportunity dashboard."""

        if self.investment_opportunities is None:
            self.identify_strategic_neighborhoods()

        # Create visualization dashboard
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))

        # Plot 1: Strategic Potential vs Current Price
        top_opportunities = self.investment_opportunities.head(top_n)

        scatter = axes[0, 0].scatter(
            self.investment_opportunities["price_clean_mean"],
            self.investment_opportunities["strategic_potential_score"],
            c=self.investment_opportunities["investment_priority"],
            cmap="viridis_r",
            alpha=0.7,
            s=60,
        )

        # Highlight strategic opportunities
        strategic_mask = self.investment_opportunities["is_strategic_opportunity"]
        axes[0, 0].scatter(
            self.investment_opportunities[strategic_mask]["price_clean_mean"],
            self.investment_opportunities[strategic_mask]["strategic_potential_score"],
            c="red",
            s=100,
            alpha=0.8,
            marker="*",
            label="Strategic Opportunities",
        )

        axes[0, 0].set_xlabel("Average Price ($)")
        axes[0, 0].set_ylabel("Strategic Potential Score")
        axes[0, 0].set_title("Investment Opportunity Map")
        axes[0, 0].legend()
        plt.colorbar(scatter, ax=axes[0, 0], label="Investment Priority")

        # Plot 2: Top Strategic Neighborhoods
        axes[0, 1].barh(
            range(top_n),
            top_opportunities["strategic_potential_score"].values,
            color="skyblue",
        )
        axes[0, 1].set_yticks(range(top_n))
        axes[0, 1].set_yticklabels(
            top_opportunities["neighbourhood_cleansed"].values, fontsize=8
        )
        axes[0, 1].set_xlabel("Strategic Potential Score")
        axes[0, 1].set_title(f"Top {top_n} Strategic Neighborhoods")

        # Plot 3: Price vs Market Activity
        axes[0, 2].scatter(
            self.investment_opportunities["price_clean_mean"],
            self.investment_opportunities["market_activity_score"],
            alpha=0.6,
            s=50,
        )
        axes[0, 2].set_xlabel("Average Price ($)")
        axes[0, 2].set_ylabel("Market Activity Score")
        axes[0, 2].set_title("Price vs Market Activity")

        # Plot 4: Supply Gap Analysis
        axes[1, 0].scatter(
            self.investment_opportunities["price_clean_count"],
            self.investment_opportunities["supply_gap_score"],
            alpha=0.6,
            s=50,
            c="orange",
        )
        axes[1, 0].set_xlabel("Current Listing Count")
        axes[1, 0].set_ylabel("Supply Gap Score")
        axes[1, 0].set_title("Market Supply Analysis")

        # Plot 5: ROI Heatmap for top neighborhoods
        sample_investments = [10000, 25000, 50000, 100000]
        sample_neighborhoods = (
            top_opportunities["neighbourhood_cleansed"].head(5).values
        )

        roi_matrix = []
        for neighborhood in sample_neighborhoods:
            roi_row = []
            for investment in sample_investments:
                roi_calc = self.calculate_service_investment_roi(
                    neighborhood, investment
                )
                roi_row.append(roi_calc["risk_adjusted_roi"] if roi_calc else 0)
            roi_matrix.append(roi_row)

        im = axes[1, 1].imshow(roi_matrix, cmap="RdYlGn", aspect="auto")
        axes[1, 1].set_xticks(range(len(sample_investments)))
        axes[1, 1].set_xticklabels([f"${x/1000:.0f}K" for x in sample_investments])
        axes[1, 1].set_yticks(range(len(sample_neighborhoods)))
        axes[1, 1].set_yticklabels(sample_neighborhoods, fontsize=8)
        axes[1, 1].set_xlabel("Investment Amount")
        axes[1, 1].set_ylabel("Neighborhood")
        axes[1, 1].set_title("ROI Heatmap (%)")
        plt.colorbar(im, ax=axes[1, 1], label="Risk-Adjusted ROI (%)")

        # Add ROI values as text
        for i in range(len(sample_neighborhoods)):
            for j in range(len(sample_investments)):
                text = axes[1, 1].text(
                    j,
                    i,
                    f"{roi_matrix[i][j]:.0f}%",
                    ha="center",
                    va="center",
                    color="black",
                    fontsize=8,
                )

        # Plot 6: Investment Priority Distribution
        priority_counts = (
            self.investment_opportunities["investment_priority"].value_counts().head(10)
        )
        axes[1, 2].bar(
            range(len(priority_counts)), priority_counts.values, color="lightcoral"
        )
        axes[1, 2].set_xlabel("Investment Priority Rank")
        axes[1, 2].set_ylabel("Count of Neighborhoods")
        axes[1, 2].set_title("Investment Priority Distribution")

        plt.tight_layout()
        plt.savefig(
            "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/business_strategy_dashboard.png",
            dpi=300,
            bbox_inches="tight",
        )
        print("Dashboard saved as 'business_strategy_dashboard.png'")

        plt.show()

        return top_opportunities


def main():
    """Main execution function for business strategy analysis."""

    # Initialize business strategy framework
    strategy = BusinessStrategyFramework(
        "/home/dennisjcarroll/Desktop/Bayesian Profolio piece/listings.csv"
    )

    print("=== BUSINESS STRATEGY ANALYSIS ===\n")

    # 1. Identify strategic neighborhoods
    print("1. Identifying strategic neighborhoods...")
    opportunities = strategy.identify_strategic_neighborhoods()

    print(f"\nTop 10 Strategic Investment Opportunities:")
    top_10 = opportunities.head(10)[
        [
            "neighbourhood_cleansed",
            "price_clean_mean",
            "strategic_potential_score",
            "investment_priority",
            "is_strategic_opportunity",
        ]
    ]
    print(top_10.to_string(index=False))

    # 2. Service investment ROI analysis
    print("\n\n2. Service Investment ROI Analysis...")
    sample_neighborhoods = opportunities["neighbourhood_cleansed"].head(5).values

    for neighborhood in sample_neighborhoods:
        roi_analysis = strategy.calculate_service_investment_roi(neighborhood, 50000)
        if roi_analysis:
            print(f"\n{neighborhood}:")
            print(f"  Investment: ${roi_analysis['investment_amount']:,}")
            print(f"  Risk-Adjusted ROI: {roi_analysis['risk_adjusted_roi']:.1f}%")
            print(f"  Recommendation: {roi_analysis['investment_recommendation']}")
            print(
                f"  Revenue increase per listing: ${roi_analysis['revenue_increase_per_listing']:,.0f}/year"
            )

    # 3. Dynamic pricing strategy
    print("\n\n3. Dynamic Pricing Analysis...")
    pricing_strategy = strategy.create_dynamic_pricing_strategy()

    # Show pricing for top neighborhood
    top_neighborhood = opportunities.iloc[0]["neighbourhood_cleansed"]
    neighborhood_pricing = pricing_strategy[
        pricing_strategy["neighborhood"] == top_neighborhood
    ]

    if not neighborhood_pricing.empty:
        print(f"\nDynamic Pricing Strategy for {top_neighborhood}:")
        print(
            neighborhood_pricing[
                [
                    "accommodates",
                    "recommended_price",
                    "high_demand_price",
                    "low_demand_price",
                ]
            ].to_string(index=False)
        )

    # 4. Generate comprehensive dashboard
    print("\n\n4. Generating investment dashboard...")
    dashboard_data = strategy.generate_investment_dashboard()

    return strategy


if __name__ == "__main__":
    strategy_framework = main()
