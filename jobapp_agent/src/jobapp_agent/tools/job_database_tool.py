from crewai.tools import BaseTool
from typing import Type, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..db.database import CrewAIJobStorage
from datetime import datetime
from psycopg2 import DatabaseError

import re


class JobDatabaseToolInput(BaseModel):
    action: str = Field(..., description="Action: 'save_jobs', 'get_unprocessed_jobs', 'save_cv_and_mark_processed'")
    jobs_list: Optional[List[Dict[str,Any]]] = Field(default=None, description="Job objects for saving")
    job_id: Optional[int] = Field(default=None, description="Job ID for CV operations")
    cv_data: Optional[bytes] = Field(default=None, description="PDF CV data as bytes")
    match_score: Optional[int] = Field(default=None, description="Match score 0-100")

class JobDatabaseTool(BaseTool):
    name: str = "job_database_tool"
    description: str = (
        "Complete database management tool for job and CV operations. Handles:\n\n"
        "1. 'save_jobs': Save job listings to database\n"
        "   - Requires: jobs_list with job objects\n\n"
        "2. 'get_unprocessed_jobs': Get jobs where is_processed = FALSE\n"
        "   - Returns: Job details for CV optimization\n\n"
        "3. 'save_cv_and_mark_processed': Save optimized CV and mark job as processed\n"
        "   - Requires: job_id, cv_data (bytes), match_score\n"
        "   - Saves CV to optimized_cvs table AND marks job as processed\n\n"
        "All operations handle schema creation and use transactions for data integrity."
    )
    args_schema: Type[BaseModel] = JobDatabaseToolInput

    def _run(self, action: str, jobs_list: Optional[List[Dict[str,Any]]] = None, job_id: Optional[int] = None, cv_data: Optional[bytes] = None, match_score: Optional[int] = None) -> str:
        try:
            if action in ["save_jobs","save jobs","save Jobs","Save jobs"]:
                return self.save_jobs(jobs_list)
            elif action == "get_unprocessed_jobs":
                return self.query_unprocessed_jobs()
            elif action == "save_cv_and_mark_processed":
                return self._save_cv_and_mark_processed(job_id, cv_data, match_score)
            else:
                return f"Invalid action: {action}. Use 'save_jobs', 'get_unprocessed_jobs', or 'save_cv_and_mark_processed'"
        
        except Exception as e:
            return f"Error in job_database_tool: {str(e)}"
            
    def prepare_job_data(self, prepared_jobs : Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not all(key in prepared_jobs for key in ['title', 'company', 'link', 'description']):
                return None
            
            posting_date = self.extract_posting_date(prepared_jobs.get('description', ''))
            
            prepared_job = {
                'title': prepared_jobs['title'],  
                'company': prepared_jobs['company'],    
                'link': prepared_jobs['link'],   
                'snippet': prepared_jobs.get('description', ''),  
                'source': 'crewai_agent',
                'scraped_date': posting_date
            }
            return prepared_job
            
        except Exception as e:
            print(f"Error preparing job data: {e}")
            return None
        
    def extract_posting_date(self, description: str) -> str:
        if not description:
            return datetime.now().strftime('%d/%m/%Y')
        
        date_patterns = [
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, description)
            if match:
                if pattern.startswith(r'(\d{1,2})'):
                    day, month, year = match.groups()
                else:
                    year, month, day = match.groups()
                
                try:
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
        
        return datetime.now().strftime('%d/%m/%Y')
        

    def save_jobs(self, jobs_list: Optional[List[Dict[str, Any]]]) -> str:
        try:
            if not jobs_list:
                return "No jobs to save"
    
            prepared_jobs = []
            for job in jobs_list:
                prepared_job = self.prepare_job_data(job)
                if prepared_job:
                    prepared_jobs.append(prepared_job)
                    
            with CrewAIJobStorage() as db:
                if not self.check_schema(db):
                    return "Failed to ensure database schema exists"
                
                insert_query = """
                    INSERT INTO jobs (title, company, link, descript, source, scraped_date)
                    VALUES (%(title)s, %(company)s, %(link)s, %(snippet)s, %(source)s, 
                            TO_DATE(%(scraped_date)s, 'DD/MM/YYYY'))
                    ON CONFLICT (company, title, link) DO NOTHING
                """
                
                db.cursor.executemany(insert_query, prepared_jobs)
                
                inserted_count = db.cursor.rowcount
                duplicate_count = len(prepared_jobs) - inserted_count
                
                db.conn.commit()
                
                return f"Successfully saved {inserted_count} jobs to database. Skipped {duplicate_count} duplicates."
            
        except DatabaseError as e:
            return f"Failed to save jobs - maximum retries exceeded {e}"
    
    def query_unprocessed_jobs(self):
        try:
            with CrewAIJobStorage() as db:
                if not self.check_schema(db):
                    return "Failed to ensure database schema exists"
            
                query = """
                    SELECT job_id, title, company, descript, link, scraped_date
                    FROM jobs 
                    WHERE is_processed = FALSE 
                    ORDER BY scraped_date DESC 
                """
                
                db.cursor.execute(query)
                jobs = db.cursor.fetchall()
                
                if not jobs:
                    return "No unprocessed jobs found in database"
                
                job_list = []
                for job in jobs:
                    job_dict = {
                        "job_id": job[0],
                        "title": job[1], 
                        "description": job[3],
                    }
                    job_list.append(job_dict)
                    
                return f"Found {len(jobs)} unprocessed jobs:\n\n" + "\n".join(job_list)   
        except DatabaseError as e:
            print(f"Error querying table: {e}")
    
    def _save_cv_and_mark_processed(self, job_id: int, cv_data: bytes, match_score: int) -> str:
        return self.save_optimized_cv(job_id, cv_data, match_score)
    
    def save_optimized_cv(self, job_id: int, cv_data: bytes, match_score: int) -> str:
        if not job_id or not cv_data or match_score is None:
            return "Missing required parameters: job_id, cv_data, and match_score are all required"

        try:
            with CrewAIJobStorage() as db:
                if not self.check_schema(db):
                    return "Failed to ensure database schema exists"
                
                try:
                    cv_insert_query = """
                        INSERT INTO optimized_cvs (job_id, cv_data, match_score)
                        VALUES (%s, %s, %s)
                        RETURNING cv_id
                    """
                    
                    db.cursor.execute(cv_insert_query, (job_id, cv_data, match_score))
                    cv_id = db.cursor.fetchone()[0]
                    
                    job_update_query = """
                        UPDATE jobs 
                        SET is_processed = TRUE 
                        WHERE job_id = %s
                    """
                    
                    db.cursor.execute(job_update_query, (job_id,))
                    
                    if db.cursor.rowcount == 0:
                        db.conn.rollback()
                        return f"Job ID {job_id} not found in database"
                
                    db.conn.commit()
                    
                    return f"SUCCESS: CV saved (ID: {cv_id}) and job {job_id} marked as processed. Match score: {match_score}"
                    
                except DatabaseError as e:
                    db.conn.rollback()
                    return f"Transaction failed: {str(e)}"
                    
        except Exception as e:
            return f"Error saving CV and marking job processed: {str(e)}"
        
    def check_schema(self, db) -> bool:
        try:
            check_query = """
                SELECT 
                    (SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'jobs'
                    )) as jobs_exists,
                    (SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'optimized_cvs'
                    )) as cvs_exists;
            """
            db.cursor.execute(check_query)
            result = db.cursor.fetchone()
            jobs_exists, cvs_exists = result
            
            if not jobs_exists or not cvs_exists:
                print(f"Tables status - jobs: {jobs_exists}, optimized_cvs: {cvs_exists}")
                db.create_schema()
                print("Missing tables created successfully")
                
            return True
        except DatabaseError as e:
            print(f"Error checking/creating schema: {e}")
            return False