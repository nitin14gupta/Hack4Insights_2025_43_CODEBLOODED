import os
import json
import pandas as pd
from server.services.data_cleaner import BearCartDataCleaner
from server.services.feature_engineer import BearCartFeatureEngineer

def run():
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, 'raw')
    PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    cleaner = BearCartDataCleaner()
    fe = BearCartFeatureEngineer()
    
    # 1. Load Data
    print("--- Loading Data ---")
    df_sessions, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'website_sessions.csv'))
    df_orders, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'orders.csv'))
    df_refunds, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'order_item_refunds.csv'))
    df_items, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'order_items.csv'))
    df_products, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'products.csv'))
    df_pageviews, _ = cleaner.load_and_profile(os.path.join(RAW_DIR, 'website_pageviews.csv'))
    
    if any(df is None for df in [df_sessions, df_orders, df_items, df_products, df_pageviews]):
        print("CRITICAL: Missing essential data files. Exiting.")
        return

    # 2. Clean Data
    print("\n--- Cleaning Data ---")
    df_sessions_clean = cleaner.clean_sessions(df_sessions)
    df_orders_clean = cleaner.clean_orders(df_orders, df_sessions_clean)
    df_refunds_clean = cleaner.clean_refunds(df_refunds, df_orders_clean)
    
    df_products_clean = cleaner.clean_products(df_products)
    df_items_clean = cleaner.clean_order_items(df_items, df_orders_clean, df_products_clean)
    df_funnel_agg = cleaner.clean_pageviews(df_pageviews)
    
    # 3. Create Master Dataset (Sessions Level)
    print("\n--- Creating Master Dataset ---")
    df_master = cleaner.create_master_dataset(df_sessions_clean, df_orders_clean, df_refunds_clean, df_funnel_agg)
    
    # 4. Feature Engineering
    print("\n--- Engineering Features ---")
    # Note: FE might need updates if it used old df_items, but we pass raw items there usually. 
    # Let's pass cleaned items if possible or just proceed. 
    # Current signature: fe.engineer_features(df_master, df_sessions, df_orders, df_items)
    df_master_features = fe.engineer_features(df_master, df_sessions_clean, df_orders_clean, df_items_clean)
    
    # 5. Save Outputs
    print("\n--- Saving Outputs ---")
    
    # Cleaned Data (Submission Requirement 1)
    CLEANED_DIR = os.path.join(BASE_DIR, 'data', 'cleaned')
    os.makedirs(CLEANED_DIR, exist_ok=True)
    
    df_sessions_clean.to_csv(os.path.join(CLEANED_DIR, 'website_sessions_clean.csv'), index=False)
    df_orders_clean.to_csv(os.path.join(CLEANED_DIR, 'orders_clean.csv'), index=False)
    df_items_clean.to_csv(os.path.join(CLEANED_DIR, 'order_items_clean.csv'), index=False)
    df_products_clean.to_csv(os.path.join(CLEANED_DIR, 'products_clean.csv'), index=False)
    df_refunds_clean.to_csv(os.path.join(CLEANED_DIR, 'order_item_refunds_clean.csv'), index=False)
    
    # Processed Data (for Dashboard App)
    df_sessions_clean.to_csv(os.path.join(PROCESSED_DIR, 'sessions_clean.csv'), index=False)
    df_orders_clean.to_csv(os.path.join(PROCESSED_DIR, 'orders_clean.csv'), index=False)
    df_items_clean.to_csv(os.path.join(PROCESSED_DIR, 'items_clean.csv'), index=False)
    df_master_features.to_csv(os.path.join(PROCESSED_DIR, 'master_dataset.csv'), index=False)
    # Add missing ones for app completeness
    df_products_clean.to_csv(os.path.join(PROCESSED_DIR, 'products_clean.csv'), index=False)
    df_refunds_clean.to_csv(os.path.join(PROCESSED_DIR, 'refunds_clean.csv'), index=False)
    
    # Save reports
    with open(os.path.join(PROCESSED_DIR, 'quality_report.json'), 'w') as f:
        json.dump(cleaner.cleaning_report, f, indent=4)
    
    with open(os.path.join(PROCESSED_DIR, 'feature_report.json'), 'w') as f:
        json.dump(fe.feature_report, f, indent=4)
        
    print(f"\nSUCCESS! Data saved to {PROCESSED_DIR}")
    print("Cleaning Report:", json.dumps(cleaner.cleaning_report, indent=2))
    print("Feature Report:", json.dumps(fe.feature_report, indent=2))

if __name__ == "__main__":
    run()
