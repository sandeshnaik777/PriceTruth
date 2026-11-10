"""
Data Cleaning and Preprocessing Module for PriceTruth
=====================================================
This module cleans, standardizes, and validates historical and current price data.
Designed for beginner readability with simple, well-documented functions.
"""

import os
import re
import numpy as np
import pandas as pd


# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")


def clean_price_value(value):
    """
    Clean and convert a price value into a float.
    Removes currency symbols (₹, Rs.), commas, and extra spaces.
    
    Parameters:
        value: Price as string, float, or int.
        
    Returns:
        float: Numeric price, or np.nan if invalid/missing.
    """
    if pd.isna(value):
        return np.nan
    
    # If already a number
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else np.nan
    
    # If string, strip whitespace and formatting characters
    val_str = str(value).strip()
    # Remove symbols like ₹, Rs, Rs., comma, whitespace
    cleaned = re.sub(r"[^\d.]", "", val_str)
    
    try:
        num = float(cleaned)
        return num if num > 0 else np.nan
    except (ValueError, TypeError):
        return np.nan


def clean_date_string(date_val):
    """
    Standardize a date string or timestamp into YYYY-MM-DD format.
    
    Parameters:
        date_val: Date as string, Timestamp, etc.
        
    Returns:
        str: Date string in 'YYYY-MM-DD' format, or None if unparseable.
    """
    if pd.isna(date_val):
        return None
    
    try:
        dt = pd.to_datetime(str(date_val).strip())
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return str(date_val).strip()


def standardize_store_name(store_name):
    """
    Standardize store names to consistent title case ('Amazon' or 'Flipkart').
    
    Parameters:
        store_name (str): Raw store name.
        
    Returns:
        str: Standardized store name.
    """
    if not isinstance(store_name, str):
        return "Unknown"
    
    cleaned = store_name.strip().lower()
    if "amazon" in cleaned:
        return "Amazon"
    elif "flipkart" in cleaned:
        return "Flipkart"
    return store_name.strip().title()


def clean_historical_dataset(raw_df):
    """
    Clean and normalize historical price records into a canonical long format:
    [product_id, product_name, store, price, recorded_date, category, brand, source]
    
    Handles both wide format (with Amazon and Flipkart columns) and already long format.
    Preserves original dates and numeric values without fabrication.
    
    Parameters:
        raw_df (pd.DataFrame): Raw historical DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned, deduplicated, and chronologically sorted records.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(columns=[
            "product_id", "product_name", "store", "price",
            "recorded_date", "category", "brand", "source"
        ])
    
    records = []
    
    # Check if this is the wide format (contains Amazon_Price and Flipkart_Price)
    has_amz_price = "Amazon_Price" in raw_df.columns
    has_fk_price = "Flipkart_Price" in raw_df.columns
    
    if has_amz_price or has_fk_price:
        # Unpivot wide format to long format
        for _, row in raw_df.iterrows():
            prod_id = str(row.get("Product_ID", "")).strip()
            
            # 1. Process Amazon side
            if has_amz_price:
                amz_price = clean_price_value(row.get("Amazon_Price"))
                amz_status = str(row.get("Status_Amazon", "Success")).strip()
                # Only include valid successful price observations
                if pd.notnull(amz_price) and amz_status != "Failed":
                    prod_name = str(row.get("Product_Name_Amazon", row.get("Product_Name", prod_id))).strip()
                    date_val = clean_date_string(row.get("Scrape_Date_Amazon", row.get("Scrape_Date", "")))
                    category = str(row.get("Category_Amazon", row.get("Category", "General"))).strip()
                    brand = str(row.get("Brand_Amazon", row.get("Brand", "Generic"))).strip()
                    
                    records.append({
                        "product_id": prod_id,
                        "product_name": prod_name,
                        "store": "Amazon",
                        "price": amz_price,
                        "recorded_date": date_val,
                        "category": category,
                        "brand": brand,
                        "source": "historical_seed"
                    })
            
            # 2. Process Flipkart side
            if has_fk_price:
                fk_price = clean_price_value(row.get("Flipkart_Price"))
                fk_status = str(row.get("Status_Flipkart", "Success")).strip()
                if pd.notnull(fk_price) and fk_status != "Failed":
                    prod_name = str(row.get("Product_Name_Flipkart", row.get("Product_Name", prod_id))).strip()
                    date_val = clean_date_string(row.get("Scrape_Date_Flipkart", row.get("Scrape_Date", "")))
                    category = str(row.get("Category_Flipkart", row.get("Category", "General"))).strip()
                    brand = str(row.get("Brand_Flipkart", row.get("Brand", "Generic"))).strip()
                    
                    records.append({
                        "product_id": prod_id,
                        "product_name": prod_name,
                        "store": "Flipkart",
                        "price": fk_price,
                        "recorded_date": date_val,
                        "category": category,
                        "brand": brand,
                        "source": "historical_seed"
                    })
        
        cleaned_df = pd.DataFrame(records)
    else:
        # Already long format; normalize column names and datatypes
        cleaned_df = raw_df.copy()
        # Lowercase column names
        cleaned_df.columns = [c.lower().strip() for c in cleaned_df.columns]
        
        # Ensure mandatory columns exist
        if "product_id" not in cleaned_df.columns and "product_name" in cleaned_df.columns:
            cleaned_df["product_id"] = cleaned_df["product_name"]
            
        if "price" in cleaned_df.columns:
            cleaned_df["price"] = cleaned_df["price"].apply(clean_price_value)
            
        if "recorded_date" in cleaned_df.columns:
            cleaned_df["recorded_date"] = cleaned_df["recorded_date"].apply(clean_date_string)
            
        if "store" in cleaned_df.columns:
            cleaned_df["store"] = cleaned_df["store"].apply(standardize_store_name)
            
        if "source" not in cleaned_df.columns:
            cleaned_df["source"] = "user_added"
            
        # Drop rows where price is null or zero
        cleaned_df = cleaned_df.dropna(subset=["price"])
        cleaned_df = cleaned_df[cleaned_df["price"] > 0]
    
    if cleaned_df.empty:
        return cleaned_df
    
    # Remove duplicates based on product_id, store, and recorded_date
    cleaned_df = cleaned_df.drop_duplicates(
        subset=["product_id", "store", "recorded_date"],
        keep="last"
    )
    
    # Sort chronologically
    cleaned_df = cleaned_df.sort_values(
        by=["recorded_date", "product_name", "store"]
    ).reset_index(drop=True)
    
    return cleaned_df


def clean_current_prices_dataset(raw_merged_df):
    """
    Clean the current price comparison dataset and compute price metrics.
    
    Parameters:
        raw_merged_df (pd.DataFrame): Raw merged comparison DataFrame.
        
    Returns:
        pd.DataFrame: Cleaned DataFrame with standard columns and comparison metrics.
    """
    if raw_merged_df is None or raw_merged_df.empty:
        return pd.DataFrame()
    
    df = raw_merged_df.copy()
    
    # Standardize column mappings
    prod_id = df.get("Product_ID", df.index.astype(str))
    prod_name = df.get("Product_Name_Amazon", df.get("Product_Name_Flipkart", df.get("Product_Name", "Unknown")))
    category = df.get("Category_Amazon", df.get("Category_Flipkart", df.get("Category", "General")))
    brand = df.get("Brand_Amazon", df.get("Brand_Flipkart", df.get("Brand", "Generic")))
    
    # Clean prices
    amz_price = df.get("Amazon_Price", pd.Series([np.nan] * len(df))).apply(clean_price_value)
    fk_price = df.get("Flipkart_Price", pd.Series([np.nan] * len(df))).apply(clean_price_value)
    
    # URLs
    amz_url = df.get("Amazon_URL", "")
    fk_url = df.get("Flipkart_URL", "")
    
    # Date
    rec_date = df.get("Scrape_Date_Amazon", df.get("Scrape_Date_Flipkart", "2026-07-12")).apply(clean_date_string)
    
    # Build clean DataFrame
    clean_df = pd.DataFrame({
        "product_id": prod_id.astype(str).str.strip(),
        "product_name": prod_name.astype(str).str.strip(),
        "category": category.astype(str).str.strip(),
        "brand": brand.astype(str).str.strip(),
        "amazon_price": amz_price,
        "flipkart_price": fk_price,
        "amazon_url": amz_url,
        "flipkart_url": fk_url,
        "recorded_date": rec_date
    })
    
    # Calculate price difference and identify cheapest store
    def determine_cheapest(row):
        ap = row["amazon_price"]
        fp = row["flipkart_price"]
        if pd.notnull(ap) and pd.notnull(fp):
            if ap < fp:
                return "Amazon"
            elif fp < ap:
                return "Flipkart"
            else:
                return "Tie (Same Price)"
        elif pd.notnull(ap):
            return "Amazon (Only)"
        elif pd.notnull(fp):
            return "Flipkart (Only)"
        return "Unavailable"
    
    clean_df["cheapest_store"] = clean_df.apply(determine_cheapest, axis=1)
    
    # Price difference: positive means Amazon is more expensive, negative means Flipkart is more expensive
    # Absolute difference for user clarity
    def calculate_price_diff(row):
        ap = row["amazon_price"]
        fp = row["flipkart_price"]
        if pd.notnull(ap) and pd.notnull(fp):
            return abs(ap - fp)
        return np.nan
    
    clean_df["price_difference"] = clean_df.apply(calculate_price_diff, axis=1)
    
    # Lowest and highest current available price
    def get_lowest(row):
        vals = [p for p in [row["amazon_price"], row["flipkart_price"]] if pd.notnull(p)]
        return min(vals) if vals else np.nan
    
    def get_highest(row):
        vals = [p for p in [row["amazon_price"], row["flipkart_price"]] if pd.notnull(p)]
        return max(vals) if vals else np.nan
        
    clean_df["lowest_price"] = clean_df.apply(get_lowest, axis=1)
    clean_df["highest_price"] = clean_df.apply(get_highest, axis=1)
    
    return clean_df


def process_and_save_all():
    """
    Load raw files, run the full cleaning pipeline, and save clean CSV files to data/
    and data/processed/.
    """
    raw_history_path = os.path.join(RAW_DATA_DIR, "price_history.csv")
    raw_merged_path = os.path.join(RAW_DATA_DIR, "merged_prices.csv")
    
    # 1. Clean History
    if os.path.exists(raw_history_path):
        raw_hist = pd.read_csv(raw_history_path)
        clean_hist = clean_historical_dataset(raw_hist)
        
        # Save to both data/price_history.csv and data/processed/clean_price_history.csv
        clean_hist.to_csv(os.path.join(DATA_DIR, "price_history.csv"), index=False, encoding="utf-8-sig")
        clean_hist.to_csv(os.path.join(PROCESSED_DATA_DIR, "clean_price_history.csv"), index=False, encoding="utf-8-sig")
        print(f"Processed price_history.csv: {len(clean_hist)} records saved.")
    
    # 2. Clean Current Prices
    if os.path.exists(raw_merged_path):
        raw_merged = pd.read_csv(raw_merged_path)
        clean_current = clean_current_prices_dataset(raw_merged)
        
        clean_current.to_csv(os.path.join(DATA_DIR, "current_prices.csv"), index=False, encoding="utf-8-sig")
        clean_current.to_csv(os.path.join(PROCESSED_DATA_DIR, "clean_current_prices.csv"), index=False, encoding="utf-8-sig")
        print(f"Processed current_prices.csv: {len(clean_current)} records saved.")


if __name__ == "__main__":
    print("Executing Data Cleaning Pipeline...")
    process_and_save_all()
