-- Tốc độ gió không thể âm.
-- Trả về row nếu có giá trị < 0 → test FAIL.
{{ config(severity='warn') }}
SELECT
    id,
    wind_speed
FROM {{ ref('stg_weather_data') }}
WHERE wind_speed < 0
