import re
from datetime import datetime, timedelta

import scrapy
from scrapy.linkextractors import LinkExtractor
import logging

from build.gen.bakdata.articles.article_pb2 import Article, SPIEGEL
from spiegel_producer import SpiegelProducer

log = logging.getLogger(__name__)

class SpiegelSpider(scrapy.Spider):
    name = "spiegel"
    articleLinkExtractor = LinkExtractor(
        restrict_xpaths='//article'
    )

    def __init__(self, start_date: datetime):

        self.date = start_date
        self.producer = SpiegelProducer()

    def start_requests(self):
        url = f"https://www.spiegel.de/nachrichtenarchiv/artikel-{datetime.strftime(self.date, '%d.%m.%Y')}.html"
        log.info(f"Extracting from {url}")
        yield scrapy.Request(url=url, callback=self.parseDateOverview)

    def parseDateOverview(self, response):
        log.info(f"Parsing date overview {response.url}")
        links = self.articleLinkExtractor.extract_links(response)

        # Crawl all found articles
        for link in links:
            yield scrapy.Request(url=link.url, callback=self.parseArticle)

        # build url of day before and crawl it
        self.date = self.date - timedelta(days=1)
        next_page = f"https://www.spiegel.de/nachrichtenarchiv/artikel-{datetime.strftime(self.date, '%d.%m.%Y')}.html"
        yield scrapy.Request(next_page, callback=self.parseDateOverview)

    def parseArticle(self, response):
        log.info(f"Parsing article {response.url}")

        title = response.css('article::attr(aria-label)').get()
        content = "\n".join(response.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," RichText ")]//text()').getall())

        # remove duplicate line breaks from content
        content = re.sub('\\n( |\\n)*\\n', '\n', content)

        id = 'spiegel_' + re.search('([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})', response.url).group(0)

        article = Article()
        article.id = id
        article.title = title
        article.content = content
        article.url = response.url
        article.source = SPIEGEL
        article.date = response.css('header .timeformat::attr(datetime)').get()

        log.info(f"Done parsing article {article}")

        self.producer.produce_to_topic(article=article)


