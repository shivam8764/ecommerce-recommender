# E commerce Hybrid Recommendation Engine

Production minded hybrid recommendation system for an online store. Combines content based ranking and item based collaborative filtering, served through Flask REST APIs with Redis caching and an A B testing router. Designed to serve more than 5K products with low latency and clear extensibility.

## Table of contents
1. Overview  
2. Features  
3. Architecture  
4. Project structure  
5. Data format  
6. Quick start  
7. Configuration  
8. API reference  
9. Caching strategy  
10. A B testing  
11. Evaluation notes  
12. Deployment notes  
13. Troubleshooting  
14. Roadmap  
15. License  
16. .gitignore  
17. Dockerfile

## 1. Overview
This project recreates a hybrid recommendation engine similar to the one described in the resume entry. It provides content based item similarity using TF IDF, item based collaborative filtering built from user interactions, and a hybrid scorer that blends both. The service exposes REST endpoints for fetching content based, user based, and hybrid recommendations, and supports an A B router for live experiments. Redis is used to cache responses and reduce average latency for repeated calls.

## 2. Features
* Content based recommendations from title, category, and description via TF IDF  
* Item based collaborative filtering using user item co occurrence  
* Hybrid scorer that blends content and collaborative scores with adjustable weights  
* Flask REST API with clean JSON responses  
* Redis cache layer with TTL and deterministic cache keys  
* Simple A B assignment based on user id hash  
* Health endpoint and example curl requests  
* Small synthetic dataset for quick demo

## 3. Architecture
Flow  
1. Ingestion of product catalog and interaction logs from CSV  
2. Content model builds TF IDF vectors for products and enables similar item search  
3. Collaborative model builds a user by item matrix, computes item item similarities, and ranks new items for a user  
4. Hybrid scorer merges scores from both models  
5. Redis caches responses per query to reduce repeat latency  
6. A B router assigns users to a variant and serves the chosen strategy

## 4. Project structure
```text
ecommerce-recommender/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── data/
│   ├── products.csv
│   └── interactions.csv
└── recommender/
    ├── __init__.py
    ├── data_loader.py
    ├── content_based.py
    ├── collaborative.py
    ├── hybrid.py
    ├── cache.py
    └── ab_testing.py
````

## 5. Data format

`data/products.csv`

```
product_id,title,category,description,price,img_url
```

Notes

* `product_id` should be unique
* `title`, `category`, and `description` are used by the content model
* Additional attributes can be added without code changes if not required by the model

`data/interactions.csv`

```
user_id,product_id,interaction_type,ts
```

Notes

* Multiple rows per user and product are allowed
* You can upweight events like add_to_cart and purchase during ranking in future work

## 6. Quick start

Prerequisites

* Python 3.10 plus recommended
* Redis server running locally on port 6379

Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS or Linux
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Start Redis locally

```bash
# macOS with Homebrew
brew services start redis
# Linux
redis-server
# Windows
docker run -p 6379:6379 redis:7
```

Run the API

```bash
python app.py
```

Open a browser

```
http://127.0.0.1:5000/health
```

## 7. Configuration

Environment variables

```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

Defaults are set in `config.py`. You can create a `.env` file and export variables before running if you deploy to cloud.

Key config in `config.py`

* Paths for CSVs
* Redis host, port, db
* A B default variants and split

## 8. API reference

Base URL

```
http://127.0.0.1:5000
```

Health

```
GET /health
Response: {"status":"ok"}
```

Content based similar items

```
GET /recommend/content/<product_id>?top_k=10
Example:
curl "http://127.0.0.1:5000/recommend/content/P001?top_k=5"
Response:
{
  "source": "model or cache",
  "results": [
    {"product_id":"P003","title":"Noise Cancelling Headphones","score":0.42}
  ]
}
```

User based collaborative recommendations

```
GET /recommend/user/<user_id>?top_k=10
Example:
curl "http://127.0.0.1:5000/recommend/user/U001?top_k=5"
Response:
{
  "source": "model or cache",
  "results": [
    {"product_id":"P005","score":0.87}
  ]
}
```

Hybrid recommendations

```
GET /recommend/hybrid?user_id=U001&product_id=P001&top_k=10&w_content=0.5&w_cf=0.5
Example:
curl "http://127.0.0.1:5000/recommend/hybrid?user_id=U001&product_id=P001&top_k=5"
Response:
{
  "source": "model or cache",
  "results": [
    {"product_id":"P003","title":"Noise Cancelling Headphones","score":0.61}
  ]
}
```

A B routed recommendations

```
GET /recommend/ab?user_id=U001&product_id=P001&top_k=10
Example:
curl "http://127.0.0.1:5000/recommend/ab?user_id=U001&product_id=P001"
Response:
{
  "variant": "content or hybrid",
  "results": [...]
}
```

Feedback intake for online learning or analytics

```
POST /feedback
Body: {"user_id":"U001","product_id":"P003","action":"clicked","ts":"2025-11-01T10:12:00"}
Example:
curl -X POST "http://127.0.0.1:5000/feedback" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"U001","product_id":"P003","action":"clicked","ts":"2025-11-01T10:12:00"}'
Response: {"status":"received"}
```

## 9. Caching strategy

* Cache keys are deterministic and built from endpoint name and parameters
* Values are JSON encoded and stored with TTL five minutes by default
* Cache hits return the same shape as model responses with `"source":"cache"`
* You can tune TTL in `recommender/cache.py`

Example cache key

```
content|product_id:P001|top_k:10
```

## 10. A B testing

* Deterministic assignment using MD5 hash of `user_id`
* Split ratio and variants are controlled in `config.py`
* Default variants are content and hybrid with a 50 percent split
* Endpoint `/recommend/ab` returns the assigned variant and the results

## 11. Evaluation notes

This repository includes a small synthetic dataset. For a real store you should

* Define an offline metric such as Precision at K or Recall at K
* Split interactions into train and test by time
* Measure baseline content and collaborative performance
* Measure hybrid uplift at different weights
* Log online metrics such as click through rate and add to cart rate if you run live

You can add a `reports` folder for plots, tables, and experiment summaries.

## 12. Deployment notes

Run with Gunicorn behind a production server

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

Docker Compose for Flask plus Redis

```yaml
version: "3.9"
services:
  api:
    build: .
    command: gunicorn -w 2 -b 0.0.0.0:5000 app:app
    ports:
      - "5000:5000"
    environment:
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_DB: 0
    depends_on:
      - redis
  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

Render or Railway

* Set environment variables for Redis connection
* Add a start command that runs gunicorn

## 13. Troubleshooting

Issue: `ModuleNotFoundError` for `recommender`
Fix: Ensure `recommender/__init__.py` exists and you run from repository root

Issue: `Redis connection error`
Fix: Start Redis locally or point to a managed Redis instance through environment variables

Issue: API returns empty results for a user
Fix: Check that the user id exists in `data/interactions.csv`. For cold start users, use content endpoint or hybrid with a product id

Issue: API returns empty for a product
Fix: Ensure the product id exists in `data/products.csv` and that title category description are populated

## 14. Roadmap

* Add interaction weighting for views, add to cart, purchase
* Add PostgreSQL storage for interactions with ingestion jobs
* Add recall then re rank architecture with candidate generation and learned ranker
* Add a minimal React UI that calls the hybrid endpoint
* Add offline evaluation notebook and unit tests

## 15. License

MIT or choose a license that fits your use case

## 16. .gitignore

Create a `.gitignore` file in the repository root with the content below to keep the repo clean.

```gitignore
# Byte code and caches
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
*.dylib
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/

# Virtual environments
venv/
.env/
.env.local
.venv/

# OS and editor junk
.DS_Store
Thumbs.db
.vscode/
.idea/

# Packaging
build/
dist/
*.egg-info/
.eggs/

# Notebooks
.ipynb_checkpoints/

# Logs
logs/
*.log

# Local overrides
.env
```

Notes

* Keep `data/` in version control for the small demo CSVs
* Do not commit real customer data or secrets

## 17. Dockerfile

Create a `Dockerfile` in the repository root for container based deployment.

```dockerfile
# Minimal production friendly image
FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0

# Expose port
EXPOSE 5000

# Start with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run locally

```bash
docker build -t ecommerce-recommender:latest .
docker run --rm -p 5000:5000 \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6379 \
  ecommerce-recommender:latest
```

If you want Redis inside Docker too, use the provided docker compose file.

```

---
