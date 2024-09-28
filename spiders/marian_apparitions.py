import scrapy
import wikipediaapi
import os
import re
import pickle

class Spider(scrapy.Spider):
    name = "quotes"

    results = []

    def start_requests(self):
        absolute_path = os.path.abspath('test-data/list-of-marian-apparitions.html')
        self.wiki = wikipediaapi.Wikipedia('MarianApparitions (julien@desrosiers.org)', 'en')
        
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
                
                wikipedia_section_title = ''
                try:
                    full_article_url = meta_tr.css('th[data-sort-value]').css('a').attrib['href']
                except (IndexError, KeyError):
                    full_article_url = None

                if full_article_url and self.url_leads_to_wikipedia(full_article_url):
                    full_article_url_slug = os.path.basename(full_article_url)
                    # wikipedia_section_title = full
                    full_article = self.get_article_content(full_article_url_slug)
                    # full_article.sections_by_title()
                
                result = {
                    'category': meta_tr.css('td:first-child[title]').attrib['title'].strip(),
                    'name': self.extract_text_with_spaces(meta_tr.css('th[data-sort-value]')),
                    'year': meta_tr.css(year_selector).get().strip(),
                    'description': self.remove_footnotes(
                        self.extract_text_with_spaces(meta_tr.xpath('following-sibling::tr[1]').css('td.description'))
                    ),
                    'wikipedia_section_title': wikipedia_section_title,
                    # 'tags': quote.css('div.tags a.tag::text').getall(),
                }
                self.results.append(result)
                yield result

    def remove_footnotes(self, text):
        return re.sub(r' \[ \d+ \]', '', text)

    def extract_text_with_spaces(self, selector):
        parts = selector.xpath('.//text()[not(parent::style)] | .//br').getall()
        text_with_spaces = ' '.join(
            part.strip() if part != '<br>' else ' ' for part in parts
        )
        return text_with_spaces
    
    def url_leads_to_wikipedia(self, url):
        return url[0:1] == '/' and '/wiki' in url

    def get_article_content(self, wikipedia_article_slug):
        full_article = None

        article_pickle_file_path = f'./article_pickles/{wikipedia_article_slug}.pkl'
        if os.path.exists(article_pickle_file_path):
            # Get it from cache:
            with open(article_pickle_file_path, 'rb') as f:
                return pickle.load(f)

        if full_article is None:
            full_article = self.wiki.page(wikipedia_article_slug)
            # Cache it:
            with open(article_pickle_file_path, 'wb') as f:
                pickle.dump(full_article, f)
            return full_article

        return None