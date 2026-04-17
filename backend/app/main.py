from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import auth, connectors, connections, webhooks, targets, admin
from app.models import crw_models, hrm_models  # Ensure models are registered

# Automatically create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ConnectReward API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(connections.router, prefix="/api/connections", tags=["Connections"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(targets.router, prefix="/api/targets", tags=["Targets"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
# Note: progress, rewards, and admin api will be hooked up similarly 

@app.get("/")
def read_root():
    return {"message": "ConnectReward Backend API is running"}
