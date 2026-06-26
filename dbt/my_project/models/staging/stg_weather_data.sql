{{ config(
    materialized= 'table',
    unique_key= 'id'
)}}

with source as (
    select * from {{ source('weather', 'weather_data') }}
),

de_dup as(
    select *,
    row_number() over (partition by timestamp order by id) as rn
    from source
)
select *
from de_dup
where rn = 1   