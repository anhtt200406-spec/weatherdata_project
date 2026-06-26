-- Test: đảm bảo không có bản ghi nào trong stg_weather_data
-- có timestamp ở tương lai (lớn hơn thời điểm hiện tại).
{{ config(severity='warn') }}
SELECT
    id,
    timestamp,
    wind_speed,
    humidity
FROM
    {{ ref('stg_weather_data') }}
WHERE
    timestamp > CURRENT_TIMESTAMP