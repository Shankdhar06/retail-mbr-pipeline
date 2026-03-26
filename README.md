
# 🛒 Retail MBR Pipeline
### End-to-End Analytics Engineering Project
**Author:** Vaibhav Shankdhar | **Stack:** MySQL → Python → Email Automation → Streamlit | **Run:** One Click

---

## 📌 Project Overview

A fully automated **end-to-end retail analytics pipeline** that ingests raw sales data, models it in SQL, builds KPIs with MoM & YoY trends, exports to a local data warehouse, generates a professional **Monthly Business Review (MBR) PDF**, emails it automatically, and serves a **live Streamlit dashboard** — all triggered by a single command.

```bash
py run_pipeline.py
```

---

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
│              Superstore.csv (100K+ transactions)            │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 1 — SQL (MySQL)                      │
│  • Dimensional modelling (Star Schema)                      │
│  • dim_customer, dim_product, fact_orders                   │
│  • 5 KPI views + Master KPI view                            │
│  • MoM & YoY window functions                               │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│           LAYER 2 — LOCAL DATA WAREHOUSE                    │
│  • master_kpi.csv          (base KPIs)                      │
│  • master_kpi_trends.csv   (KPIs + MoM + YoY)              │
└──────────┬───────────────────────────────┬──────────────────┘
           ↓                               ↓
┌──────────────────────┐     ┌─────────────────────────────┐
│  LAYER 3 — PYTHON    │     │   LAYER 4 — DASHBOARD       │
│  • 6 KPI Charts      │     │   • Streamlit live view     │
│  • MBR PDF Report    │     │   • Month/Region/Category   │
│  • Auto Email        │     │     filters                 │
└──────────────────────┘     │   • MoM & YoY KPI cards     │
                             └─────────────────────────────┘
```

---

## 📂 Repository Structure

```
retail-mbr-pipeline/
│
├── 📁 data/
│   ├── raw/
│   │   └── Superstore.csv              ← Source data
│   └── warehouse/
│       ├── master_kpi.csv              ← Base KPI warehouse
│       └── master_kpi_trends.csv       ← KPIs + MoM + YoY
│
├── 📁 sql/
│   ├── 01_create_schema.sql            ← Star schema creation
│   ├── 02_load_data.sql                ← Data loading
│   ├── 03_transform.sql                ← Cleaning & views
│   └── 04_build_kpis.sql               ← KPI models & master view
│
├── 📁 python/
│   ├── 01_load_warehouse.py            ← MySQL → CSV export
│   ├── 02_build_charts.py              ← 6 KPI charts
│   ├── 03_generate_pdf.py              ← MBR PDF generator
│   └── 04_send_email.py                ← Email automation
│
├── 📁 dashboard/
│   └── app.py                          ← Streamlit dashboard
│
├── 📁 output/
│   ├── charts/                         ← 6 PNG chart files
│   └── MBR_Report_YYYY_MM.pdf          ← Auto-generated MBR
│
├── run_pipeline.py                     ← ONE click runner
└── README.md
```

---

## 📊 The 5 KPIs

| # | KPI | Type | Formula |
|---|---|---|---|
| 1 | **Revenue** | 💰 Currency | `SUM(sales * (1 - discount))` |
| 2 | **PCOGS** | 💰 Currency | `SUM(sales - profit)` |
| 3 | **OPS** | 💰 Currency | `SUM(sales)` — Ordered Product Sales |
| 4 | **Profit Margin %** | 📈 Percentage | `SUM(profit) / SUM(sales) * 100` |
| 5 | **Conversion Rate** | 📈 Percentage | `Profitable orders / Total orders * 100` |

Each KPI includes **MoM % change** and **YoY % change** calculated using SQL Window Functions (`LAG`).

---

## 🗄️ SQL Layer — Data Model

### Star Schema Design
```
         dim_customer
              │
fact_orders ──┤
              │
         dim_product
```

### KPI Views Built
```sql
vw_clean_orders         ← Joined, cleaned master view
vw_kpi_revenue          ← Revenue aggregations
vw_kpi_pcogs            ← PCOGS aggregations
vw_kpi_ops              ← OPS aggregations
vw_kpi_profit_margin    ← Margin % calculations
vw_kpi_conversion       ← Conversion rate calculations
vw_master_kpi           ← All 5 KPIs joined
vw_master_kpi_trends    ← Master KPI + MoM + YoY (LAG functions)
```

### Key SQL Techniques Used
- **CTEs** for staged transformations
- **Window Functions** (`LAG`, `PARTITION BY`) for MoM & YoY
- **NULLIF** for safe division
- **Multi-table JOINs** across 4 tables
- **CREATE OR REPLACE VIEW** for modular KPI building

---

## 🐍 Python Layer

### 01 — Warehouse Export
Connects Python to MySQL via SQLAlchemy, loads raw CSV into dimensional tables and exports KPI views to local CSV warehouse.

### 02 — Chart Builder
Generates 6 professional charts from `master_kpi_trends.csv`:

| Chart | Description |
|---|---|
| 1 | Monthly Revenue Trend with MoM annotation |
| 2 | OPS vs Revenue vs PCOGS by Category |
| 3 | Profit Margin % by Region with MoM & YoY |
| 4 | Conversion Rate by Customer Segment |
| 5 | Monthly Margin Trend with YoY overlay |
| 6 | **Full KPI Scorecard** — all 5 KPIs with MoM & YoY |

### 03 — PDF Generator
Builds a 6-page professional MBR PDF using `reportlab`:

| Page | Content |
|---|---|
| 1 | Cover + KPI Scorecard + Executive Summary |
| 2 | KPI Summary Table + Regional Breakdown |
| 3 | Revenue Analysis Charts |
| 4 | Profitability & Conversion Charts |
| 5 | Trend Analysis + Last 6 Months Table |
| 6 | Auto-generated footer & sign-off |

### 04 — Email Automation
Sends the MBR PDF via Gmail SMTP with a professional HTML email body showing all 5 KPI cards with MoM & YoY deltas.

---

## 📊 Streamlit Dashboard

Live interactive dashboard at `http://localhost:8501`:

- **Month selector** — switch between any month
- **Region / Category / Segment filters** — slice KPIs any way
- **5 KPI metric cards** — with MoM & YoY deltas
- **Revenue trend chart** — with selected month highlighted
- **Revenue by category** — horizontal bar chart
- **Margin by region** — colour coded by performance
- **Conversion by segment** — with value labels
- **Last 6 months table** — quick trend view
- **Raw data expander** — drill into granular numbers

### Run Dashboard
```bash
py -m streamlit run dashboard/app.py
```

---

## 🚀 How to Run

### Prerequisites
```bash
pip install pandas matplotlib seaborn reportlab fpdf2 streamlit pymysql sqlalchemy openpyxl
```

### Setup Database
```sql
-- Run in MySQL Workbench
SOURCE sql/01_create_schema.sql;
SOURCE sql/03_transform.sql;
SOURCE sql/04_build_kpis.sql;
```

### Run Full Pipeline
```bash
# Without email
py run_pipeline.py

# With email
py run_pipeline.py --email
```

### Run Dashboard Only
```bash
py -m streamlit run dashboard/app.py
```

---

## ⏱️ Pipeline Performance

| Step | Script | Time |
|---|---|---|
| Warehouse Export | `01_load_warehouse.py` | ~3-5s |
| Chart Generation | `02_build_charts.py` | ~5-8s |
| PDF Report | `03_generate_pdf.py` | ~2-3s |
| Email Delivery | `04_send_email.py` | ~3-5s |
| **Total** | `run_pipeline.py` | **~15-20s** |

---

## 🛠️ Tools & Technologies

![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=flat&logo=mysql)
![Python](https://img.shields.io/badge/Python-3.13-yellow?style=flat&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Wrangling-green?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat&logo=streamlit)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Generation-orange?style=flat)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-lightgrey?style=flat)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Charts-blue?style=flat)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualisation-teal?style=flat)

---

## 💡 Key Design Decisions

**Why a local CSV as data warehouse?**
Keeps the project cloud-free and portable. The same pattern works with Snowflake, BigQuery or Redshift by simply swapping the SQLAlchemy connection string.

**Why separate SQL and Python layers?**
Mirrors real-world Analytics Engineering architecture — SQL handles data modelling and transformation, Python handles reporting and delivery. Each layer is independently testable and replaceable.

**Why `run_pipeline.py`?**
Enables scheduling via Windows Task Scheduler or cron — add one line and this pipeline runs automatically every month without manual intervention.

---

## 📅 Scheduling — Run Automatically Every Month

To run the pipeline automatically on the 1st of every month:

**Windows Task Scheduler:**
1. Open Task Scheduler → Create Basic Task
2. Trigger: Monthly → Day 1
3. Action: `py "E:\path\to\run_pipeline.py" --email`

---

## 📬 Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Vaibhav%20Shankdhar-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/vaibhav-shankdhar-0602)
[![GitHub](https://img.shields.io/badge/GitHub-Shankdhar06-black?style=flat&logo=github)](https://github.com/Shankdhar06)
