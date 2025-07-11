from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
import logging

from database import DatabaseManager
from models import (
    JobListResponse, JobResponse,
    AgentStatusResponse, StartAgentResponse
)
from agent_runner import AgentRunner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

db_manager = DatabaseManager()
agent_runner = AgentRunner()

@router.post("/agent/start", response_model=StartAgentResponse)
async def start_agent():
    """Start the CrewAI agent system in background"""
    try:
        result = agent_runner.start_agent()
        return StartAgentResponse(**result)
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """Get current agent execution status"""
    try:
        status = agent_runner.get_status()
        return AgentStatusResponse(**status)
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    company: Optional[str] = Query(None, description="Filter by company name"),
    title: Optional[str] = Query(None, description="Filter by job title"),
    source: Optional[str] = Query(None, description="Filter by job source")
):
    """Get all jobs with optional filtering"""
    try:
        if company or title or source:
            jobs_data = db_manager.get_jobs_filtered(company=company, title=title, source=source)
        else:
            jobs_data = db_manager.get_all_jobs_cvs()
        
        jobs = []
        for job_data in jobs_data:
            job = JobResponse(
                job_id=job_data['job_id'],
                title=job_data['title'],
                company=job_data['company'],
                link=job_data['link'],
                descript=job_data['descript'],
                source=job_data['source'],
                scraped_date=job_data['scraped_date'],
                is_processed=job_data['is_processed'],
                created_at=job_data['created_at']
            )
            jobs.append(job)
        
        return JobListResponse(
            jobs=jobs,
            total=len(jobs),
            message=f"Retrieved {len(jobs)} jobs"
        )
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cvs/{cv_id}/download")
async def download_cv(cv_id: int):
    """Download specific CV file as PDF"""
    try:
        cv_data = db_manager.get_cv_data_by_id(cv_id)
        
        if not cv_data:
            raise HTTPException(status_code=404, detail=f"CV with ID {cv_id} not found")

        return Response(
            content=cv_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_cv_{cv_id}.pdf"
            }
        )
    except ValueError as ve:
        logger.error(f"CV not found: {ve}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f"Failed to download CV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get basic job and CV statistics"""
    try:
        stats = db_manager.get_basic_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))