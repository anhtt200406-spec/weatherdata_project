--Model daily_average tính avg_temperature bằng AVG(temperature) từ source. Viết test xác nhận giá trị avg_temperature
--trong daily_average khớp với kết quả tính thủ công từ source('weather', 'weather_data').
-- Test: avg_temperature trong daily_average phải khớp với AVG(temperature)
-- tính lại thủ công từ source, so theo TỪNG NGÀY.
{{ config(severity='warn') }}
WITH expected AS (
    SELECT
        recorded_date,                                  -
        ROUND(AVG(temperature)::numeric, 2) AS expected_avg
    FROM {{ source('weather', 'weather_data') }}
    GROUP BY recorded_date
),
actual AS (
    SELECT
        recorded_date,                               
        ROUND(avg_temperature::numeric, 2) AS actual_avg
    FROM {{ ref('daily_average') }}
)
SELECT
    e.recorded_date,
    e.expected_avg,
    a.actual_avg
FROM expected e
INNER JOIN actual a
    ON e.recorded_date = a.recorded_date
WHERE e.expected_avg != a.actual_avg


