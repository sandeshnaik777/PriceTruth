"""
PriceTruth - Page 1: Product Comparison
========================================
Compares current prices between Amazon India and Flipkart.
Highlights the cheapest store in green, shows price differences, and handles missing listings.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.scraper_interface import (
    load_current_prices_catalog,
    get_current_prices,
    import_current_prices_from_csv
)
from src.price_analysis import calculate_store_difference

st.set_page_config(
    page_title="Product Price Comparison | PriceTruth",
    page_icon="⚖️",
    layout="wide"
)

# Custom Styles
st.markdown("""
<style>
    .comparison-card {
        background-color: #FFFFFF;
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .card-cheapest {
        border-color: #10B981 !important;
        background-color: #F0FDF4 !important;
    }
    .price-value-cheapest {
        font-size: 2.2rem;
        font-weight: 800;
        color: #059669;
    }
    .price-value-regular {
        font-size: 2rem;
        font-weight: 700;
        color: #DC2626;
    }
    .deal-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-winner {
        background-color: #10B981;
        color: #FFFFFF;
    }
    .badge-higher {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ Current Price Comparison")
st.markdown("Compare current live product prices across **Amazon India** and **Flipkart**.")

# Load active catalog
catalog_df = load_current_prices_catalog()

if catalog_df.empty:
    st.warning("No product data available in current catalog. Please import a comparison CSV.")
    st.stop()

# Product Selection
product_list = sorted(catalog_df["product_name"].dropna().unique().tolist())

# Check session state from Home page
default_index = 0
if "selected_product" in st.session_state and st.session_state["selected_product"] in product_list:
    default_index = product_list.index(st.session_state["selected_product"])

col_select, col_search = st.columns([2, 1])

with col_select:
    selected_name = st.selectbox(
        "Select Product to Compare:",
        options=product_list,
        index=default_index
    )

with col_search:
    manual_search = st.text_input("Or search any product:", placeholder="Type name...")
    if manual_search:
        selected_name = manual_search.strip()

# Fetch current comparison data
comparison = get_current_prices(selected_name)

if comparison["status"] == "not_found":
    st.error(f"❌ {comparison['message']}")
    if "candidates" in comparison and comparison["candidates"]:
        st.info("Did you mean one of these available products?")
        for cand in comparison["candidates"]:
            if st.button(f"👉 {cand}", key=f"cand_{cand}"):
                st.session_state["selected_product"] = cand
                st.rerun()
    st.stop()
elif comparison["status"] == "multiple_matches":
    st.warning(f"⚠️ {comparison['message']}")
    st.write("Please choose your intended product:")
    for cand in comparison["candidates"]:
        if st.button(f"🔎 {cand}", key=f"multi_{cand}"):
            st.session_state["selected_product"] = cand
            st.rerun()
    st.stop()

# Display Selected Product Details
prod_name = comparison["product_name"]
category = comparison["category"]
brand = comparison["brand"]
rec_timestamp = comparison["retrieval_timestamp"]
cheapest_store = comparison["cheapest_store"]
price_diff = comparison["price_difference"]
lowest_price = comparison["lowest_price"]
highest_price = comparison["highest_price"]

st.markdown(f"## **{prod_name}**")
st.caption(f"🆔 **ID:** `{comparison['product_id']}` | 🏷️ **Brand:** `{brand}` | 📂 **Category:** `{category}` | 🕒 **Data As Of:** `{rec_timestamp}`")

st.markdown("---")

# Listings
amz = comparison["listings"]["Amazon"]
fk = comparison["listings"]["Flipkart"]

amz_available = amz["available"]
fk_available = fk["available"]

# Columns for side-by-side comparison
col_amz, col_fk = st.columns(2)

# Amazon Card
with col_amz:
    is_amz_winner = "Amazon" in cheapest_store
    card_class = "comparison-card card-cheapest" if is_amz_winner else "comparison-card"
    
    with st.container():
        st.markdown("### 🛒 Amazon India")
        if amz_available:
            p_val = amz["price"]
            if is_amz_winner:
                st.markdown("<span class='deal-badge badge-winner'>🏆 LOWEST PRICE</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='price-value-cheapest'>₹{p_val:,.2f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='deal-badge badge-higher'>HIGHER PRICE</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='price-value-regular'>₹{p_val:,.2f}</div>", unsafe_allow_html=True)
            
            st.markdown(f"**Status:** `Available`")
            if amz.get("url"):
                st.link_button("🌐 View on Amazon India", amz["url"], use_container_width=True)
        else:
            st.error("❌ **Listing Unavailable**")
            st.caption(f"Reason: {amz['status']}")

# Flipkart Card
with col_fk:
    is_fk_winner = "Flipkart" in cheapest_store
    card_class = "comparison-card card-cheapest" if is_fk_winner else "comparison-card"
    
    with st.container():
        st.markdown("### 🛍️ Flipkart")
        if fk_available:
            p_val = fk["price"]
            if is_fk_winner:
                st.markdown("<span class='deal-badge badge-winner'>🏆 LOWEST PRICE</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='price-value-cheapest'>₹{p_val:,.2f}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='deal-badge badge-higher'>HIGHER PRICE</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='price-value-regular'>₹{p_val:,.2f}</div>", unsafe_allow_html=True)
            
            st.markdown(f"**Status:** `Available`")
            if fk.get("url"):
                st.link_button("🌐 View on Flipkart", fk["url"], use_container_width=True)
        else:
            st.error("❌ **Listing Unavailable**")
            st.caption(f"Reason: {fk['status']}")

st.markdown("---")

# Summary Comparison Metrics Card
st.markdown("### 📊 Comparison Summary")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.metric("🏆 Cheapest Store", cheapest_store)

with m_col2:
    if lowest_price:
        st.metric("🏷️ Lowest Available Price", f"₹{lowest_price:,.2f}")
    else:
        st.metric("🏷️ Lowest Available Price", "N/A")

with m_col3:
    if highest_price:
        st.metric("📈 Highest Available Price", f"₹{highest_price:,.2f}")
    else:
        st.metric("📈 Highest Available Price", "N/A")

with m_col4:
    if price_diff is not None and price_diff > 0:
        # Calculate percentage savings
        pct_savings = (price_diff / highest_price) * 100 if highest_price else 0
        st.metric(
            "💰 Price Difference",
            f"₹{price_diff:,.2f}",
            delta=f"-{pct_savings:.1f}% savings",
            delta_color="normal"
        )
    elif price_diff == 0:
        st.metric("💰 Price Difference", "₹0.00", delta="Identical Price")
    else:
        st.metric("💰 Price Difference", "N/A (Single Store)")

# Direct button to jump to Price History
st.markdown("---")
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.info("💡 Want to know if this is a good time to buy? Check the historical price fluctuations.")
with h_col2:
    if st.button("📈 View Historical Trend", type="primary", use_container_width=True):
        st.session_state["selected_product"] = prod_name
        st.switch_page("pages/2_Price_History.py")

# CSV Import Section (Collapsible for scraper integration)
with st.expander("📥 Import Fresh Scraper Comparison Results (CSV)"):
    st.markdown("""
    You can import a freshly generated CSV with current product prices.
    The file should have columns for Product ID/Name, Amazon Price, and Flipkart Price.
    """)
    uploaded_file = st.file_uploader("Upload Scraper Output CSV", type=["csv"])
    if uploaded_file is not None:
        success, new_df, msg = import_current_prices_from_csv(uploaded_file)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

