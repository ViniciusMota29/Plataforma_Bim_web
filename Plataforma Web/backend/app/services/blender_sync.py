"""
Blender synchronization service
Handles bidirectional data exchange with Blender add-on
"""
from sqlalchemy.orm import Session
from app.models import IFCFile, Asset, Inspection
from typing import Dict, Any
import json


def sync_to_blender(ifc_file: IFCFile, db: Session) -> Dict[str, Any]:
    """
    Prepare data for export to Blender
    Returns data structure compatible with BlenderBIM/Bonsai
    """
    assets = db.query(Asset).filter(Asset.ifc_file_id == ifc_file.id).all()
    inspections = db.query(Inspection).join(Asset).filter(Asset.ifc_file_id == ifc_file.id).all()
    
    # Format data for Blender
    blender_data = {
        "ifc_file": {
            "id": ifc_file.id,
            "filename": ifc_file.filename,
            "file_path": ifc_file.file_path
        },
        "assets": [],
        "inspections": []
    }
    
    for asset in assets:
        asset_data = {
            "ifc_guid": asset.ifc_guid,
            "name": asset.name,
            "ifc_type": asset.ifc_type,
            "condition_status": asset.condition_status,
            "condition_score": asset.condition_score,
            "manufacturer": asset.manufacturer,
            "serial_number": asset.serial_number,
            "location": {
                "building": asset.location_building,
                "floor": asset.location_floor,
                "room": asset.location_room
            }
        }
        blender_data["assets"].append(asset_data)
    
    for inspection in inspections:
        inspection_data = {
            "code": inspection.code,
            "asset_ifc_guid": inspection.asset.ifc_guid,
            "inspection_date": inspection.inspection_date.isoformat() if inspection.inspection_date else None,
            "has_pathology": inspection.has_pathology,
            "severity": inspection.severity,
            "location": inspection.location,
            "observations": inspection.observations
        }
        blender_data["inspections"].append(inspection_data)
    
    return blender_data


def sync_from_blender(ifc_file: IFCFile, db: Session, blender_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Import data from Blender
    Updates assets and inspections based on Blender modifications
    """
    if blender_data is None:
        # In real implementation, this would receive data from Blender add-on
        return {"message": "No data provided from Blender"}
    
    updated_count = 0
    
    # Update assets
    if "assets" in blender_data:
        for asset_data in blender_data["assets"]:
            asset = db.query(Asset).filter(
                Asset.ifc_guid == asset_data.get("ifc_guid"),
                Asset.ifc_file_id == ifc_file.id
            ).first()
            
            if asset:
                if "condition_status" in asset_data:
                    asset.condition_status = asset_data["condition_status"]
                if "condition_score" in asset_data:
                    asset.condition_score = asset_data["condition_score"]
                updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Updated {updated_count} assets from Blender",
        "updated_count": updated_count
    }

