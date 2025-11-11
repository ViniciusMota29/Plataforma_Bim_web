"""
Main FastAPI application for BIM-FM Platform
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from app.database import get_db, init_db
from app.routers import ifc, inspections, ai_analysis, assets, blender_sync
from app.config import settings

# Create FastAPI app
app = FastAPI(
    title="BIM-FM Platform API",
    description="Plataforma de gestão de ativos BIM/IFC baseada em openBIM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ifc.router, prefix="/api/ifc", tags=["IFC"])
app.include_router(inspections.router, prefix="/api/inspections", tags=["Inspections"])
app.include_router(ai_analysis.router, prefix="/api/ai", tags=["AI Analysis"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(blender_sync.router, prefix="/api/blender", tags=["Blender Sync"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    # Create upload directories
    os.makedirs(settings.UPLOAD_DIR / "ifc", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR / "images", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR / "videos", exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR / "results", exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BIM-FM Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

