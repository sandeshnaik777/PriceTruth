"""
PriceTruth - Page 3: Analytics Dashboard
========================================
High-level data analytics dashboard for Indian E-commerce price behavior.
Built using Pandas, NumPy, and Plotly.
Displays 7 core KPI cards, store-wise stats, category distributions,
top cheapest/expensive products, discount distributions, and historical trends.
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.price_history import (
    load_price_history,
    create_store_avg_price_chart,
    create_category_distribution_chart
)
from src.price_analysis import (
    compute_kpi_metrics,
    compute_store_wise_summary,
    compute_category_wise_summary,
    get_top_products_by_price
)
from src.scraper_interface import load_current_prices_catalog

st.set_page_config(
    page_title="Analytics Dashboard | PriceTruth",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Price Analytics & Market Intelligence")
st.markdown("Macro-level exploratory data analysis across Indian E-commerce price observations.")

# Load datasets
history_df = load_price_history()
current_df = load_current_prices_catalog()

if history_df.empty:
    st.warning("⚠️ No historical data available. Please add observations or check dataset.")
    st.stop()

# 1. KPI Cards Row (7 Required KPI metrics)
kpis = compute_kpi_metrics(history_df, current_df)

st.markdown("### 📌 Key Performance Indicators (KPIs)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📦 Total Tracked Products", f"{kpis['total_products']}")
with col2:
    st.metric("📝 Total Historical Observations", f"{kpis['total_observations']}")
with col3:
    st.metric("🛒 Amazon Observations", f"{kpis['amazon_observations']}")
with col4:
    st.metric("🛍️ Flipkart Observations", f"{kpis['flipkart_observations']}")

col5, col6, col7 = st.columns(3)
with col5:
    st.metric("📊 Average Recorded Price", f"₹{kpis['avg_recorded_price']:,.2f}")
with col6:
    st.metric("🟢 Lowest Recorded Price", f"₹{kpis['lowest_recorded_price']:,.2f}")
with col7:
    st.metric("🔴 Highest Recorded Price", f"₹{kpis['highest_recorded_price']:,.2f}")

st.markdown("---")

# 2. Charts Row: Store-wise Average Price & Category Distribution
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("🛒 Store-Wise Average Price")
    store_summary = compute_store_wise_summary(history_df)
    fig_store = create_store_avg_price_chart(store_summary)
    if fig_store:
        st.plotly_chart(fig_store, use_container_width=True)
    
    st.caption("""
    **Insight & Explanation:**
    This chart compares the arithmetic mean price across all recorded observations for Amazon India versus Flipkart.
    Differences reflect both platform-specific discounts and cases where certain high-ticket product listings were successfully tracked on one platform versus the other.
    """)

with col_chart2:
    st.subheader("📂 Category-Wise Product Distribution")
    cat_summary = compute_category_wise_summary(history_df)
    fig_cat = create_category_distribution_chart(cat_summary)
    if fig_cat:
        st.plotly_chart(fig_cat, use_container_width=True)
        
    st.caption("""
    **Insight & Explanation:**
    Shows the concentration of observations across consumer product categories (Smartphones, Laptops, Earbuds, Accessories).
    Categories with higher observation counts provide higher confidence for price fluctuation analysis.
    """)

st.markdown("---")

# 3. Top 10 Cheapest vs Most Expensive Products
st.subheader("🏷️ Price Spectrum: Top Products")
t_col1, t_col2 = st.columns(2)

with t_col1:
    st.markdown("#### 🟢 Top 10 Cheapest Products")
    cheapest_prods = get_top_products_by_price(history_df, n=10, ascending=True)
    
    fig_cheap = px.bar(
        cheapest_prods,
        x="avg_price",
        y="product_name",
        orientation="h",
        text="avg_price",
        color="avg_price",
        color_continuous_scale="Greens_r"
    )
    fig_cheap.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(title="Average Price (₹)", tickprefix="₹", tickformat=",.0f"),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    fig_cheap.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_cheap, use_container_width=True)
    st.caption("**Explanation:** Highlights budget-friendly items in the catalog (e.g. computer accessories and audio wearables).")

with t_col2:
    st.markdown("#### 🔴 Top 10 Most Expensive Products")
    expensive_prods = get_top_products_by_price(history_df, n=10, ascending=False)
    
    fig_exp = px.bar(
        expensive_prods,
        x="avg_price",
        y="product_name",
        orientation="h",
        text="avg_price",
        color="avg_price",
        color_continuous_scale="Reds"
    )
    fig_exp.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(title="Average Price (₹)", tickprefix="₹", tickformat=",.0f"),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    fig_exp.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig_exp, use_container_width=True)
    st.caption("**Explanation:** Highlights premium electronics (flagship smartphones and gaming laptops) where inter-store price gaps have the highest absolute Rupee impact.")

st.markdown("---")

# 4. Discount Distribution Chart (if valid discount/difference data exists)
st.subheader("💰 Store Price Difference & Savings Distribution")

if not current_df.empty and "price_difference" in current_df.columns:
    valid_diffs = current_df.dropna(subset=["price_difference"])
    valid_diffs = valid_diffs[valid_diffs["price_difference"] > 0]
    
    if not valid_diffs.empty:
        d_col1, d_col2 = st.columns([3, 2])
        
        with d_col1:
            fig_diff = px.histogram(
                valid_diffs,
                x="price_difference",
                nbins=10,
                color="cheapest_store",
                title="Distribution of Inter-Store Price Differences (INR)",
                labels={"price_difference": "Price Difference (₹)", "cheapest_store": "Cheapest Platform"},
                color_discrete_map={"Amazon": "#FF9900", "Flipkart": "#2874F0"}
            )
            fig_diff.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                xaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickprefix="₹", tickformat=",.0f"),
                yaxis=dict(showgrid=True, gridcolor="#F3F4F6", title="Number of Products")
            )
            st.plotly_chart(fig_diff, use_container_width=True)
            
        with d_col2:
            st.markdown("#### 💡 Price Gap Summary")
            avg_gap = valid_diffs["price_difference"].mean()
            max_gap = valid_diffs["price_difference"].max()
            max_gap_prod = valid_diffs.loc[valid_diffs["price_difference"].idxmax()]["product_name"]
            
            st.write(f"Across **{len(valid_diffs)}** products available on both stores:")
            st.write(f"- **Mean Price Gap:** `₹{avg_gap:,.2f}`")
            st.write(f"- **Largest Price Gap:** `₹{max_gap:,.2f}` on *{max_gap_prod}*")
            
            # Platform breakdown
            amz_wins = (valid_diffs["cheapest_store"] == "Amazon").sum()
            fk_wins = (valid_diffs["cheapest_store"] == "Flipkart").sum()
            st.write(f"- **Amazon Cheaper:** {amz_wins} products")
            st.write(f"- **Flipkart Cheaper:** {fk_wins} products")
            
        st.caption("""
        **Explanation:**
        This distribution shows how much a consumer saves by cross-checking prices between Amazon India and Flipkart before purchasing.
        In several high-value categories, price differences exceed ₹10,000, underscoring the importance of real-time price comparison.
        """)
    else:
        st.info("No inter-store price difference data currently available.")
else:
    st.info("Discount data is not available.")

st.markdown("---")

# 5. Historical Price Trend Over Time
st.subheader("📅 Macro Historical Price Trends Over Time")

trend_df = history_df.groupby(["recorded_date", "store"])["price"].mean().reset_index()

fig_macro = px.line(
    trend_df,
    x="recorded_date",
    y="price",
    color="store",
    markers=True,
    title="Average Recorded Price Trend by Store Over Time",
    labels={"recorded_date": "Observation Date", "price": "Average Recorded Price (₹)", "store": "Platform"},
    color_discrete_map={"Amazon": "#FF9900", "Flipkart": "#2874F0"}
)
fig_macro.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    xaxis=dict(showgrid=True, gridcolor="#F3F4F6", type="category"),
    yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickprefix="₹", tickformat=",.0f")
)
st.plotly_chart(fig_macro, use_container_width=True)
st.caption("""
**Explanation:**
Tracks the movement of the average portfolio price on recorded scrape dates.
As additional observations are added through the *Add Price Observation* tool, this trend will dynamically extend across longer time horizons.
""")

