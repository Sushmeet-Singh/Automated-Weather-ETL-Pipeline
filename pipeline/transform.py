class DataQualityError(Exception):
    pass

def validate_weather(record: dict, city: str):
    errors = []

    if not (-90 <= record["temp_celsius"] <= 60):
        errors.append(f"temp_celsius out of range: {record['temp_celsius']}")

    if not (-90 <= record["feels_like"] <= 60):
        errors.append(f"feels_like out of range: {record['feels_like']}")

    if not (0 <= record["humidity"] <= 100):
        errors.append(f"humidity out of range: {record['humidity']}")

    if not (870 <= record["pressure_hpa"] <= 1085):
        errors.append(f"pressure_hpa out of range: {record['pressure_hpa']}")

    if not (0 <= record["wind_speed"] <= 113):
        errors.append(f"wind_speed out of range: {record['wind_speed']}")

    if not record["city"] or not record["country"]:
        errors.append("city or country is missing")

    if not record["description"]:
        errors.append("description is missing")

    if errors:
        raise DataQualityError(f"Data quality check failed for {city}: {errors}")

def transform_weather(raw: dict) -> dict:
    record = {
        "city":         raw["name"],
        "country":      raw["sys"]["country"],
        "temp_celsius": round(raw["main"]["temp"] - 273.15, 2),
        "feels_like":   round(raw["main"]["feels_like"] - 273.15, 2),
        "humidity":     raw["main"]["humidity"],
        "pressure_hpa": raw["main"]["pressure"],
        "wind_speed":   raw["wind"]["speed"],
        "description":  raw["weather"][0]["description"],
    }
    validate_weather(record, record["city"])
    return record