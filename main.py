import atexit
import os
import logging

from toi_scrapper import ToiScraper

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

def main():
    log.info('Starting Main')
    obj_toi = ToiScraper()
    obj_toi.start_scraping()

@atexit.register
def on_exit():
    log.info("Saving File for Persistence")

if __name__ == "__main__":
    main()
