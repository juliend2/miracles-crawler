import sqlite3
import os
import re
from typing import Union


import scrapy
from scrapy.crawler import CrawlerProcess
from rapidfuzz import fuzz


# FETCH THE DATA
# ===============

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
                    'name': self.extract_text_with_spaces(meta_tr.css('th[data-sort-value]')),
                    'year': meta_tr.css(year_selector).get().strip(),
                    'description': self.remove_footnotes(
                        self.extract_text_with_spaces(meta_tr.xpath('following-sibling::tr[1]').css('td.description'))
                    ),
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

# Run the spider using CrawlerProcess
process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()  # the script will block here until the crawling is finished

spider = QuotesSpider()
# print(spider.results)


# PERSIST THE DATA
# ================

class Years:
    def __init__(self, year: Union[int, str]):
        self.year = year

    def __int__(self):
        if type(self.year) == type('') and type(re.match(r'\D', self.year)):
            return int(re.split(r'\D', self.year)[0])
        return int(self.year)

    # Less or Equal than...
    def __le__(self, other_year):
        return self.year <= other_year.year

    def __sub__(self, other_year):       
        return int(self) - int(other_year)


class Event:
    SIMILARITY_THRESHOLD = 90

    def __init__(self, props):
        self.category = props['category']
        self.name = props['name'].strip()
        self.year = props['year']
        self.description = props['description']

    def __repr__(self) -> str:
        return f'{self.name} ({self.year})'

    def __eq__(self, value: Union['Event', None]) -> bool:
        # Check only if the _compared_ value is None.
        # `self` is an instance, therefore it's not None.
        if value is None:
            return False
        
        name_similarity = fuzz.ratio(self.name, value.name)
        # TODO: use a type that can be compared for `year`:
        year_similarity = self.calculate_years_similarity(self.year, value.year)
        overall_similarity = (name_similarity * 0.7) + (year_similarity * 0.3)

        return overall_similarity >= 90
    
    def calculate_years_similarity(self, year1, year2) -> int:
        y1 = Years(year1)
        y2 = Years(year2)

        if y1 == y2: # Yup. Even if those are None.
            return 100

        if y1 is None or y2 is None:
            return 0
        
        if abs(y1 - y2) <= 2: # allow a difference of 2 years
            return self.SIMILARITY_THRESHOLD # less similar because the == is already done earlier
        
        return 0 # We covered all the potential cases. By this point it's NOT similar.


conn = sqlite3.connect('./data.sqlite3')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS events
                  (id INTEGER PRIMARY KEY, category TEXT, name TEXT, year INTEGER, description TEXT)''')

def fetch_all_events(cursor):
    cursor.execute('''
        SELECT  *
        FROM    events
        ''')
    columns = [column[0] for column in cursor.description]  # Get column names
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]  # Create list of dictionaries


def insert_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (category, name, year, description)
        VALUES (?, ?, ?, ?)
        ''', (event.category, event.name, event.year, event.description))
    conn.commit()

def update_event(conn, event: Event):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events
        SET description = ?
        WHERE name = ? AND year = ?
        ''', (event.description, event.name, event.year))
    conn.commit()


events = [Event(event) for event in fetch_all_events(cursor)]

for result in spider.results:
    event = Event(result)
    result = Event(result)

    # Doesn't exist? Create it:
    if event not in events:
        insert_event(conn, event)
        continue
    
    matching_event = next((e for e in events if e == result), None)
    # Exists and description isn't the same? Update it:
    if matching_event and matching_event.description != event.description:
        update_event(conn, event)
        continue


print(events)


event = Event({
    'category': 'category',
    'name': 'name and date are the same',
    'year': '2000',
    'description': 'description',
})

# event2 = Event({
#     'category': 'category',
#     'name': 'the name and date are the same',
#     'year': '2000',
#     'description': 'description',
# })

# print(event == event2)
# print(event == None)

# print(event.calculate_years_similarity(event.year, event2.year))

# print(event.calculate_years_similarity(1, 2))

