import datetime
import os.path
import sqlite3
import vocadbtosqlite.util
import vocadbtosqlite.weblinks
import vocadbtosqlite.tags
import vocadbtosqlite.pvs
import vocadbtosqlite.tags
import vocadbtosqlite.names

known_keys = ['id', 'lengthSeconds', 'nicoId', 'notes', 'notesEng', 'publishDate', 'songType', 'maxMilliBpm',
              'minMilliBpm', 'webLinks']

reported_keys = known_keys


def link_events(song_list, cursor: sqlite3.Cursor):
    for a in song_list:
        try:
            cursor.execute('''
                INSERT INTO EVENTS_SONGS (event_id, song_id) VALUES (:event_id, :id) ON CONFLICT DO NOTHING
            ''', a)
        except sqlite3.IntegrityError:
            pass


def sync_songs(db: sqlite3.Connection, song_list):
    # TODO: convert timestamp to actual timestamp instead of str (saves DB storage)
    # TODO: move song types to it's own table (saves DB storage)
    # TODO: Batch processing to improve performance
    # TODO: Indices!!!
    c = db.cursor()
    c.executemany('''
    INSERT INTO SONGS (id, lengthSeconds, nicoId, notes, notesEng, publishDate, songType, maxMilliBpm, minMilliBpm) 
    VALUES
    (:id, :lengthSeconds, :nicoId, :notes, :notesEng, :publishDate, :songType, :maxMilliBpm, :minMilliBpm) 
    ON CONFLICT DO NOTHING
    ''', song_list)
    db.commit()
    c = db.cursor()

    weblinks = []
    pvs = []
    names = []
    tags = []

    global known_keys
    global reported_keys
    for s in song_list:
        song_id = s.get('id')
        for wl in s.get('webLinks'):
            wl['song_id'] = song_id
        weblinks += s.get('webLinks')

        for name in s.get('names', []):
            name['song_id'] = song_id
            names += (name,)

        for t in s['tags']:
            t['song_id'] = song_id
            t['tag_id'] = t['tag'].get('id')
            tags += (t,)

        # Now we have all songs, extract the pvs:
        for pv in s.get('pvs', []):
            pv['song_id'] = song_id
            pvs += (pv,)
    # ReleaseEvents are: {'id': 1300, 'nameHint': '猫村いろは誕生祭 2013'}
    # OriginalVersion is: {'id': 500092, 'nameHint': 'Hello, get to you.'}
    # TODO: ReleaseEvent
    # TODO: OriginalVersion
    # TODO: lyrics is always empty -> why!?
    vocadbtosqlite.weblinks.link_to_weblinks(weblinks, c)

    vocadbtosqlite.pvs.add_pvs(pvs, c)
    vocadbtosqlite.pvs.link_songs(pvs, c)

    vocadbtosqlite.names.add_names(names, c)
    vocadbtosqlite.names.batch_link_songs(names, c)

    vocadbtosqlite.tags.link_songs(tags, cursor=c)

    db.commit()


def parse_song_dir(db: sqlite3.Connection, location):
    all_songs = []
    print('scanning song dir...')
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            all_songs += vocadbtosqlite.util.parse_json(fl)
    print('syncing to database...')
    sync_songs(db, all_songs)
