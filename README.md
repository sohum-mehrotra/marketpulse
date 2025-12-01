# MarketPulse — S&P 500 Data API  
*A DS 1000 Final Project integrating Case Study 06: Cloud-Native Data Pipelines*

## 🚀 Executive Summary
MarketPulse is a containerized, cloud-deployed analytics API built from scratch using the **S&P 500 companies dataset** and the **S&P 500 index dataset** provided for the course. The system ingests CSV data, loads it automatically into a lightweight SQL database, exposes structured API endpoints for data access, and integrates continuous testing and continuous deployment through GitHub Actions and Render.

This project follows the core principles of **Case Study 06: Cloud-Native Data Systems**, demonstrating how small teams can use containers, CI/CD, infrastructure-as-code, and cloud runtime environments to build reproducible, maintainable, and scalable data products.

---

# 🧠 Concept Integration — Case Study 06 (Cloud Systems)
This project directly applies three themes from **Case Study 06**:

### **1. Containerization as a unit of deployment**  
Like the companies in Case Study 06, MarketPulse uses Docker to:
- Bundle code + dependencies
- Standardize runtime environments
- Guarantee reproducibility
- Simplify cloud deployment

The entire system runs off a single Dockerfile, just like modern cloud microservices.

### **2. CI/CD Automation**  
Case Study 06 emphasizes automated pipelines for:
- building,
- testing,
- validating,
- deploying software.

MarketPulse implements this through **GitHub Actions**, which:
- Runs tests on every push  
- Builds the Docker image  
- Validates the server  
- Ensures no broken code reaches production  

This mirrors the shift from manual DevOps to automated cloud pipelines.

### **3. Cloud Runtime + Observability**  
The application is deployed on **Render**, representing:
- on-demand scaling  
- managed runtime  
- logs + metrics for observability  
- a stable URL for public access  

This demonstrates the cloud-native transition discussed in Case Study 06—software is no longer “run,” it is *hosted* with automated operational support.

---

# 🏗️ System Architecture Overview

MarketPulse follows a simple but production-ready cloud architecture:

1. **Data Layer**
   - Loads two provided CSVs:
     - `sp500_companies.csv`
     - `sp500_index.csv`
   - Stores them in a local SQLite database
   - Provides queries for sectors, companies, and index data

2. **API Layer**
   - Flask backend
   - REST endpoints:
     - `/companies`
     - `/sectors`
     - `/index`
   - JSON responses

3. **Container Layer**
   - Dockerfile defines environment
   - Runs gunicorn server on port 10000

4. **CI/CD Layer**
   - GitHub Actions workflow:
     - Install deps
     - Run tests
     - Build Docker image
     - Lint + validate

5. **Cloud Hosting**
   - Render web service  
   - Automatic deploy on push to `main`

### 📊 Architecture Diagram  
*(Place this file in `/assets/architecture.png` and uncomment the link)*

![Architecture Diagram](assets/architecture.png)

---

# 🌐 Live Cloud Deployment (Extra Credit)
**Base URL:**  
👉 https://marketpulse-api-spwg.onrender.com  

**Example endpoints (once root route is added):**  
- `/companies`  
- `/sectors`  
- `/index`  

---

# 🧪 Testing + Quality Assurance

The project includes a full test suite located in `/tests`:

### ✔ Test Types
- Database initialization
- Data loading from CSV
- Query outputs (companies, sectors, index)
- API route responses

### ✔ CI Integration
All tests run automatically via GitHub Actions on:
- push
- pull request

CI guarantees:
- No broken code  
- Stable deployments  
- Full reproducibility  

---

# 🐳 Running Locally (Reproducible Build)

### **1️⃣ Clone the repo**
```bash
git clone https://github.com/sohum-mehrotra/marketpulse
cd marketpulse
