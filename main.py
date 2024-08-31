import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'https://en.wikipedia.org/wiki/List_of_Marian_apparitions',
            # 'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        year_selector = 'td:nth-child(3)::text'
        for tbody in response.css('.wikitable > tbody'):
            for meta_tr in tbody.css('tr:not(.expand-child)'):
                
                if not meta_tr.css(year_selector).get():
                    continue
                
                yield {
                    'name': meta_tr.css('th[data-sort-value]::text').get(),
                    'year': meta_tr.css(year_selector).get().strip(),
                    # 'tags': quote.css('div.tags a.tag::text').getall(),
                }
            
# Run the spider using CrawlerProcess
process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()  # the script will block here until the crawling is finished
