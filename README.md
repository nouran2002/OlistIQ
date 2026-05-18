# 🟦 OlistIQ — AI-Powered Business Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-1A56FF?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00C853?style=for-the-badge)

**An end-to-end AI analytics platform that lets executives query business data in plain English.**  
Built on the real Olist Brazilian E-Commerce dataset (100k+ orders).

[📊 Live Demo](#) · [📁 Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) · [📬 Contact](#-author)

</div>

---

## 📌 Overview

**OlistIQ** is a fully agentic Business Intelligence system that transforms raw e-commerce data into boardroom-ready insights — instantly. Instead of static dashboards, decision-makers simply *ask* in plain English, and **Tommy** (the AI agent) reasons over the data, selects the right analytical tools, and returns precise, actionable answers.

> *"What caused the revenue drop in November?"*  
> *"Which product category had the highest ROAS this quarter?"*  
> *"Are we losing money on customer acquisition?"*  
> *"Run a full health check on the business."*

Tommy answers all of these — automatically, in seconds.

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚙️ **Automated ETL Pipeline** | OOP-based pipeline that loads, cleans, enriches, aggregates, and caches 100k+ records |
| 🤖 **Tommy AI Agent** | Conversational BI agent powered by Gemini 2.5 Flash with full autonomous tool use |
| 📊 **Live KPI Dashboard** | Real-time revenue, orders, customers, AOV, and retention — auto-refreshed |
| 🔍 **Statistical Anomaly Detection** | Spike/drop detection using the 2-sigma rule on daily sales |
| 📈 **Deep Sales Analysis** | Monthly trends, MoM growth %, top/bottom categories, root-cause engine |
| 💰 **Marketing Efficiency** | ROAS calculation, best/worst months, 3-month spend trend |
| 👥 **RFM Segmentation** | Champions / Loyal / New / At-Risk / Churned — with LTV per segment |
| 📉 **Unit Economics** | LTV, CAC, LTV/CAC ratio with health classification |
| 🚨 **Proactive Health Check** | Automated scan across Sales + Marketing + Customers on every startup |
| 💬 **Floating Chat Panel** | Robot button with 10 suggested questions + free-text input |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAW DATA  (Kaggle CSVs)                       │
│  orders · items · products · customers · payments · reviews      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               ETL_Pipeline.py  (OlistETLPipeline)               │
│                                                                  │
│  load_data() → clean() → enrich() → aggregate() → add_reviews() │
│                                                                  │
│  Output: final_gold_table.csv  (cached — skips on re-run)       │
└────────────────────────┬────────────────────────────────────────┘
                         │  pipeline.build()
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                tools_logic.py  (10 Analytical Tools)            │
│                                                                  │
│  final_gold_file = pipeline.build()   ← loaded once globally    │
│  _rfm_df = _build_rfm()               ← computed once at import │
│                                                                  │
│  Tool 1  get_revenue_by_range         Tool 6  analyze_sales     │
│  Tool 2  Top_selling_products         Tool 7  analyze_marketing  │
│  Tool 3  Detect_sales_anomalies       Tool 8  analyze_loyalty   │
│  Tool 4  generate_business_insights   Tool 9  health_check      │
│  Tool 5  compare_periods              Tool 10 quick_alerts      │
└────────────────────────┬────────────────────────────────────────┘
                         │ tool calls
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               Tommy — AI Agent  (Gemini 2.5 Flash)              │
│                                                                  │
│   Reads query → picks tool(s) → runs → interprets → answers     │
└────────────────────────┬────────────────────────────────────────┘
                         │ response
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit App  (app.py)                       │
│                                                                  │
│  Live KPIs · 4 Chart Tabs · Deep Analysis · Tommy Chat FAB      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **ETL Pipeline** | Python OOP — `OlistETLPipeline` class with 5 modular stages |
| **AI Agent** | Google Gemini 2.5 Flash — autonomous function calling |
| **Data Processing** | Python 3.10+, pandas, NumPy |
| **Visualization** | Plotly — area, bar, donut, bubble charts |
| **Frontend** | Streamlit + custom CSS (Olist dark enterprise theme) |
| **Customer Analytics** | RFM model — Recency, Frequency, Monetary |
| **Anomaly Detection** | Statistical — mean ± 2 standard deviations |
| **Marketing Analytics** | ROAS, CAC, LTV/CAC ratio |
| **Dataset** | Olist Brazilian E-Commerce Public Dataset (Kaggle) |
| **Secrets Management** | python-dotenv + `.env` |

---

## 📁 Repository Structure

```
olistiq/
│
├── app.py                    # Streamlit application — main entry point
│
├── ETL_Pipeline.py           # OlistETLPipeline — load, clean, enrich, aggregate
├── tools_logic.py            # 10 analytical tool functions (calls ETL on startup)
├── tools_schemas.py          # JSON schemas for Gemini function calling
├── tools_main_agent.py       # Terminal agent interface (dev/testing)
│
├── data/
│   ├── raw data/             # Original Kaggle CSV files (gitignored)
│   ├── final_gold_table.csv  # ETL output — cached gold layer (gitignored)
│   └── marketing_spend.csv   # Monthly marketing budget data (gitignored)
│
├── .env.example              # API key template — safe to commit
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ The ETL Pipeline

`ETL_Pipeline.py` implements a clean OOP pipeline with 5 stages:

| Stage | Method | What it does |
|---|---|---|
| 1 | `load_data()` | Reads all 8 raw Kaggle CSV files |
| 2 | `clean_orders_items_products()` | Strips whitespace, parses dates, drops nulls, removes zero-price rows, merges orders + items + products |
| 3 | `enrich()` | Joins customers, payments, sellers, category translation; fills missing values |
| 4 | `aggregate()` | Groups by order + product + payment type; sums revenue, freight, payment value |
| 5 | `add_reviews()` | Merges average review score per order |

**Smart caching:** On first run the pipeline builds and saves `final_gold_table.csv`. On every subsequent run it loads from cache instantly — no reprocessing.

```python
pipeline = OlistETLPipeline(data_path="data", output_path="output")
df = pipeline.build()         # builds once, loads from cache after
df = pipeline.build(force=True)  # force rebuild
```

---

## 🤖 The 10 Analytical Tools

Tommy autonomously calls any of these — alone or in combination:

| # | Tool | What it does |
|---|---|---|
| 1 | `get_revenue_by_range` | Total revenue between any two dates |
| 2 | `Top_selling_products` | Best-performing product category in a given period |
| 3 | `Detect_sales_anomalies` | Flags statistically unusual days using 2σ rule + identifies the driving category |
| 4 | `generate_business_insights` | Full RFM segment table — count, avg LTV, revenue contribution % |
| 5 | `compare_periods` | Side-by-side comparison of Revenue, Orders, Customers, AOV with Growth % |
| 6 | `analyze_sales_performance` | Monthly trends, sharpest MoM drop, root-cause by category (top losers & gainers) |
| 7 | `analyze_marketing_efficiency` | ROAS per month, best/worst marketing months, 3-month recent trend |
| 8 | `analyze_customer_loyalty` | Retention rate, avg LTV, avg CAC, LTV/CAC ratio with health classification |
| 9 | `get_business_health_check` | Full scan — CRITICAL / WARNING / INSIGHT alerts across sales, marketing, customers |
| 10 | `get_quick_alerts` | Lightweight startup scan — surfaces only flagged alerts for topbar notification |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/nouran2002/olistiq.git
cd olistiq
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
cp .env.example .env
# Open .env and add your Gemini API key
# Get one free at: https://aistudio.google.com
```

### 4. Download and place the raw data
Download the [Olist dataset from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place all CSV files in:
```
data/raw data/
```

Also place your marketing spend file at:
```
marketing_spend.csv   # columns: month_period (YYYY-MM), spend
```

### 5. Run the ETL pipeline (first time only)
```bash
python ETL_Pipeline.py
```
This builds `final_gold_table.csv` and caches it. All subsequent runs load from cache automatically.

### 6. Launch the app
```bash
streamlit run app.py
```

---

## 💡 Example Conversations with Tommy

```
You: What caused the revenue drop last November?

Tommy: Revenue fell 23.4% in November vs October.
       Root cause: furniture_decor dropped 41% — the largest single-category decline.
       bed_bath_table and computers_accessories also contracted.

       Recommendation: Investigate supply-chain issues in furniture_decor and
       consider a targeted end-of-year promotion to recover lost ground.
```

```
You: Is our marketing spend efficient?

Tommy: Average ROAS across all months: 3.8x

       Best month:  March 2018 — ROAS 6.2x ($12,400 spend → $76,880 revenue)
       Worst month: December 2016 — ROAS 0.9x (spending more than we earned)

       Recommendation: Reallocate budget away from Q4 2016 patterns.
       Focus spend on the March–May window where ROAS consistently exceeds 4x.
```

```
You: Are we losing money acquiring customers?

Tommy: LTV/CAC Ratio: 4.7x — Healthy ✅
       Avg LTV: $183.40  |  Avg CAC: $39.02
       Retention Rate: 3.1% — very low.

       Recommendation: Acquisition economics are strong, but retention is a risk.
       A post-purchase email sequence and loyalty program could move customers
       from New → Loyal and significantly increase LTV.
```

---

## 📊 Dashboard Walkthrough

**KPI Strip** — 5 live cards: Total Revenue · Total Orders · Unique Customers · Avg Order Value · Retention Rate. Each shows delta vs. previous month with color-coded direction.

**Tab 1 — Revenue & Trends:** Monthly revenue area chart · MoM growth bar chart (green/red) · Order volume trend.

**Tab 2 — Top Categories:** Horizontal bar chart (top 10 by revenue) · Donut chart (revenue share %).

**Tab 3 — Customer Segments:** RFM cards per segment · Revenue contribution bar chart · Count vs. Avg LTV bubble chart.

**Tab 4 — Deep Analysis:** Revenue range calculator · Top category finder · Anomaly date scanner · Period comparison table · Full health check runner.

---

## 🔐 Security

- API keys stored in `.env` locally — never committed
- On Streamlit Cloud: add `GEMINI_API_KEY` under **Settings → Secrets**
- Raw data and gold table are in `.gitignore` — never pushed

---

## 📦 Requirements

```
streamlit>=1.32.0
google-genai>=0.8.0
pandas>=2.0.0
numpy>=1.26.0
plotly>=5.18.0
python-dotenv>=1.0.0
pyarrow>=14.0.0
```

---

## 🗺️ Roadmap

- [ ] PDF report export — auto-generated monthly summary
- [ ] Email alerts for CRITICAL anomalies
- [ ] Forecasting module — next-month revenue prediction
- [ ] Multi-language support (Arabic / Portuguese)
- [ ] Role-based views — CEO vs. Marketing Manager vs. Operations

---

## 👩‍💻 Author

**[Nouran Waleed Mohamed]**  
Data Analyst → AI Data Analyst  
📧 nouran20602@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/nouran-waleed-0b0196210?utm_source=share_via&utm_content=profile&utm_medium=member_android) · 
[GitHub](https://github.com/nouran2002)

---

## 📄 License

This project is licensed under the MIT License.  
Dataset courtesy of [Olist](https://olist.com) via [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

---

<div align="center">
  Built with 🟦 Python · Gemini AI · Streamlit · Real Data<br>
  <b>OlistIQ — From Raw Data to Boardroom Decisions</b>
</div># OlistIQ
# OlistIQ
