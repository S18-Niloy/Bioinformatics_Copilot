from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
import logging

from database import Base, engine
from models.user import User  # noqa: register
from api import users, chat, sequence, protein, gnn

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bioinformatics Copilot API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Security: Trusted host validation
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
)

# Security: Restrict CORS to specific origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)

# Security: Exception handler to prevent stack trace leakage
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {type(exc).__name__}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

app.include_router(users.router)
app.include_router(chat.router)
app.include_router(sequence.router)
app.include_router(protein.router)
app.include_router(gnn.router)

@app.get("/")
def root():
    return {"name": "Bioinformatics Copilot", "docs": "/docs" if os.getenv("ENVIRONMENT") != "production" else None}
