"""
Create raw data files without external dependencies.
Simple CSV generation for testing.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
random.seed(42)

# Get project root directory
script_dir = Path(__file__).parent
raw_data_dir = script_dir / 'data' / 'raw'
raw_data_dir.mkdir(parents=True, exist_ok=True)

# Generate date range (last 90 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

# Channels and devices
channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct', 'Referral']
devices = ['Desktop', 'Mobile', 'Tablet']

# Generate sessions.csv
n_sessions = 5000
print(f"Generating {n_sessions} sessions...")

with open(raw_data_dir / 'sessions.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['session_id', 'user_id', 'timestamp', 'channel', 'device', 'session_duration', 'page_views'])
    
    for i in range(1, n_sessions + 1):
        session_date = start_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        channel = random.choice(channels) if random.random() > 0.01 else None
        device = random.choice(devices) if random.random() > 0.006 else None
        duration = max(0, int(random.expovariate(1/180)))
        page_views = max(1, random.randint(1, 20))
        
        writer.writerow([
            f'SES_{i:06d}',
            f'USER_{random.randint(1, 2000):06d}',
            session_date.strftime('%Y-%m-%d %H:%M:%S'),
            channel if channel else '',
            device if device else '',
            duration,
            page_views
        ])

# Add some duplicates
with open(raw_data_dir / 'sessions.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    # Add 100 duplicate rows
    for i in range(100):
        session_date = start_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        writer.writerow([
            f'SES_{random.randint(1, n_sessions):06d}',
            f'USER_{random.randint(1, 2000):06d}',
            session_date.strftime('%Y-%m-%d %H:%M:%S'),
            random.choice(channels),
            random.choice(devices),
            random.randint(10, 600),
            random.randint(1, 15)
        ])

# Generate orders.csv (subset of sessions convert)
n_orders = int(n_sessions * 0.15)  # ~15% conversion rate
print(f"Generating {n_orders} orders...")

order_sessions = random.sample(range(1, n_sessions + 1), n_orders)

with open(raw_data_dir / 'orders.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'session_id', 'user_id', 'order_date', 'total_amount', 'items_count'])
    
    for i, session_idx in enumerate(order_sessions, 1):
        order_date = start_date + timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Log-normal distribution for order amounts
        total_amount = round(random.lognormvariate(4, 0.8), 2)
        items_count = random.randint(1, 10) if random.random() > 0.04 else None
        
        writer.writerow([
            f'ORD_{i:06d}',
            f'SES_{session_idx:06d}',
            f'USER_{random.randint(1, 2000):06d}',
            order_date.strftime('%Y-%m-%d %H:%M:%S'),
            total_amount,
            items_count if items_count else ''
        ])

# Generate products.csv
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Toys']
n_products = 200
print(f"Generating {n_products} products...")

with open(raw_data_dir / 'products.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['product_id', 'product_name', 'category', 'price', 'stock_quantity'])
    
    for i in range(1, n_products + 1):
        category = random.choice(categories) if random.random() > 0.075 else None
        price = round(random.uniform(10, 500), 2)
        stock = random.randint(0, 1000)
        
        writer.writerow([
            f'PROD_{i:04d}',
            f'Product {i}',
            category if category else '',
            price,
            stock
        ])

# Generate refunds.csv (subset of orders)
n_refunds = int(n_orders * 0.08)  # ~8% refund rate
print(f"Generating {n_refunds} refunds...")

refund_orders = random.sample(range(1, n_orders + 1), n_refunds)
reasons = ['Defective', 'Wrong Item', 'Not as Described', 'Customer Request', 'Late Delivery']

# Read order amounts for validation
order_amounts = {}
with open(raw_data_dir / 'orders.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        order_amounts[row['order_id']] = float(row['total_amount'])

with open(raw_data_dir / 'refunds.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['refund_id', 'order_id', 'refund_date', 'refund_amount', 'reason'])
    
    for i, order_idx in enumerate(refund_orders, 1):
        order_id = f'ORD_{order_idx:06d}'
        order_amount = order_amounts.get(order_id, 100)
        
        refund_date = start_date + timedelta(
            days=random.randint(0, 90) + random.randint(1, 14),  # After order
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Most refunds are valid, but add some invalid ones for data cleaning to catch
        if random.random() > 0.05:
            refund_amount = round(min(order_amount, random.uniform(5, order_amount)), 2)
        else:
            refund_amount = round(order_amount * 1.5, 2)  # Invalid: refund > order
        
        writer.writerow([
            f'REF_{i:05d}',
            order_id,
            refund_date.strftime('%Y-%m-%d %H:%M:%S'),
            refund_amount,
            random.choice(reasons)
        ])

print("\n✅ Raw data files generated successfully!")
print(f"- Sessions: {n_sessions} records (+ 100 duplicates)")
print(f"- Orders: {n_orders} records")
print(f"- Products: {n_products} records")
print(f"- Refunds: {n_refunds} records")
print(f"\nFiles saved to: {raw_data_dir}")

