"""
Price Analysis Module for PriceTruth
====================================
Performs statistical analysis, price comparisons, and rule-based purchase insights
using Pandas and NumPy.
All calculations are strictly derived from real dataset records.
"""

import numpy as np
import pandas as pd


def calculate_price_statistics(price_series):
    """
    Calculate fundamental descriptive statistics for a series of prices.
    
    Parameters:
        price_series (pd.Series or list): Series of numeric prices.
        
    Returns:
        dict: Mean, median, min, max, standard deviation, and count.
    """
    if price_series is None or len(price_series) == 0:
        return {
            "count": 0,
            "mean": np.nan,
            "median": np.nan,
            "min": np.nan,
            "max": np.nan,
            "std": np.nan
        }
    
    # Ensure pandas Series with numeric type
    s = pd.Series(price_series).dropna()
    s = s[s > 0]
    
    if len(s) == 0:
        return {
            "count": 0,
            "mean": np.nan,
            "median": np.nan,
            "min": np.nan,
            "max": np.nan,
            "std": np.nan
        }
    
    return {
        "count": int(s.count()),
        "mean": float(np.round(s.mean(), 2)),
        "median": float(np.round(s.median(), 2)),
        "min": float(np.round(s.min(), 2)),
        "max": float(np.round(s.max(), 2)),
        # Sample standard deviation (ddof=1 if count > 1, else 0.0)
        "std": float(np.round(s.std(ddof=1), 2)) if len(s) > 1 else 0.0
    }


def calculate_percentage_difference(current_price, base_price):
    """
    Calculate percentage difference between current price and a base price (e.g. historical min).
    Formula: ((current_price - base_price) / base_price) * 100
    
    Parameters:
        current_price (float): The current price.
        base_price (float): The baseline price (min, avg, etc.).
        
    Returns:
        float: Percentage difference, or np.nan if base_price is invalid.
    """
    if pd.isna(current_price) or pd.isna(base_price) or base_price <= 0:
        return np.nan
    
    pct = ((current_price - base_price) / base_price) * 100.0
    return float(np.round(pct, 2))


def calculate_store_difference(amazon_price, flipkart_price):
    """
    Calculate the difference between Amazon and Flipkart prices.
    Formula: Amazon Price - Flipkart Price
    
    Parameters:
        amazon_price (float): Current price on Amazon.
        flipkart_price (float): Current price on Flipkart.
        
    Returns:
        dict: difference (Amazon - Flipkart), absolute difference, and percentage difference.
    """
    if pd.isna(amazon_price) or pd.isna(flipkart_price):
        return {
            "difference": np.nan,
            "abs_difference": np.nan,
            "pct_difference": np.nan,
            "cheaper_store": "Only one store available" if pd.notnull(amazon_price) or pd.notnull(flipkart_price) else "Neither available"
        }
    
    diff = float(np.round(amazon_price - flipkart_price, 2))
    abs_diff = abs(diff)
    
    # Base for percentage comparison is lower price
    lower_price = min(amazon_price, flipkart_price)
    pct_diff = np.round((abs_diff / lower_price) * 100.0, 2) if lower_price > 0 else 0.0
    
    if amazon_price < flipkart_price:
        cheaper_store = "Amazon"
    elif flipkart_price < amazon_price:
        cheaper_store = "Flipkart"
    else:
        cheaper_store = "Tie (Same Price)"
        
    return {
        "difference": diff,
        "abs_difference": abs_diff,
        "pct_difference": float(pct_diff),
        "cheaper_store": cheaper_store
    }


def calculate_moving_average(price_series, window=2):
    """
    Calculate a simple rolling moving average for a series of prices.
    
    Parameters:
        price_series (pd.Series or list): Ordered sequence of prices.
        window (int): Rolling window size.
        
    Returns:
        pd.Series: Rolling moving average values.
    """
    s = pd.Series(price_series).dropna()
    if len(s) < window:
        # Not enough observations for rolling window
        return s
    return s.rolling(window=window, min_periods=1).mean().round(2)


def generate_purchase_insight(current_price, min_price, max_price, avg_price, observation_count):
    """
    Generate honest, rule-based purchase insights based on historical price data.
    Does not make false discount claims or future price predictions.
    
    Parameters:
        current_price (float): Current available price.
        min_price (float): Historical minimum recorded price.
        max_price (float): Historical maximum recorded price.
        avg_price (float): Historical average recorded price.
        observation_count (int): Number of historical observations available.
        
    Returns:
        dict: 'badge' (e.g. 'Great Deal', 'Fair Price', 'High Price', 'Insufficient Data'),
              'message' (detailed explanation),
              'color' ('green', 'orange', 'red', 'gray')
    """
    if pd.isna(current_price) or current_price <= 0:
        return {
            "badge": "Price Unavailable",
            "message": "Current price could not be retrieved for this product.",
            "color": "gray"
        }
        
    if observation_count < 2 or pd.isna(min_price) or pd.isna(avg_price):
        return {
            "badge": "Insufficient Data",
            "message": "Historical observations are insufficient to determine a price trend (less than 2 recorded dates).",
            "color": "gray"
        }
    
    # 1. At or below historical minimum
    if current_price <= min_price:
        return {
            "badge": "All-Time Low",
            "message": f"The current price (₹{current_price:,.2f}) is at or below its historical minimum recorded price (₹{min_price:,.2f}). Excellent time to buy!",
            "color": "green"
        }
        
    # 2. Within 5% of historical minimum
    margin = min_price * 1.05
    if current_price <= margin:
        diff_pct = calculate_percentage_difference(current_price, min_price)
        return {
            "badge": "Close to Historical Low",
            "message": f"The current price is only {diff_pct:.1f}% above its historical low (₹{min_price:,.2f}). This is an attractive buying opportunity.",
            "color": "green"
        }
        
    # 3. At or near historical maximum
    if current_price >= max_price:
        return {
            "badge": "Historical Peak",
            "message": f"The current price (₹{current_price:,.2f}) is at its highest recorded historical price (₹{max_price:,.2f}). You may want to wait for upcoming sales.",
            "color": "red"
        }
        
    # 4. Higher than historical average
    if current_price > avg_price:
        diff_pct = calculate_percentage_difference(current_price, avg_price)
        return {
            "badge": "Above Average",
            "message": f"The current price is {diff_pct:.1f}% higher than the historical average (₹{avg_price:,.2f}).",
            "color": "orange"
        }
        
    # 5. Below historical average
    diff_pct = calculate_percentage_difference(current_price, avg_price)
    return {
        "badge": "Fair Deal",
        "message": f"The current price is below the historical average by {abs(diff_pct):.1f}% (Average: ₹{avg_price:,.2f}, Low: ₹{min_price:,.2f}).",
        "color": "green"
    }


def get_product_historical_summary(product_name_or_id, history_df, current_price=None):
    """
    Compute comprehensive historical analytics for a specific product.
    
    Parameters:
        product_name_or_id (str): Name or ID of product.
        history_df (pd.DataFrame): Historical observations DataFrame.
        current_price (float, optional): Current price to compare against.
        
    Returns:
        dict: Complete metrics including stats, store breakdowns, and insights.
    """
    if history_df is None or history_df.empty:
        return {"found": False, "message": "Historical price data is not available yet."}
    
    # Filter by ID or Name
    p_str = str(product_name_or_id).strip().lower()
    mask = (
        history_df["product_id"].astype(str).str.lower() == p_str
    ) | (
        history_df["product_name"].astype(str).str.lower().str.contains(p_str, regex=False)
    )
    
    prod_data = history_df[mask].copy()
    if prod_data.empty:
        return {
            "found": False,
            "message": f"Historical price data is not available for '{product_name_or_id}' yet."
        }
        
    prod_name = prod_data["product_name"].iloc[0]
    prod_id = prod_data["product_id"].iloc[0]
    category = prod_data["category"].iloc[0] if "category" in prod_data.columns else "General"
    brand = prod_data["brand"].iloc[0] if "brand" in prod_data.columns else "Generic"
    
    overall_stats = calculate_price_statistics(prod_data["price"])
    
    # Amazon breakdown
    amz_data = prod_data[prod_data["store"].str.lower() == "amazon"]
    amz_stats = calculate_price_statistics(amz_data["price"])
    
    # Flipkart breakdown
    fk_data = prod_data[prod_data["store"].str.lower() == "flipkart"]
    fk_stats = calculate_price_statistics(fk_data["price"])
    
    # Purchase insight
    insight = generate_purchase_insight(
        current_price=current_price,
        min_price=overall_stats["min"],
        max_price=overall_stats["max"],
        avg_price=overall_stats["mean"],
        observation_count=overall_stats["count"]
    )
    
    return {
        "found": True,
        "product_id": prod_id,
        "product_name": prod_name,
        "category": category,
        "brand": brand,
        "overall_stats": overall_stats,
        "amazon_stats": amz_stats,
        "flipkart_stats": fk_stats,
        "records_count": len(prod_data),
        "dates_covered": sorted(prod_data["recorded_date"].dropna().unique().tolist()),
        "insight": insight,
        "raw_records": prod_data
    }


def compute_kpi_metrics(history_df, current_df=None):
    """
    Compute high-level KPI cards for the Analytics Dashboard:
    - Total products
    - Total historical observations
    - Amazon observations
    - Flipkart observations
    - Average recorded price
    - Lowest recorded price
    - Highest recorded price
    
    Parameters:
        history_df (pd.DataFrame): Cleaned historical observations.
        current_df (pd.DataFrame, optional): Cleaned current prices.
        
    Returns:
        dict: Calculated KPI values.
    """
    if history_df is None or history_df.empty:
        return {
            "total_products": 0,
            "total_observations": 0,
            "amazon_observations": 0,
            "flipkart_observations": 0,
            "avg_recorded_price": 0.0,
            "lowest_recorded_price": 0.0,
            "highest_recorded_price": 0.0
        }
        
    prices = history_df["price"].dropna()
    prices = prices[prices > 0]
    
    amz_count = int((history_df["store"].str.lower() == "amazon").sum())
    fk_count = int((history_df["store"].str.lower() == "flipkart").sum())
    
    unique_prods = int(history_df["product_id"].nunique())
    if current_df is not None and not current_df.empty and "product_id" in current_df.columns:
        unique_prods = max(unique_prods, int(current_df["product_id"].nunique()))
        
    return {
        "total_products": unique_prods,
        "total_observations": int(len(history_df)),
        "amazon_observations": amz_count,
        "flipkart_observations": fk_count,
        "avg_recorded_price": float(np.round(prices.mean(), 2)) if len(prices) > 0 else 0.0,
        "lowest_recorded_price": float(np.round(prices.min(), 2)) if len(prices) > 0 else 0.0,
        "highest_recorded_price": float(np.round(prices.max(), 2)) if len(prices) > 0 else 0.0
    }


def compute_store_wise_summary(history_df):
    """
    Calculate store-wise statistical aggregation (mean, median, min, max, std dev).
    """
    if history_df is None or history_df.empty:
        return pd.DataFrame()
        
    summary = history_df.groupby("store")["price"].agg(
        Count="count",
        Average_Price="mean",
        Median_Price="median",
        Min_Price="min",
        Max_Price="max",
        Price_Std="std"
    ).reset_index()
    
    summary["Average_Price"] = summary["Average_Price"].round(2)
    summary["Median_Price"] = summary["Median_Price"].round(2)
    summary["Min_Price"] = summary["Min_Price"].round(2)
    summary["Max_Price"] = summary["Max_Price"].round(2)
    summary["Price_Std"] = summary["Price_Std"].fillna(0.0).round(2)
    
    return summary


def compute_category_wise_summary(history_df):
    """
    Calculate category-wise aggregation (product count, observation count, avg price).
    """
    if history_df is None or history_df.empty:
        return pd.DataFrame()
        
    summary = history_df.groupby("category").agg(
        Unique_Products=("product_id", "nunique"),
        Total_Observations=("price", "count"),
        Average_Price=("price", "mean"),
        Min_Price=("price", "min"),
        Max_Price=("price", "max")
    ).reset_index()
    
    summary["Average_Price"] = summary["Average_Price"].round(2)
    summary["Min_Price"] = summary["Min_Price"].round(2)
    summary["Max_Price"] = summary["Max_Price"].round(2)
    
    return summary.sort_values(by="Total_Observations", ascending=False)


def get_top_products_by_price(df, n=10, ascending=True):
    """
    Get top N cheapest or most expensive products.
    """
    if df is None or df.empty:
        return pd.DataFrame()
        
    # If this is history_df (contains product_name, price)
    if "price" in df.columns:
        grouped = df.groupby(["product_id", "product_name"])["price"].mean().reset_index()
        grouped.rename(columns={"price": "avg_price"}, inplace=True)
        res = grouped.sort_values(by="avg_price", ascending=ascending).head(n)
        res["avg_price"] = res["avg_price"].round(2)
        return res
        
    # If this is current_df (contains lowest_price)
    if "lowest_price" in df.columns:
        res = df[["product_id", "product_name", "lowest_price"]].dropna().sort_values(
            by="lowest_price", ascending=ascending
        ).head(n)
        return res
        
    return pd.DataFrame()


if __name__ == "__main__":
    import os
    print("Testing Price Analysis Module...\n")
    hist_path = "data/price_history.csv"
    if os.path.exists(hist_path):
        h_df = pd.read_csv(hist_path)
        kpis = compute_kpi_metrics(h_df)
        print("KPIs:", kpis)
        store_stats = compute_store_wise_summary(h_df)
        print("\nStore Stats:\n", store_stats)
        p_summary = get_product_historical_summary("P001", h_df, current_price=119900.0)
        print("\nP001 Summary Stats:", p_summary["overall_stats"])
        print("P001 Insight:", p_summary["insight"])

