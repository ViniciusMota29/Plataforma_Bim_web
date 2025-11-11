"""
Blender synchronization router
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import IFCFile, Asset, Inspection
from app.schemas import BlenderSyncRequest, BlenderSyncResponse
from app.services.blender_sync import sync_to_blender, sync_from_blender

router = APIRouter()


@router.post("/sync", response_model=BlenderSyncResponse)
def sync_with_blender(
    request: BlenderSyncRequest,
    db: Session = Depends(get_db)
):
    """Synchronize data with Blender (bidirectional)"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == request.ifc_file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    
    try:
        if request.sync_direction == "to_blender":
            # Export data to Blender format
            result = sync_to_blender(ifc_file, db)
            return BlenderSyncResponse(
                success=True,
                message="Data synchronized to Blender",
                data=result
            )
        elif request.sync_direction == "from_blender":
            # Import data from Blender
            result = sync_from_blender(ifc_file, db)
            return BlenderSyncResponse(
                success=True,
                message="Data synchronized from Blender",
                data=result
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid sync direction")
    except Exception as e:
        return BlenderSyncResponse(
            success=False,
            message=f"Sync failed: {str(e)}"
        )


@router.get("/{ifc_file_id}/blender-data")
def get_blender_data(ifc_file_id: int, db: Session = Depends(get_db)):
    """Get data formatted for Blender add-on"""
    ifc_file = db.query(IFCFile).filter(IFCFile.id == ifc_file_id).first()
    if not ifc_file:
        raise HTTPException(status_code=404, detail="IFC file not found")
    
    assets = db.query(Asset).filter(Asset.ifc_file_id == ifc_file_id).all()
    inspections = db.query(Inspection).join(Asset).filter(Asset.ifc_file_id == ifc_file_id).all()
    
    return {
        "ifc_file": {
            "id": ifc_file.id,
            "filename": ifc_file.filename,
            "project_name": ifc_file.project_name
        },
        "assets": [
            {
                "id": asset.id,
                "ifc_guid": asset.ifc_guid,
                "name": asset.name,
                "condition_status": asset.condition_status,
                "condition_score": asset.condition_score
            }
            for asset in assets
        ],
        "inspections": [
            {
                "id": inspection.id,
                "code": inspection.code,
                "asset_id": inspection.asset_id,
                "severity": inspection.severity,
                "has_pathology": inspection.has_pathology
            }
            for inspection in inspections
        ]
    }

