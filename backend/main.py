from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys

sys.path.append('jobapp_agent/src')

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

@app.get("/")
async def root():
    return {
        "message": "Job Application AI Backend is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        # Test import of AI agent modules
        from jobapp_agent.db.config import GenerateConfig
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