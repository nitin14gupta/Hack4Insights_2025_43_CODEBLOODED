from fastapi import APIRouter, HTTPException
import os
import json
from server.services.metrics import BearCartMetrics

router = APIRouter(prefix="/api", tags=["analytics"])

# Initialize metrics service (load data once)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

try:
    metrics_service = BearCartMetrics(data_dir=DATA_DIR)
except Exception as e:
    print(f"Error loading metrics: {e}")
    metrics_service = None

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
