"""
Main FastAPI application entry point for AfriConnect backend.
Initializes the API, registers routers, and sets up middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import create_db_and_tables
from app.middleware.auth_middleware import AuthMiddleware
from app.api.v1 import auth, founder, investor, partnership

# Get settings
settings = get_settings()

# Create FastAPI app instance
app = FastAPI(
    title=settings.app_name,
    description="Investment Discovery Platform API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (Cross-Origin Resource Sharing)
# Allows requests from frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom auth middleware for logging
app.add_middleware(AuthMiddleware)


# Startup event - runs when application starts
@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on startup.
    This creates all tables defined in SQLModel models if they don't exist.
    """
    print("[STARTUP] Creating database tables...")
    create_db_and_tables()
    print("[STARTUP] Database initialized successfully!")


# Shutdown event - runs when application shuts down
@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup operations on shutdown.
    """
    print("[SHUTDOWN] Application shutting down...")


# Include all API v1 routers
# These routes will be prefixed with /api/v1
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
# Use: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    
    # Run development server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
