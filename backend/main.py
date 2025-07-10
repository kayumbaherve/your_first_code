"""
AI Interior Design Assistant - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

# Import API routers
from api.scanning import router as scanning_router
from api.recommendations import router as recommendations_router
from api.visualization import router as visualization_router
from api.staging import router as staging_router
from api.auth import router as auth_router
from api.projects import router as projects_router

# Import database
from database.connection import engine, get_db
from database.models import Base

# Import configuration
from core.config import settings
from core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Interior Design Assistant API")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Interior Design Assistant API")


# Create FastAPI application
app = FastAPI(
    title="AI Interior Design Assistant API",
    description="Sophisticated AI-powered interior design assistant with room scanning, AI recommendations, 3D visualization, and virtual staging",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(scanning_router, prefix="/api/scan", tags=["Room Scanning"])
app.include_router(recommendations_router, prefix="/api/recommend", tags=["AI Recommendations"])
app.include_router(visualization_router, prefix="/api/3d", tags=["3D Visualization"])
app.include_router(staging_router, prefix="/api/stage", tags=["Virtual Staging"])
app.include_router(projects_router, prefix="/api/projects", tags=["Project Management"])


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Interior Design Assistant API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Room Scanning & Analysis",
            "AI-Powered Recommendations",
            "3D Visualization",
            "Virtual Staging",
            "Project Management"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
        
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

