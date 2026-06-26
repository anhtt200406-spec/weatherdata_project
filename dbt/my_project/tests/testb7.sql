
-- Test: không được có 2 dòng cùng (id, timestamp)
-- Test PASS khi query trả về 0 dòng
{{ config(severity='warn') }}
SELECT
    id,
    timestamp,
    COUNT(*) AS n_rows
FROM
    {{ ref('stg_weather_data') }}
GROUP BY
    id,
    timestamp
HAVING
    COUNT(*) > 1



