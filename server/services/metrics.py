import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

from datetime import datetime, timedelta

class BearCartMetrics:
    """Calculate all KPIs for dashboard"""
    
    def __init__(self, data_dir=None):
        if data_dir:
            self.load_data(data_dir)
            
    def load_data(self, data_dir):
        """Load processed data into memory"""
        self.data_dir = data_dir 
        self.df_master = pd.read_csv(os.path.join(data_dir, 'master_dataset.csv'))
        # Ensure date column is datetime
        if 'session_date' in self.df_master.columns:
            self.df_master['session_date'] = pd.to_datetime(self.df_master['session_date'])

        self.df_orders = pd.read_csv(os.path.join(data_dir, 'orders_clean.csv'))
        
        # Load items
        items_path = os.path.join(data_dir, 'items_clean.csv')
        if os.path.exists(items_path):
             self.df_items = pd.read_csv(items_path)
             if 'created_at' in self.df_items.columns:
                 self.df_items['created_at'] = pd.to_datetime(self.df_items['created_at'])
        else:
             # Fallback 
             raw_items_path = os.path.join(data_dir, '../../raw/order_items.csv')
             if os.path.exists(raw_items_path):
                 self.df_items = pd.read_csv(raw_items_path)
                 if 'created_at' in self.df_items.columns:
                     self.df_items['created_at'] = pd.to_datetime(self.df_items['created_at'])
             else:
                 logger.warning("Items data not found.")
                 self.df_items = pd.DataFrame()

        # Load Refunds 
        raw_refunds_path = os.path.join(data_dir, '../../raw/order_item_refunds.csv')
        if os.path.exists(raw_refunds_path):
             self.df_refunds = pd.read_csv(raw_refunds_path)
        else:
             self.df_refunds = pd.DataFrame()

    def filter_by_date(self, df, date_col, time_range):
        """Filter dataframe by time range relative to max date in data"""
        if df.empty or date_col not in df.columns:
            return df
            
        max_date = df[date_col].max()
        if pd.isnull(max_date):
            return df
            
        start_date = None
        if time_range == 'Week':
            start_date = max_date - timedelta(days=7)
        elif time_range == 'Month':
            start_date = max_date - timedelta(days=30)
        elif time_range == 'Year':
            start_date = max_date - timedelta(days=365)
            
        if start_date:
            return df[df[date_col] >= start_date]
        return df

    def traffic_metrics(self, df=None):
        """Traffic and engagement KPIs"""
        df = df if df is not None else self.df_master
        return {
            'total_sessions': int(len(df)),
            'unique_users': int(df['user_id'].nunique()) if 'user_id' in df.columns else 0,
            'sessions_by_channel': df['traffic_channel'].value_counts().to_dict() if 'traffic_channel' in df.columns else {},
            'total_pageviews': int(df['total_pageviews'].sum()) if 'total_pageviews' in df.columns else 0,
        }
    
    def conversion_metrics(self, df=None):
        """Conversion funnel KPIs"""
        df = df if df is not None else self.df_master
        total_sessions = len(df)
        converted = df['conversion_flag'].sum() if 'conversion_flag' in df.columns else 0
        
        # Funnel Analysis
        funnel = {}
        if 'step_home' in df.columns:
            funnel = {
                'sessions': int(df['step_home'].sum()), 
                'products': int(df['step_product'].sum()),
                'cart': int(df['step_cart'].sum()),
                'shipping': int(df['step_shipping'].sum()),
                'billing': int(df['step_billing'].sum()),
                'purchase': int(df['step_thankyou'].sum()), 
            }
        
        return {
            'overall_conversion_rate': float(converted / total_sessions) if total_sessions > 0 else 0,
            'total_conversions': int(converted),
            'conversion_by_channel': df.groupby('traffic_channel')['conversion_flag'].mean().to_dict() if 'traffic_channel' in df.columns else {},
            'conversion_by_device': df.groupby('device_type')['conversion_flag'].mean().to_dict() if 'device_type' in df.columns else {},
            'funnel_steps': funnel
        }
    
    def revenue_metrics(self, df=None):
        """Revenue and AOV KPIs"""
        df = df if df is not None else self.df_master
        total_revenue = df['total_order_value'].sum() if 'total_order_value' in df.columns else 0
        
        metrics = {
            'total_revenue': float(total_revenue),
            'average_order_value': float(df[df['converted'] == 1]['total_order_value'].mean() if len(df[df['converted'] == 1]) > 0 else 0) if 'converted' in df.columns else 0,
            'revenue_per_session': float(total_revenue / len(df)) if len(df) > 0 else 0,
            'revenue_by_channel': df.groupby('traffic_channel')['total_order_value'].sum().to_dict() if 'traffic_channel' in df.columns else {},
        }
        
        return metrics

    def product_metrics(self, df_items=None):
        """Product performance KPIs from items"""
        df = df_items if df_items is not None else self.df_items
        
        if df.empty:
            return []
            
        # Enrich items with refund status (Global refund check, or should we filter refunds too? Keep global for now to see refund rate accurately)
        if not self.df_refunds.empty:
            refunded_item_ids = set(self.df_refunds['order_item_id'].unique())
            if 'is_refunded' not in df.columns:
                 df['is_refunded'] = df['order_item_id'].apply(lambda x: 1 if x in refunded_item_ids else 0)
        else:
            if 'is_refunded' not in df.columns:
                df['is_refunded'] = 0

        # Group by product
        df_prod = df.groupby('product_name').agg({
            'product_id': 'count',
            'price_usd': 'sum',
            'margin_usd': 'sum',
            'is_refunded': 'sum'
        }).reset_index()
        
        df_prod = df_prod.rename(columns={
            'product_id': 'sales_count', 
            'price_usd': 'total_revenue', 
            'margin_usd': 'total_margin',
            'is_refunded': 'refund_count'
        })
        
        # Calculate Refund Rate (Refund Count / Sales Count * 100)
        df_prod['refund_rate'] = (df_prod['refund_count'] / df_prod['sales_count'] * 100).round(2)
        
        # Sort by revenue
        df_prod = df_prod.sort_values('total_revenue', ascending=False)
        
        return df_prod.to_dict('records') 

    def quality_metrics(self, df=None):
        """Refund and customer health KPIs"""
        df = df if df is not None else self.df_master
        
        refunded_sessions = df[df['was_refunded'] == 1].shape[0] if 'was_refunded' in df.columns else 0
        converted_sessions = df[df['converted'] == 1].shape[0] if 'converted' in df.columns else 0
        total_refunds = df['was_refunded'].sum() if 'was_refunded' in df.columns else 0
        
        return {
            'overall_refund_rate': float(refunded_sessions / converted_sessions) if converted_sessions > 0 else 0,
            'total_refunds': int(total_refunds),
            'repeat_customer_rate': float((df['customer_segment'] == 'Returning').sum() / len(df)) if 'customer_segment' in df.columns else 0,
            'at_risk_segments': df[df['was_refunded'] == 1]['traffic_channel'].value_counts().head(5).to_dict() if 'was_refunded' in df.columns else {},
        }

    def get_dashboard_data(self, time_range='Month'):
        """Aggregate all metrics for frontend with optional time filtering"""
        
        # Filter Master Dataset (Sessions)
        df_master_filtered = self.filter_by_date(self.df_master, 'session_date', time_range)
        
        # Filter Items (Orders)
        df_items_filtered = self.filter_by_date(self.df_items, 'created_at', time_range)
        
        return {
            'traffic': self.traffic_metrics(df_master_filtered),
            'conversion': self.conversion_metrics(df_master_filtered),
            'revenue': self.revenue_metrics(df_master_filtered),
            'quality': self.quality_metrics(df_master_filtered),
            'products': self.product_metrics(df_items_filtered)
        }
