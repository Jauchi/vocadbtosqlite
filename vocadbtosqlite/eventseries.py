import sqlite3
import os
import vocadbtosqlite.util
import vocadbtosqlite.tags
import vocadbtosqlite.weblinks
import vocadbtosqlite.names


# TODO: translatedName:
# {
#  'translatedName': {'defaultLanguage': 'English',
#                     'english': 'THE VOC@LOiD M@STER',
#                     'japanese': 'THE VOC@LOiD M@STER',
#                     'romaji': 'THE VOC@LOiD M@STER'},


def add_event_series(event_lst: [dict], cursor: sqlite3.Cursor):
    weblinks = []
    names = []
    tags = []

    cursor.executemany('''
        INSERT INTO EVENT_SERIES (series_id, category, description) VALUES
        (:id, :category, :description)
        ON CONFLICT DO NOTHING
    ''', event_lst)

    for e in event_lst:
        e_id = e.get('id')
        e_names = e.get('names')
        e_weblinks = e.get('webLinks')
        e_tags = e.get('tags')
        if e_weblinks:
            for link in e_weblinks:
                link['series_id'] = e_id
                weblinks += (link,)
        if e_names:
            for n in e_names:
                n['series_id'] = e_id
                names += (n,)
        if e_tags:
            for tag in e_tags:
                tag['tag_id'] = tag['tag']['id']
                tag['series_id'] = e_id
                tags += (tag,)

    vocadbtosqlite.weblinks.add_event_series_weblinks(weblinks, cursor)

    vocadbtosqlite.tags.link_event_series(tags, cursor)

    vocadbtosqlite.names.add_names(names, cursor)
    vocadbtosqlite.names.batch_link_event_series(names, cursor)


def parse_event_series_dir(db: sqlite3.Connection, location):
    all_events_series = []
    c = db.cursor()
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            all_events_series += vocadbtosqlite.util.parse_json(fl)

    add_event_series(event_lst=all_events_series, cursor=c)
    db.commit()
