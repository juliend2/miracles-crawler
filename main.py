import sqlite3
import os
import re
from typing import Union

from scrapy.crawler import CrawlerProcess

from spiders.marian_apparitions import Spider as MarianApparitions
from dao import fetching, executing
from event import Event

# FETCH THE DATA
# ==============

process = CrawlerProcess()
process.crawl(MarianApparitions)
process.start()

spider = MarianApparitions()

# PERSIST THE DATA
# ================

conn = sqlite3.connect('./data.sqlite3')
cursor = conn.cursor()

executing.maybe_create_events_table(cursor)

# Get previous results from the DB:
events = [Event(event) for event in fetching.all_events(cursor)]

# Compare with results we just got from the crawl:
for result in spider.results:
    event = Event(result)
    result = Event(result)

    # Doesn't exist? Create it:
    if event not in events:
        executing.insert_event(conn, event)
        continue

    matching_event = next((e for e in events if e == result), None)

    # Exists and description isn't the same? Update it:
    if matching_event and matching_event.description != event.description:
        executing.update_event(conn, event)
        continue

print(events)

# event = Event({
#     'category': 'category',
#     'name': 'name and date are the same',
#     'year': '2000',
#     'description': 'description',
# })

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
