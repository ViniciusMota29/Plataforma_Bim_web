"""
AI Analysis router for image/video processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
from pathlib import Path

from app.database import get_db
from app.models import Inspection, Asset
from app.schemas import AIAnalysisRequest, AIAnalysisResult
from app.config import settings
from app.services.ai_service import analyze_image_with_ai

router = APIRouter()


@router.post("/analyze", response_model=AIAnalysisResult)
async def analyze_images(
    images: List[UploadFile] = File(...),
    asset_id: int = None,
    inspection_id: int = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Analyze images/videos using AI model (SwinDeepLab)"""
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    # Validate asset or inspection exists
    if asset_id:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
    
    if inspection_id:
        inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
        if not inspection:
            raise HTTPException(status_code=404, detail="Inspection not found")
    
    # Save uploaded images
    upload_dir = settings.UPLOAD_DIR / "images" / "ai_input"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    image_paths = []
    for image in images:
        file_path = upload_dir / image.filename
        content = await image.read()
        with open(file_path, "wb") as f:
            f.write(content)
        image_paths.append(str(file_path))
    
    # Process images with AI
    try:
        results = analyze_image_with_ai(image_paths, settings)
        
        # Update inspection if provided
        if inspection_id:
            inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
            if inspection and results["detections"]:
                inspection.ai_analysis_performed = True
                inspection.ai_confidence = results["confidence"]
                if results.get("mask_path"):
                    inspection.ai_detection_mask_path = results["mask_path"]
                if results.get("heatmap_path"):
                    inspection.ai_heatmap_path = results["heatmap_path"]
                db.commit()
        
        return AIAnalysisResult(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")


@router.post("/analyze-video")
async def analyze_video(
    video: UploadFile = File(...),
    asset_id: int = None,
    inspection_id: int = None,
    fps: float = 1.0,
    db: Session = Depends(get_db)
):
    """Analyze video using AI model"""
    # TODO: Implement video analysis
    # This would extract frames and process them similar to analyze_images
    return {"message": "Video analysis to be implemented"}

