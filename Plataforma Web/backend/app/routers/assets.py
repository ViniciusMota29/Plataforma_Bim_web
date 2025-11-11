"""
Asset management router
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Asset, Inspection
from app.schemas import Asset as AssetSchema, AssetUpdate

router = APIRouter()


@router.get("/", response_model=List[AssetSchema])
def list_assets(
    skip: int = 0,
    limit: int = 100,
    ifc_file_id: Optional[int] = None,
    condition_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all assets"""
    query = db.query(Asset)
    
    if ifc_file_id:
        query = query.filter(Asset.ifc_file_id == ifc_file_id)
    if condition_status:
        query = query.filter(Asset.condition_status == condition_status)
    
    assets = query.offset(skip).limit(limit).all()
    return assets


@router.get("/{asset_id}", response_model=AssetSchema)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset by ID"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetSchema)
def update_asset(
    asset_id: int,
    asset_update: AssetUpdate,
    db: Session = Depends(get_db)
):
    """Update asset properties"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for key, value in asset_update.dict(exclude_unset=True).items():
        setattr(asset, key, value)
    
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{asset_id}/inspections")
def get_asset_inspections(asset_id: int, db: Session = Depends(get_db)):
    """Get all inspections for an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    inspections = db.query(Inspection).filter(Inspection.asset_id == asset_id).order_by(Inspection.inspection_date.desc()).all()
    return inspections


@router.get("/{asset_id}/statistics")
def get_asset_statistics(asset_id: int, db: Session = Depends(get_db)):
    """Get statistics for an asset"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    inspections = db.query(Inspection).filter(Inspection.asset_id == asset_id).all()
    
    total_inspections = len(inspections)
    inspections_with_pathology = sum(1 for i in inspections if i.has_pathology)
    latest_inspection = max(inspections, key=lambda x: x.inspection_date) if inspections else None
    
    severity_distribution = {}
    for inspection in inspections:
        if inspection.severity:
            severity_distribution[inspection.severity] = severity_distribution.get(inspection.severity, 0) + 1
    
    return {
        "asset_id": asset_id,
        "total_inspections": total_inspections,
        "inspections_with_pathology": inspections_with_pathology,
        "latest_inspection_date": latest_inspection.inspection_date if latest_inspection else None,
        "current_condition": asset.condition_status,
        "current_condition_score": asset.condition_score,
        "severity_distribution": severity_distribution
    }

