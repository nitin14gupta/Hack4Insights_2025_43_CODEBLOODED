import os
import logging
import asyncio
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

from server.routers.api import router as api_router

from contextlib import asynccontextmanager

import requests

async def health_check_loop():
    # Wait for server startup
    await asyncio.sleep(5)
    while True:
        try:
            response = await asyncio.to_thread(requests.get, "https://bearcart.onrender.com/health")
            logger.info(f"Health check status: {response.status_code}")
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
        
        await asyncio.sleep(30)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    task = asyncio.create_task(health_check_loop())
    yield
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Health check task cancelled")

def create_app() -> FastAPI:
    app = FastAPI(title="BearCart API", version="1.0.0", lifespan=lifespan)
    
    app.include_router(api_router)
    
    # Enable CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register error handlers
    @app.exception_handler(Exception)
    async def handle_server_error(request: Request, exc: Exception):
        logger.error(f"Server error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected error occurred. Please try again."}
        )
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    # Log app startup
    logger.info("Application started successfully")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
