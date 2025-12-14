"""
Prescriptive Pricing Engine Module
Convert statistical model into actionable pricing recommendations
"""

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")


class PrescriptivePricingEngine:
    """Convert statistical model into actionable pricing recommendations"""

    def __init__(self, bayesian_model, varying_slopes_analysis=None):
        """
        Args:
            bayesian_model: Your fitted HierarchicalBayesianPriceModel
            varying_slopes_analysis: VaryingSlopesAnalysis instance (optional)
        """
        self.model = bayesian_model
        self.slopes = varying_slopes_analysis
        self.data = bayesian_model.data

    def recommend_price(
        self, neighbourhood, accommodates, reviews=None, room_type=None
    ):
        """Generate price recommendation with uncertainty bands"""
        if neighbourhood not in self.model.neighborhood_lookup:
            return {
                "error": f"Neighborhood '{neighbourhood}' not found in model",
                "available_neighborhoods": list(self.model.neighborhood_lookup.keys()),
            }

        neighborhood_idx = self.model.neighborhood_lookup[neighbourhood]

        # Extract posterior samples
        alpha_samples = self.model.trace.posterior["alpha"].values.reshape(
            -1, self.model.n_neighborhoods
        )[:, neighborhood_idx]
        beta_samples = self.model.trace.posterior["beta"].values.reshape(
            -1, self.model.n_neighborhoods
        )[:, neighborhood_idx]
        sigma_samples = self.model.trace.posterior["sigma"].values.flatten()

        # Predict log price
        log_price_pred = alpha_samples + beta_samples * accommodates

        # Convert to price scale
        price_pred = np.exp(log_price_pred)

        # Add residual uncertainty for prediction interval
        price_with_uncertainty = np.random.lognormal(
            log_price_pred, sigma_samples[: len(log_price_pred)]
        )

        # Calculate statistics
        median_price = np.median(price_pred)
        mean_price = price_pred.mean()
        ci_90 = np.percentile(price_pred, [5, 95])
        ci_95 = np.percentile(price_pred, [2.5, 97.5])
        pi_90 = np.percentile(price_with_uncertainty, [5, 95])

        # Get neighborhood statistics
        neighborhood_data = self.data[
            self.data["neighbourhood_cleansed"] == neighbourhood
        ]
        neighborhood_avg = neighborhood_data["price_clean"].mean()
        similar_listings = neighborhood_data[
            neighborhood_data["accommodates"] == accommodates
        ]

        # Calculate competitive position
        if len(similar_listings) > 0:
            similar_avg = similar_listings["price_clean"].mean()
            similar_median = similar_listings["price_clean"].median()
            percentile_rank = (similar_listings["price_clean"] < median_price).mean()
        else:
            similar_avg = neighborhood_avg
            similar_median = neighborhood_avg
            percentile_rank = None

        # Generate rationale
        rationale = self._generate_rationale(
            neighbourhood,
            accommodates,
            median_price,
            neighborhood_avg,
            similar_avg,
            percentile_rank,
        )

        # Risk assessment
        risk_level = self._assess_risk(
            median_price, ci_90, len(similar_listings), neighborhood_data
        )

        # Recommendation tiers
        recommendation = {
            "neighborhood": neighbourhood,
            "accommodates": accommodates,
            "recommended_price": round(median_price, 2),
            "mean_price": round(mean_price, 2),
            "price_range_90_ci": [round(ci_90[0], 2), round(ci_90[1], 2)],
            "price_range_95_ci": [round(ci_95[0], 2), round(ci_95[1], 2)],
            "prediction_interval_90": [round(pi_90[0], 2), round(pi_90[1], 2)],
            "confidence": "high" if len(similar_listings) > 10 else "moderate",
            "competitive_position": {
                "neighborhood_avg": round(neighborhood_avg, 2),
                "similar_listings_avg": round(similar_avg, 2),
                "similar_listings_median": round(similar_median, 2),
                "n_similar_listings": len(similar_listings),
                "percentile_rank": (
                    round(percentile_rank * 100, 1) if percentile_rank else None
                ),
            },
            "pricing_strategy": {
                "conservative": round(ci_90[0], 2),
                "moderate": round(median_price, 2),
                "aggressive": round(ci_90[1], 2),
            },
            "rationale": rationale,
            "risk_assessment": risk_level,
        }

        return recommendation

    def _generate_rationale(
        self,
        neighbourhood,
        accommodates,
        recommended_price,
        neighborhood_avg,
        similar_avg,
        percentile_rank,
    ):
        """Generate human-readable rationale for pricing recommendation"""
        rationale = []

        # Neighborhood comparison
        diff_from_neighborhood = (
            (recommended_price - neighborhood_avg) / neighborhood_avg * 100
        )
        if abs(diff_from_neighborhood) < 5:
            rationale.append(
                f"Price is aligned with {neighbourhood} average (${neighborhood_avg:.0f})"
            )
        elif diff_from_neighborhood > 0:
            rationale.append(
                f"Price is {diff_from_neighborhood:.1f}% above {neighbourhood} average, justified by higher capacity"
            )
        else:
            rationale.append(
                f"Price is {abs(diff_from_neighborhood):.1f}% below {neighbourhood} average"
            )

        # Similar listings comparison
        diff_from_similar = (recommended_price - similar_avg) / similar_avg * 100
        if abs(diff_from_similar) < 10:
            rationale.append(
                f"Competitive with similar {accommodates}-guest listings (avg: ${similar_avg:.0f})"
            )
        elif diff_from_similar > 10:
            rationale.append(
                f"Premium pricing (+{diff_from_similar:.1f}%) vs. similar listings - ensure property justifies premium"
            )
        else:
            rationale.append(
                f"Value pricing ({diff_from_similar:.1f}%) vs. similar listings - may increase occupancy"
            )

        # Percentile rank
        if percentile_rank is not None:
            if percentile_rank > 0.75:
                rationale.append(
                    f"Positioned in top 25% of similar listings - premium strategy"
                )
            elif percentile_rank > 0.5:
                rationale.append(f"Mid-to-high range pricing within market segment")
            elif percentile_rank > 0.25:
                rationale.append(f"Mid-range pricing - balanced approach")
            else:
                rationale.append(f"Value pricing - competitive positioning")

        # Capacity insight
        if accommodates >= 6:
            rationale.append("Large capacity properties command premium in this market")
        elif accommodates <= 2:
            rationale.append(
                "Small properties have consistent pricing with lower variance"
            )

        return rationale

    def _assess_risk(self, median_price, ci_90, n_similar, neighborhood_data):
        """Assess pricing risk"""
        risk_factors = []

        # Uncertainty width
        ci_width = ci_90[1] - ci_90[0]
        relative_width = ci_width / median_price

        if relative_width > 0.5:
            risk_factors.append("High uncertainty: Wide confidence interval")
            risk_level = "high"
        elif relative_width > 0.3:
            risk_factors.append("Moderate uncertainty in price estimate")
            risk_level = "moderate"
        else:
            risk_factors.append("Low uncertainty: Tight confidence interval")
            risk_level = "low"

        # Sample size
        if n_similar < 5:
            risk_factors.append(
                f"Limited data: Only {n_similar} similar listings in neighborhood"
            )
            risk_level = "high"
        elif n_similar < 15:
            risk_factors.append(
                f"Moderate data: {n_similar} similar listings in neighborhood"
            )

        # Price level
        if median_price > 300:
            risk_factors.append(
                "High price point: May limit market size, ensure premium features"
            )

        return {"level": risk_level, "factors": risk_factors}

    def optimize_pricing_strategy(
        self, neighbourhood, accommodates, target_occupancy=0.75
    ):
        """
        Suggest optimal pricing strategy based on target occupancy
        """
        base_rec = self.recommend_price(neighbourhood, accommodates)

        if "error" in base_rec:
            return base_rec

        # Simulate different pricing strategies
        strategies = {
            "maximum_revenue": {
                "price": base_rec["pricing_strategy"]["moderate"],
                "expected_occupancy": 0.75,
                "description": "Balance price and occupancy for maximum revenue",
            },
            "high_occupancy": {
                "price": base_rec["pricing_strategy"]["conservative"],
                "expected_occupancy": 0.85,
                "description": "Lower price to maximize occupancy and reviews",
            },
            "premium": {
                "price": base_rec["pricing_strategy"]["aggressive"],
                "expected_occupancy": 0.60,
                "description": "Premium pricing for high-end market segment",
            },
        }

        # Calculate expected annual revenue for each strategy
        for strategy_name, strategy in strategies.items():
            annual_revenue = strategy["price"] * 365 * strategy["expected_occupancy"]
            strategy["annual_revenue"] = round(annual_revenue, 2)

        # Rank strategies by expected revenue
        ranked_strategies = sorted(
            strategies.items(), key=lambda x: x[1]["annual_revenue"], reverse=True
        )

        return {
            "neighborhood": neighbourhood,
            "accommodates": accommodates,
            "strategies": strategies,
            "recommended_strategy": ranked_strategies[0][0],
            "base_recommendation": base_rec,
        }

    def batch_recommendations(self, property_list):
        """
        Generate recommendations for multiple properties
        property_list: List of dicts with 'neighbourhood' and 'accommodates'
        """
        recommendations = []

        for prop in property_list:
            rec = self.recommend_price(prop["neighbourhood"], prop["accommodates"])
            recommendations.append(rec)

        return pd.DataFrame(recommendations)

    def competitive_analysis(self, neighbourhood, accommodates):
        """
        Analyze competitive landscape for a property
        """
        recommendation = self.recommend_price(neighbourhood, accommodates)

        if "error" in recommendation:
            return recommendation

        # Get all listings in neighborhood with same capacity
        competitors = self.data[
            (self.data["neighbourhood_cleansed"] == neighbourhood)
            & (self.data["accommodates"] == accommodates)
        ]

        if len(competitors) == 0:
            return {
                "error": f"No competitors found in {neighbourhood} with {accommodates} guests"
            }

        # Price distribution
        price_dist = {
            "min": competitors["price_clean"].min(),
            "25th": competitors["price_clean"].quantile(0.25),
            "median": competitors["price_clean"].median(),
            "75th": competitors["price_clean"].quantile(0.75),
            "max": competitors["price_clean"].max(),
            "mean": competitors["price_clean"].mean(),
            "std": competitors["price_clean"].std(),
        }

        # Market positioning
        recommended_price = recommendation["recommended_price"]

        if recommended_price < price_dist["25th"]:
            positioning = "Budget/Value"
        elif recommended_price < price_dist["median"]:
            positioning = "Lower Mid-Range"
        elif recommended_price < price_dist["75th"]:
            positioning = "Upper Mid-Range"
        else:
            positioning = "Premium/Luxury"

        return {
            "neighborhood": neighbourhood,
            "accommodates": accommodates,
            "n_competitors": len(competitors),
            "price_distribution": {k: round(v, 2) for k, v in price_dist.items()},
            "recommended_price": recommended_price,
            "market_positioning": positioning,
            "recommendation": recommendation,
        }
