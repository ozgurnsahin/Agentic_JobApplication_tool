-- Jobs table (updated with your new schema)
CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(200),
    link VARCHAR(1000) NOT NULL,
    descript TEXT,
    source VARCHAR(50) DEFAULT 'crewai_agent',
    scraped_date TIMESTAMP DEFAULT NOW(),
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company, title, link)
);

-- Optimized CVs table (new)
CREATE TABLE IF NOT EXISTS optimized_cvs (
    cv_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(job_id),
    cv_data BYTEA NOT NULL,
    match_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for jobs table        
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_date ON jobs(scraped_date);
CREATE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link);
CREATE INDEX IF NOT EXISTS idx_jobs_processed ON jobs(is_processed);

-- Indexes for optimized_cvs table
CREATE INDEX IF NOT EXISTS idx_optimized_cvs_job_id ON optimized_cvs(job_id);
CREATE INDEX IF NOT EXISTS idx_optimized_cvs_match_score ON optimized_cvs(match_score);