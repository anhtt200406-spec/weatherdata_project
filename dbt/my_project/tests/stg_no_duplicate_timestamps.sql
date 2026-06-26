-- Sau khi dedup, không được có 2 row cùng timestamp.
-- Trả về row nếu vẫn còn duplicate → test FAIL.
{{ config(severity='warn') }}
SELECT
    timestamp,
    COUNT(*) AS cnt
FROM {{ ref('stg_weather_data') }}
GROUP BY timestamp
HAVING COUNT(*) > 1
