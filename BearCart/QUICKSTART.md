# BearCart Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Place Your Data Files
Place your CSV files in `data/raw/`:
- `sessions.csv`
- `orders.csv`
- `products.csv`
- `refunds.csv`

**Note:** If you don't have data files yet, you can generate sample data with:
```bash
python generate_sample_data.py
```

See `README.html` for detailed data schema requirements.

### Step 3: Clean Data
```bash
python -m backend.data_cleaning
```

This will process your raw data files and create cleaned versions in `data/cleaned/`.

### Step 4: Launch Dashboard
```bash
streamlit run frontend/app.py
```

Or use the convenience script (automatically runs data cleaning if needed):
```bash
./run_dashboard.sh
```

## 🎯 Dashboard Pages

1. **Executive Overview** - Key KPIs and business insights
2. **Traffic & Marketing** - Channel and device analysis
3. **Conversion Funnel** - Session-to-order conversion analysis
4. **Revenue & AOV** - Revenue trends and average order value
5. **Refund Analysis** - Refund patterns and business impact

## 💡 Tips

- Always run data cleaning before using the dashboard
- Use date filters to analyze specific time periods
- Filter by channel/device to drill down into performance
- Check business insights for automated recommendations

## 🐛 Troubleshooting

**Error: "Data file not found"**
- Ensure data files are in `data/raw/` or `data/cleaned/`
- Run `python -m backend.data_cleaning` to generate cleaned data

**Error: "Module not found"**
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the BearCart directory

**Dashboard shows no data**
- Check that cleaned data files exist in `data/cleaned/`
- Verify CSV files have correct column names (see README.html)

