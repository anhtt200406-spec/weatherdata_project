-- Các giá trị trung bình phải nằm trong khoảng hợp lệ.
-- Trả về row nếu bất kỳ chỉ số nào ra ngoài ngưỡng thì test FAIL.
{{ config(severity='warn') }}
SELECT
    avg_temperature,
    avg_wind_speed,
    avg_humidity
FROM {{ ref('daily_average') }}
WHERE avg_temperature < -10 OR avg_temperature > 100
   OR avg_wind_speed < 0
   OR avg_humidity < 0 OR avg_humidity > 100
