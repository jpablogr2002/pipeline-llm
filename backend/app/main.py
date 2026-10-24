from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.endpoints import router as api_router
from app.core.logging_congif import setup_logging

# Logging configuration
setup_logging()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="MediaGroup LATAM - Pipeline Inteligente")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}