from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "jobapp_agent" / "src"))

from jobapp_agent.db.config import GenerateConfig
from endpoints import router

# Frontend directory
frontend_dir = project_root / "frontend"

app = FastAPI(
    title="Job Application AI Backend",
    description="Backend API for AI Job Application System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the frontend index.html"""
    return FileResponse(str(frontend_dir / "index.html"))

@app.get("/api")
async def api_root():
    return {
        "message": "Job Application AI Backend API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        db_config = GenerateConfig.config()
        
        return {
            "status": "healthy",
            "database": "connected",
            "ai_agent": "available",
            "database_host": db_config.get("host", "unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)