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
    
    def __enter__(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def get_all_jobs_cvs(self) -> List[Dict]:
        """Get all jobs from the database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT job_id, title, company, link, descript, source, cv.match_score,
                               j.title as job_title, j.company
                               scraped_date, is_processed, created_at, cv.created_at,
                        FROM jobs j
                        JOIN optimized_cvs cv ON j.job_id = cv.job_id
                        ORDER BY created_at DESC
                    """)
                    jobs = cursor.fetchall()
                    logger.info(f"Retrieved {len(jobs)} jobs from database")
                    return [dict(job) for job in jobs]
        except Exception as e:
            logger.error(f"Error fetching jobs: {e}")
            raise
    
    