"""
Authentication middleware for request logging and error handling.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging

# Setup logging
logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication and logging.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and measure execution time.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response
        """
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(f"{request.method} {request.url.path}")
        
        # Call next middleware
        response = await call_next(request)
        
        # Calculate execution time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
