-- Nhiệt độ Hà Nội hợp lệ: -10°C đến 50°C.
-- Trả về row nếu có giá trị bất thường → test FAIL.
{{ config(severity='warn') }}
SELECT
    id,
    temperature
FROM {{ ref('stg_weather_data') }}
WHERE temperature < -10 OR temperature > 50
