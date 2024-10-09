import os
import sqlite3
import urllib
import glob
import pickle
import wikipedia

from event import Event
from dao import fetching, executing

conn = sqlite3.connect('./data.sqlite3')
cursor = conn.cursor()

def get_image(file_path, file_url):
    urllib.request.urlretrieve(file_url, f'./images/marian-miracles/{file_path}')

# 1. get the pickle files
events = [Event(event) for event in fetching.all_events(cursor)]

for event in events:
    name = event.name
    try:
        page = wikipedia.page(urllib.parse.unquote(name))
    except wikipedia.PageError as e:
        print(e)
    images = page.images
    image_index = 0 # 0 is often occupied by the catholicism portal's image
    
    while (
        images[image_index].endswith('.svg') or
        '046CupolaSPietro.jpg' in images[image_index] or
        '150px-Inmaculada_Concepci%C3%B3n_de_Aranjuez.jpg' in images[image_index]):
        image_index += 1

    la_premiere = images[image_index]
    ext = la_premiere.split('.')[-1]
    get_image(f'{event.id}.{ext}', la_premiere)
