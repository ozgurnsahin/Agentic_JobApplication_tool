CREATE TABLE IF NOT EXISTS jobs (
id SERIAL PRIMARY KEY,
title VARCHAR(500) NOT NULL,
company VARCHAR(200),
link VARCHAR(1000) NOT NULL,
snippet TEXT,
position INTEGER,
source VARCHAR(50) DEFAULT 'crewai_agent',
scraped_date TIMESTAMP DEFAULT NOW(),
is_processed BOOLEAN DEFAULT FALSE,
created_at TIMESTAMP DEFAULT NOW(),

UNIQUE(company, title, link)
);
        
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date);
CREATE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link);