import time
import schedule
import psycopg2
import requests
from datetime import datetime

API_KEY = 'YOUR_WEATHER_API_KEY'
LOCATION = 'YOUR_LOCATION'  # e.g., "New York,US"
DB_NAME = 'weatherdb'
DB_USER = 'weatheruser'
DB_PASSWORD = 'someStrongPassword'
DB_HOST = 'localhost'
DB_PORT = '5432'

def create_table_if_not_exists():
    """Create the weather table if it does not exist."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    # Example schema
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            time TIMESTAMP NOT NULL,
            temp REAL,
            pressure REAL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def fetch_weather():
    """Fetch current weather data from API and store in Postgres."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()

    temp = response['main']['temp']
    pressure = response['main']['pressure']
    timestamp = datetime.utcnow()  # or local time if desired

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    insert_query = """
        INSERT INTO weather (time, temp, pressure)
        VALUES (%s, %s, %s)
    """
    cur.execute(insert_query, (timestamp, temp, pressure))
    conn.commit()
    cur.close()
    conn.close()

def main():
    create_table_if_not_exists()
    schedule.every(5).minutes.do(fetch_weather)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
