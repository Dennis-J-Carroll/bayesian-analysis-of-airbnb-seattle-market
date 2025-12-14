"""
Varying Slopes Analysis Module
Extract and interpret neighborhood-specific accommodates effects
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class VaryingSlopesAnalysis:
    """Extract and interpret neighborhood-specific accommodates effects"""

    def __init__(self, fitted_model):
        """
        Args:
            fitted_model: Your existing HierarchicalBayesianPriceModel instance
                         (already fitted, with data loaded)
        """
        self.model = fitted_model
        self.data = fitted_model.data
        self.trace = fitted_model.trace

    def extract_neighborhood_effects(self):
        """Get varying slopes and intercepts by neighborhood"""
        # Extract posterior samples
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.model.n_neighborhoods
        )
        beta_samples = self.trace.posterior["beta"].values.reshape(
            -1, self.model.n_neighborhoods
        )

        # Calculate posterior means and credible intervals
        alpha_mean = alpha_samples.mean(axis=0)
        alpha_ci = np.percentile(alpha_samples, [2.5, 97.5], axis=0)

        beta_mean = beta_samples.mean(axis=0)
        beta_ci = np.percentile(beta_samples, [2.5, 97.5], axis=0)

        # Create results DataFrame
        results = []
        for i, neighborhood in enumerate(self.model.neighborhoods):
            # Get neighborhood-specific data
            neighborhood_data = self.data[
                self.data["neighbourhood_cleansed"] == neighborhood
            ]

            results.append(
                {
                    "neighborhood": neighborhood,
                    "alpha_mean": alpha_mean[i],
                    "alpha_ci_lower": alpha_ci[0][i],
                    "alpha_ci_upper": alpha_ci[1][i],
                    "beta_mean": beta_mean[i],
                    "beta_ci_lower": beta_ci[0][i],
                    "beta_ci_upper": beta_ci[1][i],
                    "n_listings": len(neighborhood_data),
                    "avg_price": neighborhood_data["price_clean"].mean(),
                    "avg_accommodates": neighborhood_data["accommodates"].mean(),
                }
            )

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values("beta_mean", ascending=False)

        return results_df

    def interpret_patterns(self, effects_df=None):
        """Interpret neighborhood-specific patterns"""
        if effects_df is None:
            effects_df = self.extract_neighborhood_effects()

        print("\n=== Neighborhood-Specific Pricing Patterns ===\n")

        # 1. Highest baseline prices (intercepts)
        print("TOP 5 NEIGHBORHOODS BY BASELINE PRICE:")
        top_baseline = effects_df.nlargest(5, "alpha_mean")
        for idx, row in top_baseline.iterrows():
            baseline_price = np.exp(row["alpha_mean"])
            print(f"  {row['neighborhood']}: ${baseline_price:.2f} (1 guest)")

        # 2. Highest price sensitivity to accommodates (slopes)
        print("\nTOP 5 NEIGHBORHOODS WITH HIGHEST CAPACITY PREMIUM:")
        top_slopes = effects_df.nlargest(5, "beta_mean")
        for idx, row in top_slopes.iterrows():
            per_guest_increase = np.exp(row["alpha_mean"] + row["beta_mean"]) - np.exp(
                row["alpha_mean"]
            )
            print(
                f"  {row['neighborhood']}: +${per_guest_increase:.2f} per additional guest"
            )

        # 3. Lowest price sensitivity (flat pricing)
        print("\nTOP 5 NEIGHBORHOODS WITH FLATTEST PRICING:")
        flat_pricing = effects_df.nsmallest(5, "beta_mean")
        for idx, row in flat_pricing.iterrows():
            per_guest_increase = np.exp(row["alpha_mean"] + row["beta_mean"]) - np.exp(
                row["alpha_mean"]
            )
            print(
                f"  {row['neighborhood']}: +${per_guest_increase:.2f} per additional guest"
            )

        # 4. Statistical significance of slopes
        effects_df["beta_significant"] = (effects_df["beta_ci_lower"] > 0) | (
            effects_df["beta_ci_upper"] < 0
        )
        pct_significant = effects_df["beta_significant"].mean()
        print(
            f"\n{pct_significant:.1%} of neighborhoods have statistically significant capacity effects (95% CI excludes 0)"
        )

        # 5. Relationship between baseline price and slope
        correlation = effects_df[["alpha_mean", "beta_mean"]].corr().iloc[0, 1]
        print(
            f"\nCorrelation between baseline price and capacity premium: {correlation:.3f}"
        )

        if correlation > 0.3:
            print("  → High-price neighborhoods also charge MORE per additional guest")
        elif correlation < -0.3:
            print(
                "  → High-price neighborhoods charge LESS per additional guest (flatter pricing)"
            )
        else:
            print("  → Baseline price and capacity premium are weakly related")

        return effects_df

    def visualize_neighborhood_effects(self, effects_df=None, save_path=None):
        """Create visualizations of neighborhood effects"""
        if effects_df is None:
            effects_df = self.extract_neighborhood_effects()

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Varying intercepts with uncertainty
        sorted_alpha = effects_df.sort_values("alpha_mean")
        y_pos = np.arange(len(sorted_alpha))

        axes[0, 0].errorbar(
            sorted_alpha["alpha_mean"],
            y_pos,
            xerr=[
                sorted_alpha["alpha_mean"] - sorted_alpha["alpha_ci_lower"],
                sorted_alpha["alpha_ci_upper"] - sorted_alpha["alpha_mean"],
            ],
            fmt="o",
            capsize=3,
            alpha=0.6,
        )
        axes[0, 0].set_xlabel("Log Price Intercept (Baseline)")
        axes[0, 0].set_ylabel("Neighborhood")
        axes[0, 0].set_title("Varying Intercepts by Neighborhood (95% CI)")
        axes[0, 0].set_yticks([])

        # 2. Varying slopes with uncertainty
        sorted_beta = effects_df.sort_values("beta_mean")
        y_pos = np.arange(len(sorted_beta))

        axes[0, 1].errorbar(
            sorted_beta["beta_mean"],
            y_pos,
            xerr=[
                sorted_beta["beta_mean"] - sorted_beta["beta_ci_lower"],
                sorted_beta["beta_ci_upper"] - sorted_beta["beta_mean"],
            ],
            fmt="s",
            capsize=3,
            alpha=0.6,
            color="red",
        )
        axes[0, 1].axvline(0, color="black", linestyle="--", alpha=0.3)
        axes[0, 1].set_xlabel("Accommodates Effect (Slope)")
        axes[0, 1].set_ylabel("Neighborhood")
        axes[0, 1].set_title("Varying Slopes for Accommodates (95% CI)")
        axes[0, 1].set_yticks([])

        # 3. Scatter: intercept vs slope
        axes[1, 0].scatter(
            effects_df["alpha_mean"],
            effects_df["beta_mean"],
            s=effects_df["n_listings"],
            alpha=0.6,
            c=effects_df["avg_price"],
            cmap="viridis",
        )
        axes[1, 0].set_xlabel("Intercept (Baseline Log Price)")
        axes[1, 0].set_ylabel("Slope (Accommodates Effect)")
        axes[1, 0].set_title("Relationship: Baseline Price vs. Capacity Premium")

        # Add correlation line
        z = np.polyfit(effects_df["alpha_mean"], effects_df["beta_mean"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(
            effects_df["alpha_mean"].min(), effects_df["alpha_mean"].max(), 100
        )
        axes[1, 0].plot(x_line, p(x_line), "r--", alpha=0.5, linewidth=2)

        # 4. Top neighborhoods by different metrics
        top_n = 10

        top_baseline = effects_df.nlargest(top_n, "alpha_mean")
        top_slope = effects_df.nlargest(top_n, "beta_mean")

        x = np.arange(top_n)
        width = 0.35

        axes[1, 1].barh(
            x,
            np.exp(top_baseline["alpha_mean"].values),
            width,
            label="Top Baseline Price",
            alpha=0.7,
        )
        axes[1, 1].set_xlabel("Price ($) for 1 Guest")
        axes[1, 1].set_yticks(x)
        axes[1, 1].set_yticklabels(top_baseline["neighborhood"].values, fontsize=8)
        axes[1, 1].set_title(f"Top {top_n} Neighborhoods by Baseline Price")
        axes[1, 1].invert_yaxis()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"\nVisualization saved to {save_path}")

        return fig

    def get_neighborhood_premium(self, neighborhood, accommodates=4):
        """Calculate pricing premium for a specific neighborhood"""
        if neighborhood not in self.model.neighborhood_lookup:
            print(f"Neighborhood '{neighborhood}' not found")
            return None

        neighborhood_idx = self.model.neighborhood_lookup[neighborhood]

        # Extract samples
        alpha_samples = self.trace.posterior["alpha"].values.reshape(
            -1, self.model.n_neighborhoods
        )[:, neighborhood_idx]
        beta_samples = self.trace.posterior["beta"].values.reshape(
            -1, self.model.n_neighborhoods
        )[:, neighborhood_idx]

        # Grand means (population-level effects)
        mu_alpha = self.trace.posterior["mu_alpha"].values.flatten().mean()
        mu_beta = self.trace.posterior["mu_beta"].values.flatten().mean()

        # Neighborhood-specific prediction
        log_price_neighborhood = alpha_samples + beta_samples * accommodates
        price_neighborhood = np.exp(log_price_neighborhood)

        # Population-level prediction
        log_price_population = mu_alpha + mu_beta * accommodates
        price_population = np.exp(log_price_population)

        # Calculate premium
        premium = price_neighborhood.mean() - price_population
        premium_pct = (premium / price_population) * 100

        print(f"\n=== Pricing Analysis: {neighborhood} ({accommodates} guests) ===")
        print(f"Neighborhood price: ${price_neighborhood.mean():.2f}")
        print(f"City-wide average: ${price_population:.2f}")
        print(f"Premium: ${premium:.2f} ({premium_pct:+.1f}%)")

        return {
            "neighborhood": neighborhood,
            "accommodates": accommodates,
            "neighborhood_price": price_neighborhood.mean(),
            "population_price": price_population,
            "premium": premium,
            "premium_pct": premium_pct,
        }

    def compare_neighborhoods(self, neighborhoods_list, accommodates=4):
        """Compare multiple neighborhoods side-by-side"""
        results = []

        for neighborhood in neighborhoods_list:
            premium_data = self.get_neighborhood_premium(neighborhood, accommodates)
            if premium_data:
                results.append(premium_data)

        comparison_df = pd.DataFrame(results)
        comparison_df = comparison_df.sort_values("premium_pct", ascending=False)

        print("\n=== Neighborhood Comparison ===")
        print(
            comparison_df[
                ["neighborhood", "neighborhood_price", "premium", "premium_pct"]
            ].to_string(index=False)
        )

        return comparison_df
