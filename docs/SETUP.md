# Setup & Deployment Guide

## Local Installation

### Prerequisites

- **Python:** 3.9 or higher
- **pip:** Package manager (included with Python)
- **RAM:** 8GB+ recommended (for MCMC sampling)
- **Disk Space:** ~2GB for dependencies and data
- **OS:** Linux, macOS, or Windows

### Step-by-Step Setup

#### 1. Clone Repository

```bash
git clone https://github.com/Dennis-J-Carroll/bayesian-analysis-of-airbnb-seattle-market.git
cd bayesian-analysis-of-airbnb-seattle-market
```

#### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected installation time:** 5-10 minutes

#### 4. Verify Installation

```bash
python -c "import pymc; import streamlit; print('✓ Installation successful')"
```

You should see: `✓ Installation successful`

#### 5. Run Dashboard

```bash
streamlit run expert_dashboard.py
```

Dashboard will open automatically at `http://localhost:8501`

### Troubleshooting

#### Issue: PyMC installation fails

**Symptoms:**
```
ERROR: Failed building wheel for pymc
```

**Solution:**
Install build dependencies first:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential gfortran
pip install -r requirements.txt
```

**macOS:**
```bash
xcode-select --install
pip install -r requirements.txt
```

**Windows:**
1. Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Restart terminal
3. `pip install -r requirements.txt`

#### Issue: MCMC sampling is very slow

**Symptoms:**
- Model fitting takes > 30 minutes
- CPU usage is low during sampling

**Solution 1:** Reduce chains and draws for faster iteration:
```python
model.fit_model_with_diagnostics(draws=1000, tune=500, chains=2)
# Instead of default: draws=2000, tune=1000, chains=4
```

**Solution 2:** Use variational inference for quick approximation:
```python
import pymc as pm
with model.model:
    approx = pm.fit(method='advi', n=20000)
    trace = approx.sample(2000)
```

#### Issue: Memory errors during fitting

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solution 1:** Use fewer chains:
```python
model.fit_model_with_diagnostics(chains=2)  # Instead of 4
```

**Solution 2:** Reduce draws:
```python
model.fit_model_with_diagnostics(draws=1000, tune=500)
```

**Solution 3:** If model still fails, use variational inference (see above)

#### Issue: Streamlit dashboard won't start

**Symptoms:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
Ensure virtual environment is activated and dependencies installed:
```bash
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

pip install streamlit
```

## Streamlit Cloud Deployment

For detailed deployment to Streamlit Cloud, see [DENNIS_DEPLOYMENT_GUIDE.md](../DENNIS_DEPLOYMENT_GUIDE.md)

### Quick Deployment Steps

1. **Fork/Push to GitHub**
   - Ensure code is in GitHub repository
   - Main branch is up to date

2. **Connect Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"

3. **Configure App**
   - Repository: `your-username/bayesian-analysis-of-airbnb-seattle-market`
   - Branch: `main`
   - Main file: `expert_dashboard.py`

4. **Deploy**
   - Click "Deploy"
   - Wait 5-10 minutes for build
   - App will be live at `your-app.streamlit.app`

### Deployment Troubleshooting

**Issue:** Build fails due to memory limits

**Solution:** Streamlit Cloud has 1GB memory limit. The model fitting may fail. Options:
1. Pre-compute model and save trace (`model_trace.nc`)
2. Load pre-computed trace in dashboard
3. Use smaller dataset for demonstration

**Issue:** PyMC dependencies fail

**Solution:** Ensure `packages.txt` includes system dependencies:
```
build-essential
gfortran
```

## Configuration

### config.yaml (Optional)

Create a `config.yaml` file for custom settings:

```yaml
model:
  draws: 2000
  tune: 1000
  chains: 4
  target_accept: 0.95

dashboard:
  theme: "misty_morning"
  cache_ttl: 3600  # Cache duration in seconds

data:
  path: "data/raw/listings.csv"
  output_dir: "outputs/"

logging:
  level: "INFO"
  file: "logs/model.log"
```

**Usage in Python:**
```python
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

model.fit_model_with_diagnostics(**config['model'])
```

### Environment Variables

Create a `.env` file for sensitive configuration:

```bash
DATA_PATH=/path/to/listings.csv
STREAMLIT_THEME=misty_morning
LOG_LEVEL=INFO
```

**Load in Python:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
data_path = os.getenv('DATA_PATH', 'data/raw/listings.csv')
```

## Data Setup

### Download Seattle Airbnb Data

**Option 1: Inside Airbnb (Recommended)**
```bash
# Create data directory
mkdir -p data/raw

# Download latest Seattle data
wget http://data.insideairbnb.com/united-states/wa/seattle/2024-03-10/data/listings.csv.gz
gunzip listings.csv.gz
mv listings.csv data/raw/
```

**Option 2: Manual Download**
1. Visit [Inside Airbnb](http://insideairbnb.com/get-the-data/)
2. Find Seattle, Washington
3. Download `listings.csv`
4. Place in `data/raw/` directory

### Data Validation

Verify data is correctly formatted:

```python
import pandas as pd

df = pd.read_csv('data/raw/listings.csv')
print(f"Loaded {len(df)} listings")
print(f"Columns: {df.columns.tolist()}")

# Check required columns
required = ['price', 'neighbourhood_cleansed', 'accommodates', 'room_type']
missing = [col for col in required if col not in df.columns]
if missing:
    print(f"❌ Missing columns: {missing}")
else:
    print("✓ All required columns present")
```

## Running the Model

### Basic Workflow

```bash
# Activate environment
source venv/bin/activate

# Run model training
python -c "
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
model.fit_model_with_diagnostics()
"
```

### Save Model for Later Use

```python
import arviz as az

# After fitting model
az.to_netcdf(model.trace, 'outputs/model_trace.nc')

# Load later
trace = az.from_netcdf('outputs/model_trace.nc')
model.trace = trace
```

### Run Dashboard

```bash
streamlit run expert_dashboard.py
```

## Performance Optimization

### Faster Development Iteration

**Use smaller sample during development:**
```python
model.fit_model_with_diagnostics(
    draws=500,   # Instead of 2000
    tune=250,    # Instead of 1000
    chains=2     # Instead of 4
)
```

**Use subset of data:**
```python
model.load_and_clean_data()
model.data = model.data.sample(n=1000, random_state=42)  # Use 1000 listings
model.build_enhanced_hierarchical_model()
```

### Production-Ready Settings

**Maximum quality (longer runtime):**
```python
model.fit_model_with_diagnostics(
    draws=4000,
    tune=2000,
    chains=4,
    target_accept=0.99
)
```

### Parallel Processing

**Enable multithreading (if available):**
```python
import os
os.environ['OMP_NUM_THREADS'] = '4'  # Use 4 CPU cores
```

## Testing

### Run Unit Tests

```bash
pytest tests/
```

### Validate Model Convergence

```python
from src.hierarchical_bayesian_model import HierarchicalBayesianPriceModel

model = HierarchicalBayesianPriceModel('data/raw/listings.csv')
model.load_and_clean_data()
model.build_enhanced_hierarchical_model()
model.fit_model_with_diagnostics()

# Check diagnostics
import arviz as az

rhat = az.rhat(model.trace)
assert float(rhat.max()) < 1.01, "Chains did not converge"

ess = az.ess(model.trace)
assert float(ess.min()) > 400, "Insufficient effective sample size"

print("✓ Model validation passed")
```

## Production Deployment

### Docker Deployment (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run dashboard
CMD ["streamlit", "run", "expert_dashboard.py"]
```

**Build and run:**
```bash
docker build -t airbnb-model .
docker run -p 8501:8501 airbnb-model
```

---

For usage examples, see [API.md](API.md)
For technical details, see [TECHNICAL.md](TECHNICAL.md)
For business applications, see [BUSINESS.md](BUSINESS.md)
