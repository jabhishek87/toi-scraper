from datetime import date, datetime,  timedelta
import logging


from bs4 import BeautifulSoup
from security import safe_requests

# import redis


log = logging.getLogger(__name__)


class ToiScraper:
    def __init__(self):
        self.base_url = "https://timesofindia.indiatimes.com"

        # Archive will always be todays date - 2 days older
        # example if todays is 30th August, then it will always start 30 -2 = 28

        # Get Today's Date
        self.start_date = date.today() - timedelta(days=2)
        self.start_cms_id = self.get_cms_id(date.today())
        # we can get year and month from date
        # self.start_date.year, self.start_date.month
        self.rows = []
        self.news_date = ''

    @property
    def get_rows(self):
        return self.rows

    def _get_url(self, url):
        # Get the Url
        resp = safe_requests.get(url)
        # log.info(f"Response {resp.status_code}")
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
        web_url = f"{self.base_url}{url}"
        log.info(f"Parsing {web_url}")
        feed_url = f"https://toifeeds.indiatimes.com/treact/feeds/toi/web/show/news?path=/articleshow/{cms_id}.cms"
        resp = safe_requests.get(feed_url)
        rec = {}
        if resp:
            resp_data = resp.json()

            # description
            desc = ""
            for i in resp_data['story']:
                if i['tn'] == 'text':
                    desc += i['value'] + " "
            # print(desc)
        return {
            'date': self.news_date,
            'title': resp_data['hl'],
            'article': desc,
            'cms_id': cms_id
        }

    def scrape_links(self, url):
        # Function to get all the links from Date Page

        # Get the Url
        resp = self._get_url(url)
        if resp:
            soup = BeautifulSoup(resp, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                if 'articleshow' in a_tag['href']:
                    self.rows.append(
                        self.scrape_article_page(a_tag['href'])
                    )


    def start_scraping(self):
        # First check if older file Present of Not
        cms_id = self.start_cms_id
        date_obj = self.start_date
        # there is nothing before 2002
        while (cms_id >=1) and (date_obj.year > 2001):
            url = self.build_url(date_obj, cms_id)
            self.news_date =date_obj.strftime('%d-%m-%Y')
            log.info(
                f"\n\nFetching for {date_obj.strftime('%d %B, %Y')} : {url}"
            )
            self.scrape_links(url)
            # Adjust Params
            cms_id = cms_id - 1
            date_obj = date_obj - timedelta(days=1)
