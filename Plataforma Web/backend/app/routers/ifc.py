"""
IFC file upload and processing router
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import os
import ifcopenshell
from pathlib import Path

from app.database import get_db
from app.models import IFCFile, IFCElement, Asset
from app.schemas import IFCFile as IFCFileSchema, IFCFileCreate
from app.config import settings
from app.services.ifc_processor import process_ifc_file

router = APIRouter()


@router.post("/upload", response_model=IFCFileSchema)
async def upload_ifc_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Upload and process IFC file"""
    # Validate file extension
    if not file.filename.endswith(('.ifc', '.IFC')):
        raise HTTPException(status_code=400, detail="File must be .ifc format")
    
    # Save file
    upload_dir = settings.UPLOAD_DIR / "ifc"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    file_size = 0
    
    with open(file_path, "wb") as f:
        content = await file.read()
        file_size = len(content)
        f.write(content)
    
    # Create database record
    db_ifc_file = IFCFile(
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        processing_status="pending"
    )
    db.add(db_ifc_file)
    db.commit()
    db.refresh(db_ifc_file)
    
    # Process IFC file in background
    if background_tasks:
        background_tasks.add_task(process_ifc_file, db_ifc_file.id, str(file_path))
    
    return db_ifc_file


@router.get("/", response_model=List[IFCFileSchema])
def list_ifc_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all uploaded IFC files"""
    files = db.query(IFCFile).offset(skip).limit(limit).all()
    return files


@router.get("/{file_id}", response_model=IFCFileSchema)
def get_ifc_file(file_id: int, db: Session = Depends(get_db)):
    """Get IFC file by ID"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    return ifc_file


@router.get("/{file_id}/elements")
def get_ifc_elements(file_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all elements from an IFC file"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    
    elements = db.query(IFCElement).filter(IFCElement.ifc_file_id == file_id).offset(skip).limit(limit).all()
    return elements


@router.get("/{file_id}/assets")
def get_ifc_assets(file_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all assets (processed elements) from an IFC file"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    
    assets = db.query(Asset).filter(Asset.ifc_file_id == file_id).offset(skip).limit(limit).all()
    return assets


@router.post("/{file_id}/export")
def export_ifc_file(file_id: int, db: Session = Depends(get_db)):
    """Export updated IFC file with all modifications"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    
    # TODO: Implement IFC export with updated properties
    # This would use ifcopenshell to read, modify, and write the IFC file
    return {"message": "Export functionality to be implemented"}

