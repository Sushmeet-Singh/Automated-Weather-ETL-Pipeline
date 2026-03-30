import psycopg2
import os
from dotenv import load_dotenv


DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "weather_db",
    "user":     "postgres",
    "password": "Enter your postgres password",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG, connect_timeout=10)

def insert_weather(record: dict):
    sql = """
        INSERT INTO weather_data
            (city, country, temp_celsius, feels_like, humidity, pressure_hpa, wind_speed, description)
        VALUES
            (%(city)s, %(country)s, %(temp_celsius)s, %(feels_like)s,
             %(humidity)s, %(pressure_hpa)s, %(wind_speed)s, %(description)s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, record)
        conn.commit()