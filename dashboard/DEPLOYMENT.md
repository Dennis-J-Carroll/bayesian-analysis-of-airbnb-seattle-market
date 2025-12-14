# Deployment Guide
## Enterprise Airbnb Seattle Analytics Dashboard

---

## 🚀 Quick Start (Local Development)

### Step 1: Install Dependencies

```bash
cd /home/dennisjcarroll/Desktop/Dashboard-Attempt_1-airbnb-seattle-market

# Install dashboard requirements
pip install -r requirements-dashboard.txt
```

### Step 2: Verify Data Files

Ensure the following file exists:
```
data/raw/listings.csv
```

### Step 3: Run Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically in your default browser at `http://localhost:8501`

---

## 📋 Pre-Deployment Checklist

- [ ] Data file exists: `data/raw/listings.csv`
- [ ] Required columns present: `price`, `accommodates`, `neighbourhood_cleansed`
- [ ] Python 3.10+ installed
- [ ] All dependencies installed
- [ ] Port 8501 available (or configure different port)

---

## 🌐 Production Deployment Options

### Option 1: Streamlit Cloud (Recommended for MVP)

**Pros**: Free, easy, zero DevOps
**Cons**: Limited compute, public by default

**Steps**:

1. **Prepare repository**:
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Dashboard ready for deployment"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Select repository: `Dashboard-Attempt_1-airbnb-seattle-market`
   - Set main file path: `dashboard/app.py`
   - Click "Deploy"

3. **Configure secrets** (if needed):
   - In Streamlit Cloud dashboard
   - Go to App Settings > Secrets
   - Add any API keys or configuration

**Limitations**:
- Max 1GB memory
- No GPU
- Public URL (can enable password protection)

---

### Option 2: Docker Container

**Pros**: Portable, consistent environment
**Cons**: Requires container hosting

**Create Dockerfile**:

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-dashboard.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dashboard.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
ENTRYPOINT ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Build and run**:

```bash
# Build
docker build -t airbnb-dashboard .

# Run
docker run -p 8501:8501 airbnb-dashboard

# Run with volume mount (for data updates)
docker run -p 8501:8501 -v $(pwd)/data:/app/data airbnb-dashboard
```

**Deploy to cloud**:

```bash
# Tag for container registry
docker tag airbnb-dashboard your-registry/airbnb-dashboard:v1.0

# Push
docker push your-registry/airbnb-dashboard:v1.0
```

---

### Option 3: AWS EC2

**Pros**: Full control, scalable
**Cons**: Requires AWS knowledge, higher cost

**Steps**:

1. **Launch EC2 instance**:
   - Instance type: t3.medium (2 vCPU, 4GB RAM)
   - AMI: Ubuntu 22.04 LTS
   - Security group: Allow TCP 8501

2. **SSH into instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3.10 python3-pip git
   ```

4. **Clone repository**:
   ```bash
   git clone https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market.git
   cd Bayesian-Analysis-of-Airbnb-Seattle-Market
   ```

5. **Install Python packages**:
   ```bash
   pip3 install -r requirements-dashboard.txt
   ```

6. **Run with systemd** (persistent service):

Create `/etc/systemd/system/airbnb-dashboard.service`:

```ini
[Unit]
Description=Airbnb Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Bayesian-Analysis-of-Airbnb-Seattle-Market
ExecStart=/usr/bin/python3 -m streamlit run dashboard/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable airbnb-dashboard
sudo systemctl start airbnb-dashboard
sudo systemctl status airbnb-dashboard
```

7. **Configure reverse proxy** (optional, for HTTPS):

Install nginx:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Configure nginx (`/etc/nginx/sites-available/airbnb-dashboard`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable SSL:
```bash
sudo ln -s /etc/nginx/sites-available/airbnb-dashboard /etc/nginx/sites-enabled/
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

---

### Option 4: Heroku

**Pros**: Simple PaaS, free tier available
**Cons**: Heroku shutting down free tier

**Files needed**:

`Procfile`:
```
web: streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0
```

`runtime.txt`:
```
python-3.10.12
```

`setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Deploy**:

```bash
heroku create airbnb-seattle-dashboard
git push heroku main
heroku open
```

---

## ⚙️ Configuration

### Environment Variables

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
enableCORS = false
maxUploadSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#f8f9fa"
secondaryBackgroundColor = "#ffffff"
textColor = "#262730"
font = "sans serif"
```

### Secrets Management

For API keys or sensitive data, create `.streamlit/secrets.toml`:

```toml
[api_keys]
walkscore = "your-api-key-here"

[database]
connection_string = "postgresql://..."
```

Access in code:
```python
import streamlit as st

api_key = st.secrets["api_keys"]["walkscore"]
```

---

## 🔒 Security Considerations

### 1. Authentication

Add password protection:

```python
# At top of app.py
import streamlit as st

def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

### 2. Data Security

- **Don't commit secrets**: Use `.gitignore`
- **Encrypt sensitive data**: Use environment variables
- **Validate inputs**: Prevent injection attacks
- **Rate limiting**: Implement for public deployments

### 3. HTTPS

Always use HTTPS in production:
- Streamlit Cloud: Automatic
- AWS: Use ALB or nginx reverse proxy
- Heroku: Automatic

---

## 📊 Monitoring & Logging

### Application Monitoring

Add to `app.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log usage
logger.info(f"User accessed {page} page")
logger.info(f"Prediction generated for {neighborhood}")
```

### Performance Monitoring

Use Streamlit built-in profiler:

```bash
streamlit run dashboard/app.py --server.runOnSave=true --logger.level=debug
```

### Error Tracking

Integrate Sentry:

```python
import sentry_sdk
from sentry_sdk.integrations.streamlit import StreamlitIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[StreamlitIntegration()],
)
```

---

## 🔄 Updates & Maintenance

### Updating Dashboard

```bash
# Pull latest changes
git pull origin main

# Restart service (systemd)
sudo systemctl restart airbnb-dashboard

# Or restart Docker container
docker restart airbnb-dashboard
```

### Database Updates

If using database backend:

```python
# Schedule regular data refresh
import schedule
import time

def update_data():
    logger.info("Updating data from database...")
    # Fetch new data
    # Update cache

schedule.every().day.at("02:00").do(update_data)
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Port already in use
```bash
# Find process using port 8501
lsof -i :8501

# Kill process
kill -9 <PID>
```

**Issue**: Memory errors
- Increase instance size
- Enable data sampling
- Optimize caching

**Issue**: Slow loading
- Enable Streamlit caching
- Precompute expensive operations
- Use database instead of CSV

### Debug Mode

```bash
streamlit run dashboard/app.py --logger.level=debug
```

### Health Checks

Add health check endpoint:

```python
# In app.py
st.set_page_config(
    page_title="Dashboard",
    page_icon="🏠",
)

# Health check route
if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()
```

Test:
```bash
curl http://localhost:8501/?health=check
```

---

## 📈 Scaling

### Horizontal Scaling

Use load balancer with multiple instances:

```nginx
upstream streamlit_backend {
    server 10.0.1.10:8501;
    server 10.0.1.11:8501;
    server 10.0.1.12:8501;
}

server {
    location / {
        proxy_pass http://streamlit_backend;
    }
}
```

### Caching Strategy

```python
# Aggressive caching for production
@st.cache_resource(ttl=86400)  # 24 hours
def load_model():
    ...

@st.cache_data(ttl=3600)  # 1 hour
def get_predictions(neighborhood, accommodates):
    ...
```

---

## ✅ Post-Deployment Checklist

- [ ] Dashboard accessible via URL
- [ ] All pages load correctly
- [ ] Predictions working
- [ ] Data visualizations rendering
- [ ] Error handling working
- [ ] Monitoring/logging enabled
- [ ] SSL/HTTPS configured (production)
- [ ] Authentication enabled (if required)
- [ ] Backup strategy in place
- [ ] Documentation updated

---

## 📞 Support

**Issues**: https://github.com/Dennis-J-Carroll/Bayesian-Analysis-of-Airbnb-Seattle-Market/issues

**Documentation**: See `/docs` folder

---

**Last Updated**: 2025-01-20
