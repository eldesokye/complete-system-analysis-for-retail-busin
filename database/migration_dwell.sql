
-- Add object_counts column
ALTER TABLE section_analytics ADD COLUMN IF NOT EXISTS object_counts JSONB;

-- Create customer_dwell_time table
CREATE TABLE IF NOT EXISTS customer_dwell_time (
    id SERIAL PRIMARY KEY,
    track_id INTEGER NOT NULL,
    section_name VARCHAR(100) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    duration_seconds FLOAT,
    date DATE NOT NULL,
    hour INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dwell_date_hour ON customer_dwell_time(date, hour);
CREATE INDEX IF NOT EXISTS idx_dwell_section ON customer_dwell_time(section_name);
