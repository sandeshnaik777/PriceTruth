"""
PriceTruth - Indian E-commerce Price Comparison & Historical Price Analytics
=============================================================================
Main application entry point and Home Page.
Inspired by Buyhatke: clean, professional, beginner-friendly.
"""

import os
import sys
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.scraper_interface import (
    load_current_prices_catalog,
    get_all_available_products,
    get_current_prices
)
from src.price_history import load_price_history

# Page configuration
st.set_page_config(
    page_title="PriceTruth | Indian E-commerce Price Tracker",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Light, clean, Buyhatke-inspired UI)
st.markdown("""
<style>
    /* Main container clean styling */
    .main {
        background-color: #F9FAFB;
    }
    
    /* Brand Header */
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .brand-title span {
        color: #10B981;
    }
    .brand-subtitle {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    
    /* Product Cards */
    .product-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .product-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .product-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.3rem;
    }
    .product-meta {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 0.8rem;
    }
    
    /* Price tags */
    .price-badge-cheapest {
        background-color: #ECFDF5;
        color: #065F46;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-weight: 700;
        font-size: 1.05rem;
        border: 1px solid #A7F3D0;
    }
    .price-badge-regular {
        background-color: #F3F4F6;
        color: #374151;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Store Badges */
    .badge-amazon {
        background-color: #FFFBEB;
        color: #B45309;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #FDE68A;
    }
    .badge-flipkart {
        background-color: #EFF6FF;
        color: #1D4ED8;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid #BFDBFE;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []
if "selected_product" not in st.session_state:
    st.session_state["selected_product"] = None

# Sidebar Navigation Info
with st.sidebar:
    st.markdown("### 🏷️ **PriceTruth Navigation**")
    st.caption("Indian E-commerce Price Comparison & Analytics")
    st.markdown("---")
    st.markdown("""
    - 🏠 **Home**: Search & catalog overview
    - ⚖️ **Product Comparison**: Amazon vs Flipkart
    - 📈 **Price History**: Interactive Plotly trend chart
    - 📊 **Analytics Dashboard**: KPIs, store & category insights
    - ➕ **Add Price Observation**: Record new price data
    """)
    st.markdown("---")
    st.caption("💡 *Tip: Prices are retrieved in Indian Rupees (₹).*")

# Page Header
st.markdown("""
<div class="brand-title">
    Price<span>Truth</span> 🇮🇳
</div>
<div class="brand-subtitle">
    Honest Indian E-commerce price comparison & historical price tracking across Amazon India and Flipkart.
</div>
""", unsafe_allow_html=True)

# Load Catalog Data
current_df = load_current_prices_catalog()
history_df = load_price_history()

# Check if data exists
if current_df.empty:
    st.warning("⚠️ No current product listings found. Please load or import dataset in the data folder.")
    st.stop()

# Search Bar & Filter Section
col_search, col_cat, col_btn = st.columns([3, 2, 1])

with col_search:
    search_query = st.text_input(
        "Search for a product:",
        placeholder="e.g., iPhone 17, Samsung S25, HP Victus, boAt...",
        label_visibility="collapsed"
    )

# Categories
all_categories = ["All Categories"] + sorted(current_df["category"].dropna().unique().tolist())
with col_cat:
    selected_category = st.selectbox(
        "Filter by Category:",
        options=all_categories,
        index=0,
        label_visibility="collapsed"
    )

with col_btn:
    search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

# Filter logic
filtered_df = current_df.copy()

if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

if search_query:
    q = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["product_name"].astype(str).str.lower().str.contains(q) |
        filtered_df["brand"].astype(str).str.lower().str.contains(q) |
        filtered_df["category"].astype(str).str.lower().str.contains(q)
    ]
    # Track search in history
    if search_query.strip() not in st.session_state["search_history"]:
        st.session_state["search_history"].insert(0, search_query.strip())
        st.session_state["search_history"] = st.session_state["search_history"][:5]

# Recently Searched Products Pill Chips
if st.session_state["search_history"]:
    st.markdown("**Recent Searches:**")
    hist_cols = st.columns(len(st.session_state["search_history"]) + 1)
    for idx, item in enumerate(st.session_state["search_history"]):
        with hist_cols[idx]:
            if st.button(f"🕒 {item}", key=f"hist_{idx}"):
                st.session_state["selected_product"] = item
                st.switch_page("pages/1_Product_Comparison.py")

st.markdown("---")

# Display Catalog Results
st.subheader(f"Available Products ({len(filtered_df)} items found)")

if filtered_df.empty:
    st.info(f"No products found matching '{search_query}'. Try another search term or reset category filter.")
else:
    # 2-column card grid
    for idx, row in filtered_df.reset_index(drop=True).iterrows():
        p_name = row["product_name"]
        p_id = row["product_id"]
        cat = row.get("category", "General")
        brand = row.get("brand", "Generic")
        amz_p = row.get("amazon_price")
        fk_p = row.get("flipkart_price")
        cheapest_store = row.get("cheapest_store", "Unknown")
        price_diff = row.get("price_difference")
        
        with st.container():
            col_info, col_pricing, col_action = st.columns([4, 4, 2])
            
            with col_info:
                st.markdown(f"### {p_name}")
                st.markdown(f"🏷️ **Brand:** `{brand}` | 📂 **Category:** `{cat}` | 🆔 `{p_id}`")
                
            with col_pricing:
                p_cols = st.columns(2)
                with p_cols[0]:
                    if pd.notnull(amz_p):
                        is_amz_cheapest = "Amazon" in cheapest_store
                        style = "price-badge-cheapest" if is_amz_cheapest else "price-badge-regular"
                        st.markdown(f"<span class='badge-amazon'>Amazon India</span>", unsafe_allow_html=True)
                        st.markdown(f"<div class='{style}'>₹{amz_p:,.2f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='badge-amazon'>Amazon India</span>", unsafe_allow_html=True)
                        st.caption("❌ Unavailable")
                        
                with p_cols[1]:
                    if pd.notnull(fk_p):
                        is_fk_cheapest = "Flipkart" in cheapest_store
                        style = "price-badge-cheapest" if is_fk_cheapest else "price-badge-regular"
                        st.markdown(f"<span class='badge-flipkart'>Flipkart</span>", unsafe_allow_html=True)
                        st.markdown(f"<div class='{style}'>₹{fk_p:,.2f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span class='badge-flipkart'>Flipkart</span>", unsafe_allow_html=True)
                        st.caption("❌ Unavailable")
                        
                if pd.notnull(price_diff) and price_diff > 0:
                    st.caption(f"💰 Savings: **₹{price_diff:,.2f}** cheaper on **{cheapest_store}**")
                    
            with col_action:
                st.write("")
                if st.button("⚖️ Compare", key=f"cmp_{p_id}", use_container_width=True):
                    st.session_state["selected_product"] = p_name
                    st.switch_page("pages/1_Product_Comparison.py")
                if st.button("📈 Price History", key=f"hist_btn_{p_id}", use_container_width=True):
                    st.session_state["selected_product"] = p_name
                    st.switch_page("pages/2_Price_History.py")
                    
            st.markdown("<hr style='margin: 0.8rem 0; border: 0.5px solid #F3F4F6;'>", unsafe_allow_html=True)

