import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "jobapp_agent" / "src"))
from jobapp_agent.db.config import GenerateConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager that reuses existing AI agent database configuration"""
    
    def __init__(self):
        try:
            self.db_config = GenerateConfig.config()
            logger.info(f"Database config loaded for host: {self.db_config.get('host')}")
        except Exception as e:
            logger.error(f"Failed to load database config: {e}")
            raise
    
    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return self.conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'conn'):
            self.conn.close()
    
    def get_all_jobs_cvs(self) -> List[Dict]:
        """Get all jobs from the database"""
        try:
            with self as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT j.job_id, j.title, j.company, j.link, j.descript, j.source,
                               cv.match_score, j.scraped_date, j.is_processed, 
                               j.created_at, cv.created_at as cv_created_at
                        FROM jobs j
                        LEFT JOIN optimized_cvs cv ON j.job_id = cv.job_id
                        ORDER BY j.created_at DESC
                    """)
                    jobs = cursor.fetchall()
                    logger.info(f"Retrieved {len(jobs)} jobs from database")
                    return [dict(job) for job in jobs]
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            raise
    
    def get_jobs_filtered(self, company: str = None, title: str = None, source: str = None) -> List[Dict]:
        """Get jobs with optional filtering"""
        try:
            with self as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    where_conditions = []
                    params = []
                    
                    if company:
                        where_conditions.append("j.company ILIKE %s")
                        params.append(f"%{company}%")
                    
                    if title:
                        where_conditions.append("j.title ILIKE %s")
                        params.append(f"%{title}%")
                    
                    if source:
                        where_conditions.append("j.source ILIKE %s")
                        params.append(f"%{source}%")
                    
                    where_clause = ""
                    if where_conditions:
                        where_clause = "WHERE " + " AND ".join(where_conditions)
                    
                    query = f"""
                        SELECT j.job_id, j.title, j.company, j.link, j.descript, j.source,
                               cv.match_score, j.scraped_date, j.is_processed, 
                               j.created_at, cv.created_at as cv_created_at
                        FROM jobs j
                        JOIN optimized_cvs cv ON j.job_id = cv.job_id
                        {where_clause}
                        ORDER BY j.created_at DESC
                    """
                    
                    cursor.execute(query, params)
                    jobs = cursor.fetchall()
                    logger.info(f"Retrieved {len(jobs)} filtered jobs from database")
                    return [dict(job) for job in jobs]
        except Exception as e:
            logger.error(f"Error fetching filtered jobs: {e}")
            raise
    
    def get_cv_data_by_id(self, cv_id: int) -> bytes:
        """Get CV data by CV ID for download"""
        try:
            with self as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT cv_data FROM optimized_cvs WHERE cv_id = %s", (cv_id,))
                    result = cursor.fetchone()
                    if result:
                        return result[0]
                    else:
                        raise ValueError(f"CV with ID {cv_id} not found")
        except Exception as e:
            logger.error(f"Error fetching CV data: {e}")
            raise
    
    def get_all_cvs(self) -> List[Dict]:
        """Get all CVs with their associated job information"""
        try:
            with self as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            cv.cv_id,
                            cv.job_id,
                            cv.match_score,
                            cv.created_at as cv_created_at,
                            j.title as job_title,
                            j.company,
                            j.link as job_link,
                            j.source,
                            j.scraped_date
                        FROM optimized_cvs cv
                        LEFT JOIN jobs j ON cv.job_id = j.job_id
                        ORDER BY cv.created_at DESC
                    """)
                    cvs = cursor.fetchall()
                    logger.info(f"Retrieved {len(cvs)} CVs from database")
                    return [dict(cv) for cv in cvs]
        except Exception as e:
            logger.error(f"Error fetching CVs: {e}")
            raise

    def get_basic_stats(self) -> Dict:
        """Get basic job and CV statistics"""
        try:
            with self as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_jobs,
                            COUNT(CASE WHEN is_processed = true THEN 1 END) as processed_jobs,
                            COUNT(DISTINCT company) as unique_companies,
                            COUNT(DISTINCT source) as unique_sources
                        FROM jobs
                    """)
                    job_stats = cursor.fetchone()
                    
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_cvs,
                            AVG(match_score) as avg_match_score,
                            MAX(match_score) as max_match_score,
                            MIN(match_score) as min_match_score
                        FROM optimized_cvs
                        WHERE match_score IS NOT NULL
                    """)
                    cv_stats = cursor.fetchone()
                    
                    cursor.execute("""
                        SELECT company, COUNT(*) as job_count
                        FROM jobs
                        WHERE company IS NOT NULL
                        GROUP BY company
                        ORDER BY job_count DESC
                        LIMIT 10
                    """)
                    company_stats = cursor.fetchall()
                    
                    return {
                        "jobs": dict(job_stats),
                        "cvs": dict(cv_stats),
                        "top_companies": [dict(company) for company in company_stats]
                    }
        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            raise
    
    