# Binko.ai

Project idea generator. You feed it extracted ideas from YouTube videos. Users input their profile. AI generates personalized project ideas.

## Quick Start

### 1. Start Database
```bash
docker-compose up db -d
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env
cp .env.example .env
# Edit .env with your OpenAI key

# Run
uvicorn app.main:app --reload
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## API Endpoints

### Import Ideas
```bash
POST /api/ideas/bulk
```
```json
[
  {
    "title": "AI Resume Builder",
    "summary": "SaaS that generates tailored resumes",
    "idea_type": "saas",
    "skills": ["python", "react"],
    "difficulty": "intermediate",
    "niche": "career"
  }
]
```

### Generate Ideas
```bash
POST /api/generate
```
```json
{
  "profile": {
    "technical_skills": ["python", "react"],
    "experience_level": "intermediate",
    "preferred_niches": ["fintech"],
    "income_goal": "side_income"
  },
  "num_ideas": 3
}
```

## Project Structure
```
binko.ai/
├── backend/
│   └── app/
│       ├── api/          # Routes
│       ├── models/       # SQLAlchemy models
│       ├── schemas/      # Pydantic schemas
│       └── services/     # Business logic
├── frontend/
│   └── src/
│       ├── components/   # React components
│       ├── services/     # API calls
│       └── types/        # TypeScript types
└── docker-compose.yml
```
