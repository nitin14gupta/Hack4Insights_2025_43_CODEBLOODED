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
