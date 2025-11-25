from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import ideas, generate

app = FastAPI(title="Binko.ai", description="Project Idea Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])


@app.get("/")
def root():
    return {"status": "ok", "service": "binko.ai"}
