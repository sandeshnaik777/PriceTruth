"""
Scraper Interface & Current Price Comparison Module for PriceTruth
==================================================================
Provides a clean interface for importing and querying current product listings
across Amazon India and Flipkart.
Designed without fake scraper endpoints or simulated APIs; imports current data
through structured CSV files and provides the required `get_current_prices(product_name)`.
"""

import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pandas as pd
import numpy as np

from src.data_cleaning import clean_price_value, clean_current_prices_dataset

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CURRENT_PRICES_FILE = os.path.join(DATA_DIR, "current_prices.csv")


def load_current_prices_catalog():
    """
    Load the active current prices comparison catalog from CSV.
    
    Returns:
        pd.DataFrame: Clean DataFrame containing current product listings.
    """
    if not os.path.exists(CURRENT_PRICES_FILE):
        return pd.DataFrame()
        
    try:
        df = pd.read_csv(CURRENT_PRICES_FILE)
        return df
    except Exception as e:
        print(f"[Error] Failed to load {CURRENT_PRICES_FILE}: {e}")
        return pd.DataFrame()


def import_current_prices_from_csv(file_path_or_buffer):
    """
    Import and validate an external CSV file containing current comparison results.
    Can be used by external scrapers or user uploads.
    
    Parameters:
        file_path_or_buffer: Path to CSV or file-like buffer (e.g. from st.file_uploader).
        
    Returns:
        tuple: (bool, pd.DataFrame, str) -> (success, imported_dataframe, status_message)
    """
    try:
        raw_df = pd.read_csv(file_path_or_buffer)
        if raw_df.empty:
            return False, pd.DataFrame(), "The uploaded CSV file is empty."
            
        clean_df = clean_current_prices_dataset(raw_df)
        if clean_df.empty:
            return False, pd.DataFrame(), "Could not extract valid comparison columns from the CSV."
            
        # Save to data/current_prices.csv
        clean_df.to_csv(CURRENT_PRICES_FILE, index=False, encoding="utf-8-sig")
        return True, clean_df, f"Successfully imported {len(clean_df)} product listings."
    except Exception as e:
        return False, pd.DataFrame(), f"Failed to import CSV: {e}"


def get_all_available_products():
    """
    Retrieve a list of all products currently available in the comparison catalog.
    
    Returns:
        list of dict: List containing product_id, product_name, category, brand.
    """
    df = load_current_prices_catalog()
    if df.empty:
        return []
    
    products = []
    for _, row in df.iterrows():
        products.append({
            "product_id": str(row.get("product_id", "")),
            "product_name": str(row.get("product_name", "")),
            "category": str(row.get("category", "General")),
            "brand": str(row.get("brand", "Generic")),
            "amazon_price": row.get("amazon_price"),
            "flipkart_price": row.get("flipkart_price"),
            "cheapest_store": row.get("cheapest_store", "Unknown"),
            "lowest_price": row.get("lowest_price")
        })
    return products


def get_current_prices(product_name):
    """
    Retrieve current Amazon India and Flipkart price listings for a product.
    
    Handles cases:
    - No products found.
    - Store is unavailable.
    - Price cannot be extracted.
    - Multiple similar products found.
    - Product match is uncertain.
    
    Parameters:
        product_name (str): Product name or query string.
        
    Returns:
        dict: Structured comparison result including listings, differences,
              status flags, and candidates.
    """
    if not product_name or not str(product_name).strip():
        return {
            "status": "error",
            "message": "Please enter a product name to search.",
            "product": None,
            "listings": []
        }
        
    df = load_current_prices_catalog()
    if df.empty:
        return {
            "status": "no_data",
            "message": "No current comparison data is loaded. Please import current comparison results.",
            "product": None,
            "listings": []
        }
        
    query = str(product_name).strip().lower()
    query_tokens = set(query.split())
    
    # 1. Exact Match check
    exact_match = df[
        (df["product_name"].astype(str).str.lower() == query) |
        (df["product_id"].astype(str).str.lower() == query)
    ]
    
    candidates = []
    matched_row = None
    match_type = "none"
    
    if len(exact_match) == 1:
        matched_row = exact_match.iloc[0]
        match_type = "exact"
    elif len(exact_match) > 1:
        matched_row = exact_match.iloc[0]
        match_type = "multiple_exact"
        candidates = exact_match["product_name"].tolist()
    else:
        # 2. Substring matching
        substring_match = df[
            df["product_name"].astype(str).str.lower().str.contains(query, regex=False)
        ]
        
        if len(substring_match) == 1:
            matched_row = substring_match.iloc[0]
            match_type = "substring"
        elif len(substring_match) > 1:
            # Multiple candidates found - do not arbitrarily pick one
            candidates = substring_match["product_name"].tolist()
            match_type = "multiple_candidates"
        else:
            # 3. Token overlap check
            def token_score(name):
                name_tokens = set(str(name).lower().split())
                if not name_tokens:
                    return 0
                return len(query_tokens.intersection(name_tokens)) / len(query_tokens)
                
            scores = df["product_name"].apply(token_score)
            best_score = scores.max()
            
            if best_score >= 0.6:
                top_matches = df[scores == best_score]
                if len(top_matches) == 1:
                    matched_row = top_matches.iloc[0]
                    match_type = "partial"
                else:
                    candidates = top_matches["product_name"].tolist()
                    match_type = "multiple_candidates"
            else:
                match_type = "not_found"

    # Case: Multiple similar products found
    if match_type == "multiple_candidates":
        return {
            "status": "multiple_matches",
            "message": f"Multiple similar products were found matching '{product_name}'. Please select the exact product.",
            "candidates": candidates,
            "product": None,
            "listings": []
        }
        
    # Case: Not found
    if match_type == "not_found" or matched_row is None:
        return {
            "status": "not_found",
            "message": f"No product matching '{product_name}' was found in the current comparison dataset.",
            "candidates": df["product_name"].head(5).tolist(),
            "product": None,
            "listings": []
        }
        
    # Build listing details for exact or resolved match
    p_id = str(matched_row.get("product_id", "")).strip()
    p_name = str(matched_row.get("product_name", "")).strip()
    category = str(matched_row.get("category", "General")).strip()
    brand = str(matched_row.get("brand", "Generic")).strip()
    rec_date = str(matched_row.get("recorded_date", datetime.now().strftime("%Y-%m-%d"))).strip()
    
    amz_p = matched_row.get("amazon_price")
    fk_p = matched_row.get("flipkart_price")
    amz_url = str(matched_row.get("amazon_url", "")).strip()
    fk_url = str(matched_row.get("flipkart_url", "")).strip()
    
    # Check Amazon availability
    amz_available = pd.notnull(amz_p) and float(amz_p) > 0
    amazon_listing = {
        "store": "Amazon India",
        "price": float(amz_p) if amz_available else None,
        "available": amz_available,
        "status": "Available" if amz_available else "Listing Unavailable / Extraction Failed",
        "url": amz_url if amz_url else None,
        "retrieval_timestamp": rec_date
    }
    
    # Check Flipkart availability
    fk_available = pd.notnull(fk_p) and float(fk_p) > 0
    flipkart_listing = {
        "store": "Flipkart",
        "price": float(fk_p) if fk_available else None,
        "available": fk_available,
        "status": "Available" if fk_available else "Listing Unavailable / Extraction Failed",
        "url": fk_url if fk_url else None,
        "retrieval_timestamp": rec_date
    }
    
    # Store comparison calculations
    if amz_available and fk_available:
        diff = abs(amz_p - fk_p)
        highest = max(amz_p, fk_p)
        lowest = min(amz_p, fk_p)
        if amz_p < fk_p:
            cheapest = "Amazon India"
        elif fk_p < amz_p:
            cheapest = "Flipkart"
        else:
            cheapest = "Tie (Same Price)"
    elif amz_available:
        diff = None
        highest = amz_p
        lowest = amz_p
        cheapest = "Amazon India (Only Available Store)"
    elif fk_available:
        diff = None
        highest = fk_p
        lowest = fk_p
        cheapest = "Flipkart (Only Available Store)"
    else:
        diff = None
        highest = None
        lowest = None
        cheapest = "Both Stores Unavailable"
        
    return {
        "status": "success",
        "match_type": match_type,
        "product_id": p_id,
        "product_name": p_name,
        "category": category,
        "brand": brand,
        "cheapest_store": cheapest,
        "price_difference": diff,
        "lowest_price": lowest,
        "highest_price": highest,
        "retrieval_timestamp": rec_date,
        "listings": {
            "Amazon": amazon_listing,
            "Flipkart": flipkart_listing
        }
    }


if __name__ == "__main__":
    print("Testing Scraper Interface...\n")
    # Test with known product
    res = get_current_prices("Samsung Galaxy S25")
    print(f"Product: {res.get('product_name')}")
    print(f"Status: {res.get('status')}")
    print(f"Cheapest: {res.get('cheapest_store')}")
    print(f"Price Diff: {res.get('price_difference')}")
    print(f"Listings: {res.get('listings')}")
    
    # Test missing store
    res_partial = get_current_prices("Sony WH-CH520")
    print("\nPartial store test (Sony WH-CH520):")
    print("Amazon status:", res_partial["listings"]["Amazon"]["status"])
    print("Flipkart status:", res_partial["listings"]["Flipkart"]["status"])
    print("Cheapest:", res_partial["cheapest_store"])
    
    # Test not found
    res_nf = get_current_prices("NonExistentProduct12345")
    print("\nNot found test status:", res_nf["status"], "|", res_nf["message"])
