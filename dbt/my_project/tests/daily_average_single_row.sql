-- daily_average là aggregate toàn bảng, phải có đúng 1 dòng.
-- Trả về row nếu số dòng != 1 → test FAIL.
{{ config(severity='error') }}
SELECT COUNT(*) AS row_count
FROM {{ ref('daily_average') }}
HAVING COUNT(*) != 1


