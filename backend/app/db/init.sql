-- Create ideas table
CREATE TABLE IF NOT EXISTS ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Core
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    description TEXT,

    -- Classification
    idea_type VARCHAR(50),
    business_model VARCHAR(50),
    monetization TEXT,

    -- Requirements
    skills TEXT[],
    tech_stack TEXT[],
    difficulty VARCHAR(20),
    time_to_mvp VARCHAR(50),
    startup_cost VARCHAR(50),

    -- Market
    target_audience TEXT,
    niche VARCHAR(100),
    competition VARCHAR(20),

    -- Details
    key_features TEXT[],
    success_factors TEXT[],
    challenges TEXT[],

    -- Source
    source_video_id VARCHAR(50),
    source_channel VARCHAR(255),
    confidence FLOAT
);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_ideas_niche ON ideas(niche);
CREATE INDEX IF NOT EXISTS idx_ideas_difficulty ON ideas(difficulty);
CREATE INDEX IF NOT EXISTS idx_ideas_type ON ideas(idea_type);
