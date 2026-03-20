from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import os
import logging

from backend.core.config import settings
from backend.core.errors import app_exception_handler, general_exception_handler, AppException
from backend.core.rate_limiter import limiter
from backend.api.routes import health, pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    # State Limiter
    app.state.limiter = limiter

    # Security Middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Should be restricted in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Routers
    app.include_router(health.router, prefix=settings.API_V1_STR)
    app.include_router(pdf.router, prefix=settings.API_V1_STR)

    return app

app = create_app()

# Mount Frontend if exists (for Cloud Run combined deployment)
frontend_dist = os.environ.get("FRONTEND_DIST")
if frontend_dist and os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=True)
