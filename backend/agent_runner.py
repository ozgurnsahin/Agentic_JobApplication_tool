import sys
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from crewai import Crew, Process


project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "jobapp_agent" / "src"))
from jobapp_agent.crew import JobappAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRunner:
    """Handles background execution of the CrewAI agent system"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.status = "idle"  # idle, running, completed, error
        self.status_lock = Lock()
        self.current_task = None
        self.error_message = None
        self.jobs_found = 0
        self.cvs_created = 0
        
    def get_status(self) -> Dict:
        """Get current agent execution status"""
        with self.status_lock:
            return {
                "status": self.status,
                "message": self._get_status_message(),
                "jobs_found": self.jobs_found,
                "cvs_created": self.cvs_created,
                "error": self.error_message if self.status == "error" else None
            }
    
    def _get_status_message(self) -> str:
        """Get human-readable status message"""
        if self.status == "idle":
            return "Agent is ready to start"
        elif self.status == "running":
            return "Agent is currently processing jobs and creating CVs"
        elif self.status == "completed":
            return f"Agent completed successfully. Found {self.jobs_found} jobs, created {self.cvs_created} CVs"
        elif self.status == "error":
            return f"Agent encountered an error: {self.error_message}"
        return "Unknown status"
    
    def start_agent(self) -> Dict:
        """Start the agent execution in background"""
        with self.status_lock:
            if self.status == "running":
                return {
                    "message": "Agent is already running",
                    "status": "running"
                }
            
            self.jobs_found = 0
            self.cvs_created = 0
            self.error_message = None
            self.status = "running"
        
        self.current_task = self.executor.submit(self._run_agent)
        
        logger.info("Agent execution started in background")
        return {
            "message": "Agent execution started successfully",
            "status": "running"
        }
    
    def start_cv_generation(self) -> Dict:
        """Start CV generation for unprocessed jobs only"""
        with self.status_lock:
            if self.status == "running":
                return {
                    "message": "Agent is already running",
                    "status": "running"
                }
            
            self.jobs_found = 0
            self.cvs_created = 0
            self.error_message = None
            self.status = "running"
        
        self.current_task = self.executor.submit(self._run_cv_generation)
        
        logger.info("CV generation started in background")
        return {
            "message": "CV generation started successfully",
            "status": "running"
        }
    
    def _run_cv_generation(self):
        """Internal method to run only CV generation (optimizer agent)"""
        try:
            logger.info("Starting CV generation for unprocessed jobs")
            
            inputs = {
                'topic': 'AI LLMs',
                'current_year': str(datetime.now().year),
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_month': datetime.now().strftime('%Y-%m')
            }
            
            agent_instance = JobappAgent()
            optimizer_crew = Crew(
                agents=[agent_instance.optimizer()],
                tasks=[agent_instance.optimization_task()],
                process=Process.sequential,
                verbose=True,
            )
            
            result = optimizer_crew.kickoff(inputs=inputs)
            
            with self.status_lock:
                self.status = "completed"
                
            logger.info("CV generation completed successfully")
            
        except Exception as e:
            logger.error(f"CV generation failed: {e}")
            with self.status_lock:
                self.status = "error"
                self.error_message = str(e)

    def _run_agent(self):
        """Internal method to run the agent"""
        try:
            logger.info("Starting CrewAI agent execution")
            
            inputs = {
                'topic': 'AI LLMs',
                'current_year': str(datetime.now().year),
                'current_date': datetime.now().strftime('%Y-%m-%d'),
                'current_month': datetime.now().strftime('%Y-%m')
            }
            
            crew_instance = JobappAgent().crew()
            result = crew_instance.kickoff(inputs=inputs)
            
            with self.status_lock:
                self.status = "completed"
                # TODO: Extract actual counts from result if available
                
            logger.info("Agent execution completed successfully")
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            with self.status_lock:
                self.status = "error"
                self.error_message = str(e)
