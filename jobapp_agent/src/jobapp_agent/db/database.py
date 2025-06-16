import psycopg2
from psycopg2 import DatabaseError
from .config import GenerateConfig
from pathlib import Path



class CrewAIJobStorage:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CrewAIJobStorage, cls).__new__(cls)
            cls._instance.db_config = GenerateConfig.config()
        return cls._instance
    
    def __init__(self):
        self.connection_url = f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
    
    def __enter__(self):
        self.conn = psycopg2.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()
        
    def create_schema(self):
        sql_path = Path(__file__).resolve().parent / "sql" / "table_initialize.sql"
        with sql_path.open("r") as file:
            query = file.read()
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except DatabaseError as e:
            self.conn.rollback()
            raise e
        