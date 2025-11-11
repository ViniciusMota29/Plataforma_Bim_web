"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Asset Schemas
class AssetBase(BaseModel):
    ifc_guid: str
    ifc_type: str
    name: Optional[str] = None
    description: Optional[str] = None


class AssetCreate(AssetBase):
    ifc_file_id: int
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    location_building: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    condition_status: Optional[str] = None
    condition_score: Optional[int] = None


class Asset(AssetBase):
    id: int
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    condition_status: Optional[str] = None
    condition_score: Optional[int] = None
    last_inspection_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# IFC File Schemas
class IFCFileBase(BaseModel):
    filename: str
    project_name: Optional[str] = None


class IFCFileCreate(IFCFileBase):
    pass


class IFCFile(IFCFileBase):
    id: int
    file_path: str
    file_size: Optional[int] = None
    ifc_schema: Optional[str] = None
    processing_status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Inspection Schemas
class InspectionPhotoBase(BaseModel):
    file_name: str
    file_path: str


class InspectionPhoto(InspectionPhotoBase):
    id: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class InspectionBase(BaseModel):
    code: str
    inspection_date: datetime
    has_pathology: bool
    severity: Optional[int] = Field(None, ge=1, le=4)
    location: str
    observations: Optional[str] = None


class InspectionCreate(InspectionBase):
    asset_id: int
    pathology_type: Optional[str] = None


class InspectionUpdate(BaseModel):
    observations: Optional[str] = None
    severity: Optional[int] = Field(None, ge=1, le=4)
    condition_status: Optional[str] = None


class Inspection(InspectionBase):
    id: int
    asset_id: int
    pathology_type: Optional[str] = None
    ai_analysis_performed: bool
    ai_confidence: Optional[float] = None
    photos: List[InspectionPhoto] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# AI Analysis Schemas
class AIAnalysisRequest(BaseModel):
    image_paths: List[str]
    asset_id: Optional[int] = None
    inspection_id: Optional[int] = None


class AIAnalysisResult(BaseModel):
    success: bool
    detections: List[Dict[str, Any]]
    confidence: float
    mask_path: Optional[str] = None
    heatmap_path: Optional[str] = None
    result_path: Optional[str] = None


# Blender Sync Schemas
class BlenderSyncRequest(BaseModel):
    ifc_file_id: int
    sync_direction: str = Field(..., pattern="^(to_blender|from_blender)$")


class BlenderSyncResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

