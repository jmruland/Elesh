import os
import threading
import time
from utils.wp_scraper import scrape_wordpress
from indexer import reload_index

def start_scheduler(interval_seconds=1800):
    def scheduled_task():
        while True:
            print("[SCHEDULER] Running scheduled WordPress scrape...")
            scrape_wordpress()
            reload_index()
            time.sleep(interval_seconds)

    thread = threading.Thread(target=scheduled_task, daemon=True)
    thread.start()