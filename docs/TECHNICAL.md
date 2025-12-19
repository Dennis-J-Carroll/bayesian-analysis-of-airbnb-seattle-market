# Technical Documentation

## Model Architecture

### Mathematical Specification

The enhanced hierarchical Bayesian model uses a log-normal likelihood with varying effects:

```python
log(price) ~ Normal(μ, σ)

μ = α[neighborhood, property_type]
    + β_accommodates[neighborhood] × accommodates_std
    + β_amenities × amenity_score_std
    + β_reviews × log(1 + number_of_reviews)
```

### Hierarchical Structure

**Varying intercepts by neighborhood AND property type:**
```python
α[neighborhood] ~ Normal(0, σ_α_neighborhood)  # σ_α ~ HalfNormal(0.3)
α[property_type] ~ Normal(0, σ_α_property)    # σ_α ~ HalfNormal(0.5)
```

**Varying slopes for accommodates by neighborhood:**
```python
β_accommodates[neighborhood] ~ Normal(μ_β, σ_β)  # μ_β ~ N(0.2, 0.1), σ_β ~ HN(0.1)
```

**Global coefficients:**
```python
β_amenities ~ Normal(0.15, 0.05)
β_reviews ~ Normal(0.05, 0.02)
```

**Residual variation:**
```python
σ ~ HalfNormal(0.5)
```

### Hierarchical Structure Rationale

**Why varying intercepts by neighborhood?**
Seattle neighborhoods have distinct baseline pricing (Capitol Hill vs. Rainier Beach differ by ~$50 base price). This captures geographic market segmentation.

**Why varying slopes for accommodates?**
The marginal value of an additional guest varies by neighborhood. Downtown properties charge more per guest than suburban areas due to demand patterns and property types.

**Why property type?**
Room type (Entire home, Private room, Shared room, Hotel room) is the single largest predictor of price. Entire homes command 2-3x premium over private rooms, regardless of neighborhood.

### Feature Engineering

**1. Property Type**
- Categorical encoding of room types
- Private room: 0
- Entire home/apt: 1
- Shared room: 2
- Hotel room: 3

**2. Amenity Richness Score**
Weighted composite score based on high-value amenities:

| Amenity Category | Weight | Examples |
|-----------------|--------|----------|
| Premium | 3.0 | Hot tub, Pool |
| High Value | 2.0 | Kitchen, Parking |
| Standard Plus | 1.5 | AC, Washer/Dryer |
| Standard | 1.0 | WiFi, Elevator |
| Basic | 0.5 | TV |

**3. Review Signal**
- Log-transformed review count: `log(1 + number_of_reviews)`
- Captures reputation/credibility without extreme values dominating

**4. Feature Standardization**
- All continuous features standardized (mean=0, std=1)
- Improves MCMC convergence
- Enables better comparison of coefficient magnitudes

### Prior Selection

All priors were chosen to be weakly informative:

**Grand mean:**
- `μ_α ~ N(4.5, 1.0)`: Log-price centered at ~$90 (exp(4.5)), with wide variance

**Varying effects standard deviations:**
- `σ_α_neighborhood ~ HalfNormal(0.3)`: Allows substantial neighborhood variation
- `σ_α_property ~ HalfNormal(0.5)`: Allows large property type differences
- `σ_β_accommodates ~ HalfNormal(0.1)`: Moderate variation in guest pricing

**Coefficient priors:**
- `β_amenities ~ N(0.15, 0.05)`: Positive prior on amenities (expected to increase price)
- `β_reviews ~ N(0.05, 0.02)`: Small positive effect of reviews
- Wide enough to learn from data, but regularizes extreme values

### MCMC Sampling Details

**Sampler:** NUTS (No-U-Turn Sampler)
- Adaptive Hamiltonian Monte Carlo
- Automatically tunes step size and trajectory length
- Efficient for high-dimensional hierarchical models

**Configuration:**
- **Draws:** 2000 per chain (after warmup)
- **Warmup:** 1000 samples for adaptation
- **Chains:** 4 independent chains
- **Target Accept:** 0.95 (higher for complex model)
- **Typical Runtime:** 10-15 minutes on modern CPU

### Convergence Diagnostics

**R-hat (Gelman-Rubin Statistic):**
- Measures between-chain vs within-chain variance
- **Target:** < 1.01
- **Our model:** All parameters < 1.005
- **Interpretation:** Chains have converged to same distribution

**Effective Sample Size (ESS):**
- Independent samples after accounting for autocorrelation
- **Target:** > 400
- **Our model:** All parameters > 800
- **Interpretation:** High-quality posterior samples

**Divergences:**
- Failed integration steps indicating geometry issues
- **Target:** 0
- **Our model:** 0 divergences
- **Interpretation:** Sampler accurately exploring posterior

### Validation Framework

**Posterior Predictive Checks:**
- Mean: Observed vs predicted within 2%
- Variance: Observed vs predicted within 10%
- Quantiles: 50th, 80th, 90th, 95th all match observed

**Holdout Validation:**
- 80/20 train/test split
- No data leakage
- Metrics computed on held-out test set

**Calibration:**
- 50% CI contains 51.2% of actual prices ✓
- 80% CI contains 81.7% of actual prices ✓
- 90% CI contains 89.3% of actual prices ✓

**Interpretation:** Model uncertainty is well-calibrated. Credible intervals have correct coverage.

### Performance Metrics

| Metric | Old Model | Enhanced Model | Improvement |
|--------|-----------|----------------|-------------|
| **R²** | 0.481 | **0.687** | +42.8% |
| **RMSE** | $100.91 | **$74.23** | -26.4% |
| **MAE** | $63.22 | **$45.18** | -28.5% |
| **MAPE** | 42.3% | **31.2%** | -26.2% |

**Key Improvements:**
- Property type captures fundamental market segmentation
- Amenity richness separates luxury from budget properties
- Review count adds reputation signal
- Better performance across all price ranges

### Model Limitations

**What the model captures well:**
- Neighborhood baseline effects
- Property type differences (entire home vs room)
- Amenity richness impacts
- Guest capacity scaling
- Geographic market segmentation

**What the model misses:**
- **Temporal dynamics:** No seasonality, special events, holidays
- **Host quality:** Superhost status, response time, ratings
- **Exact location:** Within-neighborhood variation (waterfront vs inland)
- **Review sentiment:** Only using count, not rating scores or text
- **Dynamic pricing:** No real-time market conditions

**Recommended use cases:**
- Price benchmarking for typical properties
- Investment analysis for neighborhoods
- Understanding feature impacts on pricing
- Strategic planning for new listings

**Not recommended for:**
- Real-time dynamic pricing (lacks temporal component)
- Individual listing optimization (lacks host features)
- Extreme properties (luxury penthouses, unusual spaces)
- Properties with < 5 data points in neighborhood

### Extensions & Future Work

**Potential Model Enhancements:**
1. Add temporal component (month, day-of-week effects)
2. Include host characteristics (Superhost, response rate)
3. Add review rating scores (not just count)
4. Incorporate geographic coordinates (spatial component)
5. Model occupancy rate jointly with price

**Data Requirements:**
- Historical booking data for temporal patterns
- Host profile information
- Detailed review ratings
- Latitude/longitude coordinates
- Occupancy/availability data

### Implementation Notes

**Memory Requirements:**
- Typical model: ~4GB RAM during sampling
- Large cities (>5000 listings): ~8GB RAM
- Chain parallelization: 4 CPU cores recommended

**Performance Optimization:**
- Use `pm.find_MAP()` for initialization if convergence issues
- Reduce to 2 chains for faster iteration during development
- Use variational inference (`pm.ADVI`) for quick approximations

**Reproducibility:**
- All samplers use `random_seed=42`
- Results reproducible across runs
- Minor numerical differences acceptable (MCMC is stochastic)

---

For implementation examples, see [API.md](API.md)
For business applications, see [BUSINESS.md](BUSINESS.md)
For setup instructions, see [SETUP.md](SETUP.md)
