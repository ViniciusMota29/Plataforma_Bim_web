-- Initialize MIR Requirements if not already inserted
-- This script can be run separately to ensure all requirements are present

DO $$
BEGIN
    -- Only insert if table is empty
    IF NOT EXISTS (SELECT 1 FROM mir_requirements LIMIT 1) THEN
        INSERT INTO mir_requirements (requirement_number, category, requirement_name, description, is_mandatory) VALUES
        (1, 'Design', 'Design Criteria', 'Design specifications and criteria', TRUE),
        (2, 'Design', 'Design Standard', 'Applicable design standards and codes', TRUE),
        (3, 'Design', 'Design Loads', 'Design loads and load combinations', TRUE),
        (4, 'Design', 'Design Life', 'Expected design life of the asset', TRUE),
        (5, 'Design', 'Design Documentation', 'Design drawings and calculations', TRUE),
        (6, 'Manufacturer', 'Manufacturer Name', 'Name of the manufacturer', TRUE),
        (7, 'Manufacturer', 'Supplier Name', 'Name of the supplier', TRUE),
        (8, 'Manufacturer', 'Model Number', 'Model or product number', TRUE),
        (9, 'Manufacturer', 'Serial Number', 'Unique serial number', TRUE),
        (10, 'Manufacturer', 'Manufacturing Date', 'Date of manufacture', FALSE),
        (11, 'Location', 'Building', 'Building name or identifier', TRUE),
        (12, 'Location', 'Floor', 'Floor or level', TRUE),
        (13, 'Location', 'Room', 'Room or space identifier', TRUE),
        (14, 'Location', 'Coordinates', 'Spatial coordinates (X, Y, Z)', TRUE),
        (15, 'Location', 'Zone', 'Functional zone or area', FALSE),
        (16, 'Warranty', 'Warranty Start Date', 'Warranty start date', FALSE),
        (17, 'Warranty', 'Warranty End Date', 'Warranty expiration date', FALSE),
        (18, 'Warranty', 'Warranty Provider', 'Warranty provider name', FALSE),
        (19, 'Warranty', 'Warranty Terms', 'Warranty terms and conditions', FALSE),
        (20, 'Warranty', 'Warranty Coverage', 'What is covered under warranty', FALSE),
        (21, 'Life Cycle', 'Installation Date', 'Date of installation', FALSE),
        (22, 'Life Cycle', 'Expected Life Span', 'Expected operational life', FALSE),
        (23, 'Life Cycle', 'Replacement Cost', 'Estimated replacement cost', FALSE),
        (24, 'Life Cycle', 'Maintenance Cost', 'Annual maintenance cost', FALSE),
        (25, 'Life Cycle', 'Life Cycle Cost', 'Total life cycle cost', FALSE),
        (26, 'Spare Parts', 'Spare Parts List', 'List of required spare parts', FALSE),
        (27, 'Spare Parts', 'Availability', 'Spare parts availability status', FALSE),
        (28, 'Spare Parts', 'Supplier Information', 'Spare parts supplier details', FALSE),
        (29, 'Spare Parts', 'Lead Time', 'Lead time for spare parts', FALSE),
        (30, 'Spare Parts', 'Critical Parts', 'Critical spare parts identification', FALSE),
        (31, 'Documentation', 'Delivery Documentation', 'As-delivered documentation', TRUE),
        (32, 'Documentation', 'Operation Manual', 'Operation and maintenance manual', FALSE),
        (33, 'Documentation', 'Warranty Certificate', 'Warranty certificate', FALSE),
        (34, 'Documentation', 'Test Reports', 'Test and commissioning reports', FALSE),
        (35, 'Documentation', 'As-Built Drawings', 'As-built drawings and records', FALSE),
        (36, 'Maintenance', 'Maintenance History', 'Historical maintenance records', FALSE),
        (37, 'Maintenance', 'Maintenance Schedule', 'Scheduled maintenance plan', FALSE),
        (38, 'Maintenance', 'Maintenance Procedures', 'Standard maintenance procedures', FALSE),
        (39, 'Maintenance', 'Maintenance Frequency', 'Recommended maintenance frequency', FALSE),
        (40, 'Maintenance', 'Maintenance Cost', 'Historical maintenance costs', FALSE),
        (41, 'Inspection', 'Inspection Reports', 'Inspection reports and findings', TRUE),
        (42, 'Inspection', 'Inspection Frequency', 'Recommended inspection frequency', FALSE),
        (43, 'Inspection', 'Asset Condition', 'Current condition assessment', TRUE),
        (44, 'Inspection', 'Condition Score', 'Numerical condition score (1-4)', TRUE),
        (45, 'Inspection', 'Next Inspection Date', 'Scheduled next inspection date', FALSE);
    END IF;
END $$;

