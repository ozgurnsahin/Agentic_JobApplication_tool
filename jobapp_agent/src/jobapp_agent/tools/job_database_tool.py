from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from ..db.database import CrewAIJobStorage
from datetime import datetime
from psycopg2 import DatabaseError

import re


class JobDatabaseToolInput(BaseModel):
    jobs_list: List[Dict[str,Any]] = Field(..., description="List of job objects. Each job should have title, company, link, and description fields.")

class JobDatabaseTool(BaseTool):
    name: str = "job_database_saver"
    description: str = (
        "Saves job opportunities to the PostgreSQL database. Expects a JSON string with a simple array of job objects. "
        "Each job should have: title, company, link, description. Example: '[{\"title\":\"AI Engineer\",\"company\":\"TechCorp\",\"link\":\"https://...\",\"description\":\"...\"}]'. "
        "Handles duplicates automatically and saves all jobs in a single transaction."
    )
    args_schema: Type[BaseModel] = JobDatabaseToolInput

    def _run(self, jobs_list: List[Dict[str,Any]]) -> str :
        try:
            if not jobs_list:
                return "No jobs JSON returned"
    
            prepared_jobs = []
            for job in jobs_list:
                prepared_job = self.prepare_job_data(job)
                if prepared_job:
                    prepared_jobs.append(prepared_job)
            
            if not prepared_jobs:
                return "No valid jobs to save after data preparation"
            
            result = self.save_jobs(prepared_jobs)
            return result
        
        except Exception as e:
            return f"Error runing the tool: {str(e)}"
            
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
                'position': prepared_jobs.get('position', 0),
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
        

    def save_jobs(self, jobs: List[Dict[str, Any]]) -> str:
        try:
            with CrewAIJobStorage() as db:
                if not self.check_schema(db):
                    return "Failed to ensure database schema exists"
                
                insert_query = """
                    INSERT INTO jobs (title, company, link, snippet, position, source, scraped_date)
                    VALUES (%(title)s, %(company)s, %(link)s, %(snippet)s, %(position)s, %(source)s, 
                            TO_DATE(%(scraped_date)s, 'DD/MM/YYYY'))
                    ON CONFLICT (company, title, link) DO NOTHING
                """
                
                db.cursor.executemany(insert_query, jobs)
                
                inserted_count = db.cursor.rowcount
                duplicate_count = len(jobs) - inserted_count
                
                db.conn.commit()
                
                return f"Successfully saved {inserted_count} jobs to database. Skipped {duplicate_count} duplicates."
            
        except DatabaseError as e:
            return f"Failed to save jobs - maximum retries exceeded {e}"
    
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