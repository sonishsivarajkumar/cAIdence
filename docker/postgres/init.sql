-- Initialize database for cAIdence
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for storing clinical documents
CREATE TABLE clinical_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    document_type VARCHAR(100),
    content TEXT NOT NULL,
    metadata JSONB,
    created_date TIMESTAMP,
    processed_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing extracted entities
CREATE TABLE extracted_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES clinical_documents(id) ON DELETE CASCADE,
    entity_text VARCHAR(500) NOT NULL,
    entity_type VARCHAR(100),
    begin_offset INTEGER,
    end_offset INTEGER,
    cui VARCHAR(20),
    tui VARCHAR(20),
    confidence FLOAT,
    is_negated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing analysis results
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    execution_plan JSONB,
    results JSONB,
    execution_time FLOAT,
    confidence FLOAT,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing user sessions (for security tracking)
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_identifier VARCHAR(255),
    activity_log JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_documents_type ON clinical_documents(document_type);
CREATE INDEX idx_documents_date ON clinical_documents(created_date);
CREATE INDEX idx_entities_type ON extracted_entities(entity_type);
CREATE INDEX idx_entities_text ON extracted_entities(entity_text);
CREATE INDEX idx_entities_document ON extracted_entities(document_id);
CREATE INDEX idx_results_query ON analysis_results USING gin(to_tsvector('english', query_text));
CREATE INDEX idx_sessions_activity ON user_sessions(last_activity);

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updating timestamps
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON clinical_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing (optional)
-- INSERT INTO clinical_documents (document_id, title, document_type, content, created_date) VALUES
-- ('DOC001', 'Surgical Note - Cardiac Bypass', 'surgical_note', 'Patient underwent arterial graft procedure. No signs of infection post-surgery.', '2024-01-15'),
-- ('DOC002', 'Discharge Summary', 'discharge_summary', 'Patient recovered well from bypass surgery. Arterial graft functioning properly.', '2024-01-16');
