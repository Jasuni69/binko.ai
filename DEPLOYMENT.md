# Binko.ai Deployment Guide

Quick guide for deploy Binko.ai to production.

## Backend Options

### Option 1: Railway

1. Create Railway account
2. Click "New Project" -> "Deploy from GitHub repo"
3. Select binko.ai repo
4. Railway auto-detect `railway.json`
5. Add env vars in Railway dashboard:
   - `DATABASE_URL` (Railway provide Postgres addon)
   - `OPENAI_API_KEY`
   - `ALLOWED_ORIGINS` (your Vercel URL)
6. Deploy

**Database**: Add Postgres plugin in Railway dashboard. Railway auto-set DATABASE_URL.

### Option 2: Render

1. Create Render account
2. Click "New" -> "Blueprint"
3. Connect GitHub repo
4. Render use `render.yaml` for config
5. Add env vars in Render dashboard:
   - `DATABASE_URL` (Render provide Postgres service)
   - `OPENAI_API_KEY`
   - `ALLOWED_ORIGINS`
6. Deploy

**Database**: Render create Postgres from `render.yaml`. Auto-connect.

## Frontend: Vercel

1. Create Vercel account
2. Click "New Project" -> Import from GitHub
3. Select binko.ai repo
4. Set root directory: `frontend`
5. Vercel auto-detect Vite config
6. Add env var:
   - `VITE_API_URL` = your backend URL (Railway/Render)
7. Update `vercel.json`:
   ```json
   "rewrites": [
     {
       "source": "/api/:path*",
       "destination": "https://your-actual-backend.railway.app/api/:path*"
     }
   ]
   ```
8. Deploy

## Docker Local Production Test

Test production build local:

```bash
# Build production image
docker build --target production -t binko-backend:prod backend/

# Run
docker run -p 8000:8000 \
  -e DATABASE_URL=your_db_url \
  -e OPENAI_API_KEY=your_key \
  binko-backend:prod
```

## Environment Variables

Backend need these vars:

- `DATABASE_URL` - Postgres connection string
- `OPENAI_API_KEY` - OpenAI API key
- `PORT` - Server port (default 8000, Railway/Render set this)
- `ALLOWED_ORIGINS` - CORS origins, comma-separated
- `ENVIRONMENT` - "production" or "development"

Frontend need:

- `VITE_API_URL` - Backend API URL

## CI/CD

GitHub Actions run on PR:
- Backend lint (ruff)
- Backend tests (pytest)
- Frontend type check (tsc)
- Frontend build

All must pass before merge.

## Post-Deploy

1. Check backend health: `https://your-backend.app/health`
2. Check frontend load
3. Test API calls from frontend
4. Monitor logs in platform dashboard
5. Set up domain (optional)

## Rollback

Railway/Render keep previous deploys. Click "Rollback" in dashboard if problem.

## Monitoring

- Railway: Built-in metrics and logs
- Render: Built-in metrics and logs
- Vercel: Analytics and logs

## Cost

- Railway: $5/month starter
- Render: Free tier available (sleeps after inactivity)
- Vercel: Free for hobby projects

## Troubleshooting

**Backend not start**: Check DATABASE_URL and OPENAI_API_KEY set.

**Frontend can't reach API**: Update CORS in backend. Check VITE_API_URL correct.

**Database connection fail**: Check DATABASE_URL format. Test connection string.

**Build fail**: Check requirements.txt and package.json versions match local.
