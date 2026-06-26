{{ config(
    materialized= 'table',
)}}
select
    round(avg(temperature)::numeric, 2) as avg_temperature,
    round(avg(wind_speed)::numeric, 2) as avg_wind_speed,
    round(avg(humidity)::numeric, 2) as avg_humidity
from {{ source('weather', 'weather_data') }}
