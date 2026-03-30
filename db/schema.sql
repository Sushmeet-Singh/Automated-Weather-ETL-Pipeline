CREATE TABLE IF NOT EXISTS weather_data (
    id            SERIAL PRIMARY KEY,
    city          VARCHAR(100) NOT NULL,
    country       VARCHAR(10),
    temp_celsius  NUMERIC(5,2),
    feels_like    NUMERIC(5,2),
    humidity      INTEGER,
    pressure_hpa  NUMERIC(7,2),
    wind_speed    NUMERIC(6,2),
    description   TEXT,
    fetched_at    TIMESTAMP DEFAULT NOW()
);
