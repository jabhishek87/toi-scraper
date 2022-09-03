from datetime import date, datetime,  timedelta
import logging
import requests
import urllib.request


from bs4 import BeautifulSoup
# import redis


log = logging.getLogger(__name__)


class ToiScraper:
    def __init__(self):
        self.base_url = "https://timesofindia.indiatimes.com"
        # self.rdb = redis.Redis()

        # Archive will always be todays date - 2 days older
        # example if todays is 30th August, then it will always start 30 -2 = 28

        # Get Today's Date
        self.start_date = date.today() - timedelta(days=2)
        self.start_cms_id = self.get_cms_id(date.today())
        # we can get year and month from date
        # self.start_date.year, self.start_date.month

    def _get_url(self, url):
        # Get the Url
        resp = requests.get(url)
        log.info(f"Response {resp.status_code}")
        if resp.status_code == 200:
            return resp.text
        else:
            return None

    def get_cms_id(self, date_obj):
        # since the oldest archive is
        # year 1900
        # month Jan
        # day 1
        start_date = datetime.strptime('1-1-1900', "%d-%m-%Y")  # 1st Jan 1900
        diff = date_obj - start_date.date()
        return diff.days

    def build_url(self, date_obj, cms_id):
        # https://timesofindia.indiatimes.com/2022/8/28/archivelist/
        # year-2022,month-8,starttime-44801.cms
        # https://timesofindia.indiatimes.com/archivelist/starttime-44801.cms
        # return f"{self.base_url}/archivelist/starttime-{cms_id}.cms"
        return f"{self.base_url}/{date_obj.year}/{date_obj.month}/{date_obj.day}/archivelist/year-{date_obj.year},month-{date_obj.month},starttime-{cms_id}.cms"

    def scrape_article_page(self, url):
        cms_id=url.split('/')[len(url.split('/'))-1].strip('.cms')

        # dont Process if already present
        # if self.rdb.hgetall(cms_id):
        if False:
            log.info("Already Present Skipping")
        else:

            full_url = f"{self.base_url}{url}"
            log.info(f"Scraping article: {full_url}")
            resp = self._get_url(full_url)
            if resp:
                soup = BeautifulSoup(resp, 'html.parser')
                article_image = soup.select_one('.coverimgIn')

                if article_image:
                    # save images
                    article_image = article_image.find('img')
                    urllib.request.urlretrieve(
                        article_image['src'], f"./images/{article_image['data-imgid']}.png"
                    )

                data = {
                    'article_title': soup.find_all('arttitle')[0].text,
                    'article_text': soup.find_all('arttextxml')[0].text,
                    # 'article_image': article_image.get('data-imgid', None),
                }
                print(data)
                # Save data to db
                # self.rdb.hmset(cms_id, data)
                # self.rdb.bgsave()

            # to get data
            # r.keys()
            # r.hgetall("93835014")

    def scrape_links(self, url):
        # Function to get all the links from Date Page

        # Get the Url
        resp = self._get_url(url)
        if resp:
            soup = BeautifulSoup(resp, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                if 'articleshow' in a_tag['href']:
                    self.scrape_article_page(a_tag['href'])


    def start_scraping(self):
        # First check if older file Present of Not
        cms_id = self.start_cms_id
        date_obj = self.start_date
        # there is nothing before 2002
        while (cms_id >=1) and (date_obj.year > 2001):
            url = self.build_url(date_obj, cms_id)
            log.info(
                f"\n\nFetching for {date_obj.strftime('%d %B, %Y')} : {url}"
            )
            self.scrape_links(url)
            # Adjust Params
            cms_id = cms_id - 1
            date_obj = date_obj - timedelta(days=1)