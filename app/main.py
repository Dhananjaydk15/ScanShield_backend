from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ports as ports_router
from .routers import scan as scan_router

app = FastAPI(
    title="Comprehensive Nmap Security Scanner API",
    description="Port + security headers scanning (risk-assessment). Use with care.",
    version="1.0.0",
)

# CORS — adjust origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(ports_router.router, prefix="/api")
app.include_router(scan_router.router,prefix="/api" )

@app.get("/", tags=["Root"])
def root():
    
    return {"message": "Welcome to ScanShield"}
