from apscheduler.schedulers.background import BackgroundScheduler

from config import FETCH_INTERVAL_MINUTES
from rss_fetcher import fetch_all_sources

scheduler = BackgroundScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        fetch_all_sources,
        trigger="interval",
        minutes=FETCH_INTERVAL_MINUTES,
        id="fetch_rss_job",
    )
    scheduler.start()


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
