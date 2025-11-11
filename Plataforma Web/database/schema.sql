-- BIM-FM Platform Database Schema
-- Based on MIR (Minimum Information Requirements) - 45 requirements
-- PostgreSQL with PostGIS extension

-- Enable PostGIS for spatial data
CREATE EXTENSION IF NOT EXISTS postgis;

-- IFC Files table
CREATE TABLE ifc_files (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    ifc_schema VARCHAR(50),
    project_name VARCHAR(255),
    project_description TEXT,
    processing_status VARCHAR(50) DEFAULT 'pending',
    processing_error TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- IFC Elements table (raw IFC data)
CREATE TABLE ifc_elements (
    id SERIAL PRIMARY KEY,
    ifc_id INTEGER NOT NULL,
    ifc_guid VARCHAR(255) UNIQUE NOT NULL,
    ifc_type VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    ifc_data JSONB,
    ifc_file_id INTEGER NOT NULL REFERENCES ifc_files(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE SET NULL
);

CREATE INDEX idx_ifc_elements_guid ON ifc_elements(ifc_guid);
CREATE INDEX idx_ifc_elements_file ON ifc_elements(ifc_file_id);
CREATE INDEX idx_ifc_elements_type ON ifc_elements(ifc_type);

-- Assets table (BIM elements with MIR data)
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    ifc_guid VARCHAR(255) UNIQUE NOT NULL,
    ifc_type VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    description TEXT,
    
    -- MIR: Design Criteria
    design_criteria TEXT,
    design_standard VARCHAR(255),
    
    -- MIR: Manufacturer/Supplier Information
    manufacturer VARCHAR(255),
    supplier VARCHAR(255),
    model_number VARCHAR(255),
    serial_number VARCHAR(255) UNIQUE,
    
    -- MIR: Asset Location (using PostGIS)
    location_building VARCHAR(255),
    location_floor VARCHAR(255),
    location_room VARCHAR(255),
    location_coordinates GEOMETRY(POINT, 4326),
    
    -- MIR: Warranty Information
    warranty_start_date TIMESTAMP,
    warranty_end_date TIMESTAMP,
    warranty_provider VARCHAR(255),
    
    -- MIR: Life Cycle Cost
    installation_date TIMESTAMP,
    expected_life_span INTEGER, -- years
    replacement_cost DECIMAL(12, 2),
    maintenance_cost DECIMAL(12, 2),
    
    -- MIR: Spare Parts
    spare_parts_list JSONB,
    spare_parts_availability VARCHAR(255),
    
    -- MIR: Delivery Documentation
    delivery_documentation JSONB, -- Array of document paths/URLs
    
    -- Asset Condition
    condition_status VARCHAR(50), -- Good, Fair, Poor, Critical
    condition_score INTEGER CHECK (condition_score >= 1 AND condition_score <= 4),
    last_inspection_date TIMESTAMP,
    
    ifc_file_id INTEGER REFERENCES ifc_files(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assets_guid ON assets(ifc_guid);
CREATE INDEX idx_assets_serial ON assets(serial_number);
CREATE INDEX idx_assets_file ON assets(ifc_file_id);
CREATE INDEX idx_assets_condition ON assets(condition_status);
CREATE INDEX idx_assets_location ON assets USING GIST(location_coordinates);

-- Property Sets table
CREATE TABLE property_sets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Properties table
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    value TEXT,
    data_type VARCHAR(50),
    unit VARCHAR(50),
    property_set_id INTEGER REFERENCES property_sets(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_properties_asset ON properties(asset_id);
CREATE INDEX idx_properties_set ON properties(property_set_id);

-- Inspections table
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255) UNIQUE NOT NULL,
    inspection_date TIMESTAMP NOT NULL,
    
    -- Pathology information
    has_pathology BOOLEAN NOT NULL DEFAULT FALSE,
    pathology_type VARCHAR(255),
    severity INTEGER CHECK (severity >= 1 AND severity <= 4),
    location VARCHAR(255) NOT NULL,
    observations TEXT,
    
    -- AI Analysis results
    ai_analysis_performed BOOLEAN DEFAULT FALSE,
    ai_confidence DECIMAL(5, 4),
    ai_detection_mask_path TEXT,
    ai_heatmap_path TEXT,
    
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inspections_code ON inspections(code);
CREATE INDEX idx_inspections_asset ON inspections(asset_id);
CREATE INDEX idx_inspections_date ON inspections(inspection_date);
CREATE INDEX idx_inspections_pathology ON inspections(has_pathology);

-- Inspection Photos table
CREATE TABLE inspection_photos (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    inspection_id INTEGER NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_photos_inspection ON inspection_photos(inspection_id);

-- MIR Requirements tracking table
CREATE TABLE mir_requirements (
    id SERIAL PRIMARY KEY,
    requirement_number INTEGER UNIQUE NOT NULL,
    category VARCHAR(255) NOT NULL,
    requirement_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert MIR Requirements (45 requirements based on article)
INSERT INTO mir_requirements (requirement_number, category, requirement_name, description, is_mandatory) VALUES
-- Design Criteria (1-5)
(1, 'Design', 'Design Criteria', 'Design specifications and criteria', TRUE),
(2, 'Design', 'Design Standard', 'Applicable design standards and codes', TRUE),
(3, 'Design', 'Design Loads', 'Design loads and load combinations', TRUE),
(4, 'Design', 'Design Life', 'Expected design life of the asset', TRUE),
(5, 'Design', 'Design Documentation', 'Design drawings and calculations', TRUE),

-- Manufacturer/Supplier (6-10)
(6, 'Manufacturer', 'Manufacturer Name', 'Name of the manufacturer', TRUE),
(7, 'Manufacturer', 'Supplier Name', 'Name of the supplier', TRUE),
(8, 'Manufacturer', 'Model Number', 'Model or product number', TRUE),
(9, 'Manufacturer', 'Serial Number', 'Unique serial number', TRUE),
(10, 'Manufacturer', 'Manufacturing Date', 'Date of manufacture', FALSE),

-- Location (11-15)
(11, 'Location', 'Building', 'Building name or identifier', TRUE),
(12, 'Location', 'Floor', 'Floor or level', TRUE),
(13, 'Location', 'Room', 'Room or space identifier', TRUE),
(14, 'Location', 'Coordinates', 'Spatial coordinates (X, Y, Z)', TRUE),
(15, 'Location', 'Zone', 'Functional zone or area', FALSE),

-- Warranty (16-20)
(16, 'Warranty', 'Warranty Start Date', 'Warranty start date', FALSE),
(17, 'Warranty', 'Warranty End Date', 'Warranty expiration date', FALSE),
(18, 'Warranty', 'Warranty Provider', 'Warranty provider name', FALSE),
(19, 'Warranty', 'Warranty Terms', 'Warranty terms and conditions', FALSE),
(20, 'Warranty', 'Warranty Coverage', 'What is covered under warranty', FALSE),

-- Life Cycle (21-25)
(21, 'Life Cycle', 'Installation Date', 'Date of installation', FALSE),
(22, 'Life Cycle', 'Expected Life Span', 'Expected operational life', FALSE),
(23, 'Life Cycle', 'Replacement Cost', 'Estimated replacement cost', FALSE),
(24, 'Life Cycle', 'Maintenance Cost', 'Annual maintenance cost', FALSE),
(25, 'Life Cycle', 'Life Cycle Cost', 'Total life cycle cost', FALSE),

-- Spare Parts (26-30)
(26, 'Spare Parts', 'Spare Parts List', 'List of required spare parts', FALSE),
(27, 'Spare Parts', 'Availability', 'Spare parts availability status', FALSE),
(28, 'Spare Parts', 'Supplier Information', 'Spare parts supplier details', FALSE),
(29, 'Spare Parts', 'Lead Time', 'Lead time for spare parts', FALSE),
(30, 'Spare Parts', 'Critical Parts', 'Critical spare parts identification', FALSE),

-- Documentation (31-35)
(31, 'Documentation', 'Delivery Documentation', 'As-delivered documentation', TRUE),
(32, 'Documentation', 'Operation Manual', 'Operation and maintenance manual', FALSE),
(33, 'Documentation', 'Warranty Certificate', 'Warranty certificate', FALSE),
(34, 'Documentation', 'Test Reports', 'Test and commissioning reports', FALSE),
(35, 'Documentation', 'As-Built Drawings', 'As-built drawings and records', FALSE),

-- Maintenance (36-40)
(36, 'Maintenance', 'Maintenance History', 'Historical maintenance records', FALSE),
(37, 'Maintenance', 'Maintenance Schedule', 'Scheduled maintenance plan', FALSE),
(38, 'Maintenance', 'Maintenance Procedures', 'Standard maintenance procedures', FALSE),
(39, 'Maintenance', 'Maintenance Frequency', 'Recommended maintenance frequency', FALSE),
(40, 'Maintenance', 'Maintenance Cost', 'Historical maintenance costs', FALSE),

-- Inspection (41-45)
(41, 'Inspection', 'Inspection Reports', 'Inspection reports and findings', TRUE),
(42, 'Inspection', 'Inspection Frequency', 'Recommended inspection frequency', FALSE),
(43, 'Inspection', 'Asset Condition', 'Current condition assessment', TRUE),
(44, 'Inspection', 'Condition Score', 'Numerical condition score (1-4)', TRUE),
(45, 'Inspection', 'Next Inspection Date', 'Scheduled next inspection date', FALSE);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inspections_updated_at BEFORE UPDATE ON inspections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

