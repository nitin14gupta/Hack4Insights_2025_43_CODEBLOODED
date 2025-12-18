from fastapi import APIRouter, HTTPException
import os
import json
from server.services.metrics import BearCartMetrics
from server.services.chat_agent import BearCartChatAgent
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["analytics"])

# Initialize metrics service (load data once)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

try:
    metrics_service = BearCartMetrics(data_dir=DATA_DIR)
except Exception as e:
    print(f"Error loading metrics: {e}")
    metrics_service = None

# Initialize Chat Agent
chat_agent = BearCartChatAgent()

class ChatRequest(BaseModel):
    question: str

@router.get("/dashboard")
async def get_dashboard_data(range: str = "Month"):
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized. Run pipeline first.")
    
    try:
        data = metrics_service.get_dashboard_data(time_range=range)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality")
async def get_quality_report():
    """Get data quality metrics"""
    try:
        report_path = os.path.join(metrics_service.data_dir, 'quality_report.json')
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                return json.load(f)
        return {"error": "Report not found"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/chat")
async def chat_with_data(request: ChatRequest):
    """Chat with BearCart AI using dashboard context"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
        
    try:
        # Get current dashboard data context
        # We use a default 'Month' range for context, or could make it dynamic
        context_data = metrics_service.get_dashboard_data(time_range='Month')
        
        # Get answer from agent
        response = chat_agent.ask(request.question, context_data)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
from server.services.pdf_service import BearCartReport

@router.get("/export/pdf")
async def export_pdf(range: str = "Month"):
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        # Get data for the requested range
        data = metrics_service.get_dashboard_data(time_range=range)
        
        # Generate PDF
        report = BearCartReport()
        pdf_buffer = report.generate(data, time_range=range)
        
        headers = {
            'Content-Disposition': f'attachment; filename="BearCart_Report_{range}.pdf"'
        }
        
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights")
async def get_insights(range: str = "Month"):
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        # Get context data
        context_data = metrics_service.get_dashboard_data(time_range=range)
        
        # Generate insights
        insights = chat_agent.generate_strategic_insights(context_data)
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from server.utils.forecast_utils import calculate_linear_forecast
from collections import defaultdict
from datetime import datetime

@router.get("/forecast")
async def get_forecast(periods: int = 3):
    """Generate X-month revenue forecast based on yearly history"""
    if not metrics_service:
        raise HTTPException(status_code=500, detail="Metrics service not initialized")
    
    try:
        # Get 1 year of data for good trend analysis
        data = metrics_service.get_dashboard_data(time_range='Year')
        daily_revenue = data['revenue']['revenue_over_time']
        
        if not daily_revenue:
            return {"error": "No data available for forecasting"}

        # Aggregate to Monthly
        monthly_rev = defaultdict(float)
        for entry in daily_revenue:
            # entry is {'session_date': 'YYYY-MM-DD', 'total_order_value': X}
            date_str = str(entry['session_date'])[:7] # YYYY-MM
            monthly_rev[date_str] += float(entry['total_order_value'])
            
        # Sort keys
        sorted_months = sorted(monthly_rev.keys())
        historical_values = [monthly_rev[m] for m in sorted_months]
        
        # Calculate Forecast
        forecast_result = calculate_linear_forecast(historical_values, periods_to_forecast=periods)
        
        # Generate Future Labels
        last_month = datetime.strptime(sorted_months[-1], "%Y-%m")
        future_labels = []
        for i in range(1, periods + 1):
            # Add Month (rough)
            next_m = (last_month.month + i - 1) % 12 + 1
            next_y = last_month.year + ((last_month.month + i + last_month.month - 1) // 12 if (last_month.month + i -1) >= 12 else 0) # Fix logic below
            # simpler logic:
            total_months = last_month.month + i
            year_add = (total_months - 1) // 12
            month_rem = (total_months - 1) % 12 + 1
            next_y = last_month.year + year_add
            future_labels.append(f"{next_y}-{month_rem:02d}")
            
        return {
            "labels": sorted_months + future_labels,
            "historical": forecast_result["historical_trend"], # The trend line for history
            "actual": historical_values, # The actual bars
            "forecast": forecast_result["forecast"],
            "growth_rate_pct": round(forecast_result["growth_rate"] * 100, 2),
            "trend_direction": "Up" if forecast_result["slope"] > 0 else "Down"
        }
        
    except Exception as e:
        print(f"Forecast Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
