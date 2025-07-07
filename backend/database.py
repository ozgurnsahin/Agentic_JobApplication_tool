import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict
import logging

sys.path.append('../jobapp_agent/src')
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
    
    def get_connection(self):
        """Get database connection using existing config"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_all_jobs_cvs(self) -> List[Dict]:
        """Get all jobs with their CV information"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT j.job_id, j.title, j.company, j.link, j.descript, j.source,
                               j.scraped_date, j.is_processed, j.created_at as job_created_at,
                               cv.cv_id, cv.match_score, cv.created_at as cv_created_at
                        FROM jobs j
                        LEFT JOIN optimized_cvs cv ON j.job_id = cv.job_id
                        ORDER BY j.created_at DESC
                    """)
                    jobs = cursor.fetchall()
                    logger.info(f"Retrieved {len(jobs)} jobs with CV info from database")
                    return [dict(job) for job in jobs]
        except Exception as e:
            logger.error(f"Error fetching jobs with CVs: {e}")
            raise
    
    def get_all_cvs(self) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT cv.cv_id, cv.job_id, cv.match_score, cv.created_at,
                               j.title as job_title, j.company
                        FROM optimized_cvs cv
                        JOIN jobs j ON cv.job_id = j.job_id
                        ORDER BY cv.created_at DESC
                    """)
                    cvs = cursor.fetchall()
                    logger.info(f"Retrieved {len(cvs)} CVs from database")
                    return [dict(cv) for cv in cvs]
        except Exception as e:
            logger.error(f"Error fetching CVs: {e}")
            raise
    