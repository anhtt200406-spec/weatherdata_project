CREATE USER airflow WITH PASSWORD 'airflow_password';
CREATE DATABASE airflow_db OWNER airflow;

CREATE SCHEMA IF NOT EXISTS weather_schema;
CREATE TABLE IF NOT EXISTS weather_schema.weather_data (
    id SERIAL PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    utc_offset TEXT
);