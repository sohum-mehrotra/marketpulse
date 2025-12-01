# ✨ MarketPulse — Real-Time S&P 500 Exploration API + Web App  
### *Final Build Anything Project — DS 2022*

---

# 🧭 Executive Summary

The S&P 500 represents one of the most important indicators of U.S. market performance, but most datasets and dashboards for exploring it are either paywalled, slow, or not customizable. The goal of **MarketPulse** is to build a small, efficient, reproducible system that transforms raw S&P 500 datasets into a fully functional, cloud-hosted API and interactive dashboard.

This project ingests two CSV datasets—**sp500_index.csv** and **sp500_companies.csv**—and builds an SQLite-backed data service that supports analytical queries, web endpoints, HTML table views, and sector-level statistics. MarketPulse is deployed via **Render**, containerized using **Docker**, continuously tested using **GitHub Actions**, and structured around the data engineering and API concepts from **Case Study 06**.

---

# 🏗️ System Overview

## 🎯 Project Goals
- Convert raw CSVs into a clean, queryable relational database  
- Build an API that exposes companies, sectors, and index history  
- Render user-friendly HTML tables instead of raw JSON  
- Deploy reproducibly via Docker + GitHub Actions  
- Perform real SQL transformations (joins, aggregations, derived tables)  
- Create an accessible homepage with navigation + search  

---

## 🧩 Concepts Integrated (from Case Study 06)

This project incorporates the following concepts emphasized in Case Study 06:

- Designing structured **SQL queries & joins**  
- Loading external datasets into a normalized SQLite database  
- Creating **derived tables** (e.g., sector-level statistics)  
- Building a structured **Flask application factory**  
- Using **pandas ↔ SQLAlchemy** for data pipelines  
- API routing and HTML template rendering  
- Writing reproducible workflows with **Docker**  
- CI pipeline with **pytest** + GitHub Actions  
- Cloud deployment & observability  

---

# 🖼️ Architecture Diagram

                         +-------------------------+
                         |    sp500_companies.csv  |
                         |      sp500_index.csv    |
                         +------------+------------+
                                      |
                                      v
                         +-------------------------+
                         |                         |
                         |    init_db() Loader     |
                         |  (pandas → SQLite DB)   |
                         |                         |
                         +------------+------------+
                                      |
                         +-------------------------+
                         |     SQLite Database     |
                         |  companies, index_hist  |
                         |  sector_stats (derived) |
                         +------------+------------+
                                      |
     +------------------------+-------+-------+------------------------+
     |                        |               |                        |
     v                        v               v                        v
/companies            /company/<symbol>      /index                 /sectors
HTML Table           HTML Table             HTML Table             HTML Table
     ^                        ^               ^                        ^
     |                        |               |                        |
     +----------- Flask Application Factory +--------------------------+

Docker Container → GitHub Actions (CI) → Render Cloud Deployment


---

# ⚙️ Data Pipeline

## **Input Files (`/assets`)**

| File Name | Description |
|----------|-------------|
| `sp500_index.csv` | 10 years of daily S&P 500 index levels |
| `sp500_companies.csv` | Current S&P 500 company fundamentals, sectors, weights |

## **Database Tables Created**

| Table | Source | Description |
|-------|---------|-------------|
| `index_history` | sp500_index.csv | Daily index date/value |
| `companies` | sp500_companies.csv | Symbol, sector, market cap, etc. |
| `sector_stats` | Derived | Aggregations: weights, market caps, counts |

## **Example SQL Transformations**

- `GROUP BY` sector (n companies, avg marketcap)  
- `JOIN` companies ↔ sector stats  
- Sorting (`ORDER BY marketcap`)  
- Filtering, slicing, and limiting  
- Column normalization for SQL safety

---

# 🚀 How to Run the Project (Local, Reproducible)

## **1. Clone the Repository**
```bash
git clone https://github.com/sohum-mehrotra/marketpulse
cd marketpulse
````

---

## **2. Build & Run with Docker**

### Build the image:

```bash
docker build -t marketpulse .
```

### Run the container:

```bash
docker run --rm -p 8080:8080 marketpulse
```

Your app is available at:
👉 **[http://localhost:10000](http://localhost:8080)**

---

## **3. Run Tests**

```bash
pytest
```

Tests automatically run in CI on every push.

---

# 🌐 Cloud Deployment (Render)

The production API is live at:

👉 **[https://marketpulse-api-spwg.onrender.com](https://marketpulse-api-spwg.onrender.com)**

This instance is deployed using:

* Dockerfile
* GitHub Actions CI
* Render auto-deploy from `main`

---

# 🗂️ Features

## 🔹 1. Homepage Navigation

Includes links to:

* Companies
* Sectors
* S&P 500 Index
* Search bar → `/company/<symbol>`

## 🔹 2. Readable HTML Tables (Not Raw JSON)

All pages use Bootstrap-styled tables:

```python
df.to_html(classes="table table-striped table-hover")
```

## 🔹 3. Search by Stock Ticker

Entering `AAPL` →

```
/company/AAPL
```

## 🔹 4. Sector Explorer

Shows:

* Companies in the sector
* Market cap ordering
* Sector-level statistics

## 🔹 5. S&P 500 Index Explorer

Shows the most recent 300 records of daily index levels.

---

# 📊 Screenshots (To Be Added)

Add images inside `assets/screenshots/` and embed below:

### **Homepage**

`![homepage](assets/screenshots/home.png)`

### **Companies View**

`![companies](assets/screenshots/companies.png)`

### **Sector Page**

`![sectors](assets/screenshots/sectors.png)`

### **Index History**

`![index](assets/screenshots/index.png)`

---

# 🧪 Testing & CI

## ✔ GitHub Actions Workflow

Runs on every commit:

* Install dependencies
* Build Docker image
* Run pytest
* Fail on test errors

Defined in:

```
.github/workflows/ci.yml
```

## ✔ Tests Include:

* API health endpoint
* Query correctness
* Company table existence
* Sector table stats

---

# 🧠 Design Decisions

### **Why SQLite?**

* Extremely portable
* Deterministic, reproducible database state
* Perfect for Dockerized student projects

### **Why Flask?**

* Lightweight
* Great for small data APIs
* Mirrors the teaching style of DS 2024 & Case Study 06

### **Why Docker?**

* Eliminates Python version issues
* Ensures reproducibility
* Allows Render to deploy the exact same environment

---

# 📈 Results & Evaluation

MarketPulse successfully delivers:

* A fully functional, cloud-hosted API
* A front-end HTML interface
* Real sector-level SQL aggregations
* A reproducible build and deploy process
* Cloud deployment + CI/CD
* Complete end-to-end data pipeline (CSV → SQL → API → HTML)

All endpoints load correctly and render data fast (sub-100ms query time).

---

# 🔮 Future Work

Potential improvements:

* Add Plotly charts for index visualization
* Add stock-level performance history
* Use PostgreSQL for persistent cloud storage
* Add pagination for very large datasets
* Build a React front-end
* Add automated documentation (Swagger)

---

# 📚 Appendix

## Project Structure

```
marketpulse/
│
├── assets/
│   ├── sp500_companies.csv
│   ├── sp500_index.csv
│   └── screenshots/
│
├── src/
│   ├── app.py
│   ├── db.py
│   └── queries.py
│
├── tests/
│   ├── test_api.py
│   └── test_queries.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🏁 Links

**GitHub Repository:**
[https://github.com/sohum-mehrotra/marketpulse](https://github.com/sohum-mehrotra/marketpulse)

**Live Deployment (Render):**
[https://marketpulse-api-spwg.onrender.com](https://marketpulse-api-spwg.onrender.com)


**LICENSE**
MIT License

Copyright (c) 2024 Sohum Mehrotra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
