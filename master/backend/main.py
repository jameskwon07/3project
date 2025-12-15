"""
Master Backend - Agent Management Web Server
FastAPI-based RESTful API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pathlib import Path
import time

from database import init_db
from logging_config import request_logger, app_logger
from metrics_collector import MetricsCollectorMiddleware
from config import (
    APP_TITLE, APP_VERSION,
    CORS_ORIGINS, CORS_ALLOW_CREDENTIALS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS,
    FRONTEND_DIST_PATHS
)

# Import routers
from routers import agents, releases, deployments, settings, health

app = FastAPI(title=APP_TITLE, version=APP_VERSION)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    app_logger.info("Starting Master Agent Manager backend")
    await init_db()
    app_logger.info("Database initialized successfully")
    app_logger.info("Monitoring system enabled - logs in ./logs/ directory")


# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        # Log request
        request_logger.info(f"{method} {path} - Client: {request.client.host if request.client else 'unknown'}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            request_logger.info(
                f"{method} {path} - Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            request_logger.error(
                f"{method} {path} - Error: {str(e)} - Time: {process_time:.3f}s",
                exc_info=True
            )
            raise


# CORS configuration (for frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
)

# Metrics collection middleware (must be before request logging to capture all requests)
app.add_middleware(MetricsCollectorMiddleware)

# Request logging middleware (must be after CORS and metrics)
app.add_middleware(RequestLoggingMiddleware)

# Serve static files (frontend build)
frontend_dist = None
for path in FRONTEND_DIST_PATHS:
    if path.exists():
        frontend_dist = path
        break

if frontend_dist:
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Master Agent Manager API", "version": APP_VERSION}


# Include routers
app.include_router(agents.router)
app.include_router(releases.router)
app.include_router(deployments.router)
app.include_router(settings.router)
app.include_router(health.router)


if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT, RELOAD
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD
    )
