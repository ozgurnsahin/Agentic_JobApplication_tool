from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from ..db.database import CrewAIJobStorage
from datetime import datetime
from psycopg2 import IntegrityError, DatabaseError

import json
import re
import time


class JobDatabaseToolInput(BaseModel):
    jobs_json: str = Field(..., description="Output JSON string containing list of job opportunities to save to database")

class JobDatabaseTool(BaseTool):
    name: str = "job_database_saver"
    description: str = (
        "Saves job opportunities to the PostgreSQL database. Takes a JSON string with job data "
        "and saves all jobs in a single batch transaction. Handles duplicates automatically and "
        "ensures data consistency. Use this tool at the end of job research to store all of the found opportunities."
    )
    args_schema: Type[BaseModel] = JobDatabaseToolInput

    def _run(self, jobs_json: str) -> str:
        try:
            if not jobs_json:
                return "No jobs JSON returned"
            
            jobs_data = json.loads(jobs_json)
            
            prepared_jobs = []
            for job in jobs_data:
                prepared_job = self.prepare_job_data(job)
                if prepared_job:
                    prepared_jobs.append(prepared_job)
            
            if not prepared_jobs:
                return "No valid jobs to save after data preparation"
            
            result = self.save_jobs(prepared_jobs)
            return result
        
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON format - {str(e)}"
            
    def prepare_job_data(self, prepared_jobs : Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not all(key in prepared_jobs for key in ['title', 'company', 'link']):
                return None
            
        #company = self.clean_company_name(prepared_jobs['company'])
            
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
    
    """ def clean_company_name(self, company_name : str) -> str:
        if not company_name:
            return ""
        
        company = company_name.strip()
        company = re.sub(r'\s+', ' ', company)
        
        company = re.sub(r'\b(Inc\.?|Ltd\.?|LLC|Corp\.?|Corporation)\b', '', company, flags=re.IGNORECASE)
        company = company.strip()
        
        return company """
        
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
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                with CrewAIJobStorage() as db:
                    saved_count = 0
                    duplicate_count = 0
                    
                    for job in jobs:
                        try:
                            insert_query = """
                                INSERT INTO jobs (title, company, link, snippet, position, source, scraped_date)
                                VALUES (%(title)s, %(company)s, %(link)s, %(snippet)s, %(position)s, %(source)s, 
                                TO_DATE(%(scraped_date)s, 'DD/MM/YYYY'))"""
                            
                            db.cursor.execute(insert_query, job)
                            saved_count += 1
                            
                        except IntegrityError:
                            duplicate_count += 1
                            db.conn.rollback()
                            continue
                    
                    db.conn.commit()
                    
                    return f"Successfully saved {saved_count} jobs to database. Skipped {duplicate_count} duplicates."
                    
            except DatabaseError as e:
                if attempt < max_retries - 1:
                    print(f"Database error on attempt {attempt + 1}, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    return f"Failed to save jobs after {max_retries} attempts. Last error: {str(e)}"
            
            except Exception as e:
                return f"Unexpected error during database save: {str(e)}"
            
        return "Failed to save jobs - maximum retries exceeded"