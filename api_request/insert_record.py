import os
import psycopg2
from dotenv import load_dotenv
from api_request import get_weather_data

load_dotenv()


def connect_db():
    print("Connecting to the database...")
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            database=os.getenv("POSTGRES_DB", "db"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )
        print("Connection successful!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise


def create_table(conn):
    print("Creating table...")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE SCHEMA IF NOT EXISTS weather_schema;
            CREATE TABLE IF NOT EXISTS weather_schema.weather_data (
                id SERIAL PRIMARY KEY,
                temperature FLOAT,
                humidity FLOAT,
                wind_speed FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utc_offset TEXT
            )
        ''')
        conn.commit()
        print("Table created successfully!")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        raise


def insert_weather_data(conn, data):
    print("Inserting weather data...")
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weather_schema.weather_data (temperature, humidity, wind_speed, utc_offset)
            VALUES (%s, %s, %s, %s)
        ''', (
            data['current']['temperature'],
            data['current']['humidity'],
            data['current']['wind_speed'],
            data['location']['utc_offset']
        ))
        conn.commit()
        print("Weather data inserted successfully!")
    except psycopg2.Error as e:
        print(f"Error inserting weather data: {e}")
        raise

def main():
    try:    
        data = get_weather_data()
        print(data)
        conn = connect_db()
        create_table(conn)
        insert_weather_data(conn, data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:    
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")
            
            

