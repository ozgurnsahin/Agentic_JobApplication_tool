from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os

from agno.agent import Agent
from agno.tools.webtools import WebTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from dotenv import load_dotenv
load_dotenv()

class JobDetails(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location (city, remote, hybrid)")
    salary: Optional[str] = Field(None, description="Salary information if available")
    description: str = Field(..., description="Job description summary")
    requirements: List[str] = Field(default_factory=list, description="Key job requirements")
    technologies: List[str] = Field(default_factory=list, description="Technologies and tools mentioned")
    experience_level: Optional[str] = Field(None, description="Required experience level")
    work_type: Optional[str] = Field(None, description="remote/hybrid/onsite")
    url: str = Field(..., description="Job posting URL")
    date_found: str = Field(default_factory=lambda: datetime.now().isoformat(), description="When we found this job")

class JobSearchResult(BaseModel):
    search_keyword: str = Field(..., description="Keyword used for search")
    total_jobs_found: int = Field(..., description="Total number of jobs found")
    jobs: List[JobDetails] = Field(..., description="List of job postings")

class Agent_Class:
    def __init__(self):
        self.db_file = "job_search.db"
        self.response_structure = JobSearchResult
        self.model = OpenAIChat(id="gpt-4o-mini")
        self.db_url = os.getenv("DATABASE_URL")
        self.storage = PostgresStorage(
            table_name="job_search_agents",
            schema="ai",
            db_url=self.db_url,
            schema_version=1,
            auto_upgrade_schema=True
        )
        self.agent = Agent(
            name="Job Discovery Agent",
            role="AI/ML Job Discovery Specialist",
            model=self.model,
            storage=self.storage,
            tools=[WebTools(), GoogleSearchTools()], show_tool_calls=True,
            description= """ 
            You are an AI/ML Job Discovery Agent specialized in finding relevant job opportunities.
                Your primary focus is on:
                - AI/ML engineering positions
                - Data engineering roles  
                - Data science positions
                - Machine learning engineer jobs
                
            You search for positions matching Özgür's background in:
                - Python, JavaScript, Go, SQL
                - AI/ML technologies (OpenAI API, LangChain, spaCy, scikit-learn, TensorFlow)
                - Data analysis and backend development
                - RAG systems and document processing 
                
            You MUST return structured data in the exact format specified.
            """,
            instructions=[
                "Search for AI/ML and data engineering jobs only on linkedin and glassdoor do not search other websites",
                "Filter for companies with 11+ employees",
                "Extract job title, company, location, description, requirements, and URL",
                "Focus on roles matching the candidate's technical background",
                "Prioritize remote, hybrid, and Istanbul-based positions",
                "Store all findings with search date and source information",
                "Job posting must be int the last 24 hours only newly posted jobs must be returned"],
            response_model=self.response_structure,
            markdown=True,)

    def create_agent(self):
        return self.agent

