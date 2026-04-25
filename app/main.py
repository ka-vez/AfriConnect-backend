"""
Main FastAPI application entry point for AfriConnect backend.
Initializes the API, registers routers, and sets up middleware.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import create_db_and_tables
from app.middleware.auth_middleware import AuthMiddleware
from app.api.v1 import auth, founder, investor, partnership, landing

# Get settings
settings = get_settings()

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Startup code runs before yield, shutdown code after yield.
    """
    # Startup event
    print("[STARTUP] Creating database tables...")
    create_db_and_tables()
    print("[STARTUP] Database initialized successfully!")
    
    yield
    
    # Shutdown event
    print("[SHUTDOWN] Application shutting down...")

# Create FastAPI app instance with lifespan
app = FastAPI(
    title=settings.app_name,
    description="Investment Discovery Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS (Cross-Origin Resource Sharing)
# Allows requests from frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom auth middleware for logging
app.add_middleware(AuthMiddleware)

# Include all API v1 routers
app.include_router(landing.router, prefix=settings.api_v1_str)
app.include_router(auth.router, prefix=settings.api_v1_str)
app.include_router(founder.router, prefix=settings.api_v1_str)
app.include_router(investor.router, prefix=settings.api_v1_str)
app.include_router(partnership.router, prefix=settings.api_v1_str)

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Simple health check endpoint to verify API is running.
    """
    return {"status": "healthy", "service": settings.app_name}

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Run development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
