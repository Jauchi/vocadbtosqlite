import sqlite3
import os
import vocadbtosqlite.artists
import vocadbtosqlite.songs
import vocadbtosqlite.names
import vocadbtosqlite.util
import vocadbtosqlite.pvs
import vocadbtosqlite.tags
import vocadbtosqlite.weblinks


#  'translatedName': {'defaultLanguage': 'Japanese',
#                     'english': 'Nico Nico Chokaigi 2013',
#                     'japanese': 'ニコニコ超会議 2013',
#                     'romaji': 'Nico Nico Chokaigi 2013'},
def add_event(event_lst: [dict], cursor: sqlite3.Cursor):
    all_artists = []
    all_names = []
    all_pvs = []
    all_songs = []
    all_tags = []
    all_weblinks = []
    all_events = []

    # Preprocessing
    for event in event_lst:
        series = event.get('series')
        artists = event.get('artists')
        names = event.get('names')
        pvs = event.get('pvs')
        songs = event.get('songList')
        tags = event.get('tags')
        weblinks = event.get('webLinks')
        e_id = event.get('id')

        if series:
            seriesId = series.get('id')
            event['series_id'] = seriesId
        else:
            event['series_id'] = None
        all_events += (event,)
        if weblinks:
            for wl in weblinks:
                wl['event_id'] = e_id
                all_weblinks += (wl,)
        if artists:
            for a in artists:
                if a['id'] != 0:
                    a['event_id'] = e_id
                    all_artists += (a,)
        if names:
            for n in names:
                n['event_id'] = e_id
                all_names += (n,)
        if pvs:
            for pv in pvs:
                pv['event_id'] = e_id
                all_pvs += (pv,)
        if songs:
            # SongList is not actually a list...
            songs['event_id'] = e_id
            all_songs += (songs,)
        if tags:
            for t in tags:
                t['event_id'] = e_id
                t['tag_id'] = t['tag'].get('id')
                all_tags += (t,)
    cursor.executemany('''
        INSERT INTO EVENTS (
            event_id, description, category, date, name, series_id, series_number 
        ) VALUES (
            :id, :description, :category, :date, :name, :series_id, :seriesNumber
        ) ON CONFLICT DO NOTHING
    ''', all_events)

    vocadbtosqlite.artists.link_events_artists(all_artists, cursor)

    vocadbtosqlite.names.add_names(all_names, cursor)
    vocadbtosqlite.names.batch_link_events(all_names, cursor)

    vocadbtosqlite.pvs.add_pvs(all_pvs, cursor)
    vocadbtosqlite.pvs.link_events(all_pvs, cursor)

    vocadbtosqlite.songs.link_events(all_songs, cursor)

    vocadbtosqlite.tags.link_events(all_tags, cursor)

    vocadbtosqlite.weblinks.add_event_weblinks(all_weblinks, cursor)


def parse_event_dir(db: sqlite3.Connection, location):
    all_events = []
    c = db.cursor()
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            all_events += vocadbtosqlite.util.parse_json(fl)

    add_event(event_lst=all_events, cursor=c)
    db.commit()
