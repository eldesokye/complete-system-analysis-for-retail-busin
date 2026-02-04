-- 6. Update today's data to be more realistic (override some with patterns)
UPDATE visitors 
SET visitor_count = 
    CASE 
        WHEN hour = 10 THEN 45
        WHEN hour = 12 THEN 68
        WHEN hour = 15 THEN 72
        WHEN hour = 18 THEN 85
        WHEN hour = 20 THEN 55
        ELSE visitor_count
    END
WHERE date = CURRENT_DATE;

UPDATE cashier_analytics 
SET queue_length = 
    CASE 
        WHEN hour = 12 THEN 8
        WHEN hour = 18 THEN 11
        ELSE queue_length
    END,
estimated_wait_time = queue_length * 1.5,
is_busy = queue_length > 3
WHERE date = CURRENT_DATE;