from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, scans, teams, dashboard

app = FastAPI(
    title="ScanGuard AI",
    description="Nmap Scan Analysis Platform with AI-Powered Insights",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scans.router)
app.include_router(teams.router)
app.include_router(dashboard.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ScanGuard AI"}
