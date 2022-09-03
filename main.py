import atexit
import csv
import os
import logging

from toi_scrapper import ToiScraper

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

obj_toi = ToiScraper()

def main():
    log.info('Starting Main')
    obj_toi.start_scraping()

@atexit.register
def on_exit():
    log.info("Saving File for Persistence")

    # csv header
    fieldnames = ['date', 'title', 'article', 'cms_id']

    with open('article.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(obj_toi.get_rows)



if __name__ == "__main__":
    main()
