-- Retail Analytics System Database Schema
-- PostgreSQL Database: supabase

-- Drop existing tables if they exist
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS traffic_predictions CASCADE;
DROP TABLE IF EXISTS cashier_analytics CASCADE;
DROP TABLE IF EXISTS section_analytics CASCADE;
DROP TABLE IF EXISTS visitors CASCADE;

-- Visitors table (entrance camera data)
CREATE TABLE visitors (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    visitor_count INTEGER NOT NULL,
    date DATE NOT NULL,
    hour INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Section Analytics table (per-section data)
CREATE TABLE section_analytics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    section_name VARCHAR(100) NOT NULL,
    visitor_count INTEGER NOT NULL,
    male_count INTEGER DEFAULT 0,
    female_count INTEGER DEFAULT 0,
    female_count INTEGER DEFAULT 0,
    object_counts JSONB, -- Stores {"cell phone": 2, "chair": 5}
    heatmap_data JSONB,
    date DATE NOT NULL,
    hour INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Customer Dwell Time table (Detailed tracking)
CREATE TABLE customer_dwell_time (
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

-- Cashier Analytics table
CREATE TABLE cashier_analytics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    queue_length INTEGER NOT NULL,
    estimated_wait_time FLOAT,
    is_busy BOOLEAN DEFAULT FALSE,
    estimated_transactions INTEGER DEFAULT 0,
    date DATE NOT NULL,
    hour INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for dwell time
CREATE INDEX idx_dwell_date_hour ON customer_dwell_time(date, hour);
CREATE INDEX idx_dwell_section ON customer_dwell_time(section_name);

-- Traffic Predictions table
CREATE TABLE traffic_predictions (
    id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL,
    prediction_hour INTEGER NOT NULL,
    predicted_visitors INTEGER NOT NULL,
    confidence_level FLOAT,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prediction_date, prediction_hour)
);

-- Recommendations table (AI-generated)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_visitors_date_hour ON visitors(date, hour);
CREATE INDEX idx_visitors_timestamp ON visitors(timestamp);

CREATE INDEX idx_section_date_hour ON section_analytics(date, hour);
CREATE INDEX idx_section_name ON section_analytics(section_name);
CREATE INDEX idx_section_timestamp ON section_analytics(timestamp);

CREATE INDEX idx_cashier_date_hour ON cashier_analytics(date, hour);
CREATE INDEX idx_cashier_timestamp ON cashier_analytics(timestamp);

CREATE INDEX idx_predictions_date_hour ON traffic_predictions(prediction_date, prediction_hour);

CREATE INDEX idx_recommendations_active ON recommendations(is_active);
CREATE INDEX idx_recommendations_timestamp ON recommendations(timestamp);

-- Create a view for daily summaries
CREATE OR REPLACE VIEW daily_summary AS
SELECT 
    date,
    SUM(visitor_count) as total_visitors,
    AVG(visitor_count) as avg_hourly_visitors,
    MAX(visitor_count) as peak_visitors
FROM visitors
GROUP BY date
ORDER BY date DESC;

-- Create a view for section performance
CREATE OR REPLACE VIEW section_performance AS
SELECT 
    section_name,
    date,
    SUM(visitor_count) as total_visitors,
    AVG(visitor_count) as avg_visitors,
    SUM(male_count) as total_male,
    SUM(female_count) as total_female
FROM section_analytics
GROUP BY section_name, date
ORDER BY date DESC, total_visitors DESC;
