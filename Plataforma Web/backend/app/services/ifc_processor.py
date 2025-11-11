"""
IFC file processing service using IfcOpenShell
"""
import ifcopenshell
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import IFCFile, IFCElement, Asset
from datetime import datetime
import json


def process_ifc_file(ifc_file_id: int, file_path: str):
    """
    Process IFC file and extract elements/assets
    Runs in background task
    """
    db = SessionLocal()
    try:
        # Update status
        ifc_file = db.query(IFCFile).filter(IFCFile.id == ifc_file_id).first()
        if not ifc_file:
            return
        
        ifc_file.processing_status = "processing"
        db.commit()
        
        # Open IFC file
        try:
            ifc_file_obj = ifcopenshell.open(file_path)
            ifc_file.ifc_schema = ifc_file_obj.schema
            
            # Extract project information
            project = ifc_file_obj.by_type("IfcProject")[0] if ifc_file_obj.by_type("IfcProject") else None
            if project:
                ifc_file.project_name = project.Name or ifc_file.project_name
                ifc_file.project_description = getattr(project, "Description", None)
            
            # Process all elements
            elements_processed = 0
            for element in ifc_file_obj.by_type("IfcProduct"):
                try:
                    # Create IFCElement record
                    db_element = IFCElement(
                        ifc_id=element.id(),
                        ifc_guid=element.GlobalId,
                        ifc_type=element.is_a(),
                        name=getattr(element, "Name", None),
                        ifc_file_id=ifc_file_id,
                        ifc_data=extract_ifc_data(element)
                    )
                    db.add(db_element)
                    
                    # Create Asset record (for elements we want to track)
                    if should_create_asset(element):
                        db_asset = Asset(
                            ifc_guid=element.GlobalId,
                            ifc_type=element.is_a(),
                            name=getattr(element, "Name", None),
                            ifc_file_id=ifc_file_id,
                            description=getattr(element, "Description", None)
                        )
                        db.add(db_asset)
                    
                    elements_processed += 1
                    if elements_processed % 100 == 0:
                        db.commit()
                        
                except Exception as e:
                    print(f"Error processing element {element.id()}: {str(e)}")
                    continue
            
            db.commit()
            
            # Update status
            ifc_file.processing_status = "completed"
            ifc_file.processed_at = datetime.now()
            db.commit()
            
        except Exception as e:
            ifc_file.processing_status = "error"
            ifc_file.processing_error = str(e)
            db.commit()
            raise
            
    finally:
        db.close()


def extract_ifc_data(element):
    """Extract IFC element data as JSON"""
    data = {
        "ifc_id": element.id(),
        "ifc_guid": element.GlobalId,
        "ifc_type": element.is_a(),
    }
    
    # Extract common attributes
    for attr in ["Name", "Description", "Tag", "ObjectType"]:
        if hasattr(element, attr):
            value = getattr(element, attr)
            if value:
                data[attr.lower()] = str(value)
    
    # Extract properties
    if hasattr(element, "IsDefinedBy"):
        properties = []
        for prop_def in element.IsDefinedBy:
            if prop_def.is_a("IfcRelDefinesByProperties"):
                prop_set = prop_def.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    prop_data = {
                        "name": prop_set.Name,
                        "properties": {}
                    }
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            prop_data["properties"][prop.Name] = {
                                "value": str(prop.NominalValue.wrappedValue) if prop.NominalValue else None,
                                "type": prop.NominalValue.wrappedValue.is_a() if prop.NominalValue else None
                            }
                    properties.append(prop_data)
        data["properties"] = properties
    
    return data


def should_create_asset(element):
    """Determine if an IFC element should be tracked as an Asset"""
    # Track structural elements, MEP components, etc.
    asset_types = [
        "IfcBeam", "IfcColumn", "IfcSlab", "IfcWall", "IfcDoor", "IfcWindow",
        "IfcBuildingElementProxy", "IfcBuildingElement", "IfcElement",
        "IfcFlowTerminal", "IfcFlowController", "IfcFlowMovingDevice",
        "IfcDistributionElement", "IfcDistributionFlowElement"
    ]
    return element.is_a() in asset_types

