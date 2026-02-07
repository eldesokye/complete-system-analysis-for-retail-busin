-- Insert Demo Data for Retail Analytics System

-- 1. Insert Visitors Data (Last 7 days)
INSERT INTO visitors (timestamp, visitor_count, date, hour)
SELECT 
    timestamp,
    visitor_count,
    date,
    hour
FROM (
    SELECT 
        CURRENT_TIMESTAMP - INTERVAL '1 day' * d.day_offset - INTERVAL '1 hour' * h.hour_offset as timestamp,
        CASE 
            WHEN h.hour_offset BETWEEN 9 AND 12 THEN floor(random() * 20 + 30)  -- Morning peak
            WHEN h.hour_offset BETWEEN 13 AND 15 THEN floor(random() * 30 + 50)  -- Afternoon peak
            WHEN h.hour_offset BETWEEN 16 AND 19 THEN floor(random() * 40 + 60)  -- Evening peak
            ELSE floor(random() * 10 + 5)  -- Off-peak
        END as visitor_count,
        CURRENT_DATE - INTERVAL '1 day' * d.day_offset as date,
        h.hour_offset as hour
    FROM generate_series(0, 6) d(day_offset)
    CROSS JOIN generate_series(0, 23) h(hour_offset)
    WHERE h.hour_offset BETWEEN 8 AND 22  -- Store hours: 8 AM to 10 PM
) data
ORDER BY timestamp;