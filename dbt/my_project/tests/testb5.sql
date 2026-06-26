--Viết file test đảm bảo trong stg_weather_data:wind_speed >= 0
--humidity nằm trong khoảng 0 đến 100
{{ config(severity='warn') }}
SELECT 
    wind_speed,
    humidity
FROM
    {{ ref('stg_weather_data') }}
WHERE
    humidity BETWEEN 0 AND 48 OR
    wind_speed >= 0