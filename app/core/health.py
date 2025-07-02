import os
import time
import platform
import psutil
from typing import Dict, Any

from app.core.logging import app_logger

class HealthCheck:
    """Health check utility for the application.
    
    This class provides methods to check the health of various components
    of the application, focusing on system resources.
    """
    
    @staticmethod
    def check_system() -> Dict[str, Any]:
        """Check system health (CPU, memory, disk, process).
        
        Returns:
            Dict with system health information
        """
        try:
            app_logger.info("Starting system health check")
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            process = psutil.Process(os.getpid())
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            
            result = {
                "status": "healthy",
                "cpu": {"percent": cpu_percent, "status": "warning" if cpu_percent > 80 else "healthy"},
                "memory": {"percent": memory.percent, "status": "warning" if memory.percent > 80 else "healthy"},
                "disk": {"percent": disk.percent, "status": "warning" if disk.percent > 80 else "healthy"},
                "process": {"memory_mb": round(process_memory_mb, 2), "status": "warning" if process_memory_mb > 500 else "healthy"},
                "platform": platform.platform(),
                "python_version": platform.python_version(),
            }
            app_logger.info("System health check completed successfully")
            return result
        except Exception as e:
            app_logger.error(f"Error checking system health: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def check_all() -> Dict[str, Any]:
        """Run all health checks.
        
        Returns:
            Dict with all health check information
        """
        try:
            app_logger.info("Starting all health checks")
            start_time = time.time()
            
            system_health = HealthCheck.check_system()
            
            overall_status = system_health.get("status", "error")
            
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            
            result = {
                "status": overall_status,
                "timestamp": time.time(),
                "response_time_ms": response_time_ms,
                "system": system_health,
            }
            app_logger.info("All health checks completed successfully")
            return result
        except Exception as e:
            app_logger.error(f"Error in check_all: {e}")
            return {"status": "error", "message": str(e), "timestamp": time.time()}

def is_healthy(component: str = "all") -> bool:
    """Check if a specific component is healthy.
    
    Args:
        component: The component to check ("system" or "all")
        
    Returns:
        True if the component is healthy, False otherwise
    """
    try:
        app_logger.info(f"Checking health for component: {component}")
        if component == "system":
            return HealthCheck.check_system().get("status") == "healthy"
        elif component == "all":
            health = HealthCheck.check_all()
            return health.get("status") == "healthy"
        else:
            app_logger.warning(f"Unknown health component requested: {component}")
            return False
    except Exception as e:
        app_logger.error(f"Error checking health for {component}: {e}")
        return False