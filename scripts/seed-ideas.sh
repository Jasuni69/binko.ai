#!/bin/bash
# Seed database with sample ideas for testing
# Run after setup-db.sh

set -e

echo "=== Seeding Sample Ideas ==="

# Load env
if [ -f .env.prod ]; then
    export $(cat .env.prod | grep -v '#' | xargs)
fi

DB_USER=${POSTGRES_USER:-binko}
DB_PASS=${POSTGRES_PASSWORD:-changeme}
DB_NAME=${POSTGRES_DB:-binko}

PGPASSWORD=$DB_PASS psql -h localhost -U $DB_USER -d $DB_NAME <<'EOSQL'
-- Sample ideas for testing
INSERT INTO ideas (title, summary, idea_type, business_model, skills, difficulty, niche, target_audience)
VALUES
(
    'AI Resume Optimizer',
    'SaaS tool that analyzes resumes against job descriptions and suggests improvements using AI. Helps job seekers tailor their resume for each application.',
    'saas',
    'subscription',
    ARRAY['python', 'react', 'openai'],
    'intermediate',
    'career',
    'Job seekers, career changers'
),
(
    'Local Business Review Aggregator',
    'Platform that aggregates reviews from Google, Yelp, Facebook for local businesses. Provides sentiment analysis and response suggestions.',
    'saas',
    'subscription',
    ARRAY['python', 'web scraping', 'nlp'],
    'intermediate',
    'local business',
    'Small business owners'
),
(
    'Freelancer Invoice Generator',
    'Simple tool for freelancers to create professional invoices, track payments, and send reminders. Integrates with Stripe.',
    'saas',
    'freemium',
    ARRAY['react', 'node', 'stripe'],
    'beginner',
    'freelance',
    'Freelancers, contractors'
),
(
    'YouTube Thumbnail A/B Tester',
    'Tool that lets YouTubers test different thumbnails and titles before publishing. Uses AI to predict click-through rates.',
    'saas',
    'subscription',
    ARRAY['python', 'machine learning', 'youtube api'],
    'advanced',
    'content creation',
    'YouTubers, content creators'
),
(
    'Habit Tracker with Accountability',
    'Mobile app that pairs users with accountability partners. Daily check-ins, streak tracking, and social pressure to maintain habits.',
    'app',
    'freemium',
    ARRAY['react native', 'firebase'],
    'beginner',
    'productivity',
    'People building new habits'
),
(
    'AI-Powered Meal Planner',
    'Generates weekly meal plans based on dietary preferences, budget, and whats on sale at local stores. Creates shopping lists.',
    'app',
    'subscription',
    ARRAY['python', 'openai', 'react native'],
    'intermediate',
    'health',
    'Busy families, health-conscious individuals'
),
(
    'Micro-SaaS Directory',
    'Curated directory of profitable micro-SaaS businesses with revenue estimates, tech stacks, and founder interviews. Monetize via listings.',
    'content',
    'ads',
    ARRAY['nextjs', 'seo', 'content writing'],
    'beginner',
    'entrepreneurship',
    'Aspiring SaaS founders'
),
(
    'Cold Email Template Library',
    'Database of proven cold email templates for different industries and use cases. AI customization for each prospect.',
    'saas',
    'one_time',
    ARRAY['react', 'openai', 'copywriting'],
    'beginner',
    'sales',
    'Sales reps, founders doing outreach'
),
(
    'Developer Portfolio Generator',
    'Tool that creates beautiful portfolio sites from GitHub profile. Auto-imports projects, generates descriptions, deploys to custom domain.',
    'saas',
    'freemium',
    ARRAY['nextjs', 'github api', 'vercel'],
    'intermediate',
    'developer tools',
    'Developers looking for jobs'
),
(
    'Niche Newsletter Finder',
    'Search engine for newsletters by topic, audience size, and ad rates. Helps marketers find sponsorship opportunities.',
    'saas',
    'subscription',
    ARRAY['python', 'web scraping', 'react'],
    'intermediate',
    'marketing',
    'Newsletter sponsors, marketers'
)
ON CONFLICT DO NOTHING;

SELECT COUNT(*) as total_ideas FROM ideas;
EOSQL

echo "=== Seeding Complete ==="
