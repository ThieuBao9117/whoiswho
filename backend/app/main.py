"""
WHO Is WHO API - Main Application

Independent from HRM:
- Uses its own database (csb_db)
- Employee data synced via API from HRM
- Migrations managed by Alembic
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base, init_db
from app.api import auth, connectors, connections, webhooks, targets, admin, sync
from app.models import csb_models  # Ensure CSB models are registered (NOT HRM)

# Initialize CSB database - DISABLED because we use Alembic migrations now
# init_db()

app = FastAPI(
    title="WHO Is WHO API",
    description="Connect Reward System - Independent from HRM Database",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production
        "http://50.50.50.4",
        "https://50.50.50.4",
        # Local development
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Internal IPs
        "http://50.50.51.220:5173",
        "http://50.50.51.220:8000",
        "http://50.50.51.220",
        "http://50.50.50.24:5173",
        "http://50.50.50.24:7070",
        "http://50.50.50.24",
        # Ngrok
        "https://8848-113-161-143-253.ngrok-free.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sync.router, tags=["Sync"])  # NEW - HRM sync endpoints
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(targets.router, prefix="/api/targets", tags=["Targets"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
def read_root():
    return {
        "message": "WHO Is WHO API is running",
        "database": "Independent from HRM",
        "version": "2.0.0"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "csb_db (independent)"
    }
