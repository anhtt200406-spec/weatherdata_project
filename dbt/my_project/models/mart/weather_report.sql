{{ config(
    materialized= 'table',
    unique_key= 'id'
)}}
    select 
        *
    from {{ source('weather', 'weather_data') }}


