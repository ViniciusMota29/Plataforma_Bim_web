"""
Inspection management router
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
from pathlib import Path

from app.database import get_db
from app.models import Inspection, InspectionPhoto, Asset
from app.schemas import Inspection as InspectionSchema, InspectionCreate, InspectionUpdate
from app.config import settings

router = APIRouter()


@router.post("/", response_model=InspectionSchema)
async def create_inspection(
    code: str = Form(...),
    asset_id: int = Form(...),
    inspection_date: str = Form(...),
    has_pathology: bool = Form(...),
    severity: Optional[int] = Form(None),
    location: str = Form(...),
    observations: Optional[str] = Form(None),
    pathology_type: Optional[str] = Form(None),
    photos: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    """Create a new inspection"""
    # Validate asset exists
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Check if code already exists
    existing = db.query(Inspection).filter(Inspection.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Inspection code already exists")
    
    # Parse date
    try:
        inspection_dt = datetime.fromisoformat(inspection_date.replace("Z", "+00:00"))
    except:
        inspection_dt = datetime.now()
    
    # Create inspection
    db_inspection = Inspection(
        code=code,
        asset_id=asset_id,
        inspection_date=inspection_dt,
        has_pathology=has_pathology,
        severity=severity if has_pathology else None,
        location=location,
        observations=observations,
        pathology_type=pathology_type
    )
    db.add(db_inspection)
    db.commit()
    db.refresh(db_inspection)
    
    # Save photos
    if photos:
        upload_dir = settings.UPLOAD_DIR / "images" / f"inspection_{db_inspection.id}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, photo in enumerate(photos):
            file_path = upload_dir / f"{code}_img{idx + 1}{Path(photo.filename).suffix}"
            content = await photo.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            db_photo = InspectionPhoto(
                inspection_id=db_inspection.id,
                file_path=str(file_path),
                file_name=photo.filename,
                file_size=len(content),
                mime_type=photo.content_type
            )
            db.add(db_photo)
        
        db.commit()
    
    # Update asset condition
    if has_pathology and severity:
        asset.condition_score = severity
        asset.condition_status = get_condition_status(severity)
        asset.last_inspection_date = inspection_dt
        db.commit()
    
    return db_inspection


@router.get("/", response_model=List[InspectionSchema])
def list_inspections(
    skip: int = 0,
    limit: int = 100,
    asset_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all inspections"""
    query = db.query(Inspection)
    if asset_id:
        query = query.filter(Inspection.asset_id == asset_id)
    
    inspections = query.order_by(Inspection.inspection_date.desc()).offset(skip).limit(limit).all()
    return inspections


@router.get("/{inspection_id}", response_model=InspectionSchema)
def get_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """Get inspection by ID"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.put("/{inspection_id}", response_model=InspectionSchema)
def update_inspection(
    inspection_id: int,
    inspection_update: InspectionUpdate,
    db: Session = Depends(get_db)
):
    """Update inspection"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    for key, value in inspection_update.dict(exclude_unset=True).items():
        setattr(inspection, key, value)
    
    db.commit()
    db.refresh(inspection)
    return inspection


@router.delete("/{inspection_id}")
def delete_inspection(inspection_id: int, db: Session = Depends(get_db)):
    """Delete inspection"""
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    db.delete(inspection)
    db.commit()
    return {"message": "Inspection deleted"}


def get_condition_status(severity: int) -> str:
    """Convert severity to condition status"""
    status_map = {
        1: "Critical",
        2: "Poor",
        3: "Fair",
        4: "Good"
    }
    return status_map.get(severity, "Unknown")

