#!/bin/bash
# PostgreSQL setup script for t3.micro
# Run this BEFORE docker-compose if using native postgres
# Or skip this if using docker postgres (docker handles it)

set -e

echo "=== Binko.ai Database Setup ==="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Load env
if [ -f .env.prod ]; then
    export $(cat .env.prod | grep -v '#' | xargs)
fi

DB_USER=${POSTGRES_USER:-binko}
DB_PASS=${POSTGRES_PASSWORD:-changeme}
DB_NAME=${POSTGRES_DB:-binko}

echo "Database: $DB_NAME"
echo "User: $DB_USER"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    SUDO="sudo"
else
    SUDO=""
fi

# Install PostgreSQL if not present
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    $SUDO apt update
    $SUDO apt install -y postgresql postgresql-contrib
    $SUDO systemctl start postgresql
    $SUDO systemctl enable postgresql
fi

echo "PostgreSQL version:"
psql --version

# Create user and database
echo "Setting up database..."

$SUDO -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "Creating tables..."

# Run init.sql
PGPASSWORD=$DB_PASS psql -h localhost -U $DB_USER -d $DB_NAME <<'EOSQL'
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

-- Verify
SELECT 'Tables created successfully' as status;
SELECT COUNT(*) as idea_count FROM ideas;
EOSQL

echo ""
echo -e "${GREEN}=== Database Ready ===${NC}"
echo "Connection string:"
echo "postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME"
