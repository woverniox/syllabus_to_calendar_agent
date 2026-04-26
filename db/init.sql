-- Lead Qualification Agent Database Schema
-- Run this on first startup to initialize tables

-- Traces table - stores agent execution logs
CREATE TABLE IF NOT EXISTS traces (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(64) UNIQUE NOT NULL,
    lead_key VARCHAR(128) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Input/Output data (JSON)
    input_data JSONB NOT NULL,
    score_result JSONB,

    -- Execution details
    actions_taken TEXT[] DEFAULT '{}',
    approval_required BOOLEAN DEFAULT FALSE,
    approval_reason TEXT,
    error TEXT,

    -- Cost tracking (Week 10)
    token_usage JSONB,

    -- Indexes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_traces_lead_key ON traces(lead_key);
CREATE INDEX IF NOT EXISTS idx_traces_created_at ON traces(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_traces_trace_id ON traces(trace_id);

-- Leads table - persistent lead storage
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    lead_key VARCHAR(128) UNIQUE NOT NULL,

    -- Contact info
    email VARCHAR(254) NOT NULL,
    company VARCHAR(200) NOT NULL,
    title VARCHAR(100),

    -- Qualification data
    need TEXT,
    timeline VARCHAR(200),
    budget VARCHAR(100),
    company_size INTEGER,
    industry VARCHAR(100),

    -- Scoring
    score INTEGER,
    tier VARCHAR(20),
    segment VARCHAR(20),
    confidence VARCHAR(20),
    reasoning TEXT,

    -- Status
    status VARCHAR(20) DEFAULT 'new',
    notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company);
CREATE INDEX IF NOT EXISTS idx_leads_tier ON leads(tier);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- Approvals table - pending approval requests
CREATE TABLE IF NOT EXISTS approvals (
    id SERIAL PRIMARY KEY,
    action_id VARCHAR(64) UNIQUE NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    lead_key VARCHAR(128) NOT NULL,

    -- Request details
    reason TEXT NOT NULL,
    context JSONB,

    -- Decision
    status VARCHAR(20) DEFAULT 'pending',
    decided_by VARCHAR(100),
    decided_at TIMESTAMP WITH TIME ZONE,
    decision_notes TEXT,

    -- Timestamps
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
CREATE INDEX IF NOT EXISTS idx_approvals_lead_key ON approvals(lead_key);

-- Company history table - for memory lookups
-- Note: Primary storage is Redis, this is for persistence/backup
CREATE TABLE IF NOT EXISTS company_history (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(253) UNIQUE NOT NULL,

    -- History data
    last_contact_date TIMESTAMP WITH TIME ZONE,
    last_outcome VARCHAR(50),
    notes_summary TEXT,
    total_leads_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_company_history_domain ON company_history(domain);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_company_history_updated_at ON company_history;
CREATE TRIGGER update_company_history_updated_at
    BEFORE UPDATE ON company_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
