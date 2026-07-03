--Model daily_average tính avg_temperature 
--bằng AVG(temperature) từ source. 
--Viết test xác nhận giá trị avg_temperature trong daily_average 
--khớp với kết quả tính thủ công từ 
--source('weather', 'weather_data').
{{ config(severity='warn') }}
WITH avg_test AS (
    SELECT
        ROUND(AVG(temperature)::numeric, 2) AS a_t
    FROM {{ source('weather', 'weather_data') }}
)
SELECT
    d.avg_temperature,
    a.a_t AS expected
FROM {{ ref('daily_average') }} d
CROSS JOIN avg_test a
WHERE d.avg_temperature != a.a_t



