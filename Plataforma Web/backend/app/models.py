"""
SQLAlchemy models for BIM-FM Platform
Based on MIR (Minimum Information Requirements) - 45 requirements
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Asset(Base):
    """Asset/Element model - represents BIM elements with MIR data"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    ifc_guid = Column(String, unique=True, index=True, nullable=False)
    ifc_type = Column(String, nullable=False)
    name = Column(String)
    description = Column(Text)
    
    # MIR Requirements - Design Criteria
    design_criteria = Column(Text)
    design_standard = Column(String)
    
    # MIR Requirements - Manufacturer/Supplier
    manufacturer = Column(String)
    supplier = Column(String)
    model_number = Column(String)
    serial_number = Column(String, unique=True, index=True)
    
    # MIR Requirements - Location
    location_building = Column(String)
    location_floor = Column(String)
    location_room = Column(String)
    location_coordinates = Column(JSON)  # PostGIS geometry stored as JSON
    
    # MIR Requirements - Warranty
    warranty_start_date = Column(DateTime)
    warranty_end_date = Column(DateTime)
    warranty_provider = Column(String)
    
    # MIR Requirements - Life Cycle
    installation_date = Column(DateTime)
    expected_life_span = Column(Integer)  # years
    replacement_cost = Column(Float)
    maintenance_cost = Column(Float)
    
    # MIR Requirements - Spare Parts
    spare_parts_list = Column(JSON)
    spare_parts_availability = Column(String)
    
    # MIR Requirements - Delivery Documentation
    delivery_documentation = Column(JSON)  # List of document paths/URLs
    
    # Asset Condition
    condition_status = Column(String)  # Good, Fair, Poor, Critical
    condition_score = Column(Integer)  # 1-4 (matching severity)
    last_inspection_date = Column(DateTime)
    
    # Relationships
    ifc_file_id = Column(Integer, ForeignKey("ifc_files.id"))
    ifc_file = relationship("IFCFile", back_populates="assets")
    
    inspections = relationship("Inspection", back_populates="asset", cascade="all, delete-orphan")
    properties = relationship("Property", back_populates="asset", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class IFCFile(Base):
    """IFC file model"""
    __tablename__ = "ifc_files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)  # bytes
    ifc_schema = Column(String)  # IFC2X3, IFC4, etc.
    project_name = Column(String)
    project_description = Column(Text)
    
    # Processing status
    processing_status = Column(String, default="pending")  # pending, processing, completed, error
    processing_error = Column(Text)
    
    # Relationships
    assets = relationship("Asset", back_populates="ifc_file")
    elements = relationship("IFCElement", back_populates="ifc_file", cascade="all, delete-orphan")
    
    # Timestamps
    uploaded_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime)


class IFCElement(Base):
    """Raw IFC element data"""
    __tablename__ = "ifc_elements"
    
    id = Column(Integer, primary_key=True, index=True)
    ifc_id = Column(Integer, nullable=False)
    ifc_guid = Column(String, unique=True, index=True, nullable=False)
    ifc_type = Column(String, nullable=False)
    name = Column(String)
    
    # Raw IFC data as JSON
    ifc_data = Column(JSON)
    
    # Relationships
    ifc_file_id = Column(Integer, ForeignKey("ifc_files.id"), nullable=False)
    ifc_file = relationship("IFCFile", back_populates="elements")
    
    asset_id = Column(Integer, ForeignKey("assets.id"))
    asset = relationship("Asset", foreign_keys=[asset_id])


class PropertySet(Base):
    """IFC Property Set"""
    __tablename__ = "property_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Relationships
    properties = relationship("Property", back_populates="property_set", cascade="all, delete-orphan")


class Property(Base):
    """IFC Property"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    value = Column(Text)
    data_type = Column(String)  # String, Integer, Float, Boolean, etc.
    unit = Column(String)
    
    # Relationships
    property_set_id = Column(Integer, ForeignKey("property_sets.id"))
    property_set = relationship("PropertySet", back_populates="properties")
    
    asset_id = Column(Integer, ForeignKey("assets.id"))
    asset = relationship("Asset", back_populates="properties")


class Inspection(Base):
    """Inspection record - similar to current plugin structure"""
    __tablename__ = "inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    inspection_date = Column(DateTime, nullable=False)
    
    # Pathology information
    has_pathology = Column(Boolean, nullable=False, default=False)
    pathology_type = Column(String)
    severity = Column(Integer)  # 1-4 (1=Critical, 4=Good)
    location = Column(String, nullable=False)
    observations = Column(Text)
    
    # AI Analysis results
    ai_analysis_performed = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    ai_detection_mask_path = Column(String)
    ai_heatmap_path = Column(String)
    
    # Relationships
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    asset = relationship("Asset", back_populates="inspections")
    
    photos = relationship("InspectionPhoto", back_populates="inspection", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class InspectionPhoto(Base):
    """Inspection photos"""
    __tablename__ = "inspection_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    # Relationships
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    inspection = relationship("Inspection", back_populates="photos")
    
    # Timestamps
    uploaded_at = Column(DateTime, server_default=func.now())


class MIRRequirement(Base):
    """MIR (Minimum Information Requirements) tracking"""
    __tablename__ = "mir_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    requirement_number = Column(Integer, unique=True, nullable=False)
    category = Column(String, nullable=False)  # Design, Manufacturer, Location, etc.
    requirement_name = Column(String, nullable=False)
    description = Column(Text)
    is_mandatory = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

