import datetime
import os.path
import sqlite3
import vocadbtosqlite.util
import vocadbtosqlite.weblinks
import vocadbtosqlite.tags
import vocadbtosqlite.pvs
import vocadbtosqlite.tags

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

    global known_keys
    global reported_keys
    for s in song_list:
        song_id = s.get('id')
        for wl in s.get('webLinks'):
            wl['song_id'] = song_id
        weblinks += s.get('webLinks')

        for t in s['tags']:
            try:
                vocadbtosqlite.tags.link(song_id=s.get('id'), tag_id=t.get('tag').get('id'), cursor=c)
            except sqlite3.IntegrityError:
                pass
        # Now we have all songs, extract the pvs:
        for pv in s.get('pvs', []):
            pv['song_id'] = song_id
            pvs += (pv,)
    # ReleaseEvents are: {'id': 1300, 'nameHint': '猫村いろは誕生祭 2013'}
    # OriginalVersion is: {'id': 500092, 'nameHint': 'Hello, get to you.'}
    # TODO: lyrics is always empty -> why!?
    vocadbtosqlite.weblinks.link_to_weblinks(weblinks, c)
    vocadbtosqlite.pvs.add_pvs(pvs, c)
    vocadbtosqlite.pvs.link_songs(pvs, c)

    db.commit()


def parse_song_dir(db: sqlite3.Connection, location):
    i = 0
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            t_start = datetime.datetime.now()
            songs = vocadbtosqlite.util.parse_json(fl)
            duration_parse = datetime.datetime.now() - t_start
            print(str('Parsing took ' + str(duration_parse)))
            sync_songs(db, songs)
            duration = datetime.datetime.now() - t_start
            print(str('Syncing to db took ' + str(duration-duration_parse)))
