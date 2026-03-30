from apscheduler.schedulers.blocking import BlockingScheduler
from pipeline.extract import fetch_weather
from pipeline.transform import transform_weather, DataQualityError
from pipeline.load import insert_weather
from pipeline.logger import logger

CITIES = [
    # North America
    "Vancouver",
    "Toronto",
    "New York",
    "Mexico City",
    # South America
    "São Paulo",
    "Buenos Aires",
    # Europe
    "London",
    "Paris",
    "Berlin",
    # Africa
    "Cairo",
    "Lagos",
    # Asia
    "Tokyo",
    "Mumbai",
    "Singapore",
    # Oceania
    "Sydney",
]

def run_pipeline():
    success = 0
    failed  = 0
    skipped = 0

    for city in CITIES:
        try:
            logger.info(f"Fetching weather for {city}...")
            raw    = fetch_weather(city)
            record = transform_weather(raw)
            insert_weather(record)
            logger.info(f"[OK] {city}: {record['temp_celsius']}C, {record['description']}")
            success += 1

        except DataQualityError as e:
            logger.warning(f"[SKIPPED] {city}: {e}")
            skipped += 1

        except Exception as e:
            logger.error(f"[FAILED] {city}: {e}", exc_info=True)
            failed += 1

    logger.info(f"Run complete — {success} succeeded, {skipped} skipped, {failed} failed")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_pipeline,
        "interval",
        minutes=15,
        max_instances=1,
        misfire_grace_time=60,
        coalesce=True
    )
    logger.info("Pipeline scheduler started. Runs every 15 minutes.")
    run_pipeline()
    scheduler.start()
