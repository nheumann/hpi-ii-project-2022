import logging
import os
from datetime import datetime

import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from rb_crawler.constant import State
from spiegel_crawler.spider import SpiegelSpider

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


@click.command()
@click.option("-s", "--date", "date", type=str, help="The date to initialize the crawl from (crawling older articles from then on, YYYY-MM-DD)")
#@click.option("-s", "--state", type=click.Choice(State), help="The state ISO code")
def run(date: str):
    start_date = datetime.strptime(date, "%Y-%m-%d")
    #SpiegelSpider(start_date).extract()
    process = CrawlerProcess(get_project_settings())
    process.crawl(SpiegelSpider, start_date=start_date)
    process.start()



if __name__ == "__main__":
    run()
