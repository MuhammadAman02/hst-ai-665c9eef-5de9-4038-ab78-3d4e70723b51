from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time


from app.core.health import HealthCheck
from app.core.logging import app_logger

api_router = APIRouter()

health_router = APIRouter()

@health_router.get("/health", tags=["health"])
async def get_health_status():
    try:
        app_logger.info("Health check endpoint called")
        result = HealthCheck.check_all()
        app_logger.info(f"Health check completed with status: {result.get('status', 'unknown')}")
        return JSONResponse(content=result)
    except Exception as e:
        app_logger.error(f"Error in health endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Health check failed: {str(e)}", "timestamp": time.time()}
        )

api_router.include_router(health_router)