-- Độ ẩm phải nằm trong khoảng 0–100%.
-- Trả về row nếu có giá trị ngoài khoảng → test FAIL.
{{ config(severity='warn') }}
SELECT
    id,
    humidity
FROM {{ ref('stg_weather_data') }}
WHERE humidity < 0 OR humidity > 100
