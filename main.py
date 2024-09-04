import os
import re

import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    results = []

    def start_requests(self):
        absolute_path = os.path.abspath('test-data/list-of-marian-apparitions.html')
        
        urls = [
            f'file://{absolute_path}',
            # 'https://en.wikipedia.org/wiki/List_of_Marian_apparitions',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        year_selector = 'td:nth-child(3)::text'
        for tbody in response.css('.wikitable > tbody'):
            for meta_tr in tbody.css('tr:not(.expand-child)'):
                
                if not meta_tr.css(year_selector).get():
                    continue
                
                result = {
                    'category': meta_tr.css('td:first-child[title]').attrib['title'].strip(),
                    'name': extract_text_with_spaces(meta_tr.css('th[data-sort-value]')),
                    'year': meta_tr.css(year_selector).get().strip(),
                    'description': remove_footnotes(
                        extract_text_with_spaces(meta_tr.xpath('following-sibling::tr[1]').css('td.description'))
                    ),
                    # 'tags': quote.css('div.tags a.tag::text').getall(),
                }
                self.results.append(result)
                yield result

def remove_footnotes(text):
    return re.sub(r' \[ \d+ \]', '', text)

def extract_text_with_spaces(selector):
    parts = selector.xpath('.//text()[not(parent::style)] | .//br').getall()
    text_with_spaces = ' '.join(
        part.strip() if part != '<br>' else ' ' for part in parts
    )
    return text_with_spaces

# Run the spider using CrawlerProcess
process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()  # the script will block here until the crawling is finished

spider = QuotesSpider()
print(spider.results)