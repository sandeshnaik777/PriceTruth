"""
PriceTruth - Page 4: Add Price Observation
===========================================
Allows users to record new price observations to data/price_history.csv.
Validates all inputs, prevents duplicate entries for the same product, store, and date,
and displays clear success/error messages.
"""

import os
import sys
from datetime import datetime, date
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.price_history import save_price_observation, load_price_history
from src.scraper_interface import load_current_prices_catalog

st.set_page_config(
    page_title="Add Price Observation | PriceTruth",
    page_icon="➕",
    layout="wide"
)

st.title("➕ Add New Price Observation")
st.markdown("""
Record a verified price point for a product to build your historical price dataset.
All saved records are permanently appended to `data/price_history.csv` without overwriting existing data.
""")

# Load existing products for autocomplete
current_df = load_current_prices_catalog()
history_df = load_price_history()

known_products = set()
if not current_df.empty and "product_name" in current_df.columns:
    known_products.update(current_df["product_name"].dropna().unique().tolist())
if not history_df.empty and "product_name" in history_df.columns:
    known_products.update(history_df["product_name"].dropna().unique().tolist())

product_options = ["-- New Custom Product --"] + sorted(list(known_products))

# Form
with st.form("add_observation_form", clear_on_submit=False):
    st.markdown("### 📝 Observation Details")
    
    col_prod_type, col_store = st.columns(2)
    
    with col_prod_type:
        selected_prod_option = st.selectbox(
            "Select Existing Product (or choose 'New Custom Product'):",
            options=product_options
        )
        
    with col_store:
        store = st.selectbox(
            "Store Name:",
            options=["Amazon", "Flipkart"],
            index=0
        )
        
    # If custom product or existing
    if selected_prod_option == "-- New Custom Product --":
        col_name, col_id = st.columns([3, 1])
        with col_name:
            product_name = st.text_input("Enter Product Name *:", placeholder="e.g. Sony WH-1000XM5 Headphones")
        with col_id:
            product_id = st.text_input("Product ID (optional):", placeholder="e.g. P011")
        
        col_cat, col_brand = st.columns(2)
        with col_cat:
            category = st.text_input("Category (optional):", placeholder="e.g. Headphones")
        with col_brand:
            brand = st.text_input("Brand (optional):", placeholder="e.g. Sony")
    else:
        product_name = selected_prod_option
        # Try to find existing product_id and category
        match = history_df[history_df["product_name"] == product_name]
        if not match.empty:
            product_id = match["product_id"].iloc[0]
            category = match["category"].iloc[0] if "category" in match.columns else "General"
            brand = match["brand"].iloc[0] if "brand" in match.columns else "Generic"
        else:
            product_id = product_name[:10].replace(" ", "_")
            category = "General"
            brand = "Generic"
            
        st.info(f"Adding observation for: **{product_name}** (`ID: {product_id}` | `Category: {category}` | `Brand: {brand}`)")

    col_price, col_date = st.columns(2)
    
    with col_price:
        price = st.number_input(
            "Recorded Price in INR (₹) *:",
            min_value=1.0,
            max_value=10000000.0,
            value=1999.0,
            step=10.0,
            format="%.2f"
        )
        
    with col_date:
        obs_date = st.date_input(
            "Observation Date *:",
            value=date.today(),
            max_value=date.today()
        )
        
    source = "user_added"
    
    st.markdown("---")
    submitted = st.form_submit_button("💾 Save Observation", type="primary", use_container_width=True)

# Submission Handling and Validation
if submitted:
    if not product_name or not product_name.strip():
        st.error("❌ Validation Error: Product Name cannot be empty.")
    elif price <= 0:
        st.error("❌ Validation Error: Price must be a positive number greater than 0.")
    else:
        date_str = obs_date.strftime("%Y-%m-%d")
        
        success, message = save_price_observation(
            product_id=product_id if product_id else product_name.strip()[:10],
            product_name=product_name.strip(),
            store=store,
            price=float(price),
            recorded_date=date_str,
            source=source,
            category=category if category else "General",
            brand=brand if brand else "Generic"
        )
        
        if success:
            st.success(f"🎉 {message}")
            st.balloons()
            st.info("You can now view this updated price point in the **Price History** and **Analytics Dashboard** pages.")
        else:
            st.error(f"⚠️ {message}")

st.markdown("---")

# Recent observations table
st.subheader("📋 Recent Price Observations in Database")
updated_history = load_price_history()
if not updated_history.empty:
    recent_entries = updated_history.tail(10).iloc[::-1]
    
    display_recent = recent_entries[[
        "recorded_date", "product_name", "store", "price", "category", "source"
    ]].copy()
    display_recent["price"] = display_recent["price"].apply(lambda p: f"₹{p:,.2f}")
    
    st.dataframe(display_recent, use_container_width=True, hide_index=True)
else:
    st.write("No price observations recorded yet.")
