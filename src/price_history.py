"""
Price History Module for PriceTruth
===================================
Manages historical price observations, data storage to CSV,
and interactive Plotly visualizations.
"""

import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Directory Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRICE_HISTORY_FILE = os.path.join(DATA_DIR, "price_history.csv")


def load_price_history():
    """
    Load the canonical price history CSV.
    
    Returns:
        pd.DataFrame: Clean DataFrame with columns [product_id, product_name,
                      store, price, recorded_date, category, brand, source].
    """
    if not os.path.exists(PRICE_HISTORY_FILE):
        return pd.DataFrame(columns=[
            "product_id", "product_name", "store", "price",
            "recorded_date", "category", "brand", "source"
        ])
    
    try:
        df = pd.read_csv(PRICE_HISTORY_FILE)
        # Ensure recorded_date is string
        df["recorded_date"] = df["recorded_date"].astype(str)
        # Ensure price is numeric float
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])
        return df
    except Exception as e:
        print(f"[Error] Failed to load {PRICE_HISTORY_FILE}: {e}")
        return pd.DataFrame(columns=[
            "product_id", "product_name", "store", "price",
            "recorded_date", "category", "brand", "source"
        ])


def save_price_observation(product_id, product_name, store, price, recorded_date=None, source="user_added", category="General", brand="Generic"):
    """
    Save a new price observation to data/price_history.csv.
    Validates inputs and prevents duplicate records for the same product, store, and date.
    Never overwrites existing historical records.
    
    Parameters:
        product_id (str): Unique product identifier or slug.
        product_name (str): Human-readable product name.
        store (str): 'Amazon' or 'Flipkart'.
        price (float): Price in INR.
        recorded_date (str, optional): Date in 'YYYY-MM-DD' format. Defaults to current date.
        source (str): Source tag ('user_added', 'manual', 'scraper', etc.).
        category (str): Product category.
        brand (str): Product brand.
        
    Returns:
        tuple: (bool, str) -> (success_flag, user_message)
    """
    # 1. Validation
    if not product_name or not str(product_name).strip():
        return False, "Validation Error: Product name is required."
        
    if not store or str(store).strip().title() not in ["Amazon", "Flipkart"]:
        return False, "Validation Error: Store must be 'Amazon' or 'Flipkart'."
        
    try:
        numeric_price = float(price)
        if numeric_price <= 0:
            return False, "Validation Error: Price must be a positive number greater than 0."
    except (ValueError, TypeError):
        return False, "Validation Error: Invalid price. Please enter a valid number."
        
    # Standardize store name
    std_store = "Amazon" if "amazon" in str(store).lower() else "Flipkart"
    
    # Standardize date
    if not recorded_date:
        recorded_date = datetime.now().strftime("%Y-%m-%d")
    else:
        try:
            dt = pd.to_datetime(str(recorded_date).strip())
            recorded_date = dt.strftime("%Y-%m-%d")
        except Exception:
            recorded_date = datetime.now().strftime("%Y-%m-%d")
            
    clean_prod_id = str(product_id).strip() if product_id else str(product_name).strip()[:10]
    clean_prod_name = str(product_name).strip()
    
    # 2. Check for duplicates in existing data
    existing_df = load_price_history()
    
    if not existing_df.empty:
        # Check duplicate condition: same product_id, store, and recorded_date
        duplicate_check = (
            (existing_df["product_id"].astype(str).str.lower() == clean_prod_id.lower()) &
            (existing_df["store"].astype(str).str.lower() == std_store.lower()) &
            (existing_df["recorded_date"].astype(str) == recorded_date)
        )
        if duplicate_check.any():
            return False, f"Duplicate Record: An observation for {clean_prod_name} at {std_store} on {recorded_date} already exists."
    
    # 3. Create new record DataFrame
    new_record = pd.DataFrame([{
        "product_id": clean_prod_id,
        "product_name": clean_prod_name,
        "store": std_store,
        "price": float(numeric_price),
        "recorded_date": recorded_date,
        "category": str(category).strip() or "General",
        "brand": str(brand).strip() or "Generic",
        "source": str(source).strip() or "user_added"
    }])
    
    # 4. Append to CSV safely
    try:
        if existing_df.empty:
            new_record.to_csv(PRICE_HISTORY_FILE, index=False, encoding="utf-8-sig")
        else:
            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
            # Ensure sort order
            updated_df = updated_df.sort_values(by=["recorded_date", "product_name"]).reset_index(drop=True)
            updated_df.to_csv(PRICE_HISTORY_FILE, index=False, encoding="utf-8-sig")
            
        return True, f"Success: Price observation for {clean_prod_name} ({std_store}: ₹{numeric_price:,.2f} on {recorded_date}) saved."
    except Exception as e:
        return False, f"Storage Error: Could not save observation: {e}"


def filter_history(df, product_identifier=None, start_date=None, end_date=None):
    """
    Filter historical observations by product identifier and optional date range.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    filtered = df.copy()
    
    # Filter product
    if product_identifier:
        p_str = str(product_identifier).strip().lower()
        mask = (
            filtered["product_id"].astype(str).str.lower() == p_str
        ) | (
            filtered["product_name"].astype(str).str.lower().str.contains(p_str, regex=False)
        )
        filtered = filtered[mask]
        
    # Filter dates
    if start_date:
        filtered = filtered[filtered["recorded_date"] >= str(start_date)]
    if end_date:
        filtered = filtered[filtered["recorded_date"] <= str(end_date)]
        
    return filtered.sort_values(by="recorded_date").reset_index(drop=True)


def create_price_history_chart(product_history_df, product_name):
    """
    Generate an interactive Plotly line chart of price history.
    
    Requirements:
    - X-axis: Date
    - Y-axis: Product price in INR
    - Separate lines for Amazon and Flipkart
    - Historical minimum price, maximum price, average price reference lines
    
    Parameters:
        product_history_df (pd.DataFrame): Filtered history for a specific product.
        product_name (str): Name of the product for the chart title.
        
    Returns:
        go.Figure: Interactive Plotly figure.
    """
    if product_history_df is None or product_history_df.empty:
        return None
        
    fig = go.Figure()
    
    # Store color palette
    store_colors = {
        "Amazon": "#FF9900",    # Amazon Orange
        "Flipkart": "#2874F0"    # Flipkart Blue
    }
    
    # 1. Add trace for each store
    for store_name in ["Amazon", "Flipkart"]:
        store_data = product_history_df[product_history_df["store"].str.lower() == store_name.lower()].copy()
        if not store_data.empty:
            store_data = store_data.sort_values(by="recorded_date")
            color = store_colors.get(store_name, "#555555")
            
            fig.add_trace(go.Scatter(
                x=store_data["recorded_date"],
                y=store_data["price"],
                mode="lines+markers",
                name=f"{store_name}",
                line=dict(color=color, width=3),
                marker=dict(size=9, symbol="circle", line=dict(width=1.5, color="#FFFFFF")),
                hovertemplate=f"<b>{store_name}</b><br>Date: %{{x}}<br>Price: ₹%{{y:,.2f}}<extra></extra>"
            ))
            
    # Calculate stats for reference lines
    all_prices = product_history_df["price"].dropna()
    if len(all_prices) > 0:
        min_p = float(all_prices.min())
        max_p = float(all_prices.max())
        avg_p = float(all_prices.mean())
        
        # Horizontal reference lines
        # Min Price (Green dashed)
        fig.add_hline(
            y=min_p,
            line_dash="dot",
            line_color="#10B981",
            annotation_text=f"Hist Min: ₹{min_p:,.0f}",
            annotation_position="bottom right",
            annotation_font=dict(size=11, color="#10B981")
        )
        
        # Max Price (Red dashed)
        if max_p != min_p:
            fig.add_hline(
                y=max_p,
                line_dash="dot",
                line_color="#EF4444",
                annotation_text=f"Hist Max: ₹{max_p:,.0f}",
                annotation_position="top right",
                annotation_font=dict(size=11, color="#EF4444")
            )
            
        # Average Price (Gray dashed)
        fig.add_hline(
            y=avg_p,
            line_dash="dash",
            line_color="#6B7280",
            annotation_text=f"Hist Avg: ₹{avg_p:,.0f}",
            annotation_position="top left",
            annotation_font=dict(size=11, color="#6B7280")
        )

    # Layout styling (Clean, white/light background, professional)
    fig.update_layout(
        title=dict(
            text=f"Historical Price Trend: <b>{product_name}</b>",
            font=dict(size=16, color="#1F2937", family="sans-serif")
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="#E5E7EB",
            linecolor="#D1D5DB",
            type="category"  # Clean discrete date spacing for sparse dates
        ),
        yaxis=dict(
            title="Price in INR (₹)",
            showgrid=True,
            gridcolor="#E5E7EB",
            linecolor="#D1D5DB",
            tickprefix="₹",
            tickformat=",.0f"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_store_avg_price_chart(store_stats_df):
    """
    Create a clean Plotly bar chart of average prices by store.
    """
    if store_stats_df is None or store_stats_df.empty:
        return None
        
    colors = ["#FF9900" if s == "Amazon" else "#2874F0" for s in store_stats_df["store"]]
    
    fig = go.Figure(data=[
        go.Bar(
            x=store_stats_df["store"],
            y=store_stats_df["Average_Price"],
            marker_color=colors,
            text=store_stats_df["Average_Price"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="auto"
        )
    ])
    
    fig.update_layout(
        title="Store-Wise Average Recorded Price",
        xaxis_title="Store",
        yaxis_title="Average Price (₹)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickprefix="₹", tickformat=",.0f"),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def create_category_distribution_chart(category_stats_df):
    """
    Create a clean Plotly horizontal bar chart of product count per category.
    """
    if category_stats_df is None or category_stats_df.empty:
        return None
        
    fig = px.bar(
        category_stats_df,
        x="Total_Observations",
        y="category",
        orientation="h",
        color="category",
        title="Category-Wise Observation Distribution",
        text="Total_Observations",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
        yaxis_title="Category",
        xaxis_title="Observations Count",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig
