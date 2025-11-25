-- Binko.ai Database Initialization
-- Runs automatically on first docker-compose up
-- Safe to re-run (uses IF NOT EXISTS)

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
    confidence FLOAT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ideas_niche ON ideas(niche);
CREATE INDEX IF NOT EXISTS idx_ideas_difficulty ON ideas(difficulty);
CREATE INDEX IF NOT EXISTS idx_ideas_type ON ideas(idea_type);
CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at DESC);

-- Seed data (only insert if table is empty)
INSERT INTO ideas (title, summary, idea_type, business_model, skills, difficulty, niche, target_audience)
SELECT * FROM (VALUES
    (
        'AI Resume Optimizer',
        'SaaS tool that analyzes resumes against job descriptions and suggests improvements using AI.',
        'saas',
        'subscription',
        ARRAY['python', 'react', 'openai'],
        'intermediate',
        'career',
        'Job seekers, career changers'
    ),
    (
        'Local Business Review Aggregator',
        'Platform that aggregates reviews from Google, Yelp, Facebook for local businesses with sentiment analysis.',
        'saas',
        'subscription',
        ARRAY['python', 'web scraping', 'nlp'],
        'intermediate',
        'local business',
        'Small business owners'
    ),
    (
        'Freelancer Invoice Generator',
        'Simple tool for freelancers to create professional invoices, track payments, and send reminders.',
        'saas',
        'freemium',
        ARRAY['react', 'node', 'stripe'],
        'beginner',
        'freelance',
        'Freelancers, contractors'
    ),
    (
        'YouTube Thumbnail A/B Tester',
        'Tool that lets YouTubers test different thumbnails before publishing. AI predicts click-through rates.',
        'saas',
        'subscription',
        ARRAY['python', 'machine learning', 'youtube api'],
        'advanced',
        'content creation',
        'YouTubers, content creators'
    ),
    (
        'Habit Tracker with Accountability',
        'Mobile app that pairs users with accountability partners. Daily check-ins and streak tracking.',
        'app',
        'freemium',
        ARRAY['react native', 'firebase'],
        'beginner',
        'productivity',
        'People building new habits'
    ),
    (
        'AI-Powered Meal Planner',
        'Generates weekly meal plans based on dietary preferences, budget, and local store sales.',
        'app',
        'subscription',
        ARRAY['python', 'openai', 'react native'],
        'intermediate',
        'health',
        'Busy families, health-conscious individuals'
    ),
    (
        'Micro-SaaS Directory',
        'Curated directory of profitable micro-SaaS businesses with revenue estimates and founder interviews.',
        'content',
        'ads',
        ARRAY['nextjs', 'seo', 'content writing'],
        'beginner',
        'entrepreneurship',
        'Aspiring SaaS founders'
    ),
    (
        'Cold Email Template Library',
        'Database of proven cold email templates with AI customization for each prospect.',
        'saas',
        'one_time',
        ARRAY['react', 'openai', 'copywriting'],
        'beginner',
        'sales',
        'Sales reps, founders doing outreach'
    ),
    (
        'Developer Portfolio Generator',
        'Creates beautiful portfolio sites from GitHub profile. Auto-imports projects and deploys.',
        'saas',
        'freemium',
        ARRAY['nextjs', 'github api', 'vercel'],
        'intermediate',
        'developer tools',
        'Developers looking for jobs'
    ),
    (
        'Niche Newsletter Finder',
        'Search engine for newsletters by topic, audience size, and ad rates for sponsors.',
        'saas',
        'subscription',
        ARRAY['python', 'web scraping', 'react'],
        'intermediate',
        'marketing',
        'Newsletter sponsors, marketers'
    )
) AS seed(title, summary, idea_type, business_model, skills, difficulty, niche, target_audience)
WHERE NOT EXISTS (SELECT 1 FROM ideas LIMIT 1);
