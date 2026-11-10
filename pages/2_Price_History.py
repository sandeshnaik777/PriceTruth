"""
PriceTruth - Page 2: Price History
==================================
Displays interactive Plotly line charts showing historical price trends across
Amazon India and Flipkart. Includes statistical summaries and rule-based purchase insights.
"""

import os
import sys
from datetime import datetime
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.price_history import (
    load_price_history,
    filter_history,
    create_price_history_chart
)
from src.price_analysis import (
    get_product_historical_summary,
    calculate_percentage_difference
)
from src.scraper_interface import get_current_prices, load_current_prices_catalog

st.set_page_config(
    page_title="Price History & Analytics | PriceTruth",
    page_icon="📈",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .insight-card {
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1.25rem;
        border: 1px solid #E5E7EB;
    }
    .insight-green {
        background-color: #ECFDF5;
        border-color: #10B981;
        color: #065F46;
    }
    .insight-red {
        background-color: #FEF2F2;
        border-color: #EF4444;
        color: #991B1B;
    }
    .insight-orange {
        background-color: #FFFBEB;
        border-color: #F59E0B;
        color: #92400E;
    }
    .insight-gray {
        background-color: #F9FAFB;
        border-color: #D1D5DB;
        color: #374151;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Historical Price Trends & Analytics")
st.markdown("Track how product prices have changed over time across **Amazon India** and **Flipkart**.")

# Load historical data
history_df = load_price_history()
catalog_df = load_current_prices_catalog()

# Collect product names from both current catalog and history
all_product_names = set()
if not catalog_df.empty and "product_name" in catalog_df.columns:
    all_product_names.update(catalog_df["product_name"].dropna().unique().tolist())
if not history_df.empty and "product_name" in history_df.columns:
    all_product_names.update(history_df["product_name"].dropna().unique().tolist())

all_product_names = sorted(list(all_product_names))

if not all_product_names:
    st.info("Historical price data is not available for this product yet.")
    st.stop()

# Product Selection
default_idx = 0
if "selected_product" in st.session_state and st.session_state["selected_product"] in all_product_names:
    default_idx = all_product_names.index(st.session_state["selected_product"])

col_sel, col_date = st.columns([2, 2])

with col_sel:
    selected_product = st.selectbox(
        "Select Product to Analyze:",
        options=all_product_names,
        index=default_idx
    )

# Filter product records
product_records = filter_history(history_df, selected_product)

# Check if historical data exists for this specific product
if product_records.empty:
    st.warning("Historical price data is not available for this product yet.")
    st.info("💡 You can record initial historical price observations for this product on the **Add Price Observation** page.")
    st.stop()

# Date Range Filter
unique_dates = sorted(product_records["recorded_date"].unique().tolist())
min_date = pd.to_datetime(unique_dates[0]).date()
max_date = pd.to_datetime(unique_dates[-1]).date()

with col_date:
    if min_date == max_date:
        st.write(f"📅 **Recorded Date:** `{min_date}` (Single recording date available)")
        date_range = [min_date, max_date]
    else:
        date_range = st.date_input(
            "Filter Date Range:",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

# Apply Date Filter if valid range selected
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_records = filter_history(product_records, selected_product, start_d, end_d)
else:
    filtered_records = product_records.copy()

if filtered_records.empty:
    st.warning("No price observations found within the selected date range.")
    st.stop()

# Get current price comparison to calculate current vs historical
current_info = get_current_prices(selected_product)
current_lowest = current_info.get("lowest_price") if current_info.get("status") == "success" else None

# Compute Historical Summary
summary = get_product_historical_summary(selected_product, filtered_records, current_price=current_lowest)
stats = summary["overall_stats"]
insight = summary["insight"]

# 1. Purchase Insight Banner
insight_color = insight.get("color", "gray")
style_class = f"insight-{insight_color}"

st.markdown(f"""
<div class="insight-card {style_class}">
    <h4 style="margin: 0 0 0.3rem 0;">💡 Price Intelligence Insight: <b>{insight['badge']}</b></h4>
    <p style="margin: 0; font-size: 1.05rem;">{insight['message']}</p>
</div>
""", unsafe_allow_html=True)

# 2. Historical KPI Metrics Row
st.markdown("### 📊 Historical Price Statistics")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric("🟢 Lowest Price", f"₹{stats['min']:,.2f}")
    
with kpi2:
    st.metric("🔴 Highest Price", f"₹{stats['max']:,.2f}")
    
with kpi3:
    st.metric("🔵 Average Price", f"₹{stats['mean']:,.2f}")
    
with kpi4:
    st.metric("⚖️ Median Price", f"₹{stats['median']:,.2f}")
    
with kpi5:
    volatility = stats["std"]
    st.metric("⚡ Price Volatility (Std Dev)", f"₹{volatility:,.2f}" if volatility > 0 else "₹0.00")

# Compare Current Price vs Historical Minimum
if current_lowest is not None and pd.notnull(stats["min"]):
    diff_from_min = calculate_percentage_difference(current_lowest, stats["min"])
    st.markdown("---")
    c_col1, c_col2 = st.columns([2, 3])
    with c_col1:
        st.markdown(f"**Current Lowest Price:** `₹{current_lowest:,.2f}`")
        st.markdown(f"**Historical Minimum Price:** `₹{stats['min']:,.2f}`")
    with c_col2:
        if diff_from_min == 0:
            st.success("🎉 Current price is exactly at its historical lowest recorded price!")
        elif diff_from_min < 0:
            st.success(f"🔥 Current price is {-diff_from_min:.1f}% below the previous historical low! Best price ever.")
        elif diff_from_min <= 5:
            st.success(f"✅ Current price is within {diff_from_min:.1f}% of its historical minimum.")
        else:
            st.warning(f"⚠️ Current price is {diff_from_min:.1f}% higher than its recorded historical minimum.")

st.markdown("---")

# 3. Interactive Plotly Line Chart
st.markdown("### 📉 Historical Price Chart")
fig = create_price_history_chart(filtered_records, selected_product)

if fig:
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Historical price data is not available for this product yet.")

st.caption("ℹ️ *Chart details: Solid lines represent recorded price points per store. Dashed lines illustrate historical minimum (green), maximum (red), and average (gray).*")

# 4. Raw Historical Observations Table
with st.expander("📋 View Raw Historical Records Table"):
    st.markdown(f"**Total observations recorded for {selected_product}:** {len(filtered_records)}")
    
    display_df = filtered_records[[
        "recorded_date", "store", "price", "category", "brand", "source"
    ]].sort_values(by="recorded_date", ascending=False)
    
    display_df["price"] = display_df["price"].apply(lambda p: f"₹{p:,.2f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

