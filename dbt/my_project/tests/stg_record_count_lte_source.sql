-- Sau khi dedup, stg phải có số dòng <= source.
-- Dedup không được tạo thêm row mới.
-- Trả về row nếu stg nhiều hơn source → test FAIL.
{{ config(severity='warn') }}
WITH
  stg_count AS (
    SELECT COUNT(*) AS cnt FROM {{ ref('stg_weather_data') }}
  ),
  src_count AS (
    SELECT COUNT(*) AS cnt FROM {{ ref('weather_report') }}
  )
SELECT
    stg_count.cnt AS stg_cnt,
    src_count.cnt AS src_cnt
FROM stg_count
CROSS JOIN src_count
WHERE stg_count.cnt > src_count.cnt
