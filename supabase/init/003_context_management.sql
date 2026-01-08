-- SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
--
-- SPDX-License-Identifier: Apache-2.0

-- Create tables for Smart Contextual Onboarding and Context Management

-- Context objects table: stores all inferred and confirmed business context
CREATE TABLE IF NOT EXISTS context_objects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Type of context (company, industry, regulation, competitor, persona, assumption)
  type VARCHAR(50) NOT NULL,
  
  -- JSON content of the context object
  content JSONB NOT NULL,
  
  -- Source of the context (external | inferred | user)
  source VARCHAR(20) NOT NULL DEFAULT 'inferred',
  
  -- Confidence score (0.0 to 1.0)
  confidence DECIMAL(3,2) DEFAULT 0.5,
  
  -- Status (pending | confirmed | rejected)
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  
  -- Evidence references (URLs, document IDs, etc.)
  evidence_refs JSONB DEFAULT '[]',
  
  -- Version tracking
  version INTEGER DEFAULT 1,
  
  -- Soft delete flag
  deleted_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Context evidence table: stores detailed evidence for context objects
CREATE TABLE IF NOT EXISTS context_evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Foreign key to context_objects
  context_id UUID NOT NULL REFERENCES context_objects(id) ON DELETE CASCADE,
  
  -- Type of evidence (url | document | api | inference)
  evidence_type VARCHAR(50) NOT NULL,
  
  -- Evidence content/reference
  content JSONB NOT NULL,
  
  -- When the evidence was collected
  collected_at TIMESTAMP DEFAULT now(),
  
  created_at TIMESTAMP DEFAULT now()
);

-- Context links table: graph relationships between context objects
CREATE TABLE IF NOT EXISTS context_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Source and target context objects
  from_context_id UUID NOT NULL REFERENCES context_objects(id) ON DELETE CASCADE,
  to_context_id UUID NOT NULL REFERENCES context_objects(id) ON DELETE CASCADE,
  
  -- Relationship type (applies_to | competes_with | regulates | targets)
  relationship_type VARCHAR(50) NOT NULL,
  
  -- Optional metadata about the relationship
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT now(),
  
  -- Prevent duplicate relationships
  UNIQUE(from_context_id, to_context_id, relationship_type)
);

-- Onboarding sessions table: tracks user onboarding progress
CREATE TABLE IF NOT EXISTS onboarding_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- User/organization identifier (could be email, org_id, etc.)
  user_id VARCHAR(255) NOT NULL,
  
  -- Company information collected during onboarding
  company_name VARCHAR(255),
  company_website VARCHAR(500),
  industry VARCHAR(100),
  
  -- Current onboarding step
  current_step VARCHAR(50) DEFAULT 'company_info',
  
  -- Overall status (in_progress | completed | abandoned)
  status VARCHAR(20) DEFAULT 'in_progress',
  
  -- Metadata about the session
  metadata JSONB DEFAULT '{}',
  
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Create indexes for efficient queries

-- Index on context type and status for filtering
CREATE INDEX IF NOT EXISTS idx_context_objects_type_status
  ON context_objects(type, status) WHERE deleted_at IS NULL;

-- Index on source for filtering by origin
CREATE INDEX IF NOT EXISTS idx_context_objects_source
  ON context_objects(source) WHERE deleted_at IS NULL;

-- Index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_context_objects_created
  ON context_objects(created_at DESC) WHERE deleted_at IS NULL;

-- Index for evidence lookups
CREATE INDEX IF NOT EXISTS idx_context_evidence_context_id
  ON context_evidence(context_id);

-- Index for link traversal
CREATE INDEX IF NOT EXISTS idx_context_links_from
  ON context_links(from_context_id);

CREATE INDEX IF NOT EXISTS idx_context_links_to
  ON context_links(to_context_id);

-- Index for onboarding session lookups
CREATE INDEX IF NOT EXISTS idx_onboarding_sessions_user
  ON onboarding_sessions(user_id, status);

-- GIN index for content search
CREATE INDEX IF NOT EXISTS idx_context_objects_content
  ON context_objects USING GIN (content);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to context_objects
CREATE TRIGGER update_context_objects_updated_at BEFORE UPDATE ON context_objects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to onboarding_sessions
CREATE TRIGGER update_onboarding_sessions_updated_at BEFORE UPDATE ON onboarding_sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
