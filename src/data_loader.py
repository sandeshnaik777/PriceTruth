"""
Data Loader Module for PriceTruth
==================================
This module is responsible for loading raw CSV datasets and providing
exploratory inspection tools (shape, columns, null checks, duplicates, and summary stats).
Designed for beginners with clean, simple functions and explicit comments.
"""

import os
import pandas as pd


# Default data directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")


def load_raw_csv(file_path):
    """
    Safely load a CSV file into a pandas DataFrame.
    
    Parameters:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: Loaded DataFrame, or an empty DataFrame if file is missing/empty.
    """
    if not os.path.exists(file_path):
        print(f"[Warning] File not found: {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        return df
    except pd.errors.EmptyDataError:
        print(f"[Warning] CSV file is empty: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"[Error] Failed to load {file_path}: {e}")
        return pd.DataFrame()


def inspect_dataframe(df, dataset_name="Dataset"):
    """
    Perform standard Exploratory Data Analysis (EDA) on a DataFrame.
    Returns a dictionary of inspection metrics.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to inspect.
        dataset_name (str): Label for the dataset.
        
    Returns:
        dict: Summary containing row count, column count, column names,
              missing values, duplicate count, and descriptive statistics.
    """
    if df.empty:
        return {
            "name": dataset_name,
            "rows": 0,
            "columns": 0,
            "column_names": [],
            "missing_values": {},
            "duplicate_rows": 0,
            "numeric_summary": {}
        }
    
    inspection_report = {
        "name": dataset_name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_summary": df.describe().to_dict()
    }
    
    return inspection_report


def print_inspection_report(report):
    """
    Print an inspection report in a beginner-friendly formatted style.
    """
    print("=" * 60)
    print(f"INSPECTION REPORT: {report['name']}")
    print("=" * 60)
    print(f"Total Rows:    {report['rows']}")
    print(f"Total Columns: {report['columns']}")
    print(f"Columns:       {report['column_names']}")
    print(f"Duplicates:    {report['duplicate_rows']}")
    print("\nMissing Values per Column:")
    for col, count in report["missing_values"].items():
        if count > 0:
            print(f"  - {col}: {count} missing")
        else:
            print(f"  - {col}: 0 missing (complete)")
    print("=" * 60)


def load_raw_amazon_prices():
    """Load the raw Amazon prices CSV."""
    path = os.path.join(RAW_DATA_DIR, "amazon_prices.csv")
    return load_raw_csv(path)


def load_raw_flipkart_prices():
    """Load the raw Flipkart prices CSV."""
    path = os.path.join(RAW_DATA_DIR, "flipkart_prices.csv")
    return load_raw_csv(path)


def load_raw_merged_prices():
    """Load the raw merged comparison CSV."""
    path = os.path.join(RAW_DATA_DIR, "merged_prices.csv")
    return load_raw_csv(path)


def load_raw_price_history():
    """Load the raw price history CSV."""
    path = os.path.join(RAW_DATA_DIR, "price_history.csv")
    return load_raw_csv(path)


if __name__ == "__main__":
    print("Running Data Loader & Dataset Inspection...\n")
    
    # Inspect raw Amazon prices
    df_amz = load_raw_amazon_prices()
    report_amz = inspect_dataframe(df_amz, "Raw Amazon Prices")
    print_inspection_report(report_amz)
    
    # Inspect raw Flipkart prices
    df_fk = load_raw_flipkart_prices()
    report_fk = inspect_dataframe(df_fk, "Raw Flipkart Prices")
    print_inspection_report(report_fk)
    
    # Inspect raw Merged prices
    df_merged = load_raw_merged_prices()
    report_merged = inspect_dataframe(df_merged, "Raw Merged Prices")
    print_inspection_report(report_merged)
    
    # Inspect raw Price History
    df_hist = load_raw_price_history()
    report_hist = inspect_dataframe(df_hist, "Raw Price History")
    print_inspection_report(report_hist)
