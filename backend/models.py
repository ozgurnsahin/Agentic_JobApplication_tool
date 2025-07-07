from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class JobResponse(BaseModel):
    """Model for job data returned by the API"""
    job_id: int
    title: str
    company: Optional[str] = None
    link: str
    descript: Optional[str] = None
    source: Optional[str] = None
    scraped_date: Optional[datetime] = None
    is_processed: bool = False
    created_at: Optional[datetime] = None

class CVResponse(BaseModel):
    """Model for CV data returned by the API"""
    cv_id: int
    job_id: int
    match_score: Optional[int] = None
    created_at: Optional[datetime] = None
    job_title: Optional[str] = None
    company: Optional[str] = None

class JobListResponse(BaseModel):
    """Model for job list endpoint response"""
    jobs: List[JobResponse]
    total: int
    message: str = "Jobs retrieved successfully"

class CVListResponse(BaseModel):
    """Model for CV list endpoint response"""
    cvs: List[CVResponse]
    total: int
    message: str = "CVs retrieved successfully"

class AgentStatusResponse(BaseModel):
    """Model for agent status response"""
    status: str  # "idle", "running", "completed", "error"
    message: str
    jobs_found: int = 0
    cvs_created: int = 0

class StartAgentResponse(BaseModel):
    """Model for start agent endpoint response"""
    message: str
    status: str
    task_id: Optional[str] = None

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    detail: Optional[str] = None
    status_code: int