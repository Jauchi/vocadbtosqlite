import os.path
import sqlite3
import src.util
import vocadbtosqlite.weblinks
import vocadbtosqlite.tags
import vocadbtosqlite.pvs
import src.parse_tags
import sys
import json

known_keys = ['id', 'lengthSeconds', 'nicoId', 'notes', 'notesEng', 'publishDate', 'songType', 'maxMilliBpm',
              'minMilliBpm', 'webLinks']

reported_keys = known_keys


def sync_songs(db: sqlite3.Connection, song_list):
    # TODO: convert timestamp to actual timestamp instead of str (saves DB storage)
    # TODO: move song types to it's own table (saves DB storage)
    c = db.cursor()
    c.executemany('''
    INSERT INTO SONGS (id, lengthSeconds, nicoId, notes, notesEng, publishDate, songType, maxMilliBpm, minMilliBpm) 
    VALUES
    (:id, :lengthSeconds, :nicoId, :notes, :notesEng, :publishDate, :songType, :maxMilliBpm, :minMilliBpm) 
    ON CONFLICT DO NOTHING
    ''', song_list)
    db.commit()

    global known_keys
    global reported_keys
    for s in song_list:
        src.parse_weblinks.link_song_to_weblinks(s.get('id'), s.get('webLinks'), db)
        for k in s.keys():
            if str(k) not in reported_keys:
                print('unknown key encountered: ' + str(k))
                print(str(type(s[k])))
                reported_keys += [k]
        for t in s['tags']:
            src.parse_tags.link_song_id_to_tag(song_id=s.get('id'), tag_id=t.get('tag').get('id'), c=c)
        src.pv.add_pvs(song_id=s.get('id'), pv_list=s['pvs'], cursor=c)
    # ReleaseEvents are: {'id': 1300, 'nameHint': '猫村いろは誕生祭 2013'}
    # OriginalVersion is: {'id': 500092, 'nameHint': 'Hello, get to you.'}
    # TODO: lyrics is always empty -> why!?
    # Now we have all songs, extract the pvs:
    db.commit()
    print('commit.')


def parse_song_dir(db: sqlite3.Connection, location):
    i = 0
    for root, directory, files in os.walk(location):
        for f in files:
            fl = os.path.join(root, f)
            # print('Processing: ' + str(fl))
            songs = src.util.parse_json(fl)
            sync_songs(db, songs)
