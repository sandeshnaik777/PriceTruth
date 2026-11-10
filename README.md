# 🏷️ PriceTruth: Indian E-commerce Price Comparison & Historical Price Analytics

> **Honest, transparent price tracking and historical price intelligence for Indian online shoppers.**  
> *Inspired by Buyhatke. Built with Python 3.12, Streamlit, Pandas, NumPy, and Plotly.*

---

## 📌 1. Project Overview

**PriceTruth** is a beginner-friendly Python Data Analytics application designed to help consumers make informed purchasing decisions on Indian e-commerce platforms (**Amazon India** and **Flipkart**). 

Online retail platforms often use dynamic pricing, artificial discounts, and flash sales that make it difficult for buyers to know whether a "deal" is genuinely cheap or temporarily marked up. PriceTruth provides:
1. **Live/Current Price Comparison**: Side-by-side pricing between Amazon India and Flipkart, highlighting the cheapest store and exact savings.
2. **Historical Price Analytics**: Tracking price movements over time to evaluate whether a current price is close to its all-time low.
3. **Price Intelligence Insights**: Rule-based purchase recommendations without false hype or speculative predictions.
4. **Observation Logging**: Storing new price points over time to continuously enrich historical price datasets.

---

## 🎯 2. Project Objectives

- **Empower Indian Shoppers**: Quickly identify the cheapest available platform for electronics, wearables, and gadgets.
- **Analyze Price Volatility**: Use Pandas and NumPy to compute statistical metrics (mean, median, min, max, standard deviation).
- **Distinguish Current vs. Historical**: Provide clear logical separation between current market listings and dated historical records.
- **Learn Practical Data Analytics**: Emphasize clean, readable Python code, proper exploratory data analysis (EDA), and transparent business logic without overengineering.

---

## 💻 3. Technology Stack

- **Language**: Python 3.12
- **Web Interface**: [Streamlit](https://streamlit.io/) (Multi-page web application)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Interactive Visualization**: [Plotly](https://plotly.com/python/) (Plotly Graph Objects & Express)
- **Data Storage**: CSV (Standard flat-file storage for historical & current datasets)
- **Version Control**: Git & GitHub

> **Strict Non-Dependencies**: No React, Node.js, Spring Boot, MongoDB, paid scraping APIs, Keepa, machine learning, or black-box AI algorithms. The application runs locally and deterministically.

---

## 📂 4. Project Folder Structure

```text
PriceTruth/
│
├── data/
│   ├── raw/                               # Original raw files from reference repository
│   │   ├── amazon_prices.csv
│   │   ├── flipkart_prices.csv
│   │   ├── merged_prices.csv
│   │   ├── price_history.csv
│   │   └── products.xlsx
│   ├── processed/                         # Cleaned and normalized datasets
│   │   ├── clean_price_history.csv
│   │   └── clean_current_prices.csv
│   ├── price_history.csv                  # Canonical historical observations storage
│   └── current_prices.csv                 # Active current comparison catalog
│
├── src/
│   ├── data_loader.py                     # CSV loading and exploratory data inspection
│   ├── data_cleaning.py                   # Data cleaning, currency parsing & normalization
│   ├── price_analysis.py                  # Statistical analysis, KPIs & purchase insights
│   ├── price_history.py                   # History queries, observation storage & Plotly charts
│   ├── scraper_interface.py               # Current price comparison search & CSV import
│   └── test_integration.py                # Unit and integration test suite
│
├── pages/
│   ├── 1_Product_Comparison.py            # Page 2: Store comparison & cheapest store finder
│   ├── 2_Price_History.py                 # Page 3: Interactive Plotly historical trend chart
│   ├── 3_Analytics.py                     # Page 4: KPI dashboard & market distribution
│   └── 4_Add_Price_Record.py              # Page 5: Add and save new price observations
│
├── app.py                                 # Page 1: Homepage, search bar, & category filter
├── requirements.txt                       # Python dependencies
├── README.md                              # Comprehensive project documentation
└── .gitignore                             # Git ignore rules
```

---

## 📊 5. Historical Data Source & Validation

The seed dataset originates from the GitHub repository:  
`https://github.com/datawithsaurabh/Price-Tracker`

### Comprehensive Data Audit & Inspection Findings:
1. **Raw Files Inspected**:
   - `amazon_prices.csv` (10 rows, 10 columns)
   - `flipkart_prices.csv` (10 rows, 10 columns)
   - `merged_prices.csv` (10 rows, 21 columns)
   - `price_history.csv` (19 rows, 21 columns in wide merged format)
2. **Date Coverage**:
   - Dates recorded: Exactly two dates — `2026-07-02` and `2026-07-12`.
   - Date range: 10 days between initial scrape and subsequent scrape.
3. **Products & Coverage**:
   - **Unique Products**: 10 products (`P001` through `P010`) covering smartphones (iPhone 17 Pro Max, Samsung Galaxy S25, OnePlus 13, Google Pixel 9a), laptops (HP Victus, Lenovo LOQ), audio (boAt Airdopes 181, Sony WH-CH520), and accessories (Apple Watch SE, Logitech M331 Mouse).
   - **Observations**: 9 products have 2 dates of data; `P007` (boAt Airdopes) was recorded only on 2026-07-12.
4. **Platform Representation**:
   - Both **Amazon India** and **Flipkart** are represented.
5. **Missing Values & Scraping Failures**:
   - In `amazon_prices.csv` on 2026-07-12, `P008` (Sony WH-CH520) and `P010` (Apple Watch SE) failed during scraping (`Status: Failed`), resulting in missing `Amazon_Price` values.
   - Flipkart scraping succeeded for all 10 products.
   - Total valid historical price points: **36 observations** (17 Amazon + 19 Flipkart).
6. **Data Integrity Guarantee**:
   - **Zero fabricated observations**: Historical observations preserve original dates and price values.
   - Standardized from wide format into a canonical long-format observation schema.

---

## 📑 6. Dataset Column Descriptions

### Historical Dataset (`data/price_history.csv`)
| Column Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `product_id` | String | Unique product identifier or slug | `P001` |
| `product_name` | String | Full brand & model name | `iPhone 17 Pro Max 1 TB` |
| `store` | String | Standardized store name (`Amazon` or `Flipkart`) | `Amazon` |
| `price` | Float | Price in Indian Rupees (INR) | `119900.0` |
| `recorded_date` | String | Date of observation (`YYYY-MM-DD`) | `2026-07-12` |
| `category` | String | Product category | `Smartphone` |
| `brand` | String | Manufacturer brand | `Apple` |
| `source` | String | Data provenance (`historical_seed`, `user_added`, `scraper`) | `historical_seed` |

### Current Price Comparison Catalog (`data/current_prices.csv`)
| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `product_id` | String | Product identifier |
| `product_name` | String | Product title |
| `category` | String | Category classification |
| `brand` | String | Manufacturer brand |
| `amazon_price` | Float | Current price on Amazon India (NaN if unavailable) |
| `flipkart_price` | Float | Current price on Flipkart (NaN if unavailable) |
| `amazon_url` | String | Amazon product listing link |
| `flipkart_url` | String | Flipkart product listing link |
| `recorded_date` | String | Date of price check |
| `cheapest_store` | String | Platform with lowest price (`Amazon`, `Flipkart`, `Tie`, or `Store (Only)`) |
| `price_difference`| Float | Absolute difference in INR between Amazon and Flipkart |
| `lowest_price` | Float | Minimum price available across stores |
| `highest_price` | Float | Maximum price available across stores |

---

## ⚠️ 7. Historical Data Limitations & Integrity Rules

- **Sparse Historical Snapshots**: The initial seed dataset contains snapshots from two dates (`2026-07-02` and `2026-07-12`). Moving averages and volatility metrics require multiple observation points; when fewer than 2 observations exist for a product, the application explicitly warns: *"Historical observations are insufficient to determine a price trend."*
- **No Speculative Predictions**: PriceTruth does not make unsupported future price predictions or claim fake "mega discounts".
- **Dynamic Growth**: As users record observations via the **Add Price Observation** page or import new CSV comparison batches, the historical dataset grows permanently without overwriting existing entries.

---

## 🖥️ 8. Application Pages & Features

### 🏠 Page 1: Home (`app.py`)
- Clean PriceTruth branding with Indian flag badge.
- Live search bar with instant keyword matching.
- Category filter dropdown (Smartphones, Laptops, Audio, Accessories).
- Recent search chips for quick navigation.
- Product card grid displaying side-by-side store pricing and savings badges.

### ⚖️ Page 2: Product Comparison (`pages/1_Product_Comparison.py`)
- Direct side-by-side comparison cards for Amazon India and Flipkart.
- **Cheapest store highlighted in green** with a prominent "LOWEST PRICE" badge.
- Higher store highlighted with higher price indication.
- Graceful handling when a product is unavailable or failed extraction on one platform.
- Metric summary cards: Cheapest Store, Lowest Price, Highest Price, Price Difference, and % Savings.
- Direct external link buttons to verify listings on Amazon or Flipkart.
- Collapsible CSV import interface to load fresh scraper output files.

### 📈 Page 3: Price History (`pages/2_Price_History.py`)
- Interactive **Plotly Line Chart**:
  - X-axis: Date
  - Y-axis: Product Price in INR (formatted as `₹`)
  - Amazon in brand Orange (`#FF9900`), Flipkart in brand Blue (`#2874F0`)
  - Dashed reference lines: Historical Minimum (Green), Historical Maximum (Red), Historical Average (Gray)
- Date range filter to zoom into specific time periods.
- Statistical summary cards: Lowest, Highest, Average, Median, Volatility (Standard Deviation).
- Rule-based **Purchase Intelligence Insight**:
  - *"All-Time Low"*: Current price is at or below historical minimum.
  - *"Close to Historical Low"*: Current price is within 5% of historical minimum.
  - *"Historical Peak"*: Current price is at its highest recorded price.
  - *"Above Average"*: Current price is above historical mean.
- Raw observation data table with provenance details.

### 📊 Page 4: Analytics Dashboard (`pages/3_Analytics.py`)
- **7 Core KPI Cards**: Total Products, Total Observations, Amazon Observations, Flipkart Observations, Average Recorded Price, Lowest Price, Highest Price.
- **Store-Wise Average Price**: Comparative bar chart of average pricing.
- **Category-Wise Distribution**: Observation count per category.
- **Top 10 Cheapest Products**: Budget-friendly product analysis.
- **Top 10 Most Expensive Products**: High-ticket product analysis.
- **Inter-Store Price Gap Distribution**: Histogram of actual Rupee savings available.
- **Macro Historical Price Trends**: Portfolio-wide price movement over time.
- Plain-English analytical explanations below each visualization.

### ➕ Page 5: Add Price Observation (`pages/4_Add_Price_Record.py`)
- Interactive form to record new price observations.
- Product selection (existing catalog or new custom product).
- Store selection (`Amazon` or `Flipkart`).
- Price input with numeric validation.
- Date picker (defaults to today's date).
- **Duplicate Prevention**: Prevents saving duplicate records for the same product, store, and date.
- Real-time success confirmation and instant database refresh.

---

## 🚀 9. Installation & Local Setup

### Prerequisites
- Python 3.12 (or Python 3.10+)
- Git installed on your system

### Step-by-Step Setup

1. **Clone or Navigate to the Repository**:
   ```bash
   cd c:\Code\DataAnalytics
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Environment & Run Test Suite**:
   ```bash
   python src/test_integration.py
   ```

5. **Launch the Application**:
   ```bash
   streamlit run app.py
   ```
   The application will start locally and open in your default browser at `http://localhost:8501`.

---

## 🧪 10. Verification & Integration Testing

The project includes an automated test suite in `src/test_integration.py` covering:
- Raw CSV loading and dataset inspection.
- Currency parsing (handling `₹`, `Rs.`, commas, decimals, and negative inputs).
- Statistical analysis functions (mean, median, min, max, std dev, percentage change).
- Purchase insight generation and boundary conditions.
- Scraper comparison interface (exact match, partial match, missing store, not found).
- Duplicate observation detection and storage integrity.
- Plotly figure generation.

To run tests:
```bash
python src/test_integration.py
```

---

## 🔮 11. Future Improvements

- **Automated Background Scraper**: Connect Playwright / BeautifulSoup scrapers via scheduled tasks.
- **Price Drop Email Alerts**: User email notifications when a product reaches its target price.
- **Expanded Store Coverage**: Include additional Indian platforms like Croma, Reliance Digital, and Tata CLiQ.
- **Coupon & Bank Offer Tracking**: Account for instant bank discounts (HDFC, ICICI, SBI credit card offers).

---

## 📜 12. License & Attribution

- **Reference Dataset**: [datawithsaurabh/Price-Tracker](https://github.com/datawithsaurabh/Price-Tracker)
- Built for educational and analytical purposes.

