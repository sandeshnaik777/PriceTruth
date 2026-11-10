"""
Comprehensive Integration Test Suite for PriceTruth
====================================================
Tests:
1. Data loading and inspection
2. Cleaning and normalization pipeline
3. Price analysis metrics and statistics
4. Scraper interface and search handling
5. Price observation saving and duplicate protection
6. Plotly chart generation
"""

import os
import sys
import unittest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import (
    load_raw_csv,
    inspect_dataframe,
    load_raw_amazon_prices,
    load_raw_flipkart_prices,
    load_raw_merged_prices,
    load_raw_price_history
)
from src.data_cleaning import (
    clean_price_value,
    clean_date_string,
    standardize_store_name,
    clean_historical_dataset,
    clean_current_prices_dataset
)
from src.price_analysis import (
    calculate_price_statistics,
    calculate_percentage_difference,
    calculate_store_difference,
    generate_purchase_insight,
    get_product_historical_summary,
    compute_kpi_metrics,
    compute_store_wise_summary,
    compute_category_wise_summary,
    get_top_products_by_price
)
from src.price_history import (
    load_price_history,
    save_price_observation,
    filter_history,
    create_price_history_chart,
    create_store_avg_price_chart,
    create_category_distribution_chart
)
from src.scraper_interface import (
    load_current_prices_catalog,
    get_all_available_products,
    get_current_prices
)


class TestPriceTruth(unittest.TestCase):
    
    def test_01_data_loader(self):
        df_amz = load_raw_amazon_prices()
        self.assertFalse(df_amz.empty)
        self.assertIn("Amazon_Price", df_amz.columns)
        
        df_fk = load_raw_flipkart_prices()
        self.assertFalse(df_fk.empty)
        self.assertIn("Flipkart_Price", df_fk.columns)
        
        report = inspect_dataframe(df_amz, "Amazon Test")
        self.assertEqual(report["rows"], 10)
        self.assertIn("Amazon_Price", report["column_names"])

    def test_02_data_cleaning_primitives(self):
        # Price cleaning
        self.assertEqual(clean_price_value("₹ 1,19,900.00"), 119900.0)
        self.assertEqual(clean_price_value("Rs. 1,499"), 1499.0)
        self.assertTrue(np.isnan(clean_price_value(None)))
        self.assertTrue(np.isnan(clean_price_value(-50)))
        
        # Date cleaning
        self.assertEqual(clean_date_string("2026-07-12 12:11:59"), "2026-07-12")
        self.assertEqual(clean_date_string("2026/07/02"), "2026-07-02")
        
        # Store standardization
        self.assertEqual(standardize_store_name("amazon.in"), "Amazon")
        self.assertEqual(standardize_store_name("FLIPKART"), "Flipkart")
        self.assertEqual(standardize_store_name("unknown_store"), "Unknown_Store")

    def test_03_price_analysis(self):
        prices = [100.0, 200.0, 300.0]
        stats = calculate_price_statistics(prices)
        self.assertEqual(stats["min"], 100.0)
        self.assertEqual(stats["max"], 300.0)
        self.assertEqual(stats["mean"], 200.0)
        self.assertEqual(stats["median"], 200.0)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["std"], 100.0)
        
        # Percentage difference
        pct = calculate_percentage_difference(150.0, 100.0)
        self.assertEqual(pct, 50.0)
        
        # Store difference
        diff_res = calculate_store_difference(120.0, 100.0)
        self.assertEqual(diff_res["difference"], 20.0)
        self.assertEqual(diff_res["cheaper_store"], "Flipkart")

    def test_04_purchase_insights(self):
        # All-time low
        insight1 = generate_purchase_insight(100.0, 100.0, 200.0, 150.0, 5)
        self.assertEqual(insight1["badge"], "All-Time Low")
        self.assertEqual(insight1["color"], "green")
        
        # Peak
        insight2 = generate_purchase_insight(200.0, 100.0, 200.0, 150.0, 5)
        self.assertEqual(insight2["badge"], "Historical Peak")
        self.assertEqual(insight2["color"], "red")
        
        # Insufficient data
        insight3 = generate_purchase_insight(100.0, 100.0, 200.0, 150.0, 1)
        self.assertEqual(insight3["badge"], "Insufficient Data")

    def test_05_scraper_interface(self):
        # Existing product
        res = get_current_prices("iPhone 17 Pro Max 1 TB")
        self.assertEqual(res["status"], "success")
        self.assertIn("Amazon", res["listings"])
        self.assertIn("Flipkart", res["listings"])
        self.assertTrue(res["listings"]["Amazon"]["available"])
        self.assertTrue(res["listings"]["Flipkart"]["available"])
        
        # Non-existent product
        res_none = get_current_prices("A completely nonexistent gadget 99999")
        self.assertEqual(res_none["status"], "not_found")
        
        # Product with partial store coverage
        res_partial = get_current_prices("Sony WH-CH520")
        self.assertEqual(res_partial["status"], "success")
        self.assertFalse(res_partial["listings"]["Amazon"]["available"])
        self.assertTrue(res_partial["listings"]["Flipkart"]["available"])

    def test_06_price_history_and_storage(self):
        df_hist = load_price_history()
        self.assertFalse(df_hist.empty)
        
        # Duplicate prevention check
        # Existing record in historical data: P001 on 2026-07-02 at Amazon
        dup_success, dup_msg = save_price_observation("P001", "iPhone 17 Pro Max 1 TB", "Amazon", 189900.0, "2026-07-02")
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)
        
        # Filter check
        filtered = filter_history(df_hist, "P001")
        self.assertGreaterEqual(len(filtered), 2)
        
        # Chart generation check
        fig = create_price_history_chart(filtered, "iPhone 17 Pro Max 1 TB")
        self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()
